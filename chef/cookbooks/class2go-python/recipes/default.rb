# Sef 7-Aug-2012:
# Initial attempt to install with easy_install caused cryptic failures
# libreadline.so.5 not found...  
# possibly some interop problem with the quirky bitnami python setup?
# don't know but easy_install works, so let's go with that for now.

# execute "install_pip" do
#     command "easy_install pip"
#     user "root"
# end

# following commands used to use "pip install" instead of "easy_install"


execute "install_django_storages" do
    command "easy_install django-storages"
    user "root"
end

execute "install_boto" do
    command "easy_install boto"
    user "root"
end

