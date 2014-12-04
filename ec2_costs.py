from __future__ import unicode_literals
import collections
import boto.ec2

instance_groups = collections.defaultdict(list)

conn = boto.ec2.connect_to_region('us-west-1')

reserved_items = collections.defaultdict(list)
for reserved in conn.get_all_reserved_instances():
    if reserved.state != 'active':
        continue
    key = (
        reserved.instance_type,
        'VPC' in reserved.description,
        reserved.availability_zone
    )
    for _ in range(reserved.instance_count):
        reserved_items[key].append(reserved)

for instance in conn.get_only_instances():
    if instance.state != 'running':
        continue
    instance_groups[(instance.instance_type, instance.vpc_id, instance.placement)].append(instance)

sorted_groups = sorted(instance_groups.iteritems(), key=lambda item: len(item[1]), reverse=True)

for (itype, vpc_id, zone), values in sorted_groups:
    print '-'*10, len(values), itype, vpc_id, zone, '-'*10
    for instance in values:
        reserved_instances = reserved_items[(itype, vpc_id is not None, zone)]
        covered = False
        if reserved_instances:
            covered = True
            reserved_instances.pop()
        print ' '*4, instance, covered, instance.tags.get('Name')

print '#'*20, 'Not covered reserved instances', '#'*20
for (itype, vpc_id, zone), values in reserved_instances:
    print len(values), itype, vpc_id, zone, values[0]
