from syscore.objects import missing_contract, arg_not_supplied

from sysobjects.contract_dates_and_expiries import contractDate, expiryDate
from sysobjects.contracts import futuresContract, listOfFuturesContracts
from sysobjects.instruments import futuresInstrument
from sysobjects.rolls import contractDateWithRollParameters

from sysdata.data_blob import dataBlob
from sysproduction.data.prices import diagPrices
from sysproduction.data.contracts import dataContracts
from sysproduction.data.alt_data_source import altDataSource
from sysdata.barchart.bc_futures_contracts_data import BarchartFuturesContractData


def update_sampled_contracts_barchart():
    """
    Update the active contracts, according to what is available on Barchart for a given instrument

    These are stored in mongoDB

    The active contracts list is used to see what contracts have historical data sampled for

    It does not tell you what the current priced, forward, or carry contract are - that is in multiple prices (DRY)

    However we base the list of theoretical active contracts on the current priced, forward, and carry contracts

    We will end up adding to this list when we roll; this will change the current priced, forward, and carry contract

    When we add a new contract (because one has become available), we get the exact expiry date from BC and save this with the
       contract data.

    We do not sample contracts on the list when they have passed their expiry date

    Contracts are never deleted from the database

    :returns: None
    """
    with dataBlob(log_name="Update-Sampled-Contracts-Barchart", ib_conn=arg_not_supplied) as data:
        update_contracts_object = updateSampledContractsBarchart(data)
        update_contracts_object.update_sampled_contracts()


class updateSampledContractsBarchart(object):
    def __init__(self, data):
        self.data = data

    def update_sampled_contracts(self):
        data = self.data
        update_active_contracts_with_data(data)

def update_active_contracts_with_data(data: dataBlob):
    diag_prices = diagPrices(data)
    list_of_codes_all = diag_prices.get_list_of_instruments_in_multiple_prices()
    for instrument_code in list_of_codes_all:
        update_active_contracts_for_instrument(
            instrument_code, data)


def update_active_contracts_for_instrument(
        instrument_code: str, data: dataBlob):
    # Get the list of contracts we'd want to get prices for, given current
    # roll calendar
    required_contract_chain = get_contract_chain(data, instrument_code)

    # Make sure contract chain and database are aligned
    update_contract_database_with_contract_chain(
        instrument_code, required_contract_chain, data
    )

    # Now to check if expiry dates are resolved
    update_expiries_of_sampled_contracts(instrument_code, data)

    # mark expired as no longer sampling
    stop_expired_contracts_sampling(instrument_code, data)


def get_contract_chain(data: dataBlob, instrument_code: str) -> listOfFuturesContracts:

    furthest_out_contract = get_furthest_out_contract_with_roll_parameters(data, instrument_code)
    contract_object_chain = create_contract_object_chain(furthest_out_contract, instrument_code)

    return contract_object_chain

def get_furthest_out_contract_with_roll_parameters(data: dataBlob,
                                                   instrument_code: str) \
                                                -> contractDateWithRollParameters:

    furthest_out_contract_date = get_furthest_out_contract_date(data, instrument_code)
    furthest_out_contract = create_furthest_out_contract_with_roll_parameters_from_contract_date(data,
                                                                                                 instrument_code,
                                                                                                 furthest_out_contract_date)

    return furthest_out_contract

def get_furthest_out_contract_date(data: dataBlob,
                                   instrument_code: str) -> str:

    diag_prices = diagPrices(data)

    # Get the last contract currently being used
    multiple_prices = diag_prices.get_multiple_prices(instrument_code)
    current_contract_dict = multiple_prices.current_contract_dict()
    furthest_out_contract_date = current_contract_dict.furthest_out_contract_date()

    return furthest_out_contract_date

def create_furthest_out_contract_with_roll_parameters_from_contract_date(data: dataBlob, instrument_code: str,
                                                                         furthest_out_contract_date: str):

    diag_contracts = dataContracts(data)
    roll_parameters = diag_contracts.get_roll_parameters(instrument_code)

    furthest_out_contract = contractDateWithRollParameters(
        contractDate(furthest_out_contract_date), roll_parameters
    )

    return furthest_out_contract

