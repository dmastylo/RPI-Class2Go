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
from django.core.exceptions import ValidationError
import gdata.youtube
import gdata.youtube.service
import os
import time
import sys

# For file system upload
from django.core.files.storage import FileSystemStorage

def get_file_path(instance, filename):
    parts = str(instance.handle).split("--")
    if isinstance(instance, Exercise):
        return os.path.join(str(parts[0]), str(parts[1]), 'exercises', filename)
    if isinstance(instance, Video):
        return os.path.join(str(parts[0]), str(parts[1]), 'videos', str(instance.id), filename)
    if isinstance(instance, File):
        return os.path.join(str(parts[0]), str(parts[1]), 'files', filename)

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
    live_datetime = models.DateTimeField(editable=True, null=True, blank=True)

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
    contact = models.CharField(max_length=255, null = True, blank=True)
    list_publicly = models.IntegerField(null=True, blank=True)
    handle = models.CharField(max_length=255, null=True, db_index=True)
    preview_only_mode = models.BooleanField(default=True)
    institution_only = models.BooleanField(default=False)
    
    # Since all environments (dev, draft, prod) go against ready piazza, things will get
    # confusing if we get collisions on course ID's, so we will use a unique ID for Piazza.
    # Just use epoch seconds to make it unique.
    piazza_id = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.title
    
    def _get_prefix(self):
        return self.handle.split("--")[0]
    prefix = property(_get_prefix)

    def _get_suffix(self):
        return self.handle.split("--")[1]
    suffix = property(_get_suffix)

    def get_all_students(self):
        """
        Returns a QUERY_SET of all students
        """
        return self.student_group.user_set.all()
    
    def get_all_course_admins(self):
        """
        Returns a QUERY_SET of all staff
        """
        return (self.instructor_group.user_set.all() | self.tas_group.user_set.all())
    
    def get_all_members(self):
        """
        Returns a QUERY_SET of all course members
        """
        return (self.get_all_students() | self.get_all_course_admins())

    def create_ready_instance(self):
        ready_instance = Course(institution = self.institution,
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
            contact = self.contact,
            list_publicly = 0,
            image = self,
            mode = 'ready',
            handle = self.handle,
            institution_only = self.institution_only,
            piazza_id = int(time.mktime(time.gmtime())),
        )
        ready_instance.save()
        self.image = ready_instance
        self.save()

    def commit(self, clone_fields = None):
        if self.mode != 'draft': return;

        ready_instance = self.image
        if not clone_fields or 'institution' in clone_fields:
            ready_instance.institution = self.institution
        if not clone_fields or 'title' in clone_fields:
            ready_instance.title = self.title
        if not clone_fields or 'description' in clone_fields:
            ready_instance.description = self.description
        if not clone_fields or 'syllabus' in clone_fields:
            ready_instance.syllabus = self.syllabus
        if not clone_fields or 'term' in clone_fields:
            ready_instance.term = self.term
        if not clone_fields or 'year' in clone_fields:
            ready_instance.year = self.year
        if not clone_fields or 'calendar_start' in clone_fields:
            ready_instance.calendar_start = self.calendar_start
        if not clone_fields or 'calendar_end' in clone_fields:
            ready_instance.calendar_end = self.calendar_end

        ready_instance.save()

    def revert(self, clone_fields = None):
        if self.mode != 'draft': return;

        ready_instance = self.image
        if not clone_fields or 'institution' in clone_fields:
            self.institution = ready_instance.institution
        if not clone_fields or 'title' in clone_fields:
            self.title = ready_instance.title
        if not clone_fields or 'description' in clone_fields:
            self.description = ready_instance.description
        if not clone_fields or 'syllabus' in clone_fields:
            self.syllabus = ready_instance.syllabus
        if not clone_fields or 'term' in clone_fields:
            self.term = ready_instance.term
        if not clone_fields or 'year' in clone_fields:
            self.year = ready_instance.year
        if not clone_fields or 'calendar_start' in clone_fields:
            self.calendar_start = ready_instance.calendar_start
        if not clone_fields or 'calendar_end' in clone_fields:
            self.calendar_end = ready_instance.calendar_end

        self.save()

    class Meta:
        db_table = u'c2g_courses'

class ContentSectionManager(models.Manager):
    def getByCourse(self, course):
        return self.filter(course=course,is_deleted=0).order_by('index')

