# set up the cli53 package

easy_install_package "boto" do
    action :install
end

easy_install_package "dnspython" do
    action :install
end

execute "cli53" do
    user "root"
    creates "/opt/bitnami/python/bin/cli53"
    command "easy_install https://github.com/barnybug/cli53/tarball/master" 
    action :run
end

directory "/etc/route53" do
    owner "root"
    group "root"
    mode 00755
    action :create
end

template "/etc/route53/config" do
    owner "root"
    group "root"
    mode 00644
    source "route53-config.erb"
end
    
cookbook_file "/usr/sbin/update-route53-dns.sh" do
    owner "root"
    group "root"
    mode 00755
    action :create
end

cookbook_file "/etc/init/update-route53-dns.conf" do
    owner "root"
    group "root"
    mode 00644
    action :create
end

execute "start update-route53-dns" do
    user "root"
    action :run
end

