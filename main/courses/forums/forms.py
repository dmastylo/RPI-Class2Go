from django import forms

class PiazzaAuthForm(forms.Form):
    # User Info
    user_id = forms.CharField()
    lis_person_contact_email_primary = forms.CharField()
    lis_person_name_given = forms.CharField()
    lis_person_name_family = forms.CharField()
    lis_person_name_full = forms.CharField()
    roles = forms.CharField()

    # Class Info
    context_id = forms.CharField()
    context_label = forms.CharField()
    context_title = forms.CharField()

    # LTI
    lti_message_type = forms.CharField()
    lti_version = forms.CharField()

    # OAuth Signature
    oauth_callback = forms.CharField()
    oauth_version = forms.CharField()
    oauth_nonce = forms.CharField()
    oauth_timestamp = forms.CharField()
    oauth_consumer_key = forms.CharField()
    oauth_signature_method = forms.CharField()
    oauth_signature = forms.CharField()

