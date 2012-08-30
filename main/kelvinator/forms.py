from django import forms

class ExtractForm(forms.Form):
    bucket = forms.CharField(max_length=30,initial="stage-c2g")
    path = forms.CharField(widget=forms.TextInput(attrs={'size':60}),
            max_length=200,
            initial="/nlp/Fall2012/videos/15/nlp-sef.mp4")
    frames = forms.FloatField(initial=1)
    threshold = forms.FloatField(initial=1000)
