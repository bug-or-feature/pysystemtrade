# Release notes

This document describes changes to this fork. For upstream master, see [CHANGELOG](CHANGELOG.md)

## Status
- Upstream version: 1.80

## TODO
See
- [Issues](https://github.com/bug-or-feature/pysystemtrade-fsb/issues)
- [Roadmap / wishlist](https://github.com/bug-or-feature/pysystemtrade-fsb#roadmap--wishlist)


## July 2024
- optionally consider a subset of prices when building a roll calendar
- tool for safely modifying roll calendar options customised for FSBs
- unified buffering for systems and subsystems
- rounding strategies
- dynamic optimisation for FSBs

## June 2024
- fixed EURIBOR-ICE prices
- auto update slippage config
- send test email from Interactive Diagnostics
- improved forced roll orders

## May 2024
- easier contract skipping

## April 2024
- fix price cleaning config
- tool for manually updating fwd contract improved
- IBXEX - > IBEX
- new instruments: GAS_NL, GAS_UK, LUMBER-new, CHFJPY, EURCAD, EURCHF, GBPCHF, GBPJPY, NOK, SEK

## February 2024
- split frequency prices
- JPY prices rebuilt for changed multiplier
- improved static instrument selection report

## January 2024
- Improved Trade report
- move to Python logging complete
- affected deals written to db on trade completed

## December 2023
- better IG error handling
- better minimum bet handling
- Improved interactive rolling

## November 2023
- improved IG market info collection
- improved handling for minimum bets
- minimum bet overrides for DEMO env defined in config
- market hours overrides per instrument
- merge in upstream changes for Parquet, updated Python and pandas

## October 2023
- improved IG market info collection
- better fractional positions / fills
- improved FSB report
- instrument config uses IG names for Description
- pre submit order validation

## September 2023
- better fractional position saving
- new adhoc report compares FSB risk with Future per instrument
- new adhoc report plots FSB adjusted price vs Future
- simpler/better FSB market info collection
- new section in FSB report highlights undefined forward contract epics

## July - August 2023
- interactive order stack adapted for FSBs
- automated trading of FSBs
- custom market algo for FSBs
- rebuild of AEX_fsb, BRENT_W_fsb price data
- improved market info retrieval, now continuous
- custom balance trade for positions auto rolled by IG
- allow viewing of market info from Interactive Diagnostics
- don't allow 'Force' roll state
- custom script to adjust forward/carry when IG skip a contract

## June 2023
- checks for valid epics on roll
- temporary roll cycle overrides
- FSB roll report improvements
- rebuild of EURIBOR-ICE_fsb price data
- FSB version of `clone_data_for_instrument()`
- FSB version of `delete_instrument_from_prices()` in Interactive Controls

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
