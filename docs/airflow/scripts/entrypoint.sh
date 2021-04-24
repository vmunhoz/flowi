#!/bin/bash

airflow db init

nohup airflow scheduler &
nohup ./create_user.sh &
exec airflow webserver
