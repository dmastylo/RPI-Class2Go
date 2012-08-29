
package "s3cmd" do
    action :install
end


template "dot-s3cfg" do
    path "/home/bitnami/.s3cfg"
    source "dot-s3cfg.erb"
    owner "bitnami"
    group "bitnami"
    mode "0600"
end

