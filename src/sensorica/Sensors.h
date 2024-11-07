#ifndef SENSORS_H
#define SENSORS_H

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_BNO055.h>
#include <Adafruit_SSD1306.h>
#include <utility/imumaths.h>
#include <TinyGPSPlus.h>
#include "HMC5883L.h"
#include "ms4525do.h"
#include <thread>
class Sensors
{
public:
    Sensors();
    void begin();
    void readData();
    void updateDisplay();
    void printValues();
    void updateGPS();
    void fileCounterDisplay(float fileCounter);
    float getTemperature() const { return temperature; }
    float getPressure() const { return pressure; }
    float getAltitude() const { return altitude; }
    float getAlture() const { return alture; }
    float getYaw() const { return yaw; }
    float getPitch() const { return pitch; }
    float getRoll() const { return roll; }
    float getCompass() const { return compass_value; }
    float getLatitude() const { return Latitud; }
    float getLongitude() const { return Longitud; }
    float getAirSpeed() const { return airSpeed; }
    float getAirTemperature() const { return airTemperature; }
    float getAirPressure() const { return airPressure; }
    float getAirPressurePsi() const { return airPressurePsi; }
    
    float getSpeedGps() const { return speed_gps; }
    void showSensors();
    void showPressure();
    void displayInfo();

private:
    Adafruit_BMP280 bmp;
    Adafruit_MPU6050 mpu;
    HMC5883L compass;
    Adafruit_SSD1306 display;
    TinyGPSPlus gps;
    bfs::Ms4525do pitot;
    Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x29);
  

    #define SCREEN_WIDTH 128 // OLED display width, in pixels
    #define SCREEN_HEIGHT 64 // OLED display height, in pixels

    //---------BNO055-------------------------

    float roll = 0.0, yaw = 0.0, pitch = 0.0;
    float accel_x = 0.0, accel_y = 0.0, accel_z = 0.0;
    float mag_x = 0.0, mag_y = 0.0, mag_z = 0.0;

    float compass_value;
    unsigned char accelCalibStatus = 0;
    unsigned char magCalibStatus = 0;
    unsigned char gyroCalibStatus = 0;
    unsigned char sysCalibStatus = 0;
    unsigned long lastTime = 0;

    const float alpha1=0.3;
    float roll_offset = 0.0;
    float pitch_offset = 0.0;
    float yaw_offset = 0.0;


    //----------MPU6050----------------------
    float yawMpu, pitchMpu, rollMpu;
    float yaw_raw_mpu;
    float pitch_raw_mpu;
    float roll_raw_mpu;
    float aX, aY, aZ;
    float accelX, accelY, accelZ;
    float gyroX, gyroY, gyroZ;
    float angle_y, bias_y, P_y[2][2];
    float angle_x, bias_x, P_x[2][2];
    float angle_roll, bias_roll, P_roll[2][2];
    
    
    const float Q_angle = 0.001;
    const float Q_bias = 0.003;
    const float R_measure = 0.03;
    long tiempo_prev;

    //----------GPS----------------------
    float Latitud;
    float Longitud;
    const int TX2 = 11;
    const int RX2 = 10;

    char time_gps[9];
    float speed_gps;
    float altitude_gps;

    //----------BMP280----------------------
    float hpaZone = 1028; // hPa Bogotá
    const float alpha = 0.1; // Factor de suavizado
    float initialAltitude;
    float alture;
    float rawTemperature;
    float rawPressure;
    float rawAltitude;

    float temperature;
    float pressure;
    float altitude;

    //------------PITOT-----------------
    float airTemperature;
    float airPressure;
    float airPressurePsi;
    float airSpeed;
    float RHO_AIR;

    void initializeBno();
    void displayOffsets();
    float calculateHeading(float mx, float my);
    float smoothHeading(float newHeading, float oldHeading, float alpha);
    void readBnoData();
    bool isCalibrated();
    void printCalibrationStatus();
    void calculateOffsets();


    void initializeCompass();
    void readBMP280Data();
    void readMPU6050Data();
    void readPitotData();
    void updateRho();
    void updateAirSpeed();
    void PressurePSI();


    void KalmanFilter(float newAngle, float newRate, float *angle, float *bias, float P[2][2]);
    float calculateEMA(float currentReading, float previousEMA, float alpha);
   
    //------------Datalog-------------

};

#endif // SENSORS_H
