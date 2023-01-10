import logging
from datetime import timedelta

from sysbrokers.IG.ig_instruments import FsbInstrumentWithIgConfigData
from syscore.objects import success
from syscore.text import remove_suffix
from sysdata.data_blob import dataBlob
from sysobjects.contracts import futuresContract
from sysproduction.data.broker import dataBroker
from sysproduction.data.prices import diagPrices
from sysproduction.update_sampled_contracts import get_contract_chain


def generate_fsb_updates():
    """
    Generate daily contract FSB price updates from Futures contract prices

    :return: Nothing
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    with dataBlob(log_name="Generate-FSB-Updates") as data:
        fsb_updater = GenerateFsbUpdates(data)
        # fsb_updater.generate_fsb_updates()
        fsb_updater.update("NASDAQ_fsb")
        # fsb_updater.update_list(["BUXL_fsb", "GOLD_fsb", "NASDAQ_fsb", "NZD_fsb", "US10_fsb"])
    return success


class GenerateFsbUpdates(object):
    def __init__(self, data):
        self._data = data
        self._broker = dataBroker(data)
        self._prices = diagPrices(data)

    @property
    def data(self):
        return self._data

    @property
    def instrument_data(self):
        return self._broker.broker_futures_instrument_data

    @property
    def price_data(self):
        return self._prices.db_futures_contract_price_data

    def get_update_list(self):
        return self._prices.get_list_of_instruments_in_multiple_prices()

    def generate_fsb_updates(self):
        for instr in self.get_update_list():
            self.update(instr)

    def update_list(self, instr_list):
        for instr in instr_list:
            self.update(instr)

    def update(self, instr_code):
        self.data.log.label(instrument_code=instr_code)

        futures_code = remove_suffix(instr_code, "_fsb")
        self.data.log.msg(
            f"Starting generation of FSB price updates from {futures_code}"
        )

        fsb_chain = get_contract_chain(self.data, instr_code)
        self.data.log.msg(f"FSB contract chain: {fsb_chain}")

        for fsb_contract in fsb_chain:

            self.data.log.msg(f"Generating FSB price updates for {fsb_contract}")

            fut_contract = futuresContract.from_two_strings(
                futures_code, fsb_contract.date_str
            )

            fut_prices = self.price_data.get_merged_prices_for_contract_object(
                fut_contract
            )
            if fut_prices.shape[0] == 0:
                self.data.log.msg(f"No futures data for {fut_contract}, ignoring")
                continue

            else:
                instr_config = self._get_instr_config(instr_code)
                fut_prices_massaged = self._do_price_massage(
                    fut_contract,
                    fut_prices,
                    instr_config.multiplier,
                    instr_config.inverse,
                )

            # do we have FSB prices for this contract?
            fsb_prices = self.price_data.get_merged_prices_for_contract_object(
                fsb_contract
            )

            if fsb_prices.shape[0] > 0:
                existing_size = fsb_prices.shape[0]
                self.data.log.msg(
                    f"Existing FSB prices found ({existing_size} rows) for {fsb_contract}"
                )

                # get last index date of FSB
                last_date = fsb_prices.index[-1]
                self.data.log.msg(
                    f"Latest FSB price timestamp for {fsb_contract}: {last_date}"
                )
                last_date = last_date + timedelta(hours=1)

                # add to end of existing prices
                updated = fsb_prices.append(fut_prices_massaged[last_date:])
                new_count = updated.shape[0] - existing_size
                self.data.log.msg(f"Update: adding {new_count} new rows")

            else:
                self.data.log.msg(f"Creating new FSB prices for {fsb_contract}")
                updated = fut_prices_massaged

            # create/update contract price object in db
            self.price_data.write_merged_prices_for_contract_object(
                fsb_contract, updated, ignore_duplication=True
            )

    def _get_instr_config(self, instr_code) -> FsbInstrumentWithIgConfigData:
        instr_config = self.instrument_data.get_instrument_data(instr_code)
        return instr_config

    def _do_price_massage(
        self,
        contract_object: futuresContract,
        prices,
        multiplier: float = 1.0,
        inverse: bool = False,
    ):
        self.data.log.msg(
            f"Massaging prices for IG: multiplier {multiplier}, inverse {inverse}",
            instrument_code=contract_object.instrument_code,
            contract_date=contract_object.contract_date.date_str,
        )
        for col_name in ["OPEN", "HIGH", "LOW", "FINAL"]:
            series = prices[col_name]
            if inverse:
                series = 1 / series
            series *= multiplier
            prices[col_name] = series

        return prices


if __name__ == "__main__":
    generate_fsb_updates()
