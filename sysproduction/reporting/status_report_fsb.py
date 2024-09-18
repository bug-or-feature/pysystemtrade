from syscore.constants import arg_not_supplied

from sysdata.data_blob import dataBlob

from sysproduction.reporting.api_fsb import ReportingApiFsb


def status_report_fsb(data: dataBlob = arg_not_supplied):
    """
    FSB status report

    :param: data blob
    :return: list of formatted output items
    """
    if data is arg_not_supplied:
        data = dataBlob()

    reporting_api = ReportingApiFsb(data)
    formatted_output = []
    formatted_output.append(reporting_api.terse_header("Status report"))
    list_of_func_names = [
        "table_of_instrument_orders",
        "table_of_delayed_methods",
        "table_of_delayed_prices",
        "table_of_delayed_optimal",
        "table_of_limited_trades",
        "table_of_used_position_limits",
        "table_of_db_overrides",
        "body_text_of_position_locks",
        "table_of_last_price_updates",
        "table_of_last_optimal_position_updates",
        "table_of_trade_limits",
        "table_of_position_limits",
        "table_of_overrides",
        "table_of_process_status_list_for_all_processes",
        "table_of_control_status_list_for_all_processes",
        "table_of_control_data_list_for_all_methods",
        "table_of_control_config_list_for_all_processes",
    ]

    for func_name in list_of_func_names:
        func = getattr(reporting_api, func_name)
        formatted_output.append(func())

    formatted_output.append(reporting_api.footer())

    return formatted_output


if __name__ == "__main__":
    status_report_fsb()
