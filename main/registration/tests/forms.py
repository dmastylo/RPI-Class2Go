from django.contrib.auth.models import User
from django.test import TestCase

from registration import forms


class RegistrationFormTests(TestCase):
    """
    Test the default registration forms.

    """
    def setUp(self):
        self.__good_data = {'username':   'FooBar',
                            'email':      'foo@example.com',
                            'first_name': 'Foobury',
                            'last_name':  'Barr',
                            'password1':  'foobarbaz0',
                            'password2':  'foobarbaz0',
                            'tos':        'checked',}

    def test_registration_form(self):
        """Test ``RegistrationForm`` enforces username constraints and matching passwords."""
        # Create a user so we can verify that duplicate usernames aren't permitted.
        User.objects.create_user('alice', 'alice@example.com', 'secret')

        invalid_data_dicts = [
            # Non-alphanumeric username.
            {'data': {'username':   'foo/bar',
                      'email':      'foo@example.com',
                      'first_name': 'boo',
                      'last_name':  'bar',
                      'password1':  'foo',
                      'password2':  'foo'},
            'error': ('username', [u"This value may contain only letters, numbers and @/./+/-/_ characters. No spaces."])},
            # Non-alphabetic first name.
            {'data': {'username':   'foo/bar',
                      'email':      'foo@example.com',
                      'first_name': 'bo*o',
                      'last_name':  'bar',
                      'password1':  'foo',
                      'password2':  'foo'},
              'error': ('first_name', [u"This value may contain only letters, spaces and dashes."])},
             # Non-alphabetic last name.
            {'data': {'username':   'foo/bar',
                      'email':      'foo@example.com',
                      'first_name': 'boo',
                      'last_name':  'ba}r',
                      'password1':  'foo',
                      'password2':  'foo'},
              'error': ('last_name', [u"This value may contain only letters, spaces and dashes."])},
            # Already-existing username.
            {'data': {'username':   'alice',
                      'email':      'alice@example.com',
                      'first_name': 'alice',
                      'last_name':  'wonderland',
                      'password1':  'secret',
                      'password2':  'secret'},
            'error': ('username', [u"A user with that username already exists."])},
            # Mismatched passwords.
            {'data': {'username':   'foo',
                      'email':      'foo@example.com',
                      'first_name': 'alice',
                      'last_name':  'wonderland',
                      'password1':  'foo',
                      'password2':  'bar'},
            'error': ('password2', [u"The two password fields didn't match."])},
            ]

        for invalid_dict in invalid_data_dicts:
            form = forms.RegistrationForm(data=invalid_dict['data'])
            self.failIf(form.is_valid())
            self.assertEqual(form.errors[invalid_dict['error'][0]],
                             invalid_dict['error'][1])

    def test_correct_form_is_correct(self):
        """Test that a correct form with all required fields is valid"""
        form = forms.RegistrationForm(data = self.__good_data) 
        self.failUnless(form.is_valid())
            
    def test_registration_form_first_last(self):
        """Test that First and Last name fields are required"""
        no_firstname = self.__good_data
        no_lastname = self.__good_data
        del no_firstname['first_name']
        del no_firstname['last_name']
        form = forms.RegistrationForm(data=no_lastname)
        self.failIf(form.is_valid())
        self.assertEqual(form.errors['last_name'],
                         [u"This field is required."])
        form = forms.RegistrationForm(data=no_firstname)
        self.failIf(form.is_valid())
        self.assertEqual(form.errors['first_name'],
                         [u"This field is required."])

    def test_registration_form_tos(self):
        """Test that ``RegistrationFormTermsOfService`` requires agreement."""
        no_tos = self.__good_data
        del no_tos['tos']
        form = forms.RegistrationFormTermsOfService(data=no_tos)
        self.failIf(form.is_valid())
        self.assertEqual(form.errors['tos'], [u"You must agree to the terms to register."])

    def test_registration_form_unique_email(self):
        """Test that ``RegistrationFormUniqueEmail`` validates email uniqueness."""
        # Create a user so we can verify that duplicate addresses
        # aren't permitted.
        User.objects.create_user('alice', 'alice@example.com', 'secret')

        form = forms.RegistrationFormUniqueEmail(data={'username': 'AliceWhoForgot',
                                                       'email': 'alice@example.com',
                                                       'first_name': 'malice',
                                                       'last_name': 'palace',
                                                       'password1': 'foo',
                                                       'password2': 'foo'})
        self.failIf(form.is_valid())
        self.assertEqual(form.errors['email'],
                         [u"This email address is already in use. Please supply a different email address."])

    def test_registration_form_no_free_email(self):
        """
        Test that ``RegistrationFormNoFreeEmail`` disallows
        registration with free email addresses.

        """
        base_data = self.__good_data
        del base_data['email']
        for domain in forms.RegistrationFormNoFreeEmail.bad_domains:
            base_data['email'] = u"foo@%s" % domain
            form = forms.RegistrationFormNoFreeEmail(data=base_data)
            self.failIf(form.is_valid())
            self.assertEqual(form.errors['email'],
                             [u"Registration using free email addresses is prohibited. Please supply a different email address."])
            del base_data['email']

        base_data['email'] = 'foo@example.com'
        form = forms.RegistrationFormNoFreeEmail(data=base_data)
        self.failUnless(form.is_valid())
