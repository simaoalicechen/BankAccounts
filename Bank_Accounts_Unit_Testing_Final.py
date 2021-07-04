#!/usr/bin/env python
# coding: utf-8

# In[1]:


# TimeZone Class 
# Main class on this page here
# For other classes, or how they eventually become what they are, see other pages. 
# every time, the account class is being copied, some new functionality is being added. 

import numbers 
import itertools 

from datetime import timedelta
from datetime import datetime


class TimeZone:
    def __init__(self, name, offset_hours, offset_minutes): 
        if name is None or len(str(name).strip()) == 0: 
            raise ValueError('Timezone name cannot be empty.')
            
        self._name = str(name).strip()
        
        if not isinstance(offset_hours, numbers.Integral):
            raise ValueError('Hour offset must be an intgers.')
            
        if not isinstance(offset_minutes, numbers.Integral):
            raise ValueError('Minute offset must be an intgers.')
            
        if offset_minutes > 59 or offset_minutes < -59:
            raise ValueError('Minutes offset must be between -59 and 59 (inclusive).')
            
        offset = timedelta(hours = offset_hours, minutes = offset_minutes)
        if offset < timedelta(hours = -12, minutes = 0) or offset > timedelta(hours = 14, minutes = 0): 
            raise ValueError('Offset must be between -12:00 and +14:00.')
            
        self._offset_hours = offset_hours
        self._offset_minutes = offset_minutes
        self._offset = offset
        
        @property
        def offset(self):
            return self._offset
        
        @property
        def name(self):
            return self._name
        
        def __eq__(self, other):
            (isinstance(other, TimeZone) and 
            self.name == other.name and 
            self._offset_hours == other._offset_hours and 
            self._offset_minutes == other._offset_minutes)
            
        
        def __repr__(self):
            return (f"TimeZone(name = '{self.name}', "
                    f"offset_hours = {self._offset_hours}, "
                    f"offset_minutes = {self._offset_minutes})")


# In[16]:


class Account:
    transaction_counter = itertools.count(100)
    _interest_rate = 0.5  # percentage
    
    _transaction_codes = {
        'deposit': 'D',
        'withdraw': 'W',
        'interest': 'I',
        'rejected': 'X'
    }
    
    def __init__(self, account_number, first_name, last_name, timezone=None, initial_balance=0):
        # in practice we probably would want to add checks to make sure these values are valid / non-empty
        self._account_number = account_number
        self.first_name = first_name
        self.last_name = last_name
        
        if timezone is None:
            timezone = TimeZone('UTC', 0, 0)
        self.timezone = timezone
        
        self._balance = Account.validate_real_number(initial_balance, min_value = 0)  # force use of floats here, but maybe Decimal would be better
        
    @property
    def account_number(self):
        return self._account_number
    
    @property 
    def first_name(self):
        return self._first_name
    
    @first_name.setter
    def first_name(self, value):
        self.validate_and_set_name('_first_name', value, 'First Name')
        
    @property
    def last_name(self):
        return self._last_name
    
    @last_name.setter
    def last_name(self, value):
        self.validate_and_set_name('_last_name', value, 'Last Name')
        
    # also going to create a full_name computed property, for ease of use
    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
        
    @property
    def timezone(self):
        return self._timezone
    
    @property
    def balance(self):
        return self._balance
    
    @timezone.setter
    def timezone(self, value):
        if not isinstance(value, TimeZone):
            raise ValueError('Time zone must be a valid TimeZone object.')
        self._timezone = value
          
    @classmethod
    def get_interest_rate(cls):
        return cls._interest_rate
    
    @classmethod
    def set_interest_rate(cls, value):
        if not isinstance(value, numbers.Real):
            raise ValueError('Interest rate must be a real number')
        if value < 0:
            raise ValueError('Interest rate cannot be negative.')
        cls._interest_rate = value
        
    def validate_and_set_name(self, property_name, value, field_title):
        if value is None or len(str(value).strip()) == 0:
            raise ValueError(f'{field_title} cannot be empty.')
        setattr(self, property_name, value)
        
    @staticmethod
    def validate_real_number(value, min_value = None):
        if not isinstance(value, numbers.Real):
            raise ValueError('Value must be a real number.')
        
        if min_value is not None and value < min_value:
            raise ValueError(f'Value must be at least {min_value}.')
            
        return value 
        
        
    def generate_confirmation_code(self, transaction_code):
        # main difficulty here is to generate the current time in UTC using this formatting:
        # YYYYMMDDHHMMSS
        dt_str = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f'{transaction_code}-{self.account_number}-{dt_str}-{next(Account.transaction_counter)}'
    
    @staticmethod
    def parse_confirmation_code(confirmation_code, preferred_time_zone=None):
        # dummy-A100-20190325224918-101
        parts = confirmation_code.split('-')
        if len(parts) != 4:
            # really simplistic validation here - would need something better
            raise ValueError('Invalid confirmation code')
        
        # unpack into separate variables
        transaction_code, account_number, raw_dt_utc, transaction_id = parts
        
        # need to convert raw_dt_utc into a proper datetime object
        try:
            dt_utc = datetime.strptime(raw_dt_utc, '%Y%m%d%H%M%S')
        except ValueError as ex:
            # again, probably need better error handling here
            raise ValueError('Invalid transaction datetime') from ex
          
        if preferred_time_zone is None:
            preferred_time_zone = TimeZone('UTC', 0, 0)
            
        if not isinstance(preferred_time_zone, TimeZone):
            raise ValueError('Invalid TimeZone specified.')
            
        dt_preferred = dt_utc + preferred_time_zone.offset
        dt_preferred_str = f"{dt_preferred.strftime('%Y-%m-%d %H:%M:%S')} ({preferred_time_zone.name})"
        
        return Confirmation(account_number, transaction_code, transaction_id, dt_utc.isoformat(), dt_preferred_str)
    
    def deposit(self, value):
        #if not isinstance(value, numbers.Real):
        value = Account.validate_real_number(value, 0.01)
            
