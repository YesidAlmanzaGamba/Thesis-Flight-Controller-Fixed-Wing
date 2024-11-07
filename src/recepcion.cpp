#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <Arduino.h>
#include <Wire.h>
#include "SD.h"
#include "sensorica/Sensors.h"

// Definimos los pines CE y CSN
#define CE_PIN 21
#define CSN_PIN 16
#define MOSI_PIN 35
#define MISO_PIN 37
#define SCK_PIN 36
#define CS_PIN 38

// Definir el pin del buzzer
#define BUZZER_PIN 46

// Variable con la dirección del canal que se va a leer
byte direccion[5] = {'c', 'a', 'n', 'a', 'l'};

// Creamos el objeto radio (NRF24L01)
RF24 radio(CE_PIN, CSN_PIN);

File myFile;

Sensors sensors;

String fileName;

// Vector para los datos recibidos
int fileCounter = 0;
float devicesFound = 0.0;

float latitude = 0.0;
float longitude = 0.0;
float altitude = 0.0;
float airSpeed = 0.0;
float pressure = 0.0;
float yaw = 0.0;
float pitch = 0.0;
float roll = 0.0;
float airPressurePsi = 0.0;
float valorServ0 = 0.0;
float valorServ1 = 0.0;
float valorServ2 = 0.0;
float valorServ3 = 0.0;
float tiempo_envia = 0.0;
float temperature = 0.0;
float rawTemperature = 0.0;
float airPressure = 0.0;
float rawPressure = 0.0;
float rawAltitude = 0.0;
float yawMpu = 0.0;
float pitchMpu = 0.0;
float rollMpu = 0.0;
float compass_value = 0.0;
float Latitud = 0.0;
float Longitud = 0.0;

unsigned long initialTime = 0;
bool firstDataReceived = false;

void createNewFile()
{
  File root = SD.open("/");
  File file = root.openNextFile();

  // Contar el número de archivos en el directorio raíz
  while (file)
  {
    fileCounter++;
    file = root.openNextFile();
  }

  // Si ya hay 10 archivos, borrar todos
  if (fileCounter >= 10)
  {
    for (int i = 0; i <= fileCounter; i++)
    {
      String fileName = "/dataSaved_" + String(i) + ".csv"; // Añadir el slash inicial

      // Verificar la existencia del archivo
      if (SD.exists(fileName))
      {
        Serial.print("Intentando borrar el archivo: ");
        Serial.println(fileName);

        // Convertir el nombre del archivo a char array
        char fileNameArray[fileName.length() + 1];
        fileName.toCharArray(fileNameArray, fileName.length() + 1);

        // Intentar borrar el archivo
        if (SD.remove(fileNameArray))
        {
          Serial.println("Archivo borrado exitosamente.");
        }
        else
        {
          Serial.println("Error al borrar el archivo. Verifica el formato del nombre del archivo.");
        }
      }
      else
      {
        Serial.print("El archivo ");
        Serial.print(fileName);
        Serial.println(" no existe.");
      }
    }
    fileCounter = 0; // Reiniciar el contador después de borrar archivos
  }

  // Crear un nuevo archivo
  fileName = "/dataSaved_" + String(fileCounter + 1) + ".csv";
  myFile = SD.open(fileName, FILE_WRITE);

  if (myFile)
  {
    myFile.println("Tiempo,Latitud,Longitud,Altitud,Velocidad del aire,Presión,Yaw,Pitch,Roll,Presion del aire(PSI),serv0,serv1,serv2,serv3");
    myFile.close();
    Serial.println("File created: " + fileName);
  }
  else
  {
    Serial.println("Error creating file.");
  }
}

