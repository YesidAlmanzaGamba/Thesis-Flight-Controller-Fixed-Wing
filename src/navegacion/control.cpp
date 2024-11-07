#include "control.h"
#include <cmath>
#include <iostream>
#include <vector>

float  Control::darPolarMagnitude(float x, float y) {
    return std::hypot(x, y);
}

float  Control::darPolarAngle(float x, float y) {
    return Radians_to_Degrees(std::atan2(y, x));
}

float  Control::darRectangularMagnitude(float mag, float ang) {
    return mag * std::cos(M_PI * ang / 180);
}


float  Control::darRectangularAngle(float mag, float ang) {
    return mag * std::sin(M_PI * ang / 180);
}


float  Control::darErrorPosicion (float x_actual, float y_actual, float x_final, float y_final) {
    float diffX = x_final - x_actual;
    float diffY = y_final - y_actual;
    
    // Llamar a la función darPolar para obtener la magnitud y el ángulo
    return darPolarMagnitude(diffX, diffY);
}

float  Control::darPendiente_m(float x1, float y1, float x2, float y2) {
    float m, b;
    if (x1 - y1 == 0) {
        m = 9999;
    } else {
        m = (y2 - y1) / (y2 - y1);
    }
    return m;
}



float  Control::darPendiente_b(float x1, float y1, float x2, float y2) {
    float m, b;
    m=darPendiente_m(x1, y1, x2, y2);
    b = y2 - m * x2;
    return m;
}

float  Control::proyectarPunto_x(float x1,float y1, float Pendiente, float intersepto) {
    float xi = -(intersepto * Pendiente - Pendiente * y1 - x1) / ((Pendiente * Pendiente) + 1);
    float yi = Pendiente * xi + intersepto;
    return xi;
}

float  Control::proyectarPunto_y(float x1,float y1, float Pendiente, float intersepto) {
    float xi = proyectarPunto_x(x1, y1, Pendiente, intersepto);
    float yi = Pendiente * xi + intersepto;
    return yi;
}

int Control::signo(float x) {
    return (x >= 0) ? 1 : -1;
}
float Control::darCorreccionAngular(float AnguloActual, float AnguloDeseado) {
    float ErrorAngular = AnguloDeseado - AnguloActual;
    if (std::abs(ErrorAngular) < 180) {
        return ErrorAngular;
    } else {
        return ErrorAngular - 360 * signo(ErrorAngular);
    }
}

float Control::darDerivada(float ValorActual, float ValorAnterior, float dt) {
    return (ValorActual - ValorAnterior) / dt;
}
float Control::darAnguloBanqueo(float PorcentajeAleronIzquierdo, float AnguloBanqueoAnterior, float dt) {
    return (-1 * 1.2 * PorcentajeAleronIzquierdo * dt + AnguloBanqueoAnterior);
}

float Control::Degress_to_Radians(float grados){
    return (grados * M_PI) / 180;
}
float Control::Radians_to_Degrees(float radianes){
    return (radianes * 180) / M_PI;
}

std::vector<float> Control::darPuntoIntermedio(float PuntoProyectado_x,float PuntoProyectado_y, float angulo, float Pendiente, float intersepto, float k_distanciaAuxiliar, float PuntoObjetivo_x, float PuntoObjetivo_y) {
    /*
    # Retorna el punto intermedio (P3') en [x,y] sobre la recta definida por la pendiente y el intersecto a una distancia k_distanciaAuxiliar del punto proyectado sobre la recta y que este más cercano a PuntoObjetivo
    # PuntoProyectado (Pi) en [x,y]
    # El ángulo corresponde al angulo de la recta respecto a la horizontal (°)
    # Pendiente como escalar
    # intersecto como escalar
    # k_distanciaAuxiliar
    # PuntoObjetivo como [x,y]
    
    */
    float x1 = PuntoProyectado_x + k_distanciaAuxiliar * std::cos(std::atan(Pendiente));
    float y1 = Pendiente * x1 + intersepto;
    float x2 = PuntoProyectado_x - k_distanciaAuxiliar * std::cos(std::atan(Pendiente));
    float y2 = Pendiente * x2 + intersepto;
    if (std::hypot(PuntoObjetivo_x - x1, PuntoObjetivo_y - y1) < std::hypot(PuntoObjetivo_x - x2, PuntoObjetivo_y - y2)) {
        return {x1, y1};
    } else {
        return {x2, y2};
    }
}  

