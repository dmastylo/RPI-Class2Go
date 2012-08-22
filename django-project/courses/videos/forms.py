from django import forms
from c2g.models import ContentSection, Video
# import the logging library
#import logging
#logger = logging.getLogger('django')

class S3UploadForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        #logger.warning('test')
        course = kwargs.pop('course')
        super(S3UploadForm, self).__init__(*args, **kwargs)
        self.fields['section'] = forms.ModelChoiceField(ContentSection.objects.filter(course=course), empty_label=None)
        self.fields['live_datetime'].required = False

    class Meta:
        model = Video
        fields = ('title', 'slug', 'section', 'description', 'file', 'live_datetime')
        widgets = {
            'live_datetime': forms.widgets.DateTimeInput(format='%m/%d/%Y %H:%M', attrs={'data-datetimepicker':''})
        }
