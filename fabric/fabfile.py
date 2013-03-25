

from fabric.api import *
from fabric.colors import green as _green, yellow as _yellow
from cuisine import *
import boto
import boto.ec2
from django.template import loader, Context
import time
from django.conf import settings


if settings.VM_TYPE == "VAGRANT":
    env.use_ssh_config = True
env.user = settings.ADMIN_USER

class AppSettings:

    def __init__(self, app_key='', app_value={}):
        self.server_alias = app_value['SERVER_ALIAS']
        self.server_name =  app_value['SERVER_NAME']
        self.git_branch =  app_value['GIT_BRANCH']
        self.app_name = app_key
        self.use_shib = app_value['USE_SHIB']
        self.shib_id = app_value['SHIB_ID']
        self.git_repo = app_value['GIT_REPO']

def setup_dev_vagrant_mysql():

    if not is_sudo():
        mode_sudo()

    package_ensure('mysql-server')
    package_ensure('mysql-client')


def init_dev_vagrant_db():

    run('cd class2go/main; ./manage.py syncdb')
    run('cd class2go/main; ./manage.py migrate')
    run('cd class2go/main; ./manage.py syncdb --database=celery')
    run('cd class2go/main; ./manage.py migrate --database=celery')

def setup_dev_vagrant():

    if not is_sudo():
        mode_sudo()

    run('uname -a')

    run('apt-get update')
    package_ensure('git-core')
    package_ensure('python-pip')
    python_package_ensure('django')
    package_ensure('libmysqlclient-dev')
    package_ensure('python-dev')

    if not dir_exists('/home/vagrant/class2go'):
        run('git clone https://github.com/Stanford-Online/class2go.git')

    # Following are needed for Ubuntu dev env
    run('pip install distribute --upgrade')
    package_ensure('libsqlite3-dev')
    package_ensure('libxml2-dev')
    package_ensure('libxslt-dev')
    package_ensure('python-dateutil')



    run('cd class2go; pip install -r requirements.txt')



    #currently bombs with dateutil?
    run('cd class2go; pip install -r suggested_requirements.txt')


def update_ubuntu():

    """
    updates ubuntu packages
    """
    print(_yellow("...Updating Ubuntu..."))

    with mode_sudo():
        run('apt-get update -q -y')
        #run('apt-get upgrade')


def test_file():
    if not is_sudo():
        mode_sudo()

    # run('rm /home/ubuntu/testfile')
    # file_upload("/home/ubuntu/testfile","./files/gdata-2.0.17-c2g.tar.gz")


    # return
    if file_exists('/home/ubuntu/testfile'):
        print 'removing file'
        run('rm /home/ubuntu/testfile')

    file_upload("/home/testfile","./files/gdata-2.0.17-c2g.tar.gz", scp=True)

    return

    contents = file_local_read("./files/gdata-2.0.17-c2g.tar.gz")
    file_write("/home/ubuntu/testfile",contents,scp=True)
    file_ensure("/home/ubuntu/testfile")

def init_base_ubuntu():

    """
    Installs all basic packages for Ubuntu
    """



    print(_yellow("...Initialising Base Ubuntu..."))

    if not is_sudo():
        mode_sudo()

    file_write('hostname',settings.EC2_TAG, scp=True)
    run('mv hostname /etc/hostname; start hostname')

    # need to change hosts file to avoid warnings on sudo

    file_upload('/home/'+settings.ADMIN_HOME+'/update-hosts.sh', './files/update-hosts.sh', scp=True)
    file_ensure("/home/"+settings.ADMIN_HOME+"/update-hosts.sh", mode = "00755",
                owner = settings.ADMIN_USER,
                group=settings.ADMIN_GROUP)

    run('cd /home/'+settings.ADMIN_HOME+'; ./update-hosts.sh remove ' + settings.EC2_TAG + '; ./update-hosts.sh add ' + settings.EC2_TAG)

    run('cd /home/'+settings.ADMIN_HOME+'; rm ./update-hosts.sh')


    t =  loader.get_template('bash_aliases.txt')

    node_type = settings.EC2_TAG.upper()
    node_type = node_type[node_type.find('.')+1:]

    c = Context({ "node_type": node_type })

    file_write("/home/"+settings.ADMIN_HOME+"/.bash_aliases", t.render(c),mode = "00644",
               owner = settings.ADMIN_USER,
               group=settings.ADMIN_GROUP, scp=True)

    file_upload("/home/"+settings.ADMIN_HOME+"/.bashrc", "./files/dot-bashrc", scp=True)

    file_ensure("/home/"+settings.ADMIN_HOME+"/.bashrc", mode = "00644",
               owner = settings.ADMIN_USER,
               group=settings.ADMIN_GROUP)


    run('apt-get update')
    package_ensure('mosh')
    package_ensure('git')
    package_ensure('emacs')
    package_ensure('python-dev')
    package_ensure('mysql-client')
    package_ensure('python-setuptools')
    package_ensure('python-pip')
    package_ensure('python-mysqldb')
    python_package_ensure('django')
    python_package_ensure('South')
    run('apt-get install libjpeg-dev -y')
    file_link('/usr/lib/x86_64-linux-gnu/libjpeg.so','/usr/lib/libjpeg.so',owner='root',group='root')

    python_package_ensure('PIL')
    python_package_ensure('djangorestframework')
    python_package_ensure('pysimplesoap')
    package_ensure('lynx-cur')

    file_ensure('/etc/init.d/update-mnt-perms',mode='00755',owner='root',group='root')
    file_link('/etc/init.d/update-mnt-perms', '/etc/rc2.d/S80update-mnt-perms', owner="root",group="root")
    run('/etc/init.d/update-mnt-perms')




