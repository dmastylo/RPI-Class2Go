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

execute "a2enmod shib2" do
    user "root"
    action :run
end

package "opensaml2-tools" do
    action :install
end

execute "remove shib.conf" do
    command "F=/etc/apache2/conf.d/shib.conf; if [ -e $F ]; then rm $F; fi"
    action :run
end

template "shibboleth2.xml" do
    path "/etc/shibboleth/shibboleth2.xml"
    source "shibboleth2.xml.erb"
    owner "root"
    group "root"
    mode 00644
end

template "attribute-map.xml" do
    path "/etc/shibboleth/attribute-map.xml"
    source "attribute-map.xml.erb"
    owner "root"
    group "root"
    mode 00644
end

template "class.key" do
    path "/etc/shibboleth/class.key"
    source "class.key.erb"
    owner "_shibd"
    group "_shibd"
    mode 00600
end

template "class.pem" do
    path "/etc/shibboleth/class.pem"
    source "class.pem.erb"
    owner "_shibd"
    group "_shibd"
    mode 00644
end

directory "/etc/shibboleth/metadata" do
    owner "_shibd"
    group "_shibd"
    mode 00755
    action :create
end

cookbook_file "/etc/shibboleth/metadata/Stanford-metadata.xml" do
    source "Stanford-metadata.xml"
    mode 00644
    owner "_shibd"
    group "_shibd"
    action :create
end
