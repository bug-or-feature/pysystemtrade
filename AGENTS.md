# AGENTS.md

This file provides guidance to AI agents when working with code in this repository.

## Project Overview

**pysystemtrade** is a systematic futures trading framework (backtesting + live trading via Interactive Brokers), originally by Rob Carver, currently maintained by Andy Geach. The codebase supports both simulation/backtesting and fully automated production trading.

## Commands

### Install
```bash
# Editable install with dev dependencies
python -m pip install --editable '.[dev]'
```

### Testing
```bash
# Run all tests (doctests + unit tests as configured in pyproject.toml)
pytest

# Run a single test file
pytest sysdata/tests/test_config.py

# Skip a module
pytest --ignore=sysinit/futures/tests/test_sysinit_futures.py

# Run slow tests (marked @pytest.mark.slow, skipped by default)
pytest --runslow
```

Test paths are explicitly listed in `pyproject.toml` under `[tool.pytest.ini_options]`. Doctests are enabled for modules (`--doctest-modules`). The `examples/` directory is excluded from test collection.

### Linting / Formatting
```bash
# Format with Black (version pinned to 23.11.0 per pyproject.toml)
black . --exclude '/.venv\/.+/'
```

## Architecture

### Package Structure

Each `sys*` package has a specific role in the pipeline:

| Package | Role |
|---|---|
| `sysbrokers` | Broker abstraction layer; `IB/` contains Interactive Brokers implementation via `ib_async` |
| `syscontrol` | Process control, run-process infrastructure, monitor |
| `syscore` | Utilities: date math, pandas helpers, caching, exceptions, `arg_not_supplied` sentinel |
| `sysdata` | Data layer: abstract base classes + backends (CSV, MongoDB, Parquet, Arctic) |
| `sysexecution` | Order stack handler, algo routing, order/fill objects |
| `sysinit` | One-time data initialisation scripts (import price history, roll calendars etc.) |
| `syslogdiag` | Email control, log-to-file, log-to-screen diagnostics |
| `syslogging` | Structured logging via Python `logging`, YAML config, env-var YAML parsing |
| `sysobjects` | Domain objects: instruments, contracts, prices, rolls, fills, spreads |
| `sysproduction` | All production scripts (`run_*.py`, `update_*.py`, `interactive_*.py`, reporting) |
| `sysquant` | Quantitative logic: estimators, optimisation, portfolio risk |
| `systems` | Backtesting system pipeline (stages, caching, provided systems) |
| `private` | User's private config (`private_config.yaml`) and backtest state — never committed |

### Data Layer Pattern

`dataBlob` (`sysdata/data_blob.py`) is the central data pipeline object. It resolves class-name prefixes (`ib*`, `mongo*`, `csv*`, `parquet*`) to canonical attribute names, abstracting the underlying storage:

```python
from sysdata.data_blob import dataBlob
from sysdata.mongodb.mongo_futures_contracts import mongoFuturesContractData
from sysdata.parquet.parquet_futures_per_contract_prices import parquetFuturesContractPriceData

data = dataBlob([mongoFuturesContractData, parquetFuturesContractPriceData])
data.db_futures_contract        # → mongoFuturesContractData instance
data.db_futures_contract_price  # → parquetFuturesContractPriceData instance
```

Naming objects that participate in this hierarchy must follow the naming conventions in `docs/data.md` or the automatic attribute mapping breaks.

### Backtesting System (Stage Pipeline)

`systems/basesystem.py` defines `System`, which composes a list of `SystemStage` objects with a `simData` source and a `Config`. Stages are evaluated lazily with a `systemCache`. Provided systems are in `systems/provided/` (e.g. `futures_chapter15`, `rob_system`).

### Configuration

Configuration is layered (later overrides earlier):
1. `sysdata/config/defaults.yaml` — system-wide defaults
2. `private/private_config.yaml` — user overrides (never committed; location overridden by `PYSYS_PRIVATE_CONFIG_DIR` env var)
3. Per-system YAML config passed to `Config()`

`Config` accepts a string (YAML path), dict, or list of these. 

If the optional dependency `omegaconf` is installed, then it replaces the default Config implementation. `omegaconf` supports environment variable substitution via the `${oc.env:VAR_NAME,default}` tag.

### `arg_not_supplied` Pattern

Functions use `arg_not_supplied` (from `syscore.constants`) as default arguments instead of `None`, then resolve to the real default inside the function body. Follow this pattern for all new optional parameters.

### Coding Conventions

- Class naming: `mixedCase` preferred over `CamelCase`; single-word names use `CamelCase`
- Common method names: `get`, `calculate`, `read`, `write`
- Type hints required; use `Union`, `List`, `Dict` from `typing`
- Production code must not raise unless unrecoverable; always pair a fatal error with `log.critical()` (triggers email alert)
- Doctests in standalone functions are fine; avoid doctests on class methods (hard to set up)

## AI Policy

Per `CONTRIBUTING.md`: PRs must reflect human judgment. Do not submit AI-generated code you haven't personally reviewed, understood, and tested. If AI tools were used, mention it in the PR description.

## Branching

- `master` — stable releases
- `develop` — mirrors upstream (fork base); PRs to upstream target this branch
- `futures_dev` — production branch; contains local additions not in upstream
- Topic branches: `bug-<issue#>-<description>` or `feature-<issue#>-<description>`

### Workflow

New features and fixes are branched off `develop` (not `futures_dev`):

```bash
git checkout develop
git checkout -b feature-1234-my-feature
```

When ready to test in production, merge the feature branch onto `futures_dev`:

```bash
git checkout futures_dev
git merge feature-1234-my-feature
```

To send upstream, the feature branch merges cleanly onto `develop` (keep it rebased / free of `futures_dev`-only commits):

```bash
git checkout develop
git merge feature-1234-my-feature   # or raise a PR
```

**Important**: never merge `futures_dev` into a feature branch — that would pull in local-only production code and make the branch impossible to send upstream cleanly.

## Production

In live trading there are multiple processes that run at different times of the day relative to trading hours. Start/end times, loop frequencies and interdependencies are defined in config 

### Outside trading hours

These processes run after the end of the trading day. Prices are updated, optimal positions are calculated, and orders are generated for the next trading day. Then, there are some housekeeping tasks: clean up, backup and reporting. Each of these processes depends on the previous one to finish, they do not run at the same time

1. `run_daily_prices_updates` (updates contract prices)
2. `run_daily_update_multiple_adjusted_prices` (generate multiple and adjusted prices)
3. `run_systems` (calculates optimal positions)
4. `run_strategy_order_generator` (calculates orders based on optimal and current positions)
5. `run_cleaners` (cleans up old logs and system files)
6. `run_backups` (backs up files)
7. `run_reports` (generates reports)

### During trading hours

These processes run during trading hours, concurrently, looping constantly at variable rates

- `run_capital_update` (updates the trading capital, constantly changing due to instrument price fluctuation)
- `run_stack_handler` (executes trades, maintains local state)
- `run_monitor` (monitors the processes, reports status to an internal dashboard)

This process executes once only - timing not important

- `run_daily_fx_and_contract_updates` (updates FX prices and contract expiration status)
