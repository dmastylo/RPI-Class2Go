#!/usr/bin/env python

import csv
import random

OUTPUT="merged-may13.csv"
CHECKLINE=",sefklon+%03d@gmail.com\n"
CHECKS=10000

def dict_from_file(fname):
    result = dict()
    skips = 0
    f = open(fname, 'r')
    reader = csv.reader(f)
    for row in reader:
        if len(row) == 2: 
            (name,email) = row
            result[email.lower()] = name
        elif len(row) == 1: 
            result[row[0].lower()] = ''
        else:
            skips += 1
    print "%s:\t read %d\tskipped %d" % (fname, len(result), skips)
    return result 

def main():
    mainlist = dict_from_file("starting-may13.csv")
    lastquarter = dict_from_file("authuser-may13.csv")
    excludes = dict_from_file("excludes-may13.csv")

    newlist = dict()
    for k,v in mainlist.iteritems():
        if not excludes.has_key(k):
            newlist[k] = v
    for k,v in lastquarter.iteritems():      # pick up updates
        if not excludes.has_key(k):
            newlist[k] = v
    newlist_k = newlist.keys()
    random.shuffle(newlist_k)

    f = open(OUTPUT, 'w')
    line = 0
    written = 0
    checklines = 0

    f.write(CHECKLINE % checklines)
    checklines += 1
    for k in newlist_k:
        f.write("%s,%s\n" % (newlist[k],k))
        written += 1
        if written % CHECKS == 0:
            f.write(CHECKLINE % checklines)
            checklines += 1
    f.write(CHECKLINE % checklines)
    checklines += 1

    print "%s:\t wrote %d\tchecklines %d" % (OUTPUT, written, checklines)
    
if __name__ == '__main__':
    main()

