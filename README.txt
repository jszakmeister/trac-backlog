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

Bugs
====

There are no known bugs at this time.  If you do find some, please report
them to:
   <https://github.com/jszakmeister/trac-backlog/issues>


Main Website
============

This project was previously hosted on Launchpad.  It has since moved to
GitHub.  You can find more about the project at:
   <https://github.com/jszakmeister/trac-backlog>

