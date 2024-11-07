#include "ReguladorServos.h"
#include "telemetria/FlySky.h"
#include <Adafruit_PWMServoDriver.h>
#include "navegacion/Waypoints.h"

#define MIN_PULSE_WIDTH 600
#define MAX_PULSE_WIDTH 2600
#define FREQUENCY 60

#define CH1 7
#define CH2 6

#define CH3 5
#define CH4 4
#define CH5 3

#define CH6 2
Waypoints waypoints;

FlySky flySky(CH1, CH2, CH3, CH4, CH5, CH6);
// Adafruit_PWMServoDriver pca9685 = Adafruit_PWMServoDriver(0x40);

int ch1Value = 0;
int ch2Value = 0;
int ch3Value = 0;
int ch4Value = 0;
int ch5Value = 0;
int ch6Value = 0;
int ch7Value = 0;
int ch8Value = 0;
int ch9Value = 0;
int ch10Value = 0;

float toErrorYaw = 0;
float priErrorYaw = 0;
float toErrorPitch = 0;
float priErrorPitch = 0;
float toErrorRoll = 0;
float priErrorRoll = 0;

float kpYaw = 1;
float kdYaw = 0.1;
float kiYaw = 0.01;

float kpPitch = 1;
float kdPitch = 0.1;
float kiPitch = 0.01;

float kpRoll = 3;
float kdRoll = 0.5;
float kiRoll = 0.01;

int min_limit_c1 = 20;
int max_limit_c1 = 140;
int default_value_c1 = 80;

int min_limit_c2 = 30;
int max_limit_c2 = 140;
int default_value_c2 = 85;

int min_limit_c3 = 30;
int max_limit_c3 = 150;
int default_value_c3 = 30;

int min_limit_c4 = 30;
int max_limit_c4 = 150;
int default_value_c4 = 90;

void ReguladorServos::BeginServos()
{
}

double ReguladorServos::CalcularPid(double actual, double PosicionDeseada, double priError, double toError, double min, double max, double kp, double ki, double kd, int minMaxPid, bool signo)
{

  // Funcion que genera el angulo que debe tener los servos para regular la posicion (yaw, pitch, roll) mediante el PID

  double error = PosicionDeseada - actual;
  toError += error;
  double Pvalue = error * kp;
  double Ivalue = toError * ki;
  double Dvalue = (error - priError) * kd;
  double PIDVal = Pvalue + Ivalue + Dvalue;

  priError = error;

  // Limitar el valor de PIDVal dentro del rango de -90 a 90

  if (PIDVal > minMaxPid)
  {
    PIDVal = minMaxPid;
  }
  if (PIDVal < -minMaxPid)
  {
    PIDVal = -minMaxPid;
  }

  double valToreturn = 0;

  // Regulando la orientacion para coincidir con los servos

  if (signo)
  {
    valToreturn = map(PIDVal, -minMaxPid, minMaxPid, min, max);
  }
  else
  {
    valToreturn = map(PIDVal, -minMaxPid, minMaxPid, max, min);
  }

  // Limitar el valor de retorno dentro de los límites del servo (min a max)
  if (valToreturn > max)
  {
    valToreturn = max;
  }
  if (valToreturn < min)
  {
    valToreturn = min;
  }

  return valToreturn;
}

int ReguladorServos::pulseWidth(int angle)
{

  // Funcion a cual convierte un angulo entre 0 y 180 a ancho de pulso (Tipo de dato que leen los servos)

  int pulse_wide, analog_value;
  pulse_wide = map(angle, 0, 180, MIN_PULSE_WIDTH, MAX_PULSE_WIDTH);
  analog_value = int(float(pulse_wide) / 1000000 * FREQUENCY * 4096);
  return analog_value;
}

void ReguladorServos::updateChannelsPPM(){
  /*flySky.readPPM();

  
  ch1Value = flySky.getChannelValue(1);
  ch2Value = flySky.getChannelValue(2);
  ch3Value = flySky.getChannelValue(3);
  ch4Value = flySky.getChannelValue(4);
  ch5Value = flySky.getChannelValue(5);
  ch6Value = flySky.getChannelValue(6);
  ch7Value = flySky.getChannelValue(7);
  ch8Value = flySky.getChannelValue(8);
  ch9Value = flySky.getChannelValue(9);
  ch10Value = flySky.getChannelValue(10);
*/


}


