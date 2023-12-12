from sysdata.data_blob import dataBlob
from sysobjects.contracts import futuresContract

from sysproduction.data.contracts import dataContracts
from sysproduction.data.positions import diagPositions
from sysproduction.data.fsb_instruments import diagFsbInstruments
from sysproduction.reporting.data.rolls import (
    relative_volume_in_forward_contract_and_price,
    volume_contracts_in_forward_contract,
)


def get_roll_data_for_fsb_instrument(
    instrument_code,
    data: dataBlob,
    contracts: dataContracts,
    positions: diagPositions,
    fsb_instruments: diagFsbInstruments,
):
    """
    Get roll data for an individual FSB instrument

    :param instrument_code:
    :type instrument_code:
    :param data:
    :type data:
    :param contracts:
    :type contracts:
    :param positions:
    :type positions:
    :param fsb_instruments:
    :return:
    :rtype:
    """

    contract_priced = contracts.get_priced_contract_id(instrument_code)
    contract_fwd = contracts.get_forward_contract_id(instrument_code)

    relative_volumes = relative_volume_in_forward_contract_and_price(
        data, instrument_code
    )
    relative_volume_fwd = relative_volumes[1]

    contract_volume_fwd = volume_contracts_in_forward_contract(data, instrument_code)

    # length to expiries / length to suggested roll

    price_expiry_days = contracts.days_until_price_expiry(instrument_code)
    carry_expiry_days = contracts.days_until_carry_expiry(instrument_code)
    when_to_roll_days = contracts.days_until_roll(instrument_code)

    # roll status
    roll_status = positions.get_name_of_roll_state(instrument_code)

    # Position
    position_priced = positions.get_position_for_contract(
        futuresContract(instrument_code, contract_priced)
    )

    # min bet
    min_bet = fsb_instruments.get_minimum_bet(instrument_code)

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

    try:
        priced_expiry = data.db_market_info.expiry_dates[
            f"{instrument_code}/{contract_priced}"
        ]
    except KeyError:
        priced_expiry = "n/a"

    try:
        period_count = len(
            data.db_market_info.get_periods_for_instrument_code(instrument_code)
        )
    except KeyError:
        period_count = "n/a"

    results_dict_code = dict(
        status=roll_status,
        roll_exp=when_to_roll_days,
        price_exp=price_expiry_days,
        carry_exp=carry_expiry_days,
        priced=contract_priced,
        expires_at=priced_expiry,
        fwd=contract_fwd,
        pos=round(position_priced, 2),
        min=min_bet,
        rel_vol_fwd=relative_volume_fwd,
        vol_fwd=contract_volume_fwd,
        status_p=priced_status,
        status_f=fwd_status,
        periods=period_count,
    )

    return results_dict_code
