from django import forms
from c2g.models import ContentSection, File

class FileUploadForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course')
        super(FileUploadForm, self).__init__(*args, **kwargs)
        self.fields['section'] = forms.ModelChoiceField(ContentSection.objects.filter(course=course, is_deleted=False), empty_label=None)

    class Meta:
        model = File
        fields = ('title', 'section', 'file', 'live_datetime')
        widgets = {
            'live_datetime': forms.widgets.DateTimeInput(format='%m/%d/%Y %H:%M', attrs={'data-datetimepicker':''}),
        }

class FileEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course')
        super(FileEditForm, self).__init__(*args, **kwargs)
        self.fields['section'] = forms.ModelChoiceField(ContentSection.objects.filter(course=course, is_deleted=False), empty_label=None)
    
    class Meta:
        model = File
        fields = ('title', 'section', 'live_datetime')
        widgets = {
            'live_datetime': forms.widgets.DateTimeInput(format='%m/%d/%Y %H:%M', attrs={'data-datetimepicker':''}),
    }
