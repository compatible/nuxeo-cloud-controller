Nuxeo Cloud Controler
=====================

The project currently provides a "ncc" command-line tool that allows to
create, start, stop and destroy Nuxeo instances on a dedicated server
(or VM). 

Note: this command-line tool is not supposed to be used on the server,
so it's really useful for a sysadmin or to experiment with the system.
It is not a command-line tools for developers (a la 'bees' or 'vmc').

What it does
------------

- Manage instances (creates them from a model, setup the config file,
  wire them behind nginx)
- Stop them after some inactivity
- When an instance is stopped, point nginx to a small webserver that
  will restart the instance when a web request is made to it

Install
-------

Simply running "python setup.py install" should be enough.

You can also use "make env" to create a virtualenv, then activate it
with "source env/bin/activate".

Using
-----

The config is hardcoded in config.py. However, this is easy to fix.

Typical scenario is:

- ncc boot # starts nginx, mostly
- ncc create 
- ncc stop <iid>
- ncc destroy <iid>

Run "ncc help" for more info.

I parallel, you need to start the web server ("ncc server") and from
time to time (i.e. using a crontab) to run "ncc monitor".

TODO
----

Lots of things:

- Pass parameters to ncc create (like: admin email, hostname, etc.)
- One possibility is to move all the current scripts (only useful for
  testing) to the web server
- Make a nice admin interface using the web server
- Make an end-user interface using the web server ?
- Create a command-line tool for the users (a la vmc) ?

Cleanup:

- Ensure that everything is rock-solid.
