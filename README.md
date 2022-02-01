# exchange_rate
Web service which exposes the current exchange rate of USD to MXN from three different sources

# how to run
Add the ENV variables BANXICO_TOKEN and FIXER_TOKEN to the docker-compose.yml file
> docker build . -t exchange-rate:latest
> docker-compose up

# how to test
Install de requirement, add the ENV variables BANXICO_TOKEN and FIXER_TOKEN to 
the .env file 
> pip install -r requirements.txt
> python manage.py test

# How to test in online demo
1. go to https://zeack-exchange-rate.herokuapp.com/users/
2. create a user
3. login with the new user, https://zeack-exchange-rate.herokuapp.com/auth/login/
4. create a api key in https://zeack-exchange-rate.herokuapp.com/key/
5. use the api key in 'Authorization' with format 'Token {api_key}' or 'api_key' 
query params, https://zeack-exchange-rate.herokuapp.com/latest/?format=json