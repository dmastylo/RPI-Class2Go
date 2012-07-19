# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

#c2g specific comments
# any table indexes that use only one column here are place here.
# any table indexes that use multiple columns are placed in a south migration at
# <location to be inserted>

from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, pre_save
from django import forms

import gdata.youtube
import gdata.youtube.service

class TimestampMixin(models.Model):
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)

    def tellMeWhen(self):
       print ("Created: " + self.time_created.__str__() + "  Updated: " + self.last_updated.__str__())

    class Meta:
       abstract = True


class Institution(TimestampMixin, models.Model):
#    #id = models.BigIntegerField(primary_key=True)
    title = models.TextField()
    country = models.TextField(blank=True)
    city = models.TextField(blank=True)
    domains = models.TextField(blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        db_table = u'c2g_institutions'

class Course(TimestampMixin, models.Model):
#    #id = models.BigIntegerField(primary_key=True)
    institution = models.ForeignKey(Institution, db_index=True)
    student_group = models.ForeignKey(Group, related_name="student_group", db_index=True)
    instructor_group = models.ForeignKey(Group, related_name="instructor_group", db_index=True)
    tas_group = models.ForeignKey(Group, related_name="tas_group", db_index=True)
    readonly_tas_group = models.ForeignKey(Group, related_name="readonly_tas_group", db_index=True)
    code = models.TextField(blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    listing_description = models.TextField(blank=True)
    mode = models.TextField(blank=True)
    description = models.TextField(blank=True)
    staff_emails = models.TextField(blank=True)
    term = models.TextField(blank=True)
    year = models.IntegerField(null=True, blank=True)
    calendar_start = models.DateField(null=True, blank=True)
    calendar_end = models.DateField(null=True, blank=True)
    meeting_info = models.TextField(blank=True)
    feature_settings = models.TextField(blank=True)
    membership_control = models.TextField(blank=True)
    join_password = models.TextField(blank=True)
    list_publicly = models.IntegerField(null=True, blank=True)
    handle = models.CharField(max_length=255, null=True, unique=True, db_index=True)

    def __unicode__(self):
        return self.title

    class Meta:
        db_table = u'c2g_courses'


def defineUserGroupsForCourse(sender, **kwargs):
    instance = kwargs.get('instance')
    if (not hasattr(instance,'student_group')):
        instance.student_group = Group.objects.create( name="Student Group for " + instance.handle + "_" + str(instance.institution.id))
    if (not hasattr(instance,'instructor_group')):
        instance.instructor_group = Group.objects.create(name="Instructor Group for " + instance.handle + "_" + str(instance.institution.id))
    if (not hasattr(instance,'tas_group')):
        instance.tas_group = Group.objects.create(name="TAS Group for " + instance.handle + "_" + str(instance.institution.id))
    if (not hasattr(instance,'readonly_tas_group')):
        instance.readonly_tas_group = Group.objects.create(name="Readonly TAS Group for " + instance.handle + "_" + str(instance.institution.id))


pre_save.connect(defineUserGroupsForCourse, sender=Course)




#does additional pages need an owner?
#There's no social network
#here, so not every item need an owner.
#why overlap of write_access and access_id?
class AdditionalPage(TimestampMixin, models.Model):
#   #id = models.BigIntegerField(primary_key=True)
    #owner = models.ForeignKey(User)
    course = models.ForeignKey(Course, db_index=True)
    access_id = models.TextField(blank=True)
    write_access = models.TextField(blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    update_log = models.TextField(blank=True)
    class Meta:
        db_table = u'c2g_additional_pages'

#owner is person who posted
#does it need access_id?
class Announcement(TimestampMixin, models.Model):
    #id = models.BigIntegerField(primary_key=True)
    owner = models.ForeignKey(User)
    course = models.ForeignKey(Course, db_index=True)
    access_id = models.TextField(blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = u'c2g_announcements'


##ASSIGNMENTS SECTION####
#Assignments, AssigmentGrades, AssignmentSubmissions might need ondelete for User
class AssignmentCategory(TimestampMixin, models.Model):
    #id = models.BigIntegerField(primary_key=True)
    course = models.ForeignKey(Course, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    class Meta:
        db_table = u'c2g_assignment_categories'

#do we really need both an owner_id and an access_id?  There's no social network
#here, so not every item need an owner.
class Assignment(TimestampMixin, models.Model):
    #id = models.BigIntegerField(primary_key=True)
    #owner_id = models.ForeignKey(User)
    course = models.ForeignKey(Course, db_index=True)
    category = models.ForeignKey(AssignmentCategory, db_index=True)
    access_id = models.TextField(blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    close_date = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'c2g_assignments'

#deleted course
#Need to have a double-column (assignment, user) index here
class AssignmentGrade(TimestampMixin, models.Model):
    #id = models.BigIntegerField(primary_key=True)
    user = models.ForeignKey(User)
    #course = models.ForeignKey(Course)
    assignment = models.ForeignKey(Assignment)
    json = models.TextField()
    class Meta:
        db_table = u'c2g_assignment_grades'

#deleted course
#Need to have a double-column (assignmer, owner) index here
class AssignmentSubmission(TimestampMixin, models.Model):
    #id = models.BigIntegerField(primary_key=True)
    owner = models.ForeignKey(User)
    #course = models.ForeignKey(Course)
    assignment = models.ForeignKey(Assignment)
    json = models.TextField()
    class Meta:
        db_table = u'c2g_assignment_submissions'


#what's the difference between this and UserCourseData
#they have the same fields
#need to have (user,course) index here
class CourseAnalytics(TimestampMixin, models.Model):
    #id = models.BigIntegerField(primary_key=True)
    user = models.ForeignKey(User, null=True)
    course = models.ForeignKey(Course)
    json = models.TextField()
    class Meta:
        db_table = u'c2g_course_analytics'

class CourseMap(TimestampMixin, models.Model):
    #id = models.BigIntegerField(primary_key=True)
    course = models.ForeignKey(Course, db_index=True)
    json = models.TextField(blank=True)
    class Meta:
        db_table = u'c2g_course_maps'

#Let's use django file support or something else instead, but keep for now
#Need (owner,course) index here
class File(TimestampMixin, models.Model):
    #id = models.BigIntegerField(primary_key=True)
    owner = models.ForeignKey(User)
    course = models.ForeignKey(Course)
    access_id = models.TextField(blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = u'c2g_files'

#Let's completely delegate Forums elsewhere
#I have not edited these at all
#class ForumPostReplies(models.Model):
#    #id = models.BigIntegerField(primary_key=True)
#    owner_id = models.IntegerField(null=True, blank=True)
#    forum_id = models.BigIntegerField()
#    forum_post_id = models.BigIntegerField()
#    description = models.TextField(blank=True)
#    rating_data = models.TextField(blank=True)
#    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
#    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
#    class Meta:
#        db_table = u'c2g_forum_post_replies'
#
#class ForumPosts(models.Model):
#    #id = models.BigIntegerField(primary_key=True)
#    owner_id = models.IntegerField(null=True, blank=True)
#    forum_id = models.BigIntegerField()
#    title = models.CharField(max_length=255, null=True, blank=True)
#    description = models.TextField(blank=True)
#    rating_data = models.TextField(blank=True)
#    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
#    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
#    class Meta:
#        db_table = u'c2g_forum_posts'
#
#class Forums(models.Model):
#    #id = models.BigIntegerField(primary_key=True)
#    access_id = models.TextField(blank=True)
#    coure = models.BigIntegerField()
#    title = models.CharField(max_length=255, null=True, blank=True)
#    description = models.TextField(blank=True)
#    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
#    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
#    class Meta:
#        db_table = u'c2g_forums'


#Again, do lectures need owners?
class Lecture(TimestampMixin, models.Model):
    #id = models.BigIntegerField(primary_key=True)
    #owner = models.ForeignKey(User)
    course = models.ForeignKey(Course, db_index=True)
    access_id = models.TextField(blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    calendar_start = models.DateTimeField(null=True, blank=True)
    calendar_end = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'c2g_lectures'

class Officehour(TimestampMixin, models.Model):
    #id = models.BigIntegerField(primary_key=True)
    owner = models.ForeignKey(User)
    course = models.ForeignKey(Course)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    calendar_start = models.DateTimeField(null=True, blank=True)
    calendar_end = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'c2g_officehours'


class StudentSection(TimestampMixin, models.Model):
    #id = models.BigIntegerField(primary_key=True)
    course = models.ForeignKey(Course, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    capacity = models.IntegerField(default=999)
    members = models.ManyToManyField(User)
    class Meta:
        db_table = u'c2g_sections'


#what's the difference between this and CourseAnalytics
#they have the same fields
class UserCourseData(TimestampMixin, models.Model):
    #id = models.BigIntegerField(primary_key=True)
    user = models.ForeignKey(User)
    course = models.ForeignKey(Course)
    json = models.TextField()
    class Meta:
        db_table = u'c2g_user_course_data'

#Extended storage fields for Users, in addition to django.contrib.auth.models
#Uses one-to-one as per django recommendations at
#https://docs.djangoproject.com/en/dev/topics/auth/#django.contrib.auth.models.User
class UserProfile(models.Model):
    #id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, db_index=True)
    site_data = models.TextField(blank=True)
    class Meta:
        db_table = u'c2g_user_profiles'

def create_user_profile(sender, instance, created, raw, **kwargs):
    if created and not raw:  #create means that a new DB entry is created, raw is set when fixtures are being loaded
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

class VideoTopic(TimestampMixin, models.Model):
    #id = models.BigIntegerField(primary_key=True)
    course = models.ForeignKey(Course, db_index=True)
    title = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title

    class Meta:
        db_table = u'c2g_video_topics'


#do Videos need owners?  What are index and segments and why are they text fields
#commenting out for now
class Video(TimestampMixin, models.Model):
    #id = models.BigIntegerField(primary_key=True)
    #owner = models.ForeignKey(User, null=True, blank=True)
    course = models.ForeignKey(Course, db_index=True)
    topic = models.ForeignKey(VideoTopic, null=True, db_index=True)
    access_id = models.TextField(blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    #index = models.IntegerField(null=True, blank=True)
    #segments = models.TextField(blank=True)
    type = models.CharField(max_length=30, default="youtube")
    url = models.CharField(max_length=255, null=True)
    start_seconds = models.IntegerField(default=0, blank=True)
    duration = models.IntegerField(blank=True)

    def save(self, *args, **kwargs):
        if not self.duration:
            if self.type == "youtube":
                yt_service = gdata.youtube.service.YouTubeService()
                entry = yt_service.GetYouTubeVideoEntry(video_id=self.url)
                self.duration = entry.media.duration.seconds
        super(Video, self).save(*args, **kwargs)
        
    def percent_done(self):
        return float(self.start_seconds*100)/self.duration

    def __unicode__(self):
        return self.title

    class Meta:
        db_table = u'c2g_videos'

#video quizzes do not need owners or access
class VideoQuiz(TimestampMixin, models.Model):
    #id = models.BigIntegerField(primary_key=True)
    video = models.ForeignKey(Video, db_index=True)
    json = models.TextField(blank=True)
    class Meta:
        db_table = u'c2g_video_quizzes'

class VideoQuizQuestion(models.Model):
    #id = models.BigIntegerField(primary_key=True)
    video_quiz = models.ForeignKey(VideoQuiz, db_index=True)
    time_in_video = models.IntegerField(default=0)
    title = models.CharField(max_length=255, null=True, blank=True)
    json = models.TextField(blank=True)
    class Meta:
        db_table = u'c2g_video_quiz_questions'


#Need (owner, question) index
class VideoQuizSubmission(TimestampMixin, models.Model):
    #id = models.BigIntegerField(primary_key=True)
    owner = models.ForeignKey(User)
    question = models.ForeignKey(VideoQuizQuestion) #
    time_in_video = models.IntegerField(default=0)
    video_metadata = models.IntegerField(null=True) # might use this for YouTube ID
    json = models.TextField(blank=True)
    class Meta:
        db_table = u'c2g_video_quiz_submissions'


#video annotations may not need access_id
#need (owner,video) index
class VideoAnnotation(TimestampMixin, models.Model):
    #id = models.BigIntegerField(primary_key=True)
    owner = models.ForeignKey(User, null=True, blank=True)
    #access_id = models.TextField(blank=True)
    video = models.ForeignKey(Video)
    time_in_video = models.IntegerField(default=0)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = u'c2g_video_annotations'



class SharingPermission(TimestampMixin, models.Model):
    #id = models.BigIntegerField(primary_key=True)
    object_id = models.BigIntegerField(db_index=True)
    type = models.TextField(blank=True)
    licensee_id = models.BigIntegerField()
    cond_by = models.IntegerField(null=True, blank=True)
    cond_nc = models.IntegerField(null=True, blank=True)
    cond_nd = models.IntegerField(null=True, blank=True)
    cond_sa = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'c2g_sharing_permissions'


class instance_status(models.Model):
    prefix = models.CharField(max_length=30, null=True, db_index=True)
    current_prod = models.ForeignKey(Course, related_name="current_prod", null=True, db_index=True)
    current_staging = models.ForeignKey(Course, related_name="current_staging", null=True, db_index=True)
    class Meta:
        db_table = u'c2g_instance_status'

class ProblemSet(TimestampMixin, models.Model):
    course = models.ForeignKey(Course)
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    path = models.CharField(max_length=255)
    soft_deadline = models.DateTimeField(null=True, blank=True)
    hard_deadline = models.DateTimeField(null=True, blank=True)
    def __unicode__(self):
        return self.title
    class Meta:
        db_table = u'c2g_problem_sets'

class Problem(TimestampMixin, models.Model):
    problem_set = models.ForeignKey(ProblemSet)
    problem_number = models.IntegerField(null=True, blank=True)
    def __unicode__(self):
        return self.problem_number
    class Meta:
        db_table = u'c2g_problems'

class ProblemActivity(models.Model):
     student = models.ForeignKey(User)
     course = models.ForeignKey(Course)
     problem_set = models.ForeignKey(ProblemSet, null=True)
     problem = models.ForeignKey(Problem, null=True)
     complete = models.IntegerField(null=True, blank=True)
     count_hints = models.IntegerField(null=True, blank=True)
     time_taken = models.IntegerField(null=True, blank=True)
     attempt_number = models.IntegerField(null=True, blank=True)
     sha1 = models.TextField(blank=True)
     seed = models.TextField(blank=True)
     problem_type = models.TextField(blank=True)
     review_mode = models.IntegerField(null=True, blank=True)
     topic_mode = models.IntegerField(null=True, blank=True)
     casing = models.TextField(blank=True)
     card = models.TextField(blank=True)
     cards_done = models.IntegerField(null=True, blank=True)
     cards_left = models.IntegerField(null=True, blank=True)
     def __unicode__(self):
            return self.student.username
     class Meta:
        db_table = u'c2g_problem_activity'

class NewsEvent(models.Model):
    course = models.ForeignKey(Course)
    event = models.CharField(max_length=255)
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.event
    class Meta:
        db_table = u'c2g_news_events'

class EditProfileForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.CharField(max_length=30)
