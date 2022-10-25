Public Archive of Days Since Timers
===================================

About
*****

*PADS* was a time tracker web app (a website in old school terms) that
kept and displayed the amount of time that had happened since a
user-defined point in time. For example, one could make timers that
counted the days since they quit a habit, or filed a complaint.
It also allowed the creation of *historical* timers that were intended
to count the time passed since a past event.

Timers could be kept private or shared with the general public.
Registration was needed to create and share timers. Quick Lists could
be created as a temporary alternative to a full registration.
The ability to import Quick Lists into a full account was planned, but
never implemented.

This app project was my first serious attempt at building a web
application and was intended to be a submission for an undergraduate
assignment (an alternate submission was made instead). PADS evolved
into a challenge to implement as much functionality as possible
without JavaScript.

Upon realising that the project was out of touch with the evolution of
web app tech, PADS was scrapped in 2018 to make way for other
projects. This project has been both a pride and an embarrassment;
I really believe something like PADS would be really popular and
useful, and I reckon the only way to redeem the project is to start
from scratch with a more up-to-date architecture.

This project will not be updated. Any further endeavours will be
carried on in a successor project.

Requirements
************

Requirements
------------

* Python 3.6
* Django == 2.2.28
* pytz (>= 2017.2)

This app was only ever tested on Linux servers. Windows users are
encouraged to run the app on a GNU/Linux distro with WSL.

Optional Requirements
---------------------

A more robust depolyment is possible with a dedicated, load-balancing
web and database servers. PADS has been deployed in the past with the
Apache HTTP Server (httpd) with ``mod-wsgi`` (tested on 4.5.15).
As a Django app, a dedicated SQL database server can be hooked up
using the optional ``mysqlclient`` (tested on 1.3 with MariaDB) pip
package.

Setup
*****

The old `Installation Instructions <https://github.com/mounaiban/padsweb/wiki/Installation-Instructions/>`_
remain in the Wiki as a historical reference.

A Dockerfile has been included to let you skip the rather long-winded
(by 2020s standards) setup process; just run:

::

    docker build -t padsweb:0.5-demo .
    docker run -dp 9180:80 --rm --name pads padsweb:0.5-demo

Here's the non-volatile version that retains accounts and timers:

::

    docker volume create padsweb-data
    docker build -t padsweb:0.5-demo .
    docker run -dp 9180:80 -v padsweb-data:/usr/share/ --rm --name pads padsweb:0.5-demo

Both versions will set up a running instance on port 9180 on the host
at ``/pads``. When running on a local machine, try
http://localhost:9180/pads. The port can be overidden with the
``PADS_PORT`` environment variable on the host when building the
container image.

Remember to ``docker stop pads`` when you are done, and
``docker volume rm padsweb-data`` to delete data left behind by the
non-volatile version.

Use ``podman`` in place of ``docker`` as appropriate.

License
*******

PADS is Free Software, licensed under the terms and conditions of
the **MIT License**.
