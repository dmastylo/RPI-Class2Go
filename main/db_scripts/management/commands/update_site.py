import sys

from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = """Run this command instance setup to set the site record correctly.

The site record is used to create self-reference URLs. For example,
./manage.py update_site localhost:8888 'Test Instance' 
will make all local URLs reference http://localhost:8888 and the words 
'Test Instance' should appear in the browser titlebar.

The arguments default to 'class.stanford.edu' and 'Stanford Online', respectively.
    """

    def handle(self, *args, **options):

        domainname = 'class.stanford.edu'
        sitename = 'Stanford Online'
        if len(args) == 1:
            domainname = args[0]
        elif len(args) == 2:
            domainname = args[0]
            sitename = args[1]
        elif len(args) > 2:
            print "Error; I don't know what to do with so many arguments"
            sys.exit(1)

        try:
            site = Site.objects.get(id=1)
            site.domain = domainname
            site.name = sitename
            site.save()
            print "Site updated successfully: %s - %s" % (site.name, site.domain)
        except:
            print "Error; the site record was not found with id = 1"
            sys.exit(1)

        sys.exit(0)

