from sysdata.config.configdata import Config
from sysdata.sim.my_db_futures_sim_data import MyDbFuturesSimData
from systems.provided.futures_chapter15.basesystem import futures_system


def default_futures():
    system = futures_system(
        data=MyDbFuturesSimData(),
        config=Config("systems.futures_spreadbet.default_futures.yaml"),
    )
    return system


if __name__ == "__main__":
    default_futures()
