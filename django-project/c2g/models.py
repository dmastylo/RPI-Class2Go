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
from django.contrib.auth.models import User

class Institution(models.Model):
    id = models.BigIntegerField(primary_key=True)
    title = models.TextField()
    country = models.TextField(blank=True)
    city = models.TextField(blank=True)
    domains = models.TextField(blank=True)
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    class Meta:
        db_table = u'institutions'

class Course(models.Model):
    id = models.BigIntegerField(primary_key=True)
    institution = models.ForeignKey(Institution)
    code = models.TextField(blank=True)
    title = models.CharField(max_length=511, null=True, blank=True)
    listing_description = models.TextField(blank=True)
    mode = models.TextField(blank=True)
    description = models.TextField(blank=True)
    staff_emails = models.TextField(blank=True)
    instructors = models.ManyToManyField(User) #many-to-many
    tas = models.ManyToManyField(User, null=True) #many-to-many
    readonly_tas = models.ManyToManyField(User, null=True) #many-to-many
    term = models.TextField(blank=True)
    year = models.IntegerField(null=True, blank=True)
    calendar_start = models.DateField(null=True, blank=True)
    calendar_end = models.DateField(null=True, blank=True)
    meeting_info = models.TextField(blank=True)
    feature_settings = models.TextField(blank=True)
    membership_control = models.TextField(blank=True)
    join_password = models.TextField(blank=True)
    list_publicly = models.IntegerField(null=True, blank=True)
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    class Meta:
        db_table = u'courses'


#does additional pages need an owner?
#There's no social network
#here, so not every item need an owner.
#why overlap of write_access and access_id?
class AdditionalPage(models.Model):
    id = models.BigIntegerField(primary_key=True)
    #owner = models.ForeignKey(User)
    course = models.ForeignKey(Course)
    access_id = models.TextField(blank=True)
    write_access = models.TextField(blank=True)
    title = models.CharField(max_length=511, null=True, blank=True)
    description = models.TextField(blank=True)
    update_log = models.TextField(blank=True)
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    class Meta:
        db_table = u'additional_pages'

#owner is person who posted
#does it need access_id?
class Announcement(models.Model):
    id = models.BigIntegerField(primary_key=True)
    owner = models.ForeignKey(User)
    course = models.ForeignKey(Course)
    access_id = models.TextField(blank=True)
    title = models.CharField(max_length=511, null=True, blank=True)
    description = models.TextField(blank=True)
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    class Meta:
        db_table = u'announcements'


