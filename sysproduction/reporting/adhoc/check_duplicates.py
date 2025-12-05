from sysdata.data_blob import dataBlob
from sysproduction.data.prices import diagPrices
import pandas as pd
import yaml
from itertools import combinations


def build_correlation_matrix(instrument_list=None):
    """
    Build correlation matrix for a list of instruments using percentage returns.

    :param instrument_list: List of instrument codes. If None, uses all instruments with adjusted prices.
    :return: correlation_matrix (pd.DataFrame)
    """
    # Initialize data connection
    data = dataBlob()
    diag_prices = diagPrices(data)

    # Get list of all instruments with adjusted prices if not provided
    if instrument_list is None:
        instrument_list = (
            diag_prices.db_futures_adjusted_prices_data.get_list_of_instruments()
        )
        print(f"Found {len(instrument_list)} instruments with adjusted prices")
    else:
        print(f"Building correlation matrix for {len(instrument_list)} instruments")

    # Calculate percentage returns for all instruments
    returns_dict = {}
    for instrument_code in instrument_list:
        try:
            prices = diag_prices.get_adjusted_prices(instrument_code)
            if len(prices) > 0:
                # Calculate daily returns
                returns = prices.diff()
                # Calculate percentage returns (returns / lagged price)
                perc_returns = returns / prices.shift(1).ffill()
                returns_dict[instrument_code] = perc_returns
        except Exception as e:
            print(f"Error processing {instrument_code}: {e}")

    # Combine into DataFrame
    returns_df = pd.DataFrame(returns_dict)
    print(f"Built returns DataFrame with {len(returns_df.columns)} instruments")

    # Calculate correlation matrix
    correlation_matrix = returns_df.corr()

    return correlation_matrix


def filter_instruments_with_data(instrument_list):
    """
    Filter instruments to only those with adjusted price data.

    :param instrument_list: List of instrument codes to check
    :return: List of instruments with data
    """
    data = dataBlob()
    diag_prices = diagPrices(data)

    instruments_with_data = []
    for instrument_code in instrument_list:
        try:
            prices = diag_prices.get_adjusted_prices(instrument_code)
            if len(prices) > 0:
                instruments_with_data.append(instrument_code)
        except Exception:
            pass  # Skip instruments with no data

    return instruments_with_data


def parse_duplicate_config(duplicate_dict):
    """
    Parse duplicate configuration dict into groups of instruments to check.
    Only includes instruments that have data.

    :param duplicate_dict: Dict with top-level 'include' and 'exclude' sections, e.g.:
        {
            'include': {
                'copper': 'COPPER-micro',
                'jpy': 'JPY'
            },
            'exclude': {
                'copper': ['COPPER', 'COPPER-mini'],
                'jpy': 'JPY_mini'
            }
        }
    :return: List of tuples (category, instrument_group), each containing category name and instruments
    """
    instrument_groups = []

    include_dict = duplicate_dict.get("include", {})
    exclude_dict = duplicate_dict.get("exclude", {})

    # Get all categories (should be same in both include and exclude)
    all_categories = sorted(set(include_dict.keys()) | set(exclude_dict.keys()))

    for category in all_categories:
        include_instrument = include_dict.get(category)
        exclude_instruments = exclude_dict.get(category)

        if include_instrument is None:
            continue

        # Build group with include + all exclude instruments
        group = [include_instrument]

        # Handle exclude as either string or list
        if exclude_instruments is not None:
            if isinstance(exclude_instruments, list):
                group.extend(exclude_instruments)
            else:
                group.append(exclude_instruments)

        # Filter to only instruments with data
        group_with_data = filter_instruments_with_data(group)

        # Only add groups with at least 2 instruments with data
        if len(group_with_data) >= 2:
            instrument_groups.append((category, tuple(group_with_data)))

    return instrument_groups


