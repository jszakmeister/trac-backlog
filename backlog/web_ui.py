from trac.core import *
from trac.db import DatabaseManager
from trac.env import IEnvironmentSetupParticipant
from trac.web.chrome import INavigationContributor
from trac.web.main import IRequestHandler
from trac.util import escape, Markup
from trac.util.html import html

from backlog.schema import schema_version, schema


class BacklogPlugin(Component):
    implements(INavigationContributor, IRequestHandler, IEnvironmentSetupParticipant)

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
        yield 'mainnav', 'backlog', html.A('Backlog', href=req.href.backlog())

    # IRequestHandler methods
    def match_request(self, req):
        return (req.path_info == '/backlog') or (req.path_info == '/backlog/')

    def process_request(self, req):
        req.send_response(200)
        req.send_header('Content-Type', 'text/plain')
        req.end_headers()
        req.write('Hello world!')
