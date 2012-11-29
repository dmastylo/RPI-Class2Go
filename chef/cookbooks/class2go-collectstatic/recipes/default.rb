node["apps"].keys.each do |app|
    execute "collectstatic" do
        cwd node['system']['admin_home'] + "/#{app}/main"
        user node['system']['admin_user']
        command "python manage.py collectstatic --noinput --clear"
    end
end

