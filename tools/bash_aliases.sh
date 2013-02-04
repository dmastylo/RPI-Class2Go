#!/bin/bash

## source this from your login shell

prod_domain="prod.c2gops.com"
stage_domain="stage.c2gops.com"
dev_domain="dev.c2gops.com"

ssh_options="-A"

alias app1.prod="ssh ${ssh_options} ubuntu@app1.${prod_domain}"
alias util1.prod="ssh ${ssh_options} ubuntu@util1.${prod_domain}"

alias app1.stage="ssh ${ssh_options} ubuntu@app1.${stage_domain}"
alias app2.stage="ssh ${ssh_options} ubuntu@app2.${stage_domain}"
alias util1.stage="ssh ${ssh_options} ubuntu@util1.${stage_domain}"

alias jenkins="ssh ${ssh_options} ubuntu@jenkins.${dev_domain}"
alias deploy="ssh ${ssh_options} deploy.${dev_domain}"  # as user

alias localdb="~/src/class2go/main/manage.py dbshell"

function multitail-prod {
    multitail -s 2  \
        --config /usr/local/etc/multitail.conf \
        -CS apache \
        -l 'ssh ubuntu@app1.prod.c2gops.com "tail -f /var/log/apache2/class2go-access.log"' \
        -l 'ssh ubuntu@app2.prod.c2gops.com "tail -f /var/log/apache2/class2go-access.log"' \
        -l 'ssh ubuntu@app3.prod.c2gops.com "tail -f /var/log/apache2/class2go-access.log"' \
        -c- \
        -l 'ssh ubuntu@util1.prod.c2gops.com "tail -f /var/log/celery/*.log"' \
        -CS apache_error \
        -l 'ssh ubuntu@app1.prod.c2gops.com "tail -f /var/log/apache2/class2go-error.log"' \
        -l 'ssh ubuntu@app2.prod.c2gops.com "tail -f /var/log/apache2/class2go-error.log"' \
        -l 'ssh ubuntu@app3.prod.c2gops.com "tail -f /var/log/apache2/class2go-error.log"' \
        -c- \
        -l 'ssh ubuntu@util2.prod.c2gops.com "tail -f /var/log/celery/*.log"' \
        -c- 
}


function multitail-prod-util {
    multitail -s 2  \
        --config /usr/local/etc/multitail.conf \
        -l 'ssh ubuntu@util1.prod.c2gops.com "tail -f /var/log/celery/*.log"' \
        -l 'ssh ubuntu@util2.prod.c2gops.com "tail -f /var/log/celery/*.log"' 
}

function c2g {
    if [ "x$1" == "x" ]; then
        echo "usage: c2g <host_prefix>"
        echo "  example: \"c2g app1.prod\" will ssh to app1.prod.c2gops.com"
        return 1
    fi
    target="ubuntu@$1.c2gops.com"
    echo "connecting to $target via ssh"
    ssh -A $target
}

