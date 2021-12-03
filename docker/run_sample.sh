SECRET_KEY=<secret_key>
MAIL_SERVER=<mail_server>
MAIL_PORT=<mail_port>
MAIL_USERNAME=<mail_username>
MAIL_PASSWORD=<mail_password>
APP_PORT=8000
DEFAULT_ADMIN_USERNAME=<admin_username>
DEFAULT_ADMIN_EMAIL=<admin_email>
DEFAULT_ADMIN_PASSWORD=<admin_password>
ADMINS_EMAIL=<admin_email>

docker run --name ehroes -d -p $APP_PORT:5000 -it -e SECRET_KEY=$SECRET_KEY \
    -e MAIL_SERVER=$MAIL_SERVER -e MAIL_PORT=$MAIL_PORT -e MAIL_USE_TLS=true \
    -e MAIL_USERNAME=$MAIL_USERNAME -e MAIL_PASSWORD=$MAIL_PASSWORD \
    -e DEFAULT_ADMIN_USERNAME=$DEFAULT_ADMIN_USERNAME \
    -e DEFAULT_ADMIN_EMAIL=$DEFAULT_ADMIN_EMAIL \
    -e DEFAULT_ADMIN_PASSWORD=$DEFAULT_ADMIN_PASSWORD \
    -e ADMINS_EMAIL=$ADMINS_EMAIL \
    -v dataehroes:/home/ehroes/data \
    --restart unless-stopped ehroes:latest