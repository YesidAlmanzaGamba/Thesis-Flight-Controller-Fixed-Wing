import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
# Asumiendo que ya has leído tu archivo CSV en un DataFrame llamado df
df = pd.read_csv('datos.csv')
print(df.head())
print(df['yaw1'])
print(df['pitch1'])
print(df['roll1'])

plt.figure(figsize=(10, 6))
plt.subplot(2, 1, 1)
plt.plot(df['time'], df['ax'], label='Raw', color='lightskyblue')
plt.plot(df['time'], df['yaw'], label='Filter', color='blue')

plt.xlabel('Time')
plt.ylabel('Yaw (degrees)')
plt.title('Yaw vs Time (Mpu6050)')
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(df['time'], df['yaw1'], label='Yaw1', color='orange')
plt.xlabel('Time')
plt.ylabel('Yaw (degrees)')
plt.title('Yaw vs Time (BNO055)')
plt.legend()

plt.tight_layout()
plt.show()

# Figura para Pitch
plt.figure(figsize=(10, 6))
plt.subplot(2, 1, 1)

plt.plot(df['time'], df['ay'], label='Raw', color='lightskyblue')
plt.plot(df['time'], df['pitch'], label='Filter', color='blue')
plt.xlabel('Time')
plt.ylabel('Pitch (degrees)')
plt.title('Pitch vs Time (Mpu650)')
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(df['time'], df['pitch1'], label='Pitch1', color='orange')
plt.xlabel('Time')
plt.ylabel('Pitch (degrees)')
plt.title('Pitch vs Time (BNO055)')
plt.legend()

plt.tight_layout()
plt.show()

# Figura para Roll
plt.figure(figsize=(10, 6))
plt.subplot(2, 1, 1)

plt.plot(df['time'], df['az'], label='Raw', color='lightskyblue')
plt.plot(df['time'], df['roll'], label='Filter', color='blue')
plt.xlabel('Time')
plt.ylabel('Roll (degrees)')
plt.title('Roll vs Time')
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(df['time'], df['roll1'], label='Roll1', color='orange')
plt.xlabel('Time')
plt.ylabel('Roll1 (degrees)')
plt.title('Roll1 vs Time')
plt.legend()

plt.tight_layout()
plt.show()

# Figura 3D para Yaw, Pitch, Roll
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')
ax.plot(df['yaw'], df['pitch'], df['roll'], label='Yaw-Pitch-Roll')
ax.set_xlabel('Yaw (degrees)')
ax.set_ylabel('Pitch (degrees)')
ax.set_zlabel('Roll (degrees)')
ax.set_title('3D Trajectory of Yaw, Pitch, Roll')
ax.legend()

plt.show()

# Figura 3D para Yaw1, Pitch1, Roll1
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')
ax.plot(df['yaw1'], df['pitch1'], df['roll1'], label='Yaw1-Pitch1-Roll1', color='r')
ax.set_xlabel('Yaw1 (degrees)')
ax.set_ylabel('Pitch1 (degrees)')
ax.set_zlabel('Roll1 (degrees)')
ax.set_title('3D Trajectory of Yaw1, Pitch1, Roll1')
ax.legend()

plt.show()