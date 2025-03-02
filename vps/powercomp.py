
## Power computation functions ##

def BikePower(powerintegbuffer,speed,slope,weight,aerodynamic_coef=0.9,front_surface=0.45,air_density=1.225,roll_coef=0.005):
    "Compute bike power in Watts from speed in m/s, slope in unit (dx/dz), weight in kg"
    # gravity = 9.8 m/s/s
    
    # source: http://fontanilcyclisme.phpnet.org/puissance/form_puissance.php
    
    # slope resistance
    slopepower = weight * 9.81 * speed * slope
    
    # roll resistance
    rollpower = roll_coef * 9.81 * weight * speed
    
    # fluid resistance
    # 0.5 come from integration
    fluidpower = 0.5 * air_density * aerodynamic_coef * front_surface * speed * speed * speed
    
    #print('BikePower: slope=%f roll=%f fluid=%f' % (slopepower, rollpower, fluidpower))
    
    power = slopepower + rollpower + fluidpower
    
    if power < 0:
        powerintegbuffer[0] += -power
        return 0.0
    
    if power - powerintegbuffer[0] > 0:
        powerintegbuffer[0] = 0.0
        return power - powerintegbuffer[0]
    else:
        powerintegbuffer[0] -= power
        return 0.0


def CarPower(speed,slope,weight=1200,aerodynamic_coef=0.3,front_surface=2.8,air_density=1.225,roll_coef=0.005):
    return BikePower(speed,slope,weight,aerodynamic_coef,front_surface,air_density,roll_coef)

running_coef = [4.390658, 4.359548, 4.347104, 4.322216, 4.309772, 4.291106, 4.284884, 4.272440, 4.266218, 4.264144, 4.259996, 4.255848, 4.259996, 4.262070, 4.264144, 4.268292, 4.272440, 4.280736, 4.289032, 4.297328, 4.309772, 4.322216, 4.330512, 4.342956, 4.351252, 4.367844, 4.376140, 4.388584, 4.401028, 4.413472]

def RunningPower(speed,slope,weight):
    "Compute running power"

    # source: http://www.vo2max.com.fr/physio_coutenerg.html
    
    # slope resistance
    slopepower = IdentIfPositive(weight * 9.81 * speed * slope)
    
    # run power
    runpower = weight * speed * running_coef[InBounds(int(round((speed-6.3)/1.2)),0,len(running_coef)-1)]

    print('RunningPower: slope=%f run=%f' % (slopepower,runpower))
    
    return slopepower+runpower


def BoatPower(speed,course,hulllenght,windspeed,winddirection,windcoef,streamspeed,streamdirection,viscocinewater=1.141,fluidcoef=1.0,wavecoef=1.0,roughness=0.0001):

    # source: http://www.mecaflux.com/hydrodynamique_navale.htm
    
    correctedspeed = speed - cos(course-winddirection) * windspeed * windcoef - cos(course-streamdirection) * streamspeed
    
    reynolds = correctedspeed * hulllenght / viscocinewater
    
    rfluid = fluidcoef * reynolds * roughness / hulllength
    
    froude = correctedspeed / sqrt(9.81*hulllenght)
    
    rwave = wavecoef * froude
    
    return correctedspeed * (rfluid + rwave)


kayak_resistance = [2.3585, 4.0495, 6.0520, 8.4550, 11.2585, 14.9965, 20.6035, 30.0375, 43.4765, 52.5100, 64.0800, 83.6600]

def KayakPower(speed,course,windspeed=0.0,winddirection=0,windcoef=0.5,streamspeed=0.0,streamdirection=0,qualitycoef=1.0,):
    # http://www.oneoceankayaks.com/kayakpro/kayakgrid.htm
    
    correctedspeed = speed - cos(course-winddirection) * windspeed * windcoef - cos(course-streamdirection) * streamspeed
    correctedspeedknots = correctedspeed * 1.94384449
    
    return correctedspeed * correctedspeed * qualitycoef * kayak_resistance[InBounds(int(round((correctedspeedknots-1.5))),0,len(kayak_resistance)-1)]
    
    # http://www.robertscpa.com/kayaks/resistance.htm
