from django.contrib import admin
from c2g.models import Institution, Course, Video, AdditionalPage, Announcement, ProblemSet, UserProfile

admin.site.register(Institution)
admin.site.register(Course)
admin.site.register(Video)
admin.site.register(AdditionalPage)
admin.site.register(Announcement)
admin.site.register(ProblemSet)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'birth_year', 'education', 'work', 'client_ip_first', 'user_agent_first', 'referrer_first', 'accept_language_first')
    

admin.site.register(UserProfile, ProfileAdmin)

