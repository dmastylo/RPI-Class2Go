from django import forms
from c2g.models import ContentSection, Video, Exercise
# import the logging library
#import logging
#logger = logging.getLogger('django')

class S3UploadForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        #logger.warning('test')
        course = kwargs.pop('course')
        super(S3UploadForm, self).__init__(*args, **kwargs)
        self.fields['section'] = forms.ModelChoiceField(ContentSection.objects.filter(course=course), empty_label=None)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            del self.fields['file']
            del self.fields['url']

    class Meta:
        model = Video
        fields = ('title', 'slug', 'section', 'description', 'file', 'url', 'live_datetime')
        widgets = {
            'live_datetime': forms.widgets.DateTimeInput(format='%m/%d/%Y %H:%M', attrs={'data-datetimepicker':''})
        }

class ManageExercisesForm(forms.Form):
    file = forms.FileField()
    video_time = forms.IntegerField(min_value=0)
    course = forms.CharField(widget=(forms.HiddenInput()))

    #Check to make sure added exercise file names are unique to the course
    def clean(self):
        cleaned_data = super(ManageExercisesForm, self).clean()
        file = cleaned_data.get('file')
        course = cleaned_data.get('course')
        if file and course:
            exercises = Exercise.objects.filter(video__course=course, fileName=file)
            if len(exercises) > 0:
                self._errors['file'] = self.error_class(['An exercise by this name has already been uploaded'])
        return cleaned_data