def get_correlations_for_duplicate_config(duplicate_dict, threshold=0.95):
    """
    Get correlations for potential duplicate instruments from a config dict.
    Only returns pairs where correlation is below threshold (i.e., NOT true duplicates).

    :param duplicate_dict: Dict with 'include' and 'exclude' keys
    :param threshold: Correlation threshold (default 0.95). Pairs below this are reported as non-duplicates.
    :return: Dictionary of results {category: {(instr1, instr2): correlation_value}}
    """
    # Parse config into instrument groups (returns list of (category, group) tuples)
    instrument_groups_with_categories = parse_duplicate_config(duplicate_dict)

    # Get unique instruments from all groups
    unique_instruments = set()
    for category, group in instrument_groups_with_categories:
        for instrument in group:
            unique_instruments.add(instrument)

    unique_instruments = sorted(list(unique_instruments))

    # Build correlation matrix for just these instruments
    correlation_matrix = build_correlation_matrix(unique_instruments)

    # Extract correlations for all pairs within each group
    results = {}

    for category, group in instrument_groups_with_categories:
        group_results = {}

        # Generate all pairwise combinations within the group
        for instr1, instr2 in combinations(group, 2):
            # All instruments should have data since we filtered them
            corr_value = correlation_matrix.loc[instr1, instr2]

            # Only include pairs where correlation is BELOW threshold (not true duplicates)
            if corr_value < threshold:
                group_results[(instr1, instr2)] = corr_value

        # Only add category if there are non-duplicate pairs to report
        if group_results:
            results[category] = {"instruments": group, "correlations": group_results}

    return results


def load_duplicate_config_from_yaml(yaml_file):
    """
    Load duplicate configuration from a YAML file.

    :param yaml_file: Path to YAML file
    :return: Dict with duplicate configuration
    """
    with open(yaml_file, "r") as f:
        config = yaml.safe_load(f)

    return config.get("duplicate_instruments", {})


def print_results(results: dict, threshold: float = 0.95):
    if not results:
        print(f"\nNo non-duplicate pairs found (all correlations >= {threshold:.2f})!")
        return

    print(f"\nNon-Duplicate Pairs (correlation < {threshold:.2f}):")
    print("=" * 60)

    for category, group_data in results.items():
        instruments = group_data["instruments"]
        correlations = group_data["correlations"]

        print(f"\n{category}: {', '.join(instruments)}")
        print("-" * 60)

        for (instr1, instr2), corr in correlations.items():
            print(f"  {instr1:20s} vs {instr2:20s}: {corr:7.4f}")


def fake_config(threshold: float = 0.95):
    config = {
        "include": {
            "copper": "COPPER-micro",
            "jpy": "JPY",
            "hang": "HANG_mini",
            "coal": "COAL",
            "cocoa": "COCOA",
            "coffee": "COFFEE",
            "cotton": "COTTON",
            "sugar": "SUGAR11",
            "us10": "US10",
            "jgb": "JGB",
            "chinaa": "FTSECHINAA",
            "eurostx": "EUROSTX",
            "gas_us": "GAS_US_mini",
        },
        "exclude": {
            "copper": ["COPPER", "COPPER-mini", "COPPER_LME"],
            "jpy": "JPY_mini",
            "hang": "HANG",
            "coal": "COAL-GEORDIE",
            "cocoa": "COCOA_LDN",
            "coffee": "ROBUSTA",
            "cotton": "COTTON2",
            "sugar": ["SUGAR16", "SUGAR_WHITE"],
            "us10": "US10U",
            "jgb": "JGB-SGX-mini",
            "chinaa": "CHINAA-CON",
            "eurostx": ["EURO600", "EUROSTX-LARGE", "EUROSTX200-LARGE"],
            "gas_us": ["GAS_US", "GAS-LAST", "GAS-PEN"],
        },
    }
    results = get_correlations_for_duplicate_config(config, threshold=threshold)
    print_results(results, threshold=threshold)


