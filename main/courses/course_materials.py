from c2g.models import *
import datetime
from django.db.models import Count


def get_course_materials(common_page_data, get_video_content=False, get_pset_content=False, get_additional_page_content = False, get_file_content=False):
    section_structures = []
    if common_page_data['request'].user.is_authenticated():
        sections = ContentSection.objects.getByCourse(course=common_page_data['course'])
        problem_sets = ProblemSet.objects.getByCourse(course=common_page_data['course'])
        pages = AdditionalPage.objects.getSectionPagesByCourse(course=common_page_data['course'])
        files = File.objects.getByCourse(course=common_page_data['course'])

        index = 0
        for section in sections:
            section_dict = {'section':section, 'items':[]}

            if get_additional_page_content:
                for page in pages:
                    if page.section_id == section.id:
                        item = {'type':'additional_page', 'additional_page':page, 'index':page.index}

                        if common_page_data['course_mode'] == 'draft':
                            prod_page = page.image
                            if not prod_page.live_datetime:
                                visible_status = "<span style='color:#A00000;'>Not Live</span>"
                            else:
                                if prod_page.live_datetime > datetime.datetime.now():
                                    year = prod_page.live_datetime.year
                                    month = prod_page.live_datetime.month
                                    day = prod_page.live_datetime.day
                                    hour = prod_page.live_datetime.hour
                                    minute = prod_page.live_datetime.minute
                                    visible_status = "<span style='color:#A07000;'>Live %02d-%02d-%04d at %02d:%02d</span>" % (month,day,year,hour,minute)
                                else:
                                    visible_status = "<span style='color:green;'>Live</span>"

                            item['visible_status'] = visible_status

                        section_dict['items'].append(item)

            if get_file_content:
                for file in files:
                    if file.section_id == section.id:
                        item = {'type':'file', 'file':file, 'index':file.index}

                        if common_page_data['course_mode'] == 'draft':
                            prod_file = file.image
                            if not prod_file.live_datetime:
                                visible_status = "<span style='color:#A00000;'>Not Live</span>"
                            else:
                                if prod_file.live_datetime > datetime.datetime.now():
                                    year = prod_file.live_datetime.year
                                    month = prod_file.live_datetime.month
                                    day = prod_file.live_datetime.day
                                    hour = prod_file.live_datetime.hour
                                    minute = prod_file.live_datetime.minute
                                    visible_status = "<span style='color:#A07000;'>Live %02d-%02d-%04d at %02d:%02d</span>" % (month,day,year,hour,minute)
                                else:
                                    visible_status = "<span style='color:green;'>Live</span>"

                            item['visible_status'] = visible_status

                        section_dict['items'].append(item)

            if get_video_content:
                videos = Video.objects.getByCourse(course=common_page_data['course'])
                
                if videos:
                    video_list = []
                    for video in videos:
                        video_list.append(video.id)
                    videoToExs = VideoToExercise.objects.values('video').filter(video__in=video_list, is_deleted=0).annotate(dcount=Count('video'))
                    
                    if common_page_data['course_mode'] == 'ready':
                        video_recs = VideoActivity.objects.filter(course=common_page_data['course'], student=common_page_data['request'].user)
                        
                for video in videos:
                    if video.section_id == section.id:
                
                        item = {'type':'video', 'video':video, 'completed_percent': 0, 'index':video.index}

                        numQuestions = 0
                        for videoToEx in videoToExs:
                            if videoToEx['video'] == video.id:
                                numQuestions = videoToEx['dcount']
                                break
                        
                        if common_page_data['course_mode'] == 'draft':
                            prod_video = video.image
                            if not prod_video.live_datetime:
                                visible_status = "<span style='color:#A00000;'>Not Live</span>"
                            else:
                                if prod_video.live_datetime > datetime.datetime.now():
                                    year = prod_video.live_datetime.year
                                    month = prod_video.live_datetime.month
                                    day = prod_video.live_datetime.day
                                    hour = prod_video.live_datetime.hour
                                    minute = prod_video.live_datetime.minute
                                    visible_status = "<span style='color:#A07000;'>Live %02d-%02d-%04d at %02d:%02d</span>" % (month,day,year,hour,minute)
                                else:
                                    visible_status = "<span style='color:green;'>Live</span>"

                            item['visible_status'] = visible_status
                        else:
                            for video_rec in video_recs:
                                if video_rec.video_id == video.id:
                                    item['video_rec'] = video_rec
                                    if video.duration:
                                        item['completed_percent'] = 100.0 * video_rec.start_seconds / video.duration
                                    else:
                                        item['completed_percent'] = 0

                        item['numQuestions'] = numQuestions
                        section_dict['items'].append(item)

            if get_pset_content:
                for problem_set in problem_sets:
                    #if problem_set.section_id == section.id and (common_page_data['course_mode'] == 'draft' or (problem_set.live_datetime and problem_set.live_datetime < common_page_data['effective_current_datetime'])):
                    if problem_set.section_id == section.id:
                        item = {'type':'problem_set', 'problem_set':problem_set, 'index':problem_set.index}

                        psetToExs = ProblemSetToExercise.objects.getByProblemset(problem_set)
                        numQuestions = len(psetToExs)
                            
                        if common_page_data['course_mode'] == 'draft':
                            prod_problem_set = problem_set.image
                            if not prod_problem_set.live_datetime:
                                visible_status = "<span style='color:#A00000;'>Not Live</span>"
                            else:
                                if prod_problem_set.live_datetime > datetime.datetime.now():
                                    year = prod_problem_set.live_datetime.year
                                    month = prod_problem_set.live_datetime.month
                                    day = prod_problem_set.live_datetime.day
                                    hour = prod_problem_set.live_datetime.hour
                                    minute = prod_problem_set.live_datetime.minute
                                    visible_status = "<span style='color:#A07000;'>Live %02d-%02d-%04d at %02d:%02d</span>" % (month,day,year,hour,minute)
                                else:
                                    visible_status = "<span style='color:green;'>Live</span>"

                            item['visible_status'] = visible_status
                        else:

                            numCompleted = problem_set.get_progress(common_page_data['request'].user)
                            score = problem_set.get_score(common_page_data['request'].user)

                            #Divide by zero safety check
                            if numQuestions == 0:
                                progress = 0
                            else:
                                progress = 100.0*numCompleted/numQuestions
                                
                            item['numCompleted'] = numCompleted
                            item['score'] = score
                            item['progress'] = progress

                        item['numQuestions'] = numQuestions
                        section_dict['items'].append(item)

            if common_page_data['course_mode'] == 'draft' or len(section_dict['items']) > 0:
                section_dict['items'] = sorted(section_dict['items'], key=lambda k: k['index'])
                section_structures.append(section_dict)
                index += 1

    return section_structures
