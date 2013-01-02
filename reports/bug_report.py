#!/usr/bin/python 
"""
If you want to sent mail from your mac, you need to enable SMTP
locally.  There are guides on the Internet:
  http://www.freshblurbs.com/blog/2009/05/10/how-enable-local-smtp-postfix-os-x-leopard.html
  http://www.garron.me/mac/postfix-relay-gmail-mac-os-x-local-smtp.html
helpful python email examples:
  http://docs.python.org/2/library/email-examples.html#email-examples 
"""

import sys
import os
import requests
import smtplib
from optparse import OptionParser

repo_name="Stanford-Online/class2go"
issues_url="https://api.github.com/repos/%s/issues" % repo_name
email_sender="sef@cs.stanford.edu"
priority_labels=('P0','P1')

token=os.getenv('GHI_TOKEN')

options = {}
issues = []
users = set()
output = []

## Basic I/O Functions

def read_issues_from_github():
    """
    Use Github v3 API to get all open issues for the repo.  Returns the list of 
    issues and the set of user ids to that have at least one issue assigned.
    """

    global issues, users, output

    filters = { 'state' : 'open' }
    if token:
        filters.update({ 'access_token' : token })
    page_url = issues_url
    while page_url:
        req = requests.get(page_url, params=filters)
        req.raise_for_status()

        issues += req.json
        if 'next' in req.links:
            page_url = req.links['next']['url']
        else:
            page_url = False

    users = set(i['assignee']['login'] for i in issues if i['assignee'] )

    if options.verbose:
        print "%s has %d open issues" % (repo_name, len(issues))
        print "assignees: %s" % ",".join(users)

def output_issue(issue, to):
    line = ""
    if options.html:
        line += "<br><a href=%s>%d</a>: " % (issue['html_url'], issue['number'])
    else:
        line += "%d: " % issue['number']
    line += issue['title']
    for l in issue['labels']:
        line += " [%s]" % l['name']
    if 'assignee' in issue and issue['assignee'] is not None:
        line += " (%s)" % issue['assignee']
    to.append(line)
            

## Reporting functions, each one just appends lines to the global output list

def issues_without_assignee():
    global output
    section = list()
    section.append("P1 issues that have no assignee")
    section.append("")

    found = False
    for i in [ i for i in issues if (i['assignee'] is None and i['labels']) ]:
        if [ l for l in i['labels'] if l['name'] == u'P1' ]:
            found = True
            output_issue(i, section)
    if found:
        output.extend(section)

def issues_by_assignee_by_priority():
    global output
    section = list()
    section.append("")
    section.append("Issues By Assignee")
    section.append("")

    found = False
    for u in users:
        for p in priority_labels:
            found = True
            pass
    if found:
        output.extend(section)

def report_by_email():
    global options, output
    mailer = smtplib.SMTP('localhost')
    mailer.sendmail(email_sender, [ options.email ], "\n".join(output))

def report_to_stdout():
    global options, output
    print "\n".join(output)


################################

def main():
    global options, issues, output
    parser = OptionParser()
    parser.add_option("-q", "--quiet", dest="verbose",
                      action="store_false", default=True,
                      help="don't print status messages to stdout")
    parser.add_option("-e", "--email", dest="email",
                      help="email recipients instead of printing to stdout")
    parser.add_option("-m", "--html", dest="html", 
                      action="store_true", default=False,
                      help="force html output (always on for email)")
    (options, args) = parser.parse_args()
    if options.email:
        options.html = True
    if args:
        parser.error("Not sure what to do with %s" % args)

    read_issues_from_github()
    issues_without_assignee()
    issues_by_assignee_by_priority()
    if options.email:
        report_by_email()
    else:
        report_to_stdout()


if __name__=="__main__":
    main()
