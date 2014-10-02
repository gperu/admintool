#Attempt to connect to a remote database mysql.researchcomputing.org.uk swcuk

import os
import sys
import sqlite3
import MySQLdb 
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool, NullPool
from sqlalchemy.orm import sessionmaker

ROOT = os.path.abspath(os.path.dirname(__file__))
path = lambda *x: os.path.normpath(os.path.join(ROOT, *x))

RUNNING_TESTS = 'nose' in sys.modules

SWCARPENTRY_ADMIN_PATH = os.environ.get('SWCARPENTRY_ADMIN_PATH')
if RUNNING_TESTS or SWCARPENTRY_ADMIN_PATH is None:
    SWCARPENTRY_ADMIN_PATH = os.curdir

ROSTER_DB = 'roster.test.db' if RUNNING_TESTS else 'roster.db'
ROSTER_DB_PATH = os.path.join(SWCARPENTRY_ADMIN_PATH, ROSTER_DB)

_engine = None
_Session = None

def get_engine():
    global _engine

    if _engine is None:
        _engine = create_engine(
            'sqlite:///%s' % ROSTER_DB_PATH,
            connect_args={'check_same_thread':False},
            poolclass=NullPool if RUNNING_TESTS else StaticPool
        )
    return _engine

def get_session():
    global _Session

    if _Session is None:
        _Session = sessionmaker(bind=get_engine())
    return _Session()

def add_users(users):
  #Here we would want to actually insert the users list into the database.
  #Using SQLAlchemy is a little beyond my Python expertise, so I think it is
  #best if I leave that to someone who knows what they are doing instead of
  #hacking some poor solution together that'll need to be redone anyway.
  return True

def create_roster_db():
    '''
    Create roster.db in the Software Carpentry admin directory by
    feeding it roster.sql.

    This is normally done by the Makefile, but doing it ourselves
    here relieves many users of an annoying dependency on make.
    '''

    roster_sql_path = os.path.join(os.path.dirname(ROSTER_DB_PATH),
                                   'roster.sql')
    
    roster_sql_path = ''
    print "Reading from %s." % roster_sql_path
    print "Creating %s." % ROSTER_DB_PATH

    conn = sqlite3.connect(ROSTER_DB_PATH)
    c = conn.cursor()
    c.executescript(open(roster_sql_path).read())
    c.close()
    conn.close()
    
    
def connect_remote_db():
    db = MySQLdb.connect(host="mysql.researchcomputing.org.uk", user="swcuk", passwd="where_is_greg_wilson", db="swcuk")    
    cur = db.cursor()
    cur.execute("CREATE TABLE Test")
    db.commit()
    db.close()
        
'''
db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="john", # your username
                      passwd="megajonhy", # your password
                      db="jonhydb") # name of the data base

# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor() 

# Use all the SQL you like
cur.execute("SELECT * FROM YOUR_TABLE_NAME")

# print all the first cell of all the rows
for row in cur.fetchall() :
    print row[0]
'''    
    
    

if RUNNING_TESTS:
    def setup():
        if os.path.exists(ROSTER_DB_PATH):
            os.unlink(ROSTER_DB_PATH)
        #create_roster_db()
        connect_remote_db()

    def teardown():
        global _Session
        global _engine

        if _Session:
            _Session.close_all()
            _Session = None
        if _engine:
            _engine.dispose()
            _engine = None
        if os.path.exists(ROSTER_DB_PATH):
            os.unlink(ROSTER_DB_PATH)

if __name__ == '__main__':
    print 'Using the database at %s.' % ROSTER_DB_PATH
