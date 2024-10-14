from sysinit.futures.clone_data_for_instrument import clone_data_for_instrument


# format is 'from' = 'to'
mapping_dict = dict(
    AUD="AUD_micro",
    # COPPER="COPPER-micro",
    # CRUDE_W="CRUDE_W_micro",
    # EUR="EUR_micro",
    # GAS_US="GAS_US_mini",
    # GOLD="GOLD_micro",
    # HANG="HANG_mini",
    JPY="JPY_mini",
    # KOSPI="KOSPI_mini",
    # NASDAQ="NASDAQ_micro",
    # SOYBEAN="SOYBEAN_mini",
    # SP500="SP500_micro",
    # US30U="US30",
)


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
            ignore_duplication=True,
        )
