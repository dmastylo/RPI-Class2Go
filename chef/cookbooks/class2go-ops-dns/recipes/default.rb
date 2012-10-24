# set up the cli53 package

easy_install_package "boto" do
    action :install
end

easy_install_package "dnspython" do
    action :install
end

# cli53 -- command line util to manage settings, just a wrapper around boto.
# instead of being dependendent on this guy's repo, just copy and distribute
# the utility straight from here. see: https://github.com/barnybug/cli53
cookbook_file "/usr/local/bin/cli53" do
    owner "root"
    group "root"
    mode 00755
    action :create
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

