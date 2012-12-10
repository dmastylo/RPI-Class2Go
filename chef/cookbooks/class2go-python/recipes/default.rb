# Sef 7-Aug-2012:
# Initial attempt to install with easy_install caused cryptic failures
# libreadline.so.5 not found...  
# possibly some interop problem with the quirky bitnami python setup?
# don't know but easy_install works, so let's go with that for now.

easy_install_package "django-storages" do
    action :install
end

easy_install_package "boto" do
    action :install
end

easy_install_package "django-celery" do
    action :install
end

easy_install_package "django-celery-email" do
    action :install
end

easy_install_package "pytz" do
    action :install
end


# We need to patch the storage boto backend (see issue #70)

# -N to patch makes it ignore patches already applied.  Even then if one
# patch returns 1 if a block is skipped -- returns 2 if somehing really
# bad happens.  So allow 1 as an OK return code.

bash "patch-boto" do
    code <<-SCRIPT_END
storages_loc_init=`python -c 'import storages; print storages.__file__'`
storages_loc=`dirname ${storages_loc_init}`/backends
echo "Applying patch in ${storages_loc}"
cd $storages_loc

patch -N <<PATCH_END
--- s3boto.py	2012-08-17 17:21:51.000000000 -0700
+++ s3boto.py~	2012-08-17 16:12:34.000000000 -0700
@@ -333,14 +333,14 @@
         # Parse the last_modified string to a local datetime object.
         return _parse_datestring(entry.last_modified)
 
-    def url(self, name):
+    def url(self, name, response_headers=None):
         name = self._normalize_name(self._clean_name(name))
         if self.custom_domain:
             return "%s://%s/%s" % ('https' if self.secure_urls else 'http',
                                    self.custom_domain, name)
         return self.connection.generate_url(self.querystring_expire,
             method='GET', bucket=self.bucket.name, key=self._encode_name(name),
-            query_auth=self.querystring_auth, force_http=not self.secure_urls)
+            query_auth=self.querystring_auth, response_headers=response_headers, force_http=not self.secure_urls)
 
     def get_available_name(self, name):
         """ Overwrite existing file with the same name. """
PATCH_END

rc=$?
echo "patch command returned $rc"
exit $rc
    SCRIPT_END
    
    user "root"
    returns [0, 1]
    action :run
end

package "python-numpy" do
    action :install
end

easy_install_package "ipython" do
    action :install
end

easy_install_package "ipdb" do
    action :install
end

easy_install_package "django_nose" do
    action :install
end

easy_install_package "django_coverage" do
    action :install
end

