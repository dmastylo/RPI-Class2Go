"""
transform_interactive.py
------------------------
Python script to trasnform from Coursera XML for workbench query exercises
to Class2Go format

Author: Garrett Schlesinger
Modified: 01/08/2013
"""
import sys
import xml.etree.ElementTree as ET
import re
from pset_meta import *

def createProblemSet(root):
    """
    Creates a problem set element to be filled in by the parser. Fills in many default values -- need to change later
    """
    pset = ET.Element('problemset')
    name = root.find('.//title').text

    pset.set('data-report', name)
    pset.set('type', 'interactive')
    pset.set('title', name)
    pset.set('url-identifier', re.sub('[\s()]', '', name))
    
    ET.SubElement(pset, 'description')
    dates = ET.Element('dates')
    dates.set('due-date', DUE_DATE)
    dates.set('grace-period', GRACE_DATE)
    dates.set('hard-deadline', LATE_DATE)
    pset.append(dates)

    grading = ET.Element('grading')
    grading.set('late-penalty', LATE_PENALTY)
    grading.set('num-submissions', NUM_SUBMISSIONS)
    grading.set('resubmission-penalty', RESUBMISSION_PENALTY)
    pset.append(grading)

    section = ET.Element('section')
    section.set('section', SECTION)
    pset.append(section)

    tree_builder = ET.TreeBuilder()
    preamble = tree_builder.start('preamble', {})
    tree_builder.data(root.find('.//preamble').text)
    tree_builder.end('preamble')
    tree_builder.close()

    pset.append(preamble)

    #ET.dump(pset)

    return pset, re.sub('\s', '', name)

def questionToProblem(question):
    """
    Converts a Coursera question to a C2G problem
    """
    grader = question.find('.//grader')

    tree_builder = ET.TreeBuilder()

    attrs = {}
    attrs['id'] = 'q%s' % question.get('id')
    attrs['data-report'] = 'q%s' % question.get('id')

    problem = tree_builder.start('problem', attrs)
    s = '<p>%s</p>' % question.find('.//text').text
    x = ET.XML(s)
    problem.append(x)
    #tree_builder.data('<text><p>%s</p></text>' % question.find('.//text').text)

    tree_builder.start('dbinteractiveresponse', {})

    tree_builder.start('grader_name', {})
    tree_builder.data(grader.get('name'))
    tree_builder.end('grader_name')

    tree_builder.start('database-file', {})
    tree_builder.data(grader.find('.//database-file').text)
    tree_builder.end('database-file')

    tree_builder.start('answer-file', {})
    tree_builder.data(grader.find('.//answer-file').text)
    tree_builder.end('answer-file')

    tree_builder.start('select_dict', {})
    tree_builder.end('select_dict')

    tree_builder.start('parameters', {})

    tree_builder.start('qnum', {})
    tree_builder.data(grader.find('.//qnum').text)
    tree_builder.end('qnum')

    tree_builder.start('answer-text', {})
    tree_builder.data(grader.find('.//answer-text').text)
    tree_builder.end('answer-text')

    tree_builder.start('runquery-tag', {})
    try:
        tree_builder.data(grader.find('.//runquery-tag').text)
    except:
        pass
    tree_builder.end('runquery-tag')

    tree_builder.start('workbench-tag', {})
    try:
        tree_builder.data(grader.find('.//workbench-tag').text)
    except:
        pass
    tree_builder.end('workbench-tag')


    tree_builder.end('parameters')

    tree_builder.end('dbinteractiveresponse')

    tree_builder.start('solution', {})
    tree_builder.data(question.find('.//explanation').text)
    tree_builder.end('solution')

    tree_builder.end('problem')
    tree_builder.close()


    return problem

def parseQuestions(root):
    """
    Loops through the Coursera xml, parsing the questions into 
    c2g format
    """
    pset, name = createProblemSet(root)
    questions = root.findall('.//question')
    for question in questions:
        print("question %s" % question.get('id'))
        problem = questionToProblem(question)
        pset.append(problem)

    tree = ET.ElementTree(pset)
    tree.write('%s.xml' % name)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >> sys.stderr, 'usage: python %s <Coursera xml-file>' % sys.argv[0]
        sys.exit()
    root = ET.parse(sys.argv[1])
    parseQuestions(root)
