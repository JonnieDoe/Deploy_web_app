#!/usr/bin/env bash

echo "Creating Mongo users..."
mongo admin --host localhost -u admin_rinf -p somethingsecure1234  --eval "db.createUser({user: 'TEST', pwd: 'TESTING_1234', roles: [{role: 'readWrite', db: 'TEST'}]});" 
echo "Mongo users created."

exit 0

