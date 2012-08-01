from c2g.models import *
import datetime

def get_course_materials(common_page_data, get_video_content=True, get_pset_content=True):
    section_structures = []
    if common_page_data['request'].user.is_authenticated():
        sections = common_page_data['course'].contentsection_set.all().order_by('index')
        videos = Video.objects.filter(course=common_page_data['course']).order_by('section', 'index')
        problem_sets = ProblemSet.objects.filter(course=common_page_data['course']).order_by('section', 'index')
        video_recs = common_page_data['request'].user.videoactivity_set.filter(course=common_page_data['course'])
        
        index = 0
        for section in sections:
            section_dict = {'section':section, 'items':[]}
            
            if get_video_content:
                for video in videos:
                    if video.section_id == section.id and (common_page_data['course_mode'] == 'staging' or (video.live_datetime and video.live_datetime > common_page_data['effective_current_datetime'])):
                        item = {'type':'video', 'video':video}
                        for video_rec in video_recs:
                            if video_rec.video_id == video.id:
                                item['video_rec'] = video_rec
                                break
                        
                        live_status = ''
                        if common_page_data['course_mode'] == 'staging':
                            prod_video = video.image
                            if not prod_video.live_datetime:
                                live_status = "<span style='color:red;'>Not live</span>"
                            else:
                                if prod_video.live_datetime > datetime.datetime.now():
                                    year = prod_video.live_datetime.year
                                    month = prod_video.live_datetime.month
                                    day = prod_video.live_datetime.day
                                    hour = prod_video.live_datetime.hour
                                    minute = prod_video.live_datetime.minute
                                    live_status = "<span style='color:red;'>Goes live on %02d-%02d-%04d at %02d:%02d</span>" % (month,day,year,hour,minute)
                                else:
                                    live_status = "<span style='color:green;'>Live</span>"
                        item['live_status'] = live_status
                    
                        section_dict['items'].append(item)
            
            if get_pset_content:
                for problem_set in problem_sets:
                    if problem_set.section_id == section.id and (common_page_data['course_mode'] == 'staging' or (problem_set.live_datetime and problem_set.live_datetime > common_page_data['effective_current_datetime'])):
                        item = {'type':'problem_set', 'problem_set':problem_set}
                        
                        exercises = problem_set.exercise_set.all()
                        numQuestions = len(exercises)
                        #Starting values are total questions and will be subtracted from
                        numCompleted = numQuestions
                        numCorrect = numQuestions
                        for exercise in exercises:
                            attempts = exercise.problemactivity_set.filter(student = common_page_data['request'].user).exclude(attempt_content="hint")

                            #Counts the completed problems by subtracting all without a student activity recorded for it
                            if len(attempts) == 0:
                                numCompleted -= 1

                            #Add one to the number of correctly answered questions if the first attempt is correct
                            attempts.filter(attempt_number = 1)
                            for attempt in attempts:
                                if attempt.complete == 0:
                                    numCorrect -= 1
                                    break

                        #Divide by zero safety check
                        if numQuestions == 0:
                            progress = 0
                        else:
                            progress = 100.0*numCompleted/numQuestions
                        
                        item['numQuestions'] = numQuestions
                        item['numCompleted'] = numCompleted
                        item['numCorrect'] = numCorrect
                        item['progress'] = progress
                        
                        live_status = ''
                        if common_page_data['course_mode'] == 'staging':
                            prod_problem_set = problem_set.image
                            if not prod_problem_set.live_datetime:
                                live_status = "<span style='color:red;'>Not live</span>"
                            else:
                                if prod_problem_set.live_datetime > datetime.datetime.now():
                                    year = prod_problem_set.live_datetime.year
                                    month = prod_problem_set.live_datetime.month
                                    day = prod_problem_set.live_datetime.day
                                    hour = prod_problem_set.live_datetime.hour
                                    minute = prod_problem_set.live_datetime.minute
                                    live_status = "<span style='color:red;'>Goes live on %02d-%02d-%04d at %02d:%02d</span>" % (month,day,year,hour,minute)
                                else:
                                    live_status = "<span style='color:green;'>Live</span>"
                        item['live_status'] = live_status
                        
                        section_dict['items'].append(item)
            
            if common_page_data['course_mode'] == 'staging' or len(section_dict['items']) > 0:
                section_structures.append(section_dict)
                index += 1
                
    return section_structures