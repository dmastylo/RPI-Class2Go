from django import forms


class SectionPushForm(forms.Form):
    
    def __init__(self, class_list, *args, **kwargs):
        super(SectionPushForm, self).__init__(*args, **kwargs)
        self.fields['linked_class'] = forms.ChoiceField(label="Copy to course:", choices=map(lambda c:(c.handle,c.title), class_list))