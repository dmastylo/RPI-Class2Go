from django.contrib import admin
from c2g.models import Institution, Course, Video, AdditionalPage, Announcement, VideoTopic, VideoQuiz, VideoQuizQuestion, VideoQuizSubmission, AssignmentCategory, Assignment, AssignmentSubmission, ProblemSet

admin.site.register(Institution)
admin.site.register(Course)
admin.site.register(Video)
admin.site.register(AdditionalPage)
admin.site.register(Announcement)
admin.site.register(VideoTopic)
admin.site.register(VideoQuiz)
admin.site.register(VideoQuizQuestion)
admin.site.register(VideoQuizSubmission)
admin.site.register(ProblemSet)

