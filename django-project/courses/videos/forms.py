from django import forms
from c2g.models import ContentSection, Video

class VideoUploadForm(forms.Form):
    title = forms.CharField()
    description = forms.CharField(widget=forms.Textarea, required=False)
    url_name = forms.SlugField()
    kelvinator_threshold = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course')
        super(VideoUploadForm, self).__init__(*args, **kwargs)
        self.fields['section'] = forms.ModelChoiceField(ContentSection.objects.filter(course=course), empty_label=None)

class S3UploadForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course')
        super(S3UploadForm, self).__init__(*args, **kwargs)
        self.fields['section'] = forms.ModelChoiceField(ContentSection.objects.filter(course=course), empty_label=None)

    class Meta:
        model = Video
        fields = ('title', 'slug', 'section', 'description', 'file')
