# Release notes

This document describes changes to this fork. For upstream master, see [CHANGELOG](CHANGELOG.md)

## Status
- Upstream version: 1.47

## TODO
- See [Issues](https://github.com/bug-or-feature/pysystemtrade-fsb/issues)

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
