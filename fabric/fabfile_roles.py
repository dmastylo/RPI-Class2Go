

from fabric.api import *
from fabric.colors import green as _green, yellow as _yellow
from cuisine import *
import boto
import boto.ec2
from django.template import loader, Context
import time
from django.conf import settings
from fabfile import *

def setup_app():
    update_ubuntu()
    init_gdata()
    init_base_ubuntu()
    init_python()
    init_apache()
    if settings.USE_SHIB:
        init_shib()

    class2go_deploy()
    init_logging()
    init_dns()
    init_database()
    init_collectstatic()
    apache_restart()


def setup_maint():
    update_ubuntu()
    init_gdata()
    init_base_ubuntu()
    init_python()
    init_apache()
    class2go_deploy()
    init_logging()
    init_dns()
    init_database()
    init_collectstatic()
    apache_restart()


def setup_report():
    update_ubuntu()
    init_gdata()
    init_base_ubuntu()
    init_python()
    class2go_deploy()
    init_logging()
    init_database()
    init_s3cmd()
    init_reporting()

def setup_util():
    update_ubuntu()
    init_gdata()
    init_base_ubuntu()
    init_python()
    class2go_deploy()
    init_logging()
    init_dns()
    init_database()
    init_s3cmd()
    init_util_kelvinator()
    init_certificate()
    init_celery()

def setup_scalyr():
    init_scalyr()


