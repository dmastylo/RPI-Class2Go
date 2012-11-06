import sys

from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = "Run this command on initial setup of an instance to set the site record correctly."

    def handle(self, *args, **options):

        domainname = 'class.stanford.edu'
        if len(args) == 1:
            domainname = args[0]
        elif len(args) > 1:
            print "Error; I don't know what to do with so many arguments"
            sys.exit(1)

        try:
            site = Site.objects.get(id=1)
            #site.domain = 'class.stanford.edu'
            site.domain = domainname
            site.name = 'Stanford Online'
            site.save()
            print "Site updated successfully."
        except:
            print "Error; the site record was not found with id = 1"
            sys.exit(1)

        sys.exit(0)