void saveData(unsigned long currentTime)
{

  /*
  myFile = SD.open(fileName, FILE_APPEND);
  if (myFile)
  {
    myFile.print(currentTime / 1000);
    myFile.print(",");
    myFile.print(latitude, 6);
    myFile.print(",");
    myFile.print(longitude, 6);
    myFile.print(",");
    myFile.print(altitude, 2);
    myFile.print(",");
    myFile.print(airSpeed, 2);
    myFile.print(",");
    myFile.print(pressure, 2);
    myFile.print(",");
    myFile.print(yaw, 2);
    myFile.print(",");
    myFile.print(pitch, 2);
    myFile.print(",");
    myFile.print(roll, 2);
    myFile.print(",");
    myFile.print(airPressurePsi, 2);
    myFile.print(",");
    myFile.print(valorServ0, 2);
    myFile.print(",");
    myFile.print(valorServ1, 2);
    myFile.print(",");
    myFile.print(valorServ2, 2);
    myFile.print(",");
    myFile.print(valorServ3, 2);
    myFile.print(",");
    myFile.println(tiempo_envia, 5);
    myFile.close();
  }
  else
  {
    Serial.println("Error opening file for writing.");
  }*/
}

void SDBegin()
{
  if (!SD.begin(CS_PIN, SPI))
  {
    Serial.println("Initialization of SD card failed!");
    return;
  }
  Serial.println("SD card is ready to use.");

  createNewFile();
}
/*
void showSensors()
{

  
  Serial.print("{temperatura:");
  Serial.print(temperature);
  Serial.print(", presion:");
  Serial.print(pressure);
  Serial.print(", altitud:");
  Serial.print(altitude);
  Serial.print(", yaw:");
  Serial.print(yaw);
  Serial.print(", pitch:");
  Serial.print(pitch);
  Serial.print(", roll:");
  Serial.print(roll);
  Serial.print(", compass:");
  Serial.print(yaw);
  Serial.print(", velocidad:");
  Serial.print(airSpeed);
  Serial.print(", latitud:");
  Serial.print(latitude, 6);
  Serial.print(", longitud:");
  Serial.print(longitude, 6);
  Serial.print("}");
  Serial.println();
}
*/
void receiveData()
{
  byte buffer[128]; // Ajusta el tamaño según sea necesario
  int index = 0;

  while (radio.available())
  {
    byte fragment[32];
    radio.read(fragment, 32);
    memcpy(buffer + index, fragment, 32);
    index += 32;
    delay(5); // Pequeña pausa entre recepciones
  }

  unsigned long currentTime = millis() - initialTime;

  if (index > 0)
  {
    if (!firstDataReceived)
    {
      initialTime = millis();
      firstDataReceived = true;
    }

    // Deserializar los datos
    index = 0;
    memcpy(&Latitud, &buffer[index], sizeof(float));
    index += sizeof(float);
    memcpy(&Longitud

           ,
           &buffer[index], sizeof(float));
    index += sizeof(float);
    memcpy(&altitude, &buffer[index], sizeof(float));
    index += sizeof(float);
    memcpy(&airSpeed, &buffer[index], sizeof(float));
    index += sizeof(float);
    memcpy(&pressure, &buffer[index], sizeof(float));
    index += sizeof(float);
    memcpy(&yaw, &buffer[index], sizeof(float));
    index += sizeof(float);
    memcpy(&pitch, &buffer[index], sizeof(float));
    index += sizeof(float);
    memcpy(&roll, &buffer[index], sizeof(float));
    index += sizeof(float);
    memcpy(&airPressurePsi, &buffer[index], sizeof(float));
    index += sizeof(float);
    memcpy(&valorServ0, &buffer[index], sizeof(float));
    index += sizeof(float);
    memcpy(&valorServ1, &buffer[index], sizeof(float));
    index += sizeof(float);
    memcpy(&valorServ2, &buffer[index], sizeof(float));
    index += sizeof(float);
    memcpy(&valorServ3, &buffer[index], sizeof(float));
    index += sizeof(float);
    memcpy(&tiempo_envia, &buffer[index], sizeof(float));
    index += sizeof(float);

    // Aquí puedes usar los valores como desees

    
    Serial.print("{tiempoBase: ");
    Serial.print(currentTime/1000);
    Serial.print(", temperature: ");
    Serial.print(0, 2);
    Serial.print(", latitud: ");
    Serial.print(latitude, 6);
    Serial.print(", longitud: ");
    Serial.print(longitude, 6);
    Serial.print(", altitud: ");
    Serial.print(altitude, 2);
    Serial.print(", velocidad: ");
    Serial.print(airSpeed, 2);
    Serial.print(", presion: ");
    Serial.print(pressure, 2);
    Serial.print(", yaw: ");
    Serial.print(yaw, 2);
    Serial.print(", pitch: ");
    Serial.print(pitch, 2);
    Serial.print(", roll: ");
    Serial.print(roll, 2);
    Serial.print(", presionAire: ");
    Serial.print(airPressurePsi, 2);
    Serial.print(", Servo0: ");
    Serial.print(valorServ0, 2);
    Serial.print(", Servo1: ");
    Serial.print(valorServ1, 2);
    Serial.print(", Servo2: ");
    Serial.print(valorServ2, 2);
    Serial.print(", Servo3: ");
    Serial.print(valorServ3, 2);
    Serial.print(", tiempo_enviado: ");
    Serial.print(tiempo_envia, 5);
    Serial.println("}");
  
  }
  else
  {
    // Guardar valores predeterminados si no hay datos
    // Serial.print("Tiempo Recepcion: ");
    // Serial.print(currentTime/1000);
    // Serial.println(" No se recibieron datos. Guardando valores predeterminados.");
  }

  //saveData(currentTime);
}

