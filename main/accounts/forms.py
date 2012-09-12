from django.contrib.auth.models import User
from c2g.models import UserProfile
from django import forms
from django.utils.translation import ugettext_lazy as _

import datetime

class EditUserForm(forms.ModelForm):
    email = forms.EmailField(label=_("E-mail"), max_length=75)
    first_name = forms.RegexField(regex=r'^[\w -]+$',
                                  max_length=30,
                                  label=_("First Name"),
                                  error_messages={'invalid': _("This value may contain only letters and dashes")})
    last_name = forms.RegexField(regex=r'^[\w -]+$',
                                  max_length=30,
                                  label=_("Last Name"),
                                  error_messages={'invalid': _("This value may contain only letters and dashes")})

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class EditProfileForm(forms.ModelForm):
    max_age=110
    min_age=10
    first_year=datetime.date.today().year-max_age
    last_year=datetime.date.today().year-min_age
    YEARS=map(lambda y: (str(y),str(y)), range(last_year, first_year, -1))
    YEARS.insert(0,('decline',''))
    birth_year = forms.ChoiceField(choices=YEARS,label=_("Year of birth"))
    gender = forms.ChoiceField(label=_("Gender"), choices=(('decline',''),
                                                           ("Female","Female"),
                                                           ("Male","Male"),
                                                           ("Non-Traditional","Non-Traditional")))
    education = forms.ChoiceField(label=_("Highest degree received"), choices=(('decline',''),
                                                                               ('Doctorate','Doctorate'),
                                                                               ('MastersOrProfessional','Masters or Professional'),
                                                                               ('Bachelors','Bachelors'),
                                                                               ('Associate','Associate'),
                                                                               ('HighSchool','Secondary/High School'),
                                                                               ('Middle','Middle school/Jr. High'),
                                                                               ('Elementary','Elementary'),
                                                                               ('None','None'),
                                                                               ('Other','Other'),))
    work = forms.ChoiceField(label=_("I am currently"), choices=(  ('decline',''),
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

    class Meta:
        model = UserProfile
        fields = ('birth_year', 'gender', 'education', 'work')
