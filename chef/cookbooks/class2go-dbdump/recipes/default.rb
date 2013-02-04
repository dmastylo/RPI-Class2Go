template "/home/ubuntu/proddump-daily.sh" do
    source "proddump-daily.sh.erb"
    owner "ubuntu"
    group "ubuntu"
    mode 00755
    action :create
end

cron "run proddump-daily at 4AM PST every day" do
    user "ubuntu"
    hour 12
    minute 0
    command "(cd /home/ubuntu; ./proddump-daily.sh)"
    action :create
end

