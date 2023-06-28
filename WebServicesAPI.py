# import libraries
import time
from tqdm import tqdm
from datetime import datetime , timedelta
import random
import zeep
from zeep import Client
from CredentialsManager import CredentialsManager
from zeep.transports import Transport
from requests import Session
import csv


class _AdcWebServices:
    credentials = None
    caller_version = None
    log_file = None
    console_log = True
    use_proxy = False
    proxies = {'http': 'http://abe-elkdmz-01:443' , 'https': 'http://abe-elkdmz-01:443'}
    dealer_id = None
    result_obj_type = 'list'
    valid_cameras = ['ADC-V723' , 'ADC-V523' , 'ADC-V522IR' , 'ADC-V722W' , 'ADC-V721W' , 'ADC-V521IR' , 'ADC-VDB770', 'ADC-V523X','ADC-V723X']
    valid_doorbells = ['ADC-VDB105' , 'ADC-VDB105x' , 'SKYBELLHD' , 'SKYBELL-HD']

    iq_fw_enum = {
        '2.4.2': 'IQ_GEN2_WIFI_Update_2_4_2' ,
        '2.5.2': 'IQ_GEN2_WIFI_Update_2_5_2' ,
        '2.6.0': 'IQ_GEN2_WIFI_Update_2_6_0' ,
        '2.6.1': 'IQ_GEN2_WIFI_Update_2_6_1' ,
        '2.6.2': 'IQ_GEN2_WIFI_Update_2_6_2' ,
        'firmware2': 'IQ_GEN2_WIFI_Patch_Firmware2' ,
        # IQ4 FWV
        '4.0.1': 'IQ_GEN4_WIFI_Update_4_0_1' ,
        '4.1.0': 'IQ_GEN4_WIFI_Update_4_1_0'
    }

    panel_upgrade_attributes = ['date' , 'customer_id' , 'ecid' , 'account_status' , 'panel_type' , 'wifi_status' , 'arming_state' , 'queue_status' , 'error_message']


