from sysinit.futures.clone_data_for_instrument import clone_data_for_instrument

# NOTE: this only works if the from:to instruments have the same roll config

# format is 'from': 'to'
mapping_dict = {
    "CHF": "CHF_micro",
    "GBP": "GBP_micro",
    "R1000": "R1000_mini",
}


if __name__ == "__main__":
    write_to_csv = False
    for instrument_from, instrument_to in mapping_dict.items():
        clone_data_for_instrument(
            instrument_from=instrument_from,
            instrument_to=instrument_to,
            write_to_csv=write_to_csv,
            do_prices=True,
            do_multiple=True,
            do_adjusted=True,
            ignore_duplication=False,
        )
