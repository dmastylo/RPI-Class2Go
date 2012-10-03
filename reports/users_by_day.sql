select date(date_joined) as join_date, 
    count(*) as users
from auth_user 
where date_joined >= '2012-09-17'
group by 1;