std::vector<float> Control::darControlAleron(float Error, float DerivadaError, float kp, float kd, float cte_saturacion, float AnguloBanqueo) {
    float controlador;
    if (std::abs(AnguloBanqueo) < 25) {
        controlador = -kp * Error + kd * (DerivadaError);
        if (std::abs(controlador) > 100) {
            controlador = 100 * signo(controlador);
        }
    } else if (std::abs(AnguloBanqueo) < 30) {
        controlador = -kp * Error + kd * (DerivadaError);
        if (std::abs(controlador) > 100) {
            controlador = 100 * signo(controlador);
        }
        float penalizacion = (std::abs(AnguloBanqueo) - 25) / 5;
        controlador = controlador * (1 - penalizacion);
    } else {
        controlador = cte_saturacion * AnguloBanqueo / 100;
    }
    return {controlador, -controlador};
}



std::vector<float> Control::darAngulo_360_180(float anguloLeido) {
    float ang_encontrado_360, ang_encontrado_180;
    if (std::abs(anguloLeido) > 360) {
        float ang_encontrado_360 = std::modf(anguloLeido / 360, &ang_encontrado_360) * 360 * signo(anguloLeido);
        ang_encontrado_180 = (std::abs(ang_encontrado_360) <= 180) ? ang_encontrado_360 : ang_encontrado_360 - 360;
    } else {
        ang_encontrado_360 = anguloLeido;
        if (std::abs(anguloLeido) < 180) {
            ang_encontrado_180 = ang_encontrado_360;
        } else {
            ang_encontrado_180 = ang_encontrado_360 - 360 * signo(ang_encontrado_360);
        }
    }
    return {ang_encontrado_360, ang_encontrado_180};
}

std::vector<float> Control::darVelocidadAngular_ICC(float PoseActual_x, float PoseActual_y, float PoseActual_theta, float AnguloBanqueo, float VelocidadActual) {
    if (AnguloBanqueo == 0) {
        return {0, 0, 0, 0};
    } else {
        float RadioGiro = std::abs((VelocidadActual * VelocidadActual) / (9.81 * std::tan(M_PI * AnguloBanqueo / 180)));
        float VelocidadAngular = (VelocidadActual / RadioGiro) * signo(AnguloBanqueo) * 180 / M_PI;
        float Icc_x = RadioGiro * std::cos(M_PI * PoseActual_theta / 180 + signo(AnguloBanqueo) * M_PI / 2) + PoseActual_x;
        float Icc_y = RadioGiro * std::sin(M_PI * PoseActual_theta  / 180 + signo(AnguloBanqueo) * M_PI / 2) + PoseActual_y;
        return {VelocidadAngular, Icc_x, Icc_y, RadioGiro};
    }
}



void Control::waitPoints_coordenadas_a_rectangulares(const float inputCoords[MAX_COORDINATES][2], int numCoords) {
    float factor = 6371 * 2 * M_PI / 360;  // Factor para convertir grados a "kilómetros lineales"
    num_waitpoints = numCoords;
    // Suponiendo que el primer punto es la referencia para el origen
    float outputCoords[MAX_COORDINATES][2];
    outputCoords[0][0] = 0;
    outputCoords[0][1] = 0;

    for (int i = 0; i < numCoords-1; ++i) {
        float lonDiff = inputCoords[i][1] - inputCoords[0][1];
        float latDiff = inputCoords[i][0] - inputCoords[0][0];
        outputCoords[i][0] = lonDiff * factor * 1000;  // Conversión de longitud a metros
        outputCoords[i][1] = latDiff * factor * 1000;  // Conversión de latitud a metros

        waitPoints_rectangulares[i][0] = outputCoords[i][0];
        waitPoints_rectangulares[i][1] = outputCoords[i][1];

        waitPoints[i][0] = inputCoords[i][0];
        waitPoints[i][1] = inputCoords[i][1];
    }

    // Copy the values from outputCoords to waitPoint
}

void Control::Update_Current_Waitpoint(float Waitpoint_finalizated) {
    index_waitpoint_actual = Waitpoint_finalizated;
}

void Control::Update_Position(float latitude, float longitude, float theta1) {
    /*Actualiza valores de GPS*/
    latitudeUAV = latitude;
    longitudeUAV = longitude;
    theta = theta1;

}

