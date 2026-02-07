from typing import Any, Dict, List, Optional, Tuple, Union

import h5py as h5
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from numpy.typing import NDArray
from plotid.publish import publish
from plotid.tagplot import tagplot

# Generate HDF5 group names from controller, topology and disruption
def generate_group_name(
    controller: Union[str, List[str]],
    topology: Union[str, List[str]],
    disruption: Union[str, List[str]],
) -> List[str]:

    if isinstance(controller, str):
        controller = [controller]

    if isinstance(topology, str):
        topology = [topology]
    
    if isinstance(disruption, str):
        disruption = [disruption]

    group_names = []

    for c in controller:
        for t in topology:
            for d in disruption:
                group_names.append(c + "_" + t + "_" + d)

    return group_names            

# Read metadata from HDF5 file, return None if not available
def read_metadata(file: str, path: str, attr_key: str) -> Any:
    with h5.File(file, "r") as f:
        # check if path and attribute exist
        if path not in f:
            print(f"Warning: HDF5 path '{path}' not found.")
            return None

        obj = f[path]

        if attr_key not in obj.attrs:
            print(f"Warning: Attribute '{attr_key}' not found at path '{path}'.")
            return None
        
        return obj.attrs[attr_key]        

# Read dataset from HDF5 file, return None if path is invalid
def read_data(file: str, path: str) -> Optional[NDArray]:
    with h5.File(file, "r") as f:
        # check if path exists and points to a dataset
        if path not in f:
            print(f"Warning: dataset '{path}' not found.")
            return None

        obj = f[path]

        if isinstance(obj, h5.Group):
            print(f"Warning: path '{path}' points to a group, not a dataset.")
            return None

        return obj[:]

# Cap service data to range [0, setpoint]
def cap_service_data(service_data: NDArray, setpoint: float) -> NDArray:
    capped_data = []

    for value in service_data:
        if value > setpoint:
            capped_data.append(setpoint)
        elif value < 0:
            capped_data.append(0)
        else:
            capped_data.append(value)

    return np.array(capped_data)           

# Check if array contains only non-negative values
def check_negative_values(array: NDArray) -> bool:
    for value in array:
        if value < 0:
            return False
    return True

# Trapezoidal integral for time series data
def integral_with_time_step(data: NDArray, time_steps: NDArray) -> float:
    if len(data) != len(time_steps):
        print("Warning: data and time_steps must have the same length")
        return None

    integral = 0.0
    for i in range(len(data)-1):
        dt = time_steps[i + 1] - time_steps[i]
        integral += (data[i] + data[i + 1]) / 2 * dt
    
    return float(integral)

# Calculate service loss in percent
def calculate_service_loss(service_fill: float, service_target: float) -> float:
    service_loss = 100 * (1 - service_fill / service_target)
    return service_loss

# Convert energy from watt-seconds to watt-hours
def convert_Ws_to_Wh(energy_in_Ws: float) -> float:
    energy_in_Wh = energy_in_Ws / 3600
    return energy_in_Wh

# Calculate mean and standard deviation of a data list
def calculate_mean_and_std(data: List[float]) -> Tuple[float, float]:
    data_array = np.array(data)

    mean = float(np.mean(data_array))
    std = float(np.std(data_array))

    return mean, std

# Save processed dataframe to HDF5 and store metadata as group attributes
def save_dataframe_in_hdf5_with_metadata(
    df: pd.DataFrame,
    hdf5_path: str,
    group_name: str,
    metadata: Dict[str, Any],
) -> None:
    # save dataframe using pandas
    with pd.HDFStore(hdf5_path, mode = "a") as store:
        store.put(group_name, df, format = "table", data_columns = True)

    # save metadata as HDF5 group attributes
    with h5.File(hdf5_path, "a") as f:
        group = f.require_group(group_name)
        for key, value in metadata.items():
            group.attrs[key] = value

# Read plot data and generate plot formatting information from metadata
def read_plot_data(
    file_path: str, group_path: str
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    df = pd.read_hdf(file_path, key = group_path)

    with h5.File(file_path, "r") as f:
        group = f[group_path]
        metadata = dict(group.attrs.items())

    x_label = metadata["x_label"]
    x_unit = metadata["x_unit"]
    y_label = metadata["y_label"]
    y_unit = metadata["y_unit"]

    plot_format_data = {
        "legend_title": metadata["legend_title"],
        "x_label": f"{x_label} [{x_unit}]",
        "y_label": f"{y_label} [{y_unit}]",
    }
    
    return df, plot_format_data

# Plot power consumption vs service loss with error bars
def plot_service_loss_vs_power(
    processed_data: pd.DataFrame, plot_format_data: Dict[str, str]
) -> Figure:
    fig, ax = plt.subplots()

    for label in processed_data.index:
        label_str = str(label)

        service_loss_mean = processed_data.loc[label, "service_loss_mean"]
        service_loss_std = processed_data.loc[label, "service_loss_std"]
        power_mean = processed_data.loc[label, "power_mean"]
        power_std = processed_data.loc[label, "power_std"]

        ax.errorbar(
            service_loss_mean,
            power_mean,
            xerr = service_loss_std,
            yerr = power_std,
            label = label_str,
            fmt = "o",
            capsize = 3,
        )
    ax.set_xlabel(plot_format_data["x_label"])
    ax.set_ylabel(plot_format_data["y_label"])
    ax.legend(title = plot_format_data["legend_title"])

    # choose reasonable limits based on data
    x_min = float(processed_data["service_loss_mean"].min() - processed_data["service_loss_std"].max())
    x_max = float(processed_data["service_loss_mean"].max() + processed_data["service_loss_std"].max())
    y_min = float(processed_data["power_mean"].min() - processed_data["power_std"].max())
    y_max = float(processed_data["power_mean"].max() + processed_data["power_std"].max())

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    return fig

# Publish plot and relevant source data   
def publish_plot(
    fig: Figure, source_paths: Union[str, List[str]], destination_path: str
) -> None:   
    tagged_fig = tagplot(
        fig,
        "matplotlib",
        id_method = "time",
        prefix = "GdD_WS_2526_2757500_",
    )
    publish(tagged_fig, source_paths, destination_path)