def create_contract_object_chain(furthest_out_contract: contractDateWithRollParameters,
                                  instrument_code: str) -> listOfFuturesContracts:

    contract_date_chain = create_contract_date_chain(furthest_out_contract)
    contract_object_chain = create_contract_object_chain_from_contract_date_chain(instrument_code, contract_date_chain)

    return contract_object_chain

def create_contract_date_chain(furthest_out_contract: contractDateWithRollParameters) ->list:
    # To give us wiggle room, and ensure we start collecting the new forward a
    # little in advance
    final_contract = furthest_out_contract.next_priced_contract()

    ## this will pick up contracts from 6 months ago, to deal with any gaps
    ## however if these have expired they are marked as finished sampling later
    contract_date_chain = (
        final_contract.get_contracts_from_recently_to_contract_date()
    )

    return contract_date_chain

def create_contract_object_chain_from_contract_date_chain(instrument_code: str,
                                                          contract_date_chain: list) \
                                                    -> listOfFuturesContracts:

    # We have a list of contract_date objects, need futureContracts
    # create a 'bare' instrument object
    instrument_object = futuresInstrument(instrument_code)

    contract_object_chain_as_list = [
        futuresContract(instrument_object, contract_date)
        for contract_date in contract_date_chain
    ]

    contract_object_chain = listOfFuturesContracts(
        contract_object_chain_as_list)

    return contract_object_chain

def update_contract_database_with_contract_chain(
    instrument_code: str, required_contract_chain: listOfFuturesContracts, data: dataBlob
):
    """

    :param required_contract_chain: list of contract dates 'yyyymm'
    :param instrument_code: str
    :param data: dataBlob
    :return: None
    """

    currently_sampling_contracts = get_list_of_currently_sampling_contracts_in_db(data, instrument_code)

    list_of_contracts_missing_from_db_or_not_sampling = required_contract_chain.difference(
        currently_sampling_contracts)

    add_missing_contracts_to_database(
         list_of_contracts_missing_from_db_or_not_sampling, data)


def get_list_of_currently_sampling_contracts_in_db(data: dataBlob, instrument_code:str) -> listOfFuturesContracts:
    data_contracts = dataContracts(data)

    currently_sampling_contracts = data_contracts.get_all_sampled_contracts(instrument_code)

    return currently_sampling_contracts

def add_missing_contracts_to_database(
     list_of_contracts_missing_from_db_or_not_sampling: listOfFuturesContracts, data: dataBlob
):
    """

    :param missing_from_db: list of contract_date objects
    :param data: dataBlob
    :return: None
    """

    for contract_to_add in list_of_contracts_missing_from_db_or_not_sampling:
        add_missing_or_not_sampling_contract_to_database(data, contract_to_add)


def add_missing_or_not_sampling_contract_to_database(data: dataBlob, contract_to_add: futuresContract):
    ## A 'missing' contract may be genuinely missing, or just not sampling

    data_contracts = dataContracts(data)

    is_contract_already_in_database = data_contracts.is_contract_in_data(contract_to_add)

    if is_contract_already_in_database:
        mark_existing_contract_as_sampling(contract_to_add, data=data)
    else:
        add_new_contract_with_sampling_on(contract_to_add, data=data)

def mark_existing_contract_as_sampling(contract_to_add:futuresContract, data: dataBlob):
    data_contracts = dataContracts(data)
    data_contracts.mark_contract_as_sampling(contract_to_add)
    log = contract_to_add.specific_log(data.log)

    log.msg(
        "Contract %s now sampling" %
        str(contract_to_add))

def add_new_contract_with_sampling_on(contract_to_add:futuresContract, data: dataBlob):
    data_contracts = dataContracts(data)

    # Mark it as sampling
    contract_to_add.sampling_on()

    # Add it to the database
    # Should not be any duplication to ignore
    data_contracts.add_contract_data(
        contract_to_add, ignore_duplication=False)

    log = contract_to_add.specific_log(data.log)

    log.msg(
        "Contract %s now added to database and sampling" %
        str(contract_to_add))


