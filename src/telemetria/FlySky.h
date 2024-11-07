#ifndef FlySky_h
#define FlySky_h

#include <Arduino.h>
#include <PPMReader.h>

class FlySky {
public:
  FlySky(int pin1, int pin2, int pin3, int pin4, int pin5,int pin6);

  int getChannel1Value(int minLimit, int maxLimit, int defaultValue);
  int getChannel2Value(int minLimit, int maxLimit, int defaultValue);
  int getChannel3Value(int minLimit, int maxLimit, int defaultValue);
  int getChannel4Value(int minLimit, int maxLimit, int defaultValue);
  bool getChannel6Value();
  bool getAutomaticFly();
  void updateAutomaticFly();

  int readChannel(int channelInput, int minLimit, int maxLimit, int defaultValue);
  bool readSwitch(byte channelInput, bool defaultValue);

  void readPPM(); // Método para decodificar el protocolo PPM
  int getChannelValue(int channel); // Método para obtener el valor de un canal específico
  static const byte interruptPin = 7; // Define tu pin de interrupción
  static const byte channelAmount = 10; // Define el número de canales

  void printChannelValues();


private:
  int ch1_pin;
  int ch2_pin;
  int ch3_pin;
  int ch4_pin;
  int ch5_pin;
  int ch6_pin;
  bool automatic;
  bool channel6;

  unsigned long duration;
  unsigned long total;
  int count=0;
  unsigned long chValues[10] = {0};
  unsigned long durations[10] = {0};
  int minLimitCh=1000;
  int defaultValueCh=1500;
  int maxLimitCh=2000;





   // Suponiendo que quieres decodificar hasta 10 canales
};

#endif