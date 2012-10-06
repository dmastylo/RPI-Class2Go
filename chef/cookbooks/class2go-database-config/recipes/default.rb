# make /mnt writeable, (see issues #926 and #942)
# Doing here since it is referenced in database.py
directory "/mnt" do
    owner "root"
    group "root"
    mode 001777
    action :create
end

template "database.py" do
    path node['system']['admin_home'] + "/class2go/main/database.py"
    source "database.py.erb"
    owner node['system']['admin_user']
    group node['system']['admin_group']
    mode 00644
end

