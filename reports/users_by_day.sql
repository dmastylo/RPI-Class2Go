select date(date_joined) as join_date, 
    count(*) as users
from auth_user 
group by 1;
