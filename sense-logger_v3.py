#### Libraries #####
from sense_hat import SenseHat
import os
from datetime import datetime
import time 

##### Logging Settings #####
TEMP_H=True
TEMP_P=True

HUMIDITY=True
PRESSURE=True
ORIENTATION=True
ACCELERATION=True
MAG=True
GYRO=True
FILENAME = ""
WRITE_FREQUENCY = 1
DELAY = 0


##### Functions #####
def file_setup(filename):
    header = [] 
    header.append("timestm, amp")
    if TEMP_H:
        header.append("temp_h")
    if TEMP_P:
        header.append("temp_p")
    if HUMIDITY:
        header.append("humidity")
    if PRESSURE:
        header.append("pressure")
    if ORIENTATION:
        header.extend(["pitch","roll","yaw"])
    if MAG:
        header.extend(["mag_x","mag_y","mag_z"])
    if ACCELERATION:
        header.extend(["accel_x","accel_y","accel_z"])
    if GYRO:
        header.extend(["gyro_x","gyro_y","gyro_z"])
    

    with open(filename,"w") as f:
        f.write(",".join(str(value) for value in header)+ "\n")

def log_data():
    output_string = ",".join(str(value) for value in sense_data)
    batch_data.append(output_string)

# get CPU temperature
def get_cpu_temp():
  res = os.popen("vcgencmd measure_temp").readline()
  t = float(res.replace("temp=","").replace("'C\n",""))
  return(t)
    
# use moving average to smooth readings
def get_smooth(x):
  if not hasattr(get_smooth, "t"):
    get_smooth.t = [x,x,x]
  get_smooth.t[2] = get_smooth.t[1]
  get_smooth.t[1] = get_smooth.t[0]
  get_smooth.t[0] = x
  xs = (get_smooth.t[0]+get_smooth.t[1]+get_smooth.t[2])/3
  return(xs)

def temp_calibration(t):
    t_cpu = get_cpu_temp()
    t_corr = t - ((t_cpu-t)/1.5)
    t_corr = get_smooth(t_corr)
    return t_corr
    
    
def get_sense_data():
    sense_data=[]
    
    sense_data.append(datetime.now())
    if TEMP_H:
          t1 = sense.get_temperature_from_humidity()
          sense_data.append(temp_calibration(t1))

    if TEMP_P:
          t2 = sense.get_temperature_from_pressure()
          sense_data.append(temp_calibration(t2))

    if HUMIDITY:
          sense_data.append(sense.get_humidity())

    if PRESSURE:
          sense_data.append(sense.get_pressure())

    if ORIENTATION:
          yaw,pitch,roll = sense.get_orientation().values()
          sense_data.extend([pitch,roll,yaw])

    if MAG:
          mag_x,mag_y,mag_z = sense.get_compass_raw().values()
          sense_data.extend([mag_x,mag_y,mag_z])

    if ACCELERATION:
          x,y,z = sense.get_accelerometer_raw().values()
          sense_data.extend([x,y,z])

    if GYRO:
          gyro_x,gyro_y,gyro_z = sense.get_gyroscope_raw().values()
          sense_data.extend([gyro_x,gyro_y,gyro_z])

    
    
    return sense_data

def timed_log():
      while True:
        log_data()
        sleep(DELAY)

def Display() :
    message = " Temp. - %d C Hum. - %d %% Pressure - %d mbars " %(temp_calibration(sense.get_temperature_from_humidity()),sense.get_humidity(),sense.get_pressure())
    sense.show_message(message, scroll_speed = 0.05, text_colour = [200,200,200], back_colour = [0,0,0])
    sense.clear()
##### Main Program #####
sense = SenseHat()
batch_data= []

if FILENAME == "":
    filename = "SenseLog-"+str(datetime.now())+".csv"
else:
    filename = FILENAME+"-"+str(datetime.now())+".csv"

file_setup(filename)

while True:
    time.sleep(1)
    sense_data = get_sense_data()
    
    if DELAY == 0:
        log_data()
    
    
    if len(batch_data) >= WRITE_FREQUENCY:
        print("Writing to file..")
        with open(filename,"a") as f:
            for line in batch_data:
                f.write(line + "\n")
                
            batch_data = []
    Display()

if DELAY > 0:
    sense_data = get_sense_data()
    Thread(target= timed_log).start()
