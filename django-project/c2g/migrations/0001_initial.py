# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Institution'
        db.create_table(u'institutions', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.TextField')()),
            ('country', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('city', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('domains', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['Institution'])

        # Adding model 'Course'
        db.create_table(u'courses', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Institution'])),
            ('code', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=511, null=True, blank=True)),
            ('listing_description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('mode', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('staff_emails', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('term', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('year', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('calendar_start', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('calendar_end', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('meeting_info', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('feature_settings', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('membership_control', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('join_password', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('list_publicly', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['Course'])

        # Adding M2M table for field instructors on 'Course'
        db.create_table(u'courses_instructors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm['c2g.course'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique(u'courses_instructors', ['course_id', 'user_id'])

        # Adding M2M table for field tas on 'Course'
        db.create_table(u'courses_tas', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm['c2g.course'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique(u'courses_tas', ['course_id', 'user_id'])

        # Adding M2M table for field readonly_tas on 'Course'
        db.create_table(u'courses_readonly_tas', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm['c2g.course'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique(u'courses_readonly_tas', ['course_id', 'user_id'])

        # Adding model 'AdditionalPage'
        db.create_table(u'additional_pages', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Course'])),
            ('access_id', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('write_access', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=511, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('update_log', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['AdditionalPage'])

        # Adding model 'Announcement'
        db.create_table(u'announcements', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Course'])),
            ('access_id', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=511, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['Announcement'])

        # Adding model 'AssignmentCategory'
        db.create_table(u'assignment_categories', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Course'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=511, null=True, blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['AssignmentCategory'])

        # Adding model 'Assignment'
        db.create_table(u'assignments', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Course'])),
            ('category_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.AssignmentCategory'])),
            ('access_id', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=511, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('due_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('close_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['Assignment'])

        # Adding model 'AssignmentGrade'
        db.create_table(u'assignment_grades', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('assignment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Assignment'])),
            ('json', self.gf('django.db.models.fields.TextField')()),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['AssignmentGrade'])

        # Adding model 'AssignmentSubmission'
        db.create_table(u'assignment_submissions', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('assignment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Assignment'])),
            ('json', self.gf('django.db.models.fields.TextField')()),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['AssignmentSubmission'])

        # Adding model 'CourseAnalytics'
        db.create_table(u'course_analytics', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Course'])),
            ('json', self.gf('django.db.models.fields.TextField')()),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['CourseAnalytics'])

        # Adding model 'CourseMap'
        db.create_table(u'course_maps', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Course'])),
            ('json', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['CourseMap'])

        # Adding model 'File'
        db.create_table(u'files', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Course'])),
            ('access_id', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=511, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['File'])

        # Adding model 'Lecture'
        db.create_table(u'lectures', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Course'])),
            ('access_id', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=511, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('calendar_start', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('calendar_end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['Lecture'])

        # Adding model 'Officehour'
        db.create_table(u'officehours', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Course'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=511, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('calendar_start', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('calendar_end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['Officehour'])

        # Adding model 'StudentSection'
        db.create_table(u'sections', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Course'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=511, null=True, blank=True)),
            ('capacity', self.gf('django.db.models.fields.IntegerField')(default=999)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['StudentSection'])

        # Adding M2M table for field members on 'StudentSection'
        db.create_table(u'sections_members', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('studentsection', models.ForeignKey(orm['c2g.studentsection'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique(u'sections_members', ['studentsection_id', 'user_id'])

        # Adding model 'UserCourseData'
        db.create_table(u'user_course_data', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Course'])),
            ('json', self.gf('django.db.models.fields.TextField')()),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['UserCourseData'])

        # Adding model 'UserProfile'
        db.create_table(u'user_profiles', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('is_instructor', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('site_data', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('c2g', ['UserProfile'])

        # Adding model 'VideoTopic'
        db.create_table(u'video_topics', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Course'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['VideoTopic'])

        # Adding model 'Video'
        db.create_table(u'videos', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Course'])),
            ('topic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.VideoTopic'], null=True)),
            ('access_id', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=511, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['Video'])

        # Adding model 'VideoQuiz'
        db.create_table(u'video_quizzes', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Video'])),
            ('json', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['VideoQuiz'])

        # Adding model 'VideoQuizQuestion'
        db.create_table(u'video_quiz_questions', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('video_quiz', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.VideoQuiz'])),
            ('time_in_video', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=511, null=True, blank=True)),
            ('json', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('c2g', ['VideoQuizQuestion'])

        # Adding model 'VideoQuizSubmission'
        db.create_table(u'video_quiz_submissions', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.VideoQuizQuestion'])),
            ('time_in_video', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('video_metadata', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('json', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['VideoQuizSubmission'])

        # Adding model 'VideoAnnotations'
        db.create_table(u'video_annotations', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Video'])),
            ('time_in_video', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=511, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['VideoAnnotations'])

        # Adding model 'Roles'
        db.create_table(u'roles', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Course'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=765)),
            ('is_staff', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('privileges', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('holder_ids', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('holder_count', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['Roles'])

        # Adding model 'SharingPermissions'
        db.create_table(u'sharing_permissions', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('object_id', self.gf('django.db.models.fields.BigIntegerField')(db_index=True)),
            ('type', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('licensee_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('cond_by', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('cond_nc', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('cond_nd', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('cond_sa', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['SharingPermissions'])


    def backwards(self, orm):
        # Deleting model 'Institution'
        db.delete_table(u'institutions')

        # Deleting model 'Course'
        db.delete_table(u'courses')

        # Removing M2M table for field instructors on 'Course'
        db.delete_table('courses_instructors')

        # Removing M2M table for field tas on 'Course'
        db.delete_table('courses_tas')

        # Removing M2M table for field readonly_tas on 'Course'
        db.delete_table('courses_readonly_tas')

        # Deleting model 'AdditionalPage'
        db.delete_table(u'additional_pages')

        # Deleting model 'Announcement'
        db.delete_table(u'announcements')

        # Deleting model 'AssignmentCategory'
        db.delete_table(u'assignment_categories')

        # Deleting model 'Assignment'
        db.delete_table(u'assignments')

        # Deleting model 'AssignmentGrade'
        db.delete_table(u'assignment_grades')

        # Deleting model 'AssignmentSubmission'
        db.delete_table(u'assignment_submissions')

        # Deleting model 'CourseAnalytics'
        db.delete_table(u'course_analytics')

        # Deleting model 'CourseMap'
        db.delete_table(u'course_maps')

        # Deleting model 'File'
        db.delete_table(u'files')

        # Deleting model 'Lecture'
        db.delete_table(u'lectures')

        # Deleting model 'Officehour'
        db.delete_table(u'officehours')

        # Deleting model 'StudentSection'
        db.delete_table(u'sections')

        # Removing M2M table for field members on 'StudentSection'
        db.delete_table('sections_members')

        # Deleting model 'UserCourseData'
        db.delete_table(u'user_course_data')

        # Deleting model 'UserProfile'
        db.delete_table(u'user_profiles')

        # Deleting model 'VideoTopic'
        db.delete_table(u'video_topics')

        # Deleting model 'Video'
        db.delete_table(u'videos')

        # Deleting model 'VideoQuiz'
        db.delete_table(u'video_quizzes')

        # Deleting model 'VideoQuizQuestion'
        db.delete_table(u'video_quiz_questions')

        # Deleting model 'VideoQuizSubmission'
        db.delete_table(u'video_quiz_submissions')

        # Deleting model 'VideoAnnotations'
        db.delete_table(u'video_annotations')

        # Deleting model 'Roles'
        db.delete_table(u'roles')

        # Deleting model 'SharingPermissions'
        db.delete_table(u'sharing_permissions')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'c2g.additionalpage': {
            'Meta': {'object_name': 'AdditionalPage', 'db_table': "u'additional_pages'"},
            'access_id': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '511', 'null': 'True', 'blank': 'True'}),
            'update_log': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'write_access': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'c2g.announcement': {
            'Meta': {'object_name': 'Announcement', 'db_table': "u'announcements'"},
            'access_id': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '511', 'null': 'True', 'blank': 'True'})
        },
        'c2g.assignment': {
            'Meta': {'object_name': 'Assignment', 'db_table': "u'assignments'"},
            'access_id': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'category_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.AssignmentCategory']"}),
            'close_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'due_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '511', 'null': 'True', 'blank': 'True'})
        },
        'c2g.assignmentcategory': {
            'Meta': {'object_name': 'AssignmentCategory', 'db_table': "u'assignment_categories'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '511', 'null': 'True', 'blank': 'True'})
        },
        'c2g.assignmentgrade': {
            'Meta': {'object_name': 'AssignmentGrade', 'db_table': "u'assignment_grades'"},
            'assignment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Assignment']"}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'json': ('django.db.models.fields.TextField', [], {}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'c2g.assignmentsubmission': {
            'Meta': {'object_name': 'AssignmentSubmission', 'db_table': "u'assignment_submissions'"},
            'assignment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Assignment']"}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'json': ('django.db.models.fields.TextField', [], {}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'c2g.course': {
            'Meta': {'object_name': 'Course', 'db_table': "u'courses'"},
            'calendar_end': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'calendar_start': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'feature_settings': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Institution']"}),
            'instructors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'instructors'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'join_password': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'list_publicly': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'listing_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'meeting_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'membership_control': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'mode': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'readonly_tas': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'readonly_tas'", 'null': 'True', 'to': "orm['auth.User']"}),
            'staff_emails': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tas': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'tas'", 'null': 'True', 'to': "orm['auth.User']"}),
            'term': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '511', 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'c2g.courseanalytics': {
            'Meta': {'object_name': 'CourseAnalytics', 'db_table': "u'course_analytics'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'json': ('django.db.models.fields.TextField', [], {}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'c2g.coursemap': {
            'Meta': {'object_name': 'CourseMap', 'db_table': "u'course_maps'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'json': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'c2g.file': {
            'Meta': {'object_name': 'File', 'db_table': "u'files'"},
            'access_id': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '511', 'null': 'True', 'blank': 'True'})
        },
        'c2g.institution': {
            'Meta': {'object_name': 'Institution', 'db_table': "u'institutions'"},
            'city': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'country': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'domains': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {})
        },
        'c2g.lecture': {
            'Meta': {'object_name': 'Lecture', 'db_table': "u'lectures'"},
            'access_id': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'calendar_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'calendar_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '511', 'null': 'True', 'blank': 'True'})
        },
        'c2g.officehour': {
            'Meta': {'object_name': 'Officehour', 'db_table': "u'officehours'"},
            'calendar_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'calendar_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '511', 'null': 'True', 'blank': 'True'})
        },
        'c2g.roles': {
            'Meta': {'object_name': 'Roles', 'db_table': "u'roles'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'holder_count': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'holder_ids': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'is_staff': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'privileges': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '765'})
        },
        'c2g.sharingpermissions': {
            'Meta': {'object_name': 'SharingPermissions', 'db_table': "u'sharing_permissions'"},
            'cond_by': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cond_nc': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cond_nd': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cond_sa': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'licensee_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'object_id': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'c2g.studentsection': {
            'Meta': {'object_name': 'StudentSection', 'db_table': "u'sections'"},
            'capacity': ('django.db.models.fields.IntegerField', [], {'default': '999'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '511', 'null': 'True', 'blank': 'True'})
        },
        'c2g.usercoursedata': {
            'Meta': {'object_name': 'UserCourseData', 'db_table': "u'user_course_data'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'json': ('django.db.models.fields.TextField', [], {}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'c2g.userprofile': {
            'Meta': {'object_name': 'UserProfile', 'db_table': "u'user_profiles'"},
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'is_instructor': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'site_data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'c2g.video': {
            'Meta': {'object_name': 'Video', 'db_table': "u'videos'"},
            'access_id': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '511', 'null': 'True', 'blank': 'True'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.VideoTopic']", 'null': 'True'})
        },
        'c2g.videoannotations': {
            'Meta': {'object_name': 'VideoAnnotations', 'db_table': "u'video_annotations'"},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'time_in_video': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '511', 'null': 'True', 'blank': 'True'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Video']"})
        },
        'c2g.videoquiz': {
            'Meta': {'object_name': 'VideoQuiz', 'db_table': "u'video_quizzes'"},
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'json': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Video']"})
        },
        'c2g.videoquizquestion': {
            'Meta': {'object_name': 'VideoQuizQuestion', 'db_table': "u'video_quiz_questions'"},
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'json': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'time_in_video': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '511', 'null': 'True', 'blank': 'True'}),
            'video_quiz': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.VideoQuiz']"})
        },
        'c2g.videoquizsubmission': {
            'Meta': {'object_name': 'VideoQuizSubmission', 'db_table': "u'video_quiz_submissions'"},
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'json': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.VideoQuizQuestion']"}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'time_in_video': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'video_metadata': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'c2g.videotopic': {
            'Meta': {'object_name': 'VideoTopic', 'db_table': "u'video_topics'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['c2g']