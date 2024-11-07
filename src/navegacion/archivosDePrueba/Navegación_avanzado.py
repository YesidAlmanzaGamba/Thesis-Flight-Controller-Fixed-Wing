from typing import List
import numpy as np
import matplotlib.pyplot as plt
import math 
from Utils import *

# Entradas del Sistema

#ListaCoordenadas = [
  # (4.706908, -74.054049),(4.708387, -74.062426),(4.711306, -74.069217),
  # (4.711314, -74.070368),(4.715111, -74.070151),(4.723216, -74.066521),
  # (4.723930, -74.065776),(4.722003, -74.061314),(4.719383, -74.057230),
  # (4.718980, -74.051854),(4.718399, -74.049087),(4.711562, -74.029175),
  # (4.706295, -74.028355),(4.702076, -74.028741),(4.706772, -74.053972)]

ListaCoordenadas = [(4.653453, -74.093492),(4.691751, -74.124330),(4.635802, -74.127502),(4.705188, -74.037882),(4.648194, -74.101032),(4.686006, -74.074529),(4.591923, -74.123288),(4.666200, -74.110636)]

ListaWaitPoints = waitPoints_coordenadas_a_rectangulares(ListaCoordenadas)


#ListaWaitPoints = [[0,0],[-500,-200],[-700,800],[900,1000],[800,-1500],[0,0]]
#ListaWaitPoints = [[0,0],[1000,1000],[2000,-500], [2200, 3000],[-1000,500], [-2000,-1000]]
#WaitPointInicial = [np.random.randint(-5000,high=5000),np.random.randint(-5000,high=5000)]    # (P0) Posición X,Y en m
#WaitPointFinal = [np.random.randint(-5000,high=5000),np.random.randint(-5000,high=5000)]  # (P3) Posición X,Y en m

PoseActual = [300,150,0]      # (P1) Pose actual del UAV X,Y, theta
VelocidadActual = 30          # Velocidad del UAV en m/s

k_distanciaAuxiliar = 100     # (k-P3') Distancia sobre la recta entre waitpoints desde el punto proyectado actual (Pi) y el punto deseado (P3')
dt = 0.2                      # Tiempo de muestreo de los sensores en s

kp = 2                        # Constante Proporcional
kd = 0.1                      # Constante derivativa

cte_saturacion = 10           # Constante de saturacion del controlador [0-100]%


condicionActualizacion = 50   # Umbral de distancia del uav al punto objetivo que permite indicar una actualización de wait point

      


# Se crean listas vacias para almacenar datos 

PoseActual_list = []
PoseFutura_list = []
Alerones_list = []
AnguloBanqueo_list = []
ErrorAngular_list = []
PuntoProyectado_list = []
PuntoDeseado_list = []
VectorRumboDeseado_list = []
ErrorPosicion_list = []
TiempoSimulacion_list = []




# Inicia el algoritmo

# Se establece las condiciones iniciales de algunas variables

ErrorAngularAnterior = 0
TiempoSimulacion = 0 
AnguloBanqueo = 0           # Ángulo de inclinacion del UAV (ROLL) en °


for i in range(len(ListaWaitPoints)-1):
    WaitPointInicial = ListaWaitPoints[i]
    WaitPointFinal = ListaWaitPoints[i+1]

    ErrorPosicion = darErrorPosicion(PoseActual, WaitPointFinal)

    # Vector WaitPoint
    VectorWaitPoints = [WaitPointFinal[0]-WaitPointInicial[0], WaitPointFinal[1]- WaitPointInicial[1]]
    VectorWaitPoints_mag, VectorWaitPoints_ang = darPolar(VectorWaitPoints[0], VectorWaitPoints[1])
    PendienteWaitPoints, IntersectoWaitPoints = darPendiente(WaitPointInicial, WaitPointFinal)


    #while TiempoSimulacion<200:
    while ErrorPosicion>50:
        # Se determina el rumbo deseado
        PuntoProyectado =  proyectarPunto(PoseActual[:2], PendienteWaitPoints, IntersectoWaitPoints)
        PuntoIntermedio = darPuntoIntermedio(PuntoProyectado, VectorWaitPoints_ang ,PendienteWaitPoints, IntersectoWaitPoints ,k_distanciaAuxiliar, WaitPointFinal)
        VectorRumboDeseado = [PuntoIntermedio[0]- PoseActual[0], PuntoIntermedio[1]- PoseActual[1]]
        DistanciaPuntoIntermedio, RumboDeseado = darPolar(VectorRumboDeseado[0], VectorRumboDeseado[1])

        # Se realiza el control
        ErrorAngular = darCorreccionAngular(PoseActual[2], math.degrees(RumboDeseado))
        VelocidadErrorAngular = darDerivada(ErrorAngular, ErrorAngularAnterior, dt)
        PorcentajeAleronIzquierdo, PorcentajeAleronDerecho = darControlAleron(ErrorAngular, VelocidadErrorAngular, kp, kd, cte_saturacion, AnguloBanqueo)

        ErrorPosicion = darErrorPosicion(PoseActual, WaitPointFinal)
        #k_distanciaAuxiliar = ErrorPosicion if ErrorPosicion<200 else 100

        # Se determina el ángulo de banqueo y el movimiento circular del UAV

        AnguloBanqueo = darAnguloBanqueo(PorcentajeAleronIzquierdo, AnguloBanqueo,dt)
        AnguloBanqueo = darAngulo_360_180(AnguloBanqueo)[1]
        VelocidadAngularActual, Icc_x, Icc_y, RadioGiro = darVelocidadAngular_ICC(PoseActual, AnguloBanqueo, VelocidadActual)
        Icc = [Icc_x, Icc_y]
        PoseFutura = darPoseFutura(PoseActual, VelocidadActual, VelocidadAngularActual, Icc, dt)


        # Se guardan los valores de interes en listas
        PoseActual_list.append(PoseActual)
        PoseFutura_list.append(PoseFutura)
        PuntoProyectado_list.append(PuntoProyectado)
        VectorRumboDeseado_list.append(VectorRumboDeseado)
        Alerones_list.append([PorcentajeAleronIzquierdo, PorcentajeAleronDerecho])
        ErrorAngular_list.append(ErrorAngular)
        AnguloBanqueo_list.append(AnguloBanqueo)
        ErrorPosicion_list.append(ErrorPosicion)
        TiempoSimulacion_list.append(TiempoSimulacion)

        # Se actualizan las variables para la siguiente iteración
        ErrorAngularAnterior = ErrorAngular
        PoseActual = PoseFutura

        TiempoSimulacion = TiempoSimulacion + dt


