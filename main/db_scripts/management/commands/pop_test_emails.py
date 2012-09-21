from django.core.management.base import BaseCommand, CommandError
from c2g.models import Course
from django.contrib.auth.models import User, Group
from django.db.utils import IntegrityError
class Command(BaseCommand):
    help = "Adds some random students, all with valid emails, to test course to test sending a ton of emails"

    def handle(self, *args, **options):
        try:
            course = Course.objects.get(title='test course',mode='ready')
        except Course.DoesNotExist:
            self.stderr.write('No Test Course, so bailing out')
            return
        for (name,email) in [
                             #('sef','sefklon@gmail.com'),
                             ('jbau','jbau@stanford.edu'),
                             #('david','dcadams@stanford.edu'),
                             #('wescott','mwescott@stanford.edu'),
                             #('sherif','halawa@stanford.edu'),
                             #('jane','jinpa@stanford.edu')
                             ]:
            for i in range(100):
                try:
                    user=User(username=name+str(i), email=email)
                    user.save()
                except IntegrityError:
                    user=User.objects.get(username=name+str(i))
                    

                course.student_group.user_set.add(user)

