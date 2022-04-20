# pysystemtrade-fsb

Systematic Futures Spread Bets in Python

A fork of Rob Carver's [pysystemtrade](https://github.com/robcarver17/pysystemtrade), adapted to trade futures 
spread bets with [IG](https://www.ig.com/uk)

See upstream README [here](https://github.com/robcarver17/pysystemtrade/blob/master/README.md)

## Release notes

See [CHANGES](CHANGES.md) for release notes, and future plans.

## Description

An attempt to adapt Rob Carver's [pysystemtrade](https://github.com/robcarver17/pysystemtrade) for trading
spread bets - as outlined in his book [Leveraged Trading](https://www.systematicmoney.org/leveraged-trading). Limited
to futures based dated spread bets for Indices, Bonds/Rates, Commodities and quarterly dated forward 
spread bets for FX

## Differences with upstream

- custom instrument and roll config
- [IG](https://www.ig.com/uk) as broker instead of IB
- daily price updates from [Barchart](https://www.barchart.com/) and IG
- daily FX updates from [Alpha Vantage](https://www.alphavantage.co/)
- Futures Spread Bets (FSBs) are represented internally as futures instruments, but with codes like `GOLD_fsb`, 
  `SP500_fsb`
- Custom `dataBroker` and `dataBlob` classes
- custom scripts for data setup / import

## Challenges

### EPIC recycling
On the IG platforms, a market that you can trade on is identified by an *EPIC*. An EPIC is a unique text 
string containing letters, dots and numbers. For example, `IX.D.FTSE.DAILY.IP` is the EPIC for 
the daily funded bet (DFB) on the FTSE 100 Index. EPICs work fine for undated instruments like this, but 
for dated products they are less useful. For example, at the time of writing (January 2022), the EPIC for 
the spread bet based on the ASX Australia 200 Index future (March 2022 expiry) is `IX.D.ASX.MONTH3.IP`. 
And the contract expiring June 2022 is `IX.D.ASX.MONTH2.IP`, and September 2022 is `IX.D.ASX.MONTH4.IP`. 
No doubt December 2022 will be `IX.D.ASX.MONTH3.IP` again. EPICs are recycled.

Many markets only have two EPICs. For example the NASDAQ future has:
- `IX.D.NASDAQ.MONTH3.IP`
- `IX.D.NASDAQ.MONTH4.IP`

even though there are four contracts per year. And the NIKKEI:
- `IX.D.NIKFUT.FAR.IP`
- `IX.D.NIKFUT.FAR3.IP`

**Problem one:** there is no pattern or system for the EPIC names. When this was queried with IG Support, their 
response was:

> The dealing desk choose which EPIC to use and when, unfortunately we are unable to confirm beforehand, this is 
something they do as and when needed. They are also able to make changes to which epic is used at any given moment, so 
I do advise to check the epic if you ever receive an error

**Problem two:** obviously, due to the EPICs being recycled, it is impossible to get historical data for futures based 
spread bets. At the time of writing (January 2022) the oldest ASX contract for which you can get price 
history is December 2021. 

**Problem three:** just in terms of data, there are two API endpoints that an automated trading system would be 
interested in; one to get current prices, and another to get historical prices. To make the problems described above even
worse, with IG these two APIs are not synced. An EPIC used in the current price API will give you data for a different 
contract than the one for the historical price API.

Another request was made to IG Support for a schedule of the roll cycles for all the futures based spread bets. The 
response was:

> Your request of "Roll cycle for all Commodities, Indices, and Bonds and Rates" is not something we can provide. We 
will only be providing information based on the API reference. Some products may have the same EPIC, but there is no 
guarantee it will be the same always and its up to our dealing desk to manage that. And in such cases, we will not be 
informing clients of the changes so thats something you will need to take note of.

### IG API rate limits

The IG APIs have rate limits; you can only make a certain number of requests during a certain time period
(eg minute, hour, week etc) depending on the request type. The limits for the LIVE environment are published 
[here](https://labs.ig.com/faq), but the limits for DEMO are lower, and have been known to change randomly and 
without notice. The limits, as well as the epic recycling described above, mean that it is not practical to get 
useful historical prices from the IG APIs

### pysystemtrade is a futures trading system

From one of [Rob's comments](https://github.com/robcarver17/pysystemtrade/issues/391#issuecomment-911441646) in an 
issue in the main project:

> Although I sort of originally envisaged pysystemtrade being multi asset, in practice the use of futures is now 
completely baked in. However it should work pretty well for anything that looks like a future: a dated spread bet 
being a good example of that

What this means for this fork is that backtesting works pretty much straight out of the box, as long as the instrument 
config, roll config and price data is good. Anything else, especially production stuff, will likely need work.


## Approach
- TODO

## Assumptions
- TODO

## Additional dependencies

- [trading-ig](https://pypi.org/project/trading-ig/) - for talking to IG
- [BeautifulSoup](https://pypi.org/project/beautifulsoup4/) - web scraping
- [requests](https://pypi.org/project/requests/) - HTTP requests
- [tenacity](https://pypi.org/project/tenacity/) - workaround for IG API rate limits
- [ratelimit](https://pypi.org/project/ratelimit/) - avoid hitting Alpha Vantage API rate limits

## Licensing and legal (adapted from upstream)

GNU v3 (See [LICENSE](LICENSE))

Absolutely no warranty is implied with this product. Use at your own risk. I provide no guarantee that it will be 
profitable, or that it won't lose all your money very quickly, or delete every file on your computer (by the way: it's 
not *supposed* to do that. Just in case you thought it was). All financial trading offers the possibility of loss. 
Spread betting may result in you losing all your money, and still owing more. Backtested 
results are no guarantee of future performance. I can take no responsibility for any losses caused by live trading 
using this code. I am not registered or authorised by any financial regulator. 


