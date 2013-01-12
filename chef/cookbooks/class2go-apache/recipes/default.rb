package "libapache2-mod-wsgi" do
    action :install
end

# We have confirmed that we no longer need the servername file since 
# servers are getting set up correctly in the vhosts file.  If it was
# there before, clear it out, just causes trouble
if File.exists?("/etc/apache2/conf.d/servername") 
    file "/etc/apache2/conf.d/servername" do
        action :delete
    end
end

### Create Class2Go Main Apps ###

node["apps"].keys.each do |app|

    template "/etc/apache2/sites-available/#{app}" do
        source "class2go-site.erb"
        owner "root"
        group "root"
        variables({
            :servername => node["apps"][app]["servername"], 
            :serveralias => node["apps"][app]["serveralias"], 
            :shib_id => node["apps"][app]["shib_id"],
            :appname => app
        })
        mode 00644
    end

    execute "a2ensite #{app}" do
        user "root"
        action :run
    end

end

### Redirectors ###

if node.has_key?("redirects")
    node["redirects"].keys.each do |app|

        redir_apache_conf="#{app}-redirect"
        template "/etc/apache2/sites-available/#{redir_apache_conf}" do
            source "site-redirect.erb"
            owner "root"
            group "root"
            variables({
                :hostname_from => node["redirects"][app]["from"],
                :hostname_to => node["redirects"][app]["to"]
            })
            mode 00644
        end

        execute "a2ensite #{redir_apache_conf}" do
            user "root"
            action :run
        end

    end
end

### Turn off apache default site ###

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

# WTOP

cookbook_file "/tmp/wtop-0.6.3.tar.gz" do
    owner "root"
    action :create
end

bash "install wtop" do
    user "root"
    cwd "/tmp"
    code <<-EOH
        prior=/usr/local/bin/wtop
        if [ -e $prior ]; then
            echo "$prior already exists, skipping install"
        else
            tar -zxf wtop-0.6.3.tar.gz
            cd wtop-0.6.3
            python setup.py install
        fi
    EOH
    action :run
end

# do last so it clobbers whatever default the bundle came with

template "/etc/wtop.cfg" do
    source "wtop.cfg.erb"
    owner "root"
    group "root"
    mode 00644
end

