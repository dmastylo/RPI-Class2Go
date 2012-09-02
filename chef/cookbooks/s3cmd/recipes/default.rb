
package "s3cmd" do
    action :install
end


template "dot-s3cfg" do
    path node['system']['admin_home'] + "/.s3cfg"
    source "dot-s3cfg.erb"
    owner node['system']['admin_user']
    owner node['system']['admin_group']
    mode 00644
end

