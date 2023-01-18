from sysbrokers.IG.ig_instruments import (
    FsbInstrumentWithIgConfigData,
)
from sysdata.data_blob import dataBlob
from sysdata.mongodb.mongo_market_info import mongoMarketInfoData
from sysproduction.data.broker import dataBroker
from syscore.exceptions import existingData

"""
Initialise mongdb with market data for each epic

"""


def import_market_info_single(instr):
    with dataBlob() as data:
        data.add_class_object(mongoMarketInfoData)
        broker = dataBroker(data)
        _do_single(data, broker, instr)


def import_market_info_all():

    with dataBlob() as data:
        data.add_class_object(mongoMarketInfoData)
        broker = dataBroker(data)

        # instr_list = ["GOLD_fsb"]
        instr_list = [
            instr_code
            for instr_code in data.broker_futures_instrument.get_list_of_instruments()
            if instr_code.endswith("_fsb")
        ]

        for instr in sorted(instr_list):
            _do_single(data, broker, instr)


def _get_instr_config(broker, instr) -> FsbInstrumentWithIgConfigData:
    return broker.broker_futures_instrument_data.get_futures_instrument_object_with_ig_data(
        instr
    )


def _do_single(data, broker, instr):

    print(f"Importing market info for {instr}")

    config = _get_instr_config(broker, instr)

    if not hasattr(config, "ig_data"):
        data.log.msg(f"Skipping {instr}, no IG config")
        return None

    if len(config.ig_data.periods) == 0:
        data.log.msg(f"Skipping {instr}, no epics defined")
        return None

    for period in config.ig_data.periods:
        epic = f"{config.ig_data.epic}.{period}.IP"

        try:
            info = data.broker_conn.get_market_info(epic)
            data.db_market_info.add_market_info(instr, epic, info)
        except existingData as mde:
            msg = (
                f"Cannot overwrite market info for instrument '{instr}' "
                f"and epic '{epic}': {mde}"
            )
            data.log.warn(msg)
        except Exception as exc:
            msg = (
                f"Problem updating market info for instrument '{instr}' "
                f"and epic '{epic}' - check config: {exc}"
            )
            data.log.critical(msg)


def test_get_for_instr_code():
    with dataBlob() as data:
        data.add_class_object(mongoMarketInfoData)
        results = data.db_market_info.get_market_info_for_instrument_code("CRUDE_W_fsb")
        print(results)


def test_get_instruments():
    with dataBlob() as data:
        data.add_class_object(mongoMarketInfoData)
        results = data.db_market_info.get_list_of_instruments()
        print(results)

def test_get_expiry_details():
    with dataBlob() as data:
        data.add_class_object(mongoMarketInfoData)
        result = data.db_market_info.get_expiry_details("MT.D.GC.MONTH1.IP")
        print(result)


if __name__ == "__main__":
    # import_market_info_single("GOLD_fsb")

    # for instr in ["GOLD_fsb", "AUD_fsb", "BOBL_fsb", "NASDAQ_fsb"]:
    #      import_market_info_single(instr)

    import_market_info_all()

    # test_get_for_instr_code()

    # test_get_instruments()

    #test_get_expiry_details()
