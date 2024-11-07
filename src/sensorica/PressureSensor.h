#ifndef PRESSURESENSOR_H
#define PRESSURESENSOR_H

#include <Arduino.h>

class PressureSensor {
public:
  PressureSensor(int pin, float v_s, float sensitivity, float offset);
  void begin();
  float getPressure();
  float getPressurePSI();
  float getVelocity();
  float getFlowRate();
  void printVelocity();
  void printFlowRate();
  void printAdcValue();
  void updateEnvironmentalData(float temp, float pressure);

private:
  void calculateAirDensity();

  int sensorPin;
  float V_S;
  float sensitivity;
  float offset;
  float temperature;
  float pressure_atmospheric;
  float offset_value;
  float RHO_AIR;
  static constexpr int offset_size = 10;
  static constexpr int veloc_mean_size = 10;
  static constexpr float AREA = 0.01; // Área de la sección transversal en metros cuadrados, ajusta según tu aplicación
};

#endif // PRESSURESENSOR_H
