# should be moved to base, if we need to keep at all
package "python-setuptools" do
    action :install
end

package "python-pip" do
    action :install
end

# Now that we are install PIL in the base0cookboook, do we still need this for ffmpeg?
# because we certainly don't need for PIL anymore.
package "python-dev" do
    action :install
end

# this is redundant now
execute "pip pil" do
    command "pip install pil"
    user "root"
    action :run
end

package "libx264-dev" do
    action :install
end

cookbook_file "/usr/local/bin/ffmpeg" do
    owner "root"
    mode 00777
    action :create
end

