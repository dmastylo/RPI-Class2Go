#
# Cookbook Name:: bitnami-for-class2go
# Recipe:: default
#
# Cribbed from http://reiddraper.com/first-chef-recipe/
#

template "httpd.conf" do
    path "/home/bitnami/stack/apache2/conf/httpd.conf"
    source "httpd.conf.erb"
    owner "bitnami"
    group "bitnami"
    mode "0644"
end

template "django.conf" do
    path "/home/bitnami/apps/django/conf/django.conf"
    source "django.conf.erb"
    owner "bitnami"
    group "bitnami"
    mode "0644"
end

template "django.wsgi" do
    path "/home/bitnami/apps/django/scripts/django.wsgi"
    source "django.wsgi.erb"
    owner "bitnami"
    group "bitnami"
    mode "0644"
end

template "database.py" do
    path "/home/bitnami/class2go/django-project/database.py"
    source "database.py.erb"
    variables(
        :database_host => "c2g-stage-appdb1.czjqjb57rejd.us-west-2.rds.amazonaws.com"
    )
    owner "bitnami"
    group "bitnami"
    mode "0644"
end

execute "restart-apache" do
    command "apachectl restart"
    user "root"
end
