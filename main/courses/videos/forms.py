from django import forms
from c2g.models import ContentSection, Video, Exercise
# import the logging library
#import logging
#logger = logging.getLogger('django')

import gdata.youtube.service

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

    def clean_url(self):
        url = self.cleaned_data['url']
        if url:
            yt_service = gdata.youtube.service.YouTubeService()
            try:
                entry = yt_service.GetYouTubeVideoEntry(video_id=url)
                self.instance.duration = entry.media.duration.seconds
            except gdata.service.RequestError:
                raise forms.ValidationError('Invalid Youtube video ID.')
        return url

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

    def __init__(self, *args, **kwargs):
        used_exercises = kwargs.pop('used_exercises', None)
        super(ManageExercisesForm, self).__init__(*args, **kwargs)
        for used_exercise in used_exercises:
            check = 'check' + str(used_exercise.id)
            video_time = 'time' + str(used_exercise.id)
            self.fields[check] = forms.BooleanField(required=False)
            self.fields[video_time] = forms.IntegerField(required=False)

    #Check to make sure added exercise file names are unique to the course
    def clean(self):
        cleaned_data = super(ManageExercisesForm, self).clean()
        file = cleaned_data.get('file')
        course = cleaned_data.get('course')
        if file and course:
            exercises = Exercise.objects.filter(video__course=course, fileName=file)
            if len(exercises) > 0:
                self._errors['file'] = self.error_class(['An exercise by this name has already been uploaded'])

        check = cleaned_data.get('check')
        poo = cleaned_data.get('poo')
        if check and not poo:
            self._errors['poo'] = self.error_class(['Dont be so poopy'])
        return cleaned_data
