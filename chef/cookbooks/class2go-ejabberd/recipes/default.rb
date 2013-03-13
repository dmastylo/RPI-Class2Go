# Installing ejabberd and configuring it is fiddly. A lot of material gets 
# created when it's nonexistent, which gives things a slightly magical feeling,
# and not in a good way. Its especially problematic if you start ejabberd with
# one set of settings (such as hostname), and then restart it later with a
# different set. The following set of steps are in the following order because
# this seems to satisfy the requirements for having working ejabberd most
# easily.
#
# This set of recipes must be run after base-ubuntu, so we have a hostname.

# Remove ejabberd and completely destroy existing configuration 
# before doing other things
service "ejabberd" do
    action :stop
end
package "ejabberd" do
    action :purge
end

# Now install ejabberd and dependencies (Big!) with debian-default config
package "ejabberd" do
    action :install
end

# ejabberd is started at installation; stop it and wipe runtime files so we
# can reconfigure
service "ejabberd" do
    action :stop
end
execute "/usr/bin/killall beam" do
    user "root"
    action :run
    returns [0, 1]
end
execute "/usr/bin/killall epmd" do
    user "root"
    action :run
    returns [0, 1]
end
execute "/bin/rm -rf /var/lib/ejabberd/*" do
    user "root"
    action :run
    returns [0, 1]
end

# Configure ejabberd with our preferred settings
directory "/etc/ejabberd" do
    owner "root"
    group "ejabberd"
    mode 00750
    action :create
end

directory "/etc/default" do
    owner 'root'
    group 'root'
    mode '0755'
    action :create
end

template "/etc/default/ejabberd" do
    source "etc-default-ejabberd.erb"
    owner 'root'
    group 'root'
    mode '0644'
end

template "/etc/ejabberd/ejabberd.cfg" do
    source "etc-ejabberd-ejabberd.cfg.erb"
    owner "ejabberd"
    group "ejabberd"
    mode 00600
end

cookbook_file "/etc/ejabberd/inetrc" do
    source "etc-ejabberd-inetrc"
    owner "ejabberd"
    group "ejabberd"
    mode "0644"
end

# Ok, now it should start ok. Run the ejabberd server
service "ejabberd" do
    action :start
end

