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

class Stageable(models.Model):
    mode = models.TextField(blank=True)
    image = models.ForeignKey('self', null=True, related_name="+")
    live_datetime = models.DateTimeField(editable=True, null=True)
    
    class Meta:
       abstract = True
    
class Sortable(models.Model):
    index=models.IntegerField(null=True, blank=True)

    def move_to(self, new_index):
        pass
        
    def move_up_by_one(self):
        pass
        
    def move_down_by_one(self):
       pass

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

class Course(TimestampMixin, Stageable, models.Model):
    institution = models.ForeignKey(Institution, db_index=True)
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

class AdditionalPage(TimestampMixin, Stageable, models.Model):
    course = models.ForeignKey(Course, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    
    def create_production_instance(self):
        production_instance = AdditionalPage(
            course=self.course,
            title=self.title,
            description=self.description,
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
        db_table = u'c2g_additional_pages'

#owner is person who posted
#does it need access_id?
class Announcement(TimestampMixin, models.Model):
    owner = models.ForeignKey(User)
    course = models.ForeignKey(Course, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = u'c2g_announcements'

#Let's use django file support or something else instead, but keep for now
#Need (owner,course) index here
class File(TimestampMixin, models.Model):
    owner = models.ForeignKey(User)
    course = models.ForeignKey(Course)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = u'c2g_files'

class StudentSection(TimestampMixin, models.Model):
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

class VideoTopic(TimestampMixin, Stageable, Sortable, models.Model):
    course = models.ForeignKey(Course, db_index=True)
    title = models.CharField(max_length=255)
    
    def create_production_instance(self):
        production_instance = VideoTopic(
            course=self.course.image,
            title=self.title,
            index = self.index,
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
            
        self.save()
    
    def __unicode__(self):
        return self.title

    class Meta:
        db_table = u'c2g_video_topics'


class Video(TimestampMixin, Stageable, Sortable, models.Model):
    course = models.ForeignKey(Course, db_index=True)
    topic = models.ForeignKey(VideoTopic, null=True, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=30, default="youtube")
    url = models.CharField(max_length=255, null=True)
    duration = models.IntegerField(blank=True)
    slug = models.CharField(max_length=255, null=True)
    
    def create_production_instance(self):
        production_instance = Video(
            course=self.course.image,
            topic=self.topic.image,
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

class ProblemSet(TimestampMixin, Stageable, models.Model):
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

<<<<<<< HEAD
class Problem(TimestampMixin, Stageable, models.Model):
    problem_set = models.ForeignKey(ProblemSet)
    problem_number = models.IntegerField(null=True, blank=True)
    
=======
class Exercise(TimestampMixin, models.Model):
    problemSet = models.ForeignKey(ProblemSet)
    fileName = models.CharField(max_length=255)
    def __unicode__(self):
        return self.number
    class Meta:
        db_table = u'c2g_exercises'

class Problem(TimestampMixin, models.Model):
    exercise = models.ForeignKey(Exercise)
    slug = models.CharField(max_length=255)
>>>>>>> 718741d3c4d9a71e19c4579a2cc1f30c927fea0f
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
