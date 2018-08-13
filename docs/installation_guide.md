# Rapid Annotator Installation Guide

Install and configure **apache2** for python3 on your server.

Install **wsgi** for python3 on your server, by running the following command

`sudo apt-get install python3-pip libapache2-mod-wsgi-py3`

If you have an wsgi for python2 installed then: first uninstall it by the
following command and then run the above command

`sudo apt-get install python3-pip libapache2-mod-wsgi-py3`


Install **python3-mysqldb**.

Run

`git clone https://github.com/guptavaibhav18197/rapidannotator.git`

`cd rapidannotator`

`sudo su`

`pip3 install -r requirements.txt`


Since we need to deploy rapidannotator [flask app] on apache server, we need to link Flask and Apache using wsgi interface. For that you need to add the following lines in `/etc/apache2/sites-enabled/000-default.conf`

```
<VirtualHost *:8000>

    WSGIScriptAlias / /var/www/rapidannotator/wsgi.py

    <Directory /var/www/rapidannotator>

      Require all granted

    </Directory>

</VirtualHost>
```

Add the following line to listen to port 8000 in `/etc/apache2/ports.conf`

```Listen 8000```


Next, in _wsgi.py_ file in the rapidannotator replace the current path i.e.

`[Path_to_rapidannotator]/rapidannotator` to `/path/to/rapidannotator`

After that run : `sudo service apache2 restart`

As the last step we need to link the database[MySQL] to rapidannotator.

Login to MySQL : `mysql -u root -p`

Create a database for rapidannotator and select it :

`create database [database_name];`

`use [database_name];`

Now grant the privileges to rapidannotator :

`grant all privileges on [Database_name].* to username@localhost;`

Now set an identification password for the user :

`alter user username@localhost identified by 'password';`

Tell the server to reload the grant tables

`flush privileges;`

Finally in _rapidannotator/config.py_ update the database uri :

`SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost/[Database_name]'`

Run the following in the directory where rapidannotator is kept.

`mkdir -p [Path_to_storage_directory]`

Change [this line](https://github.com/guptavaibhav18197/rapidannotator/blob/master/rapidannotator/config.py#L14) accordingly.


After running the above steps you should be able to access the interface at http://localhost/frontpage/ in your browser.

Create a user there and make it admin by running the following command in mysql database.

`UPDATE User SET admin=1  WHERE id='X';`

Here X is the id of the user you want to make the admin.

Follow the user guide to proceed with the rest of the process. :)
