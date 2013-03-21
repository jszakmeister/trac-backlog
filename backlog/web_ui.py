# Copyright (C) 2009 John Szakmeister
# All rights reserved.
#
# This software is licensed as described in the file LICENSE.txt, which
# you should have received as part of this distribution.

import re
import simplejson

from trac.core import *
from trac.db import DatabaseManager
from trac.env import IEnvironmentSetupParticipant
from trac.perm import IPermissionRequestor
from trac.ticket.api import ITicketChangeListener
from trac.ticket.model import Ticket
from trac.web.chrome import INavigationContributor, ITemplateProvider
from trac.web.chrome import add_script, add_stylesheet
from trac.web.main import IRequestHandler
from trac.web.api import HTTPBadRequest, RequestDone
from trac.util.datefmt import format_date
from trac.util.html import html
from trac.util import get_reporter_id

from backlog.schema import schema_version, schema


BACKLOG_QUERY = '''SELECT id FROM ticket t
  LEFT JOIN enum p ON p.name = t.priority AND p.type = 'priority'
  LEFT JOIN backlog bp ON bp.ticket_id = t.id
  WHERE status <> 'closed' AND milestone = %s
  ORDER BY bp.rank, CAST(p.value AS int), t.type, time
'''

# Need a separate unscheduled backlog query since deleting a
# milestone and re-targeting a ticket can set the milestone field
# to null, instead of the empty string.
UNSCHEDULED_BACKLOG_QUERY = '''SELECT id FROM ticket t
  LEFT JOIN enum p ON p.name = t.priority AND p.type = 'priority'
  LEFT JOIN backlog bp ON bp.ticket_id = t.id
  WHERE status <> 'closed' AND (milestone = '' or milestone is null)
  ORDER BY bp.rank, CAST(p.value AS int), t.type, time
'''

MILESTONE_QUERY = '''SELECT name, due FROM milestone
  WHERE completed == 0
  ORDER BY (due == 0), due, UPPER(name), name
'''



