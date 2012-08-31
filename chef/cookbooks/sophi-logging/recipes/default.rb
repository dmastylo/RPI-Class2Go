# ensure that the Django log directory and file have permissions so that 
# the daemon:daemon user can write to it.  This is how Python is run from
# Apache.
#
# Note that specifying modes needs to be done as five digits.  See
# this chef bug: http://tickets.opscode.com/browse/CHEF-174

directory "/var/log/django" do
    owner "root"
    group "root"
    mode 00777
    action :create
end

file "/var/log/django/django.log" do
    owner "root"
    group "root"
    mode 00666
    action :create
end

# execute "django-log-permissions" do
#    cwd "/var/log/django"
#    user "root"
#    command "chmod 666 django.log"
# end

