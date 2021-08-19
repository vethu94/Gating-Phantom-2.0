from flask import Flask, render_template
import datetime,serial
import serial
import time
import math
import dummy_phantom
import multiprocessing

debug_mode = True
if not debug_mode:
    ser=serial.Serial('/dev/ttyUSB0',2400,timeout=None)
else:
    ser = dummy_phantom.DummyPhantom()

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

program =""

app = Flask(__name__)
@app.route("/")
def index():
   now = datetime.datetime.now() 
   timeString = now.strftime("%Y-%m-%d %H:%M")
   templateData = {
      'title' : 'AMS!',
      'time': timeString
      }
   return render_template('index.html', **templateData)

@app.route("/config/<period>/<amplitude>")
def config(period, amplitude):
    now = datetime.datetime.now() 
    timeString = now.strftime("%Y-%m-%d %H:%M")
    templateData = {
      'title' : 'AMS!',
      'time': timeString,
    }
    print(f"{period=}, {amplitude=}")
    return render_template('index.html', **templateData)



@app.route("/action/<buttonP>")
def action(buttonP):
    global program, cycleTime, Proz
    if buttonP == 'one':
        program = "ONE"
        cycleTime = 5
        Proz=1
        start_send(cycleTime,Proz)
    elif buttonP == 'two':
        program = "TWO"
        cycleTime = 2
        Proz=0.2
        start_send(cycleTime,Proz)
    elif buttonP == 'three':
        program = "THREE"
        ser.setRTS(True)
        ser.reset_input_buffer()
        ser.reset_output_buffer()
    elif buttonP == 'four':
        program = "FOUR"
    else:
        program = [str(temp)for temp in buttonP.split() if temp.isdigit()]
   
#     ser.write (bytes(program,'utf-8'))
    print(program)
   
    templateData = {
            'programm'  : program,
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
        print(f"{cycleTime=}, {Proz=}")
        time.sleep(2)

def send(cycleTime,Proz):
    global program
    program1 = program
    freq = 1/cycleTime
    xProz = Proz
    yProz = Proz
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
        
        # 0.05 Sekunden warten
        time.sleep(0.03)
     
if __name__ == "__main__":
   app.run(host='0.0.0.0', port=4444, debug=True)
   

    

# ser.close()