class _CustomerManagement:
    customer_management_wsdl = 'https://alarmadmin.alarm.com/WebServices/CustomerManagement.asmx?WSDL'
    customer_management_client = None
    customer_management_namespaces = None
    customer_management_auth = None
    connectivity_input = None
    customer_trouble_input = None
    wifi_input = None
    camera_wifi_settings_input = None
    camera_settings_input = None
    cs_test_input = None
    hard_reset_input = None
    event_history_input = None
    get_customer_list_input = None
    get_customer_info_input = None
    resolved_trouble_input = None
    add_sensor_input = None
    delete_sensor_input = None
    add_video_device_input = None
    customers_with_trouble_input = None
    advanced_wifi_stats_input = None
    video_device_info_input = None
    zwave_routing_table_input = None

    def get_latest_caller_version(self):
        output = self.customer_management_client.service.GetLatestCallerVersion(_soapheaders=[self.customer_management_auth])
        self.caller_version = zeep.helpers.serialize_object(output , target_cls=dict)

    def get_all_customers(self):
        output = self.customer_management_client.service.GetCustomerList(
            includeTermed=False ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def reboot_panel(self , customer_id):
        customer_info = self.customer_management_client.get_type(self.customer_management_namespaces + 'HardResetModuleQolsysInput')
        output = self.customer_management_client.service.HardResetModuleQolsys(input=customer_info(
            CustomerId=int(customer_id) ,
            PanelResetOption='RebootPanel'

        ) , _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def apply_panel_setting(self , customer_id , settings):
        aops = self.customer_management_client.get_type(self.customer_management_namespaces + 'ArrayOfPanelSettingInput')
        panel_settings_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'PanelSettingInput')
        desired_settings = []
        for key,value in settings.items():
            desired_settings.append(panel_settings_input(DeviceId=127 , PanelSettingId=key, NewValue=value))
        output = self.customer_management_client.service.DownloadToPanel(
            customerId=customer_id ,
            panelSettings=aops(desired_settings) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def apply_panel_template(self, customer_id, template_id):
        output = self.customer_management_client.service.ApplyPanelTemplate(
            customerId = customer_id ,
            panelTemplateId = template_id,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def get_panel_settings_info(self , cusomer_id):
        output = self.customer_management_client.service.GetUploadedPanelSettings(
            customerId=cusomer_id ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def create_test_connectivity_input(self):
        self.connectivity_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'TestVideoDeviceConnectivityInput')

    def test_video_device_connection(self , mac_addr):
        output = self.customer_management_client.service.TestVideoDeviceConnectivity(input=self.connectivity_input(
            VideoDeviceMacAddress=mac_addr) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def create_customer_trouble_input(self):
        self.customer_trouble_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'GetCustomerTroubleConditionsInput')

    def get_trouble_conditions(self , customer_id):
        output = self.customer_management_client.service.GetCustomerTroubleConditions_v2(input=self.customer_trouble_input(
            CallerVersion=self.caller_version ,
            CustomerId=customer_id ,
            IncludeDeviceDetails=True),
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def pause_analytics_input(self):
        self.analytics_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'SetVideoRecordingRuleExceptionStatusInput')

    def pause_analytics(self , customer_id, rule_id, exception_status):
        output = self.customer_management_client.service.SetVideoRecordingRuleExceptionStatus(input=self.analytics_input(
            CustomerId=customer_id ,
            RuleId=rule_id ,
            NewExceptionStatus=exception_status),
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def create_wifi_input(self):
        self.wifi_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'SetWifiInput')

    def set_wifi(self , customer_id , device_id , wifi_credentials):
        output = self.customer_management_client.service.SetWifi(input=self.wifi_input(
            CustomerId=customer_id ,
            DeviceId=device_id ,
            SSID=wifi_credentials['ssid'] ,
            Password=wifi_credentials['password'] ,
            EncryptionType=wifi_credentials['encryption'] ,
            EncryptionAlgorithm=wifi_credentials['encryption_algorithm']) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def request_available_wifi_networks(self , customer_id , device_id):
        output = self.customer_management_client.service.RequestAvailableWifiNetworkNames(
            customerId=customer_id ,
            deviceId=device_id ,
            _soapheaders=[self.customer_management_auth]
        )
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def get_available_wifi_networks(self , customer_id , device_id):
        output = self.customer_management_client.service.GetAvailableWifiNetworks(
            customerId=customer_id ,
            deviceId=device_id ,
            _soapheaders=[self.customer_management_auth]
        )
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def create_camera_wifi_settings_input(self):
        self.camera_settings_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'CameraSettings')
        self.camera_wifi_settings_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'CameraWirelessSettings')

    def set_camera_wifi(self , customer_id , mac , wifi_credentials):
        output = self.customer_management_client.service.UpdateCameraSettings(
            customerId=customer_id ,
            mac=mac ,
            settings=self.camera_settings_input(self.camera_wifi_settings_input(
                SSID=wifi_credentials['ssid'] ,
                EncryptionKey=wifi_credentials['password'] ,
                EncryptionType=wifi_credentials['encryption'] ,
                EncryptionAlgorithm=wifi_credentials['encryption_algorithm'])) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def create_hard_reset_input(self):
        self.hard_reset_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'HardResetModuleQolsysInput')

    def hard_reset_qolsys_panel(self , customer_id , panel_reset_option):
        output = self.customer_management_client.service.HardResetModuleQolsys(input=self.hard_reset_input(
            CustomerId=customer_id ,
            PanelResetOption=panel_reset_option) ,
            _soapheaders=[self.customer_management_auth]
        )
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def reset_panel_wifi(self , customer_id):
        return self.hard_reset_qolsys_panel(customer_id , 'WifiRadio')

    def get_dual_path_communication_status(self , customer_id):
        output = self.customer_management_client.service.GetDualPathCommunicationStatus(
            customerId=customer_id ,
            _soapheaders=[self.customer_management_auth]
        )
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def get_equipment_list(self , customer_id):
        try:
            response = self.customer_management_client.service.GetFullEquipmentList(
                customerId=customer_id ,
                _soapheaders=[self.customer_management_auth])
            output = zeep.helpers.serialize_object(response , target_cls=dict)
            if not output:
                return {}
            else:
                return output
        except zeep.exceptions.Fault:
            return {}

    def get_user_codes(self, customer_id):
        output = self.customer_management_client.service.GetUserCodes (
            customerId=customer_id ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def edit_master_code(self, customer_id, master_code):
        api_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'EditCustomerMasterCodeInput')
        output = self.customer_management_client.service.EditMasterCode(input=api_input(
            CustomerID=customer_id ,
            NewMasterCode=master_code) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def get_device_list(self , customer_id):
        try:
            response = self.customer_management_client.service.GetDeviceList(
                customerId=customer_id ,
                _soapheaders=[self.customer_management_auth])
            return zeep.helpers.serialize_object(response , target_cls=dict)
        except zeep.exceptions.Fault:
            return {}

    def get_device_list(self , customer_id):
        output = self.customer_management_client.service.GetDeviceList(
            customerId=customer_id ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def find_devices_in_account(self , customer_id , match , value):
        output = []
        equipment_list = self.get_equipment_list(customer_id)
        if not equipment_list:
            return output
        for equipment in equipment_list:
            if equipment[match] == value:
                output.append(equipment)
        return output

    def get_customer_video_devices(self, customer_id):
        cameras = []
        doorbells = []
        equipment_list = self.get_equipment_list(customer_id)
        if not equipment_list:
            return []
        for equipment in equipment_list:
            if equipment['VideoDeviceModel'] in self.valid_cameras:
                cameras.append(equipment)
            if equipment['VideoDeviceModel'] in self.valid_doorbells:
                doorbells.append(equipment)
        return {'doorbells':doorbells,'cameras':cameras}

    def test_cs_connectivity(self , customer_id):
        output = self.customer_management_client.service.RequestRoundTripCsTest(
            customerId=customer_id ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def create_event_history_input(self):
        self.event_history_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'GetEventHistoryInput')

    def get_event_history(self , customer_id , start_date):
        output = self.customer_management_client.service.GetEventHistory(input=self.event_history_input(
            CallerVersion=self.caller_version ,
            CustomerId=customer_id ,
            StartDate=start_date) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def update_central_station(self, customer_id, cs_info):
        api_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'UpdateCentralStationInfoInput')
        output = self.customer_management_client.service.UpdateCentralStationInfo_V2(
            input=api_input(
                CustomerId=customer_id ,
                ForwardingOption=cs_info['ForwardingOption'] ,
                PhoneLinePresent = cs_info['PhoneLinePresent'],
                EventGroupsToForward = cs_info['EventGroupsToForward'],
                AccountNumber = cs_info['AccountNumber'],
                ReceiverNumber = cs_info['ReceiverNumber'],
                InitiateTwoWayVoiceForFireAndCoAlarms = cs_info['TwoWayVoiceEnabled'],
                DualPathSupervisionImmediate = cs_info['DualPathSupervisionImmediate']
            ),
            _soapheaders=[self.customer_management_auth]
        )
        return zeep.helpers.serialize_object(output , target_cls=dict)


class _DealerManagement:
    dealer_management_wsdl = 'https://alarmadmin.alarm.com/webservices/DealerManagement.asmx?WSDL'
    dealer_management_client = None
    dealer_management_namespaces = None
    dealer_management_auth = None

    def get_rep_info(self, credentials):
        api_input = self.dealer_management_client.get_type(self.dealer_management_namespaces + 'GetCurrentRepInfoInput')
        output = self.dealer_management_client.service.GetCurrentRepInfo(input=api_input(
            RepLogin=credentials['login'] ,
            RepPassword=credentials['passphrase'] ,
            RepId=None) ,
            _soapheaders=[self.dealer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def get_rep_list(self):
        output = self.dealer_management_client.service.GetRepList(_soapheaders=[self.dealer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def get_package_ids(self, account_type):
        get_package_id_input = self.dealer_management_client.get_type(self.dealer_management_namespaces + 'GetPackageIdsInput')
        output = self.dealer_management_client.service.GetPackageIds(
            input=get_package_id_input(
                DealerId=self.dealer_id,
                accountType=account_type,
                CallerVersion=self.caller_version
            ),
            _soapheaders=[self.dealer_management_auth]
        )
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def get_cs_receivers(self):
        output = self.dealer_management_client.service.GetCSPhoneNumber (_soapheaders=[self.dealer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)


class _VideoFirmwareUpgrade:
    video_firmware_upgrade_wsdl = 'https://alarmadmin.alarm.com/WebServices/VideoFirmwareUpgrade.asmx?WSDL'
    video_firmware_upgrade_client = None
    video_firmware_upgrade_namespaces = None
    video_firmware_upgrade_auth = None

    def get_video_device_upgrade_history(self , customer_id , device_id):
        output = self.video_firmware_upgrade_client.service.GetVideoDeviceUpgradeHistory(
            customerId=customer_id ,
            deviceId=device_id ,
            _soapheaders=[self.video_firmware_upgrade_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def upgrade_video_device(self , customer_id , device_id , target_fw):
        output = self.video_firmware_upgrade_client.service.UpgradeVideoDevice(
            customerId=int(customer_id) ,
            deviceId=int(device_id) ,
            targetFirmware=target_fw ,
            _soapheaders=[self.video_firmware_upgrade_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def create_customer_list_input(self):
        self.get_customer_list_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'GetCustomerListInput')

    def get_customer_list(self , search_criteria):
        output = self.customer_management_client.service.GetCustomerList_V2(input=self.get_customer_list_input(
            IncludeTermed=False ,
            # AlternateId=search_criteria['alternate_id'],
            StartDate=search_criteria['start_date'] ,
            EndDate=search_criteria['end_date'] ,
            ExcludeCommitments=True ,
            ExcludeCustomers=False) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def get_customers_with_panel_fw(self, panel_versions):
        output = self.customer_management_client.service.GetCustomerList_V2(input=self.get_customer_list_input(
            IncludeTermed=False ,
            #StartDate=False ,
            #EndDate=False ,
            ExcludeCommitments=True ,
            ExcludeCustomers=False ,
            PanelVersions={'PanelVersionEnum':panel_versions}),
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def get_panel_serialnumbers(self , customer_list):
        final_output = []
        fail_count = 0
        c_counter = 1
        for customer in customer_list:
            try:
                a = self.get_panel_settings_info(int(customer.rstrip()))['Settings']['UploadedPanelSetting']
                serial_number = next((x for x in a if x['PanelSettingId'] == 20000228) , "")['UploadedValueRaw']
                serial_number = serial_number if serial_number else ""
                final_output.append([customer , serial_number])
            except Exception:
                fail_count += 1
                with open('error_' + self.log_file , "a") as f:
                    f.write(customer + "\n")
                continue
            if c_counter % 101 == 0:
                time.sleep(random.randint(1 , 20))
                self.write_to_file(final_output)
                final_output = []
                c_counter = 1
            c_counter += 1
        time.sleep(random.randint(1 , 20))
        self.write_to_file(final_output)
        return True

    def create_customer_info_input(self):
        self.get_customer_info_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'GetCustomerInfoInput')

    def get_customer_info(self , customer_id):
        output = self.customer_management_client.service.GetCustomerInfo_V2(input=self.get_customer_info_input(
            CallerVersion=int(self.caller_version) ,
            CustomerId=int(customer_id)) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def create_resolved_troubles_input(self):
        self.resolved_trouble_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'GetResolvedTroubleConditionsCsvInput')

    def get_resolved_trouble_conditions(self , customer_id):
        output = self.customer_management_client.service.GetResolvedTroubleConditionsCsv(input=self.resolved_trouble_input(
            CallerVersion=int(self.caller_version) ,
            CustomerId=int(customer_id),
            IncludeDeviceDetails=False) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def get_resolved_troubles(self , customer_list):
        final_output = []
        fail_count = 0
        c_counter = 1
        attributes = ['customer_id','device_id','short_description','trouble_condition_type','end_date_utc','device_name','device_type','device_model']
        final_output.append(attributes)
        for customer in tqdm(customer_list):
            customer_id = int(customer.rstrip())
            try:
                resolved_troubles = self.get_resolved_trouble_conditions(customer_id)
                equipment_list = self.get_equipment_list(customer_id)
                if resolved_troubles['CsvData']:
                    resolved_troubles = list(csv.reader(resolved_troubles['CsvData'].splitlines() , delimiter=','))
                    resolved_troubles.pop(0)
                    for trouble in resolved_troubles:
                        trouble.pop(-1)
                        device_id = trouble[1]
                        device = (next((item for item in equipment_list if item["DeviceId"] == int(device_id)) , None))
                        if device:
                            device_details = [
                                device['WebSiteDeviceName'],
                                device['DeviceType'],
                                device['VideoDeviceModel'] if device['VideoDeviceModel'] else 'None'
                            ]
                            trouble = trouble + device_details
                        final_output.append(trouble)
                else:
                    final_output.append(str(customer)+',,,,,')
            except Exception:
                fail_count += 1
                with open('error_' + self.log_file , "a") as f:
                    f.write(customer + "\n")
                continue
            if c_counter % 51 == 0:
                time.sleep(random.randint(1 , 20))
                self.write_to_file(final_output)
                final_output = []
                c_counter = 1
            c_counter += 1
        self.write_to_file(final_output)
        return True

    def create_add_sensor_input(self):
        self.add_sensor_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'AddSensorDeviceInput')

    def add_sensor(self , customer_id , sensor_info , partition=None):
        if not partition:
            partition = 1
        # map water sensor type 15 to 23
        if sensor_info['sensor_type_id'] == 15:
            sensor_info['sensor_type_id'] = 23
        output = self.customer_management_client.service.AddSensorDevice(input=self.add_sensor_input(
            CustomerId=int(customer_id) ,
            SensorId=int(sensor_info['sensor_id']) ,
            GroupId=int(sensor_info['group_id']) ,
            SensorName=sensor_info['sensor_name'] ,
            SensorTypeId=int(sensor_info['sensor_type_id']) ,
            SignalSourceId=int(sensor_info['signal_src']) ,
            Partition=partition ,
            DLCode=sensor_info['dlcode']) , _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def delete_sensor(self , customer_id , sensor_id):
        output = self.customer_management_client.service.DeleteSensorDevice(input=self.delete_sensor_input(
            CustomerId=customer_id ,
            SensorId=sensor_id) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def update_sensor_name(self , customer_id , sensor_info):
        api_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'UpdateSensorDeviceInput')
        output = self.customer_management_client.service.UpdateSensorDevice(input=api_input(
            CustomerId=customer_id ,
            SensorId=sensor_info['sensor_id'] ,
            GroupId=sensor_info['group_id'] ,
            SensorName=sensor_info['new_name']) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def delete_all_security_sensors(self , customer_id):
        equipment = self.get_equipment_list(customer_id)
        output = []
        for device in equipment:
            if 0 < device['DeviceId'] < 128:
                res = self.delete_sensor(customer_id , device['DeviceId'])
                output.append({'SensorName': device['WebSiteDeviceName'] , 'Deleted': res['Success']})
        return output

    def get_all_zwave_devices(self , customer_id):
        equipment = self.get_equipment_list(customer_id)
        output = []
        for device in equipment:
            if 1200 <= device['DeviceId'] <= 1260:
                output.append(device)
        return output

    def get_all_security_sensors(self, customer_id, dlid=True):
        sensor_attributes = {'sensor_name': 'Sensor Name' , 'sensor_group_id': 'Sensor Group' , 'sensor_type': 'Sensor Type' , 'partition': 'Partition' , 'source': 'Signal Source' , 'dlid': 'DL Code'}
        if not dlid:
            del(sensor_attributes['dlid'])
        equipment = self.get_equipment_list(customer_id)
        res = self.get_panel_settings_info(customer_id)
        if not res['Success'] or not res['Settings']:
            return False
        panel_settings = res['Settings']['UploadedPanelSetting']
        output = []
        for device in equipment:
            if 0 < device['DeviceId'] < 127:
                sensor = {}
                sensor['device_id'] = device['DeviceId']
                for key, value in sensor_attributes.items():
                    if key == 'dlid' or key == 'partition':
                        attribute = 'UploadedValueDesc'
                    else:
                        attribute = 'UploadedValueRaw'
                    uploaded_attribute = next((item for item in panel_settings if (item['DeviceId'] == device['DeviceId'] and item['PanelSettingName'] == value)), False)
                    if not uploaded_attribute:
                        value = ""
                    else:
                        value = uploaded_attribute[attribute]
                    sensor[key] = value
                output.append(sensor)
        return output

    def get_all_video_devices(self , customer_id):
        equipment = self.get_equipment_list(int(customer_id))
        output = []
        for device in equipment:
            if 2048 <= device['DeviceId'] <= 2088:
                output.append(device)
        return output

    def delete_all_peripherals(self , customer_id):
        equipment = self.get_equipment_list(customer_id)
        output = []
        for device in equipment:
            if 5500 < device['DeviceId'] < 5600:
                res = self.delete_sensor(customer_id , device['DeviceId'])
                output.append({'SensorName': device['WebSiteDeviceName'] , 'Deleted': res['Success']})
        return output

    def create_delete_sensor_input(self):
        self.delete_sensor_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'DeleteSensorDeviceInput')

    def upgrade_qolsys_panel_api(self , customer_id , target_fw):
        output = self.customer_management_client.service.RequestFirmwareUpgradeQolsys(
            customerId=customer_id ,
            newVersion=self.iq_fw_enum[target_fw] ,
            timeToUpdate=datetime.now() + timedelta(minutes=1) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def upgrade_qolsys_panel(self,customer, target_fw, model):
        start_time = datetime.now().isoformat()
        output = []
        try:
            output.append(start_time)
            output.append(str(customer['CustomerId']))
            if customer['IsTerminated']:
                return dict(zip(self.panel_upgrade_attributes,output + ['Terminated' , '' , '' , '' , '' , '']))
            output.append(str(customer['DealerCustomerId']))
            panel_type = customer['ModemInfo']['PanelType']
            if panel_type != model:
                return dict(zip(self.panel_upgrade_attributes,output + ['Active' , panel_type , '' , '' , '' , '']))
            if target_fw in customer['DetailedPanelVersion']:
                return dict(zip(self.panel_upgrade_attributes,output + ['Active' , panel_type , '' , '' , '' , 'Upgrade not required']))
            dual_path_status = self.get_dual_path_communication_status(customer['CustomerId'])
            wifi_status = dual_path_status['CommunicationStatus']['DualEthernetWorking']
            if not wifi_status:
                return dict(zip(self.panel_upgrade_attributes, output + ['Active' , panel_type , 'Down' , '' , '' , '']))
            res = self.get_equipment_list(customer['CustomerId'])
            panel = next(
                (
                    res[index] for (index , d) in enumerate(res) if d["DeviceId"] == 127
                ) ,
                None
            )
            panel_status = panel['Status']['DeviceStatusEnum'][0]
            result = self.upgrade_qolsys_panel_api(customer['CustomerId'] , target_fw)
            return dict(zip(self.panel_upgrade_attributes,output + ['Active', panel_type, 'Up', panel_status, 'Success' if result['Success'] else 'Fail', str(result['ErrorMessage'])]))
        except Exception as e:
            print(e)
            return output.append(str(e))

    def bulk_upgrade_qolsys_panels(self , customer_ids , target_fw, model):
        self.create_customer_info_input()
        self.get_latest_caller_version()
        final_output = []
        # customer_id, account_status, wifi_status, queue_status, error_message
        for customer_id in tqdm(customer_ids):
            customer = self.validate_customer(customer_id)
            if customer_id:
                final_output.append(self.upgrade_qolsys_panel(customer, target_fw, model))
        return final_output

    def create_add_video_device_input(self):
        self.add_video_device_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'AddVideoDeviceInput')

    def add_video_device(self , customer_id , mac):
        output = self.customer_management_client.service.AddVideoDevice(input=self.add_video_device_input(
            CustomerId=customer_id ,
            VideoDeviceMacAddress=mac) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def request_fwv_cmd(self , customer_id):
        output = self.customer_management_client.service.RequestFirmwareVersionCommand(
            customerId=customer_id ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def create_customers_with_trouble_input(self):
        self.customers_with_trouble_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'GetCustomerListWithTroubleConditionsInput')

    def get_customers_with_trouble(self , troubles):
        output = self.customer_management_client.service.GetCustomerListWithTroubleConditionsCsv_v2(input=self.customers_with_trouble_input(
            CallerVersion=self.caller_version ,
            Conditions=troubles) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def get_customer_from_modem_serial(self , serial_num):
        output = self.customer_management_client.service.LookupCustomerIdFromModemSerial(
            modemSerial=serial_num ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def get_customer_risk_scores(self , customer_id=None):
        customer_risk_score_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'GetCustomerRiskScoreDataInput')
        output = self.customer_management_client.service.GetCustomerRiskScoreData(input=customer_risk_score_input(
            CustomerId=customer_id) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def update_customer_ready_date(self, customer_id, date):
        api_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'UpdateCustomerReadyDateInput')
        output = self.customer_management_client.service.UpdateCustomerReadyDate(input=api_input(
            CustomerId=customer_id,
            ReadyDateUtc=date) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def update_commitment(self, customer_id, panel_type):
        api_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'UpdateCommitmentInput')
        output = self.customer_management_client.service.UpdateCommitment(input=api_input(
            CommitmentId=customer_id ,
            ExpectedPanelType=panel_type) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def get_customer_list_with_panel_setting(self , search_criteria):
        customer_panel_settings_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'GetCustomerListWithPanelSettingInput')
        array_panel_settings_criteria = self.customer_management_client.get_type(self.customer_management_namespaces + 'ArrayOfPanelSettingCriteria')
        search_query = array_panel_settings_criteria(search_criteria)
        output = self.customer_management_client.service.GetCustomerListWithPanelSetting(input=customer_panel_settings_input(
            Criteria=search_query) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def get_downloadable_settings(self , customer_id , device_id):
        output = self.customer_management_client.service.GetDownloadableSettings(
            customerId=customer_id ,
            deviceId=device_id ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def create_advanced_wifi_stats_input(self):
        self.advanced_wifi_stats_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'GetAdvancedWifiStatsForVideoDeviceInput')

    def get_advanced_wifi_stats(self , customer_id , device_id):
        output = self.customer_management_client.service.GetAdvancedWifiStatsForVideoDevice(input=self.advanced_wifi_stats_input(
            CustomerId=int(customer_id) ,
            DeviceId=int(device_id)) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def create_video_device_info_input(self):
        self.video_device_info_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'GetVideoDeviceInfoInput')

    def get_video_device_info(self , customer_id):
        output = self.customer_management_client.service.GetVideoDeviceInfo(input=self.video_device_info_input(
            CustomerId=customer_id) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def get_video_analytics_info(self, customer_id):
        api_input = {'CustomerId': customer_id}
        output = self.customer_management_client.service.GetVideoAnalyticsRulesInfo (
            input=api_input,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def get_video_recording_rules(self, customer_id):
        api_input = {'CustomerId': customer_id}
        output = self.customer_management_client.service.GetVideoRecordingRuleList(
            input=api_input ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def create_zwave_routing_table_input(self):
        self.zwave_routing_table_input = self.advanced_wifi_stats_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'GetZWaveRoutingTableInput')

    def get_zwave_routing_table(self , customer_id):
        output = self.customer_management_client.service.GetZWaveRoutingTable(input=self.zwave_routing_table_input(
            CustomerId=customer_id) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def request_updated_equipment_list(self , customer_id):
        output = self.customer_management_client.service.RequestUpdatedEquipmentList(
            customerId=customer_id ,
            maxZones=128 ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def request_upload_of_panel_settings(self, customer_id, device_id):
        output = self.customer_management_client.service.RequestUploadOfPanelSettings(
            customerId=customer_id ,
            deviceId=device_id ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def request_updated_zwave_equipment_list(self, customer_id):
        output = self.customer_management_client.service.RequestZWaveEquipmentList (
            customerId=customer_id ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def request_sensor_names(self , customer_id):
        output = self.customer_management_client.service.RequestSensorNames(
            customerId=customer_id ,
            waitUntilPanelConnects=False ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def add_user_code(self , customer_id , user_info , partition=1):
        api_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'AddUserCodeInput')
        output = self.customer_management_client.service.AddUserCode(input=api_input(
            CustomerId=customer_id ,
            UserFirstName=user_info['first_name'] ,
            UserLastName=user_info['last_name'] ,
            NewUserCode=user_info['pin'] ,
            VoiceAccess=False ,
            PartitionFlags=partition) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def edit_user_code(self, customer_id, user_code_info):
        api_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'EditUserCodeInput')
        output = self.customer_management_client.service.EditUserCode(input=api_input(
            CustomerId=customer_id ,
            PanelUserId=user_code_info['user_id'],
            UserFirstName=user_code_info['first_name'] ,
            UserLastName=user_code_info['last_name'] ,
            NewUserCode=user_code_info['pin'] ,
            VoiceAccess=user_code_info['voice_access'],
            PartitionFlags=user_code_info['partition'],
            DeleteAdcUserProfile = False) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def delete_user_code(self, customer_id, user_code_info):
        api_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'EditUserCodeInput')
        output = self.customer_management_client.service.EditUserCode(input=api_input(
            CustomerId=customer_id ,
            PanelUserId=user_code_info['user_id'] ,
            NewUserCode= None,
            VoiceAccess=user_code_info['voice_access'] ,
            PartitionFlags=user_code_info['partition'] ,
            DeleteAdcUserProfile=True) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def delete_all_user_codes(self,customer_id):
        user_codes = self.get_user_codes(customer_id)['UserCodes']['WsUserCodeInfo']
        # Add user codes to database
        for code in user_codes:
            if code['panelUserId'] == 1:
                continue
            user_code_info = {
                'user_id': code['panelUserId'] ,
                'voice_access': code['voiceAccess'] ,
                'partition': code['partitionFlags']
            }
            self.delete_user_code(customer_id , user_code_info)

    def delete_customer_login(self , customer_id , login_id):
        api_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'DeleteCustomerLoginInput')
        output = self.customer_management_client.service.DeleteCustomerLogin(input=api_input(
            CustomerId=customer_id ,
            LoginIdToDelete=login_id) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def swap_modem(self , customer_id , new_sn , swap_reason):
        api_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'SwapModemInput')
        output = self.customer_management_client.service.SwapModem(input=api_input(
            NewSerialNumber=new_sn ,
            SwapReason=swap_reason ,
            SpecialRequest="" ,
            CustomerId=customer_id ,
            RestoreBackedUpSettingsAfterSwap=False ,
            RestoreNetworkAfterSwap=False) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def get_uploaded_panel_settings(self, customer_id):
        output = self.customer_management_client.service.GetUploadedPanelSettings(
            customerId=customer_id ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def validate_customer(self, customer_id):
        if not str(customer_id).isnumeric():
            return False
        try:
            customer_info = self.get_customer_info(int(customer_id))
            if customer_info['IsTerminated']:
                return False
        except Exception as e:
            # print(f'Failed to get customer info for {str(customer_id)}')
            # print(e)
            return False
        return customer_info

    def validate_customer_login_credentials(self, credentials):
        api_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'ValidateLoginPasswordInput')
        output = self.customer_management_client.service.ValidateLoginPassword_v2(input=api_input(
            LoginName=credentials['login'] ,
            Password=credentials['passphrase'] ,
            RecordAsLoginEvent=True ,
            CallerVersion=self.caller_version) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def get_sim_status(self,imei):
        api_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'GetSimStatusDuringActivationInput')
        output = self.customer_management_client.service.GetSimStatusDuringActivation(input=api_input(
            ModemSerial=imei) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def activate_commitment(self, commitment_id, panel_type, imei):
        api_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'ActivateCommitmentInput')
        output = self.customer_management_client.service.ActivateCommitment(input=api_input(
            CommitmentId=commitment_id,
            PanelType = panel_type,
            ModemSerialNumber = imei,
            IgnoreLowCoverageErrors = False,
            IsInstalledByExpectedInstaller = False,
            UsingADCApp = False) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def create_customer_message(self,**kwargs ):
        api_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'CreateNewCustomerWebsiteMessageInput')
        output = self.customer_management_client.service.CreateNewCustomerWebsiteMessage (input=api_input(
            CustomerId=kwargs['customer_id'] ,
            LoginId=kwargs['login_id'] ,
            PermissionToView='CompleteCustomerControl' ,
            PermissionValueToView='ReadWrite' ,
            PermissionToClear='CompleteCustomerControl' ,
            PermissionValueToClear='ReadWrite',
            MessageId=kwargs['message_id'] ,
            Parameters=[] ,
            StartDateUtc=kwargs['start_date'] ,
            ValidUntilDateUtc=kwargs['end_date'] ,
            ClearingOption = 'PerLogin'
        ) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def change_service_plan(self, customer_id, package_id, addons):
        output = self.customer_management_client.service.ChangeServicePlan(
            customerId=customer_id ,
            newPackageId=package_id ,
            addOnFeatures=addons ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def validate_new_service_plan(self, customer_id, package_id, addons):
        output = self.customer_management_client.service.ChangeServicePlanValidationOnly(
            customerId=customer_id ,
            newPackageId=package_id ,
            addOnFeatures=addons ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def activate_modem(self, imei):
        output = self.customer_management_client.service.ActivateModem(
            modemSerial=imei ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def get_login_info(self, login_id):
        api_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'GetLoginInfoInput')
        output = self.customer_management_client.service.GetLoginInfo (input = api_input(
            LoginId=login_id) ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def get_all_logins(self, customer_id):
        output = self.customer_management_client.service.GetAllLogins_V2(
            customerId=customer_id ,
            _soapheaders=[self.customer_management_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)

    def create_scheduled_appointment(self, customer_id, appointment_details):
        api_input = self.customer_management_client.get_type(self.customer_management_namespaces + 'CreateScheduledAppointmentInputV2')
        output = self.customer_manage_client.service.CreateScheduledAppointmentV2(
            input = api_input(
                CustomerId = int(customer_id),
                DateUtc = appointment_details['date'],
                TechnicianId = appointment_details['rep_ip'],
                Confirmation = False,
                Reminder = False,
            )
        )


class _Validate:
    validate_wsdl = 'https://alarmadmin.alarm.com/webservices/Validate.asmx?WSDL'
    validate_client = None
    validate_namespaces = None
    validate_auth = None

    def validate_panel_imei(self, imei):
        output = self.validate_client.service.ValidateSerialNumber(
            serialNumber=imei ,
            _soapheaders=[self.validate_auth])
        return zeep.helpers.serialize_object(output , target_cls=dict)


# Object to handle ADC APIs
class WebServicesAPI(_AdcWebServices, _DealerManagement, _CustomerManagement, _VideoFirmwareUpgrade, _Validate):
    def __init__(self , dealer_id , log_file=None):
        super()
        if log_file:
            self.log_file = log_file
        self.dealer_id = dealer_id
        self.credentials = CredentialsManager(dealer_id)

    def authenticate(self , wsdl="CustomerManagement"):
        session = Session()
        if self.use_proxy:
            session.proxies = self.proxies
        transport = Transport(session=session)
        if wsdl == "CustomerManagement":
            self.customer_management_client = Client(wsdl=self.customer_management_wsdl, transport = transport)
            self.customer_management_namespaces = '{' + self.customer_management_client.namespaces['ns0'] + '}'
            self.customer_management_auth = self.customer_management_client.get_element(self.customer_management_namespaces + 'Authentication')(User=self.credentials.user , Password=self.credentials.password , TwoFactorDeviceId='E2FD7F0875D9A23FD3A00C087CC033F69494AF7F5C9F80EAE0A896F006092F39')
        elif wsdl == "VideoFirmwareUpgrade":
            self.video_firmware_upgrade_client = Client(wsdl=self.video_firmware_upgrade_wsdl, transport = transport)
            self.video_firmware_upgrade_namespaces = '{' + self.video_firmware_upgrade_client.namespaces['ns0'] + '}'
            self.video_firmware_upgrade_auth = self.video_firmware_upgrade_client.get_element(self.video_firmware_upgrade_namespaces + 'Authentication')(User=self.credentials.user , Password=self.credentials.password , TwoFactorDeviceId='')
        elif wsdl == "DealerManagement":
            self.dealer_management_client = Client(wsdl=self.dealer_management_wsdl, transport = transport)
            self.dealer_management_namespaces = '{' + self.dealer_management_client.namespaces['ns0'] + '}'
            self.dealer_management_auth = self.dealer_management_client.get_element(self.dealer_management_namespaces + 'Authentication')(User=self.credentials.user , Password=self.credentials.password , TwoFactorDeviceId='')
        elif wsdl == "Validate":
            self.validate_client = Client(wsdl=self.validate_wsdl, transport = transport)
            self.validate_namespaces = '{' + self.validate_client.namespaces['ns0'] + '}'
            self.validate_auth = self.validate_client.get_element(self.validate_namespaces + 'Authentication')(User=self.credentials.user , Password=self.credentials.password , TwoFactorDeviceId='')

    def write_to_file(self , data_array):
        with open(self.log_file , "a") as f:
            for data in data_array:
                if self.result_obj_type == 'dict':
                    data = list(data.values())
                if self.console_log:
                    print(",".join(data))
                f.write(",".join(data) + "\n")