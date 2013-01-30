#!/usr/bin/env python
#

import os
import time
import urllib
import re
import boto

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from optparse import make_option

from courses.exams.autograder import *
from pprint import pprint

class Command(BaseCommand):
    help = """
    """

    option_list = (
        # Main options
        make_option("-g", "--grader", dest="grader",
            help="IP or DNS name of grader to hit"),
        make_option("-q", "--question", dest="question", default="dtd3",
            help="question name (default: dtd3)"),
    ) + BaseCommand.option_list


    def handle(self, *args, **options):

        xml = {}
        answer = {}

        xml['sql'] = """
<exam_metadata>
    <question_metadata id="q1" data-report="q1">
        <solution></solution>
        <response name="q1b" answertype="dbinteractiveresponse">
            <grader_name>SQL_Grader_schroot</grader_name>
            <database-file>sql-social-query2.db</database-file>
            <answer-file>sql-social-query-ans2.txt</answer-file>
            <select_dict></select_dict>
            <parameters>
                <qnum>1</qnum>
                <answer-text>Enter your SQL query here</answer-text>
            </parameters>
        </response>
    </question_metadata>
</exam_metadata>"""
        answer['sql'] = """
        """

        xml['dtd3'] = """
    <question_metadata id="q44eb4ddedb49455b08666f30a4c55108" data-report="q44eb4ddedb49455b08666f30a4c55108">
        <solution></solution>
        <response name="dtd3" answertype="dbinteractiveresponse">
            <grader_name>DTD_Grader_schroot</grader_name>
            <database-file>countries.xml</database-file>
            <answer-file>DTD</answer-file>
            <select_dict></select_dict>
            <parameters>
                <qnum>3</qnum>
                <answer-text>Enter your DTD here</answer-text>
                <runquery-tag>Validate</runquery-tag>
            </parameters>
        </response>
    </question_metadata>
        """
        answer['dtd3'] = """
<!ELEMENT countries (country*)>
<!ELEMENT country (city*, religion*, language*)>
<!ATTLIST country name CDATA #REQUIRED
                  population CDATA #REQUIRED
                  area CDATA #REQUIRED>
<!ELEMENT city (name, population)>
<!ELEMENT name (#PCDATA)>
<!ELEMENT population (#PCDATA)>
<!ELEMENT language (#PCDATA)>
<!ATTLIST language percentage CDATA #REQUIRED>
    """

        if 'grader' in options and options['grader']:
            url = "http://%s/AJAXPostHandler.php" % options['grader']
            settings.GRADER_ENDPOINT = url

        q = options['question'] 
        ag = AutoGrader(xml[q])
        graded = ag.grade(q, answer[q])
        # pprint(graded)
        print "%s: correct = %s, score = %s" % (str(datetime.now()), graded['correct'], graded['score'])

