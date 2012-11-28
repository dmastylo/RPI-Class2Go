from django import forms
from c2g.models import ContentSection, Video, Exercise, Course
# import the logging library
#import logging
#logger = logging.getLogger('django')

import gdata.youtube.service

class S3UploadForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        #logger.warning('test')
        course = kwargs.pop('course')
        super(S3UploadForm, self).__init__(*args, **kwargs)
        self.fields['section'] = forms.ModelChoiceField(ContentSection.objects.filter(course=course, is_deleted=False), empty_label=None)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            del self.fields['file']
        else:
            self.fields['file'].help_text = "Select the mp4 video file on your machine to upload - you need to do this even if the file is already on YouTube so that we can provide downloads and generate a thumbnail index."
        self.fields['slug'].help_text = "A unique identifier that will be shown in the URL"
    
    def clean_url(self):
        url = self.cleaned_data['url']
        if url:
            yt_service = gdata.youtube.service.YouTubeService()
            try:
                entry = yt_service.GetYouTubeVideoEntry(video_id=url)
                self.instance.duration = entry.media.duration.seconds
            except gdata.service.RequestError:
                raise forms.ValidationError('Invalid YouTube video ID.')
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

class AdditionalExercisesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        used_exercises = kwargs.pop('used_exercises', None)
        super(AdditionalExercisesForm, self).__init__(*args, **kwargs)
        self.fields['exercise'] = forms.ModelMultipleChoiceField(used_exercises)
#        for used_exercise in used_exercises:
#            check = 'check' + str(used_exercise.id)
#            video_time = 'time' + str(used_exercise.id)
#            self.fields[check] = forms.BooleanField(required=False)
#            self.fields[video_time] = forms.IntegerField(required=False)

    def clean(self):
        cleaned_data = super(AdditionalExercisesForm, self).clean()
        check = cleaned_data.get('check')
        poo = cleaned_data.get('poo')
        if check and not poo:
            self._errors['poo'] = self.error_class(['Dont be so poopy'])
        return cleaned_data

class ReorderExercisesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        current_exercises = kwargs.pop('current_exercises', None)
        super(ReorderExercisesForm, self).__init__(*args, **kwargs)
        for current_exercise in current_exercises:
            self.fields[current_exercise.exercise.fileName] = forms.IntegerField(initial=current_exercise.video_time)
