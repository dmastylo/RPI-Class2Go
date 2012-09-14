
package "s3cmd" do
    action :install
end

# the recipe class2go-deploy also creates this directory today, so
# this is redundant.  But don't like creating that dependency, 
# especially since we may not want that code to live in "deploy"
# long term.
directory "/opt/class2go" do
    owner node['system']['admin_user']
    group node['system']['admin_group']
    mode 00777
    action :create
end

template "s3cfg.conf" do
    path "/opt/class2go/s3cfg.conf"
    source "s3cfg_conf.erb"
    owner node['system']['admin_user']
    owner node['system']['admin_group']
    mode 00644
end

