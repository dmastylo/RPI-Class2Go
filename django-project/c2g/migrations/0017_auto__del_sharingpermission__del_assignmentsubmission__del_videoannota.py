# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'SharingPermission'
        db.delete_table(u'c2g_sharing_permissions')

        # Deleting model 'AssignmentSubmission'
        db.delete_table(u'c2g_assignment_submissions')

        # Deleting model 'VideoAnnotation'
        db.delete_table(u'c2g_video_annotations')

        # Deleting model 'CourseMap'
        db.delete_table(u'c2g_course_maps')

        # Deleting model 'AssignmentCategory'
        db.delete_table(u'c2g_assignment_categories')

        # Deleting model 'Officehour'
        db.delete_table(u'c2g_officehours')

        # Deleting model 'Lecture'
        db.delete_table(u'c2g_lectures')

        # Deleting model 'VideoQuiz'
        db.delete_table(u'c2g_video_quizzes')

        # Deleting model 'CourseAnalytics'
        db.delete_table(u'c2g_course_analytics')

        # Deleting model 'instance_status'
        db.delete_table('c2g_instance_status')

        # Deleting model 'AssignmentGrade'
        db.delete_table(u'c2g_assignment_grades')

        # Deleting model 'VideoQuizSubmission'
        db.delete_table(u'c2g_video_quiz_submissions')

        # Deleting model 'Assignment'
        db.delete_table(u'c2g_assignments')

        # Deleting model 'UserCourseData'
        db.delete_table(u'c2g_user_course_data')

        # Deleting model 'VideoQuizQuestion'
        db.delete_table(u'c2g_video_quiz_questions')

        # Deleting field 'File.access_id'
        db.delete_column(u'c2g_files', 'access_id')

        # Deleting field 'Announcement.access_id'
        db.delete_column(u'c2g_announcements', 'access_id')

        # Deleting field 'AdditionalPage.access_id'
        db.delete_column(u'c2g_additional_pages', 'access_id')

        # Deleting field 'AdditionalPage.update_log'
        db.delete_column(u'c2g_additional_pages', 'update_log')

        # Deleting field 'AdditionalPage.write_access'
        db.delete_column(u'c2g_additional_pages', 'write_access')


    def backwards(self, orm):
        # Adding model 'SharingPermission'
        db.create_table(u'c2g_sharing_permissions', (
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('licensee_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('cond_nd', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('cond_nc', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('cond_sa', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cond_by', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('object_id', self.gf('django.db.models.fields.BigIntegerField')(db_index=True)),
            ('type', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('c2g', ['SharingPermission'])

        # Adding model 'AssignmentSubmission'
        db.create_table(u'c2g_assignment_submissions', (
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('assignment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Assignment'])),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('json', self.gf('django.db.models.fields.TextField')()),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('c2g', ['AssignmentSubmission'])

        # Adding model 'VideoAnnotation'
        db.create_table(u'c2g_video_annotations', (
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Video'])),
            ('time_in_video', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['VideoAnnotation'])

        # Adding model 'CourseMap'
        db.create_table(u'c2g_course_maps', (
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Course'])),
            ('json', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('c2g', ['CourseMap'])

        # Adding model 'AssignmentCategory'
        db.create_table(u'c2g_assignment_categories', (
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Course'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('c2g', ['AssignmentCategory'])

        # Adding model 'Officehour'
        db.create_table(u'c2g_officehours', (
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Course'])),
            ('calendar_end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('calendar_start', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('c2g', ['Officehour'])

        # Adding model 'Lecture'
        db.create_table(u'c2g_lectures', (
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Course'])),
            ('calendar_end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('access_id', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('calendar_start', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('c2g', ['Lecture'])

        # Adding model 'VideoQuiz'
        db.create_table(u'c2g_video_quizzes', (
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('json', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Video'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('c2g', ['VideoQuiz'])

        # Adding model 'CourseAnalytics'
        db.create_table(u'c2g_course_analytics', (
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Course'])),
            ('json', self.gf('django.db.models.fields.TextField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('c2g', ['CourseAnalytics'])

        # Adding model 'instance_status'
        db.create_table('c2g_instance_status', (
            ('prefix', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, db_index=True)),
            ('current_prod', self.gf('django.db.models.fields.related.ForeignKey')(related_name='current_prod', null=True, to=orm['c2g.Course'])),
            ('current_staging', self.gf('django.db.models.fields.related.ForeignKey')(related_name='current_staging', null=True, to=orm['c2g.Course'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('c2g', ['instance_status'])

        # Adding model 'AssignmentGrade'
        db.create_table(u'c2g_assignment_grades', (
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('assignment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Assignment'])),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('json', self.gf('django.db.models.fields.TextField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('c2g', ['AssignmentGrade'])

        # Adding model 'VideoQuizSubmission'
        db.create_table(u'c2g_video_quiz_submissions', (
            ('json', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('video_metadata', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('time_in_video', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.VideoQuizQuestion'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('c2g', ['VideoQuizSubmission'])

        # Adding model 'Assignment'
        db.create_table(u'c2g_assignments', (
            ('due_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Course'])),
            ('close_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.AssignmentCategory'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('access_id', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('c2g', ['Assignment'])

        # Adding model 'UserCourseData'
        db.create_table(u'c2g_user_course_data', (
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.Course'])),
            ('json', self.gf('django.db.models.fields.TextField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('c2g', ['UserCourseData'])

        # Adding model 'VideoQuizQuestion'
        db.create_table(u'c2g_video_quiz_questions', (
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('json', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('video_quiz', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['c2g.VideoQuiz'])),
            ('time_in_video', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('c2g', ['VideoQuizQuestion'])

        # Adding field 'File.access_id'
        db.add_column(u'c2g_files', 'access_id',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Announcement.access_id'
        db.add_column(u'c2g_announcements', 'access_id',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'AdditionalPage.access_id'
        db.add_column(u'c2g_additional_pages', 'access_id',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'AdditionalPage.update_log'
        db.add_column(u'c2g_additional_pages', 'update_log',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'AdditionalPage.write_access'
        db.add_column(u'c2g_additional_pages', 'write_access',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


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
            'Meta': {'object_name': 'AdditionalPage', 'db_table': "u'c2g_additional_pages'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'c2g.announcement': {
            'Meta': {'object_name': 'Announcement', 'db_table': "u'c2g_announcements'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'c2g.course': {
            'Meta': {'object_name': 'Course', 'db_table': "u'c2g_courses'"},
            'calendar_end': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'calendar_start': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'feature_settings': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'handle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['c2g.Course']"}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Institution']"}),
            'instructor_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'instructor_group'", 'to': "orm['auth.Group']"}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'list_publicly': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'live_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'mode': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'readonly_tas_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'readonly_tas_group'", 'to': "orm['auth.Group']"}),
            'student_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'student_group'", 'to': "orm['auth.Group']"}),
            'syllabus': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tas_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tas_group'", 'to': "orm['auth.Group']"}),
            'term': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'c2g.file': {
            'Meta': {'object_name': 'File', 'db_table': "u'c2g_files'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'c2g.institution': {
            'Meta': {'object_name': 'Institution', 'db_table': "u'c2g_institutions'"},
            'city': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'country': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'domains': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {})
        },
        'c2g.newsevent': {
            'Meta': {'object_name': 'NewsEvent', 'db_table': "u'c2g_news_events'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'event': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'c2g.problem': {
            'Meta': {'object_name': 'Problem', 'db_table': "u'c2g_problems'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'problem_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'problem_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.ProblemSet']"}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'c2g.problemactivity': {
            'Meta': {'object_name': 'ProblemActivity', 'db_table': "u'c2g_problem_activity'"},
            'attempt_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'card': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'cards_done': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cards_left': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'casing': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'complete': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'count_hints': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'problem': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Problem']", 'null': 'True'}),
            'problem_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.ProblemSet']", 'null': 'True'}),
            'problem_type': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'review_mode': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'seed': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'sha1': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'time_taken': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'topic_mode': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'c2g.problemset': {
            'Meta': {'object_name': 'ProblemSet', 'db_table': "u'c2g_problem_sets'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'hard_deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'soft_deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'c2g.studentsection': {
            'Meta': {'object_name': 'StudentSection', 'db_table': "u'c2g_sections'"},
            'capacity': ('django.db.models.fields.IntegerField', [], {'default': '999'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'c2g.userprofile': {
            'Meta': {'object_name': 'UserProfile', 'db_table': "u'c2g_user_profiles'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site_data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'c2g.video': {
            'Meta': {'object_name': 'Video', 'db_table': "u'c2g_videos'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['c2g.Video']"}),
            'index': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'live_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'mode': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.VideoTopic']", 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'youtube'", 'max_length': '30'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        'c2g.videoactivity': {
            'Meta': {'object_name': 'VideoActivity', 'db_table': "u'c2g_video_activity'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_seconds': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Video']"})
        },
        'c2g.videotopic': {
            'Meta': {'object_name': 'VideoTopic', 'db_table': "u'c2g_video_topics'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['c2g.VideoTopic']"}),
            'index': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'live_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'mode': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
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