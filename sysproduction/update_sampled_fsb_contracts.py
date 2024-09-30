from syscore.exceptions import missingContract
from syscore.constants import success

from sysobjects.contract_dates_and_expiries import contractDate, expiryDate
from sysobjects.contracts import futuresContract, listOfFuturesContracts
from sysobjects.rolls import contractDateWithRollParameters

from sysdata.data_blob import dataBlob
from sysproduction.data.prices import diagPrices, get_valid_instrument_code_from_user
from sysproduction.data.contracts import dataContracts
from sysproduction.update_sampled_contracts import (
    get_contract_chain,
    update_contract_database_with_contract_chain,
    update_expiries_and_sampling_status_for_contracts,
    check_key_contracts_have_not_expired,
    get_contract_expiry_from_broker,
    get_list_of_currently_sampling_contracts_in_db,
    update_contract_object_with_new_expiry_date,
)

ALL_INSTRUMENTS = "ALL"


def update_sampled_fsb_contracts(instrument_list=None):
    """
    *** This differs from the upstream version, as we need to maintain FSBs ***
    :returns: None
    """
    with dataBlob(
        log_name="Update-Sampled-FSB-Contracts",
        csv_data_paths=dict(
            csvFuturesInstrumentData="fsb.csvconfig",
            csvRollParametersData="fsb.csvconfig",
        ),
    ) as data:
        if instrument_list is None:
            update_contracts_object = updateSampledFsbContracts(data)
            instrument_code = get_valid_instrument_code_from_user(
                allow_all=True,
                all_code=ALL_INSTRUMENTS,
                prompt="FSB instrument code?",
            )
            update_contracts_object.update_sampled_contracts(
                instrument_code=instrument_code
            )
            if instrument_code is ALL_INSTRUMENTS:
                return success

            do_another = True

            while do_another:
                EXIT_CODE = "EXIT"
                instrument_code = get_valid_instrument_code_from_user(
                    allow_exit=True, exit_code=EXIT_CODE
                )
                if instrument_code is EXIT_CODE:
                    do_another = False
                else:
                    update_contracts_object.update_sampled_contracts(
                        instrument_code=instrument_code
                    )

        else:
            update_contracts_object = updateSampledFsbContracts(data, instrument_list)
            update_contracts_object.update_sampled_contracts()


class updateSampledFsbContracts(object):
    def __init__(self, data, instrument_list=None):
        self.data = data
        self._instrument_list = instrument_list

    def update_sampled_contracts(self, instrument_code: str = ALL_INSTRUMENTS):
        if self._instrument_list is None:
            update_active_contracts_with_data(
                self.data, instrument_code=instrument_code
            )
        else:
            update_active_contracts_with_data(
                self.data, instrument_list=self._instrument_list
            )


def update_active_contracts_with_data(
    data: dataBlob, instrument_code: str = ALL_INSTRUMENTS, instrument_list=None
):
    diag_prices = diagPrices(data)
    if instrument_list is not None:
        list_of_codes = instrument_list
    elif instrument_code is ALL_INSTRUMENTS:
        list_of_codes = diag_prices.get_list_of_instruments_in_multiple_prices()
    else:
        list_of_codes = [instrument_code]

    for instrument_code in list_of_codes:
        update_active_contracts_for_instrument(instrument_code, data)


def update_active_contracts_for_instrument(fsb_code: str, data: dataBlob):
    if not fsb_code.endswith("_fsb"):
        data.log.error(f"Expecting an FSB code, not {fsb_code}, exiting")
        return

    # Get the list of contracts we'd want to get prices for, given current
    # roll calendar
    required_fsb_contract_chain = get_contract_chain(data, fsb_code)

    # Make sure contract chain and database are aligned
    update_contract_database_with_contract_chain(
        fsb_code, required_fsb_contract_chain, data
    )

    # Now to check if expiry dates are matched to IB, and mark expired or unchained contracts as no longer sampling
    update_expiries_and_sampling_status_for_contracts(
        fsb_code, data, contract_chain=required_fsb_contract_chain
    )

    check_key_contracts_have_not_expired(instrument_code=fsb_code, data=data)


def create_furthest_out_contract_with_roll_parameters_from_contract_date(
    data: dataBlob, instrument_code: str, furthest_out_contract_date: str
):
    diag_contracts = dataContracts(data)
    roll_parameters = diag_contracts.get_roll_parameters(instrument_code)

    furthest_out_contract = contractDateWithRollParameters(
        contractDate(furthest_out_contract_date), roll_parameters
    )

    if diag_contracts.instrument_has_custom_roll(instrument_code):
        furthest_out_contract = furthest_out_contract.next_held_contract()
        # furthest_out_contract = furthest_out_contract.next_held_contract()

    return furthest_out_contract