def update_expiries_of_sampled_contracts(
        instrument_code: str, data: dataBlob):
    """
    # Now to check if expiry dates are resolved
    # For everything in the database which is sampling
    #   - if it hasn't got an IB expiry recorded, then check for the expiry in IB (can fail)
    #    - if expiry found, add expiry to database, and flag in lookup table as found

    :param instrument_code:
    :param data: dataBlob
    :return: None
    """

    diag_contracts = dataContracts(data)

    all_contracts_in_db = diag_contracts.get_all_contract_objects_for_instrument_code(
        instrument_code)
    currently_sampling_contracts = all_contracts_in_db.currently_sampling()

    for contract_object in currently_sampling_contracts:
        update_expiry_for_contract(contract_object, data)



def update_expiry_for_contract(contract_object: futuresContract, data: dataBlob):
    """
    Get an expiry from IB, check if same as database, otherwise update the database

    :param contract_object: contract object
    :param data: dataBlob
    :param log: log
    :return: None
    """
    log = contract_object.specific_log(data.log)

    broker_expiry_date = get_contract_expiry_from_broker(contract_object, data=data)
    db_expiry_date = get_contract_expiry_from_db(contract_object, data = data)

    if broker_expiry_date is missing_contract:
        log.msg(
            "Can't find expiry for %s, could be a connection problem but could be because contract has already expired"
            % (str(contract_object))
        )

        ## don't warn as probably expired we'll remove it from the sampling list

    elif broker_expiry_date == db_expiry_date:
        log.msg(
            "No change to contract expiry %s to %s"
            % (str(contract_object), str(broker_expiry_date))
        )
    else:
        # Different!
        update_contract_object_with_new_expiry_date(data=data,
                                                    broker_expiry_date=broker_expiry_date,
                                                    contract_object=contract_object)


def get_contract_expiry_from_db(contract: futuresContract, data: dataBlob) -> expiryDate:
    data_contracts = dataContracts(data)
    db_contract = data_contracts.get_contract_from_db(contract)
    db_expiry_date = db_contract.expiry_date

    return db_expiry_date

def get_contract_expiry_from_broker(contract:futuresContract, data: dataBlob) -> expiryDate:

    read_data = dataBlob(log_name="Source-Historical-Prices-Barchart",
                         ib_conn=arg_not_supplied,
                         class_list=[BarchartFuturesContractData])



    #data_broker = dataBroker(data)
    data_source = altDataSource(read_data)

    expiry_date = \
        data_source.get_actual_expiry_date_for_single_contract(contract)

    return expiry_date

def update_contract_object_with_new_expiry_date(data: dataBlob,
                                                broker_expiry_date: expiryDate,
                                                contract_object: futuresContract):
    data_contracts = dataContracts(data)
    data_contracts.update_expiry_date(contract_object,
                                      new_expiry_date=broker_expiry_date)

    log = contract_object.specific_log(data.log)

    log.msg(
        "Updated expiry of contract %s to %s"
        % (str(contract_object), str(broker_expiry_date))
    )


def stop_expired_contracts_sampling(instrument_code: str, data: dataBlob):
    ## expiry dates will have been updated and are correct
    currently_sampling_contracts = get_list_of_currently_sampling_contracts_in_db(data, instrument_code)

    for contract in currently_sampling_contracts:
        check_and_stop_expired_contract_sampling(contract = contract, data = data)


def check_and_stop_expired_contract_sampling(contract: futuresContract, data: dataBlob):

    data_contracts = dataContracts(data)
    db_contract = data_contracts.get_contract_from_db(contract)
    contract_expired = db_contract.expired()
    contract_sampling = db_contract.currently_sampling

    if contract_expired and contract_sampling:
        # Mark it as stop sampling in the database

        data_contracts.mark_contract_as_not_sampling(contract)
        log = contract.specific_log(data.log)
        log.msg(
            "Contract %s has expired so now stopped sampling" % str(contract),
            contract_date=contract.date_str,
        )


