service "apache2" do
    action :restart
end

service "shibd" do
    action :restart
end
