from django import forms

class LiveDateForm(forms.Form):
    live_datetime = forms.DateTimeField(required=False, widget=forms.widgets.DateTimeInput(format='%m/%d/%Y %H:%M', attrs={'data-datetimepicker':''}))
