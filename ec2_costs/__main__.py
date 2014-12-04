from __future__ import unicode_literals

import click
import boto.ec2
from prettytable import PrettyTable

from . import get_reserved_analysis


@click.command()
@click.argument('region', nargs=1)
def main(region):
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
    ]
    table = PrettyTable(columns)
    for key in columns:
        table.align[key] = 'l'

    for (instance_type, vpc, zone, tenancy), instances in result['instance_items']:
        covered_count = 0
        for _, covered, _ in instances:
            if covered:
                covered_count += 1

        table.add_row(
            [
                instance_type,
                vpc,
                zone,
                tenancy,
                '{} / {}'.format(covered_count, len(instances))
            ] + ([''] * 2)
        )
        for covered, instance_id, name in instances:
            table.add_row(([''] * 4) + [instance_id, covered, name])
    print table

    columns = [
        'Instance type',
        'VPC',
        'Zone',
        'Tenancy',
        'Count',
    ]
    table = PrettyTable(columns)
    not_used_reserved = result['not_used_reserved_instances'].iteritems()
    for (instance_type, vpc, zone, tenancy), instances in not_used_reserved:
        table.add_row([
            instance_type,
            vpc,
            zone,
            tenancy,
            len(instances),
        ])
    print '#' * 10, 'Not in-use reserved instances', '#' * 10
    print table
