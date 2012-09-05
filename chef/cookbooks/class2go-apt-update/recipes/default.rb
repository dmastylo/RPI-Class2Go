execute "apt-get update" do
    command "apt-get update -q -y"
    action :run
end

# execute "apt-get upgrade" do
    # command "apt-get upgrade -q -y"
    # action :run
# end

