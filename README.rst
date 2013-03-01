TracBacklog
===========

This plugin is meant to help you with your agile process using Trac.  One of
the key practices of agile development, is prioritizing the backlog.  That
can be difficult to do in Trac, as it doesn't have any way of doing
fine-grained ranking of tickets.  This plugin helps resolve that
short-coming.

TracBacklog adds a new navigational element to your navigation bar.
Clicking on it will take you to the unscheduled backlog (all active tickets
that aren't currently assigned to a milestone).  On the right hand side,
is a listing of open milestones.  The idea is that you drag-n-drop tickets
within the list itself to change their rank.  Once you're happy with the
ranking (i.e., you've worked with your customer to prioritize the outstanding
tickets), you drag-n-drop tickets onto a milestone to assign it into the
milestone.  This effectively treats milestones as sprints, which works well
for us... and I hope it works well for you!

The unscheduled backlog is created from tickets that are not assigned
to any milestone.  You can also view each milestone and see and individual
backlog for it, but all tickets are ranked absolutely (they maintain their
absolute ranking when you drag them in and out of a milestone).  Furthermore,
if you are trying this on an existing project, the initial rank for each
ticket will be it's ticket id.  You'll want to spend some time sorting your
tickets, and you may want to consider pulling them all into the unscheduled
backlog when you do that (so that you can order the all the tickets against
each other).


Dependencies
------------

It requires simplejson 2.0 or better, and Trac 0.11 or better.


Installation
------------

Using ``easy_install``::

    $ easy_install -U TracBacklog

From a tarball::

    python setup.py install

Enable the plugin in trac.ini::

    [components]
    backlog.* = enabled


Configuration
-------------

Users can customize the fields they see in the Backlog preference pane.

Also, you will need to run ``trac-admin upgrade`` on your database, since the
plugin needs to create a table and some default values for your tickets.


Bugs/Feature Requests
---------------------

Please use the
`GitHub site <https://github.com/jszakmeister/trac-backlog/issues>`_ to file any
bug and feature requests.


Source
------

The plugin is maintained on
`GitHub <https://github.com/jszakmeister/trac-backlog>`_.


Other Solutions
---------------

A Trac plug-in to help folks use Trac to maintain their backlog when using an
agile development methodology. See also
`TracKanbanBoard <https://pypi.python.org/pypi/TracKanbanBoard/0.2>`_,
`BacklogPlugin <https://trac-hacks.org/wiki/BacklogPlugin>`_,
`AgiloForTracPlugin <https://trac-hacks.org/wiki/AgiloForTracPlugin>`_,
`IttecoTracPlugin <https://trac-hacks.org/wiki/IttecoTracPlugin>`_.
