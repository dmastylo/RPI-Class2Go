from datetime import datetime, timedelta
from hashlib import md5
import logging
import os
import re
import sys
import time
from xml.dom.minidom import parseString

from django import forms
from django.contrib.auth.models import Group, User
from django.core.cache import get_cache
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import models
from django.db.models import Max
from django.db.models.signals import post_save
from django.utils import encoding

from c2g.util import is_storage_local, get_site_url
from kelvinator.tasks import sizes as video_resize_options 

logger = logging.getLogger(__name__)

RE_S3_PATH_FILENAME_SPLIT = re.compile('(?P<path>.+)\/(?P<filename>.*)$')


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
    image = models.ForeignKey('self', null=True, blank=True, related_name="+")  #Adding blank = True to allow these to be created in admin interface
    live_datetime = models.DateTimeField(editable=True, null=True, blank=True)
    
    def is_live(self):
        return self.live_datetime and (self.live_datetime < datetime.now())
        
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

        # Delete ContentGroup relationships when items are deleted
        # There may be exactly 0 or 1 ContentGroup entry for a given object
        contentgroup_entries = ()
        if getattr(self, 'contentgroup_set', None):
            contentgroup_entries = self.contentgroup_set.all()
        if len(contentgroup_entries) == 1:
            contentgroup_entries[0].delete()
        elif len(contentgroup_entries) > 1:
            # To allow multiple ContentGroup relationships, we can iterate
            # here, but other changes will have to be made elsewhere...
            raise ValueError, "Deletion of %s, which has multiple ContentGroup entries. Multiple entries not allowed." % (str(self))

    class Meta:
       abstract = True

class Institution(TimestampMixin, models.Model):
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
    share_to = models.ManyToManyField("self",symmetrical=False,related_name='share_from',null=True, blank=True)
    short_description = models.TextField(blank=True)
    prerequisites = models.TextField(blank=True)
    accompanying_materials = models.TextField(blank=True)
    outcomes = models.TextField(blank=True)
    faq = models.TextField(blank=True)
    logo = models.FileField(upload_to=get_file_path,null=True)
 
    
    # Since all environments (dev, draft, prod) go against ready piazza, things will get
    # confusing if we get collisions on course ID's, so we will use a unique ID for Piazza.
    # Just use epoch seconds to make it unique.
    piazza_id = models.IntegerField(null=True, blank=True)

    def logo_dl_link(self):

        if self.logo.name is None or not self.logo.storage.exists(self.logo.name):
            return ""
        
        url = self.logo.storage.url(self.logo.name)
        return url


    def __unicode__(self):
        if self.title:
            return self.title + " | Mode: " + self.mode
        else:
            return "No Title" + " | Mode: " + self.mode
    
    def _get_prefix(self):
        return self.handle.split("--")[0]
    prefix = property(_get_prefix)

    def _get_suffix(self):
        return self.handle.split("--")[1]
    suffix = property(_get_suffix)

    def has_exams(self):
        if self.mode == 'draft':
            return Exam.objects.filter(course=self, is_deleted=0, exam_type="exam").exists()
        else:
            now = datetime.now()
            return Exam.objects.filter(course=self, is_deleted=0, exam_type="exam", live_datetime__lt=now).exists()

    def has_surveys(self):
        if self.mode == 'draft':
            return Exam.objects.filter(course=self, is_deleted=0, exam_type="survey").exists()
        else:
            now = datetime.now()
            return Exam.objects.filter(course=self, is_deleted=0, exam_type="survey", live_datetime__lt=now).exists()
        
    def has_interactive_exercises(self):
        if self.mode == 'draft':
            return Exam.objects.filter(course=self, is_deleted=0, exam_type='interactive_exercise').exists()
        else:
            now = datetime.now()
            return Exam.objects.filter(course=self, is_deleted=0, exam_type='interactive_exercise', live_datetime__lt=now).exists()
                
    def has_problem_sets(self):
        if self.mode == 'draft':
            return Exam.objects.filter(course=self, is_deleted=0, exam_type="problemset").exists()
        else:
            now = datetime.now()
            return Exam.objects.filter(course=self, is_deleted=0, exam_type="problemset", live_datetime__lt=now).exists()
        
    def has_videos(self):
        if self.mode == 'draft':
            return Video.objects.filter(course=self, is_deleted=0).exists()
        else:
            now = datetime.now()
            return Video.objects.filter(course=self, is_deleted=0, live_datetime__lt=now).exists()
    
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
        return (self.get_all_course_admins() | self.get_all_students())

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
            short_description = self.short_description,
            prerequisites = self.prerequisites,
            accompanying_materials = self.accompanying_materials,
            outcomes = self.outcomes,
            faq = self.faq,
            logo = self.logo,
            preview_only_mode = self.preview_only_mode,
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
        if not clone_fields or 'short_description' in clone_fields:
            ready_instance.short_description = self.short_description    
        if not clone_fields or 'prerequisites' in clone_fields:
            ready_instance.prerequisites = self.prerequisites    
        if not clone_fields or 'accompanying_materials' in clone_fields:
            ready_instance.accompanying_materials = self.accompanying_materials    
        if not clone_fields or 'outcomes' in clone_fields:
            ready_instance.outcomes = self.outcomes
        if not clone_fields or 'faq' in clone_fields:
            ready_instance.faq = self.faq
        if not clone_fields or 'logo' in clone_fields:
            ready_instance.logo = self.logo

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
        if not clone_fields or 'short_description' in clone_fields:
            self.short_description = ready_instance.short_description    
        if not clone_fields or 'prerequisites' in clone_fields:
            self.prerequisites = ready_instance.prerequisites    
        if not clone_fields or 'accompanying_materials' in clone_fields:
            self.accompanying_materials = ready_instance.accompanying_materials    
        if not clone_fields or 'outcomes' in clone_fields:
            self.outcomes = ready_instance.outcomes
        if not clone_fields or 'faq' in clone_fields:
            self.faq = ready_instance.faq
        if not clone_fields or 'logo' in clone_fields:
            self.logo = ready_instance.logo

        self.save()

    class Meta:
        db_table = u'c2g_courses'

class ContentSectionManager(models.Manager):
    def getByCourse(self, course):
        return self.filter(course=course,is_deleted=0).order_by('index')

