import numpy as np
import math


# Se declaran las funciones 


def waitPoints_coordenadas_a_rectangulares(ListaCoordenadas):
    # Retorna una lista de coordenadas en termino de metros. donde el origen cae en la primera coordenada de ListaCoordenadas
    # Lista de coordenadas [[lat, long], ....]
    factor = 6371*2*math.pi/360 # equivalente de un grado terrestre en km

    Coordenadas_rect = [[0,0]]
    for i in range(len(ListaCoordenadas)-1):
        coord = [ListaCoordenadas[i+1][1]-ListaCoordenadas[0][1], ListaCoordenadas[i+1][0]-ListaCoordenadas[0][0]]
        coord = [coord[0]*factor*1000, coord[1]*factor*1000]
        Coordenadas_rect.append(coord)
    return Coordenadas_rect




def darPoseFutura(PoseActual, VelocidadActual, VelocidadAngularActual, Icc, dt):
    # PoseActual [X,Y,ang] en [m,m,°]
    # VelocidadActual en m/s
    # VelocidadAngularActual en °/s
    # se retorna PoseFutura [X,Y,ang] en [m,m,°]
    if VelocidadAngularActual == 0:
        return [PoseActual[0] + VelocidadActual*dt*math.cos(math.radians(PoseActual[2])), PoseActual[1] + VelocidadActual*dt*math.sin(math.radians(PoseActual[2])), PoseActual[2] ]
    else:
        Icc_vec = [PoseActual[0]-Icc[0],PoseActual[1]-Icc[1]]
        Icc_mag, Icc_ang = darPolar(Icc_vec[0],Icc_vec[1])
        AnguloRecorrido = math.radians(VelocidadAngularActual)*dt
        x,y = darRectangular(Icc_mag, math.degrees(Icc_ang+AnguloRecorrido))
        x = x + Icc[0]
        y = y +Icc[1]
        theta = PoseActual[2] + math.degrees(AnguloRecorrido)
        theta = darAngulo_360_180(theta)[1]
        return [x,y,theta]



    
def darVelocidadAngular_ICC(PoseActual, AnguloBanqueo, VelocidadActual):
    # PoseActual [X,Y,ang] en [m,m,°]
    # AnguloBanqueo en °
    # VelocidadActual en m/s
    # dt en s
    # retorna [VelocidadAngular, ICC_x, ICC_y] en [°/s, m, m]
    if AnguloBanqueo == 0:
        return [0, 0, 0, 0]
    else:
        RadioGiro = abs((VelocidadActual**2)/(9.81*math.tan(math.radians(AnguloBanqueo))))
        VelocidadAngular = (VelocidadActual/RadioGiro)*signo(AnguloBanqueo)*180/math.pi
        Icc_x = RadioGiro*math.cos(math.radians(PoseActual[2])+signo(AnguloBanqueo)*math.pi/2)+PoseActual[0]
        Icc_y = RadioGiro*math.sin(math.radians(PoseActual[2])+signo(AnguloBanqueo)*math.pi/2)+PoseActual[1]
        return [VelocidadAngular, Icc_x, Icc_y, RadioGiro]

def darPolar(x,y):
    # Retorna la magnitud y dirección (rad) de un vector de componentes x,y
    return [math.hypot(x,y), math.atan2(y,x)]

def darRectangular(mag, ang):
    # Retorna las componentes rectangulares de un vector descrito en magnitud y dirección
    return [mag*math.cos(math.radians(ang)), mag*math.sin(math.radians(ang))]

def signo(x):
    if x>=0: return 1
    else: return -1



def darPendiente(Punto1, Punto2):
    # retorna el valor de la pendiente m y del intersecto b de la linea que surge de unir el Punto 1 y el Punto 2
    # Punto1 como [x,y]
    # Punto2 como [x,y]
    if Punto2[0]-Punto1[0] == 0: 
        m = 9999
    else:
        m = (Punto2[1]-Punto1[1])/(Punto2[0]-Punto1[0])
    b = Punto2[1]-m*Punto2[0]
    return m,b

def proyectarPunto(Punto, Pendiente, interescto):
    # retorna el punto proyectado [xi, yi] sobre la recta definida por la pendiente y el intersecto
    # Punto como [x,y]
    # Pendiente como escalar
    # intersecto como escalar
    xi = -(interescto*Pendiente-Pendiente*Punto[1]-Punto[0])/((Pendiente**2) + 1)
    yi = Pendiente*xi+interescto
    return [xi, yi]


