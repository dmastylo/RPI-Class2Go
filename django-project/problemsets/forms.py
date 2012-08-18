from django import forms
from c2g.models import ProblemSet

class CreateProblemSet(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course')
        super(CreateProblemSet, self).__init__(*args, **kwargs)
#        self.fields['section'] = forms.ModelChoiceField(ContentSection.objects.filter(course=course), empty_label=None)

    class Meta:
        model = ProblemSet
        fields = ('title', 'slug', 'section', 'description')
