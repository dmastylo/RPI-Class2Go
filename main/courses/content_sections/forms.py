from django import forms


class CoursePushForm(forms.Form):
    
    def __init__(self, class_list, *args, **kwargs):
        super(CoursePushForm, self).__init__(*args, **kwargs)
        self.fields['linked_class'] = forms.ChoiceField(label="Copy to course:", choices=map(lambda c:(c.handle,c.title), class_list))
        
class SectionPushForm(forms.Form):
    
    def __init__(self, section_list, class_list, *args, **kwargs):
        super(SectionPushForm, self).__init__(*args, **kwargs)
        self.fields['section_choice'] = forms.ChoiceField(label="Choose a Section:", choices=map(lambda s: (str(s.id),s.title),section_list))
        self.fields['linked_class'] = forms.ChoiceField(label="Copy to course:", choices=map(lambda c:(c.handle,c.title), class_list))