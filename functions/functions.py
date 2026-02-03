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


def read_data(file: str, path: str) -> Optional[NDArray]:
    pass


def cap_service_data(service_data: NDArray, setpoint: float) -> NDArray:
    pass


def check_negative_values(array: NDArray) -> bool:
    pass


def integral_with_time_step(data: NDArray, time_steps: NDArray) -> float:
    pass


def calculate_service_loss(service_fill: float, service_target: float) -> float:
    pass


def convert_Ws_to_Wh(energy_in_Ws: float) -> float:
    pass


def calculate_mean_and_std(data: List[float]) -> Tuple[float, float]:
    pass


def save_dataframe_in_hdf5_with_metadata(
    df: pd.DataFrame,
    hdf5_path: str,
    group_name: str,
    metadata: Dict[str, Any],
) -> None:
    pass


def read_plot_data(
    file_path: str, group_path: str
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    pass


def plot_service_loss_vs_power(
    processed_data: pd.DataFrame, plot_format_data: Dict[str, str]
) -> Figure:
    pass


def publish_plot(
    fig: Figure, source_paths: Union[str, List[str]], destination_path: str
) -> None:
    pass
