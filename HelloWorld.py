from flask import Flask, render_template
import datetime
import serial
import time
import math
import dummy_phantom
import multiprocessing

debug_mode = False
if not debug_mode:
    ser=serial.Serial('/dev/ttyUSB0',2400,timeout=None)
else:
    ser = dummy_phantom.DummyPhantom()
    
#Globale Variablen
y = 150
y_diff = 92
yProz=1
y_mid = 162
x = 150
x_diff = 102
xProz=1
x_mid =138
cycleTime = 8
freq = 1/cycleTime
Proz=1

process_phantom = None
stop = False

program =""

app = Flask(__name__)
@app.route("/")
def index():
   now = datetime.datetime.now() 
   timeString = now.strftime("%Y-%m-%d %H:%M")
   templateData = {
      'title' : 'AMS!',
      'cycletime': 5,
      'amplitude': 100,
      
      
      }
   return render_template('index.html', **templateData)

@app.route("/config/<period>/<amplitude>")
def config(period, amplitude):
    global program, cycleTime, Proz,stop
    stop=False
    if float(period) >= 1.5:
        cycleTime = float(period)
        Proz= float(amplitude)/100 
        start_send(cycleTime,Proz)
        now = datetime.datetime.now() 
        timeString = now.strftime("%Y-%m-%d %H:%M")
        templateData = {
          'title' : 'AMS!',
          'time': timeString,
          'cycletime': cycleTime,
          'amplitude': amplitude,
          'programm'  : "CUSTOM",     
        }
    else:
        templateData = {
          'time': "CYCLE TIME TO LOW!"  
        }
        
    return render_template('index.html', **templateData)



@app.route("/action/<buttonP>")
def action(buttonP):
    global program, cycleTime, Proz, stop
     
    if buttonP == 'one':
        program = "ONE"
        cycleTime = 5
        Proz=1
        stop=False
        start_send(cycleTime,Proz)
    elif buttonP == 'two':
        program = "TWO"
        cycleTime = 3
        Proz=0.2
        stop=False
        start_send(cycleTime,Proz)
    elif buttonP == 'three':
        program = "THREE"
        cycleTime = 10
        Proz=0.8
        stop=False
        start_send(cycleTime,Proz)
    elif buttonP == 'four':
        program = "FOUR"
        cycleTime = 1
        Proz=0.2
        stop=False
        start_send(cycleTime,Proz)
    else:
        stop=True
        start_send(cycleTime,Proz)
        program = "STOP"
    print(stop)
   
    templateData = {
            'programm'  : program,
            'cycletime': cycleTime,
            'amplitude': Proz*100
        
    }
    
    return render_template('index.html', **templateData)


def start_send(cycleTime, Proz):
    global process_phantom
    if process_phantom is not None:
        process_phantom.kill()
    if not debug_mode:
        process_phantom = multiprocessing.Process(target=send, args=(cycleTime,Proz))
    else:
        process_phantom = multiprocessing.Process(target=dummy_send, args=(cycleTime,Proz))
    process_phantom.start()


def dummy_send(cycleTime,Proz):
    while True:
        print(cycleTime, Proz)
        time.sleep(2)

def send(cycleTime,Proz):
    global program,stop
    program1 = program
    freq = 1/cycleTime
    xProz = Proz
    yProz = Proz
    if stop == False:
        while program == program1:
            program1 = program
            timecounter= time.perf_counter()
            print (timecounter)
            x = int(xProz*x_diff*math.sin(2*math.pi*freq*timecounter)+x_mid)
            y = int(yProz*y_diff*math.sin(2*math.pi*freq*timecounter)+y_mid)
            data1 = bytes([255,8,x])
            time.sleep(0.01)
            data2 = bytes([255,9,y])
            ser.write(data1)
            ser.write(data2)  
            print(f"x={x}; y={y};")
            print (time.perf_counter()-timecounter)
            print(freq)
            
            # 0.03 Sekunden warten, sonst werden zu viele Daten geschickt
            time.sleep(0.03)
    else :
        # x- und y-Achse auf Mid position stellen
        data1 = bytes([255,8,150])
        time.sleep(0.01)
        data2 = bytes([255,9,162])
        ser.write(data1)
        ser.write(data2)
        #Serial Out- und Input löschen
        ser.flushInput()
        ser.flushOutput()
        print("stop")
    return
if __name__ == "__main__":
   app.run(host='0.0.0.0', port=4444, debug=True)
   

    

# ser.close()
