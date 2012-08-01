from django import forms

class VideoUploadForm(forms.Form):
    title = forms.CharField(required=False)
    file = forms.FileField()
