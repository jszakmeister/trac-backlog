# Copyright (C) 2009, 2012 John Szakmeister
# All rights reserved.
#
# This software is licensed as described in the file LICENSE.txt, which
# you should have received as part of this distribution.

from trac.db import Table, Column, Index


# The version of the database schema
schema_version = 1

# The database schema for the backlog module
schema = [
  Table('backlog', key='ticket_id')[
    Column('ticket_id', type='int'),
    Column('rank', type='int'),
    Index(['ticket_id'], unique=True),
  ]
]

