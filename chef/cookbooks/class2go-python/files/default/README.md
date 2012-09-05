django-storages Patch: s3boto_response_header_issue70.patch
===========================================================

We need to apply this patch to the s3boto.py file to allow for the
specification of response headers for S3 file URLs. This feature
then allows us to generate S3 URL download links that will start
download upon user click, rather than opening the file in a different
window. The patch simply adds a response_headers argument to the
url method of the S3BotoStorage class, and the associated boto
generate_url call (which already supports response_headers).

The patch contents have been copied into the recipe file.  So 
if this is being modified, make sure to also update 
    class2go-python/recipes/default.rb


Top apply the patch manually...
------------------
See instructions [here][1].
  [1]: https://github.com/Stanford-Online/class2go/issues/70#issuecomment-7840569
