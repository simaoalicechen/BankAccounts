#!/usr/bin/env python
# coding: utf-8

# # Transaction Numbers 

# In[6]:


class TransactionID:
    def __init__(self, start_id):
        self._start_id = start_id
        
    def next(self):
        self._start_id += 1
        return self._start_id
    


# In[7]:


class Account:
    transaction_counter = TransactionID(100)
    
    def make_transaction(self):
        new_trans_id = Account.transaction_counter.next()
        return new_trans_id


# In[8]:


a1 = Account()
a2 = Account()


# In[9]:


print(a1.make_transaction())
print(a2.make_transaction())
print(a1.make_transaction())

We do not really need a class to solve this problem. 

What is a transactionID? 

We just need an iterator, and we need something that every time we call something, we get a number back. 


# In[10]:


# using a function here instead
# An generator here. 

def transaction_ids(start_id): 
    while True:
        start_id += 1
        yield start_id
        


# In[11]:


t = transaction_ids(100)


# In[12]:


t


# In[13]:


next(t)


# In[14]:


next(t)


# In[16]:


class Account: 
    transaction_counter = transaction_ids(100)
    
    def make_transaction(self):
        new_trans_id = next(Account.transaction_counter)
        return new_trans_id


# In[17]:


a1 = Account()
a2 = Account()


# In[18]:


print(a1.make_transaction())
print(a2.make_transaction())
print(a1.make_transaction())

So we used a generator to simplify the codes. But we can take this one step further. We have itertools module as a generator in there, as counter, serving the same functions here. 
# In[19]:


import itertools 

class Account: 
    transaction_counter = itertools.count(100)
    
    def make_transaction(self):
        new_trans_id = next(Account.transaction_counter)
        return new_trans_id


# In[20]:


a1 = Account()
a2 = Account()


# In[29]:


print(a1.make_transaction())
print(a2.make_transaction())
print(a1.make_transaction())


# In[23]:


help(itertools.count)


# In[24]:


a1 = Account()
a2 = Account()


# In[28]:


print(a1.make_transaction())
print(a2.make_transaction())
print(a1.make_transaction())

# keeps the numbers going. 


# In[27]:


print(a1.make_transaction())
print(a2.make_transaction())
print(a1.make_transaction())

# keeps the numbers going. 

So we do not need a class here. Itertools would be sufficient. 
# In[ ]:




