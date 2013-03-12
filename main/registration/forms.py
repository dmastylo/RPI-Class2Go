"""Forms and validation code for user registration."""

import datetime
import logging
logger = logging.getLogger('form')
 
from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

# I put this on all required fields, because it's easier to pick up
# on them with CSS or JavaScript if they have a class of "required"
# in the HTML. Your mileage may vary. If/when Django ticket #3515
# lands in trunk, this will no longer be necessary.
attrs_dict = {'class': 'required'}


class RegistrationForm(forms.Form):
    """
    Form for registering a new user account.
    
    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.
    
    Subclasses should feel free to add any additional validation they
    need, but should avoid defining a ``save()`` method -- the actual
    saving of collected user data is delegated to the active
    registration backend.
    
    """
    username = forms.RegexField(regex=r'^[\w.@+-]+$',
                                max_length=30,
                                widget=forms.TextInput(attrs=dict(attrs_dict,placeholder='')),
                                label=_("Choose a Username*"),
                                error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters. No spaces.")})
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_("E-mail*"))
    first_name = forms.RegexField(regex=r'^[\w -]+$',
                                  max_length=30,
                                  widget=forms.TextInput(attrs=attrs_dict),
                                  label=_("First Name*"),
                                  error_messages={'invalid': _("This value may contain only letters, spaces and dashes.")})
    last_name = forms.RegexField(regex=r'^[\w -]+$',
                                  max_length=30,
                                  widget=forms.TextInput(attrs=attrs_dict),
                                  label=_("Last Name*"),
                                  error_messages={'invalid': _("This value may contain only letters, spaces and dashes.")})
    max_age=110
    min_age=10
    first_year=datetime.date.today().year-max_age
    last_year=datetime.date.today().year-min_age
    YEARS=map(lambda y: (str(y),str(y)), range(last_year, first_year, -1))
    YEARS.insert(0,('decline',''))
    birth_year = forms.ChoiceField(label=_("Year of birth"),
                                   required=False,
                                   choices=YEARS)
    gender = forms.ChoiceField(label=_("Gender"), 
                               required=False,
                               choices=(('decline',''),
                                        ("Female","Female"),
                                        ("Male","Male"),
                                        ("Non-Traditional","Non-Traditional")))
    education = forms.ChoiceField(label=_("Highest degree received"), 
                                  required=False,
                                  choices=(('decline',''),
                                           ('Doctorate','Doctorate'),
                                           ('MastersOrProfessional','Masters or Professional'),
                                           ('Bachelors','Bachelors'),
                                           ('Associate','Associate'),
                                           ('HighSchool','Secondary/High School'),
                                           ('Middle','Middle school/Jr. High'),
                                           ('Elementary','Elementary'),
                                           ('None','None'),
                                           ('Other','Other'),))
    work = forms.ChoiceField(label=_("I am currently"), 
                             required=False,
                             choices=(('decline',''),
                                      ('undergrad','An undergraduate'),
                                      ('gradStudent','A graduate student'),
                                      ('HSStudent','A high school (or younger) student'),
                                      ('Unemployed','Unemployed'),
                                      ('Retired','Retired'),
                                      ('----','-------------------'),
                                      ('Software','In the software industry'),
                                      ('Hardware','In the hardware industry'),
                                      ('Legal','In the legal industry'),
                                      ('K12','In K-12 education'),
                                      ('PostSecondary','In post-secondary education'),
                                      ('ArtsDesignArchEntertainment','In the arts, design, architecture or entertainment industries'),
                                      ('LifePhysSci','In the life or physical sciences'),
                                      ('Healthcare','In the healthcare industry'),
                                      ('SocialServices','In social services'),
                                      ('RetailServicesTransportationFood','In the retail service, transportation or food industries'),
                                      ('ManufacturingConstruction','In manufacturing or construction'),
                                      ('AnotherIndustry','In another industry'),
                                      ('Other','Other'),))

    password1 = forms.RegexField(regex=r'(?=.*\d)',
                                 min_length=6,
                                 widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                 label=_("Password*"),
                                 error_messages={'invalid': _("Your password must contain at least one number (0-9)."), 'min_length': _("Your password must be at least 6 characters")})
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_("Password (again)*"))
    
    tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                                 label=_(u'I have read and agree to the Honor Code and Terms of Service'),
                                 error_messages={'required': _("You must agree in order to register.")})

    course_prefix = forms.CharField(widget=forms.HiddenInput(),required=False)
    course_suffix = forms.CharField(widget=forms.HiddenInput(),required=False)
    invite = forms.CharField(widget=forms.HiddenInput(),required=False)
    
    def clean_username(self):
        """Verify username is alphanumeric and not already in use."""
        existing = User.objects.filter(username__iexact=self.cleaned_data['username'])
        if existing.exists():
            raise forms.ValidationError(_("A user with that username already exists."))
        else:
            return self.cleaned_data['username']

    def clean_password2(self):
        """Verify both password fields match."""
        password1 = self.cleaned_data.get('password1', '')
        password2 = self.cleaned_data.get('password2', '')
        if not password2:
            raise forms.ValidationError(_("You must confirm your password."))
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

