from systems.provided.futures_chapter15.basesystem import futures_system
from sysdata.sim.db_futures_sim_data import dbFuturesSimData
from sysdata.config.configdata import Config


def build_system():
    system = futures_system(
        data=dbFuturesSimData(), config=Config("systems.caleb.simplesystemconfig.yaml")
    )
    return system


if __name__ == "__main__":
    build_system()
