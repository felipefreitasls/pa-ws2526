import numpy as np
import pandas as pd

from functions import functions as fn


def main():
    file _path = "data/data_GdD_WiSe2526.h5"

    controllers = ["ARIMA", "DTW", "PID"]
    topologies = ["Coupled", "Decentral", "Central"]
    disruptions = [
        "BlockageConstant",
        "BlockageCosine",
        "PumpOutage",
        "NoDisruption",
    ]

if __name__ == "__main__":
    main()
