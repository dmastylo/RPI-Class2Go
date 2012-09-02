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
    action :install
end

easy_install_package "South" do
    action :install
end

easy_install_package "PIL" do
    action :install
end
