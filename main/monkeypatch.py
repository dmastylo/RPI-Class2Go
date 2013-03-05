"""monkeypatch: the module of extreme evil.

When you find yourself tempted to patch a system library, go ahead and do that.
But then submit your code upstream. While you're waiting for review, add a 
monkeypatch here.
"""


def s3boto_dlurl(self, name, response_headers=None, querystring_auth=True):
    """Copy s3boto.S3BotoStorage.url() implementation with flexibility.
    
    response_headers is normally unsupported, but useful for creating URLs
    that point to resources with peculiar configurations, i.e., 
    'content-disposition': 'attachment'.

    querystring_auth is normally configured on S3BotoStorage via the
    environment, but defaults to True and it's handy to be able to override on
    a per-model basis.
    """
    name = self._normalize_name(self._clean_name(name))
    if self.custom_domain:
        return "%s://%s/%s" % ('https' if self.secure_urls else 'http',
                               self.custom_domain, name)
    # If response_headers are set, use class-default querysting_auth behavior
    if response_headers is not None:
        querystring_auth = self.querystring_auth

    return self.connection.generate_url(self.querystring_expire,
            method='GET', response_headers=response_headers, 
            bucket=self.bucket.name, key=self._encode_name(name),
            query_auth=querystring_auth, force_http=not self.secure_urls)
import storages.backends.s3boto
storages.backends.s3boto.S3BotoStorage.url_monkeypatched = s3boto_dlurl


