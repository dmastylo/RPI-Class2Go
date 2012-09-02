#
# Cookbook Name:: sophi-util-database-config
# Recipe:: default
#
# Copyright 2012, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#
#
template "database_util.py" do
    path node['system']['admin_home'] + "/sophi/main/database_util.py"
    source "database_util.py.erb"
    owner "ubuntu"
    group "ubuntu"
    mode "0644"
end
