from django import forms

class EmailForm(forms.Form):
    to = forms.ChoiceField(label="Send to",
                           choices = (('myself', 'Myself.  (Retains email inputs below after sending)'),
                                      ('staff', 'All Course Staff'),
                                      ('students', 'All Students'),
                                      ('all', 'Students and Staff'),),
                           widget = forms.Select(attrs={'class':'span5'}),
                           )
    subject =  forms.CharField(max_length=100, label="Subject", widget=forms.TextInput(attrs={'class':'span12'}))

    message = forms.CharField(label="Message", widget=forms.Textarea(attrs={'class':'span12 tinymce', 'rows':20}))
    


    