void Control::Update_orientation(float yaw, float pitch, float roll) {
    /*Actualiza valores de orientación*/
    yawUAV = Degress_to_Radians(yaw);
    pitchUAV = Degress_to_Radians(pitch);
    rollUAV = Degress_to_Radians(roll);
}



void Control::Update_Velocidad(float VelocidadActual1) {
    VelocidadActual = VelocidadActual1;
}

void Control::Update_tiempo(float time){
    float time_act=tiempo_actual;
    tiempo_actual=time;
    dt=(tiempo_actual-tiempo_anterior)/1000;
    tiempo_anterior=time_act;


}
void Control::Update_Waitpont_info() {
    /*Actualiza valores de GPS*/
    actual_waitpoint_latitude = waitPoints[index_waitpoint_actual][0];
    actual_waitpoint_longitude = waitPoints[index_waitpoint_actual][1];

    siguiente_waitpoint_latitude = waitPoints[index_waitpoint_actual + 1][0];
    siguiente_waitpoint_longitude = waitPoints[index_waitpoint_actual + 1][1];
    errorPosicion = darErrorPosicion(latitudeUAV, longitudeUAV, siguiente_waitpoint_latitude, siguiente_waitpoint_longitude);

    vect_x1=actual_waitpoint_latitude-siguiente_waitpoint_latitude;
    vect_y1=actual_waitpoint_longitude-siguiente_waitpoint_longitude;

    vector_waitpoint_magnitud=darPolarMagnitude(vect_x1, vect_y1);
    vector_waitpoint_angulo=darPolarAngle(vect_x1, vect_y1);
    PendienteWaitPoints=darPendiente_m(actual_waitpoint_latitude, actual_waitpoint_longitude, siguiente_waitpoint_latitude, siguiente_waitpoint_longitude);
    IntersectoWaitPoints=darPendiente_b(actual_waitpoint_latitude, actual_waitpoint_longitude, siguiente_waitpoint_latitude, siguiente_waitpoint_longitude);
}

