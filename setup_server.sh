#!bin/bash
USER="kake"

# Install supervisor if not installed
if ! command -v supervisorctl &> /dev/null
then
    echo "Installing supervisor"
    sudo apt install supervisor
else
    echo "Supervisor already installed. Stop all supervisor processes"
    # Kill all supervisor processes
    sudo supervisorctl stop all
fi



CURR_DIR=$(pwd)
NAME=hoocus_server


if [ ! -f ".env" ]; then
    echo "Environment variables not set in '.env'. Does it exist?"
    # Pause execution
    printf 'press [ENTER] to exit...'
    read _
    exit 1
fi



touch $CURR_DIR/logs/gunicorn.log
sudo chown $USER $CURR_DIR/logs/gunicorn.log

if [ ! -f "$CURR_DIR/logs/combined_2.log" ]; then
    touch $CURR_DIR/logs/combined_2.log
    sudo chown $USER $CURR_DIR/logs/combined_2.log
fi

sudo chown -R $USER $CURR_DIR/logs

cat <<EOL > $CURR_DIR/gunicorn_start.sh
#!/bin/sh
CURR_DIR_INSIDE=$CURR_DIR
USER_INSIDE=$USER
VENV=\$CURR_DIR_INSIDE/venv/bin/activate
NAME_INSIDE=$NAME
WORKERS=3
GROUP=$USER
WORKER_CLASS=uvicorn.workers.UvicornWorker
LOG_LEVEL=info
LOG_FILE=\$CURR_DIR_INSIDE/logs/gunicorn.log
BIND=unix:/tmp/gunicorn_hoocus.sock

RANDOM_UUID=\$(openssl rand -hex 16)

cd \$CURR_DIR_INSIDE

# source venv/bin/activate (If you have problems, use this instead of the one below)
. venv/bin/activate

exec gunicorn "server.main:main_entry('\$RANDOM_UUID')" \\
--name \$NAME_INSIDE \\
--workers \$WORKERS \\
--worker-class \$WORKER_CLASS \\
--user \$USER_INSIDE \\
--group \$GROUP \\
--bind \$BIND \\
--log-level \$LOG_LEVEL \\
--log-file \$LOG_FILE
EOL

sudo chmod +x $CURR_DIR/gunicorn_start.sh


# Create supervisor config file
sudo touch /etc/supervisor/conf.d/hoocus_server.conf

if [ ! -d "logs" ]; then
  mkdir logs
fi

sudo cat <<EOL > /etc/supervisor/conf.d/hoocus_server.conf
[program:hoocus_server]
    command=$CURR_DIR/gunicorn_start.sh
    user=$USER
    autostart=false
    autorestart=false
    redirect_stderr=true
    stdout_logfile=$CURR_DIR/logs/gunilog.log
EOL

sudo ln -s /etc/supervisor/conf.d/hoocus_server.conf $CURR_DIR/hoocus_server.conf

# Start supervisor
sudo service supervisor start
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start hoocus_server
sudo supervisorctl status hoocus_server



