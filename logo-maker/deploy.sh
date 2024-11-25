#!/bin/bash

# Update system
apt update
apt upgrade -y

# Install required packages
apt install python3-pip python3-venv nginx -y

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Setup Gunicorn service
cp gunicorn.service /etc/systemd/system/
systemctl start gunicorn
systemctl enable gunicorn

# Setup Nginx
cp logo-maker.nginx /etc/nginx/sites-available/logo-maker
ln -s /etc/nginx/sites-available/logo-maker /etc/nginx/sites-enabled
rm /etc/nginx/sites-enabled/default
systemctl restart nginx

# Setup firewall
ufw allow 'Nginx Full'
ufw enable

echo "Deployment complete!" 