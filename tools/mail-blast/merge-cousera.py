#!/usr/bin/env python

import csv
import random

prepends = [
    "sefklon@gmail.com",
    "jbau@stanford.edu",
    "jmanning@gmail.com",
    "gregbruhns@gmail.com",
    ]

def dict_from_file(fname, fields):
    result = dict()
    skips = 0
    f = open(fname, 'r')
    reader = csv.reader(f)
    for row in reader:
        if len(row) == fields: 
            if fields == 2:
                (name,email) = row
                result[email] = name
            elif fields == 1:
                email = row[0]
                result[email] = 1
        else:
            skips += 1
    print "%s:\t read %d\tskipped %d" % (fname, len(result), skips)
    return result 

def main():
    newlist = dict()
    mainlist = dict_from_file("dec12_list.csv", 2)
    excludes = dict_from_file("excludes-dec12.csv", 2)
    coursera = dict_from_file("coursera-dec12-in.lst", 1)
    for k,v in coursera.iteritems():
        if not mainlist.has_key(k):
            if not excludes.has_key(k):
                newlist[k] = v
    addresses = newlist.keys()
    random.shuffle(addresses)
    addresses = prepends + addresses

    OUTPUT = "coursera-dec12-unique.csv"
    writes = 0
    f = open(OUTPUT, 'w')
    line = 0
    for k in addresses:
        writes += 1
        f.write("%s,%s\n" % ('', k))  # has to be (name, email) even if we don't have names
    print "%s:\t wrote %d" % (OUTPUT, writes)
    
if __name__ == '__main__':
    main()

