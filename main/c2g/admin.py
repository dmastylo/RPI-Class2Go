from django.contrib import admin
from c2g.models import Institution, Course, Video, AdditionalPage, Announcement, ProblemSet, UserProfile, EmailAddr, MailingList, ListEmail
from django.contrib.auth.models import Group

admin.site.register(Institution)
admin.site.register(Course)
admin.site.register(Video)
admin.site.register(AdditionalPage)
admin.site.register(Announcement)
admin.site.register(ProblemSet)
admin.site.register(EmailAddr)
admin.site.register(MailingList)
admin.site.register(ListEmail)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'birth_year', 'education', 'work', 'client_ip_first', 'user_agent_first', 'referrer_first', 'accept_language_first')

class GroupProxy(Group):
    class Meta:
        proxy = True


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'count')
    def count(self, obj):
        return obj.user_set.count()

admin.site.register(UserProfile, ProfileAdmin)
admin.site.register(GroupProxy, GroupAdmin)
