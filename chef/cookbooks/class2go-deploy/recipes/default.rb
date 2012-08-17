#
# Cookbook Name:: class2go-deploy
# Recipe:: default
#
# Copyright 2012, Stanford Class2Go
#
# All rights reserved - Do Not Redistribute
#

git "/home/bitnami/class2go" do
    repository "https://github.com/Stanford-Online/class2go.git"
    user "bitnami"
    group "root"
    action :sync
end

directory "/opt/class2go" do
    owner "bitnami"
    group "root"
    mode "0755"
    action :create
end

directory "/opt/class2go/static" do
    owner "bitnami"
    group "root"
    mode "0755"
    action :create
end

# eventually use the fancier deployment resources
# see http://wiki.opscode.com/display/chef/Deploy+Resource

# deploy "/home/bitnami" do
#  repo "git@github.com/jbau/class2go"
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