#    def clean(self):
#        """
#        Verifiy that the values entered into the two password fields
#        match. Note that an error here will end up in
#        ``non_field_errors()`` because it doesn't apply to a single
#        field.
#        
#        """
#        #logger.info(self.cleaned_data['first_name'])
#        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
#            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
#                raise forms.ValidationError(_("The two password fields didn't match."))
#        return self.cleaned_data


class RegistrationFormTermsOfService(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which adds a required checkbox
    for agreeing to a site's Terms of Service.
    
    """
    tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                             label=_(u'I have read and agree to the Terms of Service'),
                             error_messages={'required': _("You must agree to the terms to register.")})


class RegistrationFormUniqueEmail(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which enforces uniqueness of
    email addresses.
    
    """
    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.
        
        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
        return self.cleaned_data['email']


class RegistrationFormNoFreeEmail(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which disallows registration with
    email addresses from popular free webmail services; moderately
    useful for preventing automated spam registrations.
    
    To change the list of banned domains, subclass this form and
    override the attribute ``bad_domains``.
    
    """
    bad_domains = ['aim.com', 'aol.com', 'email.com', 'gmail.com',
                   'googlemail.com', 'hotmail.com', 'hushmail.com',
                   'msn.com', 'mail.ru', 'mailinator.com', 'live.com',
                   'yahoo.com']
    
    def clean_email(self):
        """
        Check the supplied email address against a list of known free
        webmail domains.
        
        """
        email_domain = self.cleaned_data['email'].split('@')[1]
        if email_domain in self.bad_domains:
            raise forms.ValidationError(_("Registration using free email addresses is prohibited. Please supply a different email address."))
        return self.cleaned_data['email']


class SetPasswordFormC2G(SetPasswordForm):
 #   """
 #       A form that lets a user change set his/her password without entering the
 #       old password
 #       """
    
    new_password1 = forms.RegexField(regex=r'(?=.*\d)',
                                  min_length=6,
                                 widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_("Password*"),
                                error_messages={'invalid': _("Your password must contain at least one number (0-9)."), 'min_length': _("Your password must be at least 6 characters")})
    
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)


class PasswordChangeFormC2G(SetPasswordFormC2G):
    """
        A form that lets a user change his/her password by entering
        their old password.
        """
    error_messages = dict(SetPasswordFormC2G.error_messages, **{
                          'password_incorrect': _("Your old password was entered incorrectly. "
                                                  "Please enter it again."),
                          })
    old_password = forms.CharField(label=_("Old password"),
                                   widget=forms.PasswordInput)
    
    def clean_old_password(self):
        """
            Validates that the old_password field is correct.
            """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                                        self.error_messages['password_incorrect'])
        return old_password
PasswordChangeFormC2G.base_fields.keyOrder = ['old_password', 'new_password1',
                                           'new_password2']


#######################################################################################
