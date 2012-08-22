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

# For file system upload
from django.core.files.storage import FileSystemStorage

def get_file_path(instance, filename):
    parts = str(instance.handle).split("#$!")
    if isinstance(instance, Exercise):
        return os.path.join(str(parts[0]), str(parts[1]), 'exercises', filename)
    if isinstance(instance, Video):
        return os.path.join(str(parts[0]), str(parts[1]), 'videos', str(instance.id), filename)


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

class ContentSectionManager(models.Manager):
    def getByCourse(self, course):
        return self.filter(course=course,is_deleted=0).order_by('index')

class ContentSection(TimestampMixin, Stageable, Sortable, Deletable, models.Model):
    course = models.ForeignKey(Course, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    objects = ContentSectionManager()

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

        sorted_dict_list = sorted(dict_list, key=lambda k: k['index'])

        for item in sorted_dict_list:
            output_list.append(item['item'])

        return output_list

    def countChildren(self):
        return len(self.getChildren)

    def getNextIndex(self):
        # We will not return len(children)+1 since this approach is not fail safe. If an index is skipped for whatever reason, we want to make sure we are still robust
        children = self.getChildren()
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
        if course.mode == 'staging':
            return self.filter(course=course,is_deleted=0,menu_slug=None).order_by('section','index')
        else:
            now = datetime.now()
            return self.filter(course=course,is_deleted=0,menu_slug=None,live_datetime__lt=now).order_by('section','index')

    def getBySection(self, section):
        if section.mode == 'staging':
            return self.filter(section=section, is_deleted=0).order_by('index')
        else:
            now = datetime.now()
            return self.filter(section=section, is_deleted=0, live_datetime__lt=now).order_by('index')

class AdditionalPage(TimestampMixin, Stageable, Sortable, Deletable, models.Model):
    course = models.ForeignKey(Course, db_index=True)
    menu_slug = models.CharField(max_length=255, null=True, blank=True)
    section = models.ForeignKey(ContentSection, null=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    slug = models.CharField(max_length=255, null=True, blank=True)
    objects = AdditionalPageManager()

    def create_production_instance(self):
        image_section = None
        if self.section:
            image_section = self.section.image

        production_instance = AdditionalPage(
            course=self.course.image,
            title=self.title,
            description=self.description,
            menu_slug=self.menu_slug,
            section = image_section,
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
        if not self.image: self.create_production_instance()

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

    def is_synced(self):
        if self.title != self.image.title:
            return False
        if self.description != self.image.description:
            return False

        return True

    class Meta:
        db_table = u'c2g_additional_pages'


class AnnouncementManager(models.Manager):
    def getByCourse(self, course):
        return self.filter(course=course,is_deleted=0).order_by('-time_created')

class Announcement(TimestampMixin, Stageable, Sortable, Deletable, models.Model):
    owner = models.ForeignKey(User)
    course = models.ForeignKey(Course, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    objects = AnnouncementManager()

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
        if not self.image: self.create_production_instance()

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
class UserProfile(models.Model):
    user = models.OneToOneField(User, db_index=True)
    site_data = models.TextField(blank=True)
    class Meta:
        db_table = u'c2g_user_profiles'

def create_user_profile(sender, instance, created, raw, **kwargs):
    if created and not raw:  #create means that a new DB entry is created, raw is set when fixtures are being loaded
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

class VideoManager(models.Manager):
    def getByCourse(self, course):
        if course.mode == 'staging':
            return self.filter(course=course,is_deleted=0).order_by('section','index')
        else:
            now = datetime.now()
            return self.filter(course=course,is_deleted=0,live_datetime__lt=now).order_by('section','index')

    def getBySection(self, section):
        if section.mode == 'staging':
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
    url = models.CharField(max_length=255, null=True)
    duration = models.IntegerField(null=True)
    slug = models.SlugField("URL Identifier", max_length=255, null=True)
    file = models.FileField(upload_to=get_file_path)
    handle = models.CharField(max_length=255, null=True, db_index=True)
#    kelvinator = models.IntegerField("K-Threshold", default=15)
    objects = VideoManager()

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
            file=self.file,
            image = self,
            mode = 'production',
            handle = self.handle,
            live_datetime = self.live_datetime,
        )
        production_instance.save()
        self.image = production_instance
        self.save()

    def commit(self, clone_fields = None):
        if self.mode != 'staging': return;
        if not self.image: self.create_production_instance()

        production_instance = self.image
        if not clone_fields or 'title' in clone_fields:
            production_instance.title = self.title
        if not clone_fields or 'section' in clone_fields:
            production_instance.section = self.section.image
        if not clone_fields or 'description' in clone_fields:
            production_instance.description = self.description
        if not clone_fields or 'slug' in clone_fields:
            production_instance.slug = self.slug
        if not clone_fields or 'file' in clone_fields:
            production_instance.file = self.file
        if not clone_fields or 'live_datetime' in clone_fields:
            production_instance.live_datetime = self.live_datetime

        production_instance.save()

    def revert(self, clone_fields = None):
        if self.mode != 'staging': return;

        production_instance = self.image
        if not clone_fields or 'title' in clone_fields:
            self.title = production_instance.title
        if not clone_fields or 'section' in clone_fields:
            self.section = production_instance.section.image
        if not clone_fields or 'description' in clone_fields:
            self.description = production_instance.description
        if not clone_fields or 'slug' in clone_fields:
            self.slug = production_instance.slug
        if not clone_fields or 'file' in clone_fields:
            self.file = production_instance.file
        if not clone_fields or 'live_datetime' in clone_fields:
            self.live_datetime = production_instance.live_datetime

        self.save()

    def save(self, *args, **kwargs):
        if not self.duration:
            if self.type == "youtube" and self.url:
                yt_service = gdata.youtube.service.YouTubeService()
                #entry = yt_service.GetYouTubeVideoEntry(video_id=self.url)
                #self.duration = entry.media.duration.seconds
        super(Video, self).save(*args, **kwargs)

    def is_synced(self):
        prod_instance = self.image
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
        if self.live_datetime != prod_instance.live_datetime:
            return False

        return True

    def dl_link(self):
        return self.file.storage.url(self.file.name, response_headers={'response-content-disposition': 'attachment'})

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
        if course.mode == 'staging':
            return self.filter(course=course,is_deleted=0).order_by('section','index')
        else:
            now = datetime.now()
            return self.filter(course=course,is_deleted=0,live_datetime__lt=now).order_by('section','index')

    def getBySection(self, section):
        if section.mode == 'staging':
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
            assessment_type=self.assessment_type,
            late_penalty=self.late_penalty,
            submissions_permitted=self.submissions_permitted,
            resubmission_penalty=self.resubmission_penalty,
            index=self.index,
            image = self,
            mode = 'production',
        )
        production_instance.save()
        self.image = production_instance
        self.save()
        return production_instance

    def exercises_changed(self):
        production_instance = self.image
        staging_psetToExs = ProblemSetToExercise.objects.getByProblemset(self)
        production_psetToExs = ProblemSetToExercise.objects.getByProblemset(production_instance)
        if len(staging_psetToExs) != len(production_psetToExs):
            return True
        for staging_psetToEx in staging_psetToExs:
            if not staging_psetToEx.image:
                return True
        return False

    def commit(self, clone_fields = None):
        if self.mode != 'staging': return;
        if not self.image: self.create_production_instance()

        production_instance = self.image
        if not clone_fields or 'section' in clone_fields:
            production_instance.section = self.section.image
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
        if not clone_fields or 'live_datetime' in clone_fields:
            production_instance.live_datetime = self.live_datetime
        if not clone_fields or 'due_date' in clone_fields:
            production_instance.due_date = self.due_date
        if not clone_fields or 'grace_period' in clone_fields:
            production_instance.grace_period = self.grace_period
        if not clone_fields or 'partial_credit_deadline' in clone_fields:
            production_instance.partial_credit_deadline = self.partial_credit_deadline
        if not clone_fields or 'assessment_type' in clone_fields:
            production_instance.assessment_type = self.assessment_type
        if not clone_fields or 'late_penalty' in clone_fields:
            production_instance.late_penalty = self.late_penalty
        if not clone_fields or 'submissions_permitted' in clone_fields:
            production_instance.submissions_permitted = self.submissions_permitted
        if not clone_fields or 'resubmission_penalty' in clone_fields:
            production_instance.resubmission_penalty = self.resubmission_penalty

        production_instance.save()

        if self.exercises_changed() == True:
            staging_psetToExs =  ProblemSetToExercise.objects.getByProblemset(self)
            production_psetToExs = ProblemSetToExercise.objects.getByProblemset(production_instance)
            #Delete all previous relationships
            for production_psetToEx in production_psetToExs:
                production_psetToEx.delete()
                production_psetToEx.save()

        #Create brand new copies of staging relationships
            for staging_psetToEx in staging_psetToExs:
                production_psetToEx = ProblemSetToExercise(problemSet = production_instance,
                                                    exercise = staging_psetToEx.exercise,
                                                    number = staging_psetToEx.number,
                                                    is_deleted = 0,
                                                    mode = 'production',
                                                    image = staging_psetToEx)
                production_psetToEx.save()
                staging_psetToEx.image = production_psetToEx
                staging_psetToEx.save()

        else:
            staging_psetToExs = ProblemSetToExercise.objects.getByProblemset(self)
            for staging_psetToEx in staging_psetToExs:
                staging_psetToEx.image.number = staging_psetToEx.number
                staging_psetToEx.image.save()

    def revert(self, clone_fields = None):
        if self.mode != 'staging': return;

        production_instance = self.image
        if not clone_fields or 'section' in clone_fields:
            self.section = production_instance.section.image
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
        if not clone_fields or 'live_datetime' in clone_fields:
            self.live_datetime = production_instance.live_datetime
        if not clone_fields or 'due_date' in clone_fields:
            self.due_date = production_instance.due_date
        if not clone_fields or 'grace_period' in clone_fields:
            self.grace_period = production_instance.grace_period
        if not clone_fields or 'partial_credit_deadline' in clone_fields:
            self.partial_credit_deadline = production_instance.partial_credit_deadline
        if not clone_fields or 'assessment_type' in clone_fields:
            self.assessment_type = production_instance.assessment_type
        if not clone_fields or 'late_penalty' in clone_fields:
            self.late_penalty = production_instance.late_penalty
        if not clone_fields or 'submissions_permitted' in clone_fields:
            self.submissions_permitted = production_instance.submissions_permitted
        if not clone_fields or 'resubmission_penalty' in clone_fields:
            self.resubmission_penalty = production_instance.resubmission_penalty

        self.save()

        if self.exercises_changed() == True:
            staging_psetToExs = ProblemSetToExercise.objects.getByProblemset(self)
            production_psetToExs = ProblemSetToExercise.objects.getByProblemset(production_instance)
            #Delete all previous relationships
            for staging_psetToEx in staging_psetToExs:
                staging_psetToEx.delete()
                staging_psetToEx.save()

        #Create brand new copies of staging relationships
            for production_psetToEx in production_psetToExs:
                staging_psetToEx = ProblemSetToExercise(problemSet = self,
                                                    exercise = production_psetToEx.exercise,
                                                    number = production_psetToEx.number,
                                                    is_deleted = 0,
                                                    mode = 'staging',
                                                    image = production_psetToEx)
                staging_psetToEx.save()
                production_psetToEx.image = staging_psetToEx
                production_psetToEx.save()

        else:
            production_psetToExs = ProblemSetToExercise.objects.getByProblemset(production_instance)
            for production_psetToEx in production_psetToExs:
                production_psetToEx.image.number = production_psetToEx.number
                production_psetToEx.image.save()


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
        staging_psetToExs = ProblemSetToExercise.objects.getByProblemset(self)
        for staging_psetToEx in staging_psetToExs:
            if staging_psetToEx.number != staging_psetToEx.image.number:
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



    def __unicode__(self):
        return self.title
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


class GetPsetToExsByProblemset(models.Manager):
    def getByProblemset(self, problemSet):
        return self.filter(problemSet=problemSet,is_deleted=0).order_by('number')


class ProblemSetToExercise(Deletable, models.Model):
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


class VideoToExercise(models.Model):
    video = models.ForeignKey(Video)
    exercise = models.ForeignKey(Exercise)
    number = models.IntegerField(null=True, blank=True)
    is_deleted = models.BooleanField()
    video_time = models.IntegerField(null=True, blank=True)
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

class EditProfileForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.CharField(max_length=30)
