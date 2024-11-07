#include "FlySky.h"

PPMReader ppm(FlySky::interruptPin, FlySky::channelAmount);

FlySky::FlySky(int pin1, int pin2, int pin3, int pin4, int pin5, int pin6) {
  ch1_pin = pin1;
  ch2_pin = pin2;
  ch3_pin = pin3;
  ch4_pin = pin4;
  ch5_pin = pin5;
  ch6_pin = pin6;
  automatic = false;
  channel6=false;
  pinMode(ch1_pin, INPUT);
  pinMode(ch2_pin, INPUT);
  pinMode(ch3_pin, INPUT);
  pinMode(ch4_pin, INPUT);
  pinMode(ch5_pin, INPUT);
  pinMode(ch6_pin, INPUT);

}

int FlySky::readChannel(int channelInput, int minLimit, int maxLimit, int defaultValue) {
  int ch = pulseIn(channelInput, HIGH, 30000);
  if (ch < 100) return defaultValue;
  return map(ch, 1007, 1999, minLimit, maxLimit);
}

bool FlySky::readSwitch(byte channelInput, bool defaultValue) {
  int intDefaultValue = (defaultValue) ? 100 : 0;
  int ch = readChannel(channelInput, 0, 100, intDefaultValue);
  return (ch > 50);
}

int FlySky::getChannel1Value(int minLimit, int maxLimit, int defaultValue) {
  return readChannel(ch1_pin, minLimit, maxLimit, defaultValue);
}

int FlySky::getChannel2Value(int minLimit, int maxLimit, int defaultValue) {
  return readChannel(ch2_pin,  minLimit, maxLimit, defaultValue);
}

int FlySky::getChannel3Value(int minLimit, int maxLimit, int defaultValue) {
  return readChannel(ch3_pin, minLimit, maxLimit, defaultValue);
}

int FlySky::getChannel4Value(int minLimit, int maxLimit, int defaultValue) {
  return readChannel(ch4_pin,  minLimit, maxLimit, defaultValue);
}

bool FlySky::getAutomaticFly() {
  return automatic;
}

bool FlySky::getChannel6Value() {
  return readSwitch(ch6_pin,channel6);
}


void FlySky::updateAutomaticFly() {
  automatic = readSwitch(ch5_pin,automatic);
}


void FlySky::readPPM() {

  duration = pulseIn(ch1_pin , HIGH)+400;
  total = total + duration;
  if(duration > 2000){

    /*
    Serial.print(duration);
    Serial.print("\t");
    Serial.println(total);
    */
    total = 0;
    count=0;
  }
  else{
    
    //Serial.print(count);
    
    int chvalue=duration;
    if (chvalue<200){
      chvalue=defaultValueCh;


    }

    else{

      /*
      if  ((count==4)|| (count==5)){
        int specialChannelValue = chvalue ? 1000 : 2000;
        chValues[count]=specialChannelValue;

      }

      else{
        chValues[count]=map(chvalue, 1000, 2000, minLimitCh, maxLimitCh);
      }



    }

    */
    
    durations[count] = duration;
    
    Serial.print(" ch");
    Serial.print(count);
    Serial.print(": ");
    Serial.print(durations[count]);
    Serial.print("\t");
    
    count++;
  }

}

}
int FlySky::getChannelValue(int channel) {
  if (channel >= 1 && channel <= 10) {
    return chValues[channel - 1]; // Devuelve el valor del canal (1-10)
  }
  return 0; // Devuelve 0 si el canal no es válido
}

void FlySky::printChannelValues() {
  for (int i = 0; i < 10; i++) {
    Serial.print(" ch");
    Serial.print(i + 1);
    Serial.print(": ");
    Serial.print(chValues[i]);
  }
  Serial.println();
}
