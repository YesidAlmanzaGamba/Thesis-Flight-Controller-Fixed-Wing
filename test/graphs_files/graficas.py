import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Check the current directory
current_directory = os.getcwd()
print(f"Current Directory: {current_directory}")

# Define the file name
file_name = 'csv_recepcion.csv'

# Iterate through directories to find the correct path
for root, dirs, files in os.walk(current_directory):
    if file_name in files:
        file_path = os.path.join(root, file_name)
        break
else:
    raise FileNotFoundError(f"{file_name} not found in any subdirectory of {current_directory}")

print(f"File found: {file_path}")

# Load the CSV file
data = pd.read_csv(file_path)

# Filter data to be between 300 and 1300 seconds
data_filtered = data[(data['tiempo_enviado'] >= 300) & (data['tiempo_enviado'] <= 1300)]

# Drop rows where all columns are zero
data_cleaned = data_filtered.loc[~(data_filtered == 0).all(axis=1)]

# Remove rows with duplicate 'tiempo_enviado' values
data_cleaned = data_cleaned.drop_duplicates(subset='tiempo_enviado')

# Ensure 'tiempo_enviado' is sorted
data_cleaned = data_cleaned.sort_values(by='tiempo_enviado')

# Interpolate data to have intermediate time values
time_new = np.arange(300, 1300, 0.1)
data_interpolated = pd.DataFrame({'tiempo_enviado': time_new})

# Columns to interpolate
columns_to_interpolate = ['temperatura', 'altitud', 'presion', 'yaw', 'pitch', 'roll', 'latitud', 'longitud']

# Interpolate each column
for col in columns_to_interpolate:
    data_interpolated[col] = np.interp(time_new, data_cleaned['tiempo_enviado'], data_cleaned[col])

# Define colors for the plots
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

# Create subplots for BNO055 orientation data
fig, axs = plt.subplots(4, 1, figsize=(10, 15), constrained_layout=True)


# Roll plot
axs[0].plot(data_interpolated['tiempo_enviado'], data_interpolated['roll'], color=colors[0])
axs[0].set_xlabel('Tiempo (s)')
axs[0].set_ylabel('Roll (°)')
axs[0].set_title('Roll vs Tiempo')
axs[0].grid(True)

# Pitch plot
axs[1].plot(data_interpolated['tiempo_enviado'], data_interpolated['pitch'], color=colors[1])
axs[1].set_xlabel('Tiempo (s)')
axs[1].set_ylabel('Pitch (°)')
axs[1].set_title('Pitch vs Tiempo')
axs[1].grid(True)

# Yaw plot
axs[2].plot(data_interpolated['tiempo_enviado'], data_interpolated['yaw'], color=colors[2])
axs[2].set_xlabel('Tiempo (s)')
axs[2].set_ylabel('Yaw (°)')
axs[2].set_title('Yaw vs Tiempo')
axs[2].grid(True)

# Compass plot
"""
axs[3].plot(data_interpolated['tiempo_enviado'], data_interpolated['compass'], color=colors[3])
axs[3].set_xlabel('Tiempo (s)')
axs[3].set_ylabel('Compass (°)')
axs[3].set_title('Compass vs Tiempo')
axs[3].grid(True)
"""
# Adjust the space between plots
fig.subplots_adjust(hspace=0.3)

# Save and show the BNO055 orientation data plot
plt.savefig(os.path.join(current_directory, 'BNO055_orientacion_recibidas.png'))
plt.show()

# Create subplots for BMP280 sensor data
fig, axs = plt.subplots(3, 1, figsize=(10, 12), constrained_layout=True)
fig.suptitle('BMP280 Datos del Sensor')

# Altitude plot
axs[0].plot(data_interpolated['tiempo_enviado'], data_interpolated['altitud'], color=colors[4])
axs[0].set_xlabel('Tiempo (s)')
axs[0].set_ylabel('Altitud (m)')
axs[0].set_title('Altitud vs Tiempo')
axs[0].grid(True)

# Temperature plot
axs[1].plot(data_interpolated['tiempo_enviado'], data_interpolated['temperatura'], color=colors[5])
axs[1].set_xlabel('Tiempo (s)')
axs[1].set_ylabel('Temperatura (°C)')
axs[1].set_title('Temperatura vs Tiempo')
axs[1].grid(True)

# Pressure plot
axs[2].plot(data_interpolated['tiempo_enviado'], data_interpolated['presion'], color=colors[6])
axs[2].set_xlabel('Tiempo (s)')
axs[2].set_ylabel('Presión (hPa)')
axs[2].set_title('Presión vs Tiempo')
axs[2].grid(True)

# Adjust the space between plots
fig.subplots_adjust(hspace=0.4)

# Save and show the BMP280 sensor data plot
plt.savefig(os.path.join(current_directory, 'BMP280_sensor.png'))
plt.show()

# Create a combined plot for yaw, pitch, and roll vs tiempo
plt.figure(figsize=(10, 7))
plt.plot(data_interpolated['tiempo_enviado'], data_interpolated['yaw'], label='Yaw', color=colors[0])
plt.plot(data_interpolated['tiempo_enviado'], data_interpolated['pitch'], label='Pitch', color=colors[1])
plt.plot(data_interpolated['tiempo_enviado'], data_interpolated['roll'], label='Roll', color=colors[2])
#plt.plot(data_interpolated['tiempo_enviado'], data_interpolated['compass'], label='Compass', color=colors[3])
plt.xlabel('Tiempo (s)')
plt.ylabel('Valores')
plt.title('Yaw, Pitch, Roll, y Compass vs. Tiempo')
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(current_directory, 'yaw_pitch_roll_vs_tiempo_recibidas.png'))
plt.show()

print("Plots have been saved in the current directory.")
