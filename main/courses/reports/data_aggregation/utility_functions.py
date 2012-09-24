### Work-around functions to get unique querysets with respect to a field
        
def qs_unique_by_user(qs):
    qs_sorted_by_field = qs.order_by('user')
    exclude_ids = []
    for i in range(1,qs_sorted_by_field.count()):
        if qs_sorted_by_field[i].user_id == qs_sorted_by_field[i-1].user_id: exclude_ids.append(qs_sorted_by_field[i].id)
    
    return qs.exclude(id__in=exclude_ids)
    
def qs_unique_by_student(qs):
    qs_sorted_by_field = qs.order_by('student')
    exclude_ids = []
    for i in range(1,qs_sorted_by_field.count()):
        if qs_sorted_by_field[i].student_id == qs_sorted_by_field[i-1].student_id: exclude_ids.append(qs_sorted_by_field[i].id)
    
    return qs.exclude(id__in=exclude_ids)

# Temp: Get a list of students with attempts. Try to do this using querysets as much as possible.    
def update_student_ids_with_attempts(swa, attempts):
    for i in range(attempts.count()):
        if i == 0:
            if not attempts[i].student.id in swa: swa.append(attempts[i].student.id)
        else:
            if (attempts[i].student.id != attempts[i-1].student.id) and (not attempts[i].student.id in swa): swa.append(attempts[i].student.id)
        
    return swa