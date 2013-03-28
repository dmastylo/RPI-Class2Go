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

### Now a section that pulls in unicode support for RegexField that has been
### incorporated into django itself (just not the version we run/develop on, 1.4)
### See https://github.com/django/django/pull/101/files and
### https://code.djangoproject.com/ticket/18409 for context

from django import forms
from django.core import validators
import re

def _set_regex_unicode(self, regex):
    if isinstance(regex, basestring):
        regex = re.compile(regex, re.UNICODE)
    self._regex = regex
    if hasattr(self, '_regex_validator') and self._regex_validator in self.validators:
        self.validators.remove(self._regex_validator)
    self._regex_validator = validators.RegexValidator(regex=regex)
    self.validators.append(self._regex_validator)

forms.RegexField._set_regex = _set_regex_unicode
