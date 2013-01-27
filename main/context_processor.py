from django.conf import settings # import the settings file

def context_settings(context):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'SITE_NAME_SHORT': settings.SITE_NAME_SHORT, 'SITE_NAME_LONG': settings.SITE_NAME_LONG, 'SITE_TITLE': settings.SITE_TITLE}