package "sendmail" do
    action :install
end

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

cron "users_by_class" do
    hour "10"   # GMT
    minute "0"
    user node['system']['admin_user']
    command "(cd #{node['system']['admin_home']}/class2go/reports; ./users_by_class.sh olteam@cs.stanford.edu,c2g-dev@cs.stanford.edu,nickm@stanford.edu,pal@cs.stanford.edu,bmc@stanford.edu)"
end

cron "users_by_day" do
    hour "10"   # GMT
    minute "10"
    user node['system']['admin_user']
    command "(cd #{node['system']['admin_home']}/class2go/reports; ./users_by_day.sh olteam@cs.stanford.edu,c2g-dev@cs.stanford.edu,nickm@stanford.edu,pal@cs.stanford.edu,bmc@stanford.edu)"
end

