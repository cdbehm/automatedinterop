import json

#Object for managing sensors
class SensorManager:
    sensors_file = "mySensors.json"

    def resolve_sensor_type(self, type, source):
        if "Water" in type:
            if "GE 319" in source:
                return 'Water: IQ Flood'
            else:
                return 'Water: Other Flood'
        elif "Shock" in type:
            if "GE 319" in source:
                return 'Shock: IQ Shock'
            else:
                return 'Shock: Others'
        else:
            return type

    def get_sensor_from_file(self , label):
        sensor_details = {}
        with open(self.sensors_file) as json_file:
            mySensors = json.loads(json_file.read())
            mySensors = mySensors["SENSORS"]
            for sensor in mySensors:
                if sensor["LABEL"] == label:
                    sensor_details["LABEL"] = sensor["LABEL"]
                    sensor_details["SENSOR_TYPE"] = sensor["SENSOR_TYPE"]
                    sensor_details["SENSOR_TYPE_ID"] = sensor["SENSOR_TYPE_ID"]
                    sensor_details["SOURCE"] = sensor["SOURCE"]
                    sensor_details["SOURCE_ID"] = sensor["SOURCE_ID"]
                    sensor_details["DL_ID_PREFIX"] = sensor["DL_ID_PREFIX"]
                    sensor_details["DL_ID_SUFFIX"] = sensor["DL_ID_SUFFIX"]
                    sensor_details["PARTITION"] = sensor["PARTITION"]
                    sensor_details["TAMPER_PIN"] = sensor["TAMPER_PIN"]
                    sensor_details["TRIGGER_PIN"] = sensor["TRIGGER_PIN"]
                    sensor_details["SENSOR_GROUP"] = sensor["SENSOR_GROUP"]
                    sensor_details["TRIGGER_STATE"] = sensor["TRIGGER_STATE"]
                    sensor_details["TAMPER_STATE"] = sensor["TAMPER_STATE"]
                    sensor_details['GROUP_ID'] = sensor['GROUP_ID']
                    return sensor_details
        return False

    def get_sensor_detail(self , label , detail):
        with open(self.sensors_file) as json_file:
            mySensors = json.loads(json_file.read())
            mySensors = mySensors["SENSORS"]
            for sensor in mySensors:
                if sensor["LABEL"] == label:
                    return sensor[detail]

    def get_all_sensors_from_file(self):
        sensors = {}
        with open(self.sensors_file) as json_file:
            mySensors = json.loads(json_file.read())
            mySensors = mySensors["SENSORS"]
            for sensor in mySensors:
                sensors[sensor["LABEL"]] = {}
                sensors[sensor["LABEL"]]["SENSOR_TYPE"] = sensor["SENSOR_TYPE"]
                sensors[sensor["LABEL"]]["SOURCE"] = sensor["SOURCE"]
                sensors[sensor["LABEL"]]["DL_ID_PREFIX"] = sensor["DL_ID_PREFIX"]
                sensors[sensor["LABEL"]]["DL_ID_SUFFIX"] = sensor["DL_ID_SUFFIX"]
                sensors[sensor["LABEL"]]["PARTITION"] = sensor["PARTITION"]
                sensors[sensor["LABEL"]]["TAMPER_PIN"] = sensor["TAMPER_PIN"]
                sensors[sensor["LABEL"]]["TRIGGER_PIN"] = sensor["TRIGGER_PIN"]
                sensors[sensor["LABEL"]]["SENSOR_GROUP"] = sensor["SENSOR_GROUP"]
                sensors[sensor["LABEL"]]["TRIGGER_STATE"] = sensor["TRIGGER_STATE"]
                sensors[sensor["LABEL"]]["TAMPER_STATE"] = sensor["TAMPER_STATE"]
            return sensors