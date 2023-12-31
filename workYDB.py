import os
import ydb
import ydb.iam
from dotenv import load_dotenv

from loguru import logger
import sys

logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
logger.add("file_1.log", rotation="50 MB")

load_dotenv()

driver = ydb.Driver(
  endpoint=os.getenv('YDB_ENDPOINT'),
  database=os.getenv('YDB_DATABASE'),
  #credentials=ydb.iam.MetadataUrlCredentials(),)
  credentials=ydb.AccessTokenCredentials(os.getenv('YDB_CREDINTALS_TOKEN')))
  #credentials=ydb.iam.ServiceAccountCredentials.from_file(
  #          os.getenv("SA_KEY_FILE")
  #      ))
# Wait for the driver to become active for requests.G
driver.wait(fail_fast=True, timeout=5)
# Create the session pool instance to manage YDB sessions.
pool = ydb.SessionPool(driver)

def truncate_string(string, max_length):
    if len(string.encode('utf-8')) > max_length:
        return string[:max_length]
    else:
        return string
    
class Ydb:
    def replace_query(self, tableName: str, rows: dict):
        #print('попали в инсерт')
        field_names = rows.keys()
        fields_format = ", ".join(field_names)
        my_list = list(rows.values())
    
        value = '('
        #for i in my_list:
        for key, value1 in rows.items():
            try:
                value1 = value1.replace('"',"'")    
            except:
                1 + 0

            value1 = truncate_string(str(value1), 2000)            
            
            if key == 'id':
                value += f'{value1},'
            else:
                value += f'"{value1}",'
            
        value = value[:-1] + ')'
        # values_placeholder_format = ', '.join(my_list)
        query = f"REPLACE INTO {tableName} ({fields_format}) VALUES {value}"
        #print(query)
        logger.info(query)

        def a(session):
            session.transaction(ydb.SerializableReadWrite()).execute(
            #session(ydb.SerializableReadWrite()).execute(
                query,
                commit_tx=True,
            )
        return pool.retry_operation_sync(a)

    def update_query(self, tableName: str, rows: dict, where: str):
        # 'where id > 20 '
        field_names = rows.keys()
        fields_format = ", ".join(field_names)
        my_list = list(rows.values())
        sets = ''
        for key, value in rows.items():
            if key == 'ID':
                continue
            sets += f'{key} = "{value}",'
            """
            try:
                sets += f'{key} = {int(value)},'
                
            except Exception as e:
                print(e)
                sets += f"{key} = '{value}',"
            """
        sets = sets[:-1]

        # values_placeholder_format = ', '.join(my_list)
        query = f'UPDATE {tableName} SET {sets} WHERE {where}'
        # query = f"INSERT INTO {tableName} ({fields_format}) " \
        logger.info(query)
        #print(query)

        def a(session):
            session.transaction(ydb.SerializableReadWrite()).execute(
                query,
                commit_tx=True,
            )
        return pool.retry_operation_sync(a)

    def delete_query(self, tableName: str, where: str):
        # 'where id > 20 '
        query = f"DELETE FROM `{tableName}` WHERE {where}"
        logger.info(query)
        #print(query)

        def a(session):
            session.transaction(ydb.SerializableReadWrite()).execute(
                query,
                commit_tx=True,
            )
        return pool.retry_operation_sync(a)

    def create_table(self, tableName: str, fields: dict):
        # fields = {'id': 'Uint64', 'name': 'String', 'age': 'Uint64'}
        query = f"CREATE TABLE `{tableName}` ("
        logger.info(query)
        for key, value in fields.items():
            query += f'{key} {value},'

        query = query[:-1] + ', PRIMARY KEY (id) ) '
        logger.info(query)
        #print('CREATE TABLE',tableName)
        print(query)
        def a(session):
            session.execute_scheme(
                query,
                )
        return pool.retry_operation_sync(a)


    def insert_query(self, tableNameUserID: str, rows: dict):
        field_names = rows.keys()
        fields_format = ", ".join(field_names)
        my_list = list(rows.values())
    
        value = '('
        #for i in my_list:
        for key, value1 in rows.items():
            try:
                value1 = value1.replace('"',"'")    
            except:
                1 + 0

            value1 = truncate_string(str(value1), 2000)            
            if key == 'id':
                value += f'{value1},'
            else:
                value += f'"{value1}",'
            
        value = value[:-1] + ')'
        # values_placeholder_format = ', '.join(my_list)
        query = f"INSERT INTO `{tableNameUserID}` ({fields_format}) VALUES {value}"
        logger.info(query)
        #print(query)
        def a(session):
            session.transaction(ydb.SerializableReadWrite()).execute(
            #session(ydb.SerializableReadWrite()).execute(
                query,
                commit_tx=True,
            )
        return pool.retry_operation_sync(a)

    def get_context(self, tableNameUserID: str, whereModelDialog: str):
        query = f"""SELECT * FROM `{tableNameUserID}` where MODEL_DIALOG = "{whereModelDialog}" """
        logger.info(query)
        #print(query)
        def a(session):
            return session.transaction().execute(
                query,
                commit_tx=True,
            )
        b = pool.retry_operation_sync(a)
        # string = b_string.decode('utf-8')
        # IndexError: list index out of range если нет данныйх
        #print('b',b)
        rez = b[0].rows
        #print('rez',rez)
        context = ''
        for i in rez:
            context += i['TEXT'].decode('utf-8')+ '\n'
        #print('context',context)
        logger.info(f'contextREZ={context}')
        return context
    
    def set_payload(self, userID: int, payload: str):
        query = f'UPDATE user SET payload = "{payload}" WHERE id = {userID}'
        #print(query)
        logger.info(query)
        def a(session):
            session.transaction(ydb.SerializableReadWrite()).execute(
                query,
                commit_tx=True,
            )
        return pool.retry_operation_sync(a)

    def get_payload(self, whereID: int):
        query = f'SELECT payload FROM user WHERE id = {whereID}'
        logger.info(query)
        #print(query)

        def a(session):
            return session.transaction().execute(
                query,
                commit_tx=True,
            )
        b = pool.retry_operation_sync(a)
        # string = b_string.decode('utf-8')
        # IndexError: list index out of range если нет данныйх
        #print('b',b)
        try:
            rez = b[0].rows[0]['payload'].decode('utf-8')
        except:
            rez = ''
        #print('rez',rez)
        return rez

    def select_query(self,tableName: str, where: str):
        # 'where id > 20 '
        query = f'SELECT * FROM {tableName} WHERE {where}'
        logger.info(query)
        #print(query)

        def a(session):
            return session.transaction().execute(
                query,
                commit_tx=True,
            )
        b = pool.retry_operation_sync(a)
        # string = b_string.decode('utf-8')
        # IndexError: list index out of range если нет данныйх
        #print('b',b)
        rez = b[0].rows
        print('rez',rez)
        return rez
    
    def custom_select_query(self,tableName: str, select:str):
        # 'where id > 20 '
       
        query = f'SELECT {select} FROM {tableName}' 
        logger.info(query)
        #print(query)

        def a(session):
            return session.transaction().execute(
                query,
                commit_tx=True,
            )
        b = pool.retry_operation_sync(a)
        # string = b_string.decode('utf-8')
        # IndexError: list index out of range если нет данныйх
        #print('b',b)
        rez = b[0].rows
        print('rez',rez)
        logger.info(f'custom = {rez}')
        return rez  
    
    def get_model_url(self,modelName: str):
        try: 
            modelUrl = self.select_query('model', f'model = "{modelName}"')[0]['url']
            modelUrl= modelUrl.decode('utf-8')
        except:
            modelUrl = None
        logger.info(f'{modelUrl=}')
        return modelUrl
     
    def get_promt_url(self,promtName: str):
        try:
            promtUrl = self.select_query('promt', f'promt = "{promtName}"')[0]['url']
            promtUrl = promtUrl.decode('utf-8')
        except:
            promtUrl = None

        logger.info(f'{promtUrl=}')
        return promtUrl
    
    def get_model_for_user(self,userID: int):
        try:
            model = self.select_query('user', f'id = {userID}')[0]['model'].decode('utf-8')
        except:
            model = None
        logger.info(f'{model=}')
        return model
    
    def get_promt_for_user(self,userID: int):
        
        promt = self.select_query('user', f'id = {userID}')[0]['promt']
        try:
            promt = promt.decode('utf-8')
        except:
            promt = None
        logger.info(f'{promt=}')
        
        return promt
    
    def get_models(self,):
        models = self.custom_select_query('model', 'model')
        #print(f'{models=}')
        modelReturn = []
        for model in models:
            a = model['model'].decode('utf-8')
            modelReturn.append(a)
        return modelReturn
    
    def get_promts(self):
        promts = self.custom_select_query('promt', 'promt')
        #print(f'{promts=}')
        promtReturn = []
        for promt in promts:
            a = promt['promt'].decode('utf-8')
            promtReturn.append(a)
        return promtReturn
    
def handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello World!',
    }