def real_config(yaml_file: str, threshold: float = 0.9):
    try:
        duplicate_config = load_duplicate_config_from_yaml(yaml_file)
        results = get_correlations_for_duplicate_config(
            duplicate_config, threshold=threshold
        )

        print_results(results, threshold=threshold)

    except FileNotFoundError:
        print(f"YAML file not found: {yaml_file}")


def get_pairs_from_config(duplicate_dict):
    """
    Extract all instrument pairs from the config.

    :param duplicate_dict: Dict with 'include' and 'exclude' sections
    :return: Set of tuples (instr1, instr2) with instr1 < instr2 alphabetically
    """
    config_pairs = set()

    include_dict = duplicate_dict.get("include", {})
    exclude_dict = duplicate_dict.get("exclude", {})

    for category in include_dict.keys():
        include_instrument = include_dict.get(category)
        exclude_instruments = exclude_dict.get(category)

        if include_instrument is None:
            continue

        # Build group with include + all exclude instruments
        group = [include_instrument]

        # Handle exclude as either string or list
        if exclude_instruments is not None:
            if isinstance(exclude_instruments, list):
                group.extend(exclude_instruments)
            else:
                group.append(exclude_instruments)

        # Add all pairs from this group
        for instr1, instr2 in combinations(group, 2):
            # Store in alphabetical order for consistent comparison
            pair = tuple(sorted([instr1, instr2]))
            config_pairs.add(pair)

    return config_pairs


def find_missing_duplicates(duplicate_dict=None, threshold: float = 0.95):
    """
    Find instrument pairs with high correlation (>= threshold) that are NOT in the config.

    :param duplicate_dict: Dict with 'include' and 'exclude' sections (optional)
    :param threshold: Correlation threshold (default 0.95)
    :return: Dictionary of high-correlation pairs not in config
    """
    # Get all instruments with data
    data = dataBlob()
    diag_prices = diagPrices(data)
    all_instruments = (
        diag_prices.db_futures_adjusted_prices_data.get_list_of_instruments()
    )

    # Filter to instruments with data
    instruments_with_data = filter_instruments_with_data(all_instruments)
    print(
        f"Checking {len(instruments_with_data)} instruments for missing duplicates..."
    )

    # Build correlation matrix for all instruments
    correlation_matrix = build_correlation_matrix(instruments_with_data)

    # Get pairs already in config
    config_pairs = set()
    if duplicate_dict is not None:
        config_pairs = get_pairs_from_config(duplicate_dict)
        print(f"Config contains {len(config_pairs)} known duplicate pairs")

    # Find high-correlation pairs not in config
    missing_duplicates = []

    for instr1, instr2 in combinations(instruments_with_data, 2):
        if (
            instr1 in correlation_matrix.columns
            and instr2 in correlation_matrix.columns
        ):
            corr_value = correlation_matrix.loc[instr1, instr2]

            # Check if correlation is high (potential duplicate)
            if corr_value >= threshold:
                # Store in alphabetical order for comparison
                pair = tuple(sorted([instr1, instr2]))

                # Check if this pair is NOT in the config
                if pair not in config_pairs:
                    missing_duplicates.append((pair, corr_value))

    # Sort by correlation (highest first)
    missing_duplicates.sort(key=lambda x: x[1], reverse=True)

    return missing_duplicates


def print_missing_duplicates(missing_duplicates, threshold: float = 0.95):
    """
    Print report of potential duplicates not in config.

    :param missing_duplicates: List of ((instr1, instr2), corr_value) tuples
    :param threshold: Correlation threshold used
    """
    if not missing_duplicates:
        print(
            f"\nNo missing duplicates found (all high-correlation pairs >= {threshold:.2f} are in config)!"
        )
        return

    print(f"\nPotential Duplicates NOT in Config (correlation >= {threshold:.2f}):")
    print("=" * 60)
    print(f"Found {len(missing_duplicates)} potential duplicate pairs\n")

    for (instr1, instr2), corr in missing_duplicates:
        print(f"  {instr1:20s} vs {instr2:20s}: {corr:7.4f}")


