#!/usr/bin/env python3

from modules import pg8000
import configparser


################################################################################
# Connect to the database
#   - This function reads the config file and tries to connect
#   - This is the main "connection" function used to set up our connection
################################################################################

def database_connect():
    # Read the config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Create a connection to the database
    connection = None
    try:
        '''
        This is doing a couple of things in the back
        what it is doing is:

        connect(database='y12i2120_unikey',
            host='soit-db-pro-2.ucc.usyd.edu.au,
            password='password_from_config',
            user='y19i2120_unikey')
        '''
        connection = pg8000.connect(database=config['DATABASE']['user'],
                                    user=config['DATABASE']['user'],
                                    password=config['DATABASE']['password'],
                                    host=config['DATABASE']['host'])
    except pg8000.OperationalError as e:
        print("""Error, you haven't updated your config.ini or you have a bad
        connection, please try again. (Update your files first, then check
        internet connection)
        """)
        print(e)
    except pg8000.ProgrammingError as e:
        print("""Error, config file incorrect: check your password and username""")
        print(e)
    except Exception as e:
        print(e)

    # Return the connection to use
    return connection


################################################################################
# Login Function
#   - This function performs a "SELECT" from the database to check for the
#       student with the same unikey and password as given.
#   - Note: This is only an exercise, there's much better ways to do this
################################################################################

