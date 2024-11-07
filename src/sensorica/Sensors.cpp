#include "Sensors.h"
#include <thread>

Sensors::Sensors()
    : display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire),
      temperature(0), pressure(0), altitude(0), yaw(0), pitch(0), roll(0), compass_value(0), Latitud(0), Longitud(0)
{
}

void Sensors::begin()


{
    /**/
    if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C))
    {
        Serial.println(F("SSD1306 allocation failed"));
        for (;;)
        {
        }
    }

    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 0);
    display.println("UAV Variables");
    display.display();

    

    // Inicialización del BMP280
    if (!bmp.begin(0x76))
    {
        Serial.println(F("BMP280 initialization failed"));
    }
    else
    {
        initialAltitude = bmp.readAltitude(hpaZone);
    }

    // Inicialización del MPU6050

    /*
    if (!mpu.begin(0x68))
    {
        Serial.println(F("MPU6050 initialization failed"));
    }
    */
    initializeBno();

    

    

    // Inicialización del Display




    Serial2.begin(9600, SERIAL_8N1, RX2, TX2);

    // Configuración del Pitot

    /*
    pitot.Config(&Wire, 0x28, 1.0f, -1.0f);
    if (!pitot.Begin())
    {
        Serial.println("Error communicating with pitot");
    }
    */
}
void Sensors:: initializeBno(){
        // Inicialización del BNO055 con dirección 0x29
    if (!bno.begin())
    {
        /* There was a problem detecting the BNO055 ... check your connections */
        Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    }


      // Calibración del BNO055

    /*
    Serial.println("Calibración del BNO055");
    while (!isCalibrated()) {
        printCalibrationStatus();
    }
    Serial.println("BNO055 Calibrado!");

      for (int i = 5; i > 0; i--) {
        display.clearDisplay();
        display.setCursor(0, 0);
        display.print("Colocar UAV");
        
        display.setCursor(0, 30);
        display.print("Tiempo restante: ");
        display.print(i);
        display.print(" segundos");
        display.display();
        delay(1000);
  }
  */

  // Calcular offset de roll, pitch y yaw
  calculateOffsets();
  //displayOffsets();


}
bool Sensors::isCalibrated() {
  uint8_t system, gyro, accel, mag = 0;
  bno.getCalibration(&system, &gyro, &accel, &mag);
  return system == 3 && mag == 3;
}

void Sensors::printCalibrationStatus() {
    uint8_t system, gyro, accel, mag = 0;
    bno.getCalibration(&system, &gyro, &accel, &mag);
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 0);


    display.println("Calibración: ");
    display.print("Sistema: "); display.println(system, DEC);
    display.print(" Gyro: "); display.println(gyro, DEC);
    display.print(" Acel: "); display.println(accel, DEC);
    display.print(" Mag: "); display.println(mag, DEC);

    display.display();
}

void Sensors::calculateOffsets() {
  sensors_event_t event;
  bno.getEvent(&event, Adafruit_BNO055::VECTOR_EULER);
  yaw_offset = event.orientation.x;
  pitch_offset = event.orientation.y;
  roll_offset = event.orientation.z;
}

void Sensors::displayOffsets(){
  display.clearDisplay();
  display.setCursor(0, 0);

  display.print("Offsets:");
  display.setCursor(0, 10);
  display.print("Roll Off: "); display.print(roll_offset);
  display.setCursor(0, 20);
  display.print("Pitch Off: "); display.print(pitch_offset);
  display.setCursor(0, 30);
  display.print("Yaw Off: "); display.print(yaw_offset);

  display.display();
  
  delay(5000);  // Display the offsets for 5 seconds
}


float Sensors::calculateHeading(float mx, float my)
{
    float heading_rad = atan2(my, mx);
    float heading_deg = heading_rad * 180.0 / M_PI;
    if (heading_deg < 0)
    {
        heading_deg += 360;
    }
    return heading_deg;
}

