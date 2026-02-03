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

        # iterat through runs and read start_time_index
        for run_id in range(1,11):
            run_name = f"run_{run_id:02d}"
            run_path = f"{group}/{run_name}"

            start_time_index = fn.read_metadata(
                file_path,
                run_path,
                "analyse_start_time_index",
            )
            # skip run if start time index is missing
            if start_time_index is None:
                continue

if __name__ == "__main__":
    main()
