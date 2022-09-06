#!/bin/sh

PSB_db=PSBDB
PSB_host=localhost
PSB_name=PSB
PSB_pass=password
#First create the user if they don't already exist.  Must be done with root,
#meaning sudo.  This also covers people who only installed mariadb and didn't
#expressly make the bot a user account in the database (which it needs).
sudo mariadb -u root -e "CREATE USER IF NOT EXISTS $PSB_name@$PSB_host IDENTIFIED BY '$PSD_pass';"
#As of at least Mariadb 10, the user can be made before the DB (even though
#the syntax implies the reverse).  Futher script updates will probably check
#for sudo properly before executing these first 4 commands.
sudo mariadb -u root -e "GRANT ALL PRIVILEGES ON $PSB_db.* TO $PSB_name@$PSB_host;"

#Everything else can be accomplished by the bot, and should for verification.
mariadb -u$PSB_name -p$PSB_pass -h$PSB_host -e "CREATE DATABASE IF NOT EXISTS $PSB_db;"
#Add table inserts here.
#Note: Prefix may be OBE with the slash command change but I'm keeping it for now in case it's still necessary.
mariadb -u$PSB_name -p$PSB_pass -h$PSB_host $PSD_db -e "CREATE TABLE IF NOT EXISTS (test int auto_increment, primary key (test));"
