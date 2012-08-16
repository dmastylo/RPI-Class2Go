from c2g.models import *
import datetime

def get_course_materials(common_page_data, get_video_content=False, get_pset_content=False, get_additional_page_content = False):
    section_structures = []
    if common_page_data['request'].user.is_authenticated():
        sections = ContentSection.objects.getByCourse(course=common_page_data['course'])
        videos = Video.objects.getByCourse(course=common_page_data['course'])
        problem_sets = ProblemSet.objects.getByCourse(course=common_page_data['course'])
        pages = AdditionalPage.objects.getSectionPagesByCourse(course=common_page_data['course'])

        index = 0
        for section in sections:
            section_dict = {'section':section, 'items':[]}

            if get_additional_page_content:
                for page in pages:
                    if page.section_id == section.id:
                        item = {'type':'additional_page', 'additional_page':page, 'index':page.index}

                        if common_page_data['course_mode'] == 'staging':
                            prod_page = page.image
                            if not prod_page.live_datetime:
                                visible_status = "<span style='color:#A00000;'>Not open</span>"
                            else:
                                if prod_page.live_datetime > datetime.datetime.now():
                                    year = prod_page.live_datetime.year
                                    month = prod_page.live_datetime.month
                                    day = prod_page.live_datetime.day
                                    hour = prod_page.live_datetime.hour
                                    minute = prod_page.live_datetime.minute
                                    visible_status = "<span style='color:#A07000;'>Open %02d-%02d-%04d at %02d:%02d</span>" % (month,day,year,hour,minute)
                                else:
                                    visible_status = "<span style='color:green;'>Open</span>"

                            item['visible_status'] = visible_status

                        section_dict['items'].append(item)

            if get_video_content:
                for video in videos:
                    #if video.section_id == section.id and (common_page_data['course_mode'] == 'staging' or (video.live_datetime and video.live_datetime < common_page_data['effective_current_datetime'])):
                    if video.section_id == section.id:
                        item = {'type':'video', 'video':video, 'completed_percent': 0, 'index':video.index}

                        if common_page_data['course_mode'] == 'staging':
                            prod_video = video.image
                            if not prod_video.live_datetime:
                                visible_status = "<span style='color:#A00000;'>Not open</span>"
                            else:
                                if prod_video.live_datetime > datetime.datetime.now():
                                    year = prod_video.live_datetime.year
                                    month = prod_video.live_datetime.month
                                    day = prod_video.live_datetime.day
                                    hour = prod_video.live_datetime.hour
                                    minute = prod_video.live_datetime.minute
                                    visible_status = "<span style='color:#A07000;'>Open %02d-%02d-%04d at %02d:%02d</span>" % (month,day,year,hour,minute)
                                else:
                                    visible_status = "<span style='color:green;'>Open</span>"

                            item['visible_status'] = visible_status
                        else:
                            video_recs = VideoActivity.objects.filter(video=video, student=common_page_data['request'].user)
                            if len(video_recs)>0:
                                video_rec = video_recs[0]
                                item['video_rec'] = video_rec
                                item['completed_percent'] = 100.0 * video_rec.start_seconds / video.duration

                        section_dict['items'].append(item)

            if get_pset_content:
                for problem_set in problem_sets:
                    #if problem_set.section_id == section.id and (common_page_data['course_mode'] == 'staging' or (problem_set.live_datetime and problem_set.live_datetime < common_page_data['effective_current_datetime'])):
                    if problem_set.section_id == section.id:
                        item = {'type':'problem_set', 'problem_set':problem_set, 'index':problem_set.index}

                        if common_page_data['course_mode'] == 'staging':
                            prod_problem_set = problem_set.image
                            if not prod_problem_set.live_datetime:
                                visible_status = "<span style='color:#A00000;'>Not open</span>"
                            else:
                                if prod_problem_set.live_datetime > datetime.datetime.now():
                                    year = prod_problem_set.live_datetime.year
                                    month = prod_problem_set.live_datetime.month
                                    day = prod_problem_set.live_datetime.day
                                    hour = prod_problem_set.live_datetime.hour
                                    minute = prod_problem_set.live_datetime.minute
                                    visible_status = "<span style='color:#A07000;'>Open %02d-%02d-%04d at %02d:%02d</span>" % (month,day,year,hour,minute)
                                else:
                                    visible_status = "<span style='color:green;'>Open</span>"

                            item['visible_status'] = visible_status
                        else:
                            psetToExs = ProblemSetToExercise.objects.getByProblemset(problem_set)
                            numQuestions = len(psetToExs)
                             #Starting values are total questions and will be subtracted from
                            numCompleted = numQuestions
                            numCorrect = numQuestions
                            for psetToEx in psetToExs:
                                attempts = psetToEx.problemactivity_set.filter(student = common_page_data['request'].user).exclude(attempt_content="hint")

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

                        section_dict['items'].append(item)

            if common_page_data['course_mode'] == 'staging' or len(section_dict['items']) > 0:
                section_dict['items'] = sorted(section_dict['items'], key=lambda k: k['index'])
                section_structures.append(section_dict)
                index += 1

    return section_structures