#             raise ValueError('Deposit value must be a real number.')
#         if value <= 0:
#             raise ValueError('Deposit value must be a positive number.')
        
        # get transaction code
        transaction_code = Account._transaction_codes['deposit']
        
        # generate a confirmation code
        conf_code = self.generate_confirmation_code(transaction_code)
        
        # make deposit and return conf code
        self._balance += value
        return conf_code
    
    def withdraw(self, value):
        # hmmm... repetitive code! we'll need to fix this
        # TODO: refactor a function to validate a valid positive number
        #       and use in __init__, deposit and 
        
        value = Account.validate_real_number(value, 0.01)
        
        accepted = False
        if self.balance - value < 0:
            # insufficient funds - we'll reject this transaction
            transaction_code = Account._transaction_codes['rejected']
        else:
            transaction_code = Account._transaction_codes['withdraw']
            accepted = True
            
        conf_code = self.generate_confirmation_code(transaction_code)
        
        # Doing this here in case there's a problem generating a confirmation code
        # - do not want to modify the balance if we cannot generate a transaction code successfully
        if accepted:
            self._balance -= value
            
        return conf_code

    
    def pay_interest(self):
        interest = self.balance * Account.get_interest_rate() / 100
        conf_code = self.generate_confirmation_code(Account._transaction_codes['interest'])
        self._balance += interest
        return conf_code


# In[3]:


# These are situations where everything is good and nothing is expected to be wrong. 

a = Account('A100', 'Eric', 'Idle', timezone = TimeZone('MST', -7, 0), initial_balance = 100)
print(a.balance)
print(a.deposit(150.02))
print(a.balance)
print(a.withdraw(0.02))
print(a.balance)
Account.set_interest_rate(1.0)
print(a.get_interest_rate())
print(a.pay_interest())
print(a.balance)
print(a.withdraw(1000))


# In[4]:


import unittest


# In[5]:


def run_tests(test_class): # we use a class to test, and we combine our tests in our class. 
    suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
    runner = unittest.TextTestRunner(verbosity = 2)
    runner.run(suite)


# In[6]:


class TestAccount(unittest.TestCase):
    def setUp(self):
        print('running setup...')
        self.x = 100
    
    def tearDown(self):
        print('running teardown...')
        
        
    def test_1(self): 
        self.x = 200
        self.assertEqual(100, self.x) 
        
    def test_2(self):
        self.assertEqual(100, self.x)


# In[7]:


run_tests(TestAccount)


# In[8]:


from datetime import timedelta, datetime
            
class TestAccount(unittest.TestCase):
   
    def test_create_timezone(self):
        tz = TimeZone('ABC', -1, -30)
        self.assertEqual('ABC', tz._name)
        self.assertEqual(timedelta(hours=-1, minutes=-30), tz._offset)
        
    def test_timezones_equal(self):
        tz1 = TimeZone('ABC', -1, -30)
        tz2 = TimeZone('ABC', -1, -30)
        self.assertEqual(tz1, tz1)
        
    def test_timezones_not_equal(self):
        tz = TimeZone('ABC', -1, -30)
        
        test_timezones = (
            TimeZone('DEF', -1, -30),
            TimeZone('ABC', -1, 0),
            TimeZone('ABC', 1, -30)
        )
        for test_tz in test_timezones:
            self.assertNotEqual(tz, test_tz)


# In[9]:


run_tests(TestAccount)


# In[10]:


# Sub Tests
from datetime import timedelta, datetime
            
class TestAccount(unittest.TestCase):
    
    def test_create_timezone(self):
        tz = TimeZone('ABC', -1, -30)
        self.assertEqual('ABC', tz._name)
        self.assertEqual(timedelta(hours=-1, minutes=-30), tz._offset)
        
    def test_timezones_equal(self):
        tz1 = TimeZone('ABC', -1, -30)
        tz1 = TimeZone('ABC', -1, -30)
        self.assertEqual(tz1, tz1)
        
    def test_timezones_not_equal(self):
        tz = TimeZone('ABC', -1, -30)
        
        test_timezones = (
            TimeZone('DEF', -1, -30),
            TimeZone('ABC', -1, 0),
            TimeZone('ABC', 1, -30)
        )
        for i, test_tz in enumerate(test_timezones):
            with self.subTest(test_number=i):
                self.assertNotEqual(tz, test_tz)


