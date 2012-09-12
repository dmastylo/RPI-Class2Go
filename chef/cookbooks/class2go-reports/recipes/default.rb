package "mpack" do
    action :install
end

package "gnuplot" do
    action :install
end

template "mysql-client-config" do
    path node['system']['admin_home'] + "/.my.cnf"
    source "my.cnf.erb"
    owner node['system']['admin_user']
    group node['system']['admin_group']
    mode 00644
end

