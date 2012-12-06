"""
Takes a text file for a particular survey with one JSON db entry from c2g_examrecords per line, and summarizes the results as a survey.

Args: 
    the filename of JSON strings
    
Returns:
    text formatted with summarized results - text entries at the end, grouped by question.  Eg:
    
        question q02a
    1 18 Strongly Disagree
    2 38 Somewhat Disagree
    3 67 Neutral
    4 286 Somewhat Agree
    5 543 Strongly Agree
    total 952 


"""
import json
import sys

if len(sys.argv) < 2:
    sys.exit('Usage: %s input-filename' % sys.argv[0])

json_file = open(sys.argv[1])
count = 0
errors = 0

tally={}
text={}
textanswers={}

for row in json_file:
    
    try:
        data = eval(json.loads(row))
       
        count += 1
        for question in data.keys():
            
            if (question in tally):
                tally[question]['total'] +=1
            else:
                tally[question] ={}
                text[question]={}
                tally[question]['total'] = 1
            
            if isinstance(data[question], str):
                # it's text, not radio button / checkbox
                #print "answer", data[question], "\n"
                if question not in textanswers.keys():
                    textanswers[question]=[]
                textanswers[question].append(data[question])
                
            else:
                for answer in data[question]:
                   # print "answer", answer, "\n"
                    if (answer['value'] in tally[question]):
                        tally[question][answer['value']] +=1
                    else:
                        tally[question][answer['value']] = 1
                    text[question][answer['value']] = answer['associatedText']
                
        
    except ValueError:
        errors +=1
    
#print "count", count
#print "errors", errors

# print the tallies for radio/checkbox questions

for question in sorted(tally.keys()):
    print "question", question
    for answer in sorted(tally[question]):
        
        print answer, tally[question][answer],
        if answer != 'total':
            print text[question][answer]
    print "\n"
    
# print the text answers

for question in textanswers:
    print question
    for answer in textanswers[question]:
        print answer
    print "\n"    
    
    
json_file.close()




    
