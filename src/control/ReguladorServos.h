#ifndef ReguladorServos_h
#define ReguladorServos_h

#include <Arduino.h>

class ReguladorServos
{
public:
  void BeginServos();
  double CalcularPid(double actual, double PosicionDeseada, double priError, double toError, double min, double max, double kp, double ki, double kd, int minMaxPid, bool signo);
  int pulseWidth(int angle);
  void updateChannelsAuto(float rollValue, float pitchValue);
  void updateChannels(float rollValue, float pitchValue);
  void updateChannelsPPM();
  void manualControl();
  void asistidoControl();
  void wayPointControl();

  void managePlaneMode(float rollValue, float pitchValue, float latitudeUAV, float longitudeUAV, float airSpeed, float altitude, float compass, float alture);
  void print_channels();
  int getservo0Value() const { return servo0Value; }
  int getservo1Value() const { return servo1Value; }
  int getservo2Value() const { return servo2Value; }
  int getservo3Value() const { return servo3Value; }
  int getservo4Value() const { return servo4Value; }
  float getPosicionDeseadaYaw() const { return PosicionDeseadaYaw; }
  float getPosicionDeseadaPitch() const { return PosicionDeseadaPitch; }
  float getPosicionDeseadaRoll() const { return PosicionDeseadaRoll; }

private:
  float PosicionDeseadaYaw = 0;
  float PosicionDeseadaPitch = 0;
  float PosicionDeseadaRoll = 0;
  float minMaxRoll = 40;
  float minMaxPitch = 30;
  float minMaxYaw = 60;
  int servo0Value;
  int servo1Value;
  int servo2Value;
  int servo3Value;
  int servo4Value;
  float RollValue;
  float PitchValue;
  float YawValue;

  int chValues[10];
};

#endif