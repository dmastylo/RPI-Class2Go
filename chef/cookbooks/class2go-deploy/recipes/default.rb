#
# Cookbook Name:: class2go-deploy
# Recipe:: default
#
# Copyright 2012, Stanford class2go
#
# All rights reserved - Do Not Redistribute
#

directory "/opt/class2go" do
    owner node['system']['admin_user']
    group node['system']['admin_group']
    mode 00777
    action :create
end

directory "/opt/class2go/static" do
    owner node['system']['admin_user']
    group node['system']['admin_group']
    mode 00777
    action :create
end

execute "git checkout" do
    command "git remote update"
    cwd node['system']['admin_home'] + "/class2go"
    user node['system']['admin_user']
    group node['system']['admin_group']
    action :run
end

# To be really super sure that we are on the branch we mean to be on
# go to the directory and do a pull
execute "git checkout" do
    command "git checkout -f " + node['main']['git_branch']
    cwd node['system']['admin_home'] + "/class2go"
    user node['system']['admin_user']
    group node['system']['admin_group']
    action :run
end

# ... and then do a reset hard <branch>.  Unclear if this is even 
# necessary, just being double-safe
execute "git reset" do
    command "git reset --hard " + node['main']['git_branch']
    cwd node['system']['admin_home'] + "/class2go"
    user node['system']['admin_user']
    group node['system']['admin_group']
    action :run
end


# eventually use the fancier deployment resources
# see http://wiki.opscode.com/display/chef/Deploy+Resource

# deploy "/home/bitnami" do
#  repo "git@github.com/Stanford-Onilne/class2go"
#  revision "HEAD" 
#  user "sefk"
#  enable_submodules true
#  migrate true
#  migration_command "python manage.py migrate "
#  environment "RAILS_ENV" => "production", "OTHER_ENV" => "foo"
#  shallow_clone true
#  action :deploy # or :rollback
#  restart_command "python manage.py restart"
#  git_ssh_wrapper "wrap-ssh4git.sh"
#  scm_provider Chef::Provider::Git
# end
