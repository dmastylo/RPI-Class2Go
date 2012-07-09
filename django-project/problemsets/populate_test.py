from c2g.models import Institution, Course, ProblemSet
from django.contrib.auth.models import Group

i = Institution(title='Stanford University')
i.save()
gs = Group(name='nlp_students')
gs.save()
gta = Group(name='nlp_tas')
gta.save()
gi = Group(name='nlp_instructors')
gi.save()
gr = Group(name='nlp_readonly_tas')
gr.save()
c = Course(institution=i, course_prefix='nlp', title='nlp-staging',student_group=gs, instructor_group=gi, tas_group=gta, readonly_tas_group=gr)
c.save()
p1 = ProblemSet(course=c, title='P1', path='/static/latestKhan/exercises/P1.html')
p2 = ProblemSet(course=c, title='P2', path='/static/latestKhan/exercises/P2.html')
p1.save()
p2.save()
