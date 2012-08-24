#
# Cookbook Name:: class2go-collectstatic
# Recipe:: default
#
# Copyright 2012, Stanford Class2Go
#
# All rights reserved - Do Not Redistribute
#

execute "collectstatic" do
    cwd "/home/bitnami/class2go/main"
    command "python manage.py collectstatic --noinput --clear"
    user "bitnami"
end

