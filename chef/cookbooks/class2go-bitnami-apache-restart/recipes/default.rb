file "make ctlscript.sh executible" do
    path "/opt/bitnami/ctlscript.sh"
    mode 00755
    action :create
end

execute "restart-apache" do
    command "/opt/bitnami/ctlscript.sh restart apache"
    user "root"
end

execute "restart-shib" do
    command "service shibd restart"
    user "root"
end
