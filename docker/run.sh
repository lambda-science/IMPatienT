SECRET_KEY=<secret_key>
MAIL_SERVER=<mail_server>
MAIL_PORT=<mail_port>
MAIL_USERNAME=<mail_username>
MAIL_PASSWORD=<mail_password>
APP_PORT=<app_port>
DEFAULT_ADMIN_EMAIL=<admin_email>
DEFAULT_ADMIN_PASSWORD=<admin_password>

docker run --name myoxia -d -p $APP_PORT:5000 --rm -e SECRET_KEY=$SECRET_KEY \
    -e MAIL_SERVER=$MAIL_SERVER -e MAIL_PORT=$MAIL_PORT -e MAIL_USE_TLS=true \
    -e MAIL_USERNAME=$MAIL_USERNAME -e MAIL_PASSWORD=$MAIL_PASSWORD \
    -e DEFAULT_ADMIN_EMAIL=$DEFAULT_ADMIN_EMAIL \
    -e DEFAULT_ADMIN_PASSWORD=$DEFAULT_ADMIN_EMAIL \
    --mount 'type=volume,src=datamyoxia,dst=/home/myoxia/data' \
    myoxia:latest