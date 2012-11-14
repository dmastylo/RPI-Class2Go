package "libapache2-mod-wsgi" do
    action :install
end

cookbook_file "/etc/apache2/sites-available/class2go" do
    mode 00644
    action :create
end

link "/etc/apache2/sites-enabled/000-default" do
    to "/etc/apache2/sites-available/class2go"
    link_type :symbolic
    action :create
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
