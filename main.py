import numpy as np
import pandas as pd

from functions import functions as fn


def main():
    file_path = "data/data_GdD_WiSe2526.h5"

    controllers = ["ARIMA", "DTW", "PID"]
    topologies = ["Coupled", "Decentral", "Central"]
    disruptions = [
        "BlockageConstant",
        "BlockageCosine",
        "PumpOutage",
        "NoDisruption",
    ]
    
    group_names = fn.generate_group_name(controllers, topologies, disruptions)

    print(group_names[:5])
    print("Total groups:", len(group_names))

if __name__ == "__main__":
    main()