class ContentSection(TimestampMixin, Stageable, Sortable, Deletable, models.Model):
    course = models.ForeignKey(Course, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    subtitle = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    objects = ContentSectionManager()

    def create_ready_instance(self):
        ready_instance = ContentSection(
            course=self.course.image,
            title=self.title,
            index=self.index,
            subtitle=self.subtitle,
            slug=self.slug,
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
        if not clone_fields or 'subtitle' in clone_fields:
            ready_instance.subtitle = self.subtitle
        if not clone_fields or 'slug' in clone_fields:
            ready_instance.slug = self.slug

        ready_instance.save()

    def revert(self, clone_fields = None):
        if self.mode != 'draft': return;

        ready_instance = self.image
        if not clone_fields or 'title' in clone_fields:
            self.title = ready_instance.title
        if not clone_fields or 'index' in clone_fields:
            self.index = ready_instance.index
        if not clone_fields or 'subtitle' in clone_fields:
            self.subtitle = ready_instance.subtitle
        if not clone_fields or 'slug' in clone_fields:
            self.slug = ready_instance.slug

        self.save()

    def getChildren(self, gettagged=False, getsorted=True):
        """Return the child items of this section: Videos, Files, etc.

        If gettagged is True, return a list of dictionaries having some item 
        metadata in addition to the item reference, otherwise return only a 
        list of item references.

        If getsorted is True, return the list sorted by 'index' field, which
        indicates manual sorting preference; otherwise ordering is unspecified.
        """

        dict_list = []
        for tag, cls in ContentGroup.groupable_types.iteritems():
            dict_list.extend([{'item':item, 'index':item.index, 'type':tag} for item in cls.objects.getBySection(section=self)])

        if getsorted:
            dict_list = sorted(dict_list, key=lambda k: k['index'])
        return dict_list if gettagged else [x['item'] for x in dict_list]

    def countChildren(self):
        return len(self.getChildren(gettagged=True, getsorted=False))

    def getNextIndex(self):
        # We will not return len(children)+1 since this approach is not fail-
        # safe. If an index is skipped for whatever reason, we want to make
        # sure we are still robust
        children = self.getChildren()
        if len(children) == 0:
            return 1
        
        if children[-1].index == None:
            return len(children)+1
        else:
            return children[-1].index+1

    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return "No Title"

    class Meta:
        db_table = u'c2g_content_sections'

class AdditionalPageManager(models.Manager):
    def getByCourse(self, course):
        # Additional pages displayed under sections have a live_datetime effect.
        if course.mode == 'draft':
            return self.filter(course=course,is_deleted=0, section__is_deleted=0, menu_slug=None).order_by('section','index')
        else:
            now = datetime.now()
            return self.filter(course=course,is_deleted=0, section__is_deleted=0,menu_slug=None,live_datetime__lt=now).order_by('section','index')

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
        if not self.image:
            return False
        if self.title != self.image.title:
            return False
        if self.description != self.image.description:
            return False

        return True

    def get_url(self):
        return reverse("courses.additional_pages.views.main", args=[self.course.prefix, self.course.suffix, self.slug])

    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return "No Title"
    
    class Meta:
        db_table = u'c2g_additional_pages'
        
        
class FileManager(models.Manager):
    def getByCourse(self, course):
        if course.mode == 'draft':
            return self.filter(course=course,is_deleted=0, section__is_deleted=0).order_by('section','index')
        else:
            now = datetime.now()
            return self.filter(course=course,is_deleted=0, section__is_deleted=0, live_datetime__lt=now).order_by('section','index')
            
    def getBySection(self, section):
        if section.mode == 'draft':
            return self.filter(section=section, is_deleted=0).order_by('index')
        else:
            now = datetime.now()
            return self.filter(section=section, is_deleted=0, live_datetime__lt=now).order_by('index')

class File(TimestampMixin, Stageable, Sortable, Deletable, models.Model):
    course  = models.ForeignKey(Course, db_index=True)
    section = models.ForeignKey(ContentSection, null=True)
    title   = models.CharField(max_length=255, null=True, blank=True)
    file    = models.FileField(upload_to=get_file_path)
    handle  = models.CharField(max_length=255, null=True, db_index=True)
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

    def commit(self):
        img = self.image
        img.course=self.course.image
        img.section=self.section.image
        img.title=self.title
        img.index = self.index
        img.handle = self.handle
        img.live_datetime = self.live_datetime
        img.save()
    
    def has_storage(self):
        """Return True if we have a copy of this file on our storage."""
        if self.dl_link() == "":
            return False
        else:
            return True

    def dl_link(self):
        filename = self.file.name
        if is_storage_local():
            url = get_site_url() + self.file.storage.url(filename)
        else:
            storecache = get_cache("file_store")
            storecache_key = filename.replace(' ','%20')[-240:]   # memcache no spaces in cache key, char limit
            storecache_hit = storecache.get(storecache_key)
            if storecache_hit:
                CacheStat.report('hit', 'file_store')
                if 'url' in storecache_hit:
                    return storecache_hit['url']
                else:
                    return ""
            else:
                CacheStat.report('miss', 'file_store')
                if not self.file.storage.exists(filename):
                    # negative cache
                    storecache_val = {'size':0}
                    storecache.set(storecache_key, storecache_val)
                    return ""
                url = self.file.storage.url_monkeypatched(filename, response_headers={'response-content-disposition': 'attachment'})
                storecache_val = {'url':url}
                storecache.set(storecache_key, storecache_val)
        return url
        
    def get_ext(self):
        """ Return the extension of a file - eg pdf - or just '' if it doesn't have one """
        # TODO: use filemagic or python-magic for this instead
        file_parts = self.file.name.split('.')
        if len(file_parts) > 1:
            return (file_parts.pop().lower())
        return ''
            
    def get_icon_type(self):
        """ return an appropriate icon for a file, based on its extension """
        extensions = {
          # extension : icon name
                'html': 'globe',
                'htm':  'globe',
                'ppt':  'list-alt',
                'pptx': 'list-alt',
                'jpg':  'picture',
                'png':  'picture',
                'gif':  'picture',
                'jpeg': 'picture',
                'mp3':  'music',
                'aac':  'music',
                'gz':   'download-alt',
                'zip':  'download-alt',
                'tar':  'download-alt',
                'bz':   'download-alt',
                'bz2':  'download-alt',
                'csv':  'table',
                'xls':  'table'
        }
        file_extension = self.get_ext()
        return extensions.get(file_extension, 'file')

    def get_url(self):
        return self.file.url # FIXME: cache this

    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return "No Title"

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
        if not self.image:
            return False
        if self.title != self.image.title:
            return False
        if self.description != self.image.description:
            return False

        return True

    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return "No Title"

    class Meta:
        db_table = u'c2g_announcements'

class StudentSection(TimestampMixin, Deletable, models.Model):
    course = models.ForeignKey(Course, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    capacity = models.IntegerField(default=999)
    members = models.ManyToManyField(User)
    class Meta:
        db_table = u'c2g_sections'

class CourseStudentList(TimestampMixin, models.Model):
    # TODO: is this model used anyplace? Remove?
    course = models.ForeignKey(Course, db_index=True)
    members = models.ManyToManyField(User)
    max_completion_level = models.IntegerField(default=0)

    def __unicode__(self):
        return u'CourseStudentList course: ' + str(self.course_id)

class CourseCertificate(TimestampMixin, models.Model):
    course = models.ForeignKey(Course, db_index=True)
    assets = models.CharField(max_length=255, null=True)
    storage = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=64, default="completion")

    @classmethod
    def create(cls, course, type='completion'):
        """Correctly instantiate a new CourseCertificate."""
        c = cls(course=course, type=type)
        c.assets = os.path.join(course.prefix, course.suffix, 'certificates', 'assets')
        c.storage = os.path.join(course.prefix, course.suffix, 'certificates', 'storage')
        c.save()
        return c

    def get_filename_by_user(self, user):
        """Generate the filename used for certificate storage on disk.

        If user is unspecified, return None.
        """
        return "%s-%s-%s-%s.pdf" % (user.username, str(user.id), self.course.handle, self.type)

    def dl_link(self, user):
        """Generate a download link for this certificate for the given user"""
        filename = self.get_filename_by_user(user)
        asset_path = os.path.join(self.storage, filename)
        url = ''
        if default_storage.exists(asset_path):
            if is_storage_local():
                url = get_site_url() + default_storage.url(asset_path)
            else:
                url = default_storage.url_monkeypatched(asset_path, response_headers={'response-content-disposition': 'attachement'})
        return url

    def __repr__(self):
        s = u'CourseCertificate(pk=' + str(self.id) + ','
        s += 'course_id=' + str(self.course_id) + ','
        s += 'type=' + self.type + ','
        s += 'assets=' + self.assets + ')'
        return s

    def __unicode__(self):
        return repr(self)

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
    piazza_email = models.CharField(max_length=128,blank=True)
    piazza_name = models.CharField(max_length=128,blank=True)
    email_me = models.BooleanField(default=True) #get emails sent by the teaching staff
    
    institutions = models.ManyToManyField(Institution) #these are confirmed institutions via shib or other trusted verifier

    client_ip = models.CharField(max_length=30, null=True)
    user_agent = models.CharField(max_length=256, null=True)
    referrer = models.CharField(max_length=256, null=True)
    accept_language = models.CharField(max_length=64, null=True)

    client_ip_first = models.CharField(max_length=30, null=True)
    user_agent_first = models.CharField(max_length=256, null=True)
    referrer_first = models.CharField(max_length=256, null=True)
    accept_language_first = models.CharField(max_length=64, null=True)

    certificates = models.ManyToManyField(CourseCertificate)
    
    def __unicode__(self):
        return self.user.username

    def is_student_list(self, group_list=None, courses=None):
        if group_list == None:
            group_list = self.user.groups.all()
        
        if courses == None:
            courses = Course.objects.filter(mode='ready')
    
        is_student_list = []
        for course in courses:
            for group in group_list:
                if course.student_group_id == group.id:
                    is_student_list.append(course)
                    break
        return is_student_list

    def is_instructor_list(self, group_list=None, courses=None):
        if group_list == None:
            group_list = self.user.groups.all()
        
        if courses == None:
            courses = Course.objects.filter(mode='ready')
    
        is_instructor_list = []
        for course in courses:
            for group in group_list:
                if course.instructor_group_id == group.id:
                    is_instructor_list.append(course)
                    break
        return is_instructor_list

    def is_tas_list(self, group_list=None, courses=None):
        if group_list == None:
            group_list = self.user.groups.all()
        
        if courses == None:
            courses = Course.objects.filter(mode='ready')
    
        is_tas_list = []
        for course in courses:
            for group in group_list:
                if course.tas_group_id == group.id:
                    is_tas_list.append(course)
                    break
        return is_tas_list

    def is_readonly_tas_list(self, group_list=None, courses=None):
        if group_list == None:
            group_list = self.user.groups.all()

        if courses == None:
            courses = Course.objects.filter(mode='ready')
    
        is_readonly_tas_list = []
        for course in courses:
            for group in group_list:
                if course.readonly_tas_group_id == group.id:
                    is_readonly_tas_list.append(course)
                    break
        return is_readonly_tas_list

    class Meta:
        db_table = u'c2g_user_profiles'

def create_user_profile(sender, instance, created, raw, **kwargs):
    if created and not raw:  #create means that a new DB entry is created, raw is set when fixtures are being loaded
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

class VideoManager(models.Manager):
    def getByCourse(self, course):
        if course.mode == 'draft':
            return self.filter(course=course,is_deleted=0, section__is_deleted=0).order_by('section','index')
        else:
            now = datetime.now()
            return self.filter(course=course,is_deleted=0, section__is_deleted=0, live_datetime__lt=now).order_by('section','index')

    def getBySection(self, section):
        if section.mode == 'draft':
            return self.filter(section=section, is_deleted=0).order_by('index')
        else:
            now = datetime.now()
            return self.filter(section=section, is_deleted=0, live_datetime__lt=now).order_by('index')


class Video(TimestampMixin, Stageable, Sortable, Deletable, models.Model):
    course = models.ForeignKey(Course, db_index=True)
    section = models.ForeignKey(ContentSection, null=True, db_index=True)
    exam = models.ForeignKey('Exam', null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=30, default="youtube")
    url = models.CharField("Youtube Video ID", max_length=255, null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    slug = models.SlugField("URL Identifier", max_length=255, null=True)
    file = models.FileField(upload_to=get_file_path)
    handle = models.CharField(max_length=255, null=True, db_index=True)
    objects = VideoManager()

    def create_ready_instance(self):
        if (self.exam and self.exam.image):
            image_exam = self.exam.image
        else:
            image_exam = None
        ready_instance = Video(
            course=self.course.image,
            section=self.section.image,
            exam=image_exam,
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
        if (self.exam and self.exam.image):
            image_exam = self.exam.image
        else:
            image_exam = None
        if not clone_fields or 'exam' in clone_fields:
            ready_instance.exam = image_exam
        if not clone_fields or 'live_datetime' in clone_fields:
            ready_instance.live_datetime = self.live_datetime

        ready_instance.save()

        if self.exercises_changed() == True:
            draft_videoToExs =  VideoToExercise.objects.getByVideo(self)
            ready_videoToExs = VideoToExercise.objects.getByVideo(ready_instance)

            #If filename in ready but not in draft list then delete it.
            for ready_videoToEx in ready_videoToExs:
                if not self.in_list(ready_videoToEx, draft_videoToExs):
                    ready_videoToEx.is_deleted = 1
                    ready_videoToEx.save()

            #Find ready instance, if it exists, and set it.
            for draft_videoToEx in draft_videoToExs:
                not_deleted_ready_videoToEx = VideoToExercise.objects.filter(video=ready_instance, exercise=draft_videoToEx.exercise, is_deleted=0)
                deleted_ready_videoToExs = VideoToExercise.objects.filter(video=ready_instance, exercise=draft_videoToEx.exercise, is_deleted=1).order_by('-id')
                        
                if not_deleted_ready_videoToEx.exists():
                    ready_videoToEx = not_deleted_ready_videoToEx[0]
                    ready_videoToEx.video_time = draft_videoToEx.video_time
                    ready_videoToEx.save() 
                    
                elif deleted_ready_videoToExs.exists():
                    ready_videoToEx = deleted_ready_videoToExs[0]
                    ready_videoToEx.is_deleted = 0
                    ready_videoToEx.video_time = draft_videoToEx.video_time
                    ready_videoToEx.save()
                    
                else:
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
        if (ready_instance.exam and ready_instance.exam.image):
            image_exam = ready_instance.exam.image
        else:
            image_exam = None
        if not clone_fields or 'exam' in clone_fields:
            self.exam = image_exam
        if not clone_fields or 'live_datetime' in clone_fields:
            self.live_datetime = ready_instance.live_datetime

        self.save()

        if self.exercises_changed() == True:
            draft_videoToExs = VideoToExercise.objects.getByVideo(self)
            ready_videoToExs = VideoToExercise.objects.getByVideo(ready_instance)

            #If filename in draft but not in ready list then delete it.
            for draft_videoToEx in draft_videoToExs:
                if not self.in_list(draft_videoToEx, ready_videoToExs):
                    draft_videoToEx.is_deleted = 1
                    draft_videoToEx.save()

            #Find draft instance and set it.
            for ready_videoToEx in ready_videoToExs:
                not_deleted_draft_videoToEx = VideoToExercise.objects.filter(video=self, exercise=ready_videoToEx.exercise, is_deleted=0)
                deleted_draft_videoToExs = VideoToExercise.objects.filter(video=self, exercise=ready_videoToEx.exercise, is_deleted=1).order_by('-id')
                        
                if not_deleted_draft_videoToEx.exists():
                    draft_videoToEx = not_deleted_draft_videoToEx[0]
                    draft_videoToEx.video_time = ready_videoToEx.video_time
                    draft_videoToEx.save() 
                    
                elif deleted_draft_videoToExs.exists():
                    draft_videoToEx = deleted_draft_videoToExs[0]
                    draft_videoToEx.is_deleted = 0
                    draft_videoToEx.video_time = ready_videoToEx.video_time
                    draft_videoToEx.save()

        else:
            ready_videoToExs = VideoToExercise.objects.getByVideo(ready_instance)
            for ready_videoToEx in ready_videoToExs:
                ready_videoToEx.image.video_time = ready_videoToEx.video_time
                ready_videoToEx.image.save()

    def is_synced(self):
        if not self.image:
            return False
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
        if (self.exam and self.exam.image):
            image_exam = self.exam.image
        else:
            image_exam = None
        if image_exam != prod_instance.exam:
            return False
        if self.live_datetime != prod_instance.live_datetime:
            return False
        draft_videoToExs = VideoToExercise.objects.getByVideo(self)
        for draft_videoToEx in draft_videoToExs:
            if draft_videoToEx.video_time != draft_videoToEx.image.video_time:
                return False
        return True

    def has_storage(self):
        """Return True if we have a copy of this video on our storage."""
        if self.dl_link() == "":
            return False
        else:
            return True

    def dl_link(self):
        """Return fully-qualified download URL for this video, or empty string."""
        storecache = get_cache("video_store")
        storecache_key = self.file.name.replace(' ','%20')[-240:]   # memcache no spaces in cache key, char limit
        storecache_hit = storecache.get(storecache_key)
        if storecache_hit:
            CacheStat.report('hit', 'video_store')
            if 'url' in storecache_hit:
                return storecache_hit['url']
            else:
                return ""
        else:
            CacheStat.report('miss', 'video_store')
            videoname = self.file.name
            if not self.file.storage.exists(videoname):
                # negative cache
                storecache_val = {'size':0}
                storecache.set(storecache_key, storecache_val)
                return ""
            if is_storage_local():
                # FileSystemStorage returns a path, not a url
                loc_raw = get_site_url() + self.file.storage.url(videoname)
            else:
                loc = self.file.storage.url_monkeypatched(videoname,
                    response_headers={'response-content-disposition': 'attachment'})
            storecache_val = {'size':self.file.size, 'url':loc }
            storecache.set(storecache_key, storecache_val)
            return loc


    def dl_links_all(self):
        """
        Return list of tuples fully-qualified download URLs for video variants.
        Tuples of the form: (size_tag, URL, size, description)
        """

        myname  = self.file.name
        mystore = self.file.storage
        if is_storage_local():
            # FIXME: doesn't work on local sites yet
            print "DEBUG: Multiple download links don't work on local sites yet, sorry." 
            return [('large', get_site_url() + mystore.url(myname), self.file.size, '')]
        else:
            # XXX: very S3 specific
            urlof = mystore.url_monkeypatched
            basepath, filename = RE_S3_PATH_FILENAME_SPLIT.match(myname).groups()
            names = []
            for size in sorted(video_resize_options):
                checkfor = basepath+'/'+size+'/'+filename
                storecache = get_cache('video_store')
                storecache_key = checkfor.replace(' ','%20')[-240:]  # memcache no spaces in cache key, char limit
                storecache_hit = storecache.get(storecache_key)
                if storecache_hit:
                    CacheStat.report('hit', 'video_store')
                    if storecache_hit['size'] > 0:
                        # print "found %s in cache (%s, %d, %s)"\
                        #      % (size, storecache_hit['url'], storecache_hit['size'], storecache_hit['desc'])
                        names.append((size, storecache_hit['url'], storecache_hit['size'], storecache_hit['desc']))
                    else:
                        # print "found %s in cache (NEG)" % size
                        pass

                else:
                    CacheStat.report('miss', 'video_store')
                    gotback = [x for x in mystore.bucket.list(prefix=checkfor)]
                    if gotback:
                        filesize=gotback[0].size
                        fileurl=urlof(checkfor,
                                response_headers={'response-content-disposition': 'attachment'})                  
                        filedesc=video_resize_options[size][3]
                        names.append((size, fileurl, filesize, filedesc))
                        # positive cache
                        # print "add %s in cache (%s, %d, %s)" % (size, fileurl, filesize, filedesc)
                        storecache_val = {'size':filesize, 'url':fileurl, 'desc':filedesc}
                        storecache.set(storecache_key, storecache_val)
                    else:
                        # negative cache
                        # print "add %s in cache (NEG)" % (size)
                        storecache_val = {'size':0 }
                        storecache.set(storecache_key, storecache_val)

            if not names:
                fileurl=urlof(myname,
                                response_headers={'response-content-disposition': 'attachment'})          
                names = [('large', fileurl, self.file.size, '')]
            return names

    def ret_url(self):
        return "https://www.youtube.com/analytics#dt=lt,fi=v-" + self.url + ",r=retention"

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

    def in_list(self, needle, haystack):
        for hay in haystack:
            if needle.exercise.fileName == hay.exercise.fileName:
                return True
        return False

    def get_url(self):
        return reverse("courses.videos.views.view", args=[self.course.prefix, self.course.suffix, self.slug])
        
    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return "No Title"

    class Meta:
        db_table = u'c2g_videos'


class CacheStat():
    """
    Gather and report counter-based stats for our simple caches.
       report('hit', 'video-cache') or
       report('miss', 'files-cache')
    """
    lastReportTime = datetime.now()
    count = {} 
    reportingIntervalSec = getattr(settings, 'CACHE_STATS_INTERVAL', 60*60)   # hourly
    reportingInterval = timedelta(seconds=reportingIntervalSec)

    @classmethod
    def report(cls, op, cache):
        if op not in ['hit', 'miss']:
            logger.error("cachestat invalid operation, expected hit or miss")
            return
        if cache not in cls.count:
            cls.count[cache] = {}
        if op not in cls.count[cache]:
            cls.count[cache][op] = 0
        cls.count[cache][op] += 1

        # stat interval expired: print stats and zero out counter
        if datetime.now() - cls.lastReportTime > cls.reportingInterval:
            for c in cls.count:
                hit = cls.count[c].get('hit', 0)
                miss = cls.count[c].get('miss', 0)
                if hit + miss == 0:
                    logger.info("cache stats for %s: hits %d, misses %d" % (c, hit, miss))
                else:
                    rate = float(hit) / float(hit + miss) * 100.0
                    logger.info("cache stats for %s: hits %d, misses %d, rate %2.1f" % (c, hit, miss, rate))

            cls.lastReportTime = datetime.now()
            cls.count = {}      # zero out the counts


class VideoViewTraces(TimestampMixin, models.Model):
    course = models.ForeignKey(Course, db_index=True)
    video = models.ForeignKey(Video, db_index=True)
    user = models.ForeignKey(User)
    trace = models.TextField(blank=True)
    
    class Meta:
        db_table = u'c2g_video_view_traces'
        
class VideoActivity(models.Model):
     student = models.ForeignKey(User)
     course = models.ForeignKey(Course)
     video = models.ForeignKey(Video)
     start_seconds = models.IntegerField(default=0, blank=True)
     max_end_seconds = models.IntegerField(default=0, blank=True)
     #last_watched = models.DateTimeField(auto_now=True, auto_now_add=False)

     def percent_done(self):
         return float(self.start_seconds)*100/self.video.duration

     def __unicode__(self):
            return self.student.username
     class Meta:
        db_table = u'c2g_video_activity'
        
class VideoDownload(models.Model):
    student = models.ForeignKey(User)
    course = models.ForeignKey(Course)
    video = models.ForeignKey(Video)
    download_date = models.DateTimeField(auto_now=False, auto_now_add=True)
    format = models.CharField(max_length=35, null=True, blank=True)
    
    class Meta:
        db_table = u'c2g_video_download'

class ProblemSetManager(models.Manager):
    def getByCourse(self, course):
        if course.mode == 'draft':
            return self.filter(course=course,is_deleted=0, section__is_deleted=0).order_by('section','index')
        else:
            now = datetime.now()
            return self.filter(course=course,is_deleted=0, section__is_deleted=0,live_datetime__lt=now).order_by('section','index')
        
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
    path = models.CharField(max_length=255) #used as URL path to load problem set contents (Khan Summative file)
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
                
            #If filename in ready but not in draft list then delete it.
            for ready_psetToEx in ready_psetToExs:
                if not self.in_list(ready_psetToEx, draft_psetToExs):
                    ready_psetToEx.is_deleted = 1
                    ready_psetToEx.save()

            #Find ready instance, if it exists, and set it.
            for draft_psetToEx in draft_psetToExs:
                not_deleted_ready_psetToEx = ProblemSetToExercise.objects.filter(problemSet=ready_instance, exercise=draft_psetToEx.exercise, is_deleted=0)
                deleted_ready_psetToExs = ProblemSetToExercise.objects.filter(problemSet=ready_instance, exercise=draft_psetToEx.exercise, is_deleted=1).order_by('-id')
                        
                if not_deleted_ready_psetToEx.exists():
                    ready_psetToEx = not_deleted_ready_psetToEx[0]
                    ready_psetToEx.number = draft_psetToEx.number
                    ready_psetToEx.save() 
                    
                elif deleted_ready_psetToExs.exists():
                    ready_psetToEx = deleted_ready_psetToExs[0]
                    ready_psetToEx.is_deleted = 0
                    ready_psetToEx.number = draft_psetToEx.number
                    ready_psetToEx.save()
                    
                else:
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

            #If filename in draft but not in ready list then delete it.
            for draft_psetToEx in draft_psetToExs:
                if not self.in_list(draft_psetToEx, ready_psetToExs):
                    draft_psetToEx.is_deleted = 1
                    draft_psetToEx.save()

            #Find draft instance and set it.
            for ready_psetToEx in ready_psetToExs:
                not_deleted_draft_psetToEx = ProblemSetToExercise.objects.filter(problemSet=self, exercise=ready_psetToEx.exercise, is_deleted=0)
                deleted_draft_psetToExs = ProblemSetToExercise.objects.filter(problemSet=self, exercise=ready_psetToEx.exercise, is_deleted=1).order_by('-id')
                        
                if not_deleted_draft_psetToEx.exists():
                    draft_psetToEx = not_deleted_draft_psetToEx[0]
                    draft_psetToEx.number = ready_psetToEx.number
                    draft_psetToEx.save() 
                    
                elif deleted_draft_psetToExs.exists():
                    draft_psetToEx = deleted_draft_psetToExs[0]
                    draft_psetToEx.is_deleted = 0
                    draft_psetToEx.number = ready_psetToEx.number
                    draft_psetToEx.save()

        else:
            ready_psetToExs = ProblemSetToExercise.objects.getByProblemset(ready_instance)
            for ready_psetToEx in ready_psetToExs:
                ready_psetToEx.image.number = ready_psetToEx.number
                ready_psetToEx.image.save()


    def is_synced(self):
        if not self.image:
            return False
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
            exercise_activities = pset_activities.filter(problemset_to_exercise__exercise__fileName=psetToEx.exercise.fileName).order_by('time_created')
            for exercise_activity in exercise_activities:
                if exercise_activity.attempt_number == submissions_permitted:
                    questions_completed += 1
                    break
                elif exercise_activity.complete:
                    questions_completed += 1
                    break
        return questions_completed
    
    #This is the old version, from sprint-15, without late penalties
    def get_score_v1(self, student, detailed=False):
        exercise_scores = {}
        resubmission_penalty = self.resubmission_penalty
        submissions_permitted = self.submissions_permitted
        if submissions_permitted == 0:
            submissions_permitted = sys.maxsize
        pset_activities = ProblemActivity.objects.select_related('problemSet', 'exercise').filter(problemset_to_exercise__problemSet=self, student=student)
        psetToExs = ProblemSetToExercise.objects.getByProblemset(self)
        total_score = 0.0
        for psetToEx in psetToExs:
            exercise_activities = pset_activities.filter(problemset_to_exercise__exercise__fileName=psetToEx.exercise.fileName).order_by('time_created')
            exercise_percent = 100
            for exercise_activity in exercise_activities:
                if exercise_activity.attempt_number > submissions_permitted:
                    break
                elif exercise_activity.complete:
                    total_score += exercise_percent/100.0
                    break
                else:
                    exercise_percent -= resubmission_penalty
            exercise_scores[psetToEx.exercise.id] = exercise_percent/100.0
        
        if detailed: return exercise_scores
        else: return total_score


    def get_score(self, student, detailed=False):
        exercise_scores = {}
        resubmission_penalty = self.resubmission_penalty
        submissions_permitted = self.submissions_permitted
        if submissions_permitted == 0:
            submissions_permitted = sys.maxsize
        pset_activities = ProblemActivity.objects.select_related('problemSet', 'exercise').filter(problemset_to_exercise__problemSet=self, student=student)
        psetToExs = ProblemSetToExercise.objects.getByProblemset(self)
        total_score = 0.0
        for psetToEx in psetToExs:
            exercise_activities = pset_activities.filter(problemset_to_exercise__exercise__fileName=psetToEx.exercise.fileName).order_by('time_created')
            #Exercise percent starts at 100 and gets deducted per wrong attempt, and will
            #be added to the total score if a valid complete_time is found
            exercise_percent = 100
            complete_time = None
            for exercise_activity in exercise_activities:
                #short-circuit if no correct attempts within the allowed number or
                #within the partial credit deadline
                if exercise_activity.attempt_number > submissions_permitted or \
                   exercise_activity.time_created > self.partial_credit_deadline:
                    break
                #if submission is valid and correct, mark complete_time, and break
                elif exercise_activity.complete:
                    complete_time = exercise_activity.time_created
                    break
                #deduct for submission that was incorrect
                else:
                    exercise_percent -= resubmission_penalty
        
            #give 0 if no correct attempts
            if not complete_time:
                exercise_percent=0
            #penalize if late
            elif complete_time > self.grace_period:
                exercise_percent = int(exercise_percent*(100-self.late_penalty)/100.0)
        
            #floor exercise percent at 0
            exercise_percent = max(exercise_percent,0)
            
            #add to total_score
            total_score += exercise_percent/100.0
                    
            exercise_scores[psetToEx.exercise.id] = exercise_percent/100.0
            
        if detailed: return exercise_scores
        else: return total_score

    def in_list(self, needle, haystack):
        for hay in haystack:
            if needle.exercise.fileName == hay.exercise.fileName:
                return True
        return False

    def get_url(self):
        # not using reverse() because problemsets have been removed from urls.py
        return '/' + self.course.prefix.replace('--', '/') + '/problemsets/' + self.slug

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
        
    def get_slug(self):
        split_parts = self.fileName.split('/')
        last_part = split_parts[-1]
        split_parts = last_part.split('.')
        if len(split_parts) == 0:
            return "Untitled exercise"
        elif len(split_parts) == 1:
            return split_parts[0]
        else:
            return ".".join(split_parts[0:-1])
    
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
    sender = models.ForeignKey(User, default=1, blank=True, null=True)
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
    optout = models.BooleanField(default=False)
    optout_code = models.CharField(max_length=64, default='optout')
    def __unicode__(self):
        return self.addr

def write_optout_code(sender, instance, created, raw, **kwargs):
    if created and not raw:  #create means that a new DB entry is created, raw is set when fixtures are being loaded
        instance.optout_code = md5(instance.name+instance.addr+datetime.isoformat(datetime.now())).hexdigest()
        instance.save()

post_save.connect(write_optout_code, sender=EmailAddr)


class MailingList(models.Model):
    name = models.CharField(max_length=128, blank=True)
    members = models.ManyToManyField(EmailAddr)
    def __unicode__(self):
        return self.name

class ListEmail(Email, models.Model):
    from_name = models.CharField(max_length=128, blank=True)
    from_addr = models.CharField(max_length=128, blank=True)
    to_list = models.ForeignKey(MailingList)
    def __unicode__(self):
        return self.subject
        
class PageVisitLog(TimestampMixin, models.Model):
    course = models.ForeignKey(Course, db_index=True)
    user = models.ForeignKey(User)
    page_type = models.CharField(max_length=128, db_index=True)
    object_id = models.CharField(max_length=128, blank=True)
    
    class Meta:
        db_table = u'c2g_page_visit_log'

class ExamManager(models.Manager):
    def getByCourse(self, course):
        if course.mode == 'draft':
            return self.filter(course=course, is_deleted=0, section__is_deleted=0).order_by('section','index')
        else:
            now = datetime.now()
            return self.filter(course=course, is_deleted=0, section__is_deleted=0,live_datetime__lt=now).order_by('section','index')

    def getByCourseSubTypes(self, course, types):
        if course.mode == 'draft':
            return self.filter(course=course, is_deleted=0, exam_type__in=types, section__is_deleted=0).order_by('section','index')
        else:
            now = datetime.now()
            return self.filter(course=course, is_deleted=0, exam_type__in=types, section__is_deleted=0,live_datetime__lt=now).order_by('section','index')

    def getBySection(self, section):
        if section.mode == 'draft':
            return self.filter(section=section, is_deleted=0).order_by('index')
        else:
            now = datetime.now()
            return self.filter(section=section, is_deleted=0, live_datetime__lt=now).order_by('index')

class Exam(TimestampMixin, Deletable, Stageable, Sortable, models.Model):
    
    EXAM_TYPE_CHOICES = (
                         ('exam', 'exam'),
                         ('problemset','problemset'),
                         ('survey', 'survey'),
                         ('interactive_exercise', 'interactive_exercise'),
                         )
    
    Exam_HUMAN_TYPES = {'exam':'Exam',
                        'problemset':'Quiz',
                        'survey':'Survey',
                        'interactive_exercise':'Interactive Exercise',
                       }
    
    course = models.ForeignKey(Course, db_index=True)
    section = models.ForeignKey(ContentSection, null=True, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    html_content = models.TextField(blank=True)
    xml_metadata = models.TextField(null=True, blank=True)
    xml_imported = models.TextField(null=True, blank=True) ###This is the XML used to import the exam content.  We only store it to re-display it.
    slug = models.SlugField("URL Identifier", max_length=255, null=True)
    due_date = models.DateTimeField(null=True, blank=True)
    grace_period = models.DateTimeField(null=True, blank=True)
    partial_credit_deadline = models.DateTimeField(null=True, blank=True)
    late_penalty = models.IntegerField(default=0, null=True, blank=True)
    submissions_permitted = models.IntegerField(default=999, null=True, blank=True)
    resubmission_penalty = models.IntegerField(default=0, null=True, blank=True)
    autograde = models.BooleanField(default=False)
    display_single = models.BooleanField(default=False)
    grade_single = models.BooleanField(default=False)
    invideo = models.BooleanField(default=False)
    timed = models.BooleanField(default=False)
    minutesallowed = models.IntegerField(null=True, blank=True)
    minutes_btw_attempts = models.IntegerField(default=0)
    exam_type = models.CharField(max_length=32, default="exam", choices=EXAM_TYPE_CHOICES)
    #there is a function from assessment_type => (invideo, exam_type, display_single, grade_single, autograde) that we don't want to write inverse for
    #so we just store it
    assessment_type = models.CharField(max_length=64, null=True, blank=True)
    total_score = models.FloatField(null=True, blank=True)
    objects = ExamManager()
    
    def num_of_student_records(self, student):
        """This returns the number of completed records on this exam by student"""
        attempt_num_obj = ExamRecord.objects.filter(exam=self, student=student, complete=True).aggregate(Max('attempt_number'))
        if not attempt_num_obj['attempt_number__max']:
            return 0
        else:
            return attempt_num_obj['attempt_number__max']


    def max_attempts_exceeded(self, student):
        """Returns True if student has used up max number of attempts"""
        if self.submissions_permitted==0:
            return False
        return self.num_of_student_records(student) >= self.submissions_permitted
    
    def past_due(self):
        if self.due_date and (datetime.now() > self.grace_period):
            return True
        return False
    
    def past_all_deadlines(self):
        future = datetime(3000,1,1)
        grace_period = self.grace_period if self.grace_period else future
        partial_credit_deadline = self.partial_credit_deadline if self.partial_credit_deadline else future

        compareD = max(grace_period, partial_credit_deadline)
    
        return datetime.now() > compareD
    
    def load_mathjax(self):
        """uses a regexp to figure out if the rendering of the exam needs mathjax
           the regexp are rough, but should not have any false negatives.  (at
           worst we load mathjax when we don't need it.
        """
        if re.search(r"\$\$.*\$\$", self.html_content, re.DOTALL) or re.search(r"\\\[.*\\\]", self.html_content, re.DOTALL):
            return True
        return False
        
    
    def create_ready_instance(self):
        ready_instance = Exam(
            course=self.course.image,
            section=self.section.image,
            title=self.title,
            description=self.description,
            html_content=self.html_content,
            slug=self.slug,
            index=self.index,
            mode='ready',
            image=self,
            due_date=self.due_date,
            grace_period=self.grace_period,
            total_score=self.total_score,
            exam_type=self.exam_type,
            live_datetime = self.live_datetime,
            xml_metadata = self.xml_metadata,
            xml_imported = self.xml_imported,
            partial_credit_deadline = self.partial_credit_deadline,
            late_penalty = self.late_penalty,
            submissions_permitted = self.submissions_permitted,
            resubmission_penalty = self.resubmission_penalty,
            autograde = self.autograde,
            display_single = self.display_single,
            grade_single = self.grade_single,
            invideo = self.invideo,
            timed = self.timed,
            minutesallowed = self.minutesallowed,
            minutes_btw_attempts = self.minutes_btw_attempts,
            assessment_type = self.assessment_type,
        )
        ready_instance.save()
        self.image = ready_instance
        self.save()
    
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
        if not clone_fields or 'html_content' in clone_fields:
            ready_instance.html_content = self.html_content
        if not clone_fields or 'slug' in clone_fields:
            ready_instance.slug = self.slug
        if not clone_fields or 'index' in clone_fields:
            ready_instance.index = self.index
        if not clone_fields or 'due_date' in clone_fields:
            ready_instance.due_date = self.due_date
        if not clone_fields or 'grace_period' in clone_fields:
            ready_instance.grace_period = self.grace_period
        if not clone_fields or 'total_score' in clone_fields:
            ready_instance.total_score = self.total_score
        if not clone_fields or 'exam_type' in clone_fields:
            ready_instance.exam_type = self.exam_type
        if not clone_fields or 'live_datetime' in clone_fields:
            ready_instance.live_datetime = self.live_datetime
        if not clone_fields or 'xml_metadata' in clone_fields:
            ready_instance.xml_metadata = self.xml_metadata
        if not clone_fields or 'xml_imported' in clone_fields:
            ready_instance.xml_imported = self.xml_imported
        if not clone_fields or 'partial_credit_deadline' in clone_fields:
            ready_instance.partial_credit_deadline = self.partial_credit_deadline
        if not clone_fields or 'late_penalty' in clone_fields:
            ready_instance.late_penalty = self.late_penalty
        if not clone_fields or 'submissions_permitted' in clone_fields:
            ready_instance.submissions_permitted = self.submissions_permitted
        if not clone_fields or 'resubmission_penalty' in clone_fields:
            ready_instance.resubmission_penalty = self.resubmission_penalty
        if not clone_fields or 'autograde' in clone_fields:
            ready_instance.autograde = self.autograde
        if not clone_fields or 'display_single' in clone_fields:
            ready_instance.display_single = self.display_single
        if not clone_fields or 'grade_single' in clone_fields:
            ready_instance.grade_single = self.grade_single
        if not clone_fields or 'invideo' in clone_fields:
            ready_instance.invideo = self.invideo
        if not clone_fields or 'timed' in clone_fields:
            ready_instance.timed = self.timed
        if not clone_fields or 'minutesallowed' in clone_fields:
            ready_instance.minutesallowed = self.minutesallowed
        if not clone_fields or 'minutes_btw_attempts' in clone_fields:
            ready_instance.minutes_btw_attempts = self.minutes_btw_attempts
        if not clone_fields or 'assessment_type' in clone_fields:
            ready_instance.assessment_type = self.assessment_type
        
        ready_instance.save()
    
    def revert(self, clone_fields = None):
        if self.mode != 'draft': return;

        ready_instance = self.image
        if not clone_fields or 'section' in clone_fields:
            self.section = ready_instance.section.image        
        if not clone_fields or 'title' in clone_fields:
            self.title = ready_instance.title
        if not clone_fields or 'description' in clone_fields:
            self.description = ready_instance.description            
        if not clone_fields or 'html_content' in clone_fields:
            self.html_content = ready_instance.html_content
        if not clone_fields or 'slug' in clone_fields:
            self.slug = ready_instance.slug
        if not clone_fields or 'index' in clone_fields:
            self.index = ready_instance.index
        if not clone_fields or 'due_date' in clone_fields:
            self.due_date = ready_instance.due_date
        if not clone_fields or 'grace_period' in clone_fields:
            self.grace_period = ready_instance.grace_period
        if not clone_fields or 'total_score' in clone_fields:
            self.total_score = ready_instance.total_score
        if not clone_fields or 'exam_type' in clone_fields:
            self.exam_type = ready_instance.exam_type
        if not clone_fields or 'live_datetime' in clone_fields:
            self.live_datetime = ready_instance.live_datetime
        if not clone_fields or 'xml_metadata' in clone_fields:
            self.xml_metadata = ready_instance.xml_metadata 
        if not clone_fields or 'xml_imported' in clone_fields:
            self.xml_imported = ready_instance.xml_imported
        if not clone_fields or 'partial_credit_deadline' in clone_fields:
            self.partial_credit_deadline = ready_instance.partial_credit_deadline 
        if not clone_fields or 'late_penalty' in clone_fields:
            self.late_penalty = ready_instance.late_penalty 
        if not clone_fields or 'submissions_permitted' in clone_fields:
            self.submissions_permitted = ready_instance.submissions_permitted 
        if not clone_fields or 'resubmission_penalty' in clone_fields:
            self.resubmission_penalty = ready_instance.resubmission_penalty 
        if not clone_fields or 'autograde' in clone_fields:
            self.autograde = ready_instance.autograde 
        if not clone_fields or 'display_single' in clone_fields:
            self.display_single = ready_instance.display_single 
        if not clone_fields or 'grade_single' in clone_fields:
            self.grade_single = ready_instance.grade_single
        if not clone_fields or 'invideo' in clone_fields:
            self.invideo = ready_instance.invideo 
        if not clone_fields or 'timed' in clone_fields:
            self.timed = ready_instance.timed 
        if not clone_fields or 'minutesallowed' in clone_fields:
            self.minutesallowed = ready_instance.minutesallowed
        if not clone_fields or 'minutes_btw_attempts' in clone_fields:
            self.minutes_btw_attempts = ready_instance.minutes_btw_attempts
        if not clone_fields or 'assessment_type' in clone_fields:
            self.assessment_type = ready_instance.assessment_type

        self.save()
    
    def is_synced(self):
        if not self.image:
            return False        
        prod_instance = self.image
        if self.section != prod_instance.section.image:
            return False
        if self.title != prod_instance.title:
            return False
        if self.description != prod_instance.description:
            return False
        if self.html_content != self.image.html_content:
            return False
        if self.slug != self.image.slug:
            return False
        if self.index != self.image.index:
            return False
        if self.due_date != self.image.due_date:
            return False
        if self.grace_period != self.image.grace_period:
            return False
        if self.total_score != self.image.total_score:
            return False
        if self.exam_type != self.image.exam_type:
            return False
        if self.live_datetime != self.image.live_datetime:
            return False
        if self.xml_metadata != self.image.xml_metadata:
            return False
        if self.xml_imported != self.image.xml_imported:
            return False
        if self.partial_credit_deadline != self.image.partial_credit_deadline:
            return False
        if self.late_penalty != self.image.late_penalty:
            return False
        if self.submissions_permitted != self.image.submissions_permitted:
            return False
        if self.resubmission_penalty != self.image.resubmission_penalty:
            return False
        if self.autograde != self.image.autograde:
            return False
        if self.display_single != self.image.display_single:
            return False
        if self.grade_single != self.image.grade_single:
            return False
        if self.invideo != self.image.invideo:
            return False
        if self.timed != self.image.timed:
            return False
        if self.minutesallowed != self.image.minutesallowed:
            return False
        if self.minutes_btw_attempts != self.image.minutes_btw_attempts:
            return False
        if self.assessment_type != self.image.assessment_type:
            return False
        return True

    def delete(self):
        """Do housekeeping on related Videos before calling up."""
        my_videos = self.video_set.all()
        for vid in my_videos:
            if vid.exam_id == self.id:
                vid.exam = None
                vid.save()
        super(Exam, self).delete()
    
    def safe_exam_type(self):
        if self.exam_type not in [li[0] for li in self.EXAM_TYPE_CHOICES]:
            return "exam"
        return self.exam_type
    
    def show_view_name(self):
        return self.safe_exam_type()+"_show"

    show_view = property(show_view_name)
    
    def list_view_name(self):
        return self.safe_exam_type()+"_list"

    list_view = property(list_view_name)

    def populated_view_name(self):
        return self.safe_exam_type()+"_populated"
    
    populated_view = property(populated_view_name)
        
    def graded_view_name(self):
        return self.safe_exam_type()+"_graded"

    graded_view = property(graded_view_name)

    def my_submissions_view_name(self):
        return self.safe_exam_type()+"_my_submissions"
    
    my_submissions_view = property(my_submissions_view_name)

    def record_view_name(self):
        return self.safe_exam_type()+"_record"

    def get_human_type(self):
        return self.Exam_HUMAN_TYPES[self.safe_exam_type()]

    def get_url(self):
        #return '/' + self.course.handle.replace('--', '/') + '/surveys/' + self.slug
        return reverse(self.show_view, args=[self.course.prefix, self.course.suffix, self.slug])
    
    def has_child_exams(self):
        return ContentGroup.has_children(self, types=['exam'])
    
    def is_child(self):
        return ContentGroup.is_child(self)
    
    record_view = property(record_view_name)

    def sync_videos_foreignkeys_with_metadata(self):
        """ 
            This will read self.xml_metadata and synchronize the foreignkey
            relationships in the database with those described in the xml_metadata.
            WHAT TO DO ABOUT PUBLICATION MODEL. WE ARE IGNORING IT FOR NOW, SO
            WILL HAVE TO CALL SEPARATELY FOR THE IMAGE.
        """
        #Clear out the old assocations first
        prev_videos = self.video_set.all()
        for video in prev_videos:
            video.exam = None
            video.save()
                
        new_video_slugs = videos_in_exam_metadata(self.xml_metadata)['video_slugs']
        new_videos = Video.objects.filter(course=self.course, mode=self.mode, is_deleted=False, slug__in=new_video_slugs)
        for new_video in new_videos:
            new_video.exam = self
            new_video.save()

        video_slugs_set = map(lambda li:li.slug, list(new_videos))
        video_slugs_not_set = list(set(new_video_slugs)-(set(video_slugs_set)))
    
        return {'video_slugs_set':video_slugs_set, 'video_slugs_not_set':video_slugs_not_set}
    
    def __unicode__(self):
        return self.title + " | Mode: " + self.mode

def videos_in_exam_metadata(xml, times_for_video_slug=None):
    """
        Refactored code that parses exam_metadata for video associations.
        'question_times' only gets populated in the returned dict if a
        times_for_video_slug argument is specified.
    """
    metadata_dom = parseString(encoding.smart_str(xml, encoding='utf-8')) #The DOM corresponding to the XML metadata
    video_questions = metadata_dom.getElementsByTagName('video')
    
    question_times = {}
    video_slugs = []
    for video_node in video_questions:
        video_slug = video_node.getAttribute("url-identifier")
        if video_slug == "":
            video_slug = video_node.getAttribute("url_identifier")
        video_slugs = video_slugs + [video_slug]
        if video_slug == times_for_video_slug:
            question_children = video_node.getElementsByTagName("question")
            times = []
            for question in question_children:
                time = "sec_%s" % question.getAttribute("time")
                if time not in question_times:
                    question_times[time] = []
                question_times[time].append(question.getAttribute("id"))
    
    return {'dom':metadata_dom, 'questions':video_questions,
        'video_slugs':video_slugs, 'question_times':question_times}

def parse_video_exam_metadata(xml):
    """
        Helper function to parse the exam metadata for associated videos.
        Returns the response string detailing the videos found.
        Should also return a list of slugs
    """
    videos_obj = videos_in_exam_metadata(xml)
    if videos_obj['video_slugs']:
        video_times = {}
        for slug in videos_obj['video_slugs']:
            v1 = videos_in_exam_metadata(xml, times_for_video_slug=slug)
            video_times[slug]=v1['question_times']
        
        video_return_string = "This exam will be associated with the following videos:\n"
        for slug,times in video_times.iteritems():
            video_return_string += slug + " with questions at times " + \
                ",".join(list(times.iterkeys())) + "\n"
    else:
        video_return_string = ""
    
    return {'description':video_return_string, 'slug_list':videos_obj['video_slugs']}

class ExamRecord(TimestampMixin, models.Model):
    course = models.ForeignKey(Course, db_index=True)
    exam = models.ForeignKey(Exam, db_index=True)
    student = models.ForeignKey(User, db_index=True)
    json_data = models.TextField(null=True, blank=True)   #blob
    json_score_data = models.TextField(null=True, blank=True)  #blob
    attempt_number = models.IntegerField(default=0)
    complete = models.BooleanField(default=True)
    late = models.BooleanField(default=False)
    score = models.FloatField(null=True, blank=True)
    onpage = models.CharField(max_length=512, null=True, blank=True) #this is the URL in the nav-bar of the page
    
    def __unicode__(self):
        return (self.student.username + ":" + self.course.title + ":" + self.exam.title)
    
class Instructor(TimestampMixin, models.Model):
    name = models.TextField(blank=True)
    email = models.TextField(blank=True)
    biography = models.TextField(blank=True)
    photo = models.FileField(upload_to=get_file_path, blank=True)
    handle = models.CharField(max_length=255, null=True, db_index=True)
    
    def photo_dl_link(self):
        if not self.photo.storage.exists(self.photo.name):
            return ""
        
        url = self.photo.storage.url(self.photo.name)
        return url
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        db_table = u'c2g_instructor'

class GetCourseInstructorByCourse(models.Manager):
    def getByCourse(self, course):
        return self.filter(course=course)


class CourseInstructor(TimestampMixin,  models.Model):
    course = models.ForeignKey(Course)
    instructor = models.ForeignKey(Instructor)
    objects = GetCourseInstructorByCourse()
        
    def __unicode__(self):
        return self.course.title + "-" + self.instructor.name
    
    class Meta:
        db_table = u'c2g_course_instructor'
                

class ExamScore(TimestampMixin, models.Model):
    """
    This class is meant to be the top level, authoritative score of each exam.  
    It should have a one-to-one relationship with the (exam, student) pair
    """
    course = models.ForeignKey(Course, db_index=True) #mainly for convenience
    exam = models.ForeignKey(Exam, db_index=True)
    student = models.ForeignKey(User, db_index=True)
    score = models.FloatField(null=True, blank=True) #this is the score over the whole exam, with penalities applied
    csv_imported = models.BooleanField(default=False)
    #can have subscores corresponding to these, of type ExamScoreField.  Creating new class to do notion of list.
    #TODO: Add ForeignKey to which ExamRecord is responsible for this score, per GHI #2029
    
    def __unicode__(self):
        return (self.student.username + ":" + self.course.title + ":" + self.exam.title + ":" + str(self.score))

    class Meta:
        unique_together = ("exam", "student")
        
    def setScore(self):
        #Set score to max of ExamRecordScore.score for this exam, student
        exam_records = ExamRecord.objects.values('student').filter(exam=self.exam, student=self.student, complete=1).annotate(max_score=Max('score'))
        
        if exam_records:
            self.score = exam_records[0]['max_score']
            self.save()        

# Deprecated
class ExamScoreField(TimestampMixin, models.Model):
    """Should be kept basically identical to ExamRecordScoreField"""
    parent = models.ForeignKey(ExamScore, db_index=True)
    field_name = models.CharField(max_length=128, db_index=True)
    human_name = models.CharField(max_length=128, db_index=True, null=True, blank=True)
    value = models.CharField(max_length=128, null=True, blank=True)
    correct = models.NullBooleanField()
    subscore = models.FloatField(default=0)
    comments = models.TextField(null=True, blank=True)
    associated_text = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return (self.parent.student.username + ":" + self.parent.course.title + ":" + self.parent.exam.title + ":" + self.human_name)

	

class ExamRecordScore(TimestampMixin, models.Model):
    """
    Making a separate DB table to keep scores associated with each record.
    Currently for CSV-graded exams this does not get created since there are too many DB operations
    One of these can be "promoted" -- i.e. copied into ExamScore to be the official score
       **TODO: Write Promote as a function in the model**
    """
    record = models.OneToOneField(ExamRecord, db_index=True)
    raw_score = models.FloatField(null=True, blank=True) # this is the raw score of the entire record
    csv_imported = models.BooleanField(default=False)
    #subscores are in ExamRecordScoreField
    
    def __unicode__(self):
        return (self.record.student.username + ":" + self.record.course.title + ":" + self.record.exam.title + ":" + str(self.raw_score))


class ExamRecordScoreField(TimestampMixin, models.Model):
    """Should be kept basically identical to ExamScoreField."""
    parent = models.ForeignKey(ExamRecordScore, db_index=True)
    field_name = models.CharField(max_length=128, db_index=True)
    human_name = models.CharField(max_length=128, db_index=True, null=True, blank=True)
    value = models.TextField(null=True, blank=True)
    correct = models.NullBooleanField()
    subscore = models.FloatField(default=0)
    comments = models.TextField(null=True, blank=True)
    associated_text = models.TextField(null=True, blank=True)
    def __unicode__(self):
        return (self.parent.record.student.username + ":" + self.parent.record.course.title + ":" + self.parent.record.exam.title + ":" + self.human_name)

class ExamRecordFieldLog(TimestampMixin, models.Model):
    """Log oriented table recording activity for each submission of each field."""
    course = models.ForeignKey(Course, db_index=True)
    exam = models.ForeignKey(Exam, db_index=True)
    student = models.ForeignKey(User, db_index=True)
    field_name = models.CharField(max_length=128, db_index=True)
    human_name = models.CharField(max_length=128, db_index=True, null=True, blank=True)
    value = models.TextField(null=True, blank=True)
    raw_score = models.FloatField(default=0, blank=True)
    max_score = models.FloatField(default=0, blank=True)  # info only, for interactive 
    def __unicode__(self):
        return (self.parent.record.student.username + ":" + self.parent.record.course.title + ":" + self.parent.record.exam.title + ":" + self.human_name)

class ExamRecordScoreFieldChoice(TimestampMixin, models.Model):
    """Exploding out even multiple choice answers"""
    parent = models.ForeignKey(ExamRecordScoreField, db_index=True)
    choice_value = models.CharField(max_length=128, db_index=True)
    human_name = models.CharField(max_length=128, db_index=True, null=True, blank=True)
    correct = models.NullBooleanField()
    associated_text = models.TextField(null=True, blank=True)
    def __unicode__(self):
        return (self.parent.parent.record.student.username + ":" + self.parent.parent.record.course.title + ":" \
                + self.parent.parent.record.exam.title + ":" + self.parent.human_name + ":" + self.human_name)

class CurrentTermMap(TimestampMixin, models.Model):
    course_prefix = models.CharField(max_length=64, unique=True, db_index=True)
    course_suffix = models.CharField(max_length=64)
    def __unicode__(self):
        return (self.course_prefix + "--" + self.course_suffix)

class StudentExamStart(TimestampMixin, models.Model):
    student = models.ForeignKey(User)
    exam = models.ForeignKey(Exam)


class ContentGroupManager(models.Manager):
    def getByCourse(self, course):
        return self.filter(course=course).order_by('group_id','level')

    def getByFieldnameAndId(self, fieldname, fieldid):
        """Use the type tag (video, etc.) and id to dereference an entry.
        
        Returns the ContentGroup entry for this item."""
        # TODO: cache this
        this = ContentGroup.groupable_types[fieldname].objects.get(id=fieldid)
        retset = this.contentgroup_set.get()
        if len(retset) == 1:
            return retset[0]
        else: return retset

    def getChildrenByGroupId(self, group_id):
        return self.filter(level=2, group_id=group_id).order_by('display_style')

class ContentGroup(models.Model):
    group_id        = models.IntegerField(db_index=True, null=True, blank=True)
    level           = models.IntegerField(db_index=True)
    display_style   = models.CharField(max_length=32, default='list', blank=True)

    additional_page = models.ForeignKey(AdditionalPage, null=True, blank=True)
    course          = models.ForeignKey(Course)
    exam            = models.ForeignKey(Exam, null=True, blank=True)
    file            = models.ForeignKey(File, null=True, blank=True)
    problemSet      = models.ForeignKey(ProblemSet, null=True, blank=True)
    video           = models.ForeignKey(Video, null=True, blank=True)

    objects         = ContentGroupManager()

               # ContentGroup field name: model class name
    groupable_types = { 
                       'video':           Video,
                       'problemSet':      ProblemSet,
                       'additional_page': AdditionalPage, 
                       'file':            File,
                       'exam':            Exam,
                      }

    @classmethod
    def groupinfo_by_id(thisclass, tag, id):
        """Reverse-lookup the members of a group by the object id of a member.
        
        nota bene:
        O(n**2) for # of items in a group. n should be tiny, but be wary.
        OTOH, if ContentGroup.get_content_type becomes constant-time, this
        becomes linear, and then we win.
        """
        info = {'__parent': None, '__parent_tag': '', '__children': [], '__group_id': None, }
        cls = thisclass.groupable_types.get(tag, False)
        if not cls:
            return info
        obj = cls.objects.get(id=id)

        try:
            cgobjs = ContentGroup.objects.filter(group_id=obj.contentgroup_set.get().group_id)
        except ContentGroup.DoesNotExist:
            return {}
        info['__group_id'] = cgobjs[0].group_id
        for cgo in cgobjs:
            cttag = cgo.get_content_type()
            cgref = getattr(cgo, cttag)
            if not cttag or not cgref:
                continue
            if cgo.level == 1:
                info['__parent'] = cgref
                info['__parent_tag'] = cttag
            else:
                info['__children'].append(cgref)
            if info.has_key(cttag):
                info[cttag].append(cgref)
            else:
                info[cttag] = [cgref]
        return info

    @classmethod
    def reassign_parent_child_sections(thisclass, tag, id, new_section_id):
        """When updating parent's content section, make children follow it."""
        def do_content_section_update(obj, new_section_ref):
            # NB: ContentGroup objects are all ready-mode instances of a thing.
            obj.section = new_section_ref
            obj.save()
            if hasattr(obj, 'image'):
                if new_section_ref != None:      # can't take .image() of None
                    obj.image.section = new_section_ref.image
                else:
                    obj.image.section = new_section_ref
                obj.image.save()
        group_parent = None
        cginfo = thisclass.groupinfo_by_id(tag, id)
        if new_section_id == "null":
            new_section_ref = None
        else:
            new_section_ref = ContentSection.objects.get(id=new_section_id)
        if new_section_ref and new_section_ref.mode != "ready":
            new_section_ref = new_section_ref.image
        # * Get the parent information if it's available...
        group_parent = cginfo['__parent']
        # * ...but if it's not, this call should no-op
        if not group_parent:
            return False
        # * If this CG is already in new_section, this call should no-op
        if group_parent.section and new_section_ref and new_section_ref.id == group_parent.section.id:
            return False
        # * Otherwise "normal" case of group w/ parents and children getting moved
        do_content_section_update(group_parent, new_section_ref)
        for child in cginfo['__children']:
            do_content_section_update(child, new_section_ref)
        return True

    @classmethod
    def add_child(thisclass, group_id, tag, obj_ref, display_style='list'):
        """Add obj_ref having type tag to the ContentGroup table.

        Returns the ContentGroup entry id for the resulting child item.

        If group_id doesn't correspond to an existing ContentGroup.group_id, raises ValueError
        If entry isn't in the table, create it and add it
        If entry is in the table as a parent of the given group_id, demote it
        If entry is in the table as a child of a different group, move it to this group.

        display_style determines how the child items should be rendered with
        their parent; 'button' is the default.
        """
        # Technically there's no reason to restrict the ContentGroups
        # to two levels of hierarchy, but the UI design is harder for
        # more level (and as of this iteration the spec says two)
        if tag not in thisclass.groupable_types.keys():
            raise ValueError, "ContentGroup "+str(tag)+" an invalid object type tag."
        content_group = ContentGroup.objects.filter(group_id=group_id)
        if not content_group:
            raise ValueError, "ContentGroup "+str(group_id)+" does not exist."
        cgref = obj_ref.contentgroup_set.all()
        if not cgref:
            # it's not in the table, so add it
            new_item = ContentGroup(course=content_group[0].course, level=2, group_id=group_id, display_style=display_style)
            setattr(new_item, tag, obj_ref)
            new_item.save()
            return new_item.id
        else:
            cgref = cgref[0]
            # it is in the table, so do something reasonable:
            for entry in content_group:
                if getattr(entry, tag, False) == obj_ref:
                    # If this child is in this group already, return this group
                    if entry.level == 1:
                        # It is an error to make a parent into a child of its own group
                        # Instead, make a new group, then reassign_membership 
                        raise ValueError, "ContentGroup "+str(entry.id)+" is the parent of group "+str(group_id)
                    entry.display_style = display_style
                    entry.save()
                    return entry.id
            # We have a reference to it, but it's not in content_group, so reassign it
            if content_group and cgref:
                new_group_id = thisclass.reassign_membership(cgref, content_group.get(level=1))
            return new_group_id

    @classmethod
    def reassign_membership(thisclass, contentgroup, new_parent_cg):
        """Reassign a ContentGroup entry from its current parent to another.

        If a parent is reassigned in this way, also reassign all of its child
        items.

        Arguments:
        contentgroup: the ContentGroup entry to be made into a child
        new_parent_cg: the ContentGroup entry to which parent_cg should be reassigned

        Returns:
        new_parent_cg.group_id
        """
        new_group_id = new_parent_cg.group_id
        if contentgroup.level == 2:
            contentgroup.group_id = new_parent_cg.group_id
            contentgroup.save()
        else:
            children = ContentGroup.objects.filter(level=2, group_id=contentgroup.group_id)
            contentgroup.group_id = new_group_id
            contentgroup.level = 2
            for child in children:
                child.group_id = new_group_id
                child.save()
            contentgroup.save()
        return new_group_id

    @classmethod
    def add_parent(thisclass, course_ref, tag, obj_ref):
        """Add obj_ref having type tag to the ContentGroup table.

        Returns a group_id of the resulting ContentGroup.
        Note that this is the same as the parent object's ContentGroup id.

        If it is already a parent of a ContentGroup, just return
        If it is nonexistent in ContentGroup, create it as a parent
        If it is already a child in a group with no parent, promote it
        If it is a child in a group that has a parent, promote it, creating a
            new group
        """
        cgref    = None
        if tag not in thisclass.groupable_types.keys():
            raise ValueError, "ContentGroup "+str(tag)+" an invalid object type tag."
        try:
            cgref = obj_ref.contentgroup_set.get()
        except ContentGroup.DoesNotExist:
            new_item = ContentGroup(course=course_ref, level=1)
            new_item.save()
            setattr(new_item, tag, obj_ref)
            new_item.group_id = new_item.id
            new_item.save()
            return new_item.group_id
        else:
            for cgo in ContentGroup.objects.filter(group_id=cgref.group_id):
                if cgo.level == 1: 
                    if getattr(cgo, tag, None) == obj_ref:
                        # This happens when this item is already the parent of its group
                        return cgref.group_id
                    else:
                        # This happens when this item is already a child in a
                        # group with a different parent (promote it, creating a new group)
                        cgref.group_id = cgref.id
                        cgref.level = 1
                        cgref.save()
                        return cgref.group_id
            # This happens when this item is already a child in a group with no parent
            cgref.level = 1
            cgref.save()
            for cgo in ContentGroup.objects.filter(group_id=cgref.group_id):
                cgo.group_id = cgref.id
                cgo.save()
            return cgref.group_id

    @classmethod
    def get_level2_tag_sorted(cls):
        info = {}
        l2cgobjs = ContentGroup.objects.filter(level=2)
        for l2o in l2cgobjs:
            l2o_type = l2o.get_content_type()
            info.setdefault(l2o_type, []).append(getattr(l2o, l2o_type).id)
        return info

    def delete(self):
        """Do housekeeping on related ContentGroup entries before calling up
        
        Level 2 ContentGroup entries are deleted without side effects.
        Level 1 ContentGroup entries promote all of their children to Level 1,
                making each its own group parent.
        """
        if self.level == 1:
            children = ContentGroup.objects.getChildrenByGroupId(self.group_id)
            for child in children:
                child.level = 1
                child.group_id = child.id
                child.save()
        super(ContentGroup, self).delete()

    def get_content(self):
        """Return the object to which this ContentGroup entry refers"""
        tag = self.get_content_type()
        return getattr(self, tag)

    def get_content_id(self):
        """Return the id of the object to which this ContentGroup entry refers"""
        for keyword in ContentGroup.groupable_types.keys():
            tmp = getattr(self, keyword+'_id', False)
            if tmp:
                return tmp
        return None

    def get_content_type(self):
        """This is linear in the number of content types supported for grouping
        
        TODO: Replace with a column lookup storing our type explicitly? Not
              nice to store the same information twice, but constant time
              lookups are awfully nice...
              Compromise is to use django cache table
        """
        for keyword in ContentGroup.groupable_types.keys():
            if getattr(self, keyword+'_id', False):
                return keyword
        return None
    
    
    @classmethod
    def get_tag_from_classname(thisclass, classname):
        """Reverse dictionary lookup.  Obviously O(n)"""
        for keyword in ContentGroup.groupable_types.keys():
            if ContentGroup.groupable_types[keyword]==classname:
                return keyword
        return None

    
    @classmethod
    def has_children(thisclass, obj, types=list(groupable_types.keys())):
        """
            Does obj (File, Exam, etc) have children?  types is a kwarg that
            restricts the search to the types in the argument of type list.  
            Will return true if any children of type found in types exist.
            
        """
        groupinfo = thisclass.groupinfo_by_id(thisclass.get_tag_from_classname(obj.__class__), obj.id)
        if not groupinfo:
            return False
        if obj != groupinfo.get('__parent', None): #can't have children if obj itself is a child (for now)
            return False
        for t in types:
            if filter(lambda li: li != obj, groupinfo.get(t, [])):
                return True
        return False

    
    @classmethod
    def is_child(thisclass, obj):
        """ Is obj a child? """
        return obj.contentgroup_set.all().filter(level=2).exists()
    
    def __repr__(self):
        s = "ContentGroup(group_id=" + str(self.group_id) + ", "
        s += 'course=' + str(self.course.id) + ', ' 
        s += 'level=' + str(self.level)
        for keyword in ContentGroup.groupable_types.keys():
            ref = getattr(self, keyword, '')
            if not ref or ref == "None":
                continue
            s += ', ' + keyword+'=<' + str(ref.id) + '>'
        return s+')'

    def __unicode__(self):
        level_string = "parent" if self.level==1 else "child"
        return "%s:%s:%s" % (level_string, self.get_content_type(), self.get_content().title)
    
    class Meta:
        db_table = u'c2g_content_group'
        


