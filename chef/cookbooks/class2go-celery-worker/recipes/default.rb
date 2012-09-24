directory "/opt/class2go/celery" do
    owner "root"
    group "root"
    mode 00777
    action :create
end

execute "pip install django-celery" do
    user "root"
    action :run
end

execute "celery worker local database setup" do
    cwd node['system']['admin_home'] + "/class2go/main"
    user "root"
    command "./manage.py syncdb --migrate --noinput --settings=settings_util"
    action :run
end

file "celery database file permissions" do
    path "/opt/class2go/celery/celerydb.sqlite"
    mode 00777
    owner "daemon"
    group "daemon"
    action :create
end

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
    mode 00644
    action :create
end

service "celeryd" do
    start_command "/etc/init.d/celeryd start"
    supports :status => true, :restart => true, :reload => true
    action [ :enable, :start ]
end
