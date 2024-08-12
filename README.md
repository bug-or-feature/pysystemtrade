# pysystemtrade-fsb

Systematic Futures Spread Bets in Python

A fork of Rob Carver's [pysystemtrade](https://github.com/robcarver17/pysystemtrade), adapted to trade futures 
spread bets with [IG](https://www.ig.com/uk)

See upstream README [here](https://github.com/robcarver17/pysystemtrade/blob/master/README.md)

## Description

An attempt to adapt Rob Carver's [pysystemtrade](https://github.com/robcarver17/pysystemtrade) for trading
spread bets - as outlined in his book [Leveraged Trading](https://www.systematicmoney.org/leveraged-trading). Limited
to futures based dated spread bets for Indices, Bonds/Rates, Commodities and quarterly dated forward 
spread bets for FX

## Release notes

See [CHANGES](CHANGES.md) for release notes

## Differences with upstream

- custom instrument and roll config
- [IG](https://www.ig.com/uk) as broker instead of IB
- daily price updates from [Barchart](https://www.barchart.com/) and IG
- daily FX updates from [Alpha Vantage](https://www.alphavantage.co/)
- Futures Spread Bets (FSBs) are represented internally as futures instruments, but with codes like `GOLD_fsb`, 
  `SP500_fsb`
- Custom `dataBroker` and `dataBlob` classes
- fractional positions, fills
- custom market algo
- custom scripts for data setup / import

## Status (August 2024)
My own production system
- is sampling approx 90 instruments ([list](https://pysystemtrade-fsb.bugorfeature.net/reports/instruments.html))
- get capital data from IG
- runs a dynamic backtest, generating an optimised portfolio
- makes automated trades (market orders only)
- produces the following reports ([examples](https://pysystemtrade-fsb.bugorfeature.net/reports/))
  - Costs report
  - FSB report (new report)
  - Instrument risk report (customised version)
  - Market monitor report
  - Minimum capital report (customised version)
  - P&L report
  - Reconcile report
  - Remove markets report (customised version)
  - Risk report (customised version)
  - Roll report (customised version)
  - Slippage report
  - Status report
  - Strategy report
  - Trade report

## Roadmap / wishlist
- adding more instruments
- add setup instructions to docs
- implement limit orders
- implement 'best' algo

## Support

This is an open source project, maintained by one busy developer in his spare time. Same rules apply [as for upstream](https://github.com/robcarver17/pysystemtrade#a-note-on-support). It is probably not suitable for people who are not prepared to read docs, delve into code, and go deep down rabbit holes. Report a bug or feature [here](https://github.com/bug-or-feature/pysystemtrade-fsb/issues). But please read [the docs](https://pysystemtrade-fsb.bugorfeature.net/docs/) first


## Additional dependencies

- [trading-ig](https://pypi.org/project/trading-ig/) - for talking to IG
- [BeautifulSoup](https://pypi.org/project/beautifulsoup4/) - web scraping
- [requests](https://pypi.org/project/requests/) - HTTP requests
- [tenacity](https://pypi.org/project/tenacity/) - workaround for IG API rate limits
- [ratelimit](https://pypi.org/project/ratelimit/) - avoid hitting Alpha Vantage API rate limits

## Licensing and legal (adapted from upstream)

GNU v3 (See [LICENSE](LICENSE))

Absolutely no warranty is implied with this product. Use at your own risk. I provide no guarantee that it will be profitable, or that it won't lose all your money very quickly, or delete every file on your computer (by the way: it's not *supposed* to do that. Just in case you thought it was). All financial trading offers the possibility of loss. Spread betting may result in you losing all your money, and still owing more. Backtested results are no guarantee of future performance. I can take no responsibility for any losses caused by live trading using this code. I am not registered or authorised by any financial regulator. 


