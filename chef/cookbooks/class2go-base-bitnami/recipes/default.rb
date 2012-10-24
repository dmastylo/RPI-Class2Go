file "/etc/hostname" do
  content node.name+".c2gops.com"
end

execute "start hostname" do
    user "root"
    action :run
end

template "/home/bitnami/.bash_aliases" do
    source "bash_aliases.erb"
    owner "bitnami"
    group "bitnami"
    mode "0644"
end

package "git" do
    action :install
end

