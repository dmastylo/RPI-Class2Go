from fabric.api import *
from fabric.colors import green as _green, yellow as _yellow
from cuisine import *
import boto
import boto.ec2
from django.template import loader, Context
import time
from django.conf import settings
from fabfile import *
from fabfile_aws import *
import datetime


def deploy_update():

    if not is_sudo():
        mode_sudo()
    # remove from ELB

    elb_remove_instance(settings.EC2_TAG)

    run('/etc/init.d/apache2 stop')

    new_dir = 'class2go' + datetime.datetime.now().strftime("%Y-%m-%d")
    run('mv class2go ' + new_dir)

    run('git clone https://github.com/uwacsp/class2go.git')

    run('chown -R ubuntu class2go')

    run('cd class2go/main; cp ../../'+ new_dir + '/main/settings.py .;' + ' cp ../../'+ new_dir + '/main/database.py .')

    run('cd class2go/main; sudo python manage.py collectstatic --noinput')

    run('/etc/init.d/apache2 start')

    elb_add_instance(settings.EC2_TAG)
