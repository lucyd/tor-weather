Setting up a VM using Vagrant, and getting Weather to run
=========================================================

Important
---------
At the time of writing, *none* of the steps below the line "Stop here" are necessary anymore.
A vagrant box with provisioning has been set up and should do all the work for
you!
Anyhow, these instructions will be kept for reference should anything be amiss.

Please note that the only thing you will have to do is edit your _/etc/hosts_
file accordingly to contain this line:

```sh
192.168.33.10 weather.dev
```

This will allow you to point your browser to "weather.dev".

Clone Weather Git repo
----------------------

https://gitweb.torproject.org/user/karsten/weather.git/shortlog/refs/heads/vagrant

This box uses Wheezy 7.3 (which is not the latest release), but comes with Puppet installed.  (See TODO below.)

Start VM using Vagrant
----------------------

```sh
vagrant up
vagrant ssh
```

--> Stop here! <--
==================

Install missing and/or useful packages
--------------------------------------

```sh
sudo apt-get install apache2 sqlite3 vim libapache2-mod-wsgi tor
```

Create directories and symlinks
-------------------------------

```sh
sudo mkdir -p /srv/weather.torproject.org/opt/weather
sudo ln -s /vagrant/weather /srv/weather.torproject.org/opt/weather/weather
sudo mkdir -p /srv/weather.torproject.org/home/bin   # contains two scripts
sudo ln -s /srv/weather.torproject.org/opt/weather /srv/weather.torproject.org/opt/current
sudo ln -s /srv/weather.torproject.org/opt /srv/weather.torproject.org/home/opt
sudo mkdir -p /srv/weather.torproject.org/home/var/run   # contains process id files
sudo mkdir -p /srv/weather.torproject.org/tmp   # well, temp stuff, apparently
sudo ln -s /srv/weather.torproject.org/home /home/weather
sudo mkdir -p /srv/weather.torproject.org/opt/weather/var
sudo chown -R vagrant:www-data /srv/weather.torproject.org/
```

Going through doc/INSTALL
-------------------------

### Step 1:

```sh
sudo -s
cat >> /etc/tor/torrc << EOF
FetchDirInfoEarly 1
FetchUselessDescriptors 1
ControlPort 9051
HashedControlPassword 16:067C5B9B7B036EEE603814A6F045B9EEE0B40EA60192506C005D64E436
EOF
exit
sudo service tor reload
```

### Step 2:

```sh
cat >> /srv/weather.torproject.org/opt/weather/weather/settings.py << EOF
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/weather-messages'
EOF
```

### Step 4:

```sh
sudo pip install stem
```

### Step 5:

```sh
cat > /srv/weather.torproject.org/opt/weather/weather/config/auth_token << EOF
password
EOF
```

### Step 6:

```sh
sudo touch /srv/weather.torproject.org/opt/weather/var/WeatherDB
sudo chown vagrant:www-data /srv/weather.torproject.org/opt/weather/var
sudo chmod 664 /srv/weather.torproject.org/opt/weather/var/WeatherDB
sudo chmod 775 /srv/weather.torproject.org/opt/weather/var
sudo chown vagrant:www-data \
    /srv/weather.torproject.org/opt/weather/var/WeatherDB
cd /srv/weather.torproject.org/opt/weather/weather/
python manage.py syncdb   # is it safe to say 'no' to the superusers question?
```

### Step 7b:

Generate ssl cert; just accept the defaults:

```sh
sudo openssl  req -new -x509 -days 365 -nodes -sha256 \
    -out /etc/ssl/certs/wildcard.torproject.org.pem \
    -keyout /etc/ssl/private/wildcard.torproject.org.key
```

Configure apache:

```sh
sudo a2enmod rewrite
sudo a2enmod ssl
sudo -s
cat > /etc/apache2/sites-available/weather.torproject.org << EOF
<VirtualHost *:80>
    ServerName weather.torproject.org
    ErrorLog  /var/log/apache2/weather2.torproject.org-error.log
    CustomLog /var/log/apache2/weather2.torproject.org-access.log privacy
    WSGIScriptAlias / /home/weather/opt/current/weather/weather.wsgi
    RewriteEngine On
    RewriteRule ^(.*)$ https://%{SERVER_NAME}$1 [L,R]
</VirtualHost>
<VirtualHost *:443>
    SSLEngine on
    SSLCertificateFile    /etc/ssl/certs/wildcard.torproject.org.pem
    SSLCertificateKeyFile /etc/ssl/private/wildcard.torproject.org.key
    ServerName weather.torproject.org
    AliasMatch ^/([^/]*\.png) /home/weather/opt/current/weather/media/$1
    AliasMatch ^/([^/]*\.css) /home/weather/opt/current/weather/media/$1
    AliasMatch ^/([^/]*\.js) /home/weather/opt/current/weather/media/$1
    Alias /media/ /home/weather/opt/current/weather/media/
    ErrorLog  /var/log/apache2/weather2.torproject.org-error.log
    CustomLog /var/log/apache2/weather2.torproject.org-access.log privacy
    WSGIScriptAlias / /home/weather/opt/current/weather/weather.wsgi
</VirtualHost>
EOF
exit
sudo a2ensite weather.torproject.org
sudo service apache2 restart   # need to restart for a2enmod changes above
```

### Step 7c

Edit `/etc/hosts` on your host (!) machine and add this line:

`192.168.33.10 weather.torproject.org`

(Sadly, this means the real weather is not reachable anymore, see TODO for a task regarding hostnames)

Clear all caches in your browser/fire up a separate browser and hit weather.torproject.org - when viewing the certificate-details, you should see all the dummy-data you entered earlier, explicitly NOT data relating to torproject.org (the real one)

### Step 8:

```sh
cd /srv/weather.torproject.org/opt/weather/weather/
python manage.py runlistener
```

Problem: listener terminates immediately; I recall that Abhiram solved this issue before...

### Temp section: crontab on bahri, where weather currently lives:

```sh
@reboot cd /home/weather/opt/current/weather/ && python ./manage.py runlistener
5 * * * * /home/weather/bin/check_weather_running.sh
0 5 * * * /home/weather/bin/weather restart
```

TODO
----

 - clean up hostnames and network-config
 - huge TODO: can all these setup-shenanigans be handled via puppet?  Abhiram says: "Once the sym-links and directories are created, may be this task can be automated. Will think about this later."
 - Upgrade VM to latest Wheezy release.  We could ask Puppet to update the distro.  But that would mean everyone would have to download the new distro when starting the VM for the first time and whenever they run `vagrant provision`.  Maybe there are better ways.  Like, Puppet Labs releasing a new image.
 - Cron-tab with Puppet. Try to add the background task as a cron job using puppet.  Unless that's something we don't want in the development environment.  Let's postpone this.
