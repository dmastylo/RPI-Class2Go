"""monkeypatch: the module of extreme evil.

When you find yourself tempted to patch a system library, go ahead and do that.
But then submit your code upstream. While you're waiting for review, add a 
monkeypatch here.
"""

def s3boto_dlurl(self, name, response_headers=None):
    """Just like s3boto.url(), but it supports response_headers setting.
    
    This method is monkeypatched onto the class class2go/main/monkeypatch.py
    """
    name = self._normalize_name(self._clean_name(name))
    if self.custom_domain:
        return "%s://%s/%s" % ('https' if self.secure_urls else 'http',
                               self.custom_domain, name)
    return self.connection.generate_url(self.querystring_expire,
            method='GET', response_headers=response_headers, 
            bucket=self.bucket.name, key=self._encode_name(name),
            query_auth=self.querystring_auth, force_http=not self.secure_urls)
import storages.backends.s3boto
storages.backends.s3boto.S3BotoStorage.url_monkeypatched = s3boto_dlurl

