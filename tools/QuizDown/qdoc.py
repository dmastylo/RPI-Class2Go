#!/usr/bin/env python
# by Eric Chu and Justin Foster

import sys
import time
import re
from lxml import etree as ET
from lxml.builder import E

def remove_leading_spaces(s, space=2):
  if s.startswith(' '*space):
    return s[2:]
  else:
    return s

def prettyprint(s):
  return ''.join(map(remove_leading_spaces, s.splitlines(True)))

def show_help():
  a = """Usage: qdoc.py [SOURCEFILE]
  Produces html and xml from a quiz SOURCEFILE.
  
  To use this quiz maker, typing
  
      qdoc.py myquiz.quiz
  
  will produce myquiz.html and myquiz.xml (class2go xml format)
  that contain a list of questions and answers 
  provided in myquiz.quiz.""" 
  
  b = prettyprint(a)
  
  print b
  
# print out the html header
class Question(object):
  def __init__(self, s):
    self.choices = [[]]
    self.text = ['']
    self.title = s.strip('[').strip(']').strip()
    self.current = 0
    
  def current_choice(self):
    return self.choices[self.current][-1]
  
  def add_newline(self):
    self.text[self.current] = self.text[self.current] + '<p/>'
  
  def add_subquestion(self):
    self.current += 1
    self.choices.append([])
    self.text.append('')
  
  def add_choice(self, s, answer, description):
    self.choices[self.current].append(
      Choice(s.strip('*=').strip(), answer, description))
  
  def add_text(self, s):
    if self.text[self.current] is '':
      self.text[self.current] = s
    else:
      self.text[self.current] = self.text[self.current] + ' ' + s
    
  def to_html(self):
    s = ''
    for (c,t) in zip(self.choices, self.text):
      if t is "": # FIX: hack to skip printing of extra description spans        
        continue
      s = s + ("""
      <span class="description"><p>%s</p></span>
      <ul>%s</ul>
      """ % (t, make_choices(c)))
    
    if self.title is "":
      return s
    else:
      return ("""
    <legend>%s</legend>
    %s
    """ % (self.title, s))

  def to_xml(self):
    problem = E.problem()
    for (c,t) in zip(self.choices, self.text):
      if t is "": # FIX: hack to skip printing extra problems
        continue
      qs = t.replace('$','$$').split('<p/>')
      for q in qs:
        p = E.p(q)
        problem.append(p)
      mcg = E.multiplechoiceresponse()
      mcg.append(make_xml_choices(c))
      # could append to problem, but weird formatting
      p.append(mcg)
    return problem

class Choice(object):
  def __init__(self, s, is_answer, response):
    self.txt = s
    self.answer = is_answer
    self.response = response
    
  def add_response(self, s):
      self.response = self.response + ' ' + s
      
  def to_html(self):
    # maybe use self.answer to highlight?
    return ("""
    <li class="choice">
      <div class="selection"><a href="#" onclick="return false">%s</a></div>
      <div class="response">%s</div>
    </li>
    """ % (self.txt, self.response))

  def to_xml(self):
    # add the attribute correct attribute
    if self.answer:
      choice = E.choice(correct='true',name=snake_case(self.txt)[0:19])
    else:
      choice = E.choice(correct='false',name=snake_case(self.txt)[0:19])
    # give the choice values
    choice.append(E.text(self.txt.replace('$','$$')))
    # pull out the explanation
    # HACK: get rid of <span> formatting using XML
    response = self.response.split('</span>')[-1].strip()
    choice.append(E.explanation(response))
    return choice