def init_apache():
    """
    Installs Apache
    """
    print(_yellow("...Initialising Apache..."))

    # for each app
    if not is_sudo():
        mode_sudo()

    for key,value in settings.APPS.items():
        app_settings = AppSettings(key,value)

        t =  loader.get_template('apache_app.txt')
        c = Context({ "server_name":app_settings.server_name, "server_alias": app_settings.server_alias,
                   "app_name":app_settings.app_name, "use_shib":app_settings.use_shib, "shib_id":app_settings.shib_id,
                   "admin_home":settings.ADMIN_HOME
                   })


        package_ensure('libapache2-mod-wsgi')




        file_write(app_settings.app_name+"apache", t.render(c), scp=True)

        run('mv ' + app_settings.app_name+"apache " + "/etc/apache2/sites-available/"+app_settings.app_name)

        file_ensure("/etc/apache2/sites-available/"+app_settings.app_name, mode = "00644", owner ="root", group="root")

        # not sure why this didn't work as run as sudo
        run("a2ensite " + app_settings.app_name)

        # redirectors

        for key,value in settings.REDIRECTS.items():

            t =  loader.get_template('apache_redirect.txt')
            c = Context({ "hostname_from": value['FROM'], "hostname_to": value['TO'] })

            file_write(app_settings.app_name+"-redirect", t.render(c), scp=True)
            run("mv " + app_settings.app_name+"-redirect /etc/apache2/sites-available/"+app_settings.app_name+"-redirect")
            file_ensure("/etc/apache2/sites-available/"+app_settings.app_name+"-redirect",mode = "00644", owner ="root", group="root")
            run("a2ensite " + app_settings.app_name+"-redirect")

        run('a2dissite default')

    return

def init_python():
    """
    Installs all basic packages for Ubuntu
    """
    print(_yellow("...Initialising Python Packages..."))

    if not is_sudo():
        mode_sudo()

    python_package_ensure('django-storages')
    python_package_ensure('boto')
    python_package_ensure('django-celery')
    python_package_ensure('django-celery-email')
    python_package_ensure('pytz')
    package_ensure('python-numpy')
    python_package_ensure('ipython')
    python_package_ensure('ipdb')
    python_package_ensure('django_nose')
    python_package_ensure('django_coverage')
    python_package_ensure('xhtml2pdf')
    python_package_ensure('markdown')



