execute "pip install django-celery" do
    user "root"
    action :run
end

# stop celeryd first explicitly as a one-time cleanup task, since we're renaming
# the service
execute "service celeryd stop" do
    action :run
end

# For now just get rid of the general celery start / stop script.  Eventually we'd
# want to have this helpful interface (start all/ stop all, etc)
file "/etc/init.d/celeryd" do
    action :delete
end

file "/etc/default/celeryd" do
    action :delete
end


node["apps"].keys.each do |app|

    directory "/opt/#{app}/celery" do
        owner "root"
        group "root"
        mode 00777
        action :create
    end

    execute "celery worker local database (#{app})" do
        cwd node['system']['admin_home'] + "/#{app}/main"
        user "root"
        command "./manage.py syncdb --migrate --noinput --settings=settings_util"
        action :run
    end

    file "celery database file permissions (#{app})" do
        path "/opt/#{app}/celery/celerydb.sqlite"
        mode 00777
        owner "daemon"
        group "daemon"
        action :create
    end

    cookbook_file "celeryd-#{app} init script" do
        source "celeryd-init-script"
        path "/etc/init.d/celeryd-#{app}"
        owner "root"
        group "root"
        mode 00755
        action :create
    end

    template "celeryd-#{app} init config" do
        source "celeryd-init-config.erb"
        path "/etc/default/celeryd-#{app}"
        owner "root"
        group "root"
        mode 00644
        variables = { "appname" => app }
        action :create
    end

    service "celeryd-#{app}" do
        start_command "/etc/init.d/celeryd-#{app} start"
        supports :status => true, :restart => true, :reload => true
        action [ :enable, :restart ]
    end

end
