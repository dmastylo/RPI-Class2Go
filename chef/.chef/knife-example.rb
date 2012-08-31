current_dir = File.dirname(__FILE__)
log_level                :info
log_location             STDOUT
node_name                "sefk"
client_key               "#{current_dir}/sefk.pem"
validation_client_name   "sophi-validator"
validation_key           "#{current_dir}/sophi-validator.pem"
chef_server_url          "https://api.opscode.com/organizations/sophi"
cache_type               'BasicFile'
cache_options( :path => "#{ENV['HOME']}/.chef/checksums" )
cookbook_path            ["#{current_dir}/../cookbooks"]

knife[:aws_ssh_key_id] = "c2g-stag-20120619"
knife[:aws_access_key_id]     = "AKIAIYES3HTY3TOMHCTQ"
knife[:aws_secret_access_key] = "SECRET_FROM_AWS_FOR_CLASS2GO_ACCOUNT"
knife[:region]           = "us-west-2"

