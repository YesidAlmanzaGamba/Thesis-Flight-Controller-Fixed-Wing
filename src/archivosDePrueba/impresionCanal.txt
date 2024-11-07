#include <Arduino.h>
#include <IBusBM.h>

#include <SoftwareSerial.h>
#include <Adafruit_MPU6050.h>
#include <Wire.h>
#include <Servo.h>
#include <HardwareSerial.h>
#include <TinyGPS.h>

#include <TinyGPSPlus.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// Create iBus Object
#include "telemetria/FlySky.h"
#include <Adafruit_PWMServoDriver.h>


#include <Adafruit_BMP280.h>

#include "sensorica/Sensors.h"



//I2C
#define BNO055_SAMPLERATE_DELAY_MS (100)
int devicesFound = 0;
int I2C_frequency =1000;
int I2C_rate =1000; 
int I2C_frequency_max = 1000000;

#define CH1 34
#define CH2 35
#define CH3 32
#define CH4 33
#define CH5 26
#define CH6 25
 
// Configurar receptor
FlySky flySky(CH1, CH2, CH3, CH4, CH6);
Adafruit_PWMServoDriver pca9685 = Adafruit_PWMServoDriver(0x40);

#define SER0_ELEVADORES  4   //Servo Motor 0 on connector 0
#define SER1_ALERONES  5  //Servo Motor 1 on connector 12

#define SER2_MOTOR  6   //Servo Motor 0 on connector 0
#define SER3_TIMON  7


const int servoMin = 150;  // Valor mínimo del pulso PWM para el servo (ajusta según sea necesario)
const int servoMax = 600;  // Valor máximo del pulso PWM para el servo (ajusta según sea necesario)


unsigned int pos0=172; // ancho de pulso en cuentas para pocicion 0°
unsigned int pos180=565; // ancho de pulso en cuentas para la pocicion 180°



int ch1Value = 0;
int ch2Value = 0;
int ch3Value = 0;
int ch4Value = 0;
int ch5Value = 0;
int ch6Value = 0;


int servo0Value = 0;
int servo1Value = 0;
int servo2Value = 0;
int servo3Value = 0;
int servo4Value = 0;


Sensors sensors;

Adafruit_MPU6050 mpu;


#define MPU6050_ADDRESS 0x68 // Dirección I2C del MPU6050


void print_channels(){


  Serial.print("Ch1: ");
  Serial.print(ch1Value);
  Serial.print(" | Ch2: ");
  Serial.print(ch2Value);
  Serial.print(" | Ch3: ");
  Serial.print(ch3Value);
  Serial.print(" | Ch4: ");
  Serial.print(ch4Value);
  Serial.print(" | Ch5: ");
  Serial.print(ch5Value);
  Serial.print(" | Ch6: ");
  Serial.println(ch6Value);


  Serial.print("s1: ");
  Serial.print(servo0Value);
  Serial.print(" | s2: ");
  Serial.print(servo1Value);
  Serial.print(" | s3: ");
  Serial.print(servo2Value);
  Serial.print(" | s4: ");
  Serial.print(servo3Value);
  Serial.println(" | s5: ");


}


void updateChannels(){

    // Obtenção dos valores dos canais dentro da faixa de -100 a 100
  ch1Value = flySky.getChannel1Value();
  ch2Value = flySky.getChannel2Value();
  ch3Value = flySky.getChannel3Value();
  ch4Value = flySky.getChannel4Value();
  ch5Value = flySky.readSwitch(25, false); // Canal 5 es el switch 5
  ch6Value = flySky.readSwitch(25, false);



  servo0Value = map(ch1Value,0,180,pos0, pos180);
  servo1Value = map(ch2Value,0,180,pos0, pos180);
  servo2Value = map(ch3Value,20,160,pos0, pos180);
  servo3Value = map(ch4Value,0,180,pos0, pos180);

}



