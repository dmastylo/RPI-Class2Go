package "python-setuptools" do
    action :install
end

package "python-pip" do
    action :install
end

package "python-dev" do
    action :install
end

execute "pip pil" do
    command "pip install pil"
    user "root"
    action :run
end

package "ffmpeg" do
    action :install
end

directory "/opt/class2go/kelvinator" do
    owner "root"
    group "root"
    mode 00777
    action :create
end