class BacklogPlugin(Component):
    implements(INavigationContributor, IRequestHandler,
               IEnvironmentSetupParticipant, ITemplateProvider,
               ITicketChangeListener, IPermissionRequestor)

    _ticket_fields = [ 
        'id', 'summary', 'component', 'version', 'type', 'owner', 'status', 
        'time_created'
    ]

    # IEnvironmentSetupParticipant
    def environment_created(self):
        connector, args = DatabaseManager(self.env)._get_connector()
        to_sql = connector.to_sql
        db = self.env.get_db_cnx()
        cur = db.cursor()

        for table in schema:
            sql = to_sql(table)
            for stmt in sql:
                cur.execute(stmt)

        # Insert version information
        cur.execute("INSERT INTO system (name,value) "
                    "VALUES ('backlog_schema_version', %s)" % (
                        str(schema_version)))

    def environment_needs_upgrade(self, db):
        cur = db.cursor()
        cur.execute("SELECT value FROM system WHERE name='backlog_schema_version'")
        row = cur.fetchone()
        if not row or int(row[0]) < schema_version:
            return True

        cur.execute("SELECT COUNT(*) FROM ticket")
        tickets = cur.fetchone()[0]

        no_backlog = False
        try:
            cur.execute("SELECT COUNT(*) FROM backlog")
            backlog_entries = cur.fetchone()[0]
        except OperationalError:
            no_backlog = True

        if no_backlog:
            return True

        if tickets != backlog_entries:
            return True

        return False

    def upgrade_environment(self, db):
        cur = db.cursor()
        cur.execute("SELECT value FROM system WHERE name='backlog_schema_version'")
        row = cur.fetchone()

        if not row:
            self.environment_created()
        elif int(row[0]) < schema_version:
            ### Pass we need to do an upgrade...
            ### We'll implement that later. :-)
            pass

        # Make sure that all tickets have a rank
        cur.execute("SELECT t.id FROM ticket AS t LEFT JOIN backlog " +
                    "ON t.id = backlog.ticket_id WHERE backlog.ticket_id IS NULL")

        for row in cur.fetchall():
            ticket_id = row[0]

            # Insert a default rank for the ticket, using the ticket id
            cur.execute("INSERT INTO backlog VALUES (%s,%s)",
                        (ticket_id, ticket_id))

        db.commit()

    # INavigationContributor methods
    def get_permission_actions(self):
        return ['BACKLOG_ADMIN']

    def get_active_navigation_item(self, req):
        return 'backlog'

    def get_navigation_items(self, req):
        if 'TICKET_VIEW' in req.perm:
            yield 'mainnav', 'backlog', html.A('Backlog', href=req.href.backlog())

    # ITemplateProvider
    def get_htdocs_dirs(self):
        from pkg_resources import resource_filename
        return [('backlog', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        from pkg_resources import resource_filename
        return [resource_filename(__name__, 'templates')]

    # ITicketChangeListener
    def ticket_created(self, ticket):
        db = self.env.get_db_cnx()
        cursor = db.cursor()

        try:
            cursor.execute("INSERT INTO backlog VALUES (%s, %s)",
                           (ticket.id, ticket.id))
            db.commit()
        except:
            db.rollback()
            raise

    def ticket_changed(self, ticket, comment, author, old_values):
        pass

    def ticket_deleted(ticket):
        pass

    # IRequestHandler methods
    def match_request(self, req):
        match = re.match(r'/backlog(?:/(move_after|move_before|assign|milestone/(?:[^/]+)))?/?',
                         req.path_info)
        if match:
            return True
        return False

    def process_request(self, req):
        
        req.perm.require('TICKET_VIEW')
        if req.method == 'POST':
            req.perm.require('BACKLOG_ADMIN')

            if 'move_after' in req.path_info:
                return self._move_after(req)
            elif 'move_before' in req.path_info:
                return self._move_before(req)
            elif 'assign' in req.path_info:
                return self._assign_milestone(req)
            else:
                raise HTTPBadRequest("Invalid POST request")

        if req.path_info.startswith('/backlog/milestone/'):
            milestone = req.path_info[19:]
        else:
            milestone = None

        if milestone == '(unscheduled)':
            milestone = None

        data = {
            'title': (milestone or "Unscheduled"),
        }

        class Report(object):
            def __init__(self):
                self.id = -1

        data['tickets'] = self._get_active_tickets(milestone)
        data['form_token'] = req.form_token
        data['active_milestones'] = self._get_active_milestones(milestone)
        data['base_path'] = req.base_path
        data['shown_fields'] = req.session.get('backlog_fields') or self._ticket_fields

        if 'BACKLOG_ADMIN' in req.perm:
            data['allow_sorting'] = True

        add_stylesheet(req, 'backlog/css/backlog.css')

        return 'backlog.html', data, None

    def _get_active_tickets(self, milestone = None):
        db = self.env.get_db_cnx()
        cursor = db.cursor()

        try:
            if milestone is None:
                # Check the comment for UNSCHEDULED_BACKLOG_QUERY about
                # why this is necessary.
                cursor.execute(UNSCHEDULED_BACKLOG_QUERY)
            else:
                cursor.execute(BACKLOG_QUERY, (milestone,))
        except:
            db.rollback()
            raise

        tickets = []

        for row in cursor:
            t = Ticket(self.env, row[0])
            tickets.append(t)

        return tickets

    def _move_before(self, req):
        ticket_id = int(req.args.get('ticket_id'))
        before_ticket_id = int(req.args.get('before_ticket_id'))

        ticket = Ticket(self.env, ticket_id)
        other = Ticket(self.env, before_ticket_id)

        to_result = {}

        db = self.env.get_db_cnx()

        try:
            cursor = db.cursor()

            cursor.execute('SELECT rank FROM backlog WHERE ticket_id = %s',
                           (ticket_id,))
            old_rank = cursor.fetchone()[0]

            cursor.execute('SELECT rank FROM backlog WHERE ticket_id = %s',
                           (before_ticket_id,))
            new_rank = cursor.fetchone()[0]

            if new_rank > old_rank:
                cursor.execute(
                    'UPDATE backlog SET rank = rank - 1 WHERE rank > %s AND rank < %s',
                    (old_rank, new_rank))
                new_rank -= 1
            else:
                cursor.execute(
                    'UPDATE backlog SET rank = rank + 1 WHERE rank >= %s AND rank < %s',
                    (new_rank, old_rank))

            cursor.execute(
                'UPDATE backlog SET rank = %s WHERE ticket_id = %s',
                (new_rank, ticket_id))

            db.commit()
        except:
            db.rollback()
            to_result['msg'] = 'Error trying to update rank'
            import traceback
            print traceback.print_exc()

        data = simplejson.dumps(to_result)

        if 'msg' in to_result:
            req.send_response(202)
        else:
            req.send_response(200)
        req.send_header('Content-Type', 'application/json')
        req.send_header('Content-Length', len(data))
        req.end_headers()
        req.write(data)


    def _move_after(self, req):
        ticket_id = int(req.args.get('ticket_id'))
        after_ticket_id = int(req.args.get('after_ticket_id'))

        to_result = {}

        db = self.env.get_db_cnx()

        try:
            cursor = db.cursor()

            cursor.execute('SELECT rank FROM backlog WHERE ticket_id = %s',
                           (ticket_id,))
            old_rank = cursor.fetchone()[0]

            cursor.execute('SELECT rank FROM backlog WHERE ticket_id = %s',
                           (after_ticket_id,))
            new_rank = cursor.fetchone()[0]

            if old_rank < new_rank:
                cursor.execute(
                    'UPDATE backlog SET rank = rank - 1 WHERE rank > %s AND rank <= %s',
                    (old_rank, new_rank))
            elif old_rank >= new_rank:
                cursor.execute(
                    'UPDATE backlog SET rank = rank + 1 WHERE rank > %s AND rank <= %s',
                    (new_rank, old_rank))
                new_rank += 1

            cursor.execute(
                'UPDATE backlog SET rank = %s WHERE ticket_id = %s',
                (new_rank, ticket_id))

            db.commit()
        except:
            db.rollback()
            to_result['msg'] = 'Error trying to update rank'
            raise

        self._get_active_tickets()

        data = simplejson.dumps(to_result)

        if 'msg' in to_result:
            print "error:", to_result['msg']
            req.send_response(202)
        else:
            req.send_response(200)
        req.send_header('Content-Type', 'application/json')
        req.send_header('Content-Length', len(data))
        req.end_headers()
        req.write(data)

    def _get_num_tickets(self, cursor, milestone):
        cursor.execute("SELECT COUNT(*) FROM ticket WHERE status <> 'closed' AND milestone = %s",
                       (milestone,));
        return cursor.fetchone()[0]

    def _get_active_milestones(self, exclude = None):
        '''Retrieve a list of milestones.  If exclude is specified, it
        will exclude that milestone from the list and add in the unscheduled
        milestone.'''
        db = self.env.get_db_cnx()

        cursor = db.cursor()

        results = []

        if exclude:
            num_tickets = self._get_num_tickets(cursor, '')
            results.append(
                dict(name='(unscheduled)', due='--', num_tickets=num_tickets))

        cursor.execute(MILESTONE_QUERY)

        rows = cursor.fetchall()

        for row in rows:
            if exclude and exclude == row[0]:
                continue

            num_tickets = self._get_num_tickets(cursor, row[0])

            d = dict(name=row[0],
                     due=(row[1] and format_date(row[1])) or '--',
                     num_tickets=num_tickets)
            results.append(d)

        return results

    def _assign_milestone(self, req):
        ticket_id = int(req.args.get('ticket_id'))
        milestone = req.args.get('milestone')
        author = get_reporter_id(req, 'author')

        if milestone == '(unscheduled)':
            milestone = ''

        to_result = {}

        ticket = None
        try:
            ticket = Ticket(self.env, ticket_id)
        except:
            to_result['msg'] = "Couldn't find ticket!"

        if ticket:
            db = self.env.get_db_cnx()

            cursor = db.cursor()

            try:
                ticket['milestone'] = milestone
                ticket.save_changes(author, "");

                to_result['num_tickets'] = self._get_num_tickets(cursor, milestone)
            except:
                to_result['msg'] = "Unable to assign milestone"

        data = simplejson.dumps(to_result)

        if 'msg' in to_result:
            print "error:", to_result['msg']
            req.send_response(202)
        else:
            req.send_response(200)

        req.send_header('Content-Type', 'application/json')
        req.send_header('Content-Length', len(data))
        req.end_headers()
        req.write(data)
        #raise RequestDone

