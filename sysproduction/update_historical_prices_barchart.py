"""
Update historical data per contract from Barchart, dump into mongodb
"""

from syscore.objects import success, failure, arg_not_supplied
from syscore.merge_data import spike_in_data

from syscore.dateutils import DAILY_PRICE_FREQ, Frequency

from sysobjects.contracts import futuresContract

from sysdata.data_blob import dataBlob
from sysproduction.data.prices import diagPrices, updatePrices
from sysproduction.data.alt_data_source import altDataSource
from sysproduction.data.contracts import dataContracts
from syslogdiag.email_via_db_interface import send_production_mail_msg

from sysdata.barchart.bc_futures_contract_price_data import barchartFuturesContractPriceData
from sysproduction.update_historical_prices import updateHistoricalPrices


def update_historical_prices_barchart():
    """
    Do a daily update for futures contract prices, using Barchart historical data

    :return: Nothing
    """
    with dataBlob(log_name="Update-Barchart-Historical-Prices",
                  ib_conn=arg_not_supplied) as data:
        update_historical_price_object = updateBarchartHistoricalPrices(data)
        update_historical_price_object.update_historical_prices()
    return success


class updateBarchartHistoricalPrices(updateHistoricalPrices):

    def __init__(self, data):
        super().__init__(data)

    def get_and_add_prices_for_frequency(
            self, data: dataBlob, contract_object: futuresContract, frequency: Frequency = DAILY_PRICE_FREQ):

        read_data = dataBlob(log_name="Source-Historical-Prices-Barchart",
                             ib_conn=arg_not_supplied,
                             class_list=[barchartFuturesContractPriceData])

        data_source = altDataSource(read_data)
        db_futures_prices = updatePrices(data)

        prices = data_source.get_prices_at_frequency_for_contract_object(
                contract_object, frequency)

        if len(prices) == 0:
            data.log.msg("No prices from Barchart for %s" % str(contract_object))
            return failure

        error_or_rows_added = db_futures_prices.update_prices_for_contract(
            contract_object, prices, check_for_spike=True
        )

        if error_or_rows_added is spike_in_data:
            self.report_price_spike(data, contract_object)
            return failure

        data.log.msg(
            "Added %d rows at frequency %s for %s"
            % (error_or_rows_added, frequency, str(contract_object))
        )
        return success
