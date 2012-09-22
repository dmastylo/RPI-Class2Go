from django.core.management.base import BaseCommand, CommandError
from c2g.models import MailingList, EmailAddr
from django.contrib.auth.models import User, Group
from django.db.utils import IntegrityError
import csv
from django.core.validators import validate_email, ValidationError
from _mysql_exceptions import Warning

class Command(BaseCommand):
    args = "csv_file_name list_name"
    help = """ 
        Takes the contents of csv file in csv_file_name and creates a new MailingList with EmailAddr entries
        from the csv file.  csv format should be:
        
        name1, email address1
        name2, email address2
        
        If MailingList with list_name already exists, the command exits.  If an email address in the csv already
        exists in an EmailAddr entry, a duplicate entry will be created.
        """
    
    def handle(self, *args, **options):
        if len(args) < 2 or (not args[0]) or (not args[1]):
            return "Not enough arguments!\n"
        filename=args[0]
        listname=args[1]
        if MailingList.objects.filter(name=listname).exists():
           return "A list named %s already exists!\n" % listname
        list = MailingList(name=listname)
        list.save()
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            num_imported = 0
            for row in reader:
                if len(row) >=2:
                    email = row[1].strip()
                    try: #add existing addr
                        validate_email(email)
                        try:
                            addr = EmailAddr(name=row[0].strip(),addr=email)
                            addr.save()
                            list.members.add(addr)
                            list.save()
                            num_imported = num_imported+1
                        except Warning:
                            pass
                    except ValidationError:
                        pass
        return "Successfully added %d entries to mailing list %s\n" % (num_imported , listname)