//======================================== Sonido Mario =======

bool beepCount = true;
#define BUZZER 46
#define NOTE_E7 2637
#define NOTE_C7 2093
#define NOTE_G7 3136
#define NOTE_G6 1568
#define NOTE_E6 1319
#define NOTE_A6 1760
#define NOTE_AS6 1865
#define NOTE_B6 1976
#define NOTE_A7 3520
#define NOTE_F7 2794
#define NOTE_D7 2349

void init_buzzer()
{
  pinMode(BUZZER, OUTPUT);
}
int melody[] = {
    NOTE_E7, NOTE_E7, 0, NOTE_E7,
    0, NOTE_C7, NOTE_E7, 0,
    NOTE_G7, 0, 0, 0,
    NOTE_G6, 0, 0, 0,
    NOTE_C7, 0, 0, NOTE_G6,
    0, 0, NOTE_E6, 0,
    0, NOTE_A6, NOTE_B6, NOTE_AS6,
    NOTE_A6, NOTE_G6, NOTE_E7, NOTE_G7,
    NOTE_A7, NOTE_F7, NOTE_G7, 0,
    NOTE_E7, NOTE_C7, NOTE_D7, NOTE_B6,
    0, 0, NOTE_C7, 0, 0, NOTE_G6,
    0, 0, NOTE_E6, 0, 0, NOTE_A6,
    NOTE_B6, NOTE_AS6, NOTE_A6, NOTE_G6,
    NOTE_E7, NOTE_G7, NOTE_A7, NOTE_F7,
    NOTE_G7, 0, NOTE_E7, NOTE_C7,
    NOTE_D7, NOTE_B6, 0, 0};

int noteDurations[] = {
    12, 12, 12, 12,
    12, 12, 12, 12,
    12, 12, 12, 12,
    12, 12, 12, 12,
    12, 12, 12, 12,
    12, 12, 12, 12,
    12, 12, 12, 12,
    12, 12, 12, 12,
    12, 12, 12, 12,
    12, 12, 12, 12,
    12, 12, 12, 12,
    12, 12, 12, 12,
    12, 12, 12, 12,
    12, 12, 12, 12};

//======================================== Sonido Mario =======

void playBuzzer()
{
  for (int thisNote = 0; thisNote < 16; thisNote++)
  {
    int noteDuration = 1000 / noteDurations[thisNote];
    tone(BUZZER, melody[thisNote], noteDuration);
    int pauseBetweenNotes = noteDuration * 1.30;
    delay(pauseBetweenNotes);
    noTone(BUZZER);
  }
}

void setup()
{
  Serial.begin(115200);
  // Inicializamos los pines del SPI
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN, CSN_PIN);

  SDBegin();

  // Inicializamos el NRF24L01
  radio.begin();

  // Abrimos el canal de lectura
  radio.openReadingPipe(1, direccion);

  // Empezamos a escuchar por el canal
  radio.startListening();

  init_buzzer();
  playBuzzer();
}

void loop()
{
  // Verificamos si hay datos disponibles
  receiveData();
  //showSensors();
}
