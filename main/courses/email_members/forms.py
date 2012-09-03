from django import forms

class EmailForm(forms.Form):
    to = forms.ChoiceField(label="Send to",
                           choices = (('staff', 'All Course Staff'),
                                      ('students', 'All Students'),
                                      ('all', 'All Course Members'),),
                           )
    subject =  forms.CharField(max_length=100, label="Subject", widget=forms.TextInput(attrs={'class':'span12'}))

    message = forms.CharField(label="Message", widget=forms.Textarea(attrs={'class':'span12', 'rows':20}))
    


    