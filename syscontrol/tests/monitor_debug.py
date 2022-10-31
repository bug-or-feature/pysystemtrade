from jinja2 import Environment, select_autoescape, FileSystemLoader
import datetime
from sysdata.data_blob import dataBlob
from syscore.dateutils import ISO_DATE_FORMAT
from syscontrol.list_running_pids import describe_trading_server_login_data
from syscontrol.monitor import processMonitor


def create_dashboard_file():

    jinja_env = Environment(
        loader=FileSystemLoader("../templates"),
        autoescape=select_autoescape()
    )
    template = jinja_env.get_template("monitor_template.html")

    with dataBlob(log_name="system-monitor") as data:
        data.log.msg("Starting process monitor...")
        process_observatory = processMonitor(data)

        vars = {
            "created_date": str(datetime.datetime.now().strftime(ISO_DATE_FORMAT)),
            "trading_server_description": describe_trading_server_login_data(),
            "dbase_description": str(process_observatory.data.mongo_db),
            "process_info": process_observatory.process_dict_as_df(),
            "log_messages": process_observatory.log_messages
        }

        print(template.render(vars))


if __name__ == "__main__":
    create_dashboard_file()