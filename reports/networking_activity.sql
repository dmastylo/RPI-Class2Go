select  ACTIVITY_DATE,sum(video) as video, sum(problemset) as problemset, sum(forum) as forum, sum(additional_page) as additional FROM 
	(
	SELECT DATE(c2g_page_visit_log.last_updated) as ACTIVITY_DATE, page_type, 
	IF(page_type='video', count(*), 0) as video, 
	IF(page_type='forum',count(*), 0) as forum,
	IF(page_type='problemset',count(*), 0) as problemset,
	IF(page_type='additional_page',count(*), 0) as additional_page
 	from c2g_page_visit_log WHERE c2g_page_visit_log.course_id = 4
 	AND last_updated > '2012-10-08'
 	group by 		ACTIVITY_DATE, page_type) as stuff
 	GROUP BY ACTIVITY_DATE
 	ORDER BY ACTIVITY_DATE desc, page_type
 ;
