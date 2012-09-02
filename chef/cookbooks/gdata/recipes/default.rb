cookbook_file "/tmp/gdata-2.0.17-c2g.tar.gz" do
  source "gdata-2.0.17-c2g.tar.gz"
  owner node['system']['admin_user']
  mode 00644
  action :create
end

execute "untar" do
  user node['system']['admin_user']
  cwd "/tmp"
  command "tar zxf gdata-2.0.17-c2g.tar.gz"
  action :run
end

execute "install" do
  user "root"
  cwd "/tmp/gdata-2.0.17"
  command "python setup.py install"
  action :run
end

execute "cleanup-dir" do
    user node['system']['admin_user']
    command "rm -r /tmp/gdata-2.0.17"
    action :run
end

execute "cleanup-tarball" do
    user node['system']['admin_user']
    command "rm /tmp/gdata-2.0.17-c2g.tar.gz"
    action :run
end