def check_login(sid, pwd):
    # Ask for the database connection, and get the cursor set up
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT *
                 FROM unidb.student
                 WHERE studid=%s AND password=%s"""
        cur.execute(sql, (sid, pwd))
        r = cur.fetchone()              # Fetch the first row
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Error Invalid Login")
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


################################################################################
# List Units
#   - This function performs a "SELECT" from the database to get the unit
#       of study information.
#   - This is useful for your part when we have to make the page.
################################################################################

def list_units():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        cur.execute("""SELECT uosCode, uosName, credits, year, semester
                        FROM UniDB.UoSOffering JOIN UniDB.UnitOfStudy USING (uosCode)
                        ORDER BY uosCode, year, semester""")
        val = cur.fetchall()
    except:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching from database")

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val


################################################################################
# Get transcript function
#   - Performs a SELECT query on a given sid's transcript
################################################################################

def get_transcript(sid):
    # TODO
    # Get the students transcript from the database
    # You're given an SID as a variable 'sid'
    # Return the results of your query :)
    conn = database_connect()
    if conn is None:
        return None
    
    cur = conn.cursor()
    result = None
    try:
        cur.execute("""SELECT uoscode, uosname, credits, year, semester, grade 
                       FROM UniDB.UnitOfStudy JOIN UniDB.Transcript USING (uoscode) 
                       WHERE studid=%s""", (sid, ))
        result = cur.fetchone()
    except Exception as e:
        print("Failed to fetch transcript of %s", sid)
        print(e)
    finally:
        cur.close()
        conn.close()
        return result
        
################################################################################
# New prerequisite
#   - Performs an INSERT query for a new prerequisite and unit-of-study pair
################################################################################

def new_prereq(uoscode, prerequoscode, enforcedsince):
    config = configparser.ConfigParser()
    config.read('config.ini')
    conn = None
    try:
        conn = pg8000.connect(database='y22s2i2120_mgid9133',
                                    user=config['DATABASE']['user'],
                                    password=config['DATABASE']['password'],
                                    host=config['DATABASE']['host'])
    except pg8000.OperationalError as e:
        print("""Error, you haven't updated your config.ini or you have a bad
        connection, please try again. (Update your files first, then check
        internet connection)
        """)
        print(e)
    except pg8000.ProgrammingError as e:
        print("""Error, config file incorrect: check your password and username""")
        print(e)
    except Exception as e:
        print(e)
    
    if conn is None:
        return None
    
    cur = conn.cursor()
    try:
        cur.execute("""INSERT INTO unidb.requires 
                       VALUES (%s, %s, %s)
                       """, (uoscode, prerequoscode, enforcedsince, ))
        conn.commit()
    except Exception as e:
        print("Failed to insert new prerequisite")
        print(e)
        conn.rollback()
    finally:
        cur.close()
        conn.close()
        
################################################################################################
# Number of prerequisites
#   - Performs a SELECT query that counts the number of prerequisites for each unit of study
################################################################################################

def count_prereqs():
    config = configparser.ConfigParser()
    config.read('config.ini')
    conn = None
    try:
        conn = pg8000.connect(database='y22s2i2120_mgid9133',
                                    user=config['DATABASE']['user'],
                                    password=config['DATABASE']['password'],
                                    host=config['DATABASE']['host'])
    except pg8000.OperationalError as e:
        print("""Error, you haven't updated your config.ini or you have a bad
        connection, please try again. (Update your files first, then check
        internet connection)
        """)
        print(e)
    except pg8000.ProgrammingError as e:
        print("""Error, config file incorrect: check your password and username""")
        print(e)
    except Exception as e:
        print(e)
    
    if conn is None:
        return None
    
    cur = conn.cursor()
    result = None
    try:
        cur.execute("""SELECT uoscode, count(uoscode) 
                       FROM unidb.requires 
                       GROUP BY uoscode 
                       ORDER BY uoscode;
                       """)
        result = cur.fetchall()
    except Exception as e:
        print("Failed to determine the number of prerequisites for each unit of study")
        print(e)
    finally:
        cur.close()
        conn.close()
        return result
        
################################################################################################
# Prerequisites of a unit-of-study
#   - Performs a SELECT query that shows the prerequisites for a given unit of study
################################################################################################

def uos_prereqs(uos):
    config = configparser.ConfigParser()
    config.read('config.ini')
    conn = None
    try:
        conn = pg8000.connect(database='y22s2i2120_mgid9133',
                                    user=config['DATABASE']['user'],
                                    password=config['DATABASE']['password'],
                                    host=config['DATABASE']['host'])
    except pg8000.OperationalError as e:
        print("""Error, you haven't updated your config.ini or you have a bad
        connection, please try again. (Update your files first, then check
        internet connection)
        """)
        print(e)
    except pg8000.ProgrammingError as e:
        print("""Error, config file incorrect: check your password and username""")
        print(e)
    except Exception as e:
        print(e)
        
    if conn is None:
        return None
    
    cur = conn.cursor()
    result = None
    try:
        cur.execute("""WITH prereqnames as (
                       SELECT prerequoscode, uosname, enforcedsince
                       FROM unidb.requires JOIN unidb.unitofstudy ON
                       (unidb.unitofstudy.uoscode = unidb.requires.prerequoscode)
                       ), uosnames as (
                       SELECT uoscode, uosname
                       FROM unidb.unitofstudy
                       )
                       SELECT DISTINCT P.prerequoscode, P.uosname
                       FROM uosnames U, prereqnames P, unidb.requires R
                       WHERE U.uoscode = R.uoscode AND P.prerequoscode = R.prerequoscode AND P.enforcedsince = R.enforcedsince
                       AND U.uoscode = %s;
                       """, (uos, ))
        result = cur.fetchall()
    except Exception as e:
        print("Failed to show the prerequisites for %s", uos)
        print(e)
    finally:
        cur.close()
        conn.close()
        return result
        
################################################################################################
# Prerequisites table with unit names
#   - Performs a SELECT query that shows the prerequisites table with their respective names
################################################################################################

def all_prereqs():
    config = configparser.ConfigParser()
    config.read('config.ini')
    conn = None
    try:
        conn = pg8000.connect(database='y22s2i2120_mgid9133',
                                    user=config['DATABASE']['user'],
                                    password=config['DATABASE']['password'],
                                    host=config['DATABASE']['host'])
    except pg8000.OperationalError as e:
        print("""Error, you haven't updated your config.ini or you have a bad
        connection, please try again. (Update your files first, then check
        internet connection)
        """)
        print(e)
    except pg8000.ProgrammingError as e:
        print("""Error, config file incorrect: check your password and username""")
        print(e)
    except Exception as e:
        print(e)

    if conn is None:
        return None
    
    cur = conn.cursor()
    result = None
    try:
        cur.execute("""WITH prereqnames AS (
                        SELECT prerequoscode, uosname, enforcedsince
                        FROM unidb.requires JOIN unidb.unitofstudy ON (unidb.unitofstudy.uoscode = unidb.requires.prerequoscode)
                        ), uosnames AS (
                        SELECT uoscode, uosname
                        FROM unidb.unitofstudy
                        )
                        SELECT DISTINCT U.uoscode, U.uosname, P.prerequoscode, P.uosname, P.enforcedsince
                        FROM uosnames U, prereqnames P, unidb.requires R
                        WHERE U.uoscode = R.uoscode AND P.prerequoscode = R.prerequoscode AND P.enforcedsince = R.enforcedsince;
                    """)
        result = cur.fetchall()
    except Exception as e:
        print("Failed to display prerequisites table")
        return e
    finally:
        cur.close()
        conn.close()
        return result

#####################################################
#  Python code if you run it on it's own as 2tier
#####################################################


if (__name__ == '__main__'):
    print("{}\n{}\n{}".format("=" * 50, "Welcome to the 2-Tier Python Database", "=" * 50))
    print("""
This file is to interact directly with the database.
We're using the unidb (make sure it's in your database)

Try to execute some functions:
check_login('3070799133', 'random_password')
check_login('3070088592', 'Green')
check_login('305422153', 'Purple')
list_units()""")

