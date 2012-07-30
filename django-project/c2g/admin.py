from django.contrib import admin
from c2g.models import Institution, Course, Video, AdditionalPage, Announcement, ProblemSet

admin.site.register(Institution)
admin.site.register(Course)
admin.site.register(Video)
admin.site.register(AdditionalPage)
admin.site.register(Announcement)
admin.site.register(ProblemSet)