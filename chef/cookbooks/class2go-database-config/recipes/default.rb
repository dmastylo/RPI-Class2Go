# make /mnt writeable, (see issues #926 and #942)
# Doing here since it is referenced in database.py
directory "/mnt" do
    owner "root"
    group "root"
    mode 001777
    action :create
end

# hardcoding creation of cache directories with right permissions. 
# cache_dirs = ['/mnt/cache-file', '/mnt/cache-video', '/mnt/cache-unused']
# cache_dirs.each do |dir|
#    directory "#{dir}" do
#        owner "root"
#        group "root"
#        mode 00777
#        action :create
#    end
# end

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

