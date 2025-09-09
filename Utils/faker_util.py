from faker import Faker
from datetime import datetime
import dateutil.relativedelta
import random
import string
from random import randint

fake = Faker()


class FakeDataUtil:
    @staticmethod
    def fake_first_name():
        return fake.first_name()

    @staticmethod
    def fake_middle_name():

        if random.randint(0, 1):
            return fake.last_name()
        else:
            return ""

    @staticmethod
    def fake_last_name():
        return fake.last_name()

    @staticmethod
    def fake_word():
        return fake.word()

    @staticmethod
    def generate_random_number(min_num=0, max_num=100000):
        return randint(min_num, max_num)

    @staticmethod
    def generate_closing_date():
        """ Returns the current date + 3 days in MMM-DD-YYYY format """

        closing_date = (datetime.now() + dateutil.relativedelta.relativedelta(days=3)).strftime("%b-%d-%Y").upper()

        return closing_date

    @staticmethod
    def generate_date_number(format: str):
        date = datetime.now().strftime(format).upper()

        return date

    @staticmethod
    def generate_future_date(format: str, days: int):
        """ Returns future date in given format format """

        date = (datetime.now() + dateutil.relativedelta.relativedelta(days=days)).strftime(format).upper()

        return date

    @staticmethod
    def generate_random_phone_number():
        return fake.phone_number()