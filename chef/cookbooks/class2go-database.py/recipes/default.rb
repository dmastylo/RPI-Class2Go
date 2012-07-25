#
# Cookbook Name:: class2go-database.py
# Recipe:: default
#
# Copyright 2012, Stanford Class2Go
#
# All rights reserved - Do Not Redistribute
#

template "database.py" do
    path "/home/bitnami/class2go/django-project/database.py"
    source "database.py.erb"
    owner "bitnami"
    group "bitnami"
    mode "0644"
end

