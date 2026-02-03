import numpy as np
import pandas as pd

from functions import functions as fn


def main():
    # path to HDF5 dataset (not tracked by git)
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

    # groups assigned to matriculation number 2757500
    considered_groups = [
        "ARIMA_Decentral_BlockageCosine",
        "ARIMA_Decentral_NoDisruption",
        "DTW_Decentral_NoDisruption",
        "PID_Decentral_BlockageConstant",
    ]

    processed_data = pd.DataFrame(
        columns=[
            "power_mean",
            "power_std",
            "service_loss_mean",
            "service_loss_std",
        ]
    )
    
    # iterate over all groups and process only assigned ones
    for group in group_names:
        if group not in considered_groups:
            continue
        
        # read setpoint and prepare lists for processed values
        setpoint = fn.read_metadata(file_path, group, "setpoint")

        group_service_loss = []
        group_power = []

if __name__ == "__main__":
    main()
