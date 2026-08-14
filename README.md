

For generate the auto requirement file and add the all dependacy which i am using so run the cmd:- pip freeze > requirement.txt

for making the docker images:-

Step1- create the dockerfile
step2 - create the dockerignore file
step3 - create the docker-compose.yaml file

# Stop current containers
docker-compose down

# Start fresh
docker-compose up --build
