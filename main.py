import numpy as np
import pandas as pd

from functions import functions as fn


def main():
    # path to HDF5 dataset
    file_path = "data/data_GdD_WiSe2526.h5"
    # path to processed data archive
    data_archive_path = "data/data_GdD_plot_data_WiSe2526.h5"

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

        groups_service_loss = []
        groups_power = []

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
            
            # read measurement data for current run
            tank_1_pressure = fn.read_data(file_path, f"{run_path}/tank_1_pressure")
            pump_1_power = fn.read_data(file_path, f"{run_path}/pump_1_power")
            pump_2_power = fn.read_data(file_path, f"{run_path}/pump_2_power")
            time = fn.read_data(file_path,f"{run_path}/time")
            
            # skip run if any required measurement is missing
            if tank_1_pressure is None or pump_1_power is None or pump_2_power is None or time is None:
                continue

            # cap service data using setpoint
            service_fill = fn.cap_service_data(tank_1_pressure, setpoint)

            # check pump power signals for negative values
            if not fn.check_negative_values(pump_1_power) or not fn.check_negative_values(pump_2_power):
                print(f"Warning: negative pump power values in {run_path}")    

            # integrate service fill from analyse start index
            service_fill_slice = service_fill[start_time_index:]
            time_slice = time[start_time_index:]

            service_fill_integral = fn.integral_with_time_step(service_fill_slice, time_slice)

            if service_fill_integral is None:
                continue
            
            # integrate reference signal based on setpoint
            service_target = np.full_like(service_fill_slice, setpoint)
            service_target_integral = fn.integral_with_time_step(service_target, time_slice)
            
            # calculate service loss percentage
            service_loss_percent = fn.calculate_service_loss(
                service_fill_integral,
                service_target_integral,
            )
            
            # integrate pump power signals and convert to Wh
            pump_1_slice = pump_1_power[start_time_index:]
            pump_2_slice = pump_2_power[start_time_index:]

            energy_pump_1 = fn.integral_with_time_step(pump_1_slice, time_slice)
            energy_pump_2 = fn.integral_with_time_step(pump_2_slice, time_slice)

            if energy_pump_1 is None or energy_pump_2 is None:
                continue
            
            total_energy_ws = energy_pump_1 + energy_pump_2
            total_energy_wh = fn.convert_Ws_to_Wh(total_energy_ws)
            
            # store service loss and energy consumption
            groups_service_loss.append(service_loss_percent)
            groups_power.append(total_energy_wh)
    
        # calculate mean and std for service loss and energy
        service_loss_mean, service_loss_std = fn.calculate_mean_and_std(groups_service_loss)
        power_mean, power_std = fn.calculate_mean_and_std(groups_power)

        # store aggregated results in processed_data
        processed_data.loc[group, "service_loss_mean"] = service_loss_mean
        processed_data.loc[group, "service_loss_std"] = service_loss_std
        processed_data.loc[group, "power_mean"] = power_mean
        processed_data.loc[group, "power_std"] = power_std
          
if __name__ == "__main__":
    main()
