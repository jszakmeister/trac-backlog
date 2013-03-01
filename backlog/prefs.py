# Copyright (C) 2011 Brent Atkinson
# All rights reserved.
#
# This software is licensed as described in the file LICENSE.txt, which
# you should have received as part of this distribution.

from trac.core import *
from trac.prefs import IPreferencePanelProvider
from trac.util.translation import _
from trac.web.chrome import add_notice, ITemplateProvider

class BacklogPluginPrefPanel(Component):
    implements(IPreferencePanelProvider, ITemplateProvider)

    _form_fields = [ 
        'id', 'summary', 'component', 'version', 'type', 'owner', 'status',
        'time_created'
    ]

    # IPreferencePanelProvider methods

    def get_preference_panels(self, req):
        yield ('backlog', _('Backlog'))


    def render_preference_panel(self, req, panel):
        if req.method == 'POST':
            fields = req.args.get('backlog_fields')
            req.session['backlog_fields'] = fields
            add_notice(req,_('Your backlog preferences have been saved.'))
            req.redirect(req.href.prefs(panel or None))

        return 'prefs_backlog.html', {
            'shown_fields':
                req.session.get('backlog_fields') or self._form_fields
        }

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        from pkg_resources import resource_filename
        return [('backlog', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        from pkg_resources import resource_filename
        return [resource_filename(__name__, 'templates')]
