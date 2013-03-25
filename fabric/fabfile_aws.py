

from fabric.api import *
from fabric.colors import green as _green, yellow as _yellow
from cuisine import *
import boto
import boto.ec2
import boto.ec2.elb
from django.template import loader, Context
import time
from django.conf import settings


env.user = settings.ADMIN_USER

def create_server():
    """
    Creates EC2 Instance
    """
    print(_green("Started..."))
    print(_yellow("...Creating EC2 instance..."))

    conn = boto.ec2.connect_to_region(settings.EC2_REGION, aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)


    image = conn.get_image(settings.EC2_AMI)

    reservation = image.run(1, 1, key_name=settings.EC2_KEY_PAIR, security_groups={settings.EC2_SECURITY},
                            instance_type=settings.EC2_INSTANCE_TYPE)

    instance = reservation.instances[0]
    conn.create_tags([instance.id], {"Name":settings.EC2_TAG})
    while instance.state == u'pending':
        print(_yellow("Instance state: %s" % instance.state))
        time.sleep(10)
        instance.update()

    print(_green("Instance state: %s" % instance.state))
    print(_green("Public dns: %s" % instance.public_dns_name))

    return instance.public_dns_name


class ELB:

    def __init__(self):
        self.ec2_connection = boto.ec2.connect_to_region(settings.EC2_REGION,
                                                         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                                         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        elb_region = boto.regioninfo.RegionInfo(name=settings.EC2_REGION,  endpoint=settings.EC2_ELB_ENDPOINT)

        self.elb_connection = boto.ec2.elb.ELBConnection(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                                         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                                         region=elb_region)


    def get_instance_id(self, instance_name):
        reservations = self.ec2_connection.get_all_instances()

        instance_id = ''

        for r in reservations:
            for i in r.instances:
                if i.tags['Name'] == instance_name:
                    instance_id = i.id

        if len(instance_id) == 0:
            print 'Instance ID not found'
            return None

        return instance_id

def elb_info():

    # get ELB information

    elb = ELB()

    # lb = boto.ec2.elb.loadbalancer.LoadBalancer(connection=elb_connection, name='UWAC2GProd')
    # lb = elb_connection.create_load_balancer('UWAC2GDev','ap-southeast-2a',[(80, 8080, 'http'), (443, 8443, 'tcp')])

    # get instances asssociated with ELB
    lbs = elb.elb_connection.get_all_load_balancers(load_balancer_names=[settings.EC2_ELB])
    # print lbs[0].instances

    # get health
    instance_health = elb.elb_connection.describe_instance_health(settings.EC2_ELB)
    for instance_state in instance_health:
        print

        reservations = elb.ec2_connection.get_all_instances(instance_ids=[instance_state.instance_id])
        # translate

        print instance_state.instance_id + ' ' + reservations[0].instances[0].tags['Name'] + ' ' +  \
              instance_state.state


    # instance_addresses = [ i.tags for r in reservations for i in r.instances ]

def elb_remove_instance(instance_name):

    # check instance_name
    if instance_name is None or len(instance_name) == 0:
        print('instance_name: not specified')
        return

    # get ELB information

    elb = ELB()

    # get instance id from instance_name

    instance_id = elb.get_instance_id(instance_name)

    print('Deregistering ' + instance_id)

    elb.elb_connection.deregister_instances(settings.EC2_ELB,[instance_id])

    print('Deregistered')

def elb_add_instance(instance_name):

    # check instance_name
    if instance_name is None or len(instance_name) == 0:
        print('instance_name: not specified')
        return

    # get ELB information

    elb = ELB()

    # get instance id from instance_name

    instance_id = elb.get_instance_id(instance_name)

    print('Registering ' + instance_id)

    elb.elb_connection.register_instances(settings.EC2_ELB,[instance_id])

    print('Registered')

