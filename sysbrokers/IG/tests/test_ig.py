import pytest
from sysbrokers.IG.ig_instruments_data import IgFuturesInstrumentData
from sysbrokers.IG.ig_futures_contract_data import IgFuturesContractData
from sysobjects.contracts import futuresContract as fc
from sysobjects.contract_dates_and_expiries import expiryDate
from syscore.exceptions import missingContract
from sysdata.data_blob import dataBlob
from sysdata.csv.csv_fsb_epics_history_data import CsvFsbEpicHistoryData
from sysdata.json.json_market_info import jsonMarketInfoData


class TestIg:
    def test_ig_instrument_data(self):
        data = dataBlob(
            auto_connect=False,
            csv_data_paths=dict(
                csvFuturesInstrumentData="data.futures_spreadbets.epic_history_csv"
            )
        )
        data.add_class_object(IgFuturesInstrumentData)
        instr_list = data.broker_futures_instrument.get_list_of_instruments()
        assert len(instr_list) > 0

    def test_ig_epic_mapping_good(self):
        data = dataBlob(
            auto_connect=False,
            csv_data_paths=dict(
                jsonMarketInfoData="sysbrokers.IG.tests.market_info_json_good"
            )
        )
        data.add_class_object(jsonMarketInfoData)

        assert "BUXL_fsb/20230300" in data.db_market_info.epic_mapping
        assert "NZD_fsb/20230300" in data.db_market_info.expiry_dates
        assert "GOLD_fsb/20230200" in data.db_market_info.expiry_dates

    def test_ig_epic_mapping_bad(self):
        data = dataBlob(
            auto_connect=False,
            csv_data_paths=dict(
                jsonMarketInfoData="sysbrokers.IG.tests.market_info_json_bad"
            )
        )
        data.add_class_object(jsonMarketInfoData)

        with pytest.raises(Exception):
            data.db_market_info.epic_mapping.values()

    def test_fsb_contract_ids(self):
        data = dataBlob(
            auto_connect=False,
            csv_data_paths=dict(
                csvFuturesInstrumentData="data.futures_spreadbets.epic_history_csv"
            )
        )
        data.add_class_list([IgFuturesContractData, IgFuturesInstrumentData])

        assert (
            data.broker_futures_contract.get_barchart_id(
                fc.from_two_strings("GOLD_fsb", "20210600")
            )
            == "GCM21"
        )

        assert (
            data.broker_futures_contract.get_barchart_id(
                fc.from_two_strings("EDOLLAR_fsb", "20200300")
            )
            == "GEH20"
        )

        assert (
            data.broker_futures_contract.get_barchart_id(
                fc.from_two_strings("AEX_fsb", "20190900")
            )
            == "AEU19"
        )

        assert (
            data.broker_futures_contract.get_barchart_id(
                fc.from_two_strings("GBP_fsb", "20181200")
            )
            == "B6Z18"
        )

        assert (
            data.broker_futures_contract.get_barchart_id(
                fc.from_two_strings("LEANHOG_fsb", "20000200")
            )
            == "HEG00"
        )

        assert (
            data.broker_futures_contract.get_barchart_id(
                fc.from_two_strings("PLAT_fsb", "20020400")
            )
            == "PLJ02"
        )

        with pytest.raises(Exception):
            data.broker_futures_contract.get_barchart_id(
                fc.from_two_strings("BLAH_fsb", "20210600")
            )

        with pytest.raises(Exception):
            data.broker_futures_contract.get_barchart_id(
                fc.from_two_strings("AUD_fsb", "20201300")
            )

    def test_futures_contract_ids(self):
        data = dataBlob(
            auto_connect=False,
            csv_data_paths=dict(
                csvFuturesInstrumentData="data.futures_spreadbets.epic_history_csv"
            )
        )
        data.add_class_list([IgFuturesContractData, IgFuturesInstrumentData])

        assert (
            data.broker_futures_contract.get_barchart_id(
                fc.from_two_strings("GOLD", "20210600")
            )
            == "GCM21"
        )

        assert (
            data.broker_futures_contract.get_barchart_id(
                fc.from_two_strings("EDOLLAR", "20200300")
            )
            == "GEH20"
        )

        assert (
            data.broker_futures_contract.get_barchart_id(
                fc.from_two_strings("AEX", "20190900")
            )
            == "AEU19"
        )

        assert (
            data.broker_futures_contract.get_barchart_id(
                fc.from_two_strings("GBP", "20181200")
            )
            == "B6Z18"
        )

        assert (
            data.broker_futures_contract.get_barchart_id(
                fc.from_two_strings("LEANHOG", "20000200")
            )
            == "HEG00"
        )

        assert (
            data.broker_futures_contract.get_barchart_id(
                fc.from_two_strings("PLAT", "20020400")
            )
            == "PLJ02"
        )

        with pytest.raises(Exception):
            data.broker_futures_contract.get_barchart_id(
                fc.from_two_strings("BLAH", "20210600")
            )

        with pytest.raises(Exception):
            data.broker_futures_contract.get_barchart_id(
                fc.from_two_strings("AUD", "20201300")
            )

    def test_expiry_dates(self):
        data = dataBlob(
            auto_connect=False,
            csv_data_paths=dict(
                csvFuturesInstrumentData="sysbrokers.IG.tests.epic_history_csv_good"
            )
        )
        data.add_class_list(
            [
                IgFuturesContractData,
                IgFuturesInstrumentData,
                CsvFsbEpicHistoryData,
                jsonMarketInfoData,
            ]
        )

        expiry = (
            data.broker_futures_contract.get_actual_expiry_date_for_single_contract(
                fc.from_two_strings("GOLD_fsb", "20230200")
            )
        )
        assert expiry == expiryDate.from_str("20230126")  # 2023-01-26

        expiry = (
            data.broker_futures_contract.get_actual_expiry_date_for_single_contract(
                fc.from_two_strings("BUXL_fsb", "20230300")
            )
        )
        assert expiry == expiryDate.from_str("20230307")  # 2023-03-07T16:15

        expiry = (
            data.broker_futures_contract.get_actual_expiry_date_for_single_contract(
                fc.from_two_strings("NZD_fsb", "20230300")
            )
        )
        assert expiry == expiryDate.from_str("20230310")

        # not in config, should give approx date, 28th of contract month
        expiry = (
            data.broker_futures_contract.get_actual_expiry_date_for_single_contract(
                fc.from_two_strings("EUR_fsb", "19900300")
            )
        )
        assert expiry == expiryDate.from_str("19900328")

        # unknown fsb instr
        with pytest.raises(missingContract):
            data.broker_futures_contract.get_actual_expiry_date_for_single_contract(
                fc.from_two_strings("CRAP_fsb", "20220300")
            )

        # unknown futures instr
        with pytest.raises(missingContract):
            data.broker_futures_contract.get_actual_expiry_date_for_single_contract(
                fc.from_two_strings("CRAP", "20220300")
            )