def darPuntoIntermedio(PuntoProyectado, angulo ,Pendiente, interescto ,k_distanciaAuxiliar, PuntoObjetivo):
    # Retorna el punto intermedio (P3') en [x,y] sobre la recta definida por la pendiente y el intersecto a una distancia k_distanciaAuxiliar del punto proyectado sobre la recta y que este más cercano a PuntoObjetivo
    # PuntoProyectado (Pi) en [x,y]
    # El ángulo corresponde al angulo de la recta respecto a la horizontal (°)
    # Pendiente como escalar
    # intersecto como escalar
    # k_distanciaAuxiliar
    # PuntoObjetivo como [x,y]
    #x1 = PuntoProyectado[0]+k_distanciaAuxiliar*math.cos(math.radians(angulo))
    x1 = PuntoProyectado[0]+k_distanciaAuxiliar*math.cos(math.atan(Pendiente))
    y1 = Pendiente*x1+interescto
    #x2 = PuntoProyectado[0]-k_distanciaAuxiliar*math.cos(math.radians(angulo))
    x2 = PuntoProyectado[0]-k_distanciaAuxiliar*math.cos(math.atan(Pendiente))
    y2 = Pendiente*x2+interescto
    if math.hypot(PuntoObjetivo[0]-x1,PuntoObjetivo[1]-y1)<math.hypot(PuntoObjetivo[0]-x2,PuntoObjetivo[1]-y2):
        return [x1, y1]
    else:
        return [x2, y2]


def darCorreccionAngular(AnguloActual, AnguloDeseado):
    # Retorna El recorrido angular para llegar al angulo deseado y la dirección de giro.
    # direccion -1 -> AntiHorario
    # direccion  1 -> Horario
    ErrorAngular = AnguloDeseado-AnguloActual
    if abs(ErrorAngular)<180:
      return ErrorAngular
    else:
      return ErrorAngular - 360*signo(ErrorAngular)


def darDerivada(ValorActual, ValorAnterior, dt):
    return (ValorActual-ValorAnterior)/dt


def darControlAleron(Error, DerivadaError, kp, kd, cte_saturacion, AnguloBanqueo):
    # retorna el porcentaje de alerones de cada ala [PorcentajeAlerónIzquierdo, PorcentajeAlerónDerecho]
    # Se hace referencia al Alerón izquierdo (100% alerón abajo (Genera más sustentación), -100% alerón arriba (Genera menos sustentación))
    if abs(AnguloBanqueo)<25:
        controlador =  -kp*Error + kd*DerivadaError
        if abs(controlador) > 100:
            controlador = 100*signo(controlador)
    elif abs(AnguloBanqueo)<30:
        controlador =  -kp*Error + kd*DerivadaError
        if abs(controlador) > 100:
            controlador = 100*signo(controlador)
        penalizacion = (abs(AnguloBanqueo)-25)/5
        controlador = controlador*(1-penalizacion)
    else:
        #controlador = cte_saturacion*signo(AnguloBanqueo)
        controlador = cte_saturacion*AnguloBanqueo/100
    return [controlador, -controlador] 

def darAnguloBanqueo(PorcentajeAleronIzquierdo, AnguloBanqueoAnterior,dt):
    return (-1*1.2*PorcentajeAleronIzquierdo*dt+AnguloBanqueoAnterior)


def darAngulo_360_180(anguloLeido):
  # retorna el ángulo leido en fromato de [0,360]° y [-180,180]°
  # anguloLeido en °
  if abs(anguloLeido)>360:
    ang_encontrado_360 = math.modf(anguloLeido/360)[0]*360*signo(anguloLeido)
    ang_encontrado_180 = ang_encontrado_360 if abs(ang_encontrado_360)<=180  else ang_encontrado_360-360
  else:
    ang_encontrado_360 = anguloLeido
    if abs(anguloLeido)<180:
      ang_encontrado_180 = ang_encontrado_360
    else:
      ang_encontrado_180 = ang_encontrado_360-360*signo(ang_encontrado_360)
  return ang_encontrado_360, ang_encontrado_180


def darErrorPosicion(PuntoActual, PuntoFinal):
  # Retorna la distancia entre el punto actual y el prunto final.
  vec = [PuntoFinal[0]-PuntoActual[0], PuntoFinal[1]-PuntoActual[1]]
  Mag, ang = darPolar(vec[0], vec[1])
  return Mag

def plotCircle(R, x_centro, y_centro):
    n = np.linspace(0,np.pi*2,100)
    x = R*np.cos(n)+x_centro
    y = R*np.sin(n)+y_centro
    return x,y

def plotAngle(R, x_centro, y_centro, recorridoAngular, anguloInicio):
    n = np.linspace(math.radians(anguloInicio),math.radians(anguloInicio)+math.radians(recorridoAngular),100)
    x = R*np.cos(n)+x_centro
    y = R*np.sin(n)+y_centro
    return x,y