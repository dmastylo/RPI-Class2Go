node["apps"].keys.each do |app|
    template "database.py" do
        path node['system']['admin_home'] + "/#{app}/main/database.py"
        source "database.py.erb"
        owner node['system']['admin_user']
        group node['system']['admin_group']
        variables({ 
            :appname => app
        })
        mode 00644
    end
end

directory "/opt/assets" do
    owner "root"
    mode 00777
    action :create
end

