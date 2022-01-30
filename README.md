# exchange_rate
Web service which exposes the current exchange rate of USD to MXN from three different sources

# how to run
Add the ENV variables BANXICO_TOKEN and FIXER_TOKEN to the docker-compose.yml file
> docker build . -t exchange-rate:latest
> docker-compose up