void ReguladorServos::updateChannels(float rollValue, float pitchValue)
{
  ch1Value = flySky.getChannel1Value(min_limit_c1, max_limit_c1, default_value_c1);
  ch2Value = flySky.getChannel2Value(min_limit_c2, max_limit_c2, default_value_c2);
  ch3Value = flySky.getChannel3Value(min_limit_c3, max_limit_c3, default_value_c3);
  ch4Value = flySky.getChannel4Value(min_limit_c4, max_limit_c4, default_value_c4);
  ch5Value = flySky.readSwitch(CH5, false);
  ch6Value = flySky.readSwitch(CH6, false);

  // double pidRoll = CalcularPid(rollValue, ch1Value, priErrorRoll, toErrorRoll, min_limit_c1, max_limit_c1, kpRoll, kiRoll, kdRoll, 60, 1);
  // servo0Value = pulseWidth(pidRoll);

  // double pidPitch = CalcularPid(pitchValue, ch2Value, priErrorPitch, toErrorPitch, min_limit_c2, max_limit_c2, kpPitch, kiPitch, kdPitch, 30, 0);
  // servo1Value = pulseWidth(pidPitch);
  RollValue = rollValue;
  PitchValue = pitchValue;
}
void ReguladorServos::manualControl()
{
  if (ch1Value > default_value_c1 - 2 and ch1Value < default_value_c1 + 2)
  {
    double pidRoll = CalcularPid(RollValue, 0, priErrorRoll, toErrorRoll, min_limit_c1, max_limit_c1, kpRoll, kiRoll, kdRoll, 60, 0);
    servo0Value = pulseWidth(pidRoll);
  }
  else
  {
    servo0Value = pulseWidth(ch1Value);
  }

  if (ch2Value > default_value_c2 - 2 and ch2Value < default_value_c2 + 2)
  {
    double pidPitch = CalcularPid(PitchValue, 0, priErrorPitch, toErrorPitch, min_limit_c2, max_limit_c2, kpPitch, kiPitch, kdPitch, 60, 0);
    servo1Value = pulseWidth(pidPitch);
  }
  else
  {
    servo1Value = pulseWidth(ch2Value);
  }
  servo2Value = pulseWidth(ch3Value);
  servo3Value = pulseWidth(ch4Value);
}

void ReguladorServos::asistidoControl()
{

  float mapedRoll = map(ch1Value, min_limit_c1, max_limit_c1, -minMaxRoll, minMaxRoll);
  double pidRoll = CalcularPid(-RollValue, mapedRoll, priErrorRoll, toErrorRoll, min_limit_c1, max_limit_c1, kpRoll, kiRoll, kdRoll, 60, 1);
  servo0Value = pulseWidth(pidRoll);

  float mapedPitch = map(ch2Value, min_limit_c2, max_limit_c2, -minMaxPitch, minMaxPitch);
  double pidPitch = CalcularPid(PitchValue, mapedPitch, priErrorRoll, toErrorRoll, min_limit_c1, max_limit_c1, kpRoll, kiRoll, kdRoll, 60, 1);
  servo1Value = pulseWidth(pidPitch);
  servo2Value = pulseWidth(ch3Value);
  servo3Value = pulseWidth(ch4Value);
}

void ReguladorServos::wayPointControl()
{
  float mapedRoll = map(waypoints.calculateBankAngle(), -180, 180, -minMaxRoll, minMaxRoll);
  double pidRoll = CalcularPid(-RollValue, mapedRoll, priErrorRoll, toErrorRoll, min_limit_c1, max_limit_c1, kpRoll, kiRoll, kdRoll, 60, 1);
  servo0Value = pulseWidth(pidRoll);

  float mapedPitch = map(waypoints.calculateAlture(), -60, 60, -minMaxPitch, minMaxPitch);
  double pidPitch = CalcularPid(-PitchValue, mapedPitch, priErrorRoll, toErrorRoll, min_limit_c1, max_limit_c1, kpRoll, kiRoll, kdRoll, 60, 1);
  servo1Value = pulseWidth(pidPitch);

  servo2Value = pulseWidth(ch3Value);
}

void ReguladorServos::managePlaneMode(float rollValue, float pitchValue, float latitudeUAV, float longitudeUAV, float airSpeed, float altitude, float compass, float alture)
{

  updateChannels(rollValue, pitchValue);
  // if (ch5Value)
  // Serial.println(ch6Value);

  if (ch5Value)
  {
    if (ch6Value)
    {
      waypoints.updateValues(latitudeUAV, longitudeUAV, airSpeed, altitude, compass, alture);
      wayPointControl();
    }
    else
    {
      asistidoControl();
    }
  }
  else
  {

    manualControl();
  }
}

void ReguladorServos::print_channels()
{
  Serial.println("Valores leidos de los canales:");
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
  Serial.print(ch6Value);
  Serial.print(" | Ch7: ");
  Serial.print(ch7Value);
  Serial.print(" | Ch8: ");
  Serial.print(ch8Value);
  Serial.print(" | Ch9: ");
  Serial.print(ch9Value);
  Serial.print(" | Ch10: ");
  Serial.println(ch10Value);

  Serial.println("Valores PWM enviados");
  Serial.print("s1: ");
  Serial.print(servo0Value);
  Serial.print(" | s2: ");
  Serial.print(servo1Value);
  Serial.print(" | s3: ");
  Serial.print(servo2Value);
  Serial.print(" | s4: ");
  Serial.println(servo3Value);
}