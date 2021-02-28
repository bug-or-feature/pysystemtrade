"""
Update spot FX prices using Alpha Vantage data, dump into mongodb
https://www.alphavantage.co/
"""

from syscore.objects import success, failure, arg_not_supplied
from syscore.merge_data import spike_in_data
from sysdata.data_blob import dataBlob
from sysproduction.data.currency_data import dataCurrency
from sysdata.arctic.arctic_spotfx_prices import arcticFxPricesData
from sysdata.alphavantage.av_spot_FX_data import avFxPricesData
from sysproduction.data.alt_data_source import altDataSource
from sysproduction.update_fx_prices import updateFxPrices


def update_fx_prices_alphavantage():
    """
    Update FX prices stored in Arctic (Mongo) with Alpha Vantage prices

    :return: success
    """

    # Called as standalone
    with dataBlob(log_name="Update-FX-Prices-AV",
            ib_conn=arg_not_supplied,
            class_list=[arcticFxPricesData]) as data:
        update_fx_prices_object = updateFxPricesAlphaVantage(data)
        update_fx_prices_object.update_fx_prices()

    return success


class updateFxPricesAlphaVantage(updateFxPrices):

    def __init__(self, data):
        super().__init__(data)
        self.data = data

    def update_fx_prices_with_data(self, data: dataBlob):
        fx_source = dataCurrency(data)
        list_of_codes_all = (
            fx_source.get_list_of_fxcodes()
        )
        data.log.msg("FX Codes: %s" % str(list_of_codes_all))

        for fx_code in list_of_codes_all:
            data.log.label(fx_code=fx_code)
            self.update_fx_prices_for_code(fx_code, data)

    def update_fx_prices_for_code(self, fx_code: str, data: dataBlob):

        read_data = dataBlob(log_name="Source-FX-Prices-AV",
                    ib_conn=arg_not_supplied,
                    class_list=[avFxPricesData])

        fx_source = altDataSource(read_data)
        db_fx_data = dataCurrency(data)

        new_fx_prices = fx_source.get_fx_prices(
            fx_code)  # returns fxPrices object
        rows_added = db_fx_data.update_fx_prices_and_return_rows_added(
            fx_code, new_fx_prices, check_for_spike=True
        )

        if rows_added is spike_in_data:
            self.report_fx_data_spike(data, fx_code)
            return failure

        return success
