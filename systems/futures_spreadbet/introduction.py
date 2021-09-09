from sysdata.sim.db_fsb_sim_data import dbFsbSimData
from systems.leveraged_trading.rules import calc_smac_forecast
from systems.accounts.account_forecast import pandl_for_instrument_forecast
from matplotlib.pyplot import show


def introduction():

    data = dbFsbSimData()
    print(data.get_instrument_list())

    print(data.get_raw_price("GOLD").tail(5))

    print(data.get_instrument_raw_carry_data("GOLD").tail(6))

    instrument_code = 'GOLD'
    price = data.daily_prices(instrument_code)
    smac = calc_smac_forecast(price)
    print(smac.tail(5))
    #smac.plot()
    #show()

    account = pandl_for_instrument_forecast(forecast=smac, price=price)
    print(account.percent.stats())

    print(f"account.sharpe(): {account.sharpe()}")  ## get the Sharpe Ratio (annualised), and any other statistic which is in the stats list
    account.curve().plot()  ## plot the cumulative account curve (equivalent to account.cumsum().plot() inicidentally)
    show()
    #print(f"account.percent: {account.percent}")  ## gives a % curve
    #account.percent.drawdown().plot()  ## see the drawdowns as a percentage
    #print(f"account.weekly: {account.weekly}") ## weekly returns (also daily [default], monthly, annual)
    #print(f"account.gross.ann_mean(): {account.gross.ann_mean()}")  ## annual mean for gross returns, also costs (there are none in this simple example)


if __name__ == "__main__":
    introduction()