def check_missing_duplicates(yaml_file: str = None, threshold: float = 0.95):
    """
    Check for potential duplicates not in the config.

    :param yaml_file: Path to YAML config file (optional)
    :param threshold: Correlation threshold (default 0.95)
    """
    duplicate_dict = None
    if yaml_file:
        try:
            duplicate_dict = load_duplicate_config_from_yaml(yaml_file)
        except FileNotFoundError:
            print(f"YAML file not found: {yaml_file}")
            return

    missing_duplicates = find_missing_duplicates(duplicate_dict, threshold=threshold)
    print_missing_duplicates(missing_duplicates, threshold=threshold)


def combined_report(yaml_file: str, threshold: float = 0.95):
    """
    Combined report showing both:
    1. Configured duplicates that are NOT actually correlated (< threshold)
    2. Potential duplicates NOT in config (>= threshold)

    :param yaml_file: Path to YAML config file
    :param threshold: Correlation threshold (default 0.95)
    """
    try:
        duplicate_config = load_duplicate_config_from_yaml(yaml_file)
    except FileNotFoundError:
        print(f"YAML file not found: {yaml_file}")
        return

    print("=" * 80)
    print("DUPLICATE INSTRUMENTS CORRELATION REPORT")
    print("=" * 80)
    print(f"Threshold: {threshold:.2f}")
    print()

    # Part 1: Check configured duplicates that are NOT correlated
    print("\n" + "=" * 80)
    print("PART 1: Configured Duplicates That Are NOT Actually Correlated")
    print("=" * 80)
    print("(These pairs are in the config but have low correlation)")

    non_duplicate_results = get_correlations_for_duplicate_config(
        duplicate_config, threshold=threshold
    )

    # Flatten results into simple list format like Part 2
    non_dup_list = []
    for category, group_data in non_duplicate_results.items():
        for (instr1, instr2), corr in group_data["correlations"].items():
            non_dup_list.append(((instr1, instr2), corr))

    if not non_dup_list:
        print(f"\nNo non-duplicate pairs found (all correlations >= {threshold:.2f})!")
    else:
        print(f"\nFound {len(non_dup_list)} configured pairs with low correlation:\n")
        for (instr1, instr2), corr in non_dup_list:
            print(f"  {instr1:20s} vs {instr2:20s}: {corr:7.4f}")

    # Part 2: Check for missing duplicates not in config
    print("\n\n" + "=" * 80)
    print("PART 2: Potential Duplicates NOT in Config")
    print("=" * 80)
    print("(These pairs have high correlation but are not in the config)")

    missing_duplicates = find_missing_duplicates(duplicate_config, threshold=threshold)

    if not missing_duplicates:
        print(
            f"\nNo missing duplicates found (all high-correlation pairs >= {threshold:.2f} are in config)!"
        )
    else:
        print(f"\nFound {len(missing_duplicates)} potential duplicate pairs:\n")
        for (instr1, instr2), corr in missing_duplicates:
            print(f"  {instr1:20s} vs {instr2:20s}: {corr:7.4f}")

    # Summary
    print("\n\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    non_dup_count = len(non_dup_list)
    missing_dup_count = len(missing_duplicates)
    print(f"Configured non-duplicates (need review): {non_dup_count}")
    print(f"Missing duplicates (consider adding): {missing_dup_count}")
    print("=" * 80)


if __name__ == "__main__":
    yaml_file = "/Users/ageach/Dev/work/pst-futures/sysproduction/reporting/adhoc/duplicate_config.yaml"

    # Combined report showing both issues
    combined_report(yaml_file, threshold=0.95)

    # Individual reports (if needed):
    # Check for non-duplicates in config (correlation < threshold)
    # real_config(yaml_file, threshold=0.9)

    # Check for missing duplicates not in config (correlation >= threshold)
    # check_missing_duplicates(yaml_file, threshold=0.90)
