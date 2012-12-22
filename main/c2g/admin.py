#import reversion
from django.contrib import admin
from c2g.models import *
from django.contrib.auth.models import Group

admin.site.register(Institution)
admin.site.register(Course)
admin.site.register(Video)
admin.site.register(AdditionalPage)
admin.site.register(Announcement)
admin.site.register(ProblemSet)
admin.site.register(EmailAddr)
admin.site.register(ListEmail)
admin.site.register(CourseEmail)
admin.site.register(ContentSection)
admin.site.register(File)
admin.site.register(ProblemSetToExercise)
admin.site.register(Exercise)
admin.site.register(VideoToExercise)
admin.site.register(Exam)
admin.site.register(CurrentTermMap)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'birth_year', 'education', 'work', 'client_ip_first', 'user_agent_first', 'referrer_first', 'accept_language_first')

class GroupProxy(Group):
    class Meta:
        proxy = True

class ExamRecordAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','time_created','mode')
    readonly_fields = ('course','exam','student')
    #fields=['json_data']
    
    def mode(self, obj):
        return obj.course.mode

class ExamRecordScoreAdmin(admin.ModelAdmin):
    readonly_fields = ('record',)

class ExamRecordScoreFieldAdmin(admin.ModelAdmin):
    readonly_fields = ('parent',)

class ExamRecordScoreFieldChoiceAdmin(admin.ModelAdmin):
    readonly_fields = ('parent',)


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'count')
    def count(self, obj):
        return obj.user_set.count()

class MailingListAdmin(admin.ModelAdmin):
    readonly_fields = ('members',)

#class ExamAdmin(reversion.VersionAdmin):
#    pass


#admin.site.register(Exam, ExamAdmin)


admin.site.register(UserProfile, ProfileAdmin)
admin.site.register(GroupProxy, GroupAdmin)
admin.site.register(ExamRecord, ExamRecordAdmin)
admin.site.register(ExamRecordScore, ExamRecordScoreAdmin)
admin.site.register(ExamRecordScoreField, ExamRecordScoreFieldAdmin)
admin.site.register(ExamRecordScoreFieldChoice, ExamRecordScoreFieldChoiceAdmin)
admin.site.register(MailingList, MailingListAdmin)
