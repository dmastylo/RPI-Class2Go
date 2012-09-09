from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = "Run this command on initial setup of an instance to set the site record correctly."

    def handle(self, *args, **options):

        try:
            site = Site.objects.get(id=1)
            site.domain = 'class.stanford.edu'
            site.name = 'Stanford Online'
            site.save()
            print "Site updated successfully."
        except:
            print "Error; the site record was not found with id = 1"


