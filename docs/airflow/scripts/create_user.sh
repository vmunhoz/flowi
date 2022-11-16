#!/usr/bin/expect -f

sleep 5

set timeout -1
#spawn ./create_user.sh
spawn airflow users create \
    --username admin \
    --firstname John \
    --lastname Doe \
    --role Admin \
    --email john@doe.org

expect "Password:"
send -- "admin\n"

expect "Repeat for confirmation:"
send -- "admin\n"


expect eof
