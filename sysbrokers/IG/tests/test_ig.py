import pytest
from sysbrokers.IG.ig_instruments_data import IgFuturesInstrumentData


class TestIg:

    def test_ig_instrument_data(self):
        instr_data = IgFuturesInstrumentData()
        instr_list = instr_data.get_list_of_instruments()
        assert len(instr_list) > 0

    def test_ig_epic_mapping_good(self):
        instr_data = IgFuturesInstrumentData(
            epic_history_datapath="sysbrokers.IG.tests.epic_history_csv_good"
        )
        assert "BUXL_fsb/20220300" in instr_data.epic_mapping
        assert "BUXL_fsb/20220300" in instr_data.expiry_dates

    def test_ig_epic_mapping_bad(self):
        instr_data = IgFuturesInstrumentData(
            epic_history_datapath="sysbrokers.IG.tests.epic_history_csv_bad"
        )
        with pytest.raises(Exception):
            instr_data.epic_mapping.values()