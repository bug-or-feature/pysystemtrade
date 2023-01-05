# pysystemtrade-fsb data setup

In pysystemtrade-fsb the way data works is a little different from the upstream 
project. In this project we import and store individual Futures contract prices 
as normal. We then generate the individual Futures Spread Bet (FSB) contract 
prices from the futures prices; the futures prices are not overwritten. Multiple 
and adjusted prices are only generated for FSB instruments.

We do this for a few reasons:
- it is not practical to download historical FSB prices (at least from IG, the
 only currently supported broker)
- it would be easier to start trading Futures, at some point in the future, if 
 required  
- it would be easier to start trading some other futures-based derivative product 
 (CFDs?), at some point in the future, if required  

Roll calendars are different too. For many bets only the front contract is 
available, expiry dates are often different, and so on. We try to make the FSB 
roll calendars match the ideals of the futures ones, in terms of carry contract 
selection, how long before expiry to roll etc. But it's usually not completely 
possible, so we try to get as close as we can.

These docs assume you have some external script to download futures contract 
prices. I use [this](https://github.com/bug-or-feature/bc-utils). I also have
scripts to download historic FSB prices from IG (at a low resolution), but this 
isn't strictly necessary; the FSB production scripts will do this once you have 
started sampling an instrument.


## setup process

load futures instrument configuration
```
$ python sysinit/futures/repocsv_instrument_config.py
```

load FSB instrument configuration
```
$ python sysinit/futures_spreadbet/instruments_csv_mongo.py
```

load FSB roll params config
```
$ python sysinit/futures_spreadbet/roll_parameters_csv_mongo.py
```

generate the expected FSB roll calendar from current roll config,  
and **FUTURES** csv prices. Adjust the roll params until the expected output 
looks something like the epic_history
> TODO add a note on how to generate `epic_history` files
```
# for dev/testing; reads CSV roll params and CSV prices
$ python sysinit/futures_spreadbet/fsb_rollcalendars_to_csv.py expect
```

temp roll calendar creation. we run this against **FUTURES** csv prices, to check 
the price data. We'll adjust the price files as necessary to make the roll 
calendar creation work. I usually manually add one extra line to the roll 
calendar, for the next future roll date
```
# for dev/testing; reads CSV roll params and CSV prices
$ python sysinit/futures_spreadbet/fsb_rollcalendars_to_csv.py build
```

Once the **FUTURES** csv contract prices are good, we can import them into 
MongoDB.
```
$ python sysinit/futures_spreadbet/fsb_contract_prices.py
```

now we generate FSB contract price data from futures prices, and import into 
Arctic. Note this script only looks at merged prices, and only creates merged 
FSB prices
```
$ python sysinit/futures_spreadbet/fsb_from_futures_contract_prices.py
```

Now create multiple prices from the FSB prices and the roll calendar we just 
created, and import into Arctic
```
# reads roll config from CSV
$ python sysinit/futures_spreadbet/fsb_multipleprices.py
```

now create back adjusted prices, and import into Arctic
```
$ python sysinit/futures_spreadbet/adjustedprices_from_mongo_multiple_to_mongo.py
```

import epics history
```
$ python sysinit/futures_spreadbet/fsb_epics_history.py
```

import historic IG FSB prices if you have them. Not really a problem if not, 
they're only used as a sanity check to make sure our assumption that FSB prices 
follow futures prices is correct
```
$ python sysinit/futures_spreadbet/ig_fsb_contract_prices.py
```

update fx. not really necessary, all IG FSBs are denominated in GBP
```
>>> from sysproduction.update_fx_prices import update_fx_prices
>>> update_fx_prices()
```

update epics
```
>>> from sysproduction.update_epics import update_epics
>>> update_epics()
```

update sampled contracts
```
>>> from sysproduction.update_sampled_contracts import update_sampled_contracts
>>> update_sampled_contracts()
>>> update_sampled_contracts(['BRENT_W_fsb'])
>>> update_sampled_contracts(['COCOA_LDN_fsb'])
>>> update_sampled_contracts(['BREN_fsb', 'BUND_fsb', 'EDOLLAR_fsb', 'OAT_fsb', 'SHATZ_fsb', 'US5_fsb', 'US30_fsb', 'US30U_fsb'])
```

update historic prices
```
$ pst h
>>> from sysproduction.update_historical_prices import update_historical_prices
>>> update_historical_prices()
>>> update_historical_prices(['BRENT_W','COCOA_LDN'])
>>> update_historical_prices(['BRENT_W'])
>>> update_historical_prices(['BOBL', 'BUND', 'EDOLLAR', 'OAT', 'SHATZ', 'US5', 'US30', 'US30U'])
```

generate FSB updates from Futures prices
```
>>> from sysproduction.generate_fsb_updates import generate_fsb_updates
>>> generate_fsb_updates()
```

update multiple adjusted prices
```
>>> from sysproduction.update_multiple_adjusted_prices import update_multiple_adjusted_prices
>>> update_multiple_adjusted_prices()
>>> update_multiple_adjusted_prices(['GOLD_fsb'])
>>> update_multiple_adjusted_prices(['BOBL_fsb', 'BUND_fsb', 'EDOLLAR_fsb', 'OAT_fsb', 'SHATZ_fsb', 'US5_fsb', 'US30_fsb', 'US30U_fsb'])
```

update IG FSB prices
```
>>> from sysproduction.update_historical_fsb_prices import update_historical_fsb_prices, update_historical_fsb_prices_single
>>> update_historical_fsb_prices()
>>> update_historical_fsb_prices_single(['NASDAQ_fsb'])
>>> update_historical_fsb_prices_single(['BOBL_fsb', 'BUND_fsb', 'EDOLLAR_fsb', 'OAT_fsb', 'SHATZ_fsb', 'US5_fsb', 'US30_fsb', 'US30U_fsb'])
```

> Note: now disable the scripts that download futures and FSB prices for this
> instrument. That will now happen in pysystemtrade-fsb