void Sensors::readBnoData()
{
    sensors_event_t event;
    bno.getEvent(&event, Adafruit_BNO055::VECTOR_EULER);
    yaw = event.orientation.x;
    pitch = event.orientation.y-pitch_offset;
    roll = event.orientation.z-roll_offset;

    bno.getEvent(&event, Adafruit_BNO055::VECTOR_ACCELEROMETER);
    accel_x = event.acceleration.x;
    accel_y = event.acceleration.y;
    accel_z = event.acceleration.z;

    bno.getEvent(&event, Adafruit_BNO055::VECTOR_MAGNETOMETER);
    mag_x = event.magnetic.x;
    mag_y = event.magnetic.y;
    mag_z = event.magnetic.z;



    float compass = calculateHeading(mag_x, mag_y);

    compass_value =  smoothHeading(compass, compass_value, alpha1);
  

}

float  Sensors::smoothHeading(float newHeading, float oldHeading, float alpha) {
  float diff = newHeading - oldHeading;

  if (diff > 180) {
    oldHeading += 360;
  } else if (diff < -180) {
    oldHeading -= 360;
  }

  float smoothedHeading = alpha * newHeading + (1 - alpha) * oldHeading;

  if (smoothedHeading >= 360.0) {
    smoothedHeading -= 360.0;
  } else if (smoothedHeading < 0.0) {
    smoothedHeading += 360.0;
  }

  return smoothedHeading;
}


void Sensors::readPitotData()

{
    /*
    if (pitot.Read())
    {
        airPressure = pitot.pres_pa();
        airPressurePsi =airPressure* 0.000145037737797;
        if (airPressure < 0)
        {
            airPressurePsi =0;
            airPressure = 0;
        }
    
        airTemperature = pitot.die_temp_c();
        updateRho();
        updateAirSpeed();
        //PressurePSI();
    }
    */
}
void Sensors::updateRho()
{
    float T = airTemperature + 273.15; // Convertir a Kelvin
    RHO_AIR = (pressure * 100) / ((8.31446261815324) * T);
}

void Sensors::updateAirSpeed()
{
    float pressure = pitot.pres_pa();
    if (pressure > 0)
    {
        airSpeed = sqrt((2 * pressure) / (RHO_AIR));
    }
    else
    {  
        airSpeed = 0;
    }
    
}

void Sensors::PressurePSI()
{
    airPressurePsi = airPressure * 0.1450377377; // Convertir kPa a PSI
}
void Sensors::showPressure()
{

    Serial.print(" Pressure Pa: ");
    Serial.print(airPressure, 6);
    Serial.print(" Pressure pSI: ");
    Serial.print(airPressurePsi, 6);

    Serial.print(" Velocidad del aire (m/s): ");
    Serial.print(airSpeed, 6);
    Serial.print(" Air density: ");
    Serial.print(RHO_AIR, 6);
    Serial.print(" Air Temperature: ");
    Serial.println(airTemperature);
}

void Sensors::readBMP280Data()
{
    float currentTemperature = bmp.readTemperature();
    float currentPressure = bmp.readPressure() / 100.0F;
    float currentAltitude = bmp.readAltitude(hpaZone);

    temperature = calculateEMA(currentTemperature, temperature, alpha);
    pressure = calculateEMA(currentPressure, pressure, alpha);
    altitude = calculateEMA(currentAltitude, altitude, alpha);

    rawTemperature = currentTemperature;
    rawPressure = currentPressure;
    rawAltitude = currentAltitude;
    alture = altitude - initialAltitude;
}