# Se generan las figuras de los registros de la simulación

print('P1: ', PoseActual_list[0])



# Figura que muestra la pose inicial del UAV y el trayecto recorrido hasta converger en el punto objetivo

PoseActual_list = np.array(PoseActual_list)
PoseFutura_list = np.array(PoseFutura_list)
Alerones_list = np.array(Alerones_list)

plt.figure(1,figsize=(16,8))
plt.subplot(1,2,1)
if len(ListaWaitPoints)<=2:
    plt.scatter(WaitPointInicial[0], WaitPointInicial[1], label='P0')
    plt.scatter(WaitPointFinal[0], WaitPointFinal[1], label='P3')
    plt.arrow(WaitPointInicial[0],WaitPointInicial[1],WaitPointFinal[0]-WaitPointInicial[0],WaitPointFinal[1]-WaitPointInicial[1], width= 1.2, label='WaitPoints', edgecolor ='black', facecolor = 'black', head_width= 11)
    plt.scatter(PoseActual_list[0][0],PoseActual_list[0][1], label='P1')
    plt.plot([PoseActual_list[0][0], PuntoProyectado_list[0][0]],[PoseActual_list[0][1],PuntoProyectado_list[0][1]], ls= '--', label= 'Proyeción Pi', color=[231/255,169/255,39/255])
    plt.arrow(PoseActual_list[0][0],PoseActual_list[0][1],PoseFutura_list[0][0]-PoseActual_list[0][0],PoseFutura_list[0][1]-PoseActual_list[0][1], width= 1.2, label='Rumbo Actual', edgecolor = [108/255,52/255,131/255], facecolor= [108/255,52/255,131/255], head_width= 11)
    plt.arrow(PoseActual_list[0][0],PoseActual_list[0][1],VectorRumboDeseado_list[0][0],VectorRumboDeseado_list[0][1], width= 1.2, label='Rumbo Deseado', edgecolor = [192/255,57/255,43/255], facecolor= [192/255,57/255,43/255], head_width= 11)
    plt.plot(plotAngle(30, PoseActual_list[0][0], PoseActual_list[0][1], ErrorAngular_list[0], PoseActual_list[0][2])[0], plotAngle(30, PoseActual_list[0][0], PoseActual_list[0][1], ErrorAngular_list[0], PoseActual_list[0][2])[1], label = 'Corrección Angular: '+ str(round(ErrorAngular_list[0],1)), color=[98/255,101/255,103/255])
    
