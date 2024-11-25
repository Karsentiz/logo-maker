#!/bin/bash

# Exit on error
set -e

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

# Ensure correct permissions
chown -R www-data:www-data /root/logo-maker
chmod -R 755 /root/logo-maker

# Setup Gunicorn service
cp gunicorn.service /etc/systemd/system/
systemctl daemon-reload
systemctl start gunicorn
systemctl enable gunicorn

# Setup Nginx
cp logo-maker.nginx /etc/nginx/sites-available/logo-maker
ln -sf /etc/nginx/sites-available/logo-maker /etc/nginx/sites-enabled
rm -f /etc/nginx/sites-enabled/default
nginx -t  # Test configuration
systemctl restart nginx

# Setup firewall
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

echo "Deployment complete!" 