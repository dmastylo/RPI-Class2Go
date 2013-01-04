# read in a bunch of csv files w/ problem set scores, and do an outer join on the userIDs, listing the late-penalty adjusted score for each

# columns we care about are 1 & 5 - username and total score after late penalty


import csv, sys

files = {'ps1':'2013_01_03__15_45_42-ps1spectrum11.csv' , 'ps2': '2013_01_03__15_52_14-pset2.csv', 'ps3': '2013_01_03__15_52_21-pset3.csv', 'ps4': '2013_01_03__15_52_40-ps4111111111.csv', 'ps5':'2013_01_03__15_52_34-pset5.csv'}

students = {}

for Problemset in files.keys():
    with open(files[Problemset], 'rb') as csvfile:
        StudentData = csv.reader(csvfile, dialect='excel', delimiter=',', quotechar='"')
        count = 0
        for StudentRow in StudentData:
            # we don't want the first 4 rows, they're headers & blanks
            count +=1
            if count > 4:
                username=StudentRow[0]
                score=StudentRow[4]
                
                # have we seen this userid yet?
                if username not in students:
                    students[username]={}
                    
                students[username][Problemset]=score
                
# write a header row                
sys.stdout.write('username')
for Problemset in sorted(files.keys()):
    sys.stdout.write (',')
    sys.stdout.write (Problemset)
sys.stdout.write('\n')
                
# write a row for each student
for student in sorted(students.keys()):
    sys.stdout.write('\'')
    sys.stdout.write (student)
    sys.stdout.write('\'')
    for Problemset in sorted(files.keys()):
        if Problemset in students[student]:
            sys.stdout.write(',')
            sys.stdout.write(students[student][Problemset])
        else:
            sys.stdout.write(',')
            sys.stdout.write('0')
    sys.stdout.write ('\n')
            
    
    