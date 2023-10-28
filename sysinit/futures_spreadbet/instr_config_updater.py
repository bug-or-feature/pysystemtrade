from munch import munchify
from sysdata.csv.csv_instrument_data import csvFuturesInstrumentData
from sysdata.mongodb.mongo_market_info import mongoMarketInfoData


def update_instr_config():
    input_data = csvFuturesInstrumentData(datapath="fsb.csvconfig")
    input_info = mongoMarketInfoData()
    df = input_data.get_all_instrument_data_as_df()
    for instr in input_info.get_list_of_instruments():
        info_list = input_info.get_market_info_for_instrument_code(instr)
        info = munchify(info_list[0])
        ig_name = info.instrument.name
        df.loc[instr, "Description"] = ig_name
        print(f"Instr: {instr}, new name: {ig_name}")

    input_data.write_all_instrument_data_from_df(df)


if __name__ == "__main__":
    update_instr_config()
