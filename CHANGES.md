# Release notes

This document describes changes to this fork. For upstream master, see [CHANGELOG](CHANGELOG.md)

## Status
- Upstream version: 1.61

## TODO
- See [Issues](https://github.com/bug-or-feature/pysystemtrade-fsb/issues)


## May 2023
- implementing upstream CSV instrument and roll config
- Python logging improvements
- compound mongo indexes
- margin / capital improvements
- temp fix for FSB position sizes in sim
- new project site, with docs, reports, blog

## April 2023
- starting move to Python logging
- capital improvements
- add support for connection to both IG live and demo, depending on API endpoint
- new section in FSB report showing delayed market info
- new section in FSB report showing misconfigured minimum bets
- improved spread sampling

## March 2023
- More resolutions for IG prices
- add history sync status to market info storage

## February 2023
- New section in FSB reports shows potential roll issues
- automatic epic discovery

## January 2023
- new instruments: SUGAR_WHITE_fsb, OMXS30_fsb, EURGBP, JSE40_fsb
- roll calendar adjustments for IG
- custom FSB remove markets report ignoring Volume
- adding auto Black
- retrieve FSB Market Info from IG and persist to mongo
- calculate epic history from market info
- IG trading hours
- tradeable status added to roll and FSB reports
- split FSB correlation reports: priced and forward
- implement `is_contract_okay_to_trade()` from market info

## Oct 2022 - Dec 2022 ish
- improved process monitor
- dataBlob connects to both IG REST and Streaming API
- sampling spreads with IG Streaming API
- Slippage report customised for FSBs
- easier way to run individual reports outside scheduling context
- removing site reports
- new instruments: BRENT_W_fsb, COCOA_LDN_fsb, COCOA_fsb, CORN_fsb, COTTON2_fsb, GASOIL_fsb, GASOLINE_fsb, HEATOIL_fsb, LEANHOG_fsb, LIVECOW_fsb, LUMBER_fsb, OATIES_fsb, OJ_fsb, PALLAD_fsb, PLAT_fsb, RICE_fsb, ROBUSTA_fsb, SOYMEAL_fsb, SUGAR11_fsb, WHEAT_ICE_fsb, EURIBOR_fsb, VIX_fsb, FED_fsb, SONIA3_fsb
- auto syncing price updates back to repo
- init files refactored 

## Jul 2022 - Sep 2022 ish
- get Futures prices from Barchart, derive FSB prices
- reports auto published to [project site](https://bug-or-feature.github.io/pysystemtrade-fsb/reports/)
- custom private dir
- hourly/daily price split (from upstream)
- better process viewer

## Apr 2022 - Jun 2022 ish
- streamline config
- arctic epic history 
- FSB min capital report
- FSB instr risk report
- remove ib-insync dependency
- view FSB prices, epic history in interactive_diagnostics
- FSB report
- project site github page
- custom broker classes in config

## Jan 2022 - Mar 2022 ish
- csv epic history
- more instruments
- better checks for new instruments
- first cut of spread sampling
- better interactive scripts with Flask
- persistence of contract expiry source

## Dec 2021 - Jan 2022 ish
- epic mapping as YAML config
- commandline fsb script
- IG broker code updates

## Oct 2021 - Nov 2021 ish
- fsb system runner
- fractional position sizes
- getting current position info from IG
- running individual reports from the command line
- handle Barchart rate limits
- buffered positions
- FSBs are now futures internally: GOLD -> GOLD_fsb

## Aug 2021 - Sep 2021 ish
- converting costs calculator into an fsb 'system'
- moving from NAS to MacOS, NAS too slow
- custom RawData for FSB
- adding second batch of FSB instruments
- getting capital from IG

## Jun 2021 - Jul 2021 ish
- FSB costs calculator script 
- Simple Moving Average Crossover rule
- holding costs attempt
- integrating IG prices with trading_ig
- Synology NAS prod scripts 

## Apr 2021 - May 2021 ish
- Futures spread bet instrument and roll config 
- first cut of FSB 'system'

## Feb 2021 - March 2021 ish
- getting daily price updates from Barchart
- getting daily FX updates from Alphavantage

## May 2020 - Jan 2021 ish
- Lots of docs fixes and tidy up
- Attempted Docker implementation
