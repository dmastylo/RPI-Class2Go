#
# Cookbook Name:: sophi-deploy
# Recipe:: default
#
# Copyright 2012, Stanford Sophi
#
# All rights reserved - Do Not Redistribute
#

git "/home/bitnami/sophi" do
    repository "https://github.com/Stanford-Online/sophi.git"
    user "bitnami"
    group "root"
    action :sync
end

directory "/opt/sophi" do
    owner "bitnami"
    group "root"
    mode "0755"
    action :create
end

directory "/opt/sophi/static" do
    owner "bitnami"
    group "root"
    mode "0755"
    action :create
end

# eventually use the fancier deployment resources
# see http://wiki.opscode.com/display/chef/Deploy+Resource

# deploy "/home/bitnami" do
#  repo "git@github.com/jbau/sophi"
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