def init_celery():
    """
    Installs Celery
    """

    if (not is_sudo()):
        mode_sudo()

    print(_yellow("...Initialising Celery..."))

    python_package_ensure('django-celery')

    if file_exists("/etc/init.d/celeryd"):
        run("service celeryd stop")
        run("rm /etc/init.d/celeryd")

    if file_exists("/etc/default/celeryd"):
        run("rm /etc/default/celeryd")

    for key,value in settings.APPS.items():
        app_settings = AppSettings(key,value)

        dir_ensure("/opt/"+app_settings.app_name, mode='00777',owner='root',group='root')
        dir_ensure("/opt/"+app_settings.app_name+"/celery", mode='00777',owner='root',group='root')

        # migrate celery db
        cwd = "cd /home/"+settings.ADMIN_USER+"/"+app_settings.app_name+"/main"
        cmd = "./manage.py syncdb --migrate --noinput --database=celery"
        run(cwd+";"+cmd)

        file_ensure("/opt/"+app_settings.app_name+"/celery/celerydb.sqlite",mode='0077',owner='root',group='root')

        # configure celery init script

        t =  loader.get_template('celeryd-init-script.txt')
        c = Context({ "app_name":app_settings.app_name, "admin_home": settings.ADMIN_HOME,
                      "celery_cpu_total": settings.CELERY_CPU_TOTAL, "celery_timeout": settings.CELERY_TIMEOUT,
                      "celery_concurrency": settings.CELERY_CONCURRENCY})

        file_write("/etc/init.d/celeryd-/"+app_settings.app_name, t.render(c),mode = "00755", owner ="root", group="root", scp=True)

        # configure celery config

        t =  loader.get_template('celeryd-init-config.txt')

        file_write("/etc/default/celeryd-/"+app_settings.app_name, t.render(c),mode = "00644", owner ="root", group="root", scp=True)

        # run celery

        run("/etc/init.d/celeryd-"+app_settings.app_name+" start")


def class2go_deploy():
    """
    Deploys Application
    """

    if (not is_sudo()):
        mode_sudo()

    print(_yellow("...Deploying Application..."))

    # for dev

    for key,value in settings.APPS.items():
        app_settings = AppSettings(key,value)

        dir_ensure("/opt/"+app_settings.app_name, mode='00777',owner='root',group='root')
        dir_ensure("/opt/"+app_settings.app_name+"/static", mode='00777',owner='root',group='root')

        # clone git
        # only do this on creation

        if not dir_exists("/home/"+settings.ADMIN_USER+"/"+app_settings.app_name):
            cwd = "cd /home/"+settings.ADMIN_USER+"/"
            cmd = "git clone "+app_settings.git_repo+" "+ app_settings.app_name
            run(cwd+";"+cmd)
            run('chown -R '+ settings.ADMIN_USER + ' ' + app_settings.app_name)

        dir_ensure(app_settings.app_name + "/main/static", mode='00777')
        cwd = "cd /home/"+settings.ADMIN_USER+"/"+app_settings.app_name
        cmd = "git remote prune origin"
        run(cwd+";"+cmd)

        cmd = "git remote update"
        run(cwd+";"+cmd)

        cmd = "git checkout -f "+ app_settings.git_branch
        run(cwd+";"+cmd)

        cmd = "git reset --hard "+ app_settings.git_branch
        run(cwd+";"+cmd)

        cmd = "find . -name \\*.pyc -exec rm {} \\; -print"
        run(cwd+";"+cmd)

def init_dbdump():
    """
    Installs Cron job to dump database daily
    """

    if (not is_sudo()):
        mode_sudo()

    print(_yellow("...Initialising DB Dump..."))

    # noting changes so read?
    t =  loader.get_template('proddump-daily-script.txt')

    c = Context({ "readonly_database":settings.READONLY_DATABASE_INSTANCE, "readonly_database_user": settings.READONLY_DATABASE_USER,
                  "readonly_database_password": settings.READONLY_DATABASE_PASSWORD, "readonly_database_instance": settings.READONLY_DATABASE_INSTANCE })

    file_write("/etc/cron/daily.d/proddump-daily", t.render(c),mode = "00755", owner =settings.ADMIN_USER,
                group=settings.ADMIN_GROUP, scp=True)