##ASSIGNMENTS SECTION####
#Assignments, AssigmentGrades, AssignmentSubmissions might need ondelete for User
class AssignmentCategory(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.ForeignKey(Courses)
    title = models.CharField(max_length=511, null=True, blank=True)
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    class Meta:
        db_table = u'assignment_categories'

#do we really need both an owner_id and an access_id?  There's no social network
#here, so not every item need an owner.
class Assignment(models.Model):
    id = models.BigIntegerField(primary_key=True)
    #owner_id = models.ForeignKey(User)
    course = models.ForeignKey(Course)
    category_id = models.ForeignKey(AssignmentCategory)
    access_id = models.TextField(blank=True)
    title = models.CharField(max_length=511, null=True, blank=True)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    close_date = models.DateTimeField(null=True, blank=True)
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    class Meta:
        db_table = u'assignments'

#deleted course
class AssignmentGrade(models.Model):
    #course = models.ForeignKey(Courses)
    id = models.BigIntegerField(primary_key=True)
    assignment = models.ForeignKey(Assignment)
    gradee = models.ForeignKey(User)
    json = models.TextField()
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    class Meta:
        db_table = u'assignment_grades'

#deleted course
class AssignmentSubmission(models.Model):
    id = models.BigIntegerField(primary_key=True)
    owner = models.ForeignKey(User)
    assignmet = models.ForeignKey(Assignment)
    #course = models.ForeignKey(Courses)
    json = models.TextField()
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    class Meta:
        db_table = u'assignment_submissions'


#what's the difference between this and UserCourseData
#they have the same fields
class CourseAnalytics(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.ForeignKey(Course)
    user = models.ForeignKey(User, null=True)
    json = models.TextField()
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    class Meta:
        db_table = u'course_analytics'

class CourseMap(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.ForeignKey(Course)
    json = models.TextField(blank=True)
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    class Meta:
        db_table = u'course_maps'

#Let's use django file support or something else instead, but keep for now
class File(models.Model):
    id = models.BigIntegerField(primary_key=True)
    owner = models.ForeignKey(User)
    course = models.ForeignKey(Course)
    access_id = models.TextField(blank=True)
    title = models.CharField(max_length=511, null=True, blank=True)
    description = models.TextField(blank=True)
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    class Meta:
        db_table = u'files'

#Let's completely delegate Forums elsewhere
#I have not edited these at all
#class ForumPostReplies(models.Model):
#    id = models.BigIntegerField(primary_key=True)
#    owner_id = models.IntegerField(null=True, blank=True)
#    forum_id = models.BigIntegerField()
#    forum_post_id = models.BigIntegerField()
#    description = models.TextField(blank=True)
#    rating_data = models.TextField(blank=True)
#    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
#    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
#    class Meta:
#        db_table = u'forum_post_replies'
#
#class ForumPosts(models.Model):
#    id = models.BigIntegerField(primary_key=True)
#    owner_id = models.IntegerField(null=True, blank=True)
#    forum_id = models.BigIntegerField()
#    title = models.CharField(max_length=511, null=True, blank=True)
#    description = models.TextField(blank=True)
#    rating_data = models.TextField(blank=True)
#    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
#    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
#    class Meta:
#        db_table = u'forum_posts'
#
#class Forums(models.Model):
#    id = models.BigIntegerField(primary_key=True)
#    access_id = models.TextField(blank=True)
#    course = models.BigIntegerField()
#    title = models.CharField(max_length=511, null=True, blank=True)
#    description = models.TextField(blank=True)
#    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
#    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
#    class Meta:
#        db_table = u'forums'


#Again, do lectures need owners?
class Lecture(models.Model):
    id = models.BigIntegerField(primary_key=True)
    #owner = models.ForeignKey(User)
    access_id = models.TextField(blank=True)
    course = models.ForeignKey(Course)
    title = models.CharField(max_length=511, null=True, blank=True)
    description = models.TextField(blank=True)
    calendar_start = models.DateTimeField(null=True, blank=True)
    calendar_end = models.DateTimeField(null=True, blank=True)
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    class Meta:
        db_table = u'lectures'

class Officehour(models.Model):
    id = models.BigIntegerField(primary_key=True)
    owner = models.ForeignKey(User)
    course = models.ForeignKey(Course)
    title = models.CharField(max_length=511, null=True, blank=True)
    description = models.TextField(blank=True)
    calendar_start = models.DateTimeField(null=True, blank=True)
    calendar_end = models.DateTimeField(null=True, blank=True)
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    class Meta:
        db_table = u'officehours'


class StudentSection(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.ForeignKey(Course)
    title = models.CharField(max_length=511, null=True, blank=True)
    capacity = models.IntegerField(default=999)
    members = models.ManyToManyField(User)
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    class Meta:
        db_table = u'sections'


#what's the difference between this and CourseAnalytics
#they have the same fields
class UserCourseData(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.ForeignKey(Course)
    user = models.ForeignKey(User)
    json = models.TextField()
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    class Meta:
        db_table = u'user_course_data'

#Extended storage fields for Users, in addition to django.contrib.auth.models
#Uses one-to-one as per django recommendations at
#https://docs.djangoproject.com/en/dev/topics/auth/#django.contrib.auth.models.User
class UserProfile(models.Model):
    id = models.BigIntegerField(primary_key=True)
    user = models.OneToOneField(User)
    is_instructor = models.IntegerField(null=True, blank=True)
    site_data = models.TextField(blank=True)
    class Meta:
        db_table = u'user_profiles'


class VideoTopic(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.ForeignKey(Course)
    title = models.CharField(max_length=255)
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)    
    class Meta:
        db_table = u'video_topics

#do Videos need owners?  What are index and segments and why are they text fields
#commenting out for now
class Video(models.Model):
    id = models.BigIntegerField(primary_key=True)
    #owner = models.ForeignKey(Usernull=True, blank=True)
    access_id = models.TextField(blank=True)
    course = models.ForeignKey(Courses)
    topic = models.ForeignKey(VideoTopic, null=True)
    title = models.CharField(max_length=511, null=True, blank=True)
    description = models.TextField(blank=True)
    #index = models.IntegerField(null=True, blank=True)
    #segments = models.TextField(blank=True)
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    class Meta:
        db_table = u'videos'

#video quizzes do not need owners or access
class VideoQuiz(models.Model):
    id = models.BigIntegerField(primary_key=True)
    video = models.ForeignKey(Video)
    json = models.TextField(blank=True)
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    class Meta:
        db_table = u'video_quizzes'

class VideoQuizQuestion(models.Model):
    id = models.BigIntegerField(primary_key=True)
    video_quiz = models.ForeignKey(VideoQuiz)
    time_in_video = models.IntegerField(default=0)
    title = models.CharField(max_length=511, null=True, blank=True)
    json = models.TextField(blank=True)
    class Meta:
        db_table = u'video_quiz_questions'

class VideoQuizSubmission(models.Model):
    id = models.BigIntegerField(primary_key=True)
    owner = models.ForeignKey(User)
    question = models.ForeignKey(VideoQuizQuestion) #
    time_in_video = models.IntegerField(default=0)
    video_metadata = models.IntegerField(null=True) # might use this for YouTube ID
    json = models.TextField(blank=True)
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    class Meta:
        db_table = u'video_quiz_submissions'


#video annotations may not need access_id
class VideoAnnotations(models.Model):
    id = models.BigIntegerField(primary_key=True)
    owner = models.ForeignKey(User, null=True, blank=True)
    #access_id = models.TextField(blank=True)
    video = models.ForeignKey(Video)
    time_in_video = models.IntegerField(default=0)
    title = models.CharField(max_length=511, null=True, blank=True)
    description = models.TextField(blank=True)
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    class Meta:
        db_table = u'video_annotations'




#For roles, can we make do somehow with built-in django permissions
#what custom features do we actually need here?
class Roles(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.ForeignKey(Courses)
    title = models.CharField(max_length=765)
    is_staff = models.IntegerField(null=True, blank=True)
    privileges = models.TextField(blank=True)
    holder_ids = models.TextField(blank=True)
    holder_count = models.BigIntegerField(null=True, blank=True)
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    class Meta:
        db_table = u'roles'


class SharingPermissions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    object_id = models.BigIntegerField()
    type = models.TextField(blank=True)
    licensee_id = models.BigIntegerField()
    cond_by = models.IntegerField(null=True, blank=True)
    cond_nc = models.IntegerField(null=True, blank=True)
    cond_nd = models.IntegerField(null=True, blank=True)
    cond_sa = models.IntegerField(null=True, blank=True)
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    class Meta:
        db_table = u'sharing_permissions'

