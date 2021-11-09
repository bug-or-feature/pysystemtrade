from syscore.objects import arg_not_supplied
from sysbrokers.IG.client.ig_client import IgClient
from sysbrokers.IG.ig_positions import from_ig_positions_to_dict, PositionsFromIG


class IgPositionsClient(IgClient):

    def broker_get_positions(self, account_id: str = arg_not_supplied) -> PositionsFromIG:
        # Get all the positions
        # We return these as a dict of pd DataFrame
        # dict entries are asset classes, columns are IG epic, contract ID,
        # contract expiry

        raw_positions = self.ig_connection.get_positions()
        dict_of_positions = from_ig_positions_to_dict(
            raw_positions, account_id=account_id
        )

        return dict_of_positions
