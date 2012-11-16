file "/etc/hostname" do
  content node.name+".c2gops.com"
end

execute "start hostname" do
    user "root"
    action :run
end

template "/home/ubuntu/.bash_aliases" do
    source "bash_aliases.erb"
    owner "ubuntu"
    group "ubuntu"
    mode "0644"
end

package "git" do
    action :install
end

# this one is massive but needed for PIL later
package "python-dev" do
    action :install
end

package "mysql-client" do
    action :install
end

package "python-pip" do
    action :install
end

# this will apt-get this package. Tried doing a pip instll of it, didn't work.
package "python-mysqldb" do
    action :install
end

easy_install_package "django" do
    version "1.4.1"
    action :install
end

# For now let this version float.  We use 0.7.6 now.
easy_install_package "South" do
    action :install
end

## Imaging -- a bit tricky

package "libjpeg-dev" do
    action :install
end

# PIL cannot find libjpeg without setting up this symlink.  Solution found here:
# http://jj.isgeek.net/2011/09/install-pil-with-jpeg-support-on-ubuntu-oneiric-64bits/
link "/usr/lib/libjpeg.so" do
    link_type :symbolic
    owner "root"
    group "root"
    to "/usr/lib/x86_64-linux-gnu/libjpeg.so"
end

easy_install_package "PIL" do
    action :install
end

# Use lynx to flatten out HTML emails
package "lynx-cur" do
    action :install
end

