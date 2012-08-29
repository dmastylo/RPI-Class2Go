package "python-setuptools" do
    action :install
end

package "python-pip" do
    action :install
end

package "python-dev" do
    action :install
end

# oh, how I wished these worked -- they do on the ubuntu image, but not the
# bitnami one (why!?!).
#
# package "python-numpy" do
#     action :install
# end
# 
# package "python-scipy" do
#     action :install
# end
#

# these instructions helped to see how to get these installed correctly
# so that the BLAS libraries were used
# http://williamjohnbert.com/2012/03/how-to-install-accelerated-blas-into-a-python-virtualenv/

package "liblapack-dev" do
    action :install
end

package "gfortran" do
    action :install
end

execute "pip numpy" do
    command "pip install numpy"
    user "root"
    environment ({ 
        "LAPACK" => "/usr/lib/liblapack.so",
        "ATLAS" => "/usr/lib/libatlas.so",
        "BLAS" => "/usr/lib/libblas.so"
        })
    action :run
end

execute "pip scipy" do
    command "pip install scipy"
    user "root"
    environment ({ 
        "LAPACK" => "/usr/lib/liblapack.so",
        "ATLAS" => "/usr/lib/libatlas.so",
        "BLAS" => "/usr/lib/libblas.so"
        })
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

