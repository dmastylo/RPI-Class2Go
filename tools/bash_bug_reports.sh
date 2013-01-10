#!/bin/bash
#
# Scripts for bug lists of different sorts 
#
# All rely on ghi, the nice set of comand line tools on top of the Github 
# issues API. https://github.com/stephencelis/ghi
#
# Note that currently this relies on printing milestone and assignments in
# bug list, a change made in my own fork: https://github.com/sefk/ghi
#

function set_yesterday {
    case `uname` in
        "Darwin" )
            YESTERDAY=`date -v -1d` ;;
        * )
            YESTERDAY=`date --date="yesterday"` ;;
    esac
}

function buglist-by-dev {
    if [[ $# -eq 1 ]]; then
        sprintparam="-M $1"
    fi

    for a in jbau wescott jrbl sefk dcadams kluo jinpa ividya; do
        for p in P0 P1; do
            echo "**** $a ($p) ****"
            ghi list -q -s open -l $p -u $a -q $sprintparam | grep -v '\[3-Done\]'
        done
        echo; echo
    done

    for p in P0 P1; do
        echo "**** nobody ($p) ****"
        ghi list -q -l $p -s open ${sinceparam} -q $sprintparam | grep -v '\[3-Done\]' | grep -E "^#|NO-ASGN"
    done
}

function buglist-counts {
    NOW=`date -u +"%F %R UTC"`
    set_yesterday

    for l in P0 P1 P2; do
        # echo -ne "${NOW}\t"
        echo -ne "$l\t"
        ghi list -q -s open -l $l | grep -v '3-Done' | wc -l | tr -d ' ' | tr -d '\n'

        ACTIVE=`ghi list -q -s open -l $l --since "${YESTERDAY}" | grep -v '3-Done' | wc -l | tr -d ' '`
        echo -ne "\t (${ACTIVE} active)"
        echo
    done
}

function buglist-active {
    set_yesterday
    echo -ne '# Marked as Not Done, '
    ghi list -s open --since "${YESTERDAY}"  | grep -v '3-Done'
    echo -ne '# Marked as Done, '
    ghi list -s open --since "${YESTERDAY}"  | egrep '^#|3-Done'
}

function buglist-recently-closed {
    set_yesterday
    ghi list -s closed --since "${YESTERDAY}"
}

function buglist-hot {
    ghi list -s open -l P0 | grep -v '3-Done' 
}

function buglist-to-triage {
    if [[ $1 == "new" ]]; then
        set_yesterday
        sinceparam="--since ${YESTERDAY}"
        sincemsg=" (PRIOR 24 HOURS)"
    else
        sinceparam=""
        sincemsg=""
    fi

    echo "MISSING PRIORITY${sincemsg}"
    ghi list -s open ${sinceparam} \
        | grep -v "NO-ASGN" \
        | grep -v "\[P0\]" \
        | grep -v "\[P1\]" \
        | grep -v "\[P2\]" \
        | grep -v "\[P3\]" 
    echo
    echo "NOT ASSIGNED${sincemsg}"
    ghi list -s open ${sinceparam} | grep -E "^#|NO-ASGN"
}

function buglist-full-report {
    echo "-------- COUNTS OF OPEN ISSUES"
    echo
    buglist-counts

    echo; echo
    echo "-------- CLOSED IN LAST DAY"
    echo
    buglist-recently-closed

    echo; echo
    echo "-------- ALL OPEN P0 ISSUES"
    echo
    buglist-hot

    echo; echo
    echo "-------- ACTIVE (NEW) BUGS THAT NEED TRIAGE"
    echo
    buglist-to-triage new

    echo; echo
    echo "-------- OPEN P0's AND P1's BY DEVELOPER"
    echo
    buglist-by-dev

    # too much!
    # echo; echo
    # echo "-------- ALL ACTIVE ISSUES"
    # echo
    # buglist-active

    echo; echo
    echo "Notes:"
    echo "- Counts and bug lists exclude bugs marked with \"3-Done\" label."
    echo "- \"Active\" means opened or commented-on in the prior 24 hours."
    echo "- Bugs are sorted with most recent activity on top."
    echo "- \"Needs triage\" means not labeled with P0, P1, P2, or P3."
}


