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
- daily price updates from IG and [Barchart](https://www.barchart.com/) 
- daily FX updates from [Alpha Vantage](https://www.alphavantage.co/)
- Futures Spread Bets (FSBs) are represented internally as futures instruments, but with codes like GOLD_fsb, SP500_fsb
- Custom dataBroker, dataBlob classes
- custom scripts for data setup/import

## Assumptions
- TODO

## Challenges
- TODO

## Quickstart
- TODO

## Additional dependencies

- [trading-ig](https://pypi.org/project/trading-ig/) - for talking to IG
- [BeautifulSoup](https://pypi.org/project/beautifulsoup4/) - web scraping
- [requests](https://pypi.org/project/requests/) - HTTP requests
- [ratelimit](https://pypi.org/project/ratelimit/) - avoid hitting API rate limits

## Licensing and legal (copied from upstream)

GNU v3 (See [LICENSE](LICENSE))

Absolutely no warranty is implied with this product. Use at your own risk. I provide no guarantee that it will be 
profitable, or that it won't lose all your money very quickly, or delete every file on your computer (by the way: it's 
not *supposed* to do that. Just in case you thought it was). All financial trading offers the possibility of loss. 
Leveraged trading, such as futures trading, may result in you losing all your money, and still owing more. Backtested 
results are no guarantee of future performance. I can take no responsibility for any losses caused by live trading 
using pysystemtrade. Use at your own risk. I am not registered or authorised by any financial regulator. 


