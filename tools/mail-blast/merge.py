#!/usr/bin/env python

import csv
import random

OUTPUT="dec12_list.csv"

def dict_from_file(fname):
    result = dict()
    skips = 0
    f = open(fname, 'r')
    reader = csv.reader(f)
    for row in reader:
        if len(row) == 2: 
            (name,email) = row
            result[email] = name
        else:
            skips += 1
    print "%s:\t read %d\tskipped %d" % (fname, len(result), skips)
    return result 

def main():
    mainlist = dict_from_file("sep12.csv")
    lastquarter = dict_from_file("authuser-dec12.csv")
    excludes = dict_from_file("excludes-dec12.csv")

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
    for k in newlist_k:
        f.write("%s,%s\n" % (newlist[k],k))
    
if __name__ == '__main__':
    main()

