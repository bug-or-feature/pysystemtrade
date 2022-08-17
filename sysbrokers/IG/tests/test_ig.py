import pytest
from sysbrokers.IG.ig_instruments_data import IgFuturesInstrumentData
from sysbrokers.IG.ig_futures_contract_data import IgFuturesContractData
from sysbrokers.IG.ig_connection import IGConnection
from sysobjects.contracts import futuresContract as fc
from sysobjects.contract_dates_and_expiries import expiryDate
from syscore.objects import missing_contract


class TestIg:

    def test_ig_instrument_data(self):
        instr_data = IgFuturesInstrumentData(
            epic_history_datapath="data.futures_spreadbets.epic_history_csv"
        )
        instr_list = instr_data.get_list_of_instruments()
        assert len(instr_list) > 0

    def test_ig_epic_mapping_good(self):
        instr_data = IgFuturesInstrumentData(
            epic_history_datapath="sysbrokers.IG.tests.epic_history_csv_good"
        )
        assert "BUXL_fsb/20220300" in instr_data.epic_mapping
        assert "BUXL_fsb/20220300" in instr_data.expiry_dates
        assert "VIX_fsb/20210600" in instr_data.expiry_dates
        assert "GOLD_fsb/20210800" in instr_data.expiry_dates

    def test_ig_epic_mapping_bad(self):
        instr_data = IgFuturesInstrumentData(
            epic_history_datapath="sysbrokers.IG.tests.epic_history_csv_bad"
        )
        with pytest.raises(Exception):
            instr_data.epic_mapping.values()

    def test_fsb_contract_ids(self):

        contracts = IgFuturesContractData(
            broker_conn=IGConnection(auto_connect=False),
            instr_data=IgFuturesInstrumentData(
                epic_history_datapath="data.futures_spreadbets.epic_history_csv"
            )
        )

        assert contracts.get_barchart_id(fc.from_two_strings("GOLD_fsb", "20210600")) == "GCM21"

        assert contracts.get_barchart_id(fc.from_two_strings("EDOLLAR_fsb", "20200300")) == "GEH20"

        assert contracts.get_barchart_id(fc.from_two_strings("AEX_fsb", "20190900")) == "AEU19"

        assert contracts.get_barchart_id(fc.from_two_strings("GBP_fsb", "20181200")) == "B6Z18"

        assert contracts.get_barchart_id(fc.from_two_strings("LEANHOG_fsb", "20000200")) == "HEG00"

        assert contracts.get_barchart_id(fc.from_two_strings("PLAT_fsb", "20020400")) == "PLJ02"

        with pytest.raises(Exception):
            contracts.get_barchart_id(fc.from_two_strings("BLAH_fsb", "20210600"))

        with pytest.raises(Exception):
            contracts.get_barchart_id(fc.from_two_strings("AUD_fsb", "20201300"))

    def test_futures_contract_ids(self):

        contracts = IgFuturesContractData(
            broker_conn=IGConnection(auto_connect=False),
            instr_data=IgFuturesInstrumentData(
                epic_history_datapath="data.futures_spreadbets.epic_history_csv"
            )
        )

        assert contracts.get_barchart_id(fc.from_two_strings("GOLD", "20210600")) == "GCM21"

        assert contracts.get_barchart_id(fc.from_two_strings("EDOLLAR", "20200300")) == "GEH20"

        assert contracts.get_barchart_id(fc.from_two_strings("AEX", "20190900")) == "AEU19"

        assert contracts.get_barchart_id(fc.from_two_strings("GBP", "20181200")) == "B6Z18"

        assert contracts.get_barchart_id(fc.from_two_strings("LEANHOG", "20000200")) == "HEG00"

        assert contracts.get_barchart_id(fc.from_two_strings("PLAT", "20020400")) == "PLJ02"

        with pytest.raises(Exception):
            contracts.get_barchart_id(fc.from_two_strings("BLAH", "20210600"))

        with pytest.raises(Exception):
            contracts.get_barchart_id(fc.from_two_strings("AUD", "20201300"))


    def test_expiry_dates(self):

        contracts = IgFuturesContractData(
            broker_conn=IGConnection(auto_connect=False),
            instr_data=IgFuturesInstrumentData(
                epic_history_datapath="sysbrokers.IG.tests.epic_history_csv_good"
            )
        )

        expiry = contracts.get_actual_expiry_date_for_single_contract(
            fc.from_two_strings("GOLD_fsb", "20220400")
        )
        assert expiry == expiryDate.from_str("20220328")

        expiry = contracts.get_actual_expiry_date_for_single_contract(
            fc.from_two_strings("BUXL_fsb", "20211200")
        )
        assert expiry == expiryDate.from_str("20211207")

        expiry = contracts.get_actual_expiry_date_for_single_contract(
            fc.from_two_strings("VIX_fsb", "20220300")
        )
        assert expiry == expiryDate.from_str("20220315")

        # not in config, should give approx date, 28th of contract month
        expiry = contracts.get_actual_expiry_date_for_single_contract(
            fc.from_two_strings("EUR_fsb", "19900300")
        )
        assert expiry == expiryDate.from_str("19900328")

        # unknown fsb instr
        expiry = contracts.get_actual_expiry_date_for_single_contract(
            fc.from_two_strings("CRAP_fsb", "20220300")
        )
        assert expiry == missing_contract

        # unknown futures instr
        expiry = contracts.get_actual_expiry_date_for_single_contract(
            fc.from_two_strings("CRAP", "20220300")
        )
        assert expiry == missing_contract