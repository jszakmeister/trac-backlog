from trac.db import Table, Column, Index


# The version of the database schema
schema_version = 1

# The database schema for the backlog module
schema = [
  Table('backlog_priority_table', key='ticket_id')[
    Column('ticket_id', type='int', unique=True),
    Column('priority', type='int'),
  ]
]