def init_database():
    """
    Installs Cron job to dump database daily
    """

    if (not is_sudo()):
        mode_sudo()

    print(_yellow("...Initialising Database Python..."))

    # noting changes so read?
    t =  loader.get_template('database.py.txt')

    for key,value in settings.APPS.items():
        app_settings = AppSettings(key,value)

        c = Context({ "readonly_database":settings.READONLY_DATABASE_INSTANCE,
                  "readonly_database_user": settings.READONLY_DATABASE_USER,
                  "readonly_database_password": settings.READONLY_DATABASE_PASSWORD,
                  "readonly_database_instance": settings.READONLY_DATABASE_INSTANCE,
                  "database_instance": settings.DATABASE_INSTANCE,
                  "database_user": settings.DATABASE_USER,
                  "database_password": settings.DATABASE_PASSWORD,
                  "database_host": settings.DATABASE_HOST,
                  "production": settings.PRODUCTION,
                  "maintenance_landing_page": settings.MAINT,
                  "instance": settings.INSTANCE,
                  "app_name": app_settings.app_name,
                  "admin_name": settings.ADMIN_NAME,
                  "admin_email": settings.ADMIN_EMAIL,
                  "snippet_email": settings.SNIPPET_EMAIL,
                  "aws_access_key": settings.AWS_ACCESS_KEY_ID,
                  "aws_access_secret": settings.AWS_SECRET_ACCESS_KEY,
                  "aws_storage_bucket": settings.STORAGE_BUCKET,
                  "django_secret": settings.DJANGO_SECRET,
                  "piazza_endpoint": settings.PIAZZA_ENDPOINT,
                  "piazza_secret": settings.PIAZZA_SECRET,
                  "piazza_key": settings.PIAZZA_KEY,
                  "smtp_user": settings.SMTP_USER,
                  "smtp_password": settings.SMTP_PASSWORD,
                  "yt_service_developer_key": settings.YT_SERVICE_DEVELOPER_KEY,
                  "google_client_id": settings.GOOGLE_CLIENT_ID,
                  "google_client_secret": settings.GOOGLE_CLIENT_SECRET,
                  "grader_endpoint": settings.GRADER_ENDPOINT
        })

        print settings.ADMIN_USER
        file_write("/home/"+settings.ADMIN_USER+"/"+app_settings.app_name+"/main/database.py", t.render(c),
                    mode = "00644", owner =settings.ADMIN_USER, group=settings.ADMIN_GROUP,scp=True)


    dir_ensure("/opt/assets",mode="00777",owner="root",group="root")


def init_logging():
    """
    Sets up logging
    """
    if (not is_sudo()):
        mode_sudo()

    print(_yellow("...Initialising Logging..."))

    # if dev then logging is in the home directory?

    dir_ensure("class2go/main/logs",mode="00777")
    dir_ensure("/var/log/django",mode="00777",owner="root",group="root")

    for key,value in settings.APPS.items():
        app_settings = AppSettings(key,value)

        file_ensure("class2go/main/logs/"+app_settings.app_name+"-django.log",mode='00666')
        file_ensure("/var/log/django/"+app_settings.app_name+"-django.log",mode='00666',owner='root',group='root')


def init_dns():
    """
    Sets up scripts that will register the machine in DNS
    """

    if (not is_sudo()):
        mode_sudo()

    print(_yellow("...Initialising DNS..."))

    python_package_ensure('boto')
    python_package_ensure('dnspython')

    file_upload('/usr/local/bin/cli53', './files/cli53', scp=True)
    file_ensure('/usr/local/bin/cli53',  mode="00755",owner="root",group="root")

    dir_ensure("/etc/route53",mode="00755",owner="root",group="root")

    t =  loader.get_template('route53-config.txt')

    for key,value in settings.APPS.items():
        app_settings = AppSettings(key,value)

    c = Context({ "aws_access_key": settings.AWS_ACCESS_KEY_ID,
                  "aws_access_secret": settings.AWS_SECRET_ACCESS_KEY,
                  "dns_zone": settings.ZONE,
                  "dns_ttl": settings.TTL
    })

    file_write("config", t.render(c), scp=True)
    run('mv config /etc/route53/config')
    file_ensure("/etc/route53/config", mode='00644', owner ="root", group="root")

    file_upload('update-route53-dns.sh', './files/update-route53-dns.sh')
    run('mv update-route53-dns.sh /usr/sbin/update-route53-dns.sh')
    file_ensure('/usr/sbin/update-route53-dns.sh', mode="00755",owner="root",group="root")

    file_upload('update-route53-dns.conf', './files/update-route53-dns.conf')
    run('mv update-route53-dns.conf /etc/init/update-route53-dns.conf')
    file_ensure('/etc/init/update-route53-dns.conf', mode="00644",owner="root",group="root")


    run('start update-route53-dns')

