#### Libraries #####
from sense_hat import SenseHat
import os
from datetime import datetime
import time
from pymongo import MongoClient

##### Logging Settings #####

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

def t_correct():
  t1 = sense.get_temperature_from_humidity()
  t2 = sense.get_temperature_from_pressure()
  t_cpu = get_cpu_temp()
  t = (t1 + t2) / 2
  t_corr = t - ((t_cpu - t) / 1.5)
  t_corr = get_smooth(t_corr)
  return(t_corr)

def get_sense_data():

      i = 1 
      data[i] = {
      "timestamp " : datatime.now(),
      "temp" : t_correct(),
      "humid" : sense.get_humidity(),
      "pressure" : sense.get_pressure(),
      "orientation" : sense.get_orientation(),
      "Mag" : sense.get_compass_raw(),
      "ACCELERATION" : sense.get_accelerometer_raw(),
      "Gyro" : sense.get_gyroscope_raw()
      }


def timed_log():
      while True:
        log_data()
        sleep(DELAY)


##### Main Program #####
sense = SenseHat()

while True:
    time.sleep(1)
    sense_data = get_sense_data()

    i = i + 1
    if DELAY == 0:
        log_data()

    if len(batch_data) >= WRITE_FREQUENCY:
        print("Writing to file..")
        with open(filename,"a") as f:
            for line in batch_data:
                f.write(line + "\n")
            batch_data = []
    

if DELAY > 0:
    sense_data = get_sense_data()
    Thread(target= timed_log).start()
