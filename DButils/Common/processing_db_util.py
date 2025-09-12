from DButils.Common.processing_sql_util import SqlUtil
from Utils.config_manager import ConfigManager


class ProcessingDbUtil(SqlUtil):
    def __init__(self):
        self.__driver = ConfigManager.get_config().get_value('auto_db_driver')
        self.__server = ConfigManager.get_config().get_value('auto_db_server')
        self.__username = ConfigManager.get_config().get_value('auto_db_username')
        self.__password = ConfigManager.get_config().get_value('auto_db_password')
        self.__database = ConfigManager.get_config().get_value('auto_db_name')

        super(ProcessingDbUtil, self).__init__(self.__driver, self.__server,  self.__database, self.__username, self.__password)

    def get_customer_id(self,acc_type):
        query="""select * from Customer_Details where Status='Availble'
                 and Account_type='{}'""".format(acc_type)
        result=self.execute_select_query(query)
        return result
    def update_test_customer_status_in_db(self, cust_id):
        query = """update sit.dbo.Customer_Details set status ='Used' where cust_id = {} """.format(cust_id)
        result = self.execute_update_query(query)
        return result
    def update_customer_as_prepaid_in_testdb(self,cust_id):
        query = """update sit.dbo.Customer_Details set Account_Type = 'Prepaid' where Cust_Id={}""".format(cust_id)
        result = self.execute_update_query(query)
        return result