void Control::UAV_Search(){
    Update_Waitpont_info();  

    if (errorPosicion>50){
        /* Proyecta la posición actual del UAV en un Punto (relacionado a la diferencia
         del vector de los puntos de espera (waitpoint_actual y waitpoint_siguiente)) 
        */
        x_proyectado=proyectarPunto_x(latitudeUAV, longitudeUAV, PendienteWaitPoints, IntersectoWaitPoints);
        y_proyectado=proyectarPunto_y(latitudeUAV, longitudeUAV, PendienteWaitPoints, IntersectoWaitPoints);
        std::vector<float> puntoIntermedio=darPuntoIntermedio(x_proyectado, y_proyectado, vector_waitpoint_angulo, PendienteWaitPoints, IntersectoWaitPoints, k_distanciaAuxiliar, siguiente_waitpoint_latitude, siguiente_waitpoint_longitude);
        x_intermedio=puntoIntermedio[0];
        y_intermedio=puntoIntermedio[1];
        vectorRumboDeseado_x=x_intermedio-latitudeUAV;
        vectorRumboDeseado_y=y_intermedio-longitudeUAV;

        
        vectorRumboDeseado_magnitud=darPolarMagnitude(vectorRumboDeseado_x, vectorRumboDeseado_y);
        vectorRumboDeseado_angulo=(darPolarAngle(vectorRumboDeseado_x, vectorRumboDeseado_y));
        


        // Control
        ErrorAngular=darCorreccionAngular(theta, vectorRumboDeseado_angulo);
        VelocidadErrorAngular=darDerivada(ErrorAngular, ErrorAngularAnterior, dt);

        //Revisar roll UAV angulo de Banqueo
        std::vector<float> PorcentajeAleron=darControlAleron(ErrorAngular, VelocidadErrorAngular, kp, kd, cte_saturacion, AnguloBanqueo);
        PorcentajeAleronIzquierdo=PorcentajeAleron[0];
        PorcentajeAleronDerecho=PorcentajeAleron[1];

        errorPosicion = darErrorPosicion(latitudeUAV, longitudeUAV, siguiente_waitpoint_latitude, siguiente_waitpoint_longitude);

        AnguloBanqueo=darAnguloBanqueo(PorcentajeAleronIzquierdo, AnguloBanqueo, dt);
        std::vector<float> angulos=darAngulo_360_180(AnguloBanqueo);
        AnguloBanqueo=angulos[1];
        std::vector<float> ICC=darVelocidadAngular_ICC(latitudeUAV, longitudeUAV, theta, AnguloBanqueo, VelocidadActual);
        VelocidadAngularActual=ICC[0];
        ICC_x=ICC[1];
        ICC_y=ICC[2];
        RadioGiro=ICC[3];
        ErrorAngularAnterior=ErrorAngular;

    
    }
    else{
        Update_Current_Waitpoint(index_waitpoint_actual+1);
    }


}
void Control::ImprimirDatos() {
    Serial.println("\n \n \n==== Datos Importantes ====");
    Serial.print("Dt");
    Serial.println(dt);
    Serial.print("Tiempo Actual: ");
    Serial.println(tiempo_actual);
    Serial.print("Tiempo Anterior: ");
    Serial.println(tiempo_anterior);

    Serial.print("Latitud Actual del UAVt: ");
    Serial.println(latitudeUAV, 6); // 6 dígitos decimales
    Serial.print("Longitud Actual del UAV: ");
    Serial.println(longitudeUAV, 6);

    Serial.print("Latitud Actual del Waypoint: ");
    Serial.println(actual_waitpoint_latitude, 6); // 6 dígitos decimales
    Serial.print("Longitud Actual del Waypoint: ");
    Serial.println(actual_waitpoint_longitude, 6);

    Serial.print("Latitud del Siguiente Waypoint: ");
    Serial.println(siguiente_waitpoint_latitude, 6);
    Serial.print("Longitud del Siguiente Waypoint: ");
    Serial.println(siguiente_waitpoint_longitude, 6);


    Serial.print("Magnitud del Vector Waypoint: ");
    Serial.println(vector_waitpoint_magnitud,6);
    Serial.print("Ángulo del Vector Waypoint: ");
    Serial.println(vector_waitpoint_angulo,6);

    Serial.print("Ángulo de Rumbo Deseado: ");
    Serial.println(vectorRumboDeseado_angulo,6);
    Serial.print("Magnitud de Rumbo Deseado: ");
    Serial.println(vectorRumboDeseado_magnitud,6);

    Serial.print("Error de Posición: ");
    Serial.println(errorPosicion);
    Serial.print("Error Angular: ");
    Serial.println(ErrorAngular,6);
    Serial.print("Velocidad Error Angular: ");
    Serial.println(VelocidadErrorAngular,6);



    Serial.print("Radio de Giro: ");
    Serial.println(RadioGiro,6);
    Serial.print("Velocidad Angular Actual: ");
    Serial.println(VelocidadAngularActual,6);

    Serial.print("Theta: ");
    Serial.println(theta,6);
    Serial.print("Angulo de Banqueo: ");
    Serial.println(AnguloBanqueo,6);

    Serial.print("Index ");
    Serial.println(index_waitpoint_actual);
    /*
    Serial.println("waitpoints: ");
    for (int i = 0; i < num_waitpoints; ++i) {
        Serial.print(waitPoints[i][0],6);
        Serial.print(", ");
        Serial.println(waitPoints[i][1],6);
    }
    Serial.println("===========================");
    */
}


