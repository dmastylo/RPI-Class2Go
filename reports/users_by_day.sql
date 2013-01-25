select date(date_joined) as join_date, count(*) as count
from auth_user, auth_user_groups, c2g_courses
where c2g_courses.student_group_id=auth_user_groups.group_id
and auth_user.id = auth_user_groups.user_id
and c2g_courses.mode="ready"
and c2g_courses.id = 46
group by 1 order by 1;
