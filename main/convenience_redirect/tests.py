"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from convenience_redirect.redirector import convenience_redirector
from django.test.client import RequestFactory
from django.http import HttpResponseRedirect
from c2g.models import CurrentTermMap, Course
from random import randrange
from django.contrib.auth.models import User,Group

class SimpleTest(TestCase):
    #for a ton of URLs in our system that should not get redirects (b/c they are not course specific), make sure they don't redirect
    no_course_paths = ['/_health', '/_throw500', '/_throw404', '/email_optout/afda923sdmadf/', '/shib-login', '/impersonate/jbau@stanford.edu',
                      '/videos/save/', '/accounts/login/', '/accounts/logout/', '/accounts/profile/save/', '/admin/', '/admin/doc/', '/courses/new/',
                      '/commit', '/revert/', '/change_live_datetime/', '/save_order/', '/content_section/get_children/2342/',
                      'content_section/get_children_as_contentgroup_parents/155/?', '/']

    #These paths should be redirected if preceded by /course_prefix/course_suffix, or if the host is a convenience redirect
    course_path_endings = ['/videos/', '/exams/', '/surveys', '/exams/abcd/submit/', '/', '/surveys/abcd/', '/exams/abcd/record/23/',
                              '/problemsets/test/record/55']


    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.redir = convenience_redirector()
        #db class map
        m1 = CurrentTermMap(course_prefix="db", course_suffix="Winter2013")
        m1.save()
        m2 = CurrentTermMap(course_prefix="class2go", course_suffix="tutorial")
        m2.save()
        m3 = CurrentTermMap(course_prefix="EE364A", course_suffix="Winter2013")
        m3.save()
        for (course,suffix) in (('nlp','Fall2012'),
                                ('test','Fall2012'),
                                ('networking','Fall2012'),
                                ('crypto','Fall2012'),
                                ('security','Fall2012'),
                                ('cs144','Fall2012'),
                                ('cs224n','Fall2012'),
                                ('solar','Fall2012'),
                                ('matsci256','Fall2012'),
                                ('psych30','Fall2012'),
                                ('nano','Fall2012'),
                                ('msande111','Fall2012'),
                                ('db','Winter2013'),
                                ('class2go','tutorial'),
                                ('EE364A','Winter2013'),
                                ):
            
            ### Create the new Course ###
            r = randrange(0,100000000)
            student_group = Group.objects.create(name="Student Group for class2go course " + course + " %d" % r)
            instructor_group = Group.objects.create(name="Instructor Group for class2go course " + course + " %d" % r)
            tas_group = Group.objects.create(name="TAS Group for class2go course " + course + " %d" % r)
            readonly_tas_group = Group.objects.create(name="Readonly TAS Group for class2go course " + course + " %d" % r)

            c = Course(handle=course+'--'+suffix,
                       student_group_id = student_group.id,
                       instructor_group_id = instructor_group.id,
                       tas_group_id = tas_group.id,
                       readonly_tas_group_id = readonly_tas_group.id,
            )

            c.save()
    
    def test_noop(self):
        for host in ('class.stanford.edu', 'www.class.stanford.edu', 'staging.class.stanford.edu', 'www.staging.class.stanford.edu' \
                     'class2go.stanford.edu', 'www.class2go.stanford.edu', 'staging.class2go.stanford.edu', 'www.staging.class2go.stanford.edu'):
            request = self.factory.get('/')
            request.META['HTTP_HOST']=host
            response = self.redir.process_request(request)
            self.assertIsNone(response)

    def test_no_redirect_loop1(self):
        for path in self.course_path_endings:
            for host in ('class.stanford.edu', 'www.class.stanford.edu', 'staging.class.stanford.edu', 'www.staging.class.stanford.edu'):
                request = self.factory.get('/networking/Fall2012%s' % path)
                request.META['HTTP_HOST']=host
                response = self.redir.process_request(request)
                self.assertIsNone(response)

    def test_no_direct_loop2(self):
        for path in self.course_path_endings:
            for host in ('class2go.stanford.edu', 'www.class2go.stanford.edu', 'staging.class2go.stanford.edu', 'www.staging.class2go.stanford.edu'):
                request = self.factory.get('/db/Winter2013%s' % path)
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
        #HTTP to '/', should redirect class2go to class
        request = self.factory.get('/')
        request.META['HTTP_HOST']='networking.class2go.stanford.edu'
        response = self.redir.process_request(request)
        self.assertTrue(isinstance(response,HttpResponseRedirect))
        self.assertEqual(response['Location'],'http://class.stanford.edu/networking/Fall2012/')
        #HTTPS should redirect class2go to class
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
        #HTTP to '/', redirect class2go to class
        request = self.factory.get('/')
        request.META['HTTP_HOST']='networking.staging.class2go.stanford.edu'
        response = self.redir.process_request(request)
        self.assertTrue(isinstance(response,HttpResponseRedirect))
        self.assertEqual(response['Location'],'http://staging.class.stanford.edu/networking/Fall2012/')
        #HTTPS redirect class2go to class
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
        for path in self.course_path_endings:
            for course in ('nlp','test','networking','crypto','security','cs144','cs224n','solar','matsci256','psych30','nano','msande111'):
                request = self.factory.get(path)
                request.META['HTTP_HOST']=course+'.class.stanford.edu'
                response = self.redir.process_request(request)
                self.assertTrue(isinstance(response,HttpResponseRedirect))
                self.assertEqual(response['Location'],"http://class.stanford.edu/%s/Fall2012%s" % (course, path))

    def test_Fall2012_classes_redir_to_class(self):
        #make request to class2go for fall2012 classes, should end up with class
        for path in self.course_path_endings:
            for course in ('nlp','test','networking','crypto','security','cs144','cs224n','solar','matsci256','psych30','nano','msande111'):
                request = self.factory.get(path)
                request.META['HTTP_HOST']=course+'.class2go.stanford.edu'
                response = self.redir.process_request(request)
                self.assertTrue(isinstance(response,HttpResponseRedirect))
                self.assertEqual(response['Location'],"http://class.stanford.edu/%s/Fall2012%s" % (course, path))

    def test_cur_term_map_classes(self):
        for path in self.course_path_endings:
            #db--Winter2013
            request = self.factory.get(path)
            request.META['HTTP_HOST']='db.class2go.stanford.edu'
            response = self.redir.process_request(request)
            self.assertTrue(isinstance(response,HttpResponseRedirect))
            self.assertEqual(response['Location'],"http://class2go.stanford.edu/db/Winter2013%s" %path)
            #EE364A--Winter2013
            request = self.factory.get(path)
            request.META['HTTP_HOST']='EE364A.class2go.stanford.edu'
            response = self.redir.process_request(request)
            self.assertTrue(isinstance(response,HttpResponseRedirect))
            self.assertEqual(response['Location'],"http://class2go.stanford.edu/EE364A/Winter2013%s" %path)
            #class2go--tutorial
            request = self.factory.get(path)
            request.META['HTTP_HOST']='class2go.class2go.stanford.edu'
            response = self.redir.process_request(request)
            self.assertTrue(isinstance(response,HttpResponseRedirect))
            self.assertEqual(response['Location'],"http://class2go.stanford.edu/class2go/tutorial%s" %path)
            #db--Winter2013, redirect class to class2go
            request = self.factory.get(path)
            request.META['HTTP_HOST']='db.class.stanford.edu'
            response = self.redir.process_request(request)
            self.assertTrue(isinstance(response,HttpResponseRedirect))
            self.assertEqual(response['Location'],"http://class2go.stanford.edu/db/Winter2013%s" %path)
            #EE364A--Winter2013
            request = self.factory.get(path)
            request.META['HTTP_HOST']='EE364A.class.stanford.edu'
            response = self.redir.process_request(request)
            self.assertTrue(isinstance(response,HttpResponseRedirect))
            self.assertEqual(response['Location'],"http://class2go.stanford.edu/EE364A/Winter2013%s" %path)
            #class2go--tutorial, redirect class to class2go
            request = self.factory.get(path)
            request.META['HTTP_HOST']='class2go.class.stanford.edu'
            response = self.redir.process_request(request)
            self.assertTrue(isinstance(response,HttpResponseRedirect))
            self.assertEqual(response['Location'],"http://class2go.stanford.edu/class2go/tutorial%s" %path)

    def test_redir_class_path(self):
        for ending in self.course_path_endings:
            #test that we can redirect to the old codebase based on path
            for course in ('nlp','test','networking','crypto','security','cs144','cs224n','solar','matsci256','psych30','nano','msande111'):
                #GETs
                request = self.factory.get('/%s/Fall2012%s' % (course, ending))
                request.META['HTTP_HOST']='class2go.stanford.edu'
                response = self.redir.process_request(request)
                self.assertTrue(isinstance(response,HttpResponseRedirect))
                self.assertEqual(response['Location'],"http://class.stanford.edu/%s/Fall2012%s" % (course, ending))
                request = self.factory.get('/%s/Fall2012%s' % (course, ending))
                request.META['HTTP_HOST']='class.stanford.edu'
                response = self.redir.process_request(request)
                self.assertIsNone(response)
                #POSTS
                request = self.factory.post('/%s/Fall2012%s' % (course, ending))
                request.META['HTTP_HOST']='class2go.stanford.edu'
                response = self.redir.process_request(request)
                self.assertTrue(isinstance(response,HttpResponseRedirect))
                self.assertEqual(response['Location'],"http://class.stanford.edu/%s/Fall2012%s" % (course, ending))
                request = self.factory.post('/%s/Fall2012%s' % (course, ending))
                request.META['HTTP_HOST']='class.stanford.edu'
                response = self.redir.process_request(request)
                self.assertIsNone(response)

            #test that we can redirect to the new codebase based on path
            for course in ('EE364A','db'):
                #GET
                request = self.factory.get('/%s/Winter2013%s' % (course, ending))
                request.META['HTTP_HOST']='class2go.stanford.edu'
                response = self.redir.process_request(request)
                self.assertIsNone(response)
                request = self.factory.get('/%s/Winter2013%s' % (course, ending))
                request.META['HTTP_HOST']='class.stanford.edu'
                response = self.redir.process_request(request)
                self.assertTrue(isinstance(response,HttpResponseRedirect))
                self.assertEqual(response['Location'],"http://class2go.stanford.edu/%s/Winter2013%s" % (course, ending))
                #POST
                request = self.factory.post('/%s/Winter2013%s' % (course, ending))
                request.META['HTTP_HOST']='class2go.stanford.edu'
                response = self.redir.process_request(request)
                self.assertIsNone(response)
                request = self.factory.post('/%s/Winter2013%s' % (course, ending))
                request.META['HTTP_HOST']='class.stanford.edu'
                response = self.redir.process_request(request)
                self.assertTrue(isinstance(response,HttpResponseRedirect))
                self.assertEqual(response['Location'],"http://class2go.stanford.edu/%s/Winter2013%s" % (course, ending))

                                 
    def test_no_redirect(self):
        for path in self.no_course_paths:
            for host in ('class.stanford.edu', 'www.class.stanford.edu', 'staging.class.stanford.edu', 'www.staging.class.stanford.edu' \
                         'class2go.stanford.edu', 'www.class2go.stanford.edu', 'staging.class2go.stanford.edu', 'www.staging.class2go.stanford.edu'):
                request = self.factory.get(path)
                request.META['HTTP_HOST']=host
                response = self.redir.process_request(request)
                self.assertIsNone(response)


