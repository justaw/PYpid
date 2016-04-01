#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import glob
import time
import sys
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')
import subprocess
import fcntl, socket, struct
import wiringpi
# external file imports

import PID # PID controller by 
# IvPID.
# Copyright (C) 2015 Ivmech Mechatronics Ltd. <bilgi@ivmech.com>


# activate wiringPi with mapping to physical ports of pinheader 
wiringpi.wiringPiSetupPhys()


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'

try:
 device_folder_0 = glob.glob(base_dir + '28*')[0]
 device_folder_1 = glob.glob(base_dir + '28*')[1]
except:
 print "no one wire devices found"
 
try:
 device_file_0 = device_folder_0 + '/w1_slave'
 device_file_1 = device_folder_1 + '/w1_slave'
except:
 print "no valid one wire data found"

############################################################################
############################################################################
############################################################################
#                             functions					   #
############################################################################
############################################################################
############################################################################

def getHwAddr(ifname):
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
  return '-'.join(['%02x' % ord(char) for char in info[18:24]])

def read_temp_raw(device):
   f = open(device_file_0, 'r')
   lines = f.readlines()
   f.close()
   if device == 1:
    f = open(device_file_1, 'r')
    lines = f.readlines()
    f.close()
   return lines

def read_temp(device):
 lines = read_temp_raw(device)
 while lines[0].strip()[-3:] == 'YES':
  time.sleep(0.2)
  #print "found YES"
  lines = read_temp_raw(device)
  equals_pos = lines[1].find('t=')
  if equals_pos != -1:
   temp_string = lines[1][equals_pos+2:]
   temp_c = float(temp_string) / 1000.0
   temp_f = temp_c * 9.0 / 5.0 + 32.0
   return temp_c



############################################################################
############################################################################
############################################################################
#                             functions end                                #
############################################################################
############################################################################
############################################################################



# Inputs

# Outputs
# PIN | Funkt.		 | Ziel
#---------------------------------		
# 29  | Warm auf	 | 4er 1
# 31  | Warm zu 	 | 4er 2
# 33  | Kalt auf	 | 4er 3
# 35  | Kalt zu 	 | 4er 4
# 37  | RL auf Warm	 | 2er 1
# 30  | RL auf Kalt	 | 2er 2
# 39  | GND		 | 4er GND  dann durchschleifen auf 2er GND
# Keep in mind, the relais board are low active --> 0V means Relais is activated
wiringpi.pinMode(29, 1)
wiringpi.pinMode(31, 1)
wiringpi.pinMode(33, 1)
wiringpi.pinMode(35, 1)
wiringpi.pinMode(37, 1)
wiringpi.pinMode(40, 1)

#all relays off
wiringpi.digitalWrite(29, 1)
wiringpi.digitalWrite(31, 1)
wiringpi.digitalWrite(33, 1)
wiringpi.digitalWrite(35, 1)
wiringpi.digitalWrite(37, 1)
wiringpi.digitalWrite(40, 1)


# get installes one wire devices
list = os.listdir(base_dir) # dir is your directory path
number_files = len(list)
print number_files

#print "VL: " + str(read_temp(0))
#print "RL: " + str(read_temp(1))

# Antriebe
runtime_full_range = 160 # 160sec Laufzeit  fuer 100% Ventilöffnung
runtime_offset = 10 # 10 sec Laufzeit Offset für sicheres schliessen 
runtime_frame = 2 #  sec Laufzeit minimum
runtime_max_frame = 10 # sec Laufzeit am Stue�ck maximum


# PID Regler Variablen 
P = 20
I = 0.1
D = 0.0

pid = PID.PID(P, I, D)
pid.SetPoint=23.0
pid.setSampleTime(10)
 
feedback = 0

#    feedback_list = []
#    time_list = []
#    setpoint_list = []



while 1:
 feedback = read_temp(0)
 pid.update(feedback)
 output = pid.output 
 print "Ist: " + str(feedback) + "C " + str(output) + "%" 
 time.sleep(10)
  

