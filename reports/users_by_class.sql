select substring_index(handle, '--', 1) as course,
        count(*) as count
from auth_user_groups, c2g_courses
where c2g_courses.student_group_id=auth_user_groups.group_id
and c2g_courses.mode="ready"
group by 1;
