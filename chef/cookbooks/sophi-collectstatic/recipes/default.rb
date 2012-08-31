#
# Cookbook Name:: sophi-collectstatic
# Recipe:: default
#
# Copyright 2012, Stanford Sophi
#
# All rights reserved - Do Not Redistribute
#

execute "collectstatic" do
    cwd "/home/bitnami/sophi/main"
    command "python manage.py collectstatic --noinput --clear"
    user "bitnami"
end

