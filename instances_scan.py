# Instance scanning and fix

__skip_tags = {
    'AllowSSH': 'true'
}


def scan_and_fix(ec2):
    # List group that open port 22 to 0.0.0.0/0

    loose_open_sgs = []

    for group in ec2.describe_security_groups()['SecurityGroups']:
        group_id = group['GroupId']
        for ip_perm in group['IpPermissions']:
            if ip_perm['IpProtocol'] == 'tcp' and ip_perm['ToPort'] == 22 and ip_perm['FromPort'] == 22:
                for ip in ip_perm['IpRanges']:
                    if ip['CidrIp'] == '0.0.0.0/0':
                        loose_open_sgs.append(group_id)

    print(">> list of loose open security groups: ", loose_open_sgs)

    for reservation in ec2.describe_instances().get('Reservations', []):
        for instance in reservation.get('Instances', []):

            skip = False

            for tag in instance.get('Tags', []):
                if tag['Key'] in __skip_tags and tag['Value'] == __skip_tags[tag['Key']]:
                    skip = True
                    print('>> skip check for instance %s due to specific tag: %s=%s' % (
                        instance['InstanceId'], tag['Key'], tag['Value']))

            if not skip:
                print(">> check security group violations for %s" %
                      instance['InstanceId'])
                security_group_ids = []
                should_modify = False
                for iface in instance.get('NetworkInterfaces', []):
                    for group in iface.get('Groups', []):
                        if group['GroupId'] in loose_open_sgs:
                            should_modify = True
                            print(">> instance %s has violated by loose open security group: %s" % (
                                instance['InstanceId'], group['GroupId']))
                        else:
                            security_group_ids.append(group['GroupId'])
                if should_modify:
                    print(">> modify instance security groups for %s: %s" %
                          (instance['InstanceId'], security_group_ids))
                    ec2.modify_instance_attribute(
                        InstanceId=instance['InstanceId'], Groups=security_group_ids)
