cookbook_file "/tmp/gdata-2.0.17.tar.gz" do
  source "gdata-2.0.17.tar.gz"
  owner "bitnami"
  mode "0644"
  action :create
end

execute "untar" do
  user "bitnami"
  cwd "/tmp"
  command "tar zxf gdata-2.0.17.tar.gz"
  action :run
end

execute "install" do
  user "bitnami"
  cwd "/tmp/gdata-2.0.17"
  command "sudo python setup.py install"
  action :run
end
