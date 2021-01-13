#!/bin/sh
#
# Part of Red ELK
# Script to get remote C2 logs via rsync
# The output is saved in /var/www/html/c2logs/$hostname/logs/
#
# Author: Outflank B.V. / Marc Smeets
#

LOGFILE="/var/log/redelk/getremotelogs.log"

if ! [ $# -eq 3 ] ; then
    echo "[X] Error - need IP or full DNS name of system to get remote logs from as 1st parameter."
    echo "[X] Error - need the remote system's filebeats hostname as 2nd parameter."
    echo "[X] Error - need the username to connect with as 3rd parameter."
    echo "[X] Error - need the ssh port of system to get remote logs from 4rd parameter. Defaults to '22'."
    echo "Incorrect amount of parameters" >> $LOGFILE 2>&1
    exit 1
fi
mkdir -p /var/www/html/c2logs/"$2" >> $LOGFILE 2>&1

echo "$(date) ######## Start of rsync to $1" >> $LOGFILE 2>&1
rsync -axv -e 'ssh -p '"${4:-22}"' -o "StrictHostKeyChecking=no" -i /home/redelk/.ssh/id_rsa' "$3"@"$1":~/logs /var/www/html/c2logs/"$2" >> $LOGFILE 2>&1
rsync -axv -e 'ssh -p '"${4:-22}"' -o "StrictHostKeyChecking=no" -i /home/redelk/.ssh/id_rsa' "$3"@"$1":~/downloads /var/www/html/c2logs/"$2" >> $LOGFILE 2>&1
rsync -axv -e 'ssh -p '"${4:-22}"' -o "StrictHostKeyChecking=no" -i /home/redelk/.ssh/id_rsa' "$3"@"$1":~/profiles /var/www/html/c2logs/"$2" >> $LOGFILE 2>&1
rsync -axv -e 'ssh -p '"${4:-22}"' -o "StrictHostKeyChecking=no" -i /home/redelk/.ssh/id_rsa' "$3"@"$1":~/data /var/www/html/c2logs/"$2" >> $LOGFILE 2>&1
echo "$(date) ######## Done with rsync" >> $LOGFILE 2>&1
