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


# We need to patch the storage boto backend (see issue #70)
# I think it's OK to leave the patch file around 

cookbook_file "/tmp/s3boto_response_header_issue70.patch" do
    source "s3boto_response_header_issue70.patch"
    owner "root"
    group "root"
    mode 0644
    action :create
end

execute "patch_storages_boto_backend" do
    cwd "/opt/bitnami/python/lib/python2.7/site-packages/django_storages-1.1.5-py2.7.egg/storages/backends"
    user "root"
    # -N to patch makes it ignore patches already applied.  Even then if one
    # patch returns 1 if a block is skipped -- returns 2 if somehing really
    # bad happens.  So allow 1 as an OK return code
    command "patch -N < /tmp/s3boto_response_header_issue70.patch"
    returns [0, 1]
    action :run
end

