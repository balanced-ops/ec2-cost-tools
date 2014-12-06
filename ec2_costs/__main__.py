from __future__ import unicode_literals
from __future__ import print_function
import decimal

import click
import boto.ec2
from prettytable import PrettyTable

from . import get_reserved_analysis
from . import get_price_table
from . import price_table_to_price_mapping
from . import LINUX_ON_DEMAND_PRICE_URL
from . import LINUX_ON_DEMAND_PREVIOUS_GEN_PRICE_URL


def format_price(price):
    return '{:,.2f}'.format(price)


@click.command()
@click.argument('region', nargs=1)
def main(region):
    od_price_table = get_price_table(LINUX_ON_DEMAND_PRICE_URL)
    od_price_mapping = price_table_to_price_mapping(od_price_table)
    pre_od_price_table = get_price_table(LINUX_ON_DEMAND_PREVIOUS_GEN_PRICE_URL)
    pre_od_price_mapping = price_table_to_price_mapping(pre_od_price_table)
    # mapping from instance type to price info
    od_prices = od_price_mapping[region]
    pre_prices = pre_od_price_mapping[region]
    od_prices.update(pre_prices)

    # we assume there are 30 days in a month
    month_hours = 30 * 24

    # ec2 instance totoal cost per month
    ec2_total_cost = 0
    # ec2 instance totoal cost if all are using on-demand
    ec2_all_on_demand_total_cost = 0

    conn = boto.ec2.connect_to_region(region)
    result = get_reserved_analysis(conn)

    columns = [
        'Instance type',
        'VPC',
        'Zone',
        'Tenancy',
        'Covered',
        'Instnace ID',
        'Name',
        'Monthly Cost',
    ]
    table = PrettyTable(columns)
    for key in columns:
        table.align[key] = 'l'
    table.align['Monthly Cost'] = 'r'

    for (instance_type, vpc, zone, tenancy), instances in result['instance_items']:
        covered_count = 0
        for _, covered_price, _ in instances:
            if covered_price is not None:
                covered_count += 1

        # on demand cost per month
        od_unit_cost = decimal.Decimal(
            od_prices[instance_type]['valueColumns'][0]['prices']['USD']
        )

        # cal total cost
        total_cost = 0
        for _, covered_price, _ in instances:
            unit_cost = od_unit_cost
            if covered_price is not None:
                unit_cost = decimal.Decimal(covered_price)
            total_cost += unit_cost * month_hours

        table.add_row([
            instance_type,
            vpc,
            zone,
            tenancy,
            '{} / {}'.format(covered_count, len(instances))
        ] + ([''] * 2) + [format_price(total_cost)])
        for instance_id, covered_price, name in instances:
            unit_cost = od_unit_cost
            if covered_price is not None:
                unit_cost = decimal.Decimal(covered_price)
            table.add_row(([''] * 4) + [
                covered_price is not None,
                instance_id,
                name,
                format_price(unit_cost * month_hours),
            ])

        ec2_total_cost += total_cost
        ec2_all_on_demand_total_cost += (
            od_unit_cost * month_hours * len(instances)
        )
    print(table)

    columns = [
        'Instance type',
        'VPC',
        'Zone',
        'Tenancy',
        'Count',
        'Monthly Cost',
    ]
    table = PrettyTable(columns)
    for key in columns:
        table.align[key] = 'l'
    table.align['Monthly Cost'] = 'r'
    not_used_reserved = result['not_used_reserved_instances'].iteritems()
    for (instance_type, vpc, zone, tenancy), instances in not_used_reserved:
        unit_cost = 0
        if instances:
            unit_cost = decimal.Decimal(
                instances[0].recurring_charges[0].amount
            )
        table.add_row([
            instance_type,
            vpc,
            zone,
            tenancy,
            len(instances),
            format_price(unit_cost * month_hours),
        ])
        ec2_total_cost += unit_cost * month_hours
    print('#' * 10, 'Not in-use reserved instances', '#' * 10)
    print(table)

    print('#' * 10, 'Summary', '#' * 10)
    print(
        'EC2 Monthly Costs:', format_price(ec2_total_cost)
    )
    print(
        'EC2 Monthly All On Demand Costs:',
        format_price(ec2_all_on_demand_total_cost)
    )
    print(
        'Amount you saved by using reserved:',
        format_price(ec2_all_on_demand_total_cost - ec2_total_cost)
    )
