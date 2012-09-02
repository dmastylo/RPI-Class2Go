cookbook_file "/tmp/gdata-2.0.17-c2g.tar.gz" do
  source "gdata-2.0.17-c2g.tar.gz"
  owner "root"
  mode 00644
  action :create
end

bash "install gdata" do
    cwd "/tmp"
    user "root"
    code <<-EOS
        tar zxf gdata-2.0.17-c2g.tar.gz
        cd /tmp/gdata-2.0.17
        python setup.py install
    EOS
    action :run
end

bash "cleanup gdata install" do
    cwd "/tmp"
    user "root"
    code <<-EOS
        rm -r /tmp/gdata-2.0.17
        rm /tmp/gdata-2.0.17-c2g.tar.gz
    EOS
    action :run
end
