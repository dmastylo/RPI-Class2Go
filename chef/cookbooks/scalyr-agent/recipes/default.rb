package "openjdk-6-jre" do
    action :install
end

if not File.directory? "/opt/scalyrAgent"
    file "/opt/scalyrAgentInstaller.sh" do
        action :delete
    end

    execute  "wget https://log.scalyr.com/binaries/scalyrAgentInstaller.sh" do
        cwd "/opt"
        action :run
    end

    execute "bash ./scalyrAgentInstaller.sh" do
        cwd "/opt"
        action :run
    end
end

# the Scalyr installer leaves this directory owned by 501:staff for some reason,
# this is the workaround.
execute "chown -R root:root /opt/scalyrAgent" do
    action :run
end

template "/opt/scalyrAgent/configs/agentConfig.json" do
    source "agentConfig.json.erb"
    action :create
end

template "/opt/scalyrAgent/configs/events.properties" do
    source "events.properties.erb"
    action :create
end

execute "bash agent.sh install_rcinit" do
    cwd "/opt/scalyrAgent"
    action :run
end

# Two workarounds here:
# 1. the Scalyr "rcinit" script doesn't create a runlevel 2 startup entry
# 2. typically rcX.d scripts should just be symlinks to init.d scripts, so
#    linking to a script elsewhere is really weird. But this was the only
#    way to get their init script to survive a reboot.
link "/etc/rc2.d/S98scalyr-agent" do
    to "/opt/scalyrAgent/agent.sh"
    action :create
end

file "/etc/rc2.d/K55scalyr-agent" do
    action :delete
end

# start the service, if it doesn't start, don't fail the overall install 
execute "service scalyr-agent --no-interactive start" do
    returns [0, 1] 
    action :run
end

