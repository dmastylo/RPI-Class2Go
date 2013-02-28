# The interactive graders expect there to be a database table
# for caching grader results.  Create that here.  This will 
# almost always fail because the table already exists, that is
# expected and OK.
#
# When the manage command fails with
#     Cache table 'grader_cache' could not be created.
#     The error was: (1050, "Table 'grader_cache' already exists").
# the manage.py command still has retcode=0.
#
# Currently we only support one database but multiple apps, but
# eventually we will support per-app databases.  So although 
# this is redundant today, it's the safer way to do it -- 
# otherwise how to know what app to use?

node["apps"].keys.each do |app|
    execute "create cache table: #{app}" do
        cwd node['system']['admin_home'] + "/#{app}/main"
        user node['system']['admin_user']
        command "python manage.py createcachetable grader_cache > /tmp/class2go-createcachetable-#{app}.log"
    end
end
