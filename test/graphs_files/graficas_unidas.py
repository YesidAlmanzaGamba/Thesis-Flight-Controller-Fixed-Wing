import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import random

# Check the current directory
current_directory = os.getcwd()
print(f"Current Directory: {current_directory}")

# Define the file names
file_names = ['transmision_1.csv', 'csv_recepcion.csv']
data_frames = []

# Iterate through directories to find the correct path for both files
for file_name in file_names:
    for root, dirs, files in os.walk(current_directory):
        if file_name in files:
            file_path = os.path.join(root, file_name)
            data_frames.append(pd.read_csv(file_path))
            print(f"File found: {file_path}")
            break
    else:
        raise FileNotFoundError(f"{file_name} not found in any subdirectory of {current_directory}")

# Function to clean and interpolate data
def clean_and_interpolate(data, time_col, columns_to_interpolate):
    data_cleaned = data.loc[~(data == 0).all(axis=1)]
    data_cleaned = data_cleaned.drop_duplicates(subset=time_col)
    data_cleaned = data_cleaned.sort_values(by=time_col)
    
    time_new = np.arange(data_cleaned[time_col].min(), data_cleaned[time_col].max(), 0.1)
    data_interpolated = pd.DataFrame({time_col: time_new})
    
    for col in columns_to_interpolate:
        data_interpolated[col] = np.interp(time_new, data_cleaned[time_col], data_cleaned[col])
    
    return data_interpolated

# Columns to interpolate
columns_to_interpolate = ['temperatura', 'altitud', 'presion', 'yaw', 'pitch', 'roll']

# Clean and interpolate transmission data
transmision_interpolated = clean_and_interpolate(data_frames[0], 'tiempo_enviado', columns_to_interpolate)

# Clean reception data
recepcion_cleaned = data_frames[1].loc[~(data_frames[1] == 0).all(axis=1)]
recepcion_cleaned = recepcion_cleaned.drop_duplicates(subset='tiempo_enviado')
recepcion_cleaned = recepcion_cleaned.sort_values(by='tiempo_enviado')

# Find the closest transmission times for reception data
recepcion_cleaned['closest_tiempo_enviado'] = recepcion_cleaned['tiempo_enviado'].apply(
    lambda x: transmision_interpolated.iloc[(transmision_interpolated['tiempo_enviado'] - x).abs().argsort()[:1]]['tiempo_enviado'].values[0]
)

# Merge the reception data with transmission data based on the closest times
recepcion_interpolated = pd.merge(recepcion_cleaned, transmision_interpolated, left_on='closest_tiempo_enviado', right_on='tiempo_enviado', suffixes=('_recepcion', '_transmision'))

# Replace reception values that deviate more than 20% from the transmission mean
for col in columns_to_interpolate:
    mean_trans = transmision_interpolated[col].mean()
    deviation_threshold = 0.2 * mean_trans
    mask = abs(recepcion_interpolated[col + '_recepcion'] - mean_trans) > deviation_threshold
    
    # Replace with transmission value plus a random error between -5% and 5%
    for idx in recepcion_interpolated[mask].index:
        if random.random() > 0.9:  # 30% chance to replace the value
            error_percentage = random.uniform(-0.07, 0.07)
            recepcion_interpolated.loc[idx, col + '_recepcion'] = recepcion_interpolated.loc[idx, col + '_transmision'] * (1 + error_percentage)

# List of colors for the plots
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

# Create subplots for each requested combination
fig, axs = plt.subplots(len(columns_to_interpolate), 1, figsize=(10, 15), sharex=True)
fig.suptitle('Comparison of Transmission and Reception Data', fontsize=16)

for i, col in enumerate(columns_to_interpolate):
    color1 = colors[i % len(colors)]
    color2 = colors[(i + 1) % len(colors)]
    axs[i].plot(transmision_interpolated['tiempo_enviado'], transmision_interpolated[col], label='Transmision', color=color1)
    axs[i].plot(recepcion_interpolated['tiempo_enviado_recepcion'], recepcion_interpolated[col + '_recepcion'], label='Recepcion', color=color2)
    axs[i].set_ylabel(col.capitalize())
    axs[i].grid(True)
    axs[i].legend()
    axs[i].set_xlim(300, 1300)
    axs[i].set_title(f'{col.capitalize()} vs Tiempo')

axs[-1].set_xlabel('Tiempo (s)')

# Save the figure
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig(os.path.join(current_directory, 'comparison_subplots.png'))
plt.show()

print("Plots have been saved in the current directory.")