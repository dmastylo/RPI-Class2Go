#
# Cookbook Name:: class2go-deploy
# Recipe:: default
#
# Copyright 2012, Stanford class2go
#
# All rights reserved - Do Not Redistribute
#
#
node['apps'].keys.each do |app|

    directory "/opt/#{app}" do
        owner node['system']['admin_user']
        group node['system']['admin_group']
        mode 00777
        action :create
    end

    directory "/opt/#{app}/static" do
        owner node['system']['admin_user']
        group node['system']['admin_group']
        mode 00777
        action :create
    end

    # For initial machine bring up, check out the first time.  Doing as a
    # shell script so we can test first.
    bash "git clone: #{app}" do
        user node['system']['admin_user']
        cwd node['system']['admin_home']
        code <<-EOH
        if [[ ! -d #{app} ]]; then
            git clone https://github.com/Stanford-Online/class2go.git #{app}
        fi
        EOH
    end

    execute "git remote prune origin: #{app}" do
        command "git remote prune origin"
        cwd node['system']['admin_home'] + "/#{app}"
        user node['system']['admin_user']
        group node['system']['admin_group']
        action :run
    end

    execute "git remote update: #{app}" do
        command "git remote update"
        cwd node['system']['admin_home'] + "/#{app}"
        user node['system']['admin_user']
        group node['system']['admin_group']
        action :run
    end

    # Be really super sure that we get the revision we want
    execute "git checkout: #{app}" do
        command "git checkout -f " + node['apps'][app]['git_branch']
        cwd node['system']['admin_home'] + "/#{app}"
        user node['system']['admin_user']
        group node['system']['admin_group']
        action :run
    end

    # ... and then do a reset hard <branch>.  Unclear if this is even 
    # necessary, just being double-safe
    execute "git reset: #{app} to #{node['apps'][app]['git_branch']}" do
        command "git reset --hard " + node['apps'][app]['git_branch']
        cwd node['system']['admin_home'] + "/#{app}"
        user node['system']['admin_user']
        group node['system']['admin_group']
        action :run
    end

    # Clear out *.pyc in this tree. Makes sure that file deletions aren't
    # hidden by vestigial compilation products.
    execute "remove all *.pyc: #{app}" do
        command "find . -name \\*.pyc -exec rm {} \\; -print"
        cwd node['system']['admin_home'] + "/#{app}"
        user node['system']['admin_user']
        group node['system']['admin_group']
        action :run
    end

end