# Quiz contains questions and choices
# probably not the best parser, but gets the job done....
class Quiz(object):    
  def __init__(self, f):
    self.STATE = "TITLE"
    self.parse_quiz(f)
  
  # since this is so small, it works. but could just use regex
  def parse_quiz(self, f):
    self.questions = []
    qnew = None
    for line in f:
      l = line.strip()
      if len(l) > 0:
        # skip comments
        if l.startswith('#'):
          continue
        l = l.replace("{{",'')
        l = l.replace("}}",'')

        if self.STATE is "TITLE" and l.startswith('=='):
          # this is the header
          self.title = l.strip('==').strip()
          self.STATE = "QUESTION"
          continue
 
        if self.STATE is "GET_QUESTION_TEXT" and qnew is not None:
          if l.startswith('*'):
            self.STATE = "CHOICE"
          elif l.startswith('[') and l.endswith(']'):
            self.STATE = "QUESTION"
          else:
            qnew.add_text(l)
            
        if self.STATE is "CHOICE" and qnew is not None:
          # this is the beginning of a choice
          start = l.find('::')  # find beginnings of description, if any; must be space delimited

          end = len(l)
          if l.startswith('*='):
            description = """<span class="right">Correct! </span>"""
            answer = True
          else:
            description = """<span class="wrong">Incorrect. </span>"""
            answer = False
            
          if l.startswith('*'):
            if start is not -1:
              description = description + \
                l[start:len(l)].strip('::')              
              l = l[0:start]
            
            qnew.add_choice(l, answer, description)                

          elif l.startswith('[') and l.endswith(']'):
            self.STATE = "QUESTION"
          else:
            # TODO: append multiline description
            qnew.current_choice().add_response(l)
            pass
                                        
        if self.STATE is "QUESTION":
          if l.startswith('[') and l.endswith(']'):
            # this is the beginning of a question
            if qnew is not None:
              self.questions.append(qnew)
            qnew = Question(l)
            self.STATE = "GET_QUESTION_TEXT"
          continue
      elif self.STATE is "CHOICE" and qnew is not None:
        qnew.add_subquestion()
        self.STATE = "GET_QUESTION_TEXT"
      elif self.STATE is "GET_QUESTION_TEXT":
        qnew.add_newline()
        
    if qnew is not None:
      self.questions.append(qnew)
    
def make_html_header(f, title):
  # this is a template, really...
  s = ("""
  <!DOCTYPE html">
  <head>
  <meta charset="UTF-8" />
  <title>%s</title>
  <link rel="stylesheet" href="quiz.css" type="text/css" />
  <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
  <script type="text/x-mathjax-config">
  MathJax.Hub.Config({
    tex2jax: {
      inlineMath: [ ['$','$'], ["\\\\(","\\\\)"] ],
      processEscapes: true
    }
  });

  </script>
  <script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_HTML.js"></script>
  
  <script type="text/javascript">
  $(document).ready(function(){
    //close all the content divs on page load
    $('.response').hide();
    
    // toggle slide
    $(".selection").click(function(){
      // by calling sibling, we can use same div for all demos
      $(this).siblings('.response').slideToggle();
    });
  });
  </script>
  </head>
  """ % (title))
  
  s = prettyprint(s)
  f.write(s)

def make_body(f, q):
  # TODO: convert every line of defs.tex in to new commands?
  s = ("""
  <body>
  $\\newcommand{\ones}{\mathbf 1}$
  %s
  <div id="footer">
    Last updated at %s.
  </div>
  </body> </html>
  """ % (add_questions(q), time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(time.time()))))
  s = prettyprint(s)
  f.write(s)
  
def add_questions(questions):
  s = ''
  for q in questions:
    s = s + ("""
  <fieldset>
  %s
  </fieldset><br/>
  """ % (q.to_html()))
  return s

def make_choices(choices):
  return ''.join(map(Choice.to_html, choices))

def make_xml_choices(choices):
	cg = E.choicegroup(type='MultipleChoice')
	map(cg.append,map(Choice.to_xml,choices))
	return cg
#	return E.multiplechoiceresponse().append(cg)

def print_raw(matchobj):
  return matchobj.group(0).strip('{').strip('}')

# snake_case: no special characters, replace ' ' with '_', lower case
def snake_case(string):
  return ''.join(e for e in string if e.isalnum() or e == ' ').replace(' ','_').lower()

def make_xml_tree(quiz):
  title_short = snake_case(quiz.title)[0:19]
  ps_attrib = {'data-report':title_short,
    'type': 'formative',
    'title': quiz.title,
    'url-identifier': title_short}
  ps = ET.Element('problemset',attrib=ps_attrib)
  for q in quiz.questions:
	ps.append(q.to_xml())
  return ps

def main(argv):
  # check if ends with .quiz
  if len(argv) is 0:
    #usage()
    show_help()
    sys.exit("need an input quiz file")
    
  for filename in argv:
    if filename.find(".quiz") is -1:
      #usage()
      show_help()
      sys.exit("file %s must end with .quiz" % filename)
    
    print ("processing %s" % filename)
    
    quiz_file = open(filename)
    quiz = Quiz(quiz_file)
    quiz_file.close()

    f = open(filename.replace(".quiz", ".html"), 'w+')

    make_html_header(f, quiz.title)
    make_body(f, quiz.questions)
    
    f.close()
    
    ps = make_xml_tree(quiz)
    #print(ET.tostring(ps,pretty_print=True))
    ET.ElementTree(ps).write(filename.replace(".quiz",".xml"),pretty_print=True)

if __name__ == "__main__":
  main(sys.argv[1:])
