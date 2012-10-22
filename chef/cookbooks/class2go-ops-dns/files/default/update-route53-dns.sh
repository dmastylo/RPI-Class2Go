#!/bin/sh

# Make sure only root can run our script
if [ "$(id -u)" != "0" ]; then
echo "This script must be run as root" 1>&2
    exit 1
fi

# Load configuration
. /etc/route53/config

# Export access key ID and secret for cli53
export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY

# Use command line scripts to get instance ID and public hostname
INSTANCE_ID=$(ec2metadata | grep 'instance-id:' | cut -d ' ' -f 2)
PUBLIC_HOSTNAME=`hostname`

# Create a new CNAME record on Route 53, replacing the old entry if nessesary
cli53 rrcreate "$ZONE" "$INSTANCE_ID" CNAME "$PUBLIC_HOSTNAME" --replace --ttl "$TTL"
