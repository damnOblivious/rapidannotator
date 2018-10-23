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

Copy wsgi_template.py to wsgi.py and make the required changes in the new file.

`cp wsgi_template.py wsgi.py`

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

To enable full utf8 support, check if you mysql already supports full utf8 by running the following command

`SHOW VARIABLES WHERE Variable_name LIKE 'character\_set\_%' OR Variable_name LIKE 'collation%';`

If it shows utf8 instead of utf8mb4 then add the following lines in `/etc/mysql/my.cnf` file otherwise move to next step.

```
[client]
default-character-set = utf8mb4

[mysql]
default-character-set = utf8mb4

[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
```

For more information check this [guide](https://mathiasbynens.be/notes/mysql-utf8mb4)

Now, create a database for rapidannotator and select it :

`create database [database_name];`

`use [database_name];`

Now grant the privileges to rapidannotator :

`grant all privileges on [Database_name].* to username@localhost;`

Now set an identification password for the user :

`alter user username@localhost identified by 'password';`

Tell the server to reload the grant tables

`flush privileges;`

Copy config_template.py to config.py and make the required changes in the new file.

`cp config_template.py config.py`

Finally in _rapidannotator/config.py_ update the database uri :

`SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost/[Database_name]'`

Run the following in the directory where rapidannotator is kept.

`mkdir -p [Path_to_storage_directory]`

Change [this line](https://github.com/guptavaibhav18197/rapidannotator/blob/master/rapidannotator/config_template.py#L9) accordingly.


After running the above steps you should be able to access the interface at http://localhost:8000/frontpage/ in your browser.

Create a user there and make it admin by running the following command in mysql database.

`UPDATE User SET admin=1  WHERE id='X';`

Here X is the id of the user you want to make the admin.

Follow the user guide to proceed with the rest of the process. :)
