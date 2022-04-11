import logging
from bcutils.bc_utils import get_barchart_downloads, create_bc_session

from sysdata.config.production_config import get_production_config


CONTRACT_MAP = {
    "CORN": {"code": "ZC", "cycle": "HKNUZ", "tick_date": "2008-05-04"},
    "EDOLLAR": {"code": "GE", "cycle": "HMUZ", "tick_date": "2008-05-05", "days_count": 1000},
    "SP500": {"code": "ES", "cycle": "HMUZ", "tick_date": "2008-05-05"},
    "US2": {"code": "ZT", "cycle": "HMUZ", "tick_date": "2008-05-04"},
    "WHEAT": {"code": "ZW", "cycle": "HKNUZ", "tick_date": "2008-05-04"},
}


def do_downloads():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    production_config = get_production_config()
    bc_username = production_config.get_element_or_missing_data("barchart_username")
    bc_password = production_config.get_element_or_missing_data("barchart_password")
    bc_dir = production_config.get_element_or_missing_data("barchart_path")

    bc_config = {
        'barchart_username': bc_username,
        'barchart_password': bc_password
    }

    get_barchart_downloads(
        create_bc_session(config=bc_config),
        contract_map=CONTRACT_MAP,
        save_directory=bc_dir,
        start_year=1980,
        end_year=2024,
        dry_run=False)
