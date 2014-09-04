#!/bin/bash
# LOGELK_ELK_1_PORT_8050_TCP_ADDR pass from docker
ELK_IP=$LOGELK_ELK_1_PORT_8050_TCP_ADDR
if [[ -z "$ELK_IP" ]]; then
    ELK_IP=localhost
fi
sed -i "s/localhost/$ELK_IP/g" $LFSCONF
/opt/logstash-forwarder/bin/logstash-forwarder -config $LFSCONF