void Sensors::readMPU6050Data()
{   
    /*
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    aX = a.acceleration.x;
    aY = a.acceleration.y;
    aZ = a.acceleration.z;
    accelX = aX * 9.81;
    accelY = aY * 9.81;
    accelZ = aZ * 9.81;

    gyroX = g.gyro.x;
    gyroY = g.gyro.y;
    gyroZ = g.gyro.z;

    float angleAccelZ = atan2(aY, aZ) * 180 / PI;
    yaw_raw_mpu = angleAccelZ;
    KalmanFilter(angleAccelZ, gyroZ, &angle_y, &bias_y, P_y);
    yawMpu = angle_y;

    float angleAccelY = atan2(-aX, sqrt(aY * aY + aZ * aZ)) * 180 / PI;
    pitch_raw_mpu = angleAccelZ;
    KalmanFilter(angleAccelY, gyroY, &angle_x, &bias_x, P_x);
    pitchMpu = -angle_x;

    float angleAccelX = atan2(aY, aZ) * 180 / PI;
    float rate_roll = gyroX - bias_roll;
    angle_roll += (millis() - tiempo_prev) / 1000.0 * rate_roll;
    P_roll[0][0] += (millis() - tiempo_prev) / 1000.0 * (P_roll[1][1] - P_roll[0][1] - P_roll[1][0] + Q_angle);
    P_roll[0][1] -= (millis() - tiempo_prev) / 1000.0 * P_roll[1][1];
    P_roll[1][0] -= (millis() - tiempo_prev) / 1000.0 * P_roll[1][1];
    P_roll[1][1] += Q_bias * (millis() - tiempo_prev) / 1000.0;

    float y_roll = angleAccelX - angle_roll;
    float S_roll = P_roll[0][0] + R_measure;
    float K_roll[2] = {P_roll[0][0] / S_roll, P_roll[1][0] / S_roll};
    angle_roll += K_roll[0] * y_roll;
    bias_roll += K_roll[1] * y_roll;
    P_roll[0][0] -= K_roll[0] * P_roll[0][0];
    P_roll[0][1] -= K_roll[0] * P_roll[0][1];
    P_roll[1][0] -= K_roll[1] * P_roll[0][0];
    P_roll[1][1] -= K_roll[1] * P_roll[0][1];
    rollMpu = angle_roll;

    tiempo_prev = millis();
    */
}



void Sensors::KalmanFilter(float newAngle, float newRate, float *angle, float *bias, float P[2][2])
{
    float S, K[2], y;
    float dt = (millis() - tiempo_prev) / 1000.0;

    *angle += dt * (newRate - *bias);
    P[0][0] += dt * (dt * P[1][1] - P[0][1] - P[1][0] + Q_angle);
    P[0][1] -= dt * P[1][1];
    P[1][0] -= dt * P[1][1];
    P[1][1] += Q_bias * dt;

    y = newAngle - *angle;
    S = P[0][0] + R_measure;
    K[0] = P[0][0] / S;
    K[1] = P[1][0] / S;

    *angle += K[0] * y;
    *bias += K[1] * y;
    P[0][0] -= K[0] * P[0][0];
    P[0][1] -= K[0] * P[0][1];
    P[1][0] -= K[1] * P[0][0];
    P[1][1] -= K[1] * P[0][1];
}

void Sensors::updateGPS()
{
    
    //float angle=gps.courseTo(4.67086033306706145, -74.06116161374081,4.706739812511032,-74.15178166325258);
    //Serial.print("Angle: ");
    //Serial.println(angle);
    while (Serial2.available() > 0)
    {
        if (gps.encode(Serial2.read()))
        {
            if (gps.location.isValid())
            {
                Latitud = gps.location.lat();
                Longitud = gps.location.lng();

            }
            else
            {
                Latitud = 0;
                Longitud = 0;
            }
        }
    }
}

float Sensors::calculateEMA(float currentReading, float previousEMA, float alpha)
{
    return (alpha * currentReading) + ((1 - alpha) * previousEMA);
}


