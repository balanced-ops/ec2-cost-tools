from __future__ import unicode_literals
import collections

__version__ = '0.1.0'


def get_reserved_groups(conn):
    """Get reserved instance groups, return a dict mapping from

        (instance type, VPC or not, Availability zone, Tenancy)

    to

        [reserved instance] * instance_count

    """
    reserved_groups = collections.defaultdict(list)
    for reserved in conn.get_all_reserved_instances():
        if reserved.state != 'active':
            continue
        key = (
            reserved.instance_type,
            'VPC' in reserved.description,
            reserved.availability_zone,
            reserved.instance_tenancy,
        )
        for _ in range(reserved.instance_count):
            reserved_groups[key].append(reserved)
    return reserved_groups


def get_instance_groups(conn):
    """Get instance groups, return a dict mapping from

        (instance type, VPC ID, Availability zone, Tenancy)

    to

        list of instances

    """
    instance_groups = collections.defaultdict(list)
    for instance in conn.get_only_instances():
        if instance.state != 'running':
            continue
        key = (
            instance.instance_type,
            instance.vpc_id,
            instance.placement,
            instance.placement_tenancy,
        )
        instance_groups[key].append(instance)

    sorted_groups = sorted(
        instance_groups.iteritems(),
        key=lambda item: (item[0][0], len(item[1])),
        reverse=True,
    )
    return sorted_groups


def get_reserved_analysis(conn):
    reserved_groups = get_reserved_groups(conn)
    instance_groups = get_instance_groups(conn)

    instance_items = []
    for (itype, vpc_id, zone, tenancy), values in instance_groups:
        instances = []
        for instance in values:
            key = (
                itype,
                vpc_id is not None,
                zone,
                tenancy,
            )
            reserved_instances = reserved_groups[key]
            covered = False
            if reserved_instances:
                covered = True
                reserved_instances.pop()
            instances.append((instance.id, covered, instance.tags.get('Name')))
        instance_items.append((
            (itype, vpc_id, zone, tenancy),
            instances,
        ))

    return dict(
        instance_items=instance_items,
        not_used_reserved_instances=reserved_groups,
    )