def run_reports():

    run('cd ./class2go/reports; ./users_by_class.sh')
    cmd = 'scp '+settings.ADMIN_USER+'@'+fabric.api.env.host_string+':~/class2go/reports/users_by_class.png .'
    run_local(cmd)
    sendmail_cmd = 'python ./files/sendmail.py -u ' + settings.REPORT_SMTP_USERNAME + ' -p '+ settings.REPORT_SMTP_PASSWORD +\
                   ' -f ' + settings.REPORT_SMTP_FROM + ' -t ' + settings.REPORT_SMTP_TO + ' -a users_by_class.png ' + \
                   ' -s "Daily report" -m "Daily report"'
    print(sendmail_cmd)
    run_local(sendmail_cmd)

    run('cd ./class2go/reports; ./users_by_day.sh')
    cmd = 'scp '+settings.ADMIN_USER+'@'+fabric.api.env.host_string+':~/class2go/reports/users_by_day.png .'
    run_local(cmd)
    sendmail_cmd = 'python ./files/sendmail.py -u ' + settings.REPORT_SMTP_USERNAME + ' -p '+ settings.REPORT_SMTP_PASSWORD + \
                   ' -f ' + settings.REPORT_SMTP_FROM + ' -t ' + settings.REPORT_SMTP_TO + ' -a users_by_day.png ' + \
                   ' -s "Daily report" -m "Daily report"'
    print(sendmail_cmd)
    run_local(sendmail_cmd)



def init_reporting():

    if (not is_sudo()):
        mode_sudo()

    print(_yellow("...Initialising Reporting..."))

    package_ensure('gnuplot')

    # noting changes so read?
    t =  loader.get_template('my.cnf.txt')

    c = Context({ "readonly_database":settings.READONLY_DATABASE_INSTANCE,
                  "readonly_database_user": settings.READONLY_DATABASE_USER,
                  "readonly_database_password": settings.READONLY_DATABASE_PASSWORD,
                  "readonly_database_instance": settings.READONLY_DATABASE_INSTANCE })

    file_write("/home/"+settings.ADMIN_USER+"/.my.cnf", t.render(c),mode = "00644",
                owner =settings.ADMIN_USER, group=settings.ADMIN_GROUP, scp=True)

    cmd = '* 10 * * 0,7 (cd /home/'+settings.ADMIN_USER+'/class2go/reports; ./users_by_class.sh ' + settings.REPORT_EMAIL + ')'

    run("{ crontab -l -u user; echo" + cmd + "; } | crontab -u user ")

    cmd = '* 10 10 * 0,7 (cd /home/'+settings.ADMIN_USER+'/class2go/reports; ./users_by_day.sh  ' + settings.REPORT_EMAIL + ')'

    run("{ crontab -l -u user; echo" + cmd + "; } | crontab -u user ")

    cmd = '* 10 20 * 0,7 (cd /home/'+settings.ADMIN_USER+'/class2go/main; ./manage.py gen_active_course_reports)'

    run("{ crontab -l -u user; echo" + cmd + "; } | crontab -u user ")


def init_util_kelvinator():

    if (not is_sudo()):
        mode_sudo()

    print(_yellow("...Initialising Util Kelvinator..."))

    package_ensure('libx264-dev')

    run_upload('./files/ffmpeg','/usr/local/bin/ffmpeg')

    file_ensure('/usr/local/bin/ffmpeg', mode="00777",owner="root",group="root")


def init_gdata():

    if (not is_sudo()):
        mode_sudo()

    print(_yellow("...Initialising GData..."))

    package_ensure('libx264-dev')

    file_upload('/tmp/gdata-2.0.17-c2g.tar.gz', './files/gdata-2.0.17-c2g.tar.gz', scp=True)

    file_ensure('/tmp/gdata-2.0.17-c2g.tar.gz', mode="00644",owner="root",group="root")

    # install
    run('cd /tmp; tar zxf gdata-2.0.17-c2g.tar.gz; cd /tmp/gdata-2.0.17; python setup.py install')

    # cleanup
    run('cd /tmp; rm -r gdata-2.0.17; rm gdata-2.0.17-c2g.tar.gz ')


