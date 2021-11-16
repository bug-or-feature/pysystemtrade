from trading_ig import IGService
from sysdata.config.production_config import get_production_config
from syslogdiag.log_to_screen import logtoscreen


class ConnectionIG(object):

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
            pos['account'] = ig_service.ACC_NUMBER
            pos['name'] = positions.iloc[i]['instrumentName']
            pos['size'] = positions.iloc[i]['size']
            pos['dir'] = positions.iloc[i]['direction']
            pos['level'] = positions.iloc[i]['level']
            pos['expiry'] = positions.iloc[i]['expiry']
            pos['epic'] = positions.iloc[i]['epic']
            pos['currency'] = positions.iloc[i]['currency']
            pos['createDate'] = positions.iloc[i]['createdDateUTC']
            pos['dealId'] = positions.iloc[i]['dealId']
            pos['dealReference'] = positions.iloc[i]['dealReference']
            pos['instrumentType'] = positions.iloc[i]['instrumentType']
            result_list.append(pos)

        ig_service.logout()

        return result_list

    def get_activity(self):
        ig_service = self._create_ig_session()
        activities = ig_service.fetch_account_activity_by_period(48 * 60 * 60 * 1000)
        test_epics = ['CS.D.GBPUSD.TODAY.IP', 'IX.D.FTSE.DAILY.IP']
        activities = activities.loc[~activities['epic'].isin(test_epics)]


        result_list = []
        for i in range(0, len(activities)):
            row = activities.iloc[i]
            action = dict()
            action['epic'] = row['epic']
            action['date'] = row['date']
            action['time'] = row['time']
            action['marketName'] = row['marketName']
            action['size'] = row['size']
            action['level'] = row['level']
            action['actionStatus'] = row['actionStatus']
            action['expiry'] = row['period']

            result_list.append(action)

        ig_service.logout()

        return result_list