# In[11]:


run_tests(TestAccount)


# In[12]:


# Unit Testing when things go as expected. 
from datetime import timedelta, datetime
            
class TestAccount(unittest.TestCase):
    
    def test_create_timezone(self):
        tz = TimeZone('ABC', -1, -30)
        self.assertEqual('ABC', tz._name)
        self.assertEqual(timedelta(hours=-1, minutes=-30), tz._offset)
        
    def test_timezones_equal(self):
        tz1 = TimeZone('ABC', -1, -30)
        tz1 = TimeZone('ABC', -1, -30)
        self.assertEqual(tz1, tz1)
        
    def test_timezones_not_equal(self):
        tz = TimeZone('ABC', -1, -30)
        
        test_timezones = (
            TimeZone('DEF', -1, -30),
            TimeZone('ABC', -1, 0),
            TimeZone('ABC', 1, -30)
        )
        for i, test_tz in enumerate(test_timezones):
            with self.subTest(test_number=i):
                self.assertNotEqual(tz, test_tz)
    
    def test_create_account(self):
        account_number = 'A100'
        first_name = 'FIRST'
        last_name = 'LAST'
        tz = TimeZone('TZ', 1, 30)
        balance = 100.00
        
        a = Account(account_number, first_name, last_name, tz, balance)
        
        self.assertEqual(account_number, a.account_number)
        self.assertEqual(first_name, a.first_name)
        self.assertEqual(last_name, a.last_name)
        self.assertEqual(first_name + " " + last_name, a.full_name)
        self.assertEqual(tz, a.timezone)
        self.assertEqual(balance, a.balance)


# In[13]:


run_tests(TestAccount)


# In[14]:


# Cleanedup code 

from datetime import timedelta, datetime
            
class TestAccount(unittest.TestCase):
    
    # make setter to reduece the repeated codes later
    def setUp(self):
        self.account_number = 'A100'
        self.first_name = 'FIRST'
        self.last_name = 'LAST'
        self.tz = TimeZone('TZ', 1, 30)
        self.balance = 100.00
        
    # utility function, so that we do not need to rewrite Account every single time later. 
    def create_account(self):
        return Account(self.account_number, self.first_name, self.last_name, self.tz, self.balance)
        
    def test_create_timezone(self):
        tz = TimeZone('ABC', -1, -30)
        self.assertEqual('ABC', tz._name)
        self.assertEqual(timedelta(hours=-1, minutes=-30), tz._offset)
        
    def test_timezones_equal(self):
        tz1 = TimeZone('ABC', -1, -30)
        tz1 = TimeZone('ABC', -1, -30)
        self.assertEqual(tz1, tz1)
        
    def test_timezones_not_equal(self):
        tz = TimeZone('ABC', -1, -30)
        
        test_timezones = (
            TimeZone('DEF', -1, -30),
            TimeZone('ABC', -1, 0),
            TimeZone('ABC', 1, -30)
        )
        for i, test_tz in enumerate(test_timezones):
            with self.subTest(test_number=i):
                self.assertNotEqual(tz, test_tz)
    
    def test_create_account(self):
            
        a = self.create_account()
    
    
        self.assertEqual(self.account_number, a.account_number)
        self.assertEqual(self.first_name, a.first_name)
        self.assertEqual(self.last_name, a.last_name)
        self.assertEqual(self.first_name + " " + self.last_name, a.full_name)
        self.assertEqual(self.tz, a.timezone)
        self.assertEqual(self.balance, a.balance)
        
    def test_create_account_blank_first_name(self):
        
        self.first_name = ''
        
        with self.assertRaises(ValueError): 
            a = self.create_account()

        
    def test_create_account_negative_balance(self):
        
        self.balance = -100.00
        
        with self.assertRaises(ValueError):
            a = self.create_account()
    
    def test_account_withdraw_ok(self):
        account_number = 'A100'
        first_name = 'First'
        last_name = 'LAST'
        tz = TimeZone('TZ', 1, 30)
        balance = 100.00
        withdrawal_amount = 20
        
        
        a = self.create_account()
        conf_code = a.withdraw(withdrawal_amount)
        self.assertTrue(conf_code.startswith('W-'))
        self.assertEqual(balance - withdrawal_amount, a.balance)  # reduce constants in code, using variables instead. 
            
    # The test where we overwithdraw
    
    def test_account_withdraw_overdraw(self):
        account_number = 'A100'
        first_name = 'First'
        last_name = 'LAST'
        tz = TimeZone('TZ', 1, 30)
        balance = 100.00
        withdrawal_amount = 200
        

        a = self.create_account()
        conf_code = a.withdraw(withdrawal_amount)
        self.assertTrue(conf_code.startswith('X-'))
        self.assertEqual(balance, a.balance) 
        
        


# In[15]:


run_tests(TestAccount)


# In[ ]:




