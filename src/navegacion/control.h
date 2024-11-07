#ifndef CONTROL_H
#define CONTROL_H

#include <vector>
#include <Arduino.h>




class Control {
public:
    static const int MAX_COORDINATES = 100;
    float VelocidadActual;
    float k_distanciaAuxiliar;
    
    float kp;
    float kd;
    float cte_saturacion;
    float condicionActualizacion;

    int num_waitpoints;
    int index_waitpoint_actual=0;
    float actual_waitpoint_latitude=0;
    float actual_waitpoint_longitude=0;
    float siguiente_waitpoint_latitude=0;
    float siguiente_waitpoint_longitude=0;
    float vector_waitpoint_magnitud=0;
    float vector_waitpoint_angulo=0;
    float vect_x1=0;
    float vect_y1=0;
    float x_proyectado=0;
    float y_proyectado=0;
    float x_intermedio=0;
    float y_intermedio=0;
    float vectorRumboDeseado_x=0;
    float vectorRumboDeseado_y=0;
    float vectorRumboDeseado_magnitud=0;
    float vectorRumboDeseado_angulo=0;
    float ErrorAngular=0;
    float ErrorAngularAnterior=0;
    float VelocidadErrorAngular=0;
    float PorcentajeAleronIzquierdo=0;
    float PorcentajeAleronDerecho=0;
    float AnguloBanqueo=0;


    float ICC_x=0;
    float ICC_y=0;
    float VelocidadAngularActual=0;
    float VelocidadAngularActualAnterior=0;
    float RadioGiro=0;


    float latitudeUAV=0;  
    float longitudeUAV=0;
    float theta=0;
    float waitPoints_rectangulares [Control::MAX_COORDINATES][2];
    float waitPoints [Control::MAX_COORDINATES][2];
    float errorPosicion=0;
    float PendienteWaitPoints=0;
    float IntersectoWaitPoints=0; 

    float yawUAV=0;
    float pitchUAV=0;
    float rollUAV=0;

    float tiempo_actual=0;
    float tiempo_anterior=0;
    
    float dt=0;

    Control(float k_distanciaAuxiliar, float kp, float kd, float cte_saturacion,float condicionActualizacion):

        k_distanciaAuxiliar(k_distanciaAuxiliar),
        kp(kp), 
        kd(kd), 
        cte_saturacion(cte_saturacion),
        condicionActualizacion(condicionActualizacion) {}

    // ... Aquí irían las declaraciones de tus funciones miembro...


//std::vector<std::vector<float>> waitPoints_coordenadas_a_rectangulares(std::vector<std::vector<float>> ListaCoordenadas);

void waitPoints_coordenadas_a_rectangulares(const float inputCoords[MAX_COORDINATES][2], int numCoords);
void Update_Current_Waitpoint(float Waitpoint_finalizated);
void Update_Position(float latitude, float longitude,float theta1);
void Update_Velocidad(float VelocidadActual1);  
void Update_orientation(float yaw, float pitch, float roll);
void Update_tiempo(float time);
void Update_Waitpont_info();
void get_current_waitpoint();
void ImprimirDatos();
void UAV_Search();

int signo(float x);

float darPolarMagnitude(float x, float y);
float darPolarAngle(float x, float y);
float darErrorPosicion(float x1, float y1, float x2, float y2);
float darPendiente_m(float x1, float y1, float x2, float y2);
float darPendiente_b(float x1, float y1, float x2, float y2);
float darCorreccionAngular(float AnguloActual, float AnguloDeseado);
float darDerivada(float ValorActual, float ValorAnterior, float dt);
float darAnguloBanqueo(float PorcentajeAleronIzquierdo, float AnguloBanqueoAnterior, float dt);
float proyectarPunto_x(float x1,float y1, float Pendiente, float intersepto);
float proyectarPunto_y(float x1,float y1, float Pendiente, float intersepto);
float darRectangularMagnitude(float mag, float ang);
float darRectangularAngle(float mag, float ang);
float Degress_to_Radians(float grados);
float Radians_to_Degrees(float radianes);



std::vector<float> darControlAleron(float Error, float DerivadaError, float kp, float kd, float cte_saturacion, float AnguloBanqueo);
std::vector<float> darAngulo_360_180(float anguloLeido);
std::vector<float> darPuntoIntermedio(float PuntoProyectado_x, float PuntoProyectado_y,float angulo, float Pendiente, float interescto, float k_distanciaAuxiliar, float PuntoObjetivo_x, float PuntoObjetivo_y);
std::vector<float> darVelocidadAngular_ICC(float PoseActual_x, float PoseActual_y, float PoseActual_theta,float AnguloBanqueo, float VelocidadActual);

//std::vector<float> darPoseFutura(std::vector<float> PoseActual, float VelocidadActual, float VelocidadAngularActual, std::vector<float> Icc, float dt);
//std::vector<float> darPolar(float x, float y);
//std::vector<float> darRectangular(float mag, float ang);
//std::vector<float> darPendiente(std::vector<float> Punto1, std::vector<float> Punto2);
//std::vector<float> proyectarPunto(std::vector<float> Punto, float Pendiente, float interescto);



};


#endif // Fix: Added a semicolon at the end of the line