def init_shib():
    """
    Sets up Shibboleth for Apache
    """
    if (not is_sudo()):
        mode_sudo()


    package_ensure("shibboleth-sp2-schemas")
    package_ensure("libshibsp-dev")
    package_ensure("libshibsp-doc")
    package_ensure("libapache2-mod-shib2")

    run("a2enmod shib2")
    package_ensure("opensaml2-tools")

    # "remove shib.conf" do
    run("F=/etc/apache2/conf.d/shib.conf; if [ -e $F ]; then rm $F; fi")

    t =  loader.get_template('shibboleth2.xml.txt')

    c = Context({ "shib_entity_id":settings.SHIB_ID, "shib_sp_key": settings.SHIB_SP_KEY, "shib_sp_cert": settings.SHIB_SP_CERT })

    file_write("/etc/shibboleth/shibboleth2.xml", t.render(c), mode="00644", owner ="root", group="root", scp=True)

    t =  loader.get_template('attribute-map.xml.txt')
    file_write("/etc/shibboleth/attribute-map.xml", t.render(c), mode = "00644", owner ="root", group="root", scp=True)

    t =  loader.get_template('class.pem.txt')
    file_write("/etc/shibboleth/class.pem", t.render(c),mode = "00644", owner ="_shibd", group="_shibd", scp=True)

    t =  loader.get_template('class.key.txt')
    file_write("/etc/shibboleth/class.key", t.render(c),mode = "00600", owner ="_shibd", group="_shibd", scp=True)

    dir_ensure("/etc/shibboleth/metadata",mode='00755', owner='_shibd', group='_shibd')

    contents = file_local_read('./files/Stanford-metadata.xml')
    file_write('/etc/shibboleth/metadata/Stanford-metadata.xml', contents, mode="00644",owner="root",group="root", scp=True)


def init_scalyr():
    """
    Sets up Shibboleth for Apache
    """
    if (not is_sudo()):
        mode_sudo()


    package_ensure("openjdk-6-jre")

    if not dir_exists("/opt/scalyrAgent"):
        if file_exists('/opt/scalyrAgentInstaller.sh'):
            run('rm /opt/scalyrAgentInstaller.sh')
        run('cd /opt; wget https://log.scalyr.com/binaries/scalyrAgentInstaller.sh')
        run('cd /opt; bash ./scalyrAgentInstaller.sh')

    # the Scalyr installer leaves this directory owned by 501:staff for some reason,
    # this is the workaround.

    run('chown -R root:root /opt/scalyrAgent')

    t =  loader.get_template('agentConfig.json.txt')

    c = Context({ })

    file_write("/opt/scalyrAgent/configs/agentConfig.json", t.render(c), owner ="root", group="root",check=False, scp=True)

    t =  loader.get_template('events.properties.txt')

    c = Context({'scalyr_write_key':settings.SCALYR_WRITE_KEY })

    file_write("/opt/scalyrAgent/configs/events.properties", t.render(c), owner ="root", group="root", scp=True)

    run('cd /opt/scalyrAgent; bash agent.sh install_rcinit')


    # Two workarounds here:
    # 1. the Scalyr "rcinit" script doesn't create a runlevel 2 startup entry
    # 2. typically rcX.d scripts should just be symlinks to init.d scripts, so
    #    linking to a script elsewhere is really weird. But this was the only
    #    way to get their init script to survive a reboot.

    file_link( '/opt/scalyrAgent/agent.sh', '/etc/rc2.d/S98scalyr-agent')

    if file_exists('/etc/rc2.d/K55scalyr-agent'):
        run('rm /etc/rc2.d/K55scalyr-agent')

    run('service scalyr-agent --no-interactive start')


def init_collectstatic():
    """
    Runs python job to collectstatic
    """

    if (not is_sudo()):
        mode_sudo()

    print(_yellow("...Initialising Python Collectstatic..."))


    for key,value in settings.APPS.items():
        app_settings = AppSettings(key,value)

        cwd = '/home/'+settings.ADMIN_USER+'/'+app_settings.app_name+'/main'
        cmd = 'python manage.py collectstatic --noinput --clear > /tmp/class2go-collectstatic-'+app_settings.app_name+'.log'

        run('cd '+cwd+';'+cmd);


def apache_restart():
    """
    Restart Apache and Shib if necessary
    """

    if (not is_sudo()):
        mode_sudo()

    print(_yellow("...Restarting Apache & Shib..."))

    run('service apache2 restart')

    if settings.USE_SHIB:
        run('service shibd restart')


def init_s3cmd():
    """
    Sets up AWS S3
    """
    if (not is_sudo()):
        mode_sudo()


    package_ensure("s3cmd")

    dir_ensure("/opt/class2go",mode='00777',owner='ubuntu',group='ubuntu')

    t =  loader.get_template('s3cmd_conf.txt')

    c = Context({ "aws_access_key": settings.AWS_ACCESS_KEY_ID,
                  "aws_access_secret": settings.AWS_SECRET_ACCESS_KEY
                                   })

    file_write("/opt/class2go/s3cmd.conf", t.render(c), mode='00644', owner =settings.ADMIN_USER, group=settings.ADMIN_GROUP, scp=True)




