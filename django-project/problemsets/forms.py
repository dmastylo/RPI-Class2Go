from django import forms
from django.forms import Textarea
from c2g.models import ProblemSet, ContentSection

class CreateProblemSet(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course')
        super(CreateProblemSet, self).__init__(*args, **kwargs)
        self.fields['section'] = forms.ModelChoiceField(ContentSection.objects.filter(course=course), empty_label=None)
        self.fields['live_datetime'].widget.attrs.update({'data-datetimepicker':''})
        self.fields['due_date'].widget.attrs.update({'data-datetimepicker':''})
        self.fields['grace_period'].widget.attrs.update({'data-datetimepicker':''})
        self.fields['partial_credit_deadline'].widget.attrs.update({'data-datetimepicker':''})

    assessment_type = forms.TypedChoiceField(choices=(('formative', 'Formative'), ('assessive', 'Assessive')), widget=forms.RadioSelect)

    class Meta:
        model = ProblemSet
        fields = ('title', 'slug', 'section', 'description', 'live_datetime', 'due_date', 'grace_period', 'partial_credit_deadline',
                'late_penalty', 'assessment_type', 'submissions_permitted', 'resubmission_penalty')
        widgets = {
                'description': Textarea(attrs={'cols': 20, 'rows': 10})
        }
