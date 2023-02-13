import logging

from syscore.dateutils import DAILY_PRICE_FREQ, Frequency
from syscore.pandas.merge_data_keeping_past_data import SPIKE_IN_DATA
from syscore.constants import success, failure
from sysdata.data_blob import dataBlob
from syslogdiag.email_via_db_interface import send_production_mail_msg
from sysobjects.contracts import futuresContract
from sysproduction.data.broker import dataBroker
from sysproduction.data.contracts import dataContracts
from sysproduction.data.fsb_prices import UpdateFsbPrices
from sysproduction.data.prices import diagPrices


def update_historical_fsb_prices():
    """
    Do a daily update for FSB contract prices, using IG historical data

    :return: Nothing
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    with dataBlob(log_name="Update-Historical-FSB-Prices") as data:
        price_data = diagPrices(data)
        list_of_codes_all = price_data.get_list_of_instruments_in_multiple_prices()
        update_historical_fsb_prices = updateHistoricalFsbPrices(
            data, list_of_codes_all
        )
        update_historical_fsb_prices.update_prices()
    return success


def update_historical_fsb_prices_single(instrument_list=None):
    """
    Do a daily update for FSB contract prices, using IG historical data

    :return: Nothing
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    with dataBlob(log_name="Update-Historical-FSB-Prices") as data:
        update_historical_fsb_prices = updateHistoricalFsbPrices(data, instrument_list)
        update_historical_fsb_prices.update_prices()
    return success


class updateHistoricalFsbPrices(object):
    def __init__(self, data, instrument_list=None):
        self.data = data
        self._instrument_list = instrument_list

    def update_prices(self):
        update_historical_prices_with_data(self.data, self._instrument_list)


def update_historical_prices_with_data(data: dataBlob, instrument_list=None):
    price_data = diagPrices(data)
    if instrument_list is None:
        list_of_codes_all = price_data.get_list_of_instruments_in_multiple_prices()
    else:
        list_of_codes_all = instrument_list
    for instrument_code in list_of_codes_all:
        data.log.msg(f"Starting processing for instrument {instrument_code}")
        data.log.label(instrument_code=instrument_code)
        update_historical_fsb_prices_for_instrument(instrument_code, data)


def update_historical_fsb_prices_for_instrument(instrument_code: str, data: dataBlob):
    """
    Do a daily update for FSB contract prices, using IG historical data

    :param instrument_code: str
    :param data: dataBlob
    :return: None
    """
    diag_contracts = dataContracts(data)
    all_contracts_list = diag_contracts.get_all_contract_objects_for_instrument_code(
        instrument_code
    )
    contract_list = all_contracts_list.currently_sampling()

    if len(contract_list) == 0:
        data.log.warn("No contracts marked for sampling for %s" % instrument_code)
        return failure

    for contract_object in contract_list:
        data.log.label(contract_date=contract_object.date_str)
        data.log.msg(f"Starting processing for contract {contract_object.key}")
        # update contract_object params so that we know to get data from IG, not Barchart
        contract_object.params.data_source = "IG"
        update_historical_prices_for_instrument_and_contract(contract_object, data)

    return success


def update_historical_prices_for_instrument_and_contract(
    contract_object: futuresContract, data: dataBlob
):
    """
    Do a daily update for futures contract prices, using IG historical data

    :param contract_object: futuresContract
    :param data: data blob
    :return: None
    """
    diag_prices = diagPrices(data)
    # intraday_frequency = diag_prices.get_intraday_frequency_for_historical_download()
    # daily_frequency = DAILY_PRICE_FREQ

    # Get daily prices
    result = get_and_add_prices_for_frequency(
        data, contract_object, frequency=DAILY_PRICE_FREQ
    )
    if result is failure:
        return None


def get_and_add_prices_for_frequency(
    data: dataBlob,
    contract_object: futuresContract,
    frequency: Frequency = DAILY_PRICE_FREQ,
):
    broker_data_source = dataBroker(data)
    db_fsb_prices = UpdateFsbPrices(data)

    broker_prices = broker_data_source.get_prices_at_frequency_for_contract_object(
        contract_object, frequency
    )

    if broker_prices is failure:
        print(
            "Something went wrong with getting prices for %s to check"
            % str(contract_object)
        )
        return failure

    if len(broker_prices) == 0:
        print("No broker prices found for %s nothing to check" % str(contract_object))
        return success
    else:
        data.log.msg(f"broker_prices latest price {broker_prices.index[-1]}")

    error_or_rows_added = db_fsb_prices.update_prices_for_contract(
        contract_object, broker_prices, check_for_spike=False
    )

    if error_or_rows_added is SPIKE_IN_DATA:
        report_price_spike(data, contract_object)
        return failure

    data.log.msg(
        "Added %d rows at frequency %s for %s"
        % (error_or_rows_added, frequency, str(contract_object))
    )
    return success


def report_price_spike(data: dataBlob, contract_object: futuresContract):
    # SPIKE
    # Need to email user about this as will need manually checking
    msg = (
        "Spike found in prices for %s: need to manually check by running interactive_manual_check_historical_prices"
        % str(contract_object)
    )
    data.log.warn(msg)
    try:
        send_production_mail_msg(
            data, msg, "Price Spike %s" % contract_object.instrument_code
        )
    except BaseException:
        data.log.warn(
            "Couldn't send email about price spike for %s" % str(contract_object)
        )


if __name__ == "__main__":
    update_historical_fsb_prices_single(["SP500_fsb"])
