from trading_ig import IGService
from sysdata.config.production_config import get_production_config
from syslogdiag.log_to_screen import logtoscreen


class ConnectionIG(object):

    INSTR_CODES = {
        'Bund': 'BUND',
        'Gold': 'GOLD',
        'NZD/USD Forward': 'NZD',
        'US 500': 'SP500',
    }

    def __init__(self, log=logtoscreen("ConnectionIG")):
        production_config = get_production_config()
        self._ig_username = production_config.get_element_or_missing_data('ig_username')
        self._ig_password = production_config.get_element_or_missing_data('ig_password')
        self._ig_api_key = production_config.get_element_or_missing_data('ig_api_key')
        self._ig_acc_type = production_config.get_element_or_missing_data('ig_acc_type')
        self._ig_acc_number = production_config.get_element_or_missing_data('ig_acc_number')

    def _create_ig_session(self):
        ig_service = IGService(
            self._ig_username, self._ig_password, self._ig_api_key, acc_number=self._ig_acc_number
        )
        ig_service.create_session(version='3')
        return ig_service

    @property
    def service(self):
        return

    def get_account_number(self):
        return self._ig_acc_number

    def get_capital(self, account: str):
        ig_service = self._create_ig_session()
        data = ig_service.fetch_accounts()
        data = data.loc[data["accountId"] == account]
        #data = data.loc[data["accountType"] == "SPREADBET"]
        capital = float(data["balance"].loc[1])
        ig_service.logout()

        return capital

    def get_positions(self):
        ig_service = self._create_ig_session()
        positions = ig_service.fetch_open_positions()
        # print_full(positions)
        result_list = []
        for i in range(0, len(positions)):
            pos = dict()
            pos['name'] = positions.iloc[i]['instrumentName']
            try:
                pos['instr'] = self.INSTR_CODES[pos['name']]
            except KeyError:
                continue
            pos['size'] = positions.iloc[i]['size']
            pos['dir'] = positions.iloc[i]['direction']
            pos['level'] = positions.iloc[i]['level']
            pos['expiry'] = positions.iloc[i]['expiry']
            pos['epic'] = positions.iloc[i]['epic']
            result_list.append(pos)

        ig_service.logout()

        return result_list
