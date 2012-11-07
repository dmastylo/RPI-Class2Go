package "libapache2-mod-wsgi" do
    action :install
end

cookbook_file "/etc/apache2/sites-available/class2go" do
    mode 00644
    action :create
end

link "/etc/apache2/sites-enabled/000-default" do
    to "/etc/apache2/sites-available/class2go"
    link_type :symbolic
    action :create
end


