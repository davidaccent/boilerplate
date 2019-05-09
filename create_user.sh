#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color
BLUE='\033[0;34m'

clear

printf "Do you want to create a user? (y/n)\n"
read -p "->: " CORRECT

 if [ "$CORRECT" = "y" ]; then
    echo -e "\nPlease enter an email address for the user"
    read -p "->: " EMAIL
    echo -e "\nPlease enter an first name for the user"
    read -p "->: " FIRST_NAME
    echo -e "\nPlease enter an last name for the user"
    read -p "->: " LAST_NAME
   	echo "Creating the user..."
   	docker-compose exec app python user_create.py ${EMAIL} ${FIRST_NAME} ${LAST_NAME}
 else
   	echo "User creation cancelled..."
 fi
