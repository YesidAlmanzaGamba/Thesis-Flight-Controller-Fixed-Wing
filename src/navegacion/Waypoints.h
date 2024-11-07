#ifndef WAYPOINTS_H
#define WAYPOINTS_H

#include <Arduino.h>
#include <TinyGPSPlus.h>

class Waypoints
{
public:
  // Constructor para inicializar la matriz de waypoints
  void waypoints();

  // Destructor para liberar la memoria
  //~Waypoints();

  // Método para actualizar la matriz de waypoints
  // void updateWaypoints(float latitudes[], float longitudes[], String names[], int size);

  // Método para imprimir los waypoints almacenados
  void printWaypoints();
  void updateTarget();
  void updateValues(float latitudeUAV, float longitudeUAV, float airSpeed, float altitude, float compass, float alture);
  float calculateBankAngle();
  float calculateAlture();

  float getBankAngle() const { return bankAngle; }
  TinyGPSPlus gps;

private:
  // Matriz para almacenar las latitudes, longitudes y nombres
  /*
  float* latitudes;
  float* longitudes;
  String* names;

  int size;
  */
  // Tamaño de la matriz de waypoints
  int currentWaypoint = 0;   // Índice del waypoint actual
  float radiusDistance = 20; // Radio de distancia para considerar que se llegó a un waypoint metros
  float latitudeUAV = 0;
  float longitudeUAV = 0;
  float airSpeed = 0;
  float altitude = 0;
  float compass = 0;
  float alture = 0;
  float bankAngle = 0;
  float distanceToWaypoint = 0;

  float altureConst = 60;

  float maxAngleBank = 25;
};

#endif // WAYPOINTS_H
