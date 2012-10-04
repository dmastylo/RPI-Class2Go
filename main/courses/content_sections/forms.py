from django import forms


class SectionPushForm(forms.Form):
    
    def __init__(self, section_list, class_list, *args, **kwargs):
        super(SectionPushForm, self).__init__(*args, **kwargs)
        self.fields['section_choice'] = forms.ChoiceField(label="Choose a Section:", choices=map(lambda s: (str(s.id),s.title),section_list))
        self.fields['linked_class'] = forms.ChoiceField(label="Copy to class:", choices=map(lambda c:(c.handle,c.title), class_list))