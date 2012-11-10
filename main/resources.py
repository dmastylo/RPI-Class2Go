from djangorestframework.resources import ModelResource
from djangorestframework.reverse import reverse
from c2g.models import *


class CourseResource(ModelResource):

    # a change
    model = Course

    fields =  ('id', 'institution','student_group' ,'instructor_group','tas_group','readonly_tas_group', 
               'title','description', 'syllabus','term', 'year', 'calendar_start', 'calendar_end', 
               'contact', 'list_publicly', 'handle', 'preview_only_mode', 'piazza_id', 'mode')


    ordering = ('-title',)



 
class AnnouncementResource(ModelResource):

    model = Announcement
    
    fields =  ('id', 'time_created','last_updated' ,'mode','image_id','live_datetime', 
               'index','is_deleted', 'owner_id','course_id', 'title', 'description')


    ordering = ('-title',)


class PSetResource(ModelResource):

    model =  ProblemSet
    
    fields =  ('id','mode','image_id','live_datetime', 
               'index','is_deleted', 'course_id', 'section_id', 'slug', 'title', 'description', 'path',
               'due_date','grace_period','partial_credit_deadline','assessment_type','late_penalty','submissions_permitted',
               'resubmission_penalty','randomize')


    ordering = ('-id',)
    
class PSetExerciseResource(ModelResource):

    model =  ProblemSetToExercise
    
    fields =  ('id','mode','image_id','number', 
               'exercise_id','problemSet_id', 'is_deleted')


    ordering = ('-id',)

class ExerciseResource(ModelResource):

    model =  Exercise
    
    fields =  ('id','is_deleted', 'fileName', 'file', 'handle')

    ordering = ('-id',)
    

class ContentSectionResource(ModelResource):

    model =  ContentSection
    
    fields =  ('id', 'mode', 'image_id', 'live_datetime', 'index', 'is_deleted', 'course_id', 'title')

    ordering = ('-id',)

class VideoResource(ModelResource):

    model =  Video
    
    fields =  ('id', 'mode', 'image_id', 'live_datetime', 'index', 'is_deleted', 'course_id', 'section_id',
               'title','description','type','url','duration','slug','file','handle')

    ordering = ('-id',)
    

class VideoToExerciseResource(ModelResource):

    model =  VideoToExercise
    
    fields =  ('id', 'is_deleted',  'video_id', 'exercise_id', 'video_time','image_id','mode')

    ordering = ('-id',)

