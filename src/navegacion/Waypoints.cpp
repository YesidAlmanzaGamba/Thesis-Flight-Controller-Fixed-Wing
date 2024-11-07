#include "Waypoints.h"
#include <array>

// Constructor para inicializar la matriz de waypoints

void Waypoints::waypoints()
{
}
/*
// Destructor para liberar la memoria
Waypoints::~Waypoints()
{
    delete[] latitudes;
    delete[] longitudes;
    delete[] names;
}

// Método para actualizar la matriz de waypoints

void Waypoints::updateWaypoints(float latitudes[], float longitudes[], String names[], int size)
{
    if (size > this->size)
    {
        // Redimensionar la matriz si es necesario
        delete[] this->latitudes;
        delete[] this->longitudes;
        delete[] this->names;
        this->latitudes = new float[size];
        this->longitudes = new float[size];
        this->names = new String[size];
        this->size = size;
    }

    for (int i = 0; i < size; i++)
    {
        this->latitudes[i] = latitudes[i];
        this->longitudes[i] = longitudes[i];
        this->names[i] = names[i];
    }
}
*/
// Método para imprimir los waypoints almacenados
// 4.613791607210351, -74.07930108839342
double latitudes[] = {4.613791607210351};
double longitudes[] = {-74.07930108839342};
String names[] = {"Sisas"};
int size = 4;
int alturaDeseada = 60;
void Waypoints::printWaypoints()
{
    for (int i = 0; i < size; i++)
    {
        Serial.print("Waypoint ");
        Serial.print(i);
        Serial.print(": ");
        Serial.print("Latitud: ");
        Serial.print(latitudes[i], 6);
        Serial.print(", Longitud: ");
        Serial.print(longitudes[i], 6);
        Serial.print(", Nombre: ");
        Serial.println(names[i]);
    }
}
void Waypoints::updateTarget()
{
    distanceToWaypoint = gps.distanceBetween(latitudeUAV, longitudeUAV, latitudes[currentWaypoint], longitudes[currentWaypoint]);

    if (distanceToWaypoint <= radiusDistance)
    {
        if (currentWaypoint == size - 1)
        {
            currentWaypoint = 0;
        }
        else
            currentWaypoint++;
    }
}
void Waypoints::updateValues(float latitudeUAV, float longitudeUAV, float airSpeed, float altitude, float compass, float alture)
{
    this->latitudeUAV = latitudeUAV;
    this->longitudeUAV = longitudeUAV;
    this->airSpeed = airSpeed;
    this->altitude = altitude;
    this->compass = compass;
    this->alture = alture;
}
float Waypoints::calculateBankAngle()
{
    float angle_to_target = gps.courseTo(latitudeUAV, longitudeUAV, latitudes[currentWaypoint], longitudes[currentWaypoint]);
    //float angle_to_target = gps.courseTo(4.603086020432502, -74.06496610416175, latitudes[currentWaypoint], longitudes[currentWaypoint]);
    float alfa = compass;
    float beta = angle_to_target;
    float turnAngle = 0;
    if (alfa <= beta)
    {

        if (360 - beta + alfa <= beta - alfa)
        {
            turnAngle = -(360 - beta + alfa);
        }
        else
        {
            turnAngle = (beta - alfa);
        }
    }
    else
    {
        if (360 - alfa + beta <= alfa - beta)
        {
            turnAngle = (360 - alfa + beta);
        }
        else
        {
            turnAngle = -(alfa - beta);
        }
    }
    return (turnAngle);
}

float Waypoints::calculateAlture()
{
    return alture - alturaDeseada;
}