def create_contract_date_chain(
    furthest_out_contract: contractDateWithRollParameters, use_priced=True
) -> list:
    # To give us wiggle room, and ensure we start collecting the new forward a
    # little in advance
    final_contract = furthest_out_contract.next_priced_contract()

    ## this will pick up contracts from 6 months ago, to deal with any gaps
    ## however if these have expired they are marked as close sampling later
    contract_date_chain = final_contract.get_contracts_from_recently_to_contract_date(
        use_priced=use_priced
    )

    return contract_date_chain


def update_expiry_and_sampling_status_for_contract(
    contract_object: futuresContract,
    data: dataBlob,
    contract_chain: listOfFuturesContracts,
):
    """
    1) Get an expiry from IB, check if same as database, otherwise update the database
    2) If we can't get an expiry from IB, or the contract has expired, or it's missing from the contract chain
         then mark the contract as not sampling


    """
    OK_TO_SAMPLE = "okay to sample"
    unsample_reason = OK_TO_SAMPLE

    log_attrs = {**contract_object.log_attributes(), "method": "temp"}
    data_contracts = dataContracts(data)

    db_contract = data_contracts.get_contract_from_db(contract_object)
    db_expiry_date = db_contract.expiry_date

    try:
        broker_expiry_date = get_contract_expiry_from_broker(contract_object, data=data)
    except missingContract:
        data.log.debug(
            "Can't find expiry for %s, could be a connection problem but could be because contract has already expired"
            % (str(contract_object)),
            **log_attrs,
        )

        ## As probably expired we'll remove it from the sampling list
        unsample_reason = "Contract not available from IB"
    else:
        if broker_expiry_date == db_expiry_date:
            data.log.debug(
                "No change to contract expiry %s to %s"
                % (str(contract_object), str(broker_expiry_date)),
                **log_attrs,
            )
        else:
            existing_expiry_source = contract_object.params.expiry_source
            if existing_expiry_source == "B" and broker_expiry_date.source == "E":
                data.log.debug(
                    f"Not updating expiry for {contract_object.key}, "
                    f"new date is estimated",
                    **log_attrs,
                )
            else:
                # Different!
                update_contract_object_with_new_expiry_date(
                    data=data,
                    broker_expiry_date=broker_expiry_date,
                    contract_object=contract_object,
                )

    ## Now the unsampling, re-read contract as expiry maybe updated
    db_contract = data_contracts.get_contract_from_db(contract_object)

    if db_contract.expired():
        unsample_reason = "has expired"
    elif db_contract not in contract_chain:
        unsample_reason = "not in chain"

    turn_off_sampling = not (unsample_reason == OK_TO_SAMPLE)
    if turn_off_sampling:
        # Mark it as stop sampling in the database
        data_contracts.mark_contract_as_not_sampling(contract_object)
        data.log.debug(
            "Contract %s %s so now stopped sampling"
            % (str(contract_object), unsample_reason),
            **log_attrs,
        )


# testing / debugging only
def _get_all_currently_sampling(fsb_code):
    with dataBlob(log_name="Test-Sampled_Contracts") as data:
        sampling = get_list_of_currently_sampling_contracts_in_db(data, fsb_code)

        fut = get_list_of_currently_sampling_contracts_in_db(data, fsb_code)
        for instr in fut:
            sampling.append(instr)
        print(f"Sampling: {sampling}")

        return sampling


# testing / debugging only
def _mark_as_not_sampling(fsb_code):
    instr_list = _get_all_currently_sampling(fsb_code)
    with dataBlob(log_name="Mark-Not-Sampling") as data:
        data_contracts = dataContracts(data)
        for contract in instr_list:
            data_contracts.mark_contract_as_not_sampling(contract)


# testing / debugging only
def get_contract_expiry_from_db(
    contract: futuresContract, data: dataBlob
) -> expiryDate:
    data_contracts = dataContracts(data)
    db_contract = data_contracts.get_contract_from_db(contract)
    db_expiry_date = db_contract.expiry_date

    return db_expiry_date


if __name__ == "__main__":
    # update_sampled_contracts()
    update_sampled_fsb_contracts(["CADJPY_fsb", "EU-BANKS_fsb", "EURO600_fsb"])
    # get_all_currently_sampling("BUXL_fsb")
    # mark_as_not_sampling("GOLD_fsb")
