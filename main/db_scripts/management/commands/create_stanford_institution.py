from django.core.management.base import BaseCommand, CommandError
from c2g.models import Institution

#from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = "Run this command on initial setup of an instance to create the Stanford institution."

    def handle(self, *args, **options):
        institution = Institution(
                                  title = "Stanford",
                                  country = "USA",
                                  city = "Palo Alto",
                                  domains = "stanford.edu")
                                  
        institution.save()
        print "Institution created successfully"
            