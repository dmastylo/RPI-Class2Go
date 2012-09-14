
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

# Write same config file daemon user's home dir (/usr/sbin) (!), since that's
# the account that the kelvinator runs as on deployed util machines.
#
# TODO: once @halawa's changes are done, consider putting outside homedirs
# and referencing explicitly with the --config option to s3cmd.  Or just 
# start using the s3 API properly.

template "dot-s3cfg" do
    path "/usr/sbin/.s3cfg"
    source "dot-s3cfg.erb"
    owner "daemon"
    owner "daemon"
    mode 00600
end