void Sensors::fileCounterDisplay(float fileCounter){

    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 0);
    display.print("Num archivos: ");
    display.print(fileCounter);
    display.display();
}
void Sensors::updateDisplay()
{
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 0);
    display.print("Compas: ");
    display.print(compass_value);
    display.println(" °");
    display.print("Yaw: ");
    display.print(yaw);
    display.println();
    display.print("Pitch: ");
    display.print(pitch);
    display.println();
    display.print("Roll: ");
    display.print(roll);
    display.println();
    display.print("Temp: ");
    display.print(temperature);
    display.println(" C");
    display.print("Alt: ");
    display.print(altitude);
    display.println(" m");
    display.print("Lat: ");
    display.print(Latitud, 6);
    display.println();
    display.print("Long: ");
    display.print(Longitud, 6);
    display.print("Long: ");
    display.print(Longitud, 6);
    display.println();
    display.display();
}

void Sensors::printValues()
{
    Serial.print("Temperatura (C): ");
    Serial.println(temperature);
    Serial.print("Presión (hPa): ");
    Serial.println(pressure);
    Serial.print("Altitud (mSA) ");
    Serial.println(altitude);

    Serial.print("Acelerómetro (X, Y, Z): ");
    Serial.print(aX);
    Serial.print(", ");
    Serial.print(aY);
    Serial.print(", ");
    Serial.println(aZ);
    Serial.print("Yaw: ");
    Serial.print(yaw);
    Serial.print(", Pitch: ");
    Serial.print(pitch);
    Serial.print(", Roll: ");
    Serial.println(roll);

    Serial.print(F("Orientation (Yaw, Pitch, Roll): "));
    Serial.print(yaw);
    Serial.print(F(", "));
    Serial.print(pitch);
    Serial.print(F(", "));
    Serial.println(roll);

    Serial.print("GPS (Lat, Long): ");
    Serial.print(Latitud, 6);
    Serial.print(", ");
    Serial.println(Longitud, 6);
}

void Sensors::displayInfo()
{
    if (gps.location.isValid())
    {
        Latitud = gps.location.lat();
        Longitud = gps.location.lng();
        Serial.print(", ");
        Serial.print(Latitud, 6);
        Serial.print(", ");
        Serial.println(Longitud, 6);
    }
    else
    {
        Latitud = 0;
        Longitud = 0;
        Serial.print(", ");
        Serial.print(Latitud, 6);
        Serial.print(", ");
        Serial.println(Longitud, 6);
    }
}

void Sensors::showSensors()
{
    Serial.print("{temperatura:");
    Serial.print(temperature);
    Serial.print(", rawTemperatura:");
    Serial.print(rawTemperature);
    Serial.print(", presion:");
    Serial.print(airPressure);
    Serial.print(", rawPresion:");
    Serial.print(rawPressure);
    Serial.print(", altitud:");
    Serial.print(altitude);
    Serial.print(", rawAltitud:");
    Serial.print(rawAltitude);
    Serial.print(", yaw1:");
    Serial.print(yawMpu);
    Serial.print(", pitch1:");
    Serial.print(pitchMpu);
    Serial.print(", roll1:");
    Serial.print(rollMpu);
    Serial.print(", yaw:");
    Serial.print(yaw);
    Serial.print(", pitch:");
    Serial.print(pitch);
    Serial.print(", roll:");
    Serial.print(roll);
    Serial.print(", compass:");
    Serial.print(compass_value);
    Serial.print(", velocidad:");
    Serial.print(airSpeed);
    Serial.print(", latitud:");
    Serial.print(Latitud, 6);
    Serial.print(", longitud:");
    Serial.print(Longitud, 6);
    Serial.print("}");
    Serial.println();
}
void Sensors::readData()
{
    readBnoData();
    readBMP280Data();
    readMPU6050Data();
    readPitotData();

    updateGPS();


    /*
    
    std::thread thread_obj(readBnoData());
    std::thread thread_obj(readBMP280Data());
    std::thread thread_obj(readMPU6050Data());
    std::thread thread_obj(readPitotData());
    std::thread thread_obj(updateGPS());

    */
}