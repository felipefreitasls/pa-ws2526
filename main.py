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

    # Groups assigned to matriculation number 2757500
    considered_groups = [
        "ARIMA_Decentral_BlockageCosine",
        "ARIMA_Decentral_NoDisruption",
        "DTW_Decentral_NoDisruption",
        "PID_Decentral_BlockageConstant",
    ]
    
if __name__ == "__main__":
    main()
