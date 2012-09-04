
execute "collectstatic" do
    cwd node['system']['admin_home'] + "/class2go/main"
    user node['system']['admin_user']
    command "python manage.py collectstatic --noinput --clear"
end

