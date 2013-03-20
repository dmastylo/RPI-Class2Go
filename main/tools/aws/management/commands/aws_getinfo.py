import boto.ec2
from boto.ec2 import EC2Connection
import boto.ec2.elb
from boto.ec2.elb import ELBConnection
from boto.exception import BotoServerError
import socket

from django.core.management.base import BaseCommand, CommandError

import settings


def get_my_private_ip():
    """Returns the ip address that routes to the outside world
    
    Note - this is the local address that routes to outside, not the outside
    address that routes to local
    """
    # NB: Doesn't actually create a connection, just does set up and teardown
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))    # google DNS
    my_ip = s.getsockname()[0]
    s.close()
    return my_ip

class Command(BaseCommand):
    args = ""
    help = """Write information about this host and its neighbors to disk
    
    Assumes our outbound IP address is a private address that is the same registered internally with Amazon
    Assumes we've tagged instances with a Name, and that the name is used to build the hostname
    Assumes the name of the security group of the instance matches the name of the load balancer
    """

    def handle(self, *args, **options):
        ec2_connection = EC2Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        regions = boto.ec2.elb.regions()
        my_priv_ip = get_my_private_ip()

        for region in regions:
            region_lb_connection = ELBConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, region=region)
            # regions is a list of RegionInfo with connection_cls ELBConnection
            # so for our EC2Connection we want to get an EC2Connection RegionInfo with the corresponding region descriptor
            region_connection = EC2Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, region=boto.ec2.get_region(region.name))

            load_balancers = region_lb_connection.get_all_load_balancers()
            instances = [r.instances[0] for r in region_connection.get_all_instances()]
            try:
                # FIXME: TEST This in dev, stage, prod environments
                me = [i for i in instances if i.private_ip_address == my_priv_ip][0]
                my_main_group = me.groups[0].name
            except IndexError:
                me = None
                my_main_group = 'dev'
            instances = [i for i in instances if i.state != u'stopped' and i.groups[0].name == my_main_group]
            load_balancers = [lb for lb in load_balancers if lb.name == my_main_group]

            if load_balancers:
                print region, load_balancers[0]
                for instance in instances:
                    print instance.tags['Name'], instance.public_dns_name, instance.tags['Name'] + '.c2gops.com' # FIXME assumes basename
                    # TODO: we could do a set of socket connections to confirm that it's up on some set of ports we care about
                    #import ipdb; ipdb.set_trace()

            # FIXME: write the interesting information out to disk in some easily usable form
