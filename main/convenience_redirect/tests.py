"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from convenience_redirect.redirector import convenience_redirector
from django.test.client import RequestFactory
from django.http import HttpResponseRedirect

class SimpleTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.redir = convenience_redirector()

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
    
    def test_noop(self):
        for host in ('class.stanford.edu', 'www.class.stanford.edu', 'staging.class.stanford.edu', 'www.staging.class.stanford.edu'):
            request = self.factory.get('/')
            request.META['HTTP_HOST']=host
            response = self.redir.process_request(request)
            self.assertIsNone(response)
    
    def test_malformed(self):
        for host in ('www.cnn.com', 'cs144.stanford.edu', 'class.stanford.edu.au', 'bad.prefix.class.stanford.edu'):
            request = self.factory.get('/')
            request.META['HTTP_HOST']=host
            response = self.redir.process_request(request)
            self.assertIsNone(response)

    def test_class_networking(self):
        #HTTP to '/'
        request = self.factory.get('/')
        request.META['HTTP_HOST']='networking.class.stanford.edu'
        response = self.redir.process_request(request)
        self.assertTrue(isinstance(response,HttpResponseRedirect))
        self.assertEqual(response['Location'],'http://class.stanford.edu/networking/Fall2012/')
        #HTTPS
        request.is_secure=lambda: True
        response = self.redir.process_request(request)
        self.assertTrue(isinstance(response,HttpResponseRedirect))
        self.assertEqual(response['Location'],'https://class.stanford.edu/networking/Fall2012/')

    def test_url_paths_and_params(self):
        #path
        request = self.factory.get('/videos/TheInternet/')
        request.META['HTTP_HOST']='networking.class.stanford.edu'
        response = self.redir.process_request(request)
        self.assertTrue(isinstance(response,HttpResponseRedirect))
        self.assertEqual(response['Location'],'http://class.stanford.edu/networking/Fall2012/videos/TheInternet/')
        #query param
        request = self.factory.get('/preview/?login=login&cnn=cnn')
        request.META['HTTP_HOST']='networking.class.stanford.edu'
        response = self.redir.process_request(request)
        self.assertTrue(isinstance(response,HttpResponseRedirect))
        self.assertEqual(response['Location'],'http://class.stanford.edu/networking/Fall2012/preview/?login=login&cnn=cnn')
        #query param2
        request = self.factory.get('?a=a;b=b')
        request.META['HTTP_HOST']='networking.class.stanford.edu'
        response = self.redir.process_request(request)
        self.assertTrue(isinstance(response,HttpResponseRedirect))
        self.assertEqual(response['Location'],'http://class.stanford.edu/networking/Fall2012/?a=a;b=b')


    def test_staging_networking(self):
        #HTTP to '/'
        request = self.factory.get('/')
        request.META['HTTP_HOST']='networking.staging.class.stanford.edu'
        response = self.redir.process_request(request)
        self.assertTrue(isinstance(response,HttpResponseRedirect))
        self.assertEqual(response['Location'],'http://staging.class.stanford.edu/networking/Fall2012/')
        #HTTPS
        request.is_secure=lambda: True
        response = self.redir.process_request(request)
        self.assertTrue(isinstance(response,HttpResponseRedirect))
        self.assertEqual(response['Location'],'https://staging.class.stanford.edu/networking/Fall2012/')
   
    
    def test_ports(self):
        #HTTP 80
        request = self.factory.get('/')
        request.META['HTTP_HOST']='networking.class.stanford.edu:80'
        response = self.redir.process_request(request)
        self.assertTrue(isinstance(response,HttpResponseRedirect))
        self.assertEqual(response['Location'],'http://class.stanford.edu/networking/Fall2012/')
        #HTTPS 443
        request = self.factory.get('/')
        request.META['HTTP_HOST']='networking.class.stanford.edu:443'
        request.is_secure=lambda: True
        response = self.redir.process_request(request)
        self.assertTrue(isinstance(response,HttpResponseRedirect))
        self.assertEqual(response['Location'],'https://class.stanford.edu/networking/Fall2012/')
        #HTTP 8080
        request = self.factory.get('/')
        request.META['HTTP_HOST']='networking.class.stanford.edu:8080'
        response = self.redir.process_request(request)
        self.assertTrue(isinstance(response,HttpResponseRedirect))
        self.assertEqual(response['Location'],'http://class.stanford.edu:8080/networking/Fall2012/')
        #HTTPS 4443
        request = self.factory.get('/')
        request.META['HTTP_HOST']='networking.class.stanford.edu:4443'
        request.is_secure=lambda: True
        response = self.redir.process_request(request)
        self.assertTrue(isinstance(response,HttpResponseRedirect))
        self.assertEqual(response['Location'],'https://class.stanford.edu:4443/networking/Fall2012/')

    def test_active_classes(self):
        for course in ('nlp','test','networking','crypto','security','cs144','cs224n','solar','matsci256','psych30','nano','msande111'):
            request = self.factory.get('/')
            request.META['HTTP_HOST']=course+'.class.stanford.edu'
            response = self.redir.process_request(request)
            self.assertTrue(isinstance(response,HttpResponseRedirect))
            self.assertEqual(response['Location'],"http://class.stanford.edu/%s/Fall2012/" % course)
        