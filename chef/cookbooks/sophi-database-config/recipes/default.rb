
template "database.py" do
    path node['system']['admin_home'] + "/sophi/main/database.py"
    source "database.py.erb"
    owner node['system']['admin_user']
    group node['system']['admin_group']
    mode 00644
end

