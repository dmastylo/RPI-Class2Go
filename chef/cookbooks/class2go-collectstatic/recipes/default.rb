node["apps"].keys.each do |app|
    execute "collectstatic: #{app}" do
        cwd node['system']['admin_home'] + "/#{app}/main"
        user node['system']['admin_user']
        command "python manage.py collectstatic --noinput --clear > /tmp/class2go-collectstatic-#{app}.log"
    end
end

