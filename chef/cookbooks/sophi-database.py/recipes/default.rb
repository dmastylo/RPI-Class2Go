#
# Cookbook Name:: sophi-database.py
# Recipe:: default
#
# Copyright 2012, Stanford Sophi
#
# All rights reserved - Do Not Redistribute
#

template "database.py" do
    path "/home/bitnami/sophi/main/database.py"
    source "database.py.erb"
    owner "bitnami"
    group "bitnami"
    mode "0644"
end

