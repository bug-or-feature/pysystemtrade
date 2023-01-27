from sysdata.data_blob import dataBlob
from sysobjects.contracts import futuresContract

from sysproduction.data.contracts import dataContracts
from sysproduction.data.positions import diagPositions
from sysproduction.reporting.data.rolls import (
    relative_volume_in_forward_contract_and_price,
    volume_contracts_in_forward_contract,
)


def get_roll_data_for_fsb_instrument(instrument_code, data: dataBlob):
    """
    Get roll data for an individual FSB instrument

    :param instrument_code: str
    :param data: dataBlob
    :return:
    """
    c_data = dataContracts(data)
    contract_priced = c_data.get_priced_contract_id(instrument_code)
    contract_fwd = c_data.get_forward_contract_id(instrument_code)

    relative_volumes = relative_volume_in_forward_contract_and_price(
        data, instrument_code
    )
    relative_volume_fwd = relative_volumes[1]

    contract_volume_fwd = volume_contracts_in_forward_contract(data, instrument_code)

    # length to expiries / length to suggested roll

    price_expiry_days = c_data.days_until_price_expiry(instrument_code)
    carry_expiry_days = c_data.days_until_carry_expiry(instrument_code)
    when_to_roll_days = c_data.days_until_roll(instrument_code)

    # roll status
    diag_positions = diagPositions(data)
    roll_status = diag_positions.get_name_of_roll_state(instrument_code)

    # Positions
    position_priced = diag_positions.get_position_for_contract(
        futuresContract(instrument_code, contract_priced)
    )

    # tradeability
    try:
        priced_status = data.db_market_info.in_hours_status[
            f"{instrument_code}/{contract_priced}"
        ]
    except KeyError:
        priced_status = "n/a"

    try:
        fwd_status = data.db_market_info.in_hours_status[
            f"{instrument_code}/{contract_fwd}"
        ]
    except KeyError:
        fwd_status = "n/a"

    results_dict_code = dict(
        status=roll_status,
        roll_expiry=when_to_roll_days,
        price_expiry=price_expiry_days,
        carry_expiry=carry_expiry_days,
        contract_priced=contract_priced,
        contract_fwd=contract_fwd,
        position_priced=position_priced,
        relative_volume_fwd=relative_volume_fwd,
        contract_volume_fwd=contract_volume_fwd,
        priced_status=priced_status,
        fwd_status=fwd_status,
    )

    return results_dict_code
