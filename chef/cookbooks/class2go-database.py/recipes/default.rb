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
    variables(
        # TODO - should come from environment
        :database_host => "c2g-stage-appdb1.czjqjb57rejd.us-west-2.rds.amazonaws.com"
    )
    owner "bitnami"
    group "bitnami"
    mode "0644"
end

