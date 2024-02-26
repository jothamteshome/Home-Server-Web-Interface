import configparser


# Reads from important_info.properties file
class PropertiesReader:
    def __init__(self):
        self.__config_parser = configparser.ConfigParser()
        self.__config_parser.read('flask_app/utils/HelperFiles/important_info.properties')

    # Get key from important_info.properties file
    def getDatabaseInfo(self, identifier):
        return self.__config_parser.get('database_info', identifier)
    
    def getAdminUser(self, identifier):
        return self.__config_parser.get('admin_login', identifier)
    
    def getGuestUser(self, identifier):
        return self.__config_parser.get('guest_login', identifier)


