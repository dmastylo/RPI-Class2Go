file "make ctlscript.sh executible" do
    path "/opt/bitnami/ctlscript.sh"
    mode 00755
    action :create
end

execute "stop apache" do
    command "/opt/bitnami/ctlscript.sh stop apache"
    user "root"
end

execute "sleep 5 seconds" do
    command "sleep 5"
end

execute "start apache" do
    command "/opt/bitnami/ctlscript.sh start apache"
    user "root"
end

execute "restart-shib" do
    command "service shibd restart"
    user "root"
end
