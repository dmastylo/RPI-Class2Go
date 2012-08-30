from django import forms

class EmailForm(forms.Form):
    to = forms.ChoiceField(label="Send to",
                           choices = (('all', 'All Course Members'),
                                      ('students', 'All Students'),
                                      ('staff', 'All Course Staff'),),
                           )
    subject =  forms.CharField(max_length=100, label="Subject", widget=forms.TextInput(attrs={'class':'span12'}))

    message = forms.CharField(label="Message", widget=forms.Textarea(attrs={'class':'span12', 'rows':20}))
    


    