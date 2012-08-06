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
from django.db.models.signals import post_save
from django import forms
from datetime import datetime

import gdata.youtube
import gdata.youtube.service

# For file system upload
from django.core.files.storage import FileSystemStorage

class TimestampMixin(models.Model):
    time_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)

    def tellMeWhen(self):
       print ("Created: " + self.time_created.__str__() + "  Updated: " + self.last_updated.__str__())

    class Meta:
       abstract = True

class Stageable(models.Model):
    mode = models.TextField(blank=True)
    image = models.ForeignKey('self', null=True, related_name="+")
    live_datetime = models.DateTimeField(editable=True, null=True)

    class Meta:
       abstract = True

class Sortable(models.Model):
    index=models.IntegerField(null=True, blank=True)

    class Meta:
       abstract = True
       
class Deletable(models.Model):
    is_deleted=models.IntegerField(default=0)
    
    def delete(self):
        self.is_deleted = 1
        fields = self._meta.fields
        for field in fields:
            if field.name == 'slug':
                self.slug = ''
                break
        self.save()
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

class Course(TimestampMixin, Stageable, Deletable, models.Model):
    institution = models.ForeignKey(Institution, null=True, db_index=True)
    student_group = models.ForeignKey(Group, related_name="student_group", db_index=True)
    instructor_group = models.ForeignKey(Group, related_name="instructor_group", db_index=True)
    tas_group = models.ForeignKey(Group, related_name="tas_group", db_index=True)
    readonly_tas_group = models.ForeignKey(Group, related_name="readonly_tas_group", db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    syllabus = models.TextField(blank=True)
    term = models.TextField(blank=True)
    year = models.IntegerField(null=True, blank=True)
    calendar_start = models.DateField(null=True, blank=True)
    calendar_end = models.DateField(null=True, blank=True)
    list_publicly = models.IntegerField(null=True, blank=True)
    handle = models.CharField(max_length=255, null=True, db_index=True)

    def __unicode__(self):
        return self.title

    def create_production_instance(self):
        production_instance = Course(institution = self.institution,
            student_group = self.student_group,
            instructor_group = self.instructor_group,
            tas_group = self.tas_group,
            readonly_tas_group = self.readonly_tas_group,
            title = self.title,
            description = self.description,
            syllabus = self.syllabus,
            term = self.term,
            year = self.year,
            calendar_start = self.calendar_start,
            calendar_end = self.calendar_end,
            list_publicly = 0,
            image = self,
            mode = 'production',
            handle = self.handle,
        )
        production_instance.save()
        self.image = production_instance
        self.save()

    def commit(self, clone_fields = None):
        if self.mode != 'staging': return;

        production_instance = self.image
        if not clone_fields or 'institution' in clone_fields:
            production_instance.institution = self.institution
        if not clone_fields or 'title' in clone_fields:
            production_instance.title = self.title
        if not clone_fields or 'description' in clone_fields:
            production_instance.description = self.description
        if not clone_fields or 'syllabus' in clone_fields:
            production_instance.syllabus = self.syllabus
        if not clone_fields or 'term' in clone_fields:
            production_instance.term = self.term
        if not clone_fields or 'year' in clone_fields:
            production_instance.year = self.year
        if not clone_fields or 'calendar_start' in clone_fields:
            production_instance.calendar_start = self.calendar_start
        if not clone_fields or 'calendar_end' in clone_fields:
            production_instance.calendar_end = self.calendar_end

        production_instance.save()

    def revert(self, clone_fields = None):
        if self.mode != 'staging': return;

        production_instance = self.image
        if not clone_fields or 'institution' in clone_fields:
            self.institution = production_instance.institution
        if not clone_fields or 'title' in clone_fields:
            self.title = production_instance.title
        if not clone_fields or 'description' in clone_fields:
            self.description = production_instance.description
        if not clone_fields or 'syllabus' in clone_fields:
            self.syllabus = production_instance.syllabus
        if not clone_fields or 'term' in clone_fields:
            self.term = production_instance.term
        if not clone_fields or 'year' in clone_fields:
            self.year = production_instance.year
        if not clone_fields or 'calendar_start' in clone_fields:
            self.calendar_start = production_instance.calendar_start
        if not clone_fields or 'calendar_end' in clone_fields:
            self.calendar_end = production_instance.calendar_end

        self.save()

    class Meta:
        db_table = u'c2g_courses'

class GetAdditionalPagesByCourse(models.Manager):
    def getByCourse(self, course):
        all_items = self.filter(course=course).order_by('index')
        now = datetime.now()
        returned_items = []
        for item in all_items:
            if item.is_deleted == 0:
                returned_items.append(item)
        return returned_items
        
class AdditionalPage(TimestampMixin, Stageable, Sortable, Deletable, models.Model):
    course = models.ForeignKey(Course, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    slug = models.CharField(max_length=255, null=True, blank=True)
    objects = GetAdditionalPagesByCourse()
    
    def create_production_instance(self):
        production_instance = AdditionalPage(
            course=self.course.image,
            title=self.title,
            description=self.description,
            slug=self.slug,
            index=self.index,
            mode='production',
            image=self,
        )
        production_instance.save()
        self.image=production_instance
        self.save()

    def commit(self, clone_fields = None):
        if self.mode != 'staging': return;

        production_instance = self.image
        if not clone_fields or 'title' in clone_fields:
            production_instance.title = self.title
        if not clone_fields or 'description' in clone_fields:
            production_instance.description = self.description
        if not clone_fields or 'index' in clone_fields:
            production_instance.index = self.index

        production_instance.save()

    def revert(self, clone_fields = None):
        if self.mode != 'staging': return;

        production_instance = self.image
        if not clone_fields or 'title' in clone_fields:
            self.title = production_instance.title
        if not clone_fields or 'description' in clone_fields:
            self.description = production_instance.description
        if not clone_fields or 'index' in clone_fields:
            self.index = production_instance.index

        self.save()
    def getCourseAdditionalPages(self,course):
        now = datetime.now()
        pages = []
        all_pages = AdditionalPage.objects.filter(course=course)
        for page in pages:
            if page.is_deleted == 0 and (course.mode == 'staging' or page.live_datetime < now):
                pages.append(page)
        return pages
        
    class Meta:
        db_table = u'c2g_additional_pages'


class GetAnnouncementsByCourse(models.Manager):
    def getByCourse(self, course):
        all_items = self.filter(course=course).order_by('-time_created')
        now = datetime.now()
        returned_items = []
        for item in all_items:
            if item.is_deleted == 0:
                returned_items.append(item)
        return returned_items
        
class Announcement(TimestampMixin, Stageable, Sortable, Deletable, models.Model):
    owner = models.ForeignKey(User)
    course = models.ForeignKey(Course, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    objects = GetAnnouncementsByCourse()
    
    def create_production_instance(self):
        production_instance = Announcement(
            course=self.course.image,
            title=self.title,
            description=self.description,
            owner = self.owner,
            mode='production',
            image=self,
        )
        production_instance.save()
        self.image=production_instance
        self.save()

    def commit(self, clone_fields = None):
        if self.mode != 'staging': return;

        production_instance = self.image
        if not clone_fields or 'title' in clone_fields:
            production_instance.title = self.title
        if not clone_fields or 'description' in clone_fields:
            production_instance.description = self.description

        production_instance.save()

    def revert(self, clone_fields = None):
        if self.mode != 'staging': return;

        production_instance = self.image
        if not clone_fields or 'title' in clone_fields:
            self.title = production_instance.title
        if not clone_fields or 'description' in clone_fields:
            self.description = production_instance.description

        self.save()

    class Meta:
        db_table = u'c2g_announcements'

class GetContentSectionsByCourse(models.Manager):
    def getByCourse(self, course):
        all_items = self.filter(course=course).order_by('index')
        now = datetime.now()
        returned_items = []
        for item in all_items:
            if item.is_deleted == 0:
                returned_items.append(item)
        return returned_items
        
class ContentSection(TimestampMixin, Stageable, Sortable, Deletable, models.Model):
    course = models.ForeignKey(Course, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    objects = GetContentSectionsByCourse()
    
    def create_production_instance(self):
        production_instance = ContentSection(
            course=self.course.image,
            title=self.title,
            index=self.index,
            mode='production',
            image=self,
        )
        production_instance.save()
        self.image=production_instance
        self.save()

    def commit(self, clone_fields = None):
        if self.mode != 'staging': return;

        production_instance = self.image
        if not clone_fields or 'title' in clone_fields:
            production_instance.title = self.title
        if not clone_fields or 'index' in clone_fields:
            production_instance.index = self.index

        production_instance.save()

    def revert(self, clone_fields = None):
        if self.mode != 'staging': return;

        production_instance = self.image
        if not clone_fields or 'title' in clone_fields:
            self.title = production_instance.title
        if not clone_fields or 'index' in clone_fields:
            self.index = production_instance.index

        self.save()

    def __unicode__(self):
        return self.title

    class Meta:
        db_table = u'c2g_content_sections'

class StudentSection(TimestampMixin, Deletable, models.Model):
    course = models.ForeignKey(Course, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    capacity = models.IntegerField(default=999)
    members = models.ManyToManyField(User)
    class Meta:
        db_table = u'c2g_sections'

#Extended storage fields for Users, in addition to django.contrib.auth.models
#Uses one-to-one as per django recommendations at
#https://docs.djangoproject.com/en/dev/topics/auth/#django.contrib.auth.models.User
class UserProfile(models.Model):
    user = models.OneToOneField(User, db_index=True)
    site_data = models.TextField(blank=True)
    class Meta:
        db_table = u'c2g_user_profiles'

def create_user_profile(sender, instance, created, raw, **kwargs):
    if created and not raw:  #create means that a new DB entry is created, raw is set when fixtures are being loaded
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

class GetVideosByCourse(models.Manager):
    def getByCourse(self, course):
        all_items = self.filter(course=course).order_by('section_id','index')
        now = datetime.now()
        returned_items = []
        for item in all_items:
            if item.is_deleted == 0 and (course.mode == 'staging' or item.live_datetime < now):
                returned_items.append(item)
        return returned_items
        
class Video(TimestampMixin, Stageable, Sortable, Deletable, models.Model):
    course = models.ForeignKey(Course, db_index=True)
    section = models.ForeignKey(ContentSection, null=True, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=30, default="youtube")
    url = models.CharField(max_length=255, null=True)
    duration = models.IntegerField(null=True)
    slug = models.CharField(max_length=255, null=True)
    objects = GetVideosByCourse()
    
    def create_production_instance(self):
        production_instance = Video(
            course=self.course.image,
            section=self.section.image,
            title=self.title,
            description=self.description,
            type=self.type,
            url=self.url,
            duration=self.duration,
            slug=self.slug,
            image = self,
            mode = 'production',
        )
        production_instance.save()
        self.image = production_instance
        self.save()

    def commit(self, clone_fields = None):
        if self.mode != 'staging': return;

        production_instance = self.image
        if not clone_fields or 'title' in clone_fields:
            production_instance.title = self.title
        if not clone_fields or 'index' in clone_fields:
            production_instance.index = self.index

        production_instance.save()

    def revert(self, clone_fields = None):
        if self.mode != 'staging': return;

        production_instance = self.image
        if not clone_fields or 'title' in clone_fields:
            self.title = production_instance.title
        if not clone_fields or 'index' in clone_fields:
            self.index = production_instance.index

    def save(self, *args, **kwargs):
        if not self.duration:
            if self.type == "youtube" and self.url:
                yt_service = gdata.youtube.service.YouTubeService()
                entry = yt_service.GetYouTubeVideoEntry(video_id=self.url)
                self.duration = entry.media.duration.seconds
        super(Video, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title

    class Meta:
        db_table = u'c2g_videos'

class VideoActivity(models.Model):
     student = models.ForeignKey(User)
     course = models.ForeignKey(Course)
     video = models.ForeignKey(Video)
     start_seconds = models.IntegerField(default=0, blank=True)
     #last_watched = models.DateTimeField(auto_now=True, auto_now_add=False)

     def percent_done(self):
         return float(self.start_seconds)*100/self.video.duration

     def __unicode__(self):
            return self.student.username
     class Meta:
        db_table = u'c2g_video_activity'

class GetProblemSetsByCourse(models.Manager):
    def getByCourse(self, course):
        all_items = self.filter(course=course).order_by('section_id','index')
        now = datetime.now()
        returned_items = []
        for item in all_items:
            if item.is_deleted == 0 and (course.mode == 'staging' or item.live_datetime < now):
                returned_items.append(item)
        return returned_items
        
class ProblemSet(TimestampMixin, Stageable, Sortable, Deletable, models.Model):
    course = models.ForeignKey(Course)
    section = models.ForeignKey(ContentSection, null=True, db_index=True)
    slug = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    path = models.CharField(max_length=255)
    due_date = models.DateTimeField(null=True, blank=True)
    grace_period = models.DateTimeField(null=True, blank=True)
    partial_credit_deadline = models.DateTimeField(null=True, blank=True)
    penalty_preference = models.CharField(max_length=255)
    late_penalty = models.IntegerField(null=True, blank=True)
    submissions_permitted = models.IntegerField(null=True, blank=True)
    resubmission_penalty = models.IntegerField(null=True, blank=True)
    randomize = models.BooleanField()
    objects = GetProblemSetsByCourse()
    
    def create_production_instance(self):
        production_instance = ProblemSet(
            course=self.course.image,
            section=self.section.image,
            slug=self.slug,
            title=self.title,
            description=self.description,
            path=self.path,
            live_datetime=self.live_datetime,
            due_date=self.due_date,
            grace_period=self.grace_period,
            partial_credit_deadline=self.partial_credit_deadline,
            penalty_preference=self.penalty_preference,
            late_penalty=self.late_penalty,
            submissions_permitted=self.submissions_permitted,
            resubmission_penalty=self.resubmission_penalty,
            randomize=self.randomize,
            index=self.index,
            image = self,
            mode = 'production',
        )
        production_instance.save()
        self.image = production_instance
        self.save()
        return production_instance

    def commit(self, clone_fields = None):
        if self.mode != 'staging': return;

        production_instance = self.image
        if not clone_fields or 'title' in clone_fields:
            production_instance.title = self.title
        if not clone_fields or 'description' in clone_fields:
            production_instance.description = self.description
        if not clone_fields or 'path' in clone_fields:
            production_instance.path = self.path
        if not clone_fields or 'slug' in clone_fields:
            production_instance.slug = self.slug
        if not clone_fields or 'index' in clone_fields:
            production_instance.index = self.index

        production_instance.save()

    def revert(self, clone_fields = None):
        if self.mode != 'staging': return;

        production_instance = self.image
        if not clone_fields or 'title' in clone_fields:
            self.title = production_instance.title
        if not clone_fields or 'description' in clone_fields:
            self.description = production_instance.description
        if not clone_fields or 'path' in clone_fields:
            self.path = production_instance.path
        if not clone_fields or 'slug' in clone_fields:
            self.slug = production_instance.slug
        if not clone_fields or 'index' in clone_fields:
            self.index = production_instance.index

    def __unicode__(self):
        return self.title
    class Meta:
        db_table = u'c2g_problem_sets'

class Exercise(TimestampMixin, Deletable, models.Model):
    problemSet = models.ManyToManyField(ProblemSet, through='ProblemSetToExercise')
    fileName = models.CharField(max_length=255)
    file = models.FileField(upload_to='exercise_files', null=True)
    def __unicode__(self):
        return self.fileName
    class Meta:
        db_table = u'c2g_exercises'

class ProblemSetToExercise(models.Model):
    problemSet = models.ForeignKey(ProblemSet)
    exercise = models.ForeignKey(Exercise)
    number = models.IntegerField(null=True, blank=True)
    def __unicode__(self):
        return self.problemSet.title + "-" + self.exercise.fileName
    class Meta:
        db_table = u'c2g_problemset_to_exercise'

class Problem(TimestampMixin, Stageable, Deletable, models.Model):
    exercise = models.ForeignKey(Exercise)
    slug = models.CharField(max_length=255)

    def __unicode__(self):
        return self.number
    class Meta:
        db_table = u'c2g_problems'

class ProblemActivity(TimestampMixin, models.Model):
     student = models.ForeignKey(User)
     exercise = models.ForeignKey(Exercise, null=True)
     problem = models.ForeignKey(Problem, null=True)
     complete = models.IntegerField(null=True, blank=True)
     attempt_content = models.TextField(null=True, blank=True)
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
