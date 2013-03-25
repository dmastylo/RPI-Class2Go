# Default case is just upgrading the package or changing configuration.
# Note that if you case the host's Name tag to change, things will break.
# The easiest fix in this case is to uninstall ejabberd, remove 
# /var/lib/ejabberd, and then re-run chef-client.
WIPE_MNESIA_TABLES = false

if not FileTest.directory?('/var/lib/ejabberd')
    # When the ejabberd package gets installed, ejabberd gets started, and a
    # bunch of mnesia tables get created with the wrong data in them. So if 
    # we've never had ejabberd on this box, we should remember to wipe this 
    # directory during our reconfiguration stage (below).
    WIPE_MNESIA_TABLES = true
end

# Now install ejabberd and dependencies (Big!) with debian-default config
package "ejabberd" do
    action :install
end

# ejabberd is started at installation. Let's stop it while we reconfigure
service "ejabberd" do
    action :stop
end
# Next two stanzas are because ubuntu's service scripts are too dumb to kill
# orphaned erlang processes after their parents crash
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
if WIPE_MNESIA_TABLES
    execute "/bin/rm /var/lib/ejabberd/*" do
        user "root"
        action :run
        returns [0, 1]
    end
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
    mode 00755
    action :create
end

template "/etc/default/ejabberd" do
    source "etc-default-ejabberd.erb"
    owner 'root'
    group 'root'
    mode 00644
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
    mode 00644
end

# Now it's safe to start the server for real
service "ejabberd" do
    action :start
end

