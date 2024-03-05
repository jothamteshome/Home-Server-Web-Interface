import mysql.connector
import hashlib
import itertools

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
        tables = {"users": True, 'comicData': True, 'showData': True, 'shortContentData': True, 'uploadDirectories': True}

        for table in tables:
            if purge and tables[table]:
                self.query(f'DROP TABLE IF EXISTS {table}')


            with open(f"{data_path}/{table}.sql", "r") as sql_table:
                self.query(" ".join(sql_table.readlines()))


    def insertRows(self, table, columns, parameters):
        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )
        
        cursor = cnx.cursor()


        col_string = ", ".join(columns)

        parameter_format_list = ['%s'] * len(columns)
        param_string = ", ".join(parameter_format_list)

        insert_statement = f"INSERT IGNORE INTO {table} ({col_string}) VALUES ({param_string});"

        cursor.executemany(insert_statement, parameters)
        cnx.commit()
        
        cursor.close()
        cnx.close()


    def _decodeDBData(self, data):
        for column in data:
            try:
                data[column] = data[column].decode('utf-8') 
            except AttributeError:
                if '_id' in column:
                    data[column] = str(data[column])
                else:
                    continue

        return data

    
    def storeUploadDirectories(self, data):
        all_prepared_data = []

        for row in data:
            prepared_data = (row[0].encode('utf-8'), row[1].encode('utf-8'), row[2].encode('utf-8'), row[3], row[4], row[5])

            all_prepared_data.append(prepared_data)

        self.insertRows('uploadDirectories',
                        ['section_name', 'section_directory', 'section_content_style', 'separate_uploaded_content', 'separate_image_video', 'single_upload_limit'],
                        all_prepared_data)
        
    
    def getAllUploadDirectories(self):
        directoryOptions = []

        content_styles = self.getDecodedData("SELECT section_content_style FROM uploadDirectories GROUP BY section_content_style ORDER BY section_content_style")

        for content_style in content_styles:
            directoryOptions.append({'name': f"--- {content_style['section_content_style']} ---", 'disabled': True})

            results = self.getDecodedData("SELECT section_name FROM uploadDirectories WHERE section_content_style=%s ORDER BY %s", [content_style['section_content_style'], 'section_name'])

            directoryOptions.extend([{'name': result['section_name']} for result in results])

        return directoryOptions
        

    
    def storeComics(self, data):
        all_prepared_data = []

        for row in data:
            prepared_data = (row[0], row[1].encode('utf-8'), row[2].encode('utf-8'), row[3].encode('utf-8'),
                             row[4], row[5].encode('utf-8'), row[6].encode('utf-8'))
            
            all_prepared_data.append(prepared_data)

        self.insertRows('comicData', 
                        ['comic_id', 'comic_name', 'comic_franchise', 'comic_series', 'has_chapters', 'comic_author', 'comic_loc'], 
                        all_prepared_data)

    def getComic(self, comic_id):
        comicData = self.query("SELECT * FROM comicData WHERE comic_id=%s", [comic_id])

        return self._decodeDBData(comicData[0])

    def storeShows(self, data):
        all_prepared_data = []

        for row in data:
            prepared_data = (row[0], row[1].encode('utf-8'), row[2].encode('utf-8'), row[3].encode('utf-8'), 
                          row[4].encode('utf-8'), row[5].encode('utf-8'), row[6].encode('utf-8'))
            
            all_prepared_data.append(prepared_data)

        
        self.insertRows('showData',
                        ['show_id', 'show_episode', 'show_name', 'show_ep_num', 'show_search_dir', 'show_thumb', 'show_loc'],
                        all_prepared_data)
        
    def getShow(self, show_id):
        showData = self.query("SELECT * FROM showData WHERE show_id=%s", [show_id])

        return self._decodeDBData(showData[0])
    

    def storeShortContent(self, data):
        all_prepared_data = []

        # Prepare data for executemany statement
        for row in data:
            prepared_data = (row[0], row[1].encode('utf-8'), row[2].encode('utf-8'), row[3].encode('utf-8'), row[4].encode('utf-8'),
                             row[5].encode('utf-8'), row[6].encode('utf-8'), row[7], row[8].encode('utf-8'), row[9].encode('utf-8'), row[10].encode('utf-8'))
            
            all_prepared_data.append(prepared_data)

        self.insertRows('shortContentData',
                        ['content_id', 'content_name', 'content_type', 'content_loc', 'search_dir_name', 'source_dir_name', 'content_style', 'has_caption', 'caption_loc', 'prev_content_id', 'next_content_id'],
                        all_prepared_data)
        
    
    def updateShortContent(self, columns, data):
        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )
        
        cursor = cnx.cursor()


        col_string = ", ".join([f"{column}=%s" for column in columns])

        updateStatement = f"UPDATE shortContentData SET {col_string} WHERE content_id=%s"

        cursor.executemany(updateStatement, data)
        cnx.commit()
        
        cursor.close()
        cnx.close()


        
    def getShortContent(self, content_id):
        shortContentData = self.query("SELECT * FROM shortContentData WHERE content_id=%s", [content_id])

        return self._decodeDBData(shortContentData[0])
    

    def getDecodedData(self, statement, params=None):
        data = self.query(statement, params)

        for i, row in enumerate(data):
            data[i] = self._decodeDBData(row)

        return data
    

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

        


