# bash the configuration files provided by bitnami so they are useful
# for the particular Sophi EC2 setup.  
#
# This is pretty fragile.  Best to be rewritten, see issue #162.
#

template "httpd.conf" do
    path "/home/bitnami/stack/apache2/conf/httpd.conf"
    source "httpd.conf.erb"
    owner "bitnami"
    group "bitnami"
    mode "0644"
end

template "django.conf" do
    path "/home/bitnami/apps/django/conf/django.conf"
    source "django.conf.erb"
    owner "bitnami"
    group "bitnami"
    mode "0644"
end

template "django.wsgi" do
    path "/home/bitnami/apps/django/scripts/django.wsgi"
    source "django.wsgi.erb"
    owner "bitnami"
    group "bitnami"
    mode "0644"
end

# need to make this directory writeable by all since it's where python
# eggs get written to.  Both the daemon and bitnami accounts use this.
directory "python-egg-dir" do
    path "/opt/bitnami/.tmp"
    mode "0777"
    owner "root"
    action :create
end

# I don't know why bitnami stores their log files in a quirky place, but
# the apache rotation script they ship with still goes to the old place
# (/var/log/apache2).  
cookbook_file "/etc/logrotate.d/apache2" do
    source "logrotate-apache2"
    owner "root"
    group "root"
    mode 00644
    action :create
end 

cron "logrotate in root cron" do
    hour   "9"          # GMT
    minute "0"
    user "root"
    command "logrotate -s /var/log/logrotate.status /etc/logrotate.d"
    action :create
end

