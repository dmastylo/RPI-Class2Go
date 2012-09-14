
package "s3cmd" do
    action :install
end


template "dot-s3cfg" do
    path node['system']['admin_home'] + "/.s3cfg"
    source "dot-s3cfg.erb"
    owner node['system']['admin_user']
    owner node['system']['admin_group']
    mode 00600
end

# Write same config file to the root of the daemon user, since that's
# the account that the kelvinator runs as on deployed util machines.
template "dot-s3cfg" do
    path node['system']['admin_home'] + "/.s3cfg"
    source "dot-s3cfg.erb"
    owner "daemon"
    owner "daemon"
    mode 00600
end

