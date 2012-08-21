cookbook_file "/tmp/gdata-2.0.17-c2g.tar.gz" do
  source "gdata-2.0.17-c2g.tar.gz"
  owner "bitnami"
  mode "0644"
  action :create
end

execute "untar" do
  user "bitnami"
  cwd "/tmp"
  command "tar zxf gdata-2.0.17-c2g.tar.gz"
  action :run
end

execute "install" do
  user "bitnami"
  cwd "/tmp/gdata-2.0.17"
  command "sudo python setup.py install"
  action :run
end

execute "cleanup-dir" do
    user "bitnami"
    command "rm -r /tmp/gdata-2.0.17"
    action :run
end

execute "cleanup-tarball" do
    user "bitnami"
    command "rm /tmp/gdata-2.0.17-c2g.tar.gz"
    action :run
end

