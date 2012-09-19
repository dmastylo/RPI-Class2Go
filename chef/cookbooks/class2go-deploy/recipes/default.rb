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

git "class2go-sourcecode" do
    repository "https://github.com/Stanford-Online/class2go.git"
    destination node['system']['admin_home'] + "/class2go"
    user node['system']['admin_user']
    group node['system']['admin_group']
    revision node['main']['git_branch']
    action :sync
end

# To be really super sure that we are on the branch we mean to be on
# go to the directory and do a pull
execute "git checkout" do
    command "git checkout " + node['main']['git_branch']
    cwd node['system']['admin_home'] + "/class2go"
    user node['system']['admin_user']
    group node['system']['admin_group']
    action :run
end

# ... and then do a reset hard HEAD.  This handles the case where we were
# inadvertently ahead of the production branch, which can happen if you 
# happen to be on master first.
execute "git reset hard" do
    command "git reset --hard HEAD"
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
