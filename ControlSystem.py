import SensorManager
import time
import serial
import pyfirmata
from pyfirmata import Arduino , util , ArduinoMega


# Object to interact with a Firmata Control System
class ControlSystem:
    com_port = None
    board = None
    SensorManager = None
    iterator = None
    inputs = []
    input_pins = None
    relays = None

    def __init__(self , sensors=None):
        self.SensorManager = SensorManager()
        if sensors:
            self.SensorManager.sensors_file = sensors

    def test(self , pins):
        for pin in pins:
            self.board.digital[pin].write(1)
            time.sleep(1)
            self.board.digital[pin].write(0)

    def setup(self):
        self.board = ArduinoMega(self.com_port)
        self.iterator = util.Iterator(self.board)
        self.iterator.start()
        if self.relays == "SSR":
            sensors = self.SensorManager.get_all_sensors_from_file()
            for key in sensors:
                if sensors[key]['TAMPER_STATE']:
                    if sensors[key]['TAMPER_STATE'] == "NO":
                        self.board.digital[int(sensors[key]['TAMPER_PIN'])].write(1)
                    else:
                        self.board.digital[int(sensors[key]['TAMPER_PIN'])].write(0)
                if sensors[key]['TRIGGER_STATE']:
                    if sensors[key]['TRIGGER_STATE'] == "NO":
                        self.board.digital[int(sensors[key]['TRIGGER_PIN'])].write(1)
                    else:
                        self.board.digital[int(sensors[key]['TRIGGER_PIN'])].write(0)

    def prepare_inputs(self):
        for INPUT in self.input_pins:
            self.inputs.append(self.board.get_pin('d:' + str(INPUT) + ':i'))
        time.sleep(3)

    def send_serial_command(self , text):
        arduino = serial.Serial(self.com_port , 115200 , timeout=0.1)
        time.sleep(3)  # give the connection a second to settle
        arduino.write(text.encode())
        i = 0
        while True:
            if i == 100:
                break
            data = arduino.readline()
            if data:
                data = data.decode("utf-8").strip()
                data.rstrip('\r\n')  # strip out the new lines for now
                # (better to do .read() in the long run for this reason
                # print(data)
                if data == "ACK":
                    time.sleep(1)
                    arduino.flush()
                    return True
            i = i + 1
        return False

    def asycn_send_serial_command(self , text):
        arduino = serial.Serial(self.com_port , 115200 , timeout=0.1)
        time.sleep(3)  # give the connection a second to settle
        arduino.write(text.encode())

    def trigger_sensor(self , sensor):
        trigger_pin = self.SensorManager.get_sensor_detail(sensor , "TRIGGER_PIN")
        if trigger_pin:
            self.board.digital[int(trigger_pin)].write(1)
            time.sleep(3)
            self.board.digital[int(trigger_pin)].write(0)

    def toggle_sensor(self , sensor):
        trigger_pin = self.SensorManager.get_sensor_detail(sensor , "TRIGGER_PIN")
        self.board.digital[int(trigger_pin)].mode = pyfirmata.INPUT
        pin_state = self.board.digital[int(trigger_pin)].read()
        self.board.digital[int(trigger_pin)].mode = pyfirmata.OUTPUT
        if not pin_state:
            self.board.digital[int(trigger_pin)].write(1)
        else:
            self.board.digital[int(trigger_pin)].write(0)

    def toggle_tamper(self , sensor):
        tamper_pin = self.SensorManager.get_sensor_detail(sensor , "TAMPER_PIN")
        self.board.digital[int(tamper_pin)].mode = pyfirmata.INPUT
        pin_state = self.board.digital[int(tamper_pin)].read()
        self.board.digital[int(tamper_pin)].mode = pyfirmata.OUTPUT
        if not pin_state:
            self.board.digital[int(tamper_pin)].write(1)
        else:
            self.board.digital[int(tamper_pin)].write(0)

    def open(self , sensor):
        self.board.digital[int(self.SensorManager.get_sensor_detail(sensor , "TRIGGER_PIN"))].write(1)

    def close(self , sensor):
        self.board.digital[int(self.SensorManager.get_sensor_detail(sensor , "TRIGGER_PIN"))].write(0)

    def tamper_sensor(self , sensor):
        tamper_pin = self.SensorManager.get_sensor_detail(sensor , "TAMPER_PIN")
        if tamper_pin:
            self.board.digital[int(tamper_pin)].write(1)
            time.sleep(3)
            self.board.digital[int(tamper_pin)].write(0)

    def register_sensor(self , sensor):
        self.tamper_sensor(sensor)
        time.sleep(4)
        self.trigger_sensor(sensor)

    def open_garage(self):
        garage = self.asycn_send_serial_command("CMD4/0")
        if garage != True:
            return False
        else:
            return True

    def close_garage(self):
        garage = self.asycn_send_serial_command("CMD5/0")
        if garage != True:
            return False
        else:
            return True

    def trigger_doorbell(self , Doorbell):
        if Doorbell.model == "ADC-VDB770":
            actuator_time = 1
        else:
            actuator_time = 0.8
        self.board.digital[int(Doorbell.aux_pin)].write(1)
        time.sleep(1)
        self.board.digital[int(Doorbell.trigger_pin)].write(1)
        time.sleep(actuator_time)
        self.board.digital[int(Doorbell.trigger_pin)].write(0)
        time.sleep(1)
        self.board.digital[int(Doorbell.aux_pin)].write(0)

    def confirm_input_high(self , w):
        counter = 0
        while counter < 12000:
            iter = 0
            for INPUT in self.inputs:
                if INPUT.read():
                    iter += 1
            if iter == len(self.inputs):
                break
            time.sleep(0.3)
            counter += 1
        if counter >= 12000:
            return False
        w.put({"toggle_time": datetime.now()})
        return datetime.now()

    def confirm_input_low(self , q):
        counter = 0
        while counter < 12000:
            iter = 0
            for INPUT in self.inputs:
                if not INPUT.read():
                    iter += 1
            if iter == len(self.inputs):
                break
            time.sleep(0.3)
            counter += 1
        if counter >= 12000:
            return False
        q.put({"toggle_time": datetime.now()})
        return datetime.now()

    def tear_down(self):
        self.board.exit()