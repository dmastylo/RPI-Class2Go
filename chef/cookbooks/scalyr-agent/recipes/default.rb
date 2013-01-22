package "openjdk-6-jre" do
    action :install
end

cookbook_file "/opt/scalyrAgentInstaller.sh" do
    mode 00755
    action :create
end

execute "bash scalyrAgentInstaller.sh" do
    cwd "/opt"
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

execute "service scalyr-agent start" do
    action :run
end

