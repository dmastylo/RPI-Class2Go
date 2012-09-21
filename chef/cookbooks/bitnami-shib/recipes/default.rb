# bash the configuration files provided by bitnami so they are useful
# for the particular Sophi EC2 setup.  
#
# This is pretty fragile.  Best to be rewritten, see issue #162.
#
package "shibboleth-sp2-schemas" do
    action :install
end

package "libshibsp-dev" do
    action :install
end

package "libshibsp-doc" do
    action :install
end

package "libapache2-mod-shib2" do
    action :install
end

package "opensaml2-tools" do
    action :install
end

template "shib.conf" do
    path "/home/bitnami/apps/django/conf/shib.conf"
    source "shib.conf.erb"
    owner "bitnami"
    group "bitnami"
    mode "0644"
end

template "shibboleth2.xml" do
    path "/etc/shibboleth/shibboleth2.xml"
    source "shibboleth2.xml.erb"
    owner "root"
    group "root"
    mode "0644"
end

template "attribute-map.xml" do
    path "/etc/shibboleth/attribute-map.xml"
    source "attribute-map.xml.erb"
    owner "root"
    group "root"
    mode "0644"
end

template "sp-key.pem" do
    path "/etc/shibboleth/sp-key.pem"
    source "sp-key.pem.erb"
    owner "_shibd"
    group "_shibd"
    mode "0600"
end

template "sp-cert.pem" do
    path "/etc/shibboleth/sp-cert.pem"
    source "sp-cert.pem.erb"
    owner "_shibd"
    group "_shibd"
    mode "0644"
end
