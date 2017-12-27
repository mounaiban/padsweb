Public Archive of Days Since Timers
===================================

*A Long-term Stopwatch App*

Django/web version

About
*****

PADS is basically a web browser-operated version of those "days since"
apps you find all over Google Play, App Store and such, but intended to
be accessible from about any device with a web browser and internet
access. If you wish, you can hack it to work offline or set up your own
instance in an intranet. And I promise, there will be no "special offers"
in this personally-sanctioned version of this app.

Requirements
************

Minimum Requirements
--------------------
* Python 3.6
* Django (1.11.2, 2.0 is not yet supported)
* pytz (2017.2)

PADS should work with later versions of the above dependencies either
out of the box, or with minimal changes. The only reason PADS requires 
Python 3.6 is because it uses the ``secrets`` module which was 
introduced in this version.

Optional Requirements
---------------------
If just the minimum requirements are met, PADS will function only 
as a Django test application. For production-grade deployments, you
may need to install additional packages in your Python environment 
to make use of more sophisticated hosting solutions. Version numbers
are recommendations only.

* mod-wsgi (4.5.15), required if hosting with dedicated HTTP server software via WSGI.
* mysqlclient (1.3.10), required if using PADS with MySQL or MariaDB.

License
*******

PADS is licensed under the MIT License, so you're welcome to do whatever
you like to it, whether it's improving your life, using it as the basis
of the next quantum leap in social media technology, or heaven forbid, 
adding those "special offers".
