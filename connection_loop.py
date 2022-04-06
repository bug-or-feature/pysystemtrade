#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from sysbrokers.IB.ib_connection import connectionIB
from ib_insync import *

import sysproduction.run_daily_price_updates as update

#util.startLoop()
import nest_asyncio
nest_asyncio.apply()
print("Success, IBGateway connection loop running.")