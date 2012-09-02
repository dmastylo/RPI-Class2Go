directory "/opt/sophi/celery" do
    owner "root"
    group "root"
    mode 00777
    action :create
end

execute "pip install django-celery" do
    user "root"
    action :run
end

execute "celery worker db setup" do
    cwd node['system']['admin_home'] + "/sophi/main"
    user "root"
    command "./manage.py syncdb --migrate --noinput --settings=settings_util"
    action :run
end

# TODO: turn in to a proper service
# - maybe use the chef "service" resource
# - or consider using python-daemon module
# - or maybe the celery command line?
#
# Maybe use this as an example? 
#   http://stackoverflow.com/questions/9938314/chef-how-to-run-a-template-that-creates-a-init-d-script-before-the-service-is-c
#
# it appears that just trying to put in the background like this won't work, most 
# likely because this isn't running in an interactive shell
#
# execute "celery worker start" do
#    cwd node['system']['admin_home'] + "/sophi/main"
#    user "root"
#    command "./manage.py celery worker --loglevel=info --settings=settings_util &"
#    action :run
#end

cookbook_file "celeryd init script" do
    source "celeryd-init-script"
    path "/etc/init.d/celeryd"
    owner "root"
    group "root"
    mode 00755
    action :create
end

template "celeryd init config" do
    source "celeryd-init-config"
    path "/etc/default/celeryd"
    owner "root"
    group "root"
    mode 00755
    action :create
end

service "celeryd" do
    start_command "/etc/init.d/celeryd start --settings=settings_util"
    supports :status => true, :restart => true, :reload => true
    action [ :enable, :start ]
end
