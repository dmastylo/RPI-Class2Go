#
# Cookbook Name:: sophi-bitnami-apache-restart
# Recipe:: default
#
# Copyright 2012, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

execute "restart-apache" do
    command "/opt/bitnami/ctlscript.sh restart apache"
    user "root"
end