class ContentSection(TimestampMixin, Stageable, Sortable, Deletable, models.Model):
    course = models.ForeignKey(Course, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    objects = ContentSectionManager()

    def create_ready_instance(self):
        ready_instance = ContentSection(
            course=self.course.image,
            title=self.title,
            index=self.index,
            mode='ready',
            image=self,
        )
        ready_instance.save()
        self.image=ready_instance
        self.save()

    def commit(self, clone_fields = None):
        if self.mode != 'draft': return;

        ready_instance = self.image
        if not clone_fields or 'title' in clone_fields:
            ready_instance.title = self.title
        if not clone_fields or 'index' in clone_fields:
            ready_instance.index = self.index

        ready_instance.save()

    def revert(self, clone_fields = None):
        if self.mode != 'draft': return;

        ready_instance = self.image
        if not clone_fields or 'title' in clone_fields:
            self.title = ready_instance.title
        if not clone_fields or 'index' in clone_fields:
            self.index = ready_instance.index

        self.save()

    def getChildren(self):
        dict_list = []
        output_list = []

        videos = Video.objects.getBySection(section=self)
        for item in videos:
            dict_list.append({'item':item, 'index':item.index})

        problemsets = ProblemSet.objects.getBySection(section=self)
        for item in problemsets:
            dict_list.append({'item':item, 'index':item.index})

        additionalpages = AdditionalPage.objects.getBySection(section=self)
        for item in additionalpages:
            dict_list.append({'item':item, 'index':item.index})
            
        files = File.objects.getBySection(section=self)
        for item in files:
            dict_list.append({'item':item, 'index':item.index})

        sorted_dict_list = sorted(dict_list, key=lambda k: k['index'])

        for item in sorted_dict_list:
            output_list.append(item['item'])

        return output_list

    def countChildren(self):
        return len(self.getChildren)

    def getNextIndex(self):
        # We will not return len(children)+1 since this approach is not fail safe. If an index is skipped for whatever reason, we want to make sure we are still robust
        # So what if the children list is empty?
        children = self.getChildren()
        if len(children) == 0 :
            return 1
        
        if children[-1].index == None:
            return len(children)+1
        else:
            return children[-1].index+1

    def __unicode__(self):
        return self.title

    class Meta:
        db_table = u'c2g_content_sections'

class AdditionalPageManager(models.Manager):
    def getByCourseAndMenuSlug(self, course, menu_slug):
        # This method does not check live_datetime. Additional pages to display under menus have no live_datetime effect.
        return self.filter(course=course,is_deleted=0,menu_slug=menu_slug).order_by('index')

    def getSectionPagesByCourse(self, course):
        # Additional pages displayed under sections have a live_datetime effect.
        if course.mode == 'draft':
            return self.filter(course=course,is_deleted=0,menu_slug=None).order_by('section','index')
        else:
            now = datetime.now()
            return self.filter(course=course,is_deleted=0,menu_slug=None,live_datetime__lt=now).order_by('section','index')

    def getBySection(self, section):
        if section.mode == 'draft':
            return self.filter(section=section, is_deleted=0).order_by('index')
        else:
            now = datetime.now()
            return self.filter(section=section, is_deleted=0, live_datetime__lt=now).order_by('index')

class AdditionalPage(TimestampMixin, Stageable, Sortable, Deletable, models.Model):
    course = models.ForeignKey(Course, db_index=True)
    menu_slug = models.SlugField(max_length=255, null=True, blank=True)
    section = models.ForeignKey(ContentSection, null=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    objects = AdditionalPageManager()

    def create_ready_instance(self):
        image_section = None
        if self.section:
            image_section = self.section.image

        ready_instance = AdditionalPage(
            course=self.course.image,
            title=self.title,
            description=self.description,
            menu_slug=self.menu_slug,
            section = image_section,
            slug=self.slug,
            index=self.index,
            mode='ready',
            image=self,
        )
        ready_instance.save()
        self.image=ready_instance
        self.save()

    def commit(self, clone_fields = None):
        if self.mode != 'draft': return;
        if not self.image: self.create_ready_instance()

        ready_instance = self.image
        if not clone_fields or 'title' in clone_fields:
            ready_instance.title = self.title
        if not clone_fields or 'description' in clone_fields:
            ready_instance.description = self.description
        if not clone_fields or 'index' in clone_fields:
            ready_instance.index = self.index

        ready_instance.save()

    def revert(self, clone_fields = None):
        if self.mode != 'draft': return;

        ready_instance = self.image
        if not clone_fields or 'title' in clone_fields:
            self.title = ready_instance.title
        if not clone_fields or 'description' in clone_fields:
            self.description = ready_instance.description
        if not clone_fields or 'index' in clone_fields:
            self.index = ready_instance.index

        self.save()

    def is_synced(self):
        if self.title != self.image.title:
            return False
        if self.description != self.image.description:
            return False

        return True

    class Meta:
        db_table = u'c2g_additional_pages'

class FileManager(models.Manager):
    def getByCourse(self, course):
        if course.mode == 'draft':
            return self.filter(course=course,is_deleted=0).order_by('section','index')
        else:
            now = datetime.now()
            return self.filter(course=course,is_deleted=0,live_datetime__lt=now).order_by('section','index')
            
    def getBySection(self, section):
        if section.mode == 'draft':
            return self.filter(section=section, is_deleted=0).order_by('index')
        else:
            now = datetime.now()
            return self.filter(section=section, is_deleted=0, live_datetime__lt=now).order_by('index')

class File(TimestampMixin, Stageable, Sortable, Deletable, models.Model):
    course = models.ForeignKey(Course, db_index=True)
    section = models.ForeignKey(ContentSection, null=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    file = models.FileField(upload_to=get_file_path)
    handle = models.CharField(max_length=255, null=True, db_index=True)
    objects = FileManager()

    def create_ready_instance(self):
        ready_instance = File(
            course=self.course.image,
            section=self.section.image,
            title=self.title,
            file=self.file,
            image = self,
            index = self.index,
            mode = 'ready',
            handle = self.handle,
            live_datetime = self.live_datetime,
        )
        ready_instance.save()
        self.image = ready_instance
        self.save()

    def dl_link(self):
        if not self.file.storage.exists(self.file.name):
            return ""
        
        url = self.file.storage.url(self.file.name, response_headers={'response-content-disposition': 'attachment'})
        return url

    class Meta:
        db_table = u'c2g_files'

class AnnouncementManager(models.Manager):
    def getByCourse(self, course):
        return self.filter(course=course,is_deleted=0).order_by('-time_created')

class Announcement(TimestampMixin, Stageable, Sortable, Deletable, models.Model):
    owner = models.ForeignKey(User)
    course = models.ForeignKey(Course, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    objects = AnnouncementManager()

    def create_ready_instance(self):
        ready_instance = Announcement(
            course=self.course.image,
            title=self.title,
            description=self.description,
            owner = self.owner,
            mode='ready',
            image=self,
        )
        ready_instance.save()
        self.image=ready_instance
        self.save()

    def commit(self, clone_fields = None):
        if self.mode != 'draft': return;
        if not self.image: self.create_ready_instance()

        ready_instance = self.image
        if not clone_fields or 'title' in clone_fields:
            ready_instance.title = self.title
        if not clone_fields or 'description' in clone_fields:
            ready_instance.description = self.description

        ready_instance.save()

    def revert(self, clone_fields = None):
        if self.mode != 'draft': return;

        ready_instance = self.image
        if not clone_fields or 'title' in clone_fields:
            self.title = ready_instance.title
        if not clone_fields or 'description' in clone_fields:
            self.description = ready_instance.description

        self.save()

    def is_synced(self):
        if self.title != self.image.title:
            return False
        if self.description != self.image.description:
            return False

        return True

    class Meta:
        db_table = u'c2g_announcements'

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
class UserProfile(TimestampMixin, models.Model):
    user = models.OneToOneField(User, db_index=True)
    site_data = models.TextField(blank=True)
    gender = models.CharField(max_length=64, null=True)
    birth_year = models.CharField(max_length=64, null=True)
    education = models.CharField(max_length=64, null=True)
    work = models.CharField(max_length=128,null=True)

    institutions = models.ManyToManyField(Institution) #these are confirmed institutions via shib or other trusted verifier

    client_ip = models.CharField(max_length=30, null=True)
    user_agent = models.CharField(max_length=256, null=True)
    referrer = models.CharField(max_length=256, null=True)
    accept_language = models.CharField(max_length=64, null=True)

    client_ip_first = models.CharField(max_length=30, null=True)
    user_agent_first = models.CharField(max_length=256, null=True)
    referrer_first = models.CharField(max_length=256, null=True)
    accept_language_first = models.CharField(max_length=64, null=True)
    
    def __unicode__(self):
        return self.user.username

    class Meta:
        db_table = u'c2g_user_profiles'

def create_user_profile(sender, instance, created, raw, **kwargs):
    if created and not raw:  #create means that a new DB entry is created, raw is set when fixtures are being loaded
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

class VideoManager(models.Manager):
    def getByCourse(self, course):
        if course.mode == 'draft':
            return self.filter(course=course,is_deleted=0).order_by('section','index')
        else:
            now = datetime.now()
            return self.filter(course=course,is_deleted=0,live_datetime__lt=now).order_by('section','index')

    def getBySection(self, section):
        if section.mode == 'draft':
            return self.filter(section=section, is_deleted=0).order_by('index')
        else:
            now = datetime.now()
            return self.filter(section=section, is_deleted=0, live_datetime__lt=now).order_by('index')

class Video(TimestampMixin, Stageable, Sortable, Deletable, models.Model):
    course = models.ForeignKey(Course, db_index=True)
    section = models.ForeignKey(ContentSection, null=True, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=30, default="youtube")
    url = models.CharField("Youtube Video ID", max_length=255, null=True, blank=True)
    duration = models.IntegerField(null=True)
    slug = models.SlugField("URL Identifier", max_length=255, null=True)
    file = models.FileField(upload_to=get_file_path)
    handle = models.CharField(max_length=255, null=True, db_index=True)
#    kelvinator = models.IntegerField("K-Threshold", default=15)
    objects = VideoManager()

    def create_ready_instance(self):
        ready_instance = Video(
            course=self.course.image,
            section=self.section.image,
            title=self.title,
            description=self.description,
            type=self.type,
            url=self.url,
            duration=self.duration,
            slug=self.slug,
            file=self.file,
            image = self,
            index = self.index,
            mode = 'ready',
            handle = self.handle,
            live_datetime = self.live_datetime,
        )
        ready_instance.save()
        self.image = ready_instance
        self.save()

    def exercises_changed(self):
        ready_instance = self.image
        draft_videoToExs = VideoToExercise.objects.getByVideo(self)
        ready_videoToExs = VideoToExercise.objects.getByVideo(ready_instance)
        if len(draft_videoToExs) != len(ready_videoToExs):
            return True
        for draft_videoToEx in draft_videoToExs:
            if not draft_videoToEx.image:
                return True
        return False

    def commit(self, clone_fields = None):
        if self.mode != 'draft': return;
        if not self.image: self.create_ready_instance()

        ready_instance = self.image
        if not clone_fields or 'title' in clone_fields:
            ready_instance.title = self.title
        if not clone_fields or 'section' in clone_fields:
            ready_instance.section = self.section.image
        if not clone_fields or 'description' in clone_fields:
            ready_instance.description = self.description
        if not clone_fields or 'slug' in clone_fields:
            ready_instance.slug = self.slug
        if not clone_fields or 'file' in clone_fields:
            ready_instance.file = self.file
        if not clone_fields or 'url' in clone_fields:
            ready_instance.url = self.url
        if not clone_fields or 'live_datetime' in clone_fields:
            ready_instance.live_datetime = self.live_datetime

        ready_instance.save()

        if self.exercises_changed() == True:
            draft_videoToExs =  VideoToExercise.objects.getByVideo(self)
            ready_videoToExs = VideoToExercise.objects.getByVideo(ready_instance)
            #Delete all previous relationships
            for ready_videoToEx in ready_videoToExs:
                ready_videoToEx.delete()
                ready_videoToEx.save()

        #Create brand new copies of draft relationships
            for draft_videoToEx in draft_videoToExs:
                ready_videoToEx = VideoToExercise(video = ready_instance,
                                                    exercise = draft_videoToEx.exercise,
                                                    video_time = draft_videoToEx.video_time,
                                                    is_deleted = 0,
                                                    mode = 'ready',
                                                    image = draft_videoToEx)
                ready_videoToEx.save()
                draft_videoToEx.image = ready_videoToEx
                draft_videoToEx.save()

        else:
            draft_videoToExs = VideoToExercise.objects.getByVideo(self)
            for draft_videoToEx in draft_videoToExs:
                draft_videoToEx.image.video_time = draft_videoToEx.video_time
                draft_videoToEx.image.save()

    def revert(self, clone_fields = None):
        if self.mode != 'draft': return;

        ready_instance = self.image
        if not clone_fields or 'title' in clone_fields:
            self.title = ready_instance.title
        if not clone_fields or 'section' in clone_fields:
            self.section = ready_instance.section.image
        if not clone_fields or 'description' in clone_fields:
            self.description = ready_instance.description
        if not clone_fields or 'slug' in clone_fields:
            self.slug = ready_instance.slug
        if not clone_fields or 'file' in clone_fields:
            self.file = ready_instance.file
        if not clone_fields or 'url' in clone_fields:
            self.url = ready_instance.url
        if not clone_fields or 'live_datetime' in clone_fields:
            self.live_datetime = ready_instance.live_datetime

        self.save()

        if self.exercises_changed() == True:
            draft_videoToExs = VideoToExercise.objects.getByVideo(self)
            ready_videoToExs = VideoToExercise.objects.getByVideo(ready_instance)
            #Delete all previous relationships
            for draft_videoToEx in draft_videoToExs:
                draft_videoToEx.delete()
                draft_videoToEx.save()

        #Create brand new copies of draft relationships
            for ready_videoToEx in ready_videoToExs:
                draft_videoToEx = VideoToExercise(video = self,
                                                    exercise = ready_videoToEx.exercise,
                                                    video_time = ready_videoToEx.video_time,
                                                    is_deleted = 0,
                                                    mode = 'draft',
                                                    image = ready_videoToEx)
                draft_videoToEx.save()
                ready_videoToEx.image = draft_videoToEx
                ready_videoToEx.save()

        else:
            ready_videoToExs = VideoToExercise.objects.getByVideo(ready_instance)
            for ready_videoToEx in ready_videoToExs:
                ready_videoToEx.image.video_time = ready_videoToEx.video_time
                ready_videoToEx.image.save()

    def is_synced(self):
        prod_instance = self.image
        if self.exercises_changed() == True:
            return False
        if self.title != prod_instance.title:
            return False
        if self.section != prod_instance.section.image:
            return False
        if self.description != prod_instance.description:
            return False
        if self.slug != prod_instance.slug:
            return False
        if self.file != prod_instance.file:
            return False
        if self.url != prod_instance.url:
            return False
        if self.live_datetime != prod_instance.live_datetime:
            return False
        draft_videoToExs = VideoToExercise.objects.getByVideo(self)
        for draft_videoToEx in draft_videoToExs:
            if draft_videoToEx.video_time != draft_videoToEx.image.video_time:
                return False
        return True

    def dl_link(self):
        if not self.file.storage.exists(self.file.name):
            return ""
        return self.file.storage.url(self.file.name, response_headers={'response-content-disposition': 'attachment'})

    def ret_url(self):
        return "https://www.youtube.com/analytics#fi=v-" + self.url + ",r=retention"

    def runtime(self):
        if not self.duration:
            return "Runtime not yet available"
        m, s = divmod(self.duration, 60)
        h, m = divmod(m, 60)
        if h:
            return "%d:%02d:%02d" % (h, m, s)
        else:
            return "%d:%02d" % (m, s)

    def validate_unique(self, exclude=None):
        errors = {}

        try:
            super(Video, self).validate_unique(exclude=exclude)
        except ValidationError, e:
            errors.update(e.message_dict)

        # Special slug uniqueness validation for course
        slug_videos = Video.objects.filter(course=self.course,is_deleted=0,slug=self.slug)

        # Exclude the current object from the query if we are editing an
        # instance (as opposed to creating a new one)
        if not self._state.adding and self.pk is not None:
            slug_videos = slug_videos.exclude(pk=self.pk)

        if slug_videos.exists():
            errors.setdefault("slug", []).append("Video with this URL identifier already exists.")

        if errors:
            raise ValidationError(errors)

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

class ProblemSetManager(models.Manager):
    def getByCourse(self, course):
        if course.mode == 'draft':
            return self.filter(course=course,is_deleted=0).order_by('section','index')
        else:
            now = datetime.now()
            return self.filter(course=course,is_deleted=0,live_datetime__lt=now).order_by('section','index')

    def getBySection(self, section):
        if section.mode == 'draft':
            return self.filter(section=section, is_deleted=0).order_by('index')
        else:
            now = datetime.now()
            return self.filter(section=section, is_deleted=0, live_datetime__lt=now).order_by('index')

class ProblemSet(TimestampMixin, Stageable, Sortable, Deletable, models.Model):
    course = models.ForeignKey(Course)
    section = models.ForeignKey(ContentSection, db_index=True)
    slug = models.SlugField("URL Identifier")
    title = models.CharField(max_length=255,)
    description = models.TextField(blank=True)
    path = models.CharField(max_length=255)
    due_date = models.DateTimeField(null=True)
    grace_period = models.DateTimeField()
    partial_credit_deadline = models.DateTimeField()
    assessment_type = models.CharField(max_length=255)
    late_penalty = models.IntegerField()
    submissions_permitted = models.IntegerField()
    resubmission_penalty = models.IntegerField()
    randomize = models.BooleanField()
    objects = ProblemSetManager()

    def create_ready_instance(self):
        ready_instance = ProblemSet(
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
            assessment_type=self.assessment_type,
            late_penalty=self.late_penalty,
            submissions_permitted=self.submissions_permitted,
            resubmission_penalty=self.resubmission_penalty,
            index=self.index,
            image = self,
            mode = 'ready',
        )
        ready_instance.save()
        self.image = ready_instance
        self.save()
        return ready_instance

    def exercises_changed(self):
        ready_instance = self.image
        draft_psetToExs = ProblemSetToExercise.objects.getByProblemset(self)
        ready_psetToExs = ProblemSetToExercise.objects.getByProblemset(ready_instance)
        if len(draft_psetToExs) != len(ready_psetToExs):
            return True
        for draft_psetToEx in draft_psetToExs:
            if not draft_psetToEx.image:
                return True
        return False

    def commit(self, clone_fields = None):
        if self.mode != 'draft': return;
        if not self.image: self.create_ready_instance()

        ready_instance = self.image
        if not clone_fields or 'section' in clone_fields:
            ready_instance.section = self.section.image
        if not clone_fields or 'title' in clone_fields:
            ready_instance.title = self.title
        if not clone_fields or 'description' in clone_fields:
            ready_instance.description = self.description
        if not clone_fields or 'path' in clone_fields:
            ready_instance.path = self.path
        if not clone_fields or 'slug' in clone_fields:
            ready_instance.slug = self.slug
        if not clone_fields or 'index' in clone_fields:
            ready_instance.index = self.index
        if not clone_fields or 'live_datetime' in clone_fields:
            ready_instance.live_datetime = self.live_datetime
        if not clone_fields or 'due_date' in clone_fields:
            ready_instance.due_date = self.due_date
        if not clone_fields or 'grace_period' in clone_fields:
            ready_instance.grace_period = self.grace_period
        if not clone_fields or 'partial_credit_deadline' in clone_fields:
            ready_instance.partial_credit_deadline = self.partial_credit_deadline
        if not clone_fields or 'assessment_type' in clone_fields:
            ready_instance.assessment_type = self.assessment_type
        if not clone_fields or 'late_penalty' in clone_fields:
            ready_instance.late_penalty = self.late_penalty
        if not clone_fields or 'submissions_permitted' in clone_fields:
            ready_instance.submissions_permitted = self.submissions_permitted
        if not clone_fields or 'resubmission_penalty' in clone_fields:
            ready_instance.resubmission_penalty = self.resubmission_penalty

        ready_instance.save()

        if self.exercises_changed() == True:
            draft_psetToExs =  ProblemSetToExercise.objects.getByProblemset(self)
            ready_psetToExs = ProblemSetToExercise.objects.getByProblemset(ready_instance)
            #Delete all previous relationships
            for ready_psetToEx in ready_psetToExs:
                ready_psetToEx.delete()
                ready_psetToEx.save()

        #Create brand new copies of draft relationships
            for draft_psetToEx in draft_psetToExs:
                ready_psetToEx = ProblemSetToExercise(problemSet = ready_instance,
                                                    exercise = draft_psetToEx.exercise,
                                                    number = draft_psetToEx.number,
                                                    is_deleted = 0,
                                                    mode = 'ready',
                                                    image = draft_psetToEx)
                ready_psetToEx.save()
                draft_psetToEx.image = ready_psetToEx
                draft_psetToEx.save()

        else:
            draft_psetToExs = ProblemSetToExercise.objects.getByProblemset(self)
            for draft_psetToEx in draft_psetToExs:
                draft_psetToEx.image.number = draft_psetToEx.number
                draft_psetToEx.image.save()

    def revert(self, clone_fields = None):
        if self.mode != 'draft': return;

        ready_instance = self.image
        if not clone_fields or 'section' in clone_fields:
            self.section = ready_instance.section.image
        if not clone_fields or 'title' in clone_fields:
            self.title = ready_instance.title
        if not clone_fields or 'description' in clone_fields:
            self.description = ready_instance.description
        if not clone_fields or 'path' in clone_fields:
            self.path = ready_instance.path
        if not clone_fields or 'slug' in clone_fields:
            self.slug = ready_instance.slug
        if not clone_fields or 'index' in clone_fields:
            self.index = ready_instance.index
        if not clone_fields or 'live_datetime' in clone_fields:
            self.live_datetime = ready_instance.live_datetime
        if not clone_fields or 'due_date' in clone_fields:
            self.due_date = ready_instance.due_date
        if not clone_fields or 'grace_period' in clone_fields:
            self.grace_period = ready_instance.grace_period
        if not clone_fields or 'partial_credit_deadline' in clone_fields:
            self.partial_credit_deadline = ready_instance.partial_credit_deadline
        if not clone_fields or 'assessment_type' in clone_fields:
            self.assessment_type = ready_instance.assessment_type
        if not clone_fields or 'late_penalty' in clone_fields:
            self.late_penalty = ready_instance.late_penalty
        if not clone_fields or 'submissions_permitted' in clone_fields:
            self.submissions_permitted = ready_instance.submissions_permitted
        if not clone_fields or 'resubmission_penalty' in clone_fields:
            self.resubmission_penalty = ready_instance.resubmission_penalty

        self.save()

        if self.exercises_changed() == True:
            draft_psetToExs = ProblemSetToExercise.objects.getByProblemset(self)
            ready_psetToExs = ProblemSetToExercise.objects.getByProblemset(ready_instance)
            #Delete all previous relationships
            for draft_psetToEx in draft_psetToExs:
                draft_psetToEx.delete()
                draft_psetToEx.save()

        #Create brand new copies of draft relationships
            for ready_psetToEx in ready_psetToExs:
                draft_psetToEx = ProblemSetToExercise(problemSet = self,
                                                    exercise = ready_psetToEx.exercise,
                                                    number = ready_psetToEx.number,
                                                    is_deleted = 0,
                                                    mode = 'draft',
                                                    image = ready_psetToEx)
                draft_psetToEx.save()
                ready_psetToEx.image = draft_psetToEx
                ready_psetToEx.save()

        else:
            ready_psetToExs = ProblemSetToExercise.objects.getByProblemset(ready_instance)
            for ready_psetToEx in ready_psetToExs:
                ready_psetToEx.image.number = ready_psetToEx.number
                ready_psetToEx.image.save()


    def is_synced(self):
        image = self.image
        if self.exercises_changed() == True:
            return False
        if self.section != image.section.image:
            return False
        if self.title != image.title:
            return False
        if self.description != image.description:
            return False
        if self.path != image.path:
            return False
        if self.slug != image.slug:
            return False
        if self.index != image.index:
            return False
        if self.live_datetime != image.live_datetime:
            return False
        if self.due_date != image.due_date:
            return False
        if self.grace_period != image.grace_period:
            return False
        if self.partial_credit_deadline != image.partial_credit_deadline:
            return False
        if self.assessment_type != image.assessment_type:
            return False
        if self.late_penalty != image.late_penalty:
            return False
        if self.submissions_permitted != image.submissions_permitted:
            return False
        if self.resubmission_penalty != image.resubmission_penalty:
            return False
        draft_psetToExs = ProblemSetToExercise.objects.getByProblemset(self)
        for draft_psetToEx in draft_psetToExs:
            if draft_psetToEx.number != draft_psetToEx.image.number:
                return False
        return True

    def validate_unique(self, exclude=None):
        errors = {}

        try:
            super(ProblemSet, self).validate_unique(exclude=exclude)
        except ValidationError, e:
            errors.update(e.message_dict)

        # Special slug uniqueness validation for course
        slug_psets = ProblemSet.objects.filter(course=self.course,is_deleted=0,slug=self.slug)

        # Exclude the current object from the query if we are editing an
        # instance (as opposed to creating a new one)
        if not self._state.adding and self.pk is not None:
            slug_psets = slug_psets.exclude(pk=self.pk)

        if slug_psets.exists():
            errors.setdefault("slug", []).append("Problem set with this URL identifier already exists.")

        if errors:
            raise ValidationError(errors)

    def get_progress(self, student):
        submissions_permitted = self.submissions_permitted
        if submissions_permitted == 0:
            submissions_permitted = sys.maxsize
        pset_activities = ProblemActivity.objects.select_related('problemSet', 'exercise').filter(problemset_to_exercise__problemSet=self, student=student)
        psetToExs = ProblemSetToExercise.objects.getByProblemset(self)
        questions_completed = 0
        for psetToEx in psetToExs:
            exercise_activities = pset_activities.filter(problemset_to_exercise=psetToEx).order_by('time_created')
            for exercise_activity in exercise_activities:
                if exercise_activity.attempt_number == submissions_permitted:
                    questions_completed += 1
                    break
                elif exercise_activity.complete:
                    questions_completed += 1
                    break
        return questions_completed

    def get_score(self, student):
        resubmission_penalty = self.resubmission_penalty
        submissions_permitted = self.submissions_permitted
        if submissions_permitted == 0:
            submissions_permitted = sys.maxsize
        pset_activities = ProblemActivity.objects.select_related('problemSet', 'exercise').filter(problemset_to_exercise__problemSet=self, student=student)
        psetToExs = ProblemSetToExercise.objects.getByProblemset(self)
        total_score = 0.0
        for psetToEx in psetToExs:
            exercise_activities = pset_activities.filter(problemset_to_exercise=psetToEx).order_by('time_created')
            exercise_percent = 100
            for exercise_activity in exercise_activities:
                if exercise_activity.attempt_number > submissions_permitted:
                    break
                elif exercise_activity.complete:
                    total_score += exercise_percent/100.0
                    break
                else:
                    exercise_percent -= resubmission_penalty
        return total_score

    class Meta:
        db_table = u'c2g_problem_sets'

class Exercise(TimestampMixin, Deletable, models.Model):
    problemSet = models.ManyToManyField(ProblemSet, through='ProblemSetToExercise')
    video = models.ManyToManyField(Video, through='VideoToExercise')
    fileName = models.CharField(max_length=255)
    file = models.FileField(upload_to=get_file_path, null=True)
    handle = models.CharField(max_length=255, null=True, db_index=True)
    def __unicode__(self):
        return self.fileName
    class Meta:
        db_table = u'c2g_exercises'


class GetPsetToExsByProblemset (models.Manager):
    def getByProblemset(self, problemSet):
        return self.filter(problemSet=problemSet,is_deleted=0).order_by('number')


class ProblemSetToExercise( Deletable, models.Model):
    problemSet = models.ForeignKey(ProblemSet)
    exercise = models.ForeignKey(Exercise)
    number = models.IntegerField(null=True, blank=True)
    image = models.ForeignKey('self',null=True, blank=True)
    mode = models.TextField(blank=True)
    objects = GetPsetToExsByProblemset()
    def __unicode__(self):
        return self.problemSet.title + "-" + self.exercise.fileName
    class Meta:
        db_table = u'c2g_problemset_to_exercise'


class GetVideoToExerciseByVideo(models.Manager):
    def getByVideo(self, video):
        return self.filter(video=video, is_deleted=0).order_by('video_time')

class VideoToExercise(Deletable, models.Model):
    video = models.ForeignKey(Video)
    exercise = models.ForeignKey(Exercise)
    video_time = models.IntegerField()
    image = models.ForeignKey('self',null=True, blank=True)
    mode = models.TextField(blank=True)
    objects = GetVideoToExerciseByVideo()
    def __unicode__(self):
        return self.video.title + "-" + self.exercise.fileName
    class Meta:
        db_table = u'c2g_video_to_exercise'


class ProblemActivity(TimestampMixin, models.Model):
     student = models.ForeignKey(User)
     video_to_exercise = models.ForeignKey(VideoToExercise, null=True)
     problemset_to_exercise = models.ForeignKey(ProblemSetToExercise, null=True)
     problem_identifier = models.CharField(max_length=255, blank=True)
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
     user_selection_val = models.CharField(max_length=1024, null=True, blank=True)
     user_choices = models.CharField(max_length=1024, null=True, blank=True)
     def __unicode__(self):
            return self.student.username + " " + str(self.time_created)
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

#Should probably slate this EditProfileForm for moving to a different file
class EditProfileForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.CharField(max_length=30)

class Email(TimestampMixin, models.Model):
    sender = models.ForeignKey(User)
    hash = models.CharField(max_length=128, db_index=True)
    subject = models.CharField(max_length=128, blank=True)
    html_message = models.TextField(null=True, blank=True)    
    class Meta:
        abstract = True

class CourseEmail(Email, models.Model):
    TO_OPTIONS =(('myself','myself'),
                 ('staff','staff'),
                 ('students','students'),
                 ('all','all'),
                 )
    course = models.ForeignKey(Course)
    to = models.CharField(max_length=64, choices=TO_OPTIONS, default='myself')

    
    def __unicode__(self):
        return self.subject
    class Meta:
        db_table = u'c2g_course_emails'

class EmailAddr(models.Model):
    name = models.CharField(max_length=128, null=True, blank=True)
    addr = models.EmailField(max_length=128)
    def __unicode__(self):
       return self.addr

class MailingList(models.Model):
    name = models.CharField(max_length=128, blank=True)
    members = models.ManyToManyField(EmailAddr)
    def __unicode__(self):
        return self.name

class ListEmail(Email, models.Model):
    from_name = models.CharField(max_length=128, blank=True)
    to_list = models.ForeignKey(MailingList)
    def __unicode__(self):
        return self.subject
