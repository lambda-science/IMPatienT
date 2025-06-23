SECRET_KEY=xxxxxx
MAIL_SERVER=xxxxxx
MAIL_PORT=25
MAIL_USERNAME=xxxxxx
MAIL_PASSWORD=xxxxxx
APP_PORT=7860
ADMINS_EMAIL=xxxxxx

docker run --name impatient -d -p $APP_PORT:7860 -it -e SECRET_KEY=$SECRET_KEY \
    -e MAIL_SERVER=$MAIL_SERVER -e MAIL_PORT=$MAIL_PORT -e MAIL_USE_TLS=true \
    -e MAIL_USERNAME=$MAIL_USERNAME -e MAIL_PASSWORD=$MAIL_PASSWORD \
    -e ADMINS_EMAIL=$ADMINS_EMAIL \
    -v dataimpatient:/home/impatient/data \
    --restart unless-stopped impatient:latest