/*
std::vector<float> darPoseFutura(std::vector<float> PoseActual, float VelocidadActual, float VelocidadAngularActual, std::vector<float> Icc, float dt) {
    if (VelocidadAngularActual == 0) {
        return {PoseActual[0] + VelocidadActual * dt * cos(M_PI * PoseActual[2] / 180), PoseActual[1] + VelocidadActual * dt * sin(M_PI * PoseActual[2] / 180), PoseActual[2]};
    } else {
        float Icc_vec_x = PoseActual[0] - Icc[0];
        float Icc_vec_y = PoseActual[1] - Icc[1];
        std::vector<float> Icc_vec = {Icc_vec_x, Icc_vec_y};
        std::vector<float> Icc_polar = darPolar(Icc_vec[0], Icc_vec[1]);
        float Icc_mag = Icc_polar[0];
        float Icc_ang = Icc_polar[1];
        float AnguloRecorrido = VelocidadAngularActual * M_PI / 180 * dt;
        std::vector<float> xy = darRectangular(Icc_mag, Icc_ang + AnguloRecorrido);
        float x = xy[0] + Icc[0];
        float y = xy[1] + Icc[1];
        float theta = PoseActual[2] + AnguloRecorrido * 180 / M_PI;
        theta = darAngulo_360_180(theta)[1];
        return {x, y, theta};
    }
}

std::vector<float> darVelocidadAngular_ICC(std::vector<float> PoseActual, float AnguloBanqueo, float VelocidadActual) {
    if (AnguloBanqueo == 0) {
        return {0, 0, 0, 0};
    } else {
        float RadioGiro = std::abs((VelocidadActual * VelocidadActual) / (9.81 * std::tan(M_PI * AnguloBanqueo / 180)));
        float VelocidadAngular = (VelocidadActual / RadioGiro) * signo(AnguloBanqueo) * 180 / M_PI;
        float Icc_x = RadioGiro * std::cos(M_PI * PoseActual[2] / 180 + signo(AnguloBanqueo) * M_PI / 2) + PoseActual[0];
        float Icc_y = RadioGiro * std::sin(M_PI * PoseActual[2] / 180 + signo(AnguloBanqueo) * M_PI / 2) + PoseActual[1];
        return {VelocidadAngular, Icc_x, Icc_y, RadioGiro};
    }
}

std::vector<float> darPolar(float x, float y) {
    return {std::hypot(x, y), std::atan2(y, x)};
}


int signo(float x) {
    return (x >= 0) ? 1 : -1;
}

std::vector<float> darPendiente(std::vector<float> Punto1, std::vector<float> Punto2) {
    float m, b;
    if (Punto2[0] - Punto1[0] == 0) {
        m = 9999;
    } else {
        m = (Punto2[1] - Punto1[1]) / (Punto2[0] - Punto1[0]);
    }
    b = Punto2[1] - m * Punto2[0];
    return {m, b};
}

std::vector<float> proyectarPunto(std::vector<float> Punto, float Pendiente, float intersepto) {
    float xi = -(intersepto * Pendiente - Pendiente * Punto[1] - Punto[0]) / ((Pendiente * Pendiente) + 1);
    float yi = Pendiente * xi + intersepto;
    return {xi, yi};
}

std::vector<float> darPuntoIntermedio(std::vector<float> PuntoProyectado, float angulo, float Pendiente, float intersepto, float k_distanciaAuxiliar, std::vector<float> PuntoObjetivo) {
    float x1 = PuntoProyectado[0] + k_distanciaAuxiliar * std::cos(std::atan(Pendiente));
    float y1 = Pendiente * x1 + intersepto;
    float x2 = PuntoProyectado[0] - k_distanciaAuxiliar * std::cos(std::atan(Pendiente));
    float y2 = Pendiente * x2 + intersepto;
    if (std::hypot(PuntoObjetivo[0] - x1, PuntoObjetivo[1] - y1) < std::hypot(PuntoObjetivo[0] - x2, PuntoObjetivo[1] - y2)) {
        return {x1, y1};
    } else {
        return {x2, y2};
    }
}

float darCorreccionAngular(float AnguloActual, float AnguloDeseado) {
    float ErrorAngular = AnguloDeseado - AnguloActual;
    if (std::abs(ErrorAngular) < 180) {
        return ErrorAngular;
    } else {
        return ErrorAngular - 360 * signo(ErrorAngular);
    }
}

float darDerivada(float ValorActual, float ValorAnterior, float dt) {
    return (ValorActual - ValorAnterior) / dt;
}





std::vector<float> darAngulo_360_180(float anguloLeido) {
    float ang_encontrado_360, ang_encontrado_180;
    if (std::abs(anguloLeido) > 360) {
        float ang_encontrado_360 = std::modf(anguloLeido / 360, &ang_encontrado_360) * 360 * signo(anguloLeido);
        ang_encontrado_180 = (std::abs(ang_encontrado_360) <= 180) ? ang_encontrado_360 : ang_encontrado_360 - 360;
    } else {
        ang_encontrado_360 = anguloLeido;
        if (std::abs(anguloLeido) < 180) {
            ang_encontrado_180 = ang_encontrado_360;
        } else {
            ang_encontrado_180 = ang_encontrado_360 - 360 * signo(ang_encontrado_360);
        }
    }
    return {ang_encontrado_360, ang_encontrado_180};
}

float darErrorPosicion(const std::vector<float>& PuntoActual, const std::vector<float>& PuntoFinal) {
    float diffX = PuntoFinal[0] - PuntoActual[0];
    float diffY = PuntoFinal[1] - PuntoActual[1];
    
    // Llamar a la función darPolar para obtener la magnitud y el ángulo
    std::vector<float> polarResult = darPolar(diffX, diffY);
    
    // La magnitud se encuentra en el primer elemento del vector
    return polarResult[0];
}

*/