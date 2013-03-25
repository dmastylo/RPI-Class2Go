import os

from c2g.models import *
from copy import *
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from django.db.models import Max

import settings

AWS_ACCESS_KEY_ID = getattr(settings,'AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'local')
    


# Why am I doing this here instead of within the c2g/models.py file?  That file has gotten too long
# try to reduce clutter and modularize

# First, some helper functions
def copyAndSaveModelObj(obj):
    """
       This makes a copy of the model, saves it, and returns it.
       This is a shallow copy--the model fields are duplicated and so file contents, for instance, are aliased.
       The primary key is changed of course.
       Callers of this function are responsible for modifying *all fields* that are *any* form of referecence within the returned object.
       Examples of reference fields include primary-key ids, paths, etc.  These all have to be fixed up by the caller.
    """

    newobj = copy(obj)
    newobj.id = None
    newobj.save()

    return newobj



def copyStageableSectionObj(draft, new_draft_course, new_draft_section):
    """
       Takes as argument the the draft version of an object in a ContentSection and copies both the draft and ready versions over to new_course in new_section
       Sets livedate to None so that materials copied over from earlier course don't automatically become live.
       Relies on new_draft_course and new_draft_section already having images
       Returns draft version of new object.  Ready version is accessible via the image field
    """
    ready = draft.image
    
    # Copy and Setup image relationships
    newdraft = copyAndSaveModelObj(draft)
    newready = copyAndSaveModelObj(ready)
    newready.image = newdraft
    newdraft.image = newready
    
    # Reference fields Section Objects are course and section
    # Setup for draft
    newdraft.course = new_draft_course
    newdraft.section = new_draft_section
    newdraft.live_datetime = None
    
    # Setup for ready
    newready.course = new_draft_course.image
    newready.section = new_draft_section.image
    newready.live_datetime = None
    
    newdraft.save()
    newready.save()
    
    return newdraft



def copyExerciseS3(exercise, new_course):
    """
       Copies exercise to new course.  Will create a new exercise, do the copy in S3, and return new exercise object if new_course does not already have
       an exercise with the same filename.  Otherwise, will simply return the exercise object in the new course with the same filename
    """

    #Look for matching filename in the new course first.
    try:
        return Exercise.objects.get(handle = new_course.handle, fileName = exercise.fileName, is_deleted=False)
    except Exercise.DoesNotExist:
        pass #fall through
    except Exercise.MultipleObjectsReturned:
        return Exercise.objects.filter(handle = new_course.handle, fileName = exercise.fileName, is_deleted=False)[0]

    #Time to create new Exercise object in new course
    newex = Exercise()
    newex.handle = new_course.handle #This is what sets the right S3 prefix as the new course
    newex.fileName = exercise.fileName
    newex.save() #This is to generate an id for newex, which is used by S3
    newex.file.save(newex.fileName, ContentFile(exercise.file.read()))
    newex.save()

    return newex



def copyS3VideoDataById(id, handle, new_id, new_handle):
    """
       Copies all of the metadata, including raw video file and Kelvinator outputs (manifest and thumbnails) belonging to video identified by id, 
       in class identified by handle, to a location corresponding to a video object with new_id in class identified by new_handle
       Returns the new prefix of the assets
    """
    #Going to use BOTO directly, because we just need new keys to the same content and this should be faster, hopefully
    s3conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    bucket = s3conn.get_bucket(AWS_STORAGE_BUCKET_NAME)
    prefix = handle.replace('--', '/') + '/videos/' + str(id)
    new_prefix = new_handle.replace('--','/') + '/videos/' + str(new_id)

    for key in bucket.list(prefix):
        new_key_name = key.key.replace(prefix, new_prefix)
        new_key = key.copy(AWS_STORAGE_BUCKET_NAME, new_key_name)

    return new_prefix


    
#Now, functions that copy over data-types used by ContentSections.  ProblemSets, Videos, Files, and StaticPages

def copyStageableProblemSet(draft, new_draft_course, new_draft_section):
    """
       Takes a draft problem set and copies the (draft,ready) problemSet pair to new_course, in new_section
       Relies on new_draft_course and new_draft_section already having images.
       Then copies over all of the _draft_ exercise relationships, and commits the draft to save the ready version.
    """
    newdraft = copyStageableSectionObj(draft, new_draft_course, new_draft_section)
    
    #Copy over exercises, making new S3 copies where appropriate.
    #We have an idiosyncratic way of deleting pset-to-exercise relationships -- we don't actually delete them
    #but rather set a flag.  It changes the way we search here
    for psToEx in ProblemSetToExercise.objects.filter(is_deleted=False, problemSet=draft):
        exercise = psToEx.exercise
        newex = copyExerciseS3(exercise, new_draft_course)
        newPsToEx = ProblemSetToExercise(problemSet=newdraft, exercise=newex, number=psToEx.number, mode='draft')
        newPsToEx.save()

    #sanity check to avoid duplicate slugs
    if ProblemSet.objects.filter(is_deleted=False, course=new_draft_course, slug=newdraft.slug).count() > 1: #There's definitely one, the one we just copied
        while ProblemSet.objects.filter(is_deleted=False, course=new_draft_course, slug=newdraft.slug).exists():  #Now start appending until slug is unique
            newdraft.slug = newdraft.slug + "1"

    #recompute the path
    newdraft.path = "/"+new_draft_course.handle.replace('--','/')+"/problemsets/"+newdraft.slug+"/load_problem_set"

    newdraft.save()
    newdraft.commit() #Make the ready version

    return draft.image.id, newdraft.image.id


def copyStageableVideo(draft, new_draft_course, new_draft_section):
    """
       Takes a video and copies the (draft,ready) video pair to new_course, in new_section
       Relies on new_draft_course and new_draft_section already having images.
       Then copies over all of the _draft_ exercise relationships, and commits the draft to save the ready version.V
    """
    newdraft = copyStageableSectionObj(draft, new_draft_course, new_draft_section)
    #Copy over exercises, making new S3 copies where appropriate.
    #We have an idiosyncratic way of deleting video-to-exercise relationships -- we don't actually delete them
    #but rather set a flag.  It changes the way we search here
    for vidToEx in VideoToExercise.objects.filter(is_deleted=False, video=draft):
        exercise = vidToEx.exercise
        newex = copyExerciseS3(exercise, new_draft_course)
        newVidToEx = VideoToExercise(video=newdraft, exercise=newex, video_time=vidToEx.video_time, mode='draft')
        newVidToEx.save()
    
    newdraft.save()

    #now move over the S3 video assets
    new_prefix=copyS3VideoDataById(draft.id, draft.course.handle, newdraft.id, new_draft_course.handle)
    #and fix up the file references
    fileName = draft.file.name.split("/")[-1]
    newdraft.file.name= new_prefix + "/" + fileName
    newdraft.handle = new_draft_course.handle

    #sanity check to avoid duplicate slugs
    if Video.objects.filter(is_deleted=False, course=new_draft_course, slug=newdraft.slug).count() > 1: #There's definitely one, the one we just copied
        while Video.objects.filter(is_deleted=False, course=new_draft_course, slug=newdraft.slug).exists():  #Now start appending until slug is unique
            newdraft.slug = newdraft.slug + "1"

    newdraft.save()
    newdraft.commit() #push changes to ready version


    return draft.image.id, newdraft.image.id

def copyStageableFile(draft, new_draft_course, new_draft_section):
    """
       Takes a draft file and copies the (draft,ready) pair to new_course, in new_section
       Relies on new_draft_course and new_draft_section already having images
    """
    newdraft = copyStageableSectionObj(draft, new_draft_course, new_draft_section)
    newready = newdraft.image
    
    newdraft.handle = new_draft_course.handle #This is what sets the right S3 prefix as the new course
    newready.handle = new_draft_course.image.handle

    new_prefix = new_draft_course.handle.replace('--','/') + "/files/"
    new_name =  draft.file.name.split('/')[-1]
    
    found = False
    
    #Search for File with identical filename in new course first    
    for f in File.objects.filter(course = new_draft_course, is_deleted=False):
        if f.file.name == new_prefix+new_name:
            found=True
            foundfile=f
            break

    if found:
        newdraft.file.name = foundfile.file.name
        newready.file.name = foundfile.file.name
        
#ToDo uncomment this        
#    else:
#        newdraft.file.save(new_name, ContentFile(draft.file.read()))
#        newready.file=newdraft.file
  
    newdraft.save()    
    newready.save()

    return draft.image.id, newdraft.image.id

def copyStageableStaticPage(draft, new_draft_course, new_draft_section):
    """
       Takes a draft static page and copies the (draft,ready) pair to new_course, in new_section
       Relies on new_draft_course and new_draft_section already having images
    """
    newdraft = copyStageableSectionObj(draft, new_draft_course, new_draft_section)
    newready = newdraft.image

    #sanity check to avoid duplicate slugs
    if AdditionalPage.objects.filter(is_deleted=False, course=new_draft_course, slug=newdraft.slug).count() > 1: #There's definitely one, the one we just copied
        while AdditionalPage.objects.filter(is_deleted=False, course=new_draft_course, slug=newdraft.slug).exists():  #Now start appending until slug is unique
            newdraft.slug = newdraft.slug + "1"

    newdraft.save()
    newdraft.commit()

    return draft.image.id, newdraft.image.id

def copyStageableExam(draft, new_draft_course, new_draft_section):
    """
       Takes a draft exam and copies the (draft,ready) pair to new_course, in new_section
       Relies on new_draft_course and new_draft_section already having images
    """
    newdraft = copyStageableSectionObj(draft, new_draft_course, new_draft_section)
    newready = newdraft.image

    #sanity check to avoid duplicate slugs
    if Exam.objects.filter(is_deleted=False, course=new_draft_course, slug=newdraft.slug).count() > 1: #There's definitely one, the one we just copied
        while Exam.objects.filter(is_deleted=False, course=new_draft_course, slug=newdraft.slug).exists():  #Now start appending until slug is unique
            newdraft.slug = newdraft.slug + "1"

    newdraft.save()
    newdraft.commit()

    return draft.image.id, newdraft.image.id

def copySection(draft, new_draft_course):
    """ 
       Given a draft copy of a ContentSection, copies the content in the ContentSection to the course identified by new_draft_course.
       If a section with an identical title exists in new_course, uses that as the target section.
       Otherwise, creates a new section with identical name.
    """
    #Figure out whether to create or reuse section.  Either way the result is newdraft
    if ContentSection.objects.filter(is_deleted=False, course=new_draft_course, title=draft.title).exists():
        newdraft = ContentSection.objects.filter(is_deleted=False, course=new_draft_course, title=draft.title)[0]
    else:
        index = ContentSection.objects.filter(is_deleted=False, course=new_draft_course).aggregate(Max('index'))['index__max']+1
        newdraft = ContentSection(course=new_draft_course, title=draft.title)
        newdraft.index = index
        newdraft.mode="draft"
        newdraft.save()
        newdraft.create_ready_instance()

    #Static Pages
    for sp in AdditionalPage.objects.filter(is_deleted=False, course=draft.course, section=draft):
        copyStageableStaticPage(sp, new_draft_course, newdraft)

    #Files
    for f in File.objects.filter(is_deleted=False, course=draft.course, section=draft):
        copyStageableFile(f, new_draft_course, newdraft)

    #ProblemSets
    for ps in ProblemSet.objects.filter(is_deleted=False, course=draft.course, section=draft):
        copyStageableProblemSet(ps, new_draft_course, newdraft)

    #Videos
    for v in Video.objects.filter(is_deleted=False, course=draft.course, section=draft):
        copyStageableVideo(v, new_draft_course, newdraft)

    newdraft.save()
    newdraft.commit()

def copyCourse(old_draft_course, new_draft_course):
    """ 
       Given a draft copy of a Course, copies the content in the course identified by old_draft_course to the
       course identified by new_draft_course.
    """
    
    #Use these dicts to map new entity ids to old entity ids when creating the new ContentGroups.
    additionalpage_map = {}
    file_map = {}
    video_map = {}
    exam_map = {}
    
    old_draftcontentsections = ContentSection.objects.filter(is_deleted=False, course=old_draft_course)
    for old_draftcontentsection in old_draftcontentsections:
    
    #Figure out whether to create or reuse section.  Either way the result is newdraft
        if ContentSection.objects.filter(is_deleted=False, course=new_draft_course, title=old_draftcontentsection.title).exists():
            new_draftcontentsection = ContentSection.objects.filter(is_deleted=False, course=new_draft_course, title=old_draftcontentsection.title)[0]
    
        else:
        
            index = ContentSection.objects.filter(is_deleted=False, course=new_draft_course).aggregate(Max('index'))['index__max']
            if index == None:
                index = 0
            else:
                index +=1
        
            new_draftcontentsection = ContentSection(course=draft_new_course, title=old_draftcontentsection.title)
            new_draftcontentsection.index = index
            new_draftcontentsection.mode="draft"
            new_draftcontentsection.save()
            new_draftcontentsection.create_ready_instance()

        #Additional Pages
        for ap in AdditionalPage.objects.filter(is_deleted=False, course=old_draft_course, section=old_draftcontentsection):
            old_ready_id, new_ready_id = copyStageableStaticPage(ap, new_draft_course, new_draftcontentsection)
            additionalpage_map[old_ready_id] = new_ready_id

        #Files
        for f in File.objects.filter(is_deleted=False, course=old_draft_course, section=old_draftcontentsection):
            old_ready_id, new_ready_id = copyStageableFile(f, new_draft_course, new_draftcontentsection)            
            file_map[old_ready_id] = new_ready_id

        #Videos
        for v in Video.objects.filter(is_deleted=False, course=old_draft_course, section=old_draftcontentsection):
            old_ready_id, new_ready_id = copyStageableVideo(v, new_draft_course, new_draftcontentsection)
            video_map[old_ready_id] = new_ready_id
            
        #Exams
        for e in Exam.objects.filter(is_deleted=False, course=old_draft_course, section=old_draftcontentsection):
            old_ready_id, new_ready_id = copyStageableExam(e, new_draft_course, new_draftcontentsection)
            exam_map[old_ready_id] = new_ready_id
            print "old : new : " + str(old_ready_id) + " : " + str(new_ready_id)

        new_draftcontentsection.save()
        new_draftcontentsection.commit()
    
    #ContentGroups
    copyAllContentGroups(old_draft_course.image.id, new_draft_course.image.id, additionalpage_map, file_map, video_map, exam_map)
 
 
def copyAllContentGroups(old_ready_course_id, new_ready_course_id, additionalpage_map, file_map, video_map, exam_map):
    print "from ready course_id : " + str(old_ready_course_id)
    print "to ready course_id : " + str(new_ready_course_id)
    print exam_map
    
    #Do the level 1 content groups first  
    for cg in ContentGroup.objects.filter(course_id = old_ready_course_id, level = 1):
        
        #We need to ignore those groups where id != group_id as
        #this should never happen. Unfortunately, it did happen.
        if cg.id == cg.group_id:
            new_cg = copyAndSaveModelObj(cg)
            new_cg.group_id = new_cg.id
            new_cg.course_id = new_ready_course_id
            new_cg.video_id = video_map.get(cg.video_id, None)
            new_cg.additional_page_id = additionalpage_map.get(cg.additional_page_id, None)
            new_cg.file_id = file_map.get(cg.file_id, None)
            new_cg.exam_id = file_map.get(cg.exam_id, None)
            new_cg.save()
        
   #Now do the level 2's

