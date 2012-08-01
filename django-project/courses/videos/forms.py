from django import forms

class VideoUploadForm(forms.Form):
    title = forms.CharField()
    description = forms.CharField(widget=forms.Textarea, required=False)
    url_name = forms.SlugField()
    tags = forms.CharField(required=False)
    kelvinator_threshold = forms.IntegerField(required=False)
    section_choices = [('NLP Introduction and Regular Expressions', 'NLP Introduction and Regular Expressions'), ('Tokenizations and Minimum Edit Distance', 'Tokenizations and Minimum Edit Distance'), ('N-grams', 'N-grams')]
    section = forms.ChoiceField(choices=section_choices)

#    def __init__(self, *args, **kwargs):
#        sections = kwargs.pop('sections')
#        super(VideoUploadForm, self).__init__(*args, **kwargs)
#        section_choices = []
#        for section in sections:
#            section_choices.append((section.title, section.title))
#        self.fields['section'] = forms.ChoiceField(choices=section_choices)
