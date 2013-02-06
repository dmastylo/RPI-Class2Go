# Sef 7-Aug-2012:
# Initial attempt to install with pip caused cryptic failures
# libreadline.so.5 not found...  
# possibly some interop problem with the quirky bitnami python setup?
# don't know but easy_install works, so let's go with that for now.

easy_install_package "django-storages" do
    options "-U"
    version "1.1.6"
    action :install
end

easy_install_package "boto" do
    options "-U"
    version "2.7.0"
    action :install
end

easy_install_package "django-celery" do
    action :install
end

easy_install_package "django-celery-email" do
    action :install
end

easy_install_package "pytz" do
    action :install
end

package "python-numpy" do
    action :install
end

easy_install_package "ipython" do
    action :install
end

easy_install_package "ipdb" do
    action :install
end

easy_install_package "django_nose" do
    action :install
end

easy_install_package "django_coverage" do
    action :install
end

easy_install_package "xhtml2pdf" do
    action :install
end

easy_install_package "markdown" do
    action :install
end
