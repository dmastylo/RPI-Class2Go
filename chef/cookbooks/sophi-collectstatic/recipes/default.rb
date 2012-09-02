#
# Cookbook Name:: sophi-collectstatic
# Recipe:: default
#
# Copyright 2012, Stanford Sophi
#
# All rights reserved - Do Not Redistribute
#

execute "collectstatic" do
    cwd node['system']['admin_home'] + "/sophi/main"
    user node['system']['admin_user']
    command "python manage.py collectstatic --noinput --clear"
end

