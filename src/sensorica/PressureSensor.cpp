#include "PressureSensor.h"

PressureSensor::PressureSensor(int pin, float v_s, float sensitivity, float offset)
  : sensorPin(pin), V_S(v_s), sensitivity(sensitivity), offset(offset), temperature(0), pressure_atmospheric(0) {
}

void PressureSensor::begin() {
  int sensor_value_sum = 0;
  for (int ii = 0; ii < offset_size; ii++) {
    sensor_value_sum += analogRead(sensorPin);
    delay(10);
  }
  offset_value = sensor_value_sum / offset_size;
}

float PressureSensor::getPressure() {
  float adc_avg = 0;
  for (int ii = 0; ii < veloc_mean_size; ii++) {
    adc_avg += analogRead(sensorPin);
  }
  adc_avg /= veloc_mean_size;
  //adc_avg = analogRead(sensorPin);

  float adjusted_adc = adc_avg - offset_value;
  float voltage = adjusted_adc * (3.3 / 4095.0);
  float pressure = (((voltage - offset) / V_S) -0.04)*(1 / (0.09));

  if (pressure < 0) {
    pressure = 0;
  }

  return pressure;
}

float PressureSensor::getPressurePSI() {
  float pressure_kPa = getPressure();
  return pressure_kPa * 0.1450377377; // Convertir kPa a PSI
}

float PressureSensor::getVelocity() {
  float pressure = getPressure();
  if (pressure > 0) {
    return sqrt((2 * pressure)/ (RHO_AIR));
  } else {
    return 0;
  }
}

float PressureSensor::getFlowRate() {
  float velocity = getVelocity();
  float flowRate = velocity * AREA * 60; // Convertir a litros por minuto
  return flowRate;
}

void PressureSensor::printVelocity() {
  float velocity = getVelocity();
  float pressure = getPressure();
  Serial.print("Velocidad del aire (m/s): ");
  Serial.print(velocity);
  Serial.print(" Presión (kPa): ");
  Serial.println(pressure);
}

void PressureSensor::printFlowRate() {
  float flowRate = getFlowRate();
  float pressure = getPressurePSI();
  float pressureKpa=getPressure();
  Serial.print("Flujo (L/min): ");
  Serial.print(flowRate,6);
  Serial.print(" Presión (PSI): ");
  Serial.println(pressure,6);
}
void  PressureSensor::printAdcValue() {
    float adc = analogRead(sensorPin);  
    float voltage = adc  * (3.3 / 4095.0);  
    float pressurePsi=getPressurePSI();
    float pressureKpa=getPressure();
    float velocity = getVelocity();
    Serial.print(" ADC value: ");
    Serial.print(adc,6);
    Serial.print(" Voltage: ");
    Serial.print(voltage,6);
    Serial.print(" Pressure Kpa: ");
    Serial.print(pressureKpa,6);

    Serial.print(" Velocidad del aire (m/s): ");
    Serial.print(velocity,6);
    Serial.print(" Air density: ");
    Serial.println(RHO_AIR,6);

}
void PressureSensor::updateEnvironmentalData(float temp, float pressure) {
  temperature = temp;
  pressure_atmospheric = pressure;
  calculateAirDensity();
}

void PressureSensor::calculateAirDensity() {
  float T = temperature + 273.15; // Convertir a Kelvin
  RHO_AIR = (pressure_atmospheric * 100) / (8.31446261815324 *(287.05 * T)); // Convertir presión a Pascales
}