void setServos(){
  pca9685.setPWM(SER0_ELEVADORES, 0, servo0Value);
  pca9685.setPWM(SER1_ALERONES, 0, servo1Value);
  pca9685.setPWM(SER2_MOTOR, 0, servo2Value);
  pca9685.setPWM(SER3_TIMON, 0, servo3Value);

  Serial.println("Servos");
  delay(100);
  
}

void scanI2C() {
  Serial.println("Scanning I2C Addresses");
  uint8_t cnt = 0;
  
  // Establece la frecuencia del bus I2C a 100 kHz
  Wire.setClock(100000);

  for (uint8_t i = 0; i < 128; i++) {
    Wire.beginTransmission(i);
    uint8_t ec = Wire.endTransmission(true);

    if (ec == 0) {
      if (i < 16) Serial.print('0');
      Serial.print(i, HEX);
      cnt++;
    } else {
      Serial.print("..");
    }
    
    Serial.print(' ');
    if ((i & 0x0F) == 0x0F) Serial.println();
  }

  Serial.print("Scan Completed, ");
  Serial.print(cnt);
  Serial.println(" I2C Devices found.");

  devicesFound = cnt;

  if (devicesFound == 0) {
    Serial.println("No I2C devices found.");
  } else {
    Serial.println("I2C devices found.");
  }
}


void initializeMpu(){


if (!sensors.initialize()) {
    Serial.println("Error al inicializar los sensores.");
    while (1);
  }

  Serial.println("Sensores inicializados correctamente.");


  


}

void showSensors(){

    if (sensors.isBmpWorking()) {
    float temperature = sensors.getTemperature();
    float pressure = sensors.getPressure();
    float altitude = sensors.getAltitude();

    Serial.print("Temperatura BMP: ");
    Serial.print(temperature);
    Serial.print(" °C, Presión BMP: ");
    Serial.print(pressure);
    Serial.print(" Pa, Altitud BMP: ");
    Serial.print(altitude);
    Serial.println(" metros");
  } else {
    Serial.println("Sensor BMP280 no está funcionando.");
  }

  if (sensors.isMpuWorking()) {
    // float yaw, pitch, roll;
    // sensors.getOrientation(yaw, pitch, roll);

    // Serial.print("Orientación MPU - Yaw: ");
    // Serial.print(yaw);
    // Serial.print(" Pitch: ");
    // Serial.print(pitch);
    // Serial.print(" Roll: ");
    // Serial.println(roll);

    // float accelX, accelY, accelZ;
    // sensors.getAcceleration(accelX, accelY, accelZ);

    // Serial.print("Aceleración MPU - X: ");
    // Serial.print(accelX);
    // Serial.print(" m/s^2, Y: ");
    // Serial.print(accelY);
    // Serial.print(" m/s^2, Z: ");
    // Serial.println(accelZ);

    float gyroX, gyroY, gyroZ;
    sensors.getRotation(gyroX, gyroY, gyroZ);
    Serial.println(" ");
    Serial.print("Giro MPU - X: ");
    Serial.print(gyroX);
    Serial.print(" Y: ");
    Serial.print(gyroY);
    Serial.print(" Z: ");
    Serial.println(gyroZ);
  } else {
    Serial.println("Sensor MPU6050 no está funcionando.");
  }
}


bool calibrate=true;

void setup(){

  Serial.begin(115200);
  Wire.begin();
  scanI2C();
  pca9685.begin();
  pca9685.setPWMFreq(60); 

  //Wire.setClock(10000);
  //pca9685.setPWMFreq(1000);


  // if (!sensors.initialize()) {
  //   Serial.println("Error al inicializar los sensores.");
  //   while (1);
  // }

  // Serial.println("Sensores inicializados correctamente.");

  
  //initializeMpu();
    

  




}
 


 
void loop() {
  

  //Enviar a informação dos valores dos canais através da comunicação serial

  updateChannels();
  //print_channels();
  

 




  if (ch5Value == 1){
    Serial.println("Automatico");


  }

  else{
    setServos();


  }

  showSensors();

  // Envía señales PWM a los servos

  //delay(100);




  

}