else:
    plt.scatter(PoseActual_list[0][0],PoseActual_list[0][1], label='P1')
    plt.plot([PoseActual_list[0][0], PuntoProyectado_list[0][0]],[PoseActual_list[0][1],PuntoProyectado_list[0][1]], ls= '--', label= 'Proyeción Pi', color=[231/255,169/255,39/255])
    plt.arrow(PoseActual_list[0][0],PoseActual_list[0][1],PoseFutura_list[0][0]-PoseActual_list[0][0],PoseFutura_list[0][1]-PoseActual_list[0][1], width= 1.2, label='Rumbo Actual', edgecolor = [108/255,52/255,131/255], facecolor= [108/255,52/255,131/255], head_width= 11)
    plt.arrow(PoseActual_list[0][0],PoseActual_list[0][1],VectorRumboDeseado_list[0][0],VectorRumboDeseado_list[0][1], width= 1.2, label='Rumbo Deseado', edgecolor = [192/255,57/255,43/255], facecolor= [192/255,57/255,43/255], head_width= 11)
    plt.plot(plotAngle(30, PoseActual_list[0][0], PoseActual_list[0][1], ErrorAngular_list[0], PoseActual_list[0][2])[0], plotAngle(30, PoseActual_list[0][0], PoseActual_list[0][1], ErrorAngular_list[0], PoseActual_list[0][2])[1], label = 'Corrección Angular: '+ str(round(ErrorAngular_list[0],1)), color=[98/255,101/255,103/255])
    for i in range(len(ListaWaitPoints)-1):
        if i ==0:
            plt.scatter(ListaWaitPoints[i][0],ListaWaitPoints[i][1], label = 'WaitPoint Inicial')
        else:
            plt.scatter(ListaWaitPoints[i][0],ListaWaitPoints[i][1])
        plt.arrow(ListaWaitPoints[i][0],ListaWaitPoints[i][1],ListaWaitPoints[i+1][0]-ListaWaitPoints[i][0],ListaWaitPoints[i+1][1]-ListaWaitPoints[i][1], width= 1.2, edgecolor ='black', facecolor = 'black', head_width= 30)
    
plt.grid(1)
plt.legend()
plt.axis('equal')
plt.title('Condición Inicial')


plt.subplot(1,2,2)
plt.plot(PoseActual_list[:,0], PoseActual_list[:,1], color='red')
plt.arrow(WaitPointInicial[0],WaitPointInicial[1],WaitPointFinal[0]-WaitPointInicial[0],WaitPointFinal[1]-WaitPointInicial[1], width= 1.2, label='WaitPoints', edgecolor ='black', facecolor = 'black', head_width= 11)
plt.scatter(WaitPointInicial[0], WaitPointInicial[1], label='P0')
plt.scatter(WaitPointFinal[0], WaitPointFinal[1], label='P3')
plt.scatter(PoseActual_list[0][0],PoseActual_list[0][1], label='P1')
for i in range(len(ListaWaitPoints)-1):
        plt.scatter(ListaWaitPoints[i][0],ListaWaitPoints[i][1])
        plt.arrow(ListaWaitPoints[i][0],ListaWaitPoints[i][1],ListaWaitPoints[i+1][0]-ListaWaitPoints[i][0],ListaWaitPoints[i+1][1]-ListaWaitPoints[i][1], width= 1.2, edgecolor ='black', facecolor = 'black', head_width= 30)
    
plt.grid(1)
plt.legend()
plt.axis('equal')
plt.title('Recorrido')



# Figura que muestra El error angular y el Error de posición a lo largo del tiempo de simulación


plt.figure(figsize= (16,8))
plt.subplot(1,2,1)
plt.plot(TiempoSimulacion_list, ErrorAngular_list)
plt.title('Error Angular Vs Tiempo')
plt.xlabel('Tiempo [s]')
plt.ylabel('Error [°]')
plt.axis([0,TiempoSimulacion_list[-1], -360,360])
plt.grid(1)

plt.subplot(1,2,2)
plt.plot(TiempoSimulacion_list, ErrorPosicion_list)
plt.title('Error de Posición Vs Tiempo')
plt.xlabel('Tiempo [s]')
plt.ylabel('Error [m]')
plt.axis([0,TiempoSimulacion_list[-1], min(ErrorPosicion_list)-100,max(ErrorPosicion_list)+100])
plt.grid(1)



# Figura que muestra la accion de control y el ángulo de banqueo

plt.figure(figsize= (19,8))
plt.subplot(1,3,1)
plt.plot(TiempoSimulacion_list, Alerones_list[:,0], label='Porcentaje Alerón Izquierdo')
plt.title('Controlador Vs Tiempo')
plt.xlabel('Tiempo [s]')
plt.ylabel('Porcentaje [%]')
plt.legend()
plt.axis([0,TiempoSimulacion_list[-1], -110,110])
plt.grid(1)
plt.subplot(1,3,2)
plt.plot(TiempoSimulacion_list, Alerones_list[:,1], label='Porcentaje Alerón Derecho')
plt.title('Controlador Vs Tiempo')
plt.xlabel('Tiempo [s]')
plt.ylabel('Porcentaje [%]')
plt.legend()
plt.axis([0,TiempoSimulacion_list[-1], -110,110])
plt.grid(1)

plt.subplot(1,3,3)
plt.plot(TiempoSimulacion_list, AnguloBanqueo_list)
plt.title('ángulo de Banqueo Vs Tiempo')
plt.xlabel('Tiempo [s]')
plt.ylabel('Ángulo Banqueo [°]')
plt.axis([0,TiempoSimulacion_list[-1], -90,90])
plt.grid(1)
plt.show()



print(round(8/9,2))