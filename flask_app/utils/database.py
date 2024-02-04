import mysql.connector
import hashlib
from cryptography.fernet import Fernet

from flask_app.utils.PropertiesReader import PropertiesReader

class database:

    def __init__(self):
        prop_reader = PropertiesReader()
        # Grab information from the configuration file
        self.database       = prop_reader.getDatabaseInfo('MYSQL_DATABASE')
        self.host           = prop_reader.getDatabaseInfo('MYSQL_HOST')
        self.user           = prop_reader.getDatabaseInfo('MYSQL_USERNAME')
        self.port           = prop_reader.getDatabaseInfo('MYSQL_PORT')
        self.password       = prop_reader.getDatabaseInfo('MYSQL_PASSWORD')

        self.encryption     =  {   'oneway': {'salt' : b'averysaltysailortookalongwalkoffashortbridge',
                                                 'n' : int(pow(2,5)),
                                                 'r' : 9,
                                                 'p' : 1
                                             },
                                'reversible': { 'key' : '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                                }

    def query(self, query = "SELECT CURDATE()", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )


        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def createTables(self, purge=False, data_path='flask_app/database/'):
        # Create new tables
        tables = {"users": "purge", 'returnData': "purge", 'comicData': 'purge', 'showData': 'purge'}

        for table in tables:
            if purge and tables[table] == "purge":
                self.query(f'DROP TABLE IF EXISTS {table}')


            with open(f"{data_path}/{table}.sql", "r") as sql_table:
                self.query(" ".join(sql_table.readlines()))


    def insertRows(self, table, columns, parameters):
        col_string = ", ".join(columns)

        parameter_format_list = ['%s'] * len(columns)
        param_string = ", ".join(parameter_format_list)

        insert_statement = f"INSERT IGNORE INTO {table} ({col_string}) VALUES ({param_string});"

        # Replace all instances of "NULL" with None then run query
        for row in parameters:
            self.query(insert_statement, row)

    
    def storeComic(self, comic_id, comic_name, comic_franchise, comic_author, comic_loc, comic_series="", has_chapters=0):
        self.insertRows('comicData', 
                        ['comic_id', 'comic_name', 'comic_franchise', 'comic_series', 'has_chapters', 'comic_author', 'comic_loc'], 
                        [[comic_id, comic_name.encode('utf-8'), comic_franchise.encode('utf-8'), comic_series.encode('utf-8'), 
                          has_chapters, comic_author.encode('utf-8'), comic_loc.encode('utf-8')]])

    def getComic(self, comic_id):
        comicData = self.query("SELECT * FROM comicData WHERE comic_id=%s", [comic_id])

        return comicData[0]

    def storeShow(self, show_id, show_episode, show_name, show_ep_num, show_search_dir, show_thumb, show_loc):
        self.insertRows('showData',
                        ['show_id', 'show_episode', 'show_name', 'show_ep_num', 'show_search_dir', 'show_thumb', 'show_loc'],
                        [[show_id, show_episode.encode('utf-8'), show_name.encode('utf-8'), show_ep_num.encode('utf-8'), 
                          show_search_dir.encode('utf-8'), show_thumb.encode('utf-8'), show_loc.encode('utf-8')]])
        
    def getShow(self, show_id):
        showData = self.query("SELECT * FROM showData WHERE show_id=%s", [show_id])

        return showData[0]
    
    def storeReturnData(self, searchName, itemName, itemLoc, itemProcessURL, itemDirName=None, itemThumb=None):
        self.insertRows('returnData', ['searchName', 'itemName', 'itemSource', 'itemProcessURL', 'itemDirName', 'itemThumb'], 
                        [[searchName, itemName, itemLoc, itemProcessURL, itemDirName, itemThumb]])

    def getReturnData(self, searchName):
        returnData = self.query(f"SELECT * FROM returnData where searchName=%s", [searchName])

        return returnData

    def createUser(self, user='user', password='user', role='user'):
        users = self.query(f"SELECT * FROM users WHERE username = '{user}'")
        if not users:
            self.insertRows('users', ['username', 'password', 'role'], [[user, self.onewayEncrypt(password), role]])
            return {'success': 1, 'role': role}
        else:
            return {'success': 0}
        

    def authenticate(self, username='user', password='user'):
        users = self.query(f"SELECT * FROM users WHERE username = '{username}' AND password = '{self.onewayEncrypt(password)}'")
        if users == []:
            return {'success': 0}
        else:
            return {'success': 1, 'role': users[0]['role']}
    
        
    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt = self.encryption['oneway']['salt'],
                                          n    = self.encryption['oneway']['n'],
                                          r    = self.encryption['oneway']['r'],
                                          p    = self.encryption['oneway']['p']
                                          ).hex()
        return encrypted_string


    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])
        
        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message

        


