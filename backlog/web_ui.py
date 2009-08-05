import re
import simplejson

from trac.core import *
from trac.db import DatabaseManager
from trac.env import IEnvironmentSetupParticipant
from trac.ticket.api import ITicketChangeListener
from trac.ticket.model import Ticket
from trac.web.chrome import INavigationContributor, ITemplateProvider, add_script
from trac.web.main import IRequestHandler
from trac.web.api import HTTPBadRequest
from trac.util.html import html

from backlog.schema import schema_version, schema


BACKLOG_QUERY = '''SELECT p.value AS __color__,
   id AS ticket, summary, component, version, milestone, t.type AS type, 
   owner, status,
   time AS created,
   changetime AS _changetime, description AS _description,
   reporter AS _reporter
  FROM ticket t
  LEFT JOIN enum p ON p.name = t.priority AND p.type = 'priority'
  LEFT JOIN backlog_priority_table bp ON bp.ticket_id = t.id 
  WHERE status <> 'closed'
  ORDER BY bp.priority, CAST(p.value AS int), milestone, t.type, time
'''



class BacklogPlugin(Component):
    implements(INavigationContributor, IRequestHandler, 
               IEnvironmentSetupParticipant, ITemplateProvider,
               ITicketChangeListener)

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


    # INavigationContributor methods
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
            cursor.execute("INSERT INTO backlog_priority_table VALUES (%s, %s)",
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
        match = re.match(r'/backlog(?:/(move_after|move_before))?/?',
                         req.path_info)
        if match:
            return True
        return False

    def process_request(self, req):
        req.perm.require('TICKET_VIEW')
        if req.method == 'POST':
           req.perm.require('TICKET_MODIFY')

           if 'move_after' in req.path_info:
               return self._move_after(req)
           elif 'move_before' in req.path_info:
               return self._move_before(req)
           else:
               raise HTTPBadRequest("Invalid POST request")

        data = {
            'title': 'Backlog',
        }

        class Report(object):
            def __init__(self):
                self.id = -1

        data['tickets'] = self._get_active_tickets()
        data['form_token'] = req.form_token

        if 'TICKET_MODIFY' in req.perm:
            data['allow_sorting'] = True

        add_script(req, 'backlog/js/jquery-ui.js')
        return 'backlog.html', data, None

    def _get_active_tickets(self):
        db = self.env.get_db_cnx()
        cursor = db.cursor()

        try:
            cursor.execute(BACKLOG_QUERY)
        except:
            db.rollback()
            raise

        tickets = []

        for row in cursor:
            t = Ticket(self.env, row[1])
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

            cursor.execute('SELECT priority FROM backlog_priority_table WHERE ticket_id = %s',
                           (ticket_id,))
            old_priority = cursor.fetchone()[0]

            cursor.execute('SELECT priority FROM backlog_priority_table WHERE ticket_id = %s',
                           (before_ticket_id,))
            new_priority = cursor.fetchone()[0]

            if new_priority > old_priority:
                cursor.execute(
                    'UPDATE backlog_priority_table SET priority = priority - 1 WHERE priority > %s AND priority < %s',
                    (old_priority, new_priority))
                new_priority -= 1
            else:
                cursor.execute(
                    'UPDATE backlog_priority_table SET priority = priority + 1 WHERE priority >= %s AND priority < %s',
                    (new_priority, old_priority))

            cursor.execute(
                'UPDATE backlog_priority_table SET priority = %s WHERE ticket_id = %s',
                (new_priority, ticket_id))

            db.commit()
        except:
            db.rollback()
            to_result['msg'] = 'Error trying to update priority'
            import traceback
            print traceback.print_exc()

        data = simplejson.dumps(to_result)

        if 'msg' in to_result:
            req.send_response(202)
        else:
            req.send_response(200)
        req.send_header('Content-Type', 'application/json')
        req.end_headers()
        req.write(data)


    def _move_after(self, req):
        ticket_id = int(req.args.get('ticket_id'))
        after_ticket_id = int(req.args.get('after_ticket_id'))

        ticket = Ticket(self.env, ticket_id)
        other = Ticket(self.env, after_ticket_id)

        to_result = {}

        db = self.env.get_db_cnx()

        try:
            cursor = db.cursor()

            cursor.execute('SELECT priority FROM backlog_priority_table WHERE ticket_id = %s',
                           (ticket_id,))
            old_priority = cursor.fetchone()[0]

            cursor.execute('SELECT priority FROM backlog_priority_table WHERE ticket_id = %s',
                           (after_ticket_id,))
            new_priority = cursor.fetchone()[0]

            if old_priority < new_priority:
                cursor.execute(
                    'UPDATE backlog_priority_table SET priority = priority - 1 WHERE priority > %s AND priority <= %s',
                    (old_priority, new_priority))
            elif old_priority >= new_priority:
                cursor.execute(
                    'UPDATE backlog_priority_table SET priority = priority - 1 WHERE priority > %s AND priority <= %s',
                    (old_priority, new_priority))
                new_priority += 1

            cursor.execute(
                'UPDATE backlog_priority_table SET priority = %s WHERE ticket_id = %s',
                (new_priority, ticket_id))

            db.commit()
        except:
            db.rollback()
            to_result['msg'] = 'Error trying to update priority'
            raise

        data = simplejson.dumps(to_result)

        if 'msg' in to_result:
            print "error:", to_result['msg']
            req.send_response(202)
        else:
            req.send_response(200)
        req.send_header('Content-Type', 'application/json')
        req.end_headers()
        req.write(data)


