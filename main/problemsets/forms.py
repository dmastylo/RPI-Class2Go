from django import forms
from django.forms import Textarea
from c2g.models import ProblemSet, ContentSection, Exercise, Course
class CreateProblemSet(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course')
        super(CreateProblemSet, self).__init__(*args, **kwargs)
        self.fields['section'] = forms.ModelChoiceField(ContentSection.objects.filter(course=course, is_deleted=False).order_by('index'), empty_label=None)
        self.fields['live_datetime'].required = False

    assessment_type = forms.TypedChoiceField(choices=(('formative', 'Formative'), ('assessive', 'Summative'), ('survey', 'Survey')), widget=forms.RadioSelect)
    submissions_permitted = forms.IntegerField(min_value=0)
    resubmission_penalty = forms.IntegerField(min_value=0, max_value=100)

    class Meta:
        model = ProblemSet
        fields = ('title', 'slug', 'section', 'description', 'live_datetime', 'due_date', 'grace_period', 'partial_credit_deadline',
                'late_penalty', 'assessment_type', 'submissions_permitted', 'resubmission_penalty')
        widgets = {
                'description': Textarea(attrs={'cols': 20, 'rows': 10}),
                'live_datetime': forms.widgets.DateTimeInput(format='%m/%d/%Y %H:%M', attrs={'data-datetimepicker':''}),
                'due_date': forms.widgets.DateTimeInput(format='%m/%d/%Y %H:%M', attrs={'data-datetimepicker':''}),
                'grace_period': forms.widgets.DateTimeInput(format='%m/%d/%Y %H:%M', attrs={'data-datetimepicker':''}),
                'partial_credit_deadline': forms.widgets.DateTimeInput(format='%m/%d/%Y %H:%M', attrs={'data-datetimepicker':''})
        }


class ManageExercisesForm(forms.Form):
    file = forms.FileField()
    course = forms.CharField(widget=(forms.HiddenInput()))
