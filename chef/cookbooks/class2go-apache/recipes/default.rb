package "libapache2-mod-wsgi" do
    action :install
end

template "/etc/apache2/conf.d/servername" do
    source "servername.erb"
    owner "root"
    group "root"
    mode 00644
end

template "/etc/apache2/sites-available/class2go" do
    source "class2go-site.erb"
    owner "root"
    group "root"
    mode 00644
end

execute "a2ensite class2go" do
    user "root"
    action :run
end

execute "a2dissite default" do
    user "root"
    action :run
end

cookbook_file "/etc/logrotate.d/apache2" do
    source "logrotate-apache2"
    mode 00644
    owner "root"
    group "root"
    action :create
end

cron "logrotate in root cron" do
    hour   "0"          # GMT
    minute "0" 
    user "root"
    command "logrotate -s /var/log/logrotate.status /etc/logrotate.d/apache2"
    action :create
end
