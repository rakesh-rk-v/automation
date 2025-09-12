import logging
from datetime import timedelta, datetime

from DButils.Common.raptr_sql_util import MySqlUtil


class CmsDataUtil(MySqlUtil):

    #Get Queries

    def get_customer_request_id(self,cust_id):
        query="""
           SELECT * FROM customer_requests WHERE tenant_id={} 
           AND customer_id={} ORDER BY request_id DESC
        """.format(self._tenant_id,cust_id)
        results = self.execute_select_query(query)
        return results

    def get_work_order_id(self,cust_id,activity_id):
        logging.info("Getting Work Order ID From Data Base ....")
        query = """SELECT work_order_id FROM dxpoms.work_orders WHERE tenant_id={}
                   AND customer_id={} and activity_id={} and status !=19 ORDER BY work_order_id desc;
            """.format(self._tenant_id, cust_id,activity_id)
        logging.info("get_work_order_id QUERY = {}".format(query))
        results = self.execute_select_query(query)
        logging.info("Result Set Of Work Order = {}".format(results))
        if results is None or len(results)==0:
            logging.error("WORK_ORDER_ID NOT FOUND FOR Customer ID = {} ,ACTIVITY_ID ={}".format(cust_id,activity_id))
            raise AssertionError("NO WORK_ORDER ID FOUND ")
        else:
            logging.info("WORK_ORDER_ID FOUND FOR Customer ID = {} ,ACTIVITY_ID ={}, Results = {}".format(cust_id,activity_id,results))

        return results

    def get_activity_code_from_activities(self,activity_name):
        logging.info(f"Activity for Request = {activity_name}")
        query = """SELECT * FROM dxpref.activities WHERE tenant_id={}
                   AND activity_name='{}'
                   """.format(self._tenant_id,activity_name)
        results = self.execute_select_query(query)
        return results

    def get_customer_contract_status(self,cust_id,wo_id):
        query="""SELECT * FROM customer_contracts 
        WHERE customer_id={} 
        AND work_order_id={}
        AND tenant_id={}""".format(cust_id,wo_id,self._tenant_id)
        result=self.execute_select_query(query)
        return result

    def get_customer_contract_hit(self,contract_id,cust_id,wo_id):
        query="""SELECT * FROM customer_contracts_hist 
        WHERE tenant_id={} 
        AND customer_id={} 
        AND customer_contract_id={}
        AND work_order_id={}
        """.format(self._tenant_id,cust_id,contract_id,wo_id)

    #Update Queries
    def update_work_order_table(self,cust_id,wo_id):
        logging.info("Executing the Update Query For Work Order for Customer_ID ={} and Work Order ID = {} ".format(cust_id,wo_id))
        query="""UPDATE work_orders SET STATUS=45 
        WHERE tenant_id={} 
        AND customer_id={}
        AND work_order_id={}""".format(self._tenant_id,cust_id,wo_id)
        result=self.execute_update_query(query)
        logging.info("Results = {}".format(result))
        if result:
            logging.info(f"Work order {wo_id} for customer {cust_id} updated successfully. Rows affected: {result}")
        else:
            logging.warning(
                f"No rows updated for work order {wo_id} and customer {cust_id}. Maybe work order does not exist or status is already 45.")

        return result
    #Call Quiries
    def call_post_provisioning(self,wo_id,activity_code):
        query = """CALL POSTPROV({},'{}','2025-03-01','2025-03-01', '2025-03-31', @status, @result, @sat)
                   """.format(wo_id,activity_code)
        results = self.execute_call_query(query)
        return results
    def get_cust_acc_status_by_custid(self,customer_id:int):
        query = """ select CUSTOMER_ACCOUNT_ID , CUSTOMER_ID ,BILLING_ACCOUNT_ID ,CUSTOMER_ACCOUNT_NAME ,STATUS  from dxpoms.customer_accounts ca where CUSTOMER_ID ={}""".format(customer_id)
        results = self.execute_select_query(query)
        return results
    def do_provisioning_for_work_order(self,wo_id,activity_code):
        """
            Executes provisioning by calling the stored procedure POSTPROV
            and returning its output variables.

            Args:
                wo_id (int): Work Order ID.
                activity_code (str): Activity Code.

            Returns:
                dict: Contains 'status', 'result', and 'sat' returned from the procedure.
            """
        try:
            # Calculate dynamic time (10 minutes ago)
            ten_minutes_ago = datetime.now() - timedelta(minutes=10)
            formatted_time = ten_minutes_ago.strftime('%Y-%m-%d %H:%M:%S')
            logging.info(f"executing procedure with WORK_ORDER_ID = {wo_id} and ACTIVITY_CODE = {activity_code}")
            # First, call the stored procedure
            script = """CALL POSTPROV({},'{}','{}','2025-08-24', '2025-09-23', @status, @result, @sat);
                        SELECT @status , @result;
                       """.format(wo_id, activity_code,formatted_time)
            results =self.execute_script(script)
            return results
        except Exception as e:
            logging.error(f"Exception Executing the PROV Procedure.\n {e}")
            raise

    def get_request_id_from_db(self,customer_id):
        query= """SELECT REQUEST_ID FROM DXPOMS.CUSTOMER_REQUESTS WHERE 
                TENANT_ID = {} AND
                CUSTOMER_ID = {} AND 
                STATUS !=19 ORDER BY 1 DESC LIMIT 1
                """.format(self._tenant_id,customer_id)
        result = self.execute_select_query(query)
        request_id = result[0]["REQUEST_ID"]
        return request_id

    def get_account_status_from_customer_accounts(self,account_id):
        query = """ select * from customer_accounts ca where 
        tenant_id = {} and 
        CUSTOMER_ACCOUNT_ID = {} """.format(self._tenant_id,account_id)
        result = self.execute_select_query(query)
        status = result[0]["STATUS"]
        if status:
            logging.info("Status of the Account = {}".format(status))
        else :
            logging.error("No Records Found for get_account_status_from_customer_accounts")
        return  status

    def get_customer_status_from_customer_master(self,customer_id):
        query = """ select """

    def check_suspended_contract_for_customer(self,customer_id):
        logging.info("Checking if customer having any contracts that are suspended.")
        query = """select * from customer_contracts cc where 
        tenant_id = {} 
        and customer_id = {} 
        and status = 21
            """.format(self._tenant_id,customer_id)
        results = self.execute_select_query(query)
        if results is None or len(results)==0:
            logging.warning("There is no contract is suspended for the CUSTOMER of Customer ID = {}".format(customer_id))
            return False
        else :
            logging.info("Customer is Having Suspended Contracts . Res={}".format(results))
            return True

    def get_contract_status_from_customer_contracts(self,customer_id):
        query = """ select * from customer_contracts ca where 
        tenant_id = {} and 
        customer_id = {} """.format(self._tenant_id,customer_id)
        result = self.execute_select_query(query)
        status = result[0]["STATUS"]
        if status:
            logging.info("Status of the Account = {}".format(result))
        else :
            logging.warning("No Records Found for get_account_status_from_customer_accounts")
        return  status
    def get_customer_account_details(self,cust_id,status,acc_type):
        query="""SELECT * FROM customer_accounts 
        WHERE tenant_id={} 
        AND customer_id={} 
        AND STATUS={} 
        AND customer_account_type={}
        """.format(self._tenant_id,cust_id,status,acc_type)
        result=self.execute_select_query(query)
        # logging.info("get_customer_account_details . Result = {}".format(result))
        return result

    def get_bill_deleivery_mode(self,customer_id):
        query = """select DELIVERY_MODE  from dxpoms.billing_accounts ba   where customer_id = {}""".format(customer_id)
        result = self.execute_select_query(query)
        logging.info("Got Bill Delivery Mode From DB. {}".format(result))
        mode = result[0]["DELIVERY_MODE"]
        return mode

    def get_bill_cycle(self,customer_id):
        logging.info("Getting the Bill Cycle from the database.")
        query = """ select * from dxpoms.customer_bill_cycles where CUSTOMER_ID ={}""".format(customer_id)
        result = self.execute_select_query(query)
        return result

    def check_bill_cycle_exists_in_db_or_not(self,bill_cycle_id):
        query = "select * from dxpbill.bill_cycles bc where TENANT_ID ={} and BILL_CYCLE_ID = '{}'".format(self._tenant_id,bill_cycle_id)
        result = self.execute_select_query(query)

        if result:
            logging.info("Bill Cycle of {} is Exists in Database.".format(bill_cycle_id))
            return True
        else:
            logging.warn("Bill Cycle Doesn't Exists in Database")
            return False

    def get_contact_id_from_customer_contacts_mapping(self,cust_id):
        query="""SELECT * FROM customer_contacts_mapping
                 WHERE customer_id={}""".format(cust_id)
        result=self.execute_select_query(query)
        return result

    def get_email_from_customer_contacts(self,cont_id):
        query="""SELECT * FROM customer_contacts
                 WHERE contact_id={}""".format(cont_id)
        result = self.execute_select_query(query)
        return result
    def check_customer_acc_type(self,customer_id,acc_type):
        logging.info("Checking Customer Having a Postpaid Account or Not in Database.")
        query = """ select * from dxpoms.customer_accounts ca where 
        tenant_id = {} and 
        CUSTOMER_ID = {} and 
        CUSTOMER_ACCOUNT_TYPE = {} and 
        STATUS = 13
                """.format(self._tenant_id,customer_id,acc_type)
        result = self.execute_select_query(query)
        logging.debug("Executed Account Check Query : {}".format(result))
        return result


