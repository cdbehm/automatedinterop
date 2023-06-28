# import libraries
import time
import json
from lxml import html
from datetime import datetime
import requests
import random
import mysql.connector
from CredentialsManager import CredentialsManager
from WebServicesAPI import WebServicesAPI
import traceback
from tqdm import tqdm


class WebServicesHTTP(object):
    start_time = None
    credentials = None
    log_file = None
    time_stamp_format = None
    dealer_id = None
    WebServicesAPI = None
    session = None
    proxies = {'http': 'http://abe-elkdmz-01:443', 'https': 'http://abe-elkdmz-01:443'}
    22
    proxy = False

    def __init__(self , dealer_id , log_file=None):
        self.dealer_id = dealer_id
        self.credentials = CredentialsManager(dealer_id)
        if log_file:
            self.log_file = log_file
        if dealer_id == 15525:
            self.time_stamp_format = "%Y-%m-%d %I:%M %p"
        elif dealer_id == 17233:
            self.time_stamp_format = "%Y-%m-%d %I:%M %p"
        elif dealer_id == 343:
            self.time_stamp_format = "%Y-%m-%d %I:%M %p"
        elif dealer_id == 915525:
            self.time_stamp_format = "%m/%d/%Y %I:%M %p"
        else:
            print('Invalid dealer id')
        self.start_time = datetime.now().strftime("%Y-%m-%d")

    def login(self):
        self.session = requests.Session()
        self.session.max_redirects = 5
        if self.proxy:
            self.session.proxies.update(self.proxies)
        p = self.session.get('https://alarmadmin.alarm.com')
        tree = html.fromstring(p.text)
        view_state = tree.xpath('//input[@name="__VIEWSTATE"]/@value')
        event_validation = tree.xpath('//input[@name="__EVENTVALIDATION"]/@value')
        payload = {
            "txtUsername": self.credentials.user ,
            "txtPassword": self.credentials.password ,
            "butLogin": 'Login' ,
            "__VIEWSTATEGENERATOR": "CA0B0334" ,  # 02F837B7 for ADT by TELUS, CA0B0334 for TELUS SHS
            "__VIEWSTATE": view_state[0] ,
            "__EVENTVALIDATION": event_validation[0] ,
            "__EVENTTARGET": "" ,
            "__EVENTARGUMENT": "" ,
            "__VIEWSTATEENCRYPTED": ""
        }
        self.session.post('https://alarmadmin.alarm.com' , data=payload)

    def validate_login(self):
        p = self.session.get('https://alarmadmin.alarm.com/ManageDealer/RepProfile')
        tree = html.fromstring(p.text)
        try:
            login_status = tree.xpath('//div[@class="div-login-status"]//text()')[0].strip().lower()
            if login_status=="active":
                return True
        except:
            return False
        return False

    def create_adc_webservices_api(self):
        self.WebServicesAPI = WebServicesAPI(self.dealer_id)
        self.WebServicesAPI.authenticate()

    def write_to_file(self , data_array , log=False):
        if log:
            log_file = log
        else:
            log_file = self.log_file
        for data in data_array:
            print(",".join(data))
        if self.log_file:
            for data in data_array:
                with open(log_file , "a" , encoding='utf-8') as f:
                    f.write(",".join(data) + "\n")

    def convert_timestamp(self , date_string):
        if date_string == "Never":
            return ''
        else:
            date_string = date_string.replace(' (EDT)' , '')
            date_string = date_string.replace(' (PST)' , '')
            date_string = date_string.replace(' (EST)' , '')
            date_string = date_string.replace(' (MST)' , '')
            date_string = date_string.replace(' (MDT)' , '')
            try:
                date = datetime.strptime(date_string.upper() , self.time_stamp_format)
                return date.strftime("%Y-%m-%d %H:%M:%S")
            except Exception as e:
                self.time_stamp_format = "%m/%d/%Y %I:%M %p"
                print(f'{e.args[0]} - Updating timestamp format to {self.time_stamp_format}')
                date = datetime.strptime(date_string.upper(), self.time_stamp_format)
                return date.strftime("%Y-%m-%d %H:%M:%S")

    def get_camera_info(self , camera_list, input_cam, testtime, get_rssi=True, track_progress=False):
        final_output = []
        fail_count = 0
        if get_rssi:
            webapi = WebServicesAPI(self.dealer_id)
            webapi.authenticate()
            webapi.create_advanced_wifi_stats_input()
        c_counter = 1
        error_count = 0
        max_error_count = round(0.05*len(camera_list))
        if track_progress:
            pbar = tqdm(total=len(camera_list))
        for camera in camera_list:
            if error_count > max_error_count:
                break
            url = 'https://alarmadmin.alarm.com/Support/CameraInfo.aspx?customer_id=' + camera[0] + '&device_id=' + \
                  camera[1]
            try:
                a = self.session.get(url)
                tree = html.fromstring(a.text)
                output = [""] * 45
                output[0] = self.start_time
                output[1] = camera[0]  # customer ID
                print(output)
                output[2] = tree.xpath('//td[contains(text(),"Model")]//following-sibling::td//span/text()')[0]  # Model
                output[3] = self.convert_timestamp(tree.xpath('//td[contains(text(),"Install Date")]/following-sibling::td//span/text()')[0])  # Install Date
                output[4] = tree.xpath('//td[contains(text(),"MAC")]/following-sibling::td//span/text()')[0]  # MAC
                output[5] = tree.xpath('//td[contains(text(),"Device ID")]/following-sibling::td//span/text()')[0]  # Device ID
                output[6] = tree.xpath('//td[contains(text(),"External IP")]/following-sibling::td//span/text()')[0]  # External IP
                output[7] = tree.xpath('//span[@id="ctl00_phBody_lblPort"]/text()')[0]  # Port
                output[8] = tree.xpath('//span[@id="ctl00_phBody_lblHttpsPort"]/text()')[0]  # HTTPS Port
                output[9] = tree.xpath('//span[@id="ctl00_phBody_lblRTSPPort"]/text()')[0]  # RTSP Port
                output[10] = tree.xpath('//span[@id="ctl00_phBody_lblInternalIP"]/text()')[0]  # Internal IP
                output[11] = "Yes"  # HTTPS Enabled
                output[12] = tree.xpath('//span[@id="ctl00_phBody_lblStreamingMethod"]/text()')[0]  # Streaming Enabled
                try:
                    output[13] = tree.xpath('//span[@id="ctl00_phBody_SSIDLabel"]/text()')[0].replace(',' , '')  # Wireless SSID
                except:
                    output[13] = ''
                output[14] = tree.xpath('//td[contains(text(),"Encryption")]//following-sibling::td//span/text()')[0]  # Encryption Type
                # Wireless SNR
                try:
                    output[15] = tree.xpath('//td[contains(text(),"Wireless Signal-To-Noise Ratio")]//following-sibling::td//span/text()')[0].replace(' dB' , '')
                except Exception:
                    output[15] = ""
                # Wireless TX Rate
                try:
                    output[16] = tree.xpath('//td[contains(text(),"Wireless Tx Rate")]//following-sibling::td//span/text()')[0].replace(' Mbps' , '')
                except Exception:
                    output[16] = ""
                # Wireless Frequency Band
                try:
                    output[17] = tree.xpath('//td[contains(text(),"Wireless Frequency Band")]//following-sibling::td//span/text()')[0]
                except Exception:
                    output[17] = ""
                # Wireless Frequency Channel
                try:
                    output[18] = tree.xpath('//td[contains(text(),"Wireless Frequency Channel")]//following-sibling::td//span/text()')[0]
                except Exception:
                    output[18] = ""
                output[19] = tree.xpath('//td[contains(text(),"Record Resolution")]//following-sibling::td//span/text()')[0]  # Record Resolution
                output[20] = tree.xpath('//td[contains(text(),"Record Quality")]//following-sibling::td//span/text()')[0]  # Record Quality
                output[21] = tree.xpath('//input[@id="ctl00_phBody_cbImageFlipped"]/@disabled')[0]  # Image Flipped
                output[22] = self.convert_timestamp(tree.xpath('//td[contains(text(),"Last Bootup")]//following-sibling::td//span/text()')[0])  # Last Bootup
                output[23] = self.convert_timestamp(tree.xpath('//td[contains(text(),"Last DDNS Update")]/following-sibling::td//span/text()')[0])  # Last DDNS Update
                output[24] = tree.xpath('//td[contains(text(),"Average time between DDNS updates")]//following-sibling::td//span/text()')[0]  # Average time between DDNS Updates
                output[25] = tree.xpath('//td[contains(text(),"Average time between VPN updates")]//following-sibling::td//span/text()')[0]  # Average time between VPN updates
                output[26] = self.convert_timestamp(tree.xpath('//span[@id="ctl00_phBody_lblLastUploadTime"]/text()')[0])  # Last Video Upload
                output[27] = tree.xpath('//span[@id="ctl00_phBody_lblNumOfRecordingSchedules"]/text()')[0]  # Number of recording schedules
                output[28] = self.convert_timestamp(tree.xpath('//td[contains(text(),"Last Supervision Attempt")]/following-sibling::td//span/text()')[0])  # Last Supervision Attempt
                output[29] = self.convert_timestamp(tree.xpath('//td[contains(text(),"Last Successful Supervision")]/following-sibling::td//span/text()')[0])  # Last Successful Supervision
                output[30] = self.convert_timestamp(tree.xpath('//td[contains(text(),"Last Failed Supervision")]/following-sibling::td//span/text()')[0])  # Last Failed Supervision
                output[31] = tree.xpath('//td[contains(text(),"Successful Supervision Attempts in 24 hrs")]/following-sibling::td//span/text()')[0].replace('%' , '')  # Successful Supervision Attempts in 24 hrs
                output[32] = tree.xpath('//td[contains(text(),"Stored Clips (all cameras)")]/following-sibling::td//span/text()')[0].replace(' Clips' , '').replace("," , "")  # Stored Clips
                output[33] = tree.xpath('//td[contains(text(),"Storage Quota (all cameras)")]/following-sibling::td//span/text()')[0].replace(' Clips' , '').replace("," , "")  # Storage Quota
                output[34] = tree.xpath('//td[contains(text(),"Monthly Upload Quota (all cameras)")]/following-sibling::td//span/text()')[0].replace(' Clips' , '').replace("," , "")  # Monthly Upload Quota
                output[35] = tree.xpath('//td[contains(text(),"Total uploads this month (all cameras)")]/following-sibling::td//span/text()')[0].replace(' Clips' , '').replace("," , "")  # Total uploads this month
                output[36] = tree.xpath('//span[@id="ctl00_phBody_ucsFirmwareUpgrade_lblFirmwareVer"]/text()')[0]  # Firmware Version
                output[37] = ""
                output[38] = ""
                output[39] = ""
                output[40] = ""
                output[41] = ""
                output[42] = ""
                try:
                    if "No SD cards were found" not in tree.xpath('//table[@id="ctl00_phBody_SdCardDbRowsAlarmDataGrid"]//span//text()')[0]:
                        sd_card_info = tree.xpath('//table[@id="ctl00_phBody_SdCardDbRowsAlarmDataGrid"]//tr')[1]
                        sd_card_data = sd_card_info.xpath('.//td//text()')
                        output[37] = sd_card_data[0]
                        output[38] = sd_card_data[1]
                        output[39] = sd_card_data[2]
                        output[40] = sd_card_data[3]
                        output[41] = sd_card_data[4]
                        output[42] = sd_card_data[5]
                except:
                    None
                if output[2] == 'ADC-VDB770':
                    output[43] = tree.xpath('//select[@id="ctl00_phBody_chimeTypeDropDown"]//option[@selected]/text()')[0]
                    output[44] = tree.xpath('//td[contains(text(),"Battery Voltage")]/following-sibling::td//span/text()')[0]
                if get_rssi:
                    rssi_info = webapi.get_advanced_wifi_stats(camera[0], camera[1])
                    if rssi_info['Success']:
                        output.append(str(rssi_info['Stats']['NormalizedSignalStrength']))
                        output.append(str(rssi_info['Stats']['SNR']))
                        output.append(str(rssi_info['Stats']['RSSI']))
                        output.append(str(rssi_info['Stats']['TxRate']))
                    else:
                        output.append("")
                        output.append("")
                        output.append("")
                        output.append("")
                final_output.append(output)
            except Exception as e:
                error_count += 1
                print(f'{url};{e}')
                print(traceback.format_exc())
                fail_count += 1
                with open(str(testtime) + "_" + input_cam + "_camera_info_error.csv" , "a") as f:
                    f.write(url + "\n")
                continue
            if track_progress:
                pbar.update(1)
            if c_counter % 101 == 0:
                if self.log_file:
                    time.sleep(random.randint(1 , 20))
                    self.write_to_file(final_output)
                final_output = []
                c_counter = 1
            c_counter += 1
        if not self.log_file:
            return final_output
        else:
            time.sleep(random.randint(1 , 20))
            self.write_to_file(final_output)

    def get_doorbell_info(self , customer_list, input_cam, testtime, get_rssi = True, track_progress=False):
        final_output = []
        fail_count = 0
        '''
        with requests.Session() as s:
            p = s.get('https://alarmadmin.alarm.com')
            tree = html.fromstring(p.text)
            view_state = tree.xpath('//input[@name="__VIEWSTATE"]/@value')
            event_validation = tree.xpath('//input[@name="__EVENTVALIDATION"]/@value')
            payload = {
                "txtUsername": self.credentials.user ,
                "txtPassword": self.credentials.password ,
                "butLogin": 'Login' ,
                "__VIEWSTATEGENERATOR": "CA0B0334" ,  # 02F837B7 for ADT by TELUS, CA0B0334 for TELUS SHS
                "__VIEWSTATE": view_state[0] ,
                "__EVENTVALIDATION": event_validation[0] ,
                "__EVENTTARGET": "" ,
                "__EVENTARGUMENT": "" ,
                "__VIEWSTATEENCRYPTED": ""
            }
            s.post('https://alarmadmin.alarm.com' , data=payload)
            '''
        if get_rssi:
            webapi=WebServicesAPI(self.dealer_id)
            webapi.authenticate()
            webapi.create_advanced_wifi_stats_input()
        c_counter = 1
        error_count = 0
        max_error_count = round(0.05*len(customer_list))
        if track_progress:
            pbar=tqdm(total=len(customer_list))
        for customer in customer_list:
            if error_count > max_error_count:
                break
            url = 'https://alarmadmin.alarm.com/Support/CameraInfo.aspx?customer_id=' + customer[
                0].rstrip() + '&device_id=' + customer[1].rstrip()
            try:
                a = self.session.get(url)
                tree = html.fromstring(a.text)
                info = [""] * 28
                info[0] = customer[0].rstrip()
                info[1] = tree.xpath('//td[contains(text(),"Device ID")]/following-sibling::td//span/text()')[0]
                info[2] = tree.xpath('//td[contains(text(),"Description")]/following-sibling::td//span/text()')[0].replace(',' , '')
                info[3] = self.convert_timestamp(tree.xpath('//td[contains(text(),"Install Date")]/following-sibling::td//span/text()')[0])
                info[4] = tree.xpath('//td[contains(text(),"MAC")]/following-sibling::td//span/text()')[0]
                info[5] = tree.xpath('//td[contains(text(),"Serial Number")]/following-sibling::td//span/text()')[0]
                info[6] = tree.xpath('//td[contains(text(),"Model")]/following-sibling::td//span/text()')[0]
                try:
                    hardware_version = \
                    tree.xpath('//td[contains(text(),"Hardware Version")]/following-sibling::td//span/text()')[0]
                    if "Refresh to load value" not in hardware_version:
                        info[7] = hardware_version
                    else:
                        info[7] = ""
                except Exception:
                    info[7] = ""
                info[8] = tree.xpath('//td[ contains(text(),"External IP")]/following-sibling::td//span/text()')[0]
                try:
                    info[9] = tree.xpath('//td[contains(text(),"Wireless SSID")]/following-sibling::td//span/text()')[
                        0].replace(',', '')
                except:
                    info[9] = ''
                try:
                    info[10] = \
                    tree.xpath('//td[contains(text(),"Wireless Quality")]/following-sibling::td//span/text()')[0]
                except:
                    info[10] = ""
                try:
                    info[11] = \
                    tree.xpath('//td[contains(text(),"Wireless Link Quality")]/following-sibling::td//span/text()')[
                        0].replace('%', '')
                except:
                    info[11] = ''
                try:
                    info[12] = \
                    tree.xpath('//td[contains(text(),"Wireless Tx Rate")]/following-sibling::td//span/text()')[
                        0].replace(' Mbps', '')
                except:
                    info[12] = ''
                info[13] = tree.xpath('//td[contains(text(),"Record Resolution")]/following-sibling::td//span/text()')[0]
                info[14] = tree.xpath('//td[contains(text(),"Record Quality")]/following-sibling::td//span/text()')[0]
                info[15] = self.convert_timestamp(tree.xpath('//td[contains(text(),"Last DDNS Update")]/following-sibling::td//span/text()')[0])
                info[16] = self.convert_timestamp(tree.xpath('//td[contains(text(),"Last Video Upload")]/following-sibling::td//span/text()')[0])
                info[17] = tree.xpath('//td[contains(text(),"Number of recording schedules")]/following-sibling::td//span/text()')[0]
                info[18] = self.convert_timestamp(tree.xpath('//td[contains(text(),"Last Supervision Attempt")]/following-sibling::td//span/text()')[0])
                info[19] = self.convert_timestamp(tree.xpath('//td[contains(text(),"Last Successful Supervision")]/following-sibling::td//span/text()')[0])
                info[20] = self.convert_timestamp(tree.xpath('//td[contains(text(),"Last Failed Supervision")]/following-sibling::td//span/text()')[0])
                info[21] = tree.xpath('//td[contains(text(),"Successful Supervision Attempts in 24 hrs")]/following-sibling::td//span/text()')[0].replace('%' , '')
                info[22] = tree.xpath('//td[contains(text(),"Stored Clips (all cameras)")]/following-sibling::td//span/text()')[0].replace(' Clips' , '').replace("," , "")
                info[23] = tree.xpath('//td[contains(text(),"Storage Quota (all cameras)")]/following-sibling::td//span/text()')[0].replace(' Clips' , '').replace("," , "")
                info[24] = tree.xpath('//td[contains(text(),"Monthly Upload Quota (all cameras)")]/following-sibling::td//span/text()')[0].replace(' Clips' , '').replace("," , "")
                info[25] = tree.xpath('//td[contains(text(),"Total uploads this month (all cameras)")]/following-sibling::td//span/text()')[0].replace(' Clips' , '').replace("," , "")
                info[26] = ""
                #if info[6] == "ADC-VDB105":
                    #info[26] = tree.xpath('//td[contains(text(),"Current Firmware Version")]/following-sibling::td//span/text()')[1]
                #else:
                    #info[26] = tree.xpath('//td[contains(text(),"Current Firmware Version")]/following-sibling::td//span/text()')[0]
                info[27] = tree.xpath('//td[contains(text(),"Current Firmware Version")]/following-sibling::td//span/text()')[0]
                #info[27] = ""
                chime_type = tree.xpath('//option[@selected="selected"]/text()')
                info.append(chime_type[1])
                info.insert(0 , self.start_time)
                if get_rssi:
                    rssi_info = webapi.get_advanced_wifi_stats(customer[0], customer[1])
                if rssi_info['Success'] == True:
                    info.append(str(rssi_info['Stats']['NormalizedSignalStrength']))
                    info.append(str(rssi_info['Stats']['SNR']))
                    info.append(str(rssi_info['Stats']['RSSI']))
                    info.append(str(rssi_info['Stats']['TxRate']))
                else:
                    info.append("")
                    info.append("")
                    info.append("")
                    info.append("")
                final_output.append(info)
            except Exception as e:
                error_count += 1
                print(f'{url};{e}')
                print(traceback.format_exc())
                fail_count += 1
                with open(str(testtime) + "_" + input_cam + "_DOORBELL_DATA_ERROR.csv" , "a") as f:
                    f.write(url + "\n")
                continue
            if track_progress:
                pbar.update(1)
            if c_counter % 101 == 0:
                if self.log_file:
                    time.sleep(random.randint(1 , 20))
                    self.write_to_file(final_output)
                final_output = []
                c_counter = 1
            c_counter += 1
        if not self.log_file:
            return final_output
        else:
            time.sleep(random.randint(1, 20))
            self.write_to_file(final_output)

    def get_modem_info(self , customer_list):
        final_output = []
        fail_count = 0
        self.create_adc_webservices_api()
        self.WebServicesAPI.create_customer_info_input()
        self.WebServicesAPI.get_latest_caller_version()
        with requests.Session() as s:
            p = s.get('https://alarmadmin.alarm.com')
            tree = html.fromstring(p.text)
            view_state = tree.xpath('//input[@name="__VIEWSTATE"]/@value')
            event_validation = tree.xpath('//input[@name="__EVENTVALIDATION"]/@value')
            payload = {
                "txtUsername": self.credentials.user ,
                "txtPassword": self.credentials.password ,
                "butLogin": 'Login' ,
                "__VIEWSTATEGENERATOR": "CA0B0334" ,  # 02F837B7 for ADT by TELUS, CA0B0334 for TELUS SHS
                "__VIEWSTATE": view_state[0] ,
                "__EVENTVALIDATION": event_validation[0] ,
                "__EVENTTARGET": "" ,
                "__EVENTARGUMENT": "" ,
                "__VIEWSTATEENCRYPTED": ""
            }
            s.post('https://alarmadmin.alarm.com' , data=payload)
            c_counter = 1
            for customer in customer_list:
                try:
                    customer_id = int(customer.rstrip())
                    customer_data = self.WebServicesAPI.get_customer_info(customer_id)
                    if customer_data['IsTerminated']:
                        continue
                    wifi_status = self.WebServicesAPI.get_dual_path_communication_status(customer_id)['CommunicationStatus']['DualEthernetWorking']
                    res = self.WebServicesAPI.get_equipment_list(customer_id)
                    panel = next(
                        (
                            res[index] for (index , d) in enumerate(res) if d["DeviceId"] == 127
                        ) ,
                        None
                    )
                    panel_status = panel['Status']['DeviceStatusEnum'][0]
                    url = 'https://alarmadmin.alarm.com/Support/FindEquipment.aspx?search=1&ModemSerial=' + customer_data['ModemInfo']['IMEI']
                    a = s.get(url)
                    tree = html.fromstring(a.text)
                    output = [None] * 19
                    output[0] = self.start_time
                    output[1] = customer.strip()  # customer ID
                    output[2] = str(customer_data['DealerCustomerId'])  # ecid
                    output[3] = customer_data['ModemInfo']['IMEI']  # imei
                    output[4] = tree.xpath('//span[@id="ctl00_phBody_ucsModemSearch_modemInformation_lblVersion"]/text()')[0]  # FWV
                    output[5] = tree.xpath('//span[@id="ctl00_phBody_ucsModemSearch_modemInformation_lblNetwork"]/text()')[0]  # Network
                    output[6] = tree.xpath('//span[@id="ctl00_phBody_ucsModemSearch_modemInformation_lblNetworkGen"]/text()')[0]  # Network Gen
                    output[7] = tree.xpath('//span[@id="ctl00_phBody_ucsModemSearch_modemInformation_lblEmbeddedRadios"]/text()')[0]  # Built-in
                    output[8] = tree.xpath('//span[@id="ctl00_phBody_ucsModemSearch_modemInformation_lblDaughterboard"]/text()')[0]  # Daughter Cards
                    output[9] = tree.xpath('//span[@id="ctl00_phBody_ucsModemSearch_modemInformation_lblImsi"]/text()')[0]  # IMSI
                    output[10] = tree.xpath('//span[@id="ctl00_phBody_ucsModemSearch_modemInformation_lblIccid"]/text()')[0]  # ICCID
                    output[11] = tree.xpath('//span[@id="ctl00_phBody_ucsModemSearch_modemInformation_lblRadioType"]/text()')[0]  # HW Version
                    output[12] = self.convert_timestamp(tree.xpath('//span[@id="ctl00_phBody_ucsModemSearch_modemInformation_lblActivationDate"]/text()')[0])  # Activation Date
                    output[13] = str(self.dealer_id)  # Dealer ID
                    output[14] = str(customer_data['SubDealerId'])  # Subdealer ID
                    output[15] = customer_data['ServicePlanInfo']['PackageDescription']  # Package Desc
                    output[16] = str(tree.xpath('//span[@id="ctl00_phBody_ucsModemSearch_modemInformation_lblBuildNumber"]/text()')[0])  # Build #
                    output[17] = 'Up' if wifi_status else 'Down'
                    output[18] = panel_status
                    final_output.append(output)
                    time.sleep(0.3)
                except Exception as e:
                    fail_count += 1
                    with open("module_info_error.log" , "a") as f:
                        f.write(url + str(e) + "\n")
                    continue

                if c_counter % 101 == 0:
                    time.sleep(random.randint(1 , 20))
                    self.write_to_file(final_output)
                    final_output = []
                    c_counter = 1
                c_counter += 1
        time.sleep(random.randint(1 , 120))
        self.write_to_file(final_output)

    def get_troubles_info(self , customer_list):
        final_output = []
        fail_count = 0
        self.create_adc_webservices_api()
        self.WebServicesAPI.create_customer_info_input()
        self.WebServicesAPI.get_latest_caller_version()
        c_counter = 1
        for customer in customer_list:
            try:
                customer_data = self.WebServicesAPI.get_customer_info(int(customer.rstrip()))
                if customer_data['IsTerminated']:
                    continue
                a = self.session.get('https://alarmadmin.alarm.com/Support/TroubleConditions.aspx?customer_Id=' + str(customer))
                tree = html.fromstring(a.text)
                rows = tree.xpath('//table[@id="ctl00_phBody_ucTroubleConditionHistory_adgTroubleConditionHistory"]//tr[@class="dataRow" or @class="altDataRow"]')
                for row in rows:
                    output = ""
                    for col in row:
                        output += col.text.rstrip() + ","
                    data = output.replace(",," , ",").split(",")
                    if len(data) > 4:
                        data.pop()
                    data.insert(0 , str(customer))
                    final_output.append(data)
                time.sleep(0.3)
            except Exception as e:
                fail_count += 1
                with open("troubles_info_error.log" , "a") as f:
                    f.write(str(customer) + "\n")
                continue
            if c_counter % 101 == 0:
                time.sleep(random.randint(1 , 20))
                self.write_to_file(final_output)
                final_output = []
                c_counter = 1
            c_counter += 1
        time.sleep(random.randint(1 , 120))
        self.write_to_file(final_output)

    def get_event_history(self , customer , text_filter):
        e = self.session.post('https://alarmadmin.alarm.com/Support/Events.aspx?customer_Id=' + str(customer))
        tree = html.fromstring(e.text)
        events = tree.xpath('//span[contains(text(),"' + text_filter + '")]/parent::div/parent::td/parent::tr')
        output = []
        for data in events:
            cols = data.xpath('./td/text()')
            output.append({'id': customer , 'type': cols[0].rstrip() , 'desc': data.xpath('./td/div/span/text()')[0].rstrip().encode("ascii" , "ignore").decode() , 'time': cols[-1].rstrip()})
        return output

    def get_panel_signal_info(self , customer_list):
        self.time_stamp_format = "%Y-%m-%d %I:%M:%S %p"
        final_output = []
        fail_count = 0
        self.login()
        self.create_adc_webservices_api()
        self.WebServicesAPI.create_customer_info_input()
        self.WebServicesAPI.get_latest_caller_version()
        c_counter = 1
        for customer in customer_list:
            try:
                customer_id = int(customer.rstrip())
                url = 'https://alarmadmin.alarm.com/Support/CheckSignaling.aspx?customer_id=' + str(customer)
                customer_data = self.WebServicesAPI.get_customer_info(customer_id)
                if customer_data['IsTerminated'] or customer_data['CommitmentDetail']:
                    continue
                if not customer_data['ModemInfo']['PanelType'] == 'IQPanel2':
                    continue
                a = self.session.get(url)
                tree = html.fromstring(a.text)
                output = [""] * 28
                output[0] = self.start_time
                output[1] = customer  # customer ID
                output[2] = str(customer_data['DealerCustomerId'])  # ecid
                output[3] = str(self.dealer_id)  # Dealer ID
                output[4] = str(customer_data['SubDealerId'])  # Subdealer ID
                output[5] = customer_data['ServicePlanInfo']['PackageDescription']  # Package Desc
                output[6] = customer_data['ModemInfo']['IMEI']  # imei
                output[7] = tree.xpath('//span[@id="ctl00_phBody_lblFirmwareVersionValue"]/text()')[0]  # FWV
                output[8] = tree.xpath('//span[@id="ctl00_phBody_lblNetworkValue"]/text()')[0]  # Network
                output[9] = tree.xpath('//span[@id="ctl00_phBody_lblNetworkGenerationValue"]/text()')[0]  # Network Gen
                output[10] = tree.xpath('//span[@id="ctl00_phBody_lblPanelCommModeValue"]/text()')[0]  # Communication Mode
                try:
                    output[11] = tree.xpath('//span[@id="ctl00_phBody_lblNetworkNameValue"]/text()')[0]  # Wi-Fi SSID
                except Exception:
                    output[11] = ""
                try:
                    output[12] = tree.xpath('//span[@id="ctl00_phBody_lblCurrentStatusValue"]/text()')[0]  # Wi-Fi Status
                except Exception:
                    output[12] = ""
                try:
                    output[13] = self.convert_timestamp(tree.xpath('//span[@id="ctl00_phBody_lnkCommunicationSystemCheckRunValue"]/text()')[0])  # Communication System Check
                except Exception:
                    output[13] = "Never"
                try:
                    output[14] = self.convert_timestamp(tree.xpath('//span[@id="ctl00_phBody_lblLatestSignalReceivedValue"]/text()')[0])  # Latest Signal Received
                except Exception:
                    output[14] = "Never"
                try:
                    output[15] = self.convert_timestamp(tree.xpath('//span[@id="ctl00_phBody_lblLastBroadbandPingValue"]/text()')[0])  # Last Broadband Ping
                except Exception:
                    output[15] = "Never"
                try:
                    output[16] = self.convert_timestamp(tree.xpath('//span[@id="ctl00_phBody_lblLastCellPingValue"]/text()')[0])  # Last Cell Ping
                except Exception:
                    output[16] = "Never"
                try:
                    output[17] = self.convert_timestamp(tree.xpath('//span[@id="ctl00_phBody_lblEquipmentListReceivedValue"]/text()')[0])  # Last Equipment List Received
                except Exception:
                    output[14] = "Never"
                try:
                    output[18] = self.convert_timestamp(tree.xpath('//span[@id="ctl00_phBody_lblSignalForwardedValue"]/text()')[0])  # Last Signal Fwd to CMS
                except Exception:
                    output[18] = 'N/A'
                output[19] = tree.xpath('//span[@id="ctl00_phBody_lblSignalRatingValue"]/text()')[0]  # Signal Rating
                output[20] = tree.xpath('//span[@id="ctl00_phBody_lblRegistrationEventsValue"]/text()')[0]  # Registration events > 90s
                signal_data = tree.xpath('//span[@id="ctl00_phBody_lblSignalStrengthBarsValue"]/text()')[0].replace(',' , '').split()
                if len(signal_data) > 1:
                    output[21] = signal_data[0]  # Average Signal Strength
                    output[22] = signal_data[3]
                    output[23] = signal_data[5]
                internal_signal_data = tree.xpath('//span[@id="ctl00_phBody_lblSignalStrengthInternalValue"]/text()')[0].replace(',' , '').split()
                if len(internal_signal_data) > 1:
                    output[24] = internal_signal_data[0]  # Average Internal  Signal Strength
                    output[25] = internal_signal_data[3]
                    output[26] = internal_signal_data[5]
                output[27] = tree.xpath('//span[@id="ctl00_phBody_lblPanelNotRespondingPercentageValue"]/text()')[0]  # % time panel not responding
                final_output.append(output)
            except Exception as e:
                fail_count += 1
                with open("signal_info_error.log" , "a") as f:
                    f.write(url + " " + str(e) + "\n")
                continue
            if c_counter % 101 == 0:
                time.sleep(random.randint(1 , 20))
                self.write_to_file(final_output)
                final_output = []
                c_counter = 1
            c_counter += 1
        time.sleep(random.randint(1 , 20))
        self.write_to_file(final_output)

    def get_panel_zwave_info(self , customer_list):
        self.time_stamp_format = "%Y-%m-%d %I:%M:%S %p"
        final_device_output = []
        final_diagnostic_output = []
        fail_count = 0
        self.login()
        self.create_adc_webservices_api()
        self.WebServicesAPI.create_customer_info_input()
        self.WebServicesAPI.get_latest_caller_version()
        self.WebServicesAPI.create_zwave_routing_table_input()
        c_counter = 1
        for customer in customer_list:
            try:
                customer_id = int(customer.rstrip())
                url = 'https://alarmadmin.alarm.com/Support/DeviceAutomation.aspx?customer_id=' + str(customer)
                customer_data = self.WebServicesAPI.get_customer_info(customer_id)
                if customer_data['IsTerminated'] or customer_data['CommitmentDetail']:
                    continue
                if not customer_data['ModemInfo']['PanelType'] == 'IQPanel2':
                    continue
                try:
                    neighbor_data = self.WebServicesAPI.get_zwave_routing_table(customer_id)['ZWaveRoutingTableInfoList']['ZWaveRoutingTableInfo']
                except Exception:
                    neighbor_data = False
                a = self.session.get(url)
                tree = html.fromstring(a.text)
                base_xpath = '//div[@id="ctl00_phBody_pnlNewEqList"]//section[@class="view-container zwave-device-table"]//div[@class="row device-row"]'
                attribute_xpath = './/label[contains(text(),"{%ATTRIBUTE%}")]//..//..//span//text()'
                # xpath_template = '//div[@id="ctl00_phBody_pnlNewEqList"]//section[@class="view-container zwave-device-table"]//div[@class="row device-row"]//label[contains(text(),"{%ATTRIBUTE%}")]//..//..//span'
                attributes = ['Status Date' ,
                              'Node ID' ,
                              'Link Quality' ,
                              'Info' ,
                              'Rediscover Date' ,
                              'Manufacturer' ,
                              'Z-Wave Version' ,
                              'Malfunction Duration' ,
                              'Install Date' ,
                              'Malfunction Rate' ,
                              'Security Level' ,
                              'Manufacturer String' ,
                              'Version' ,
                              'Device ID' ,
                              'Date Added']
                devices = tree.xpath(base_xpath)
                for device in devices:
                    output = [""] * 26
                    output[0] = self.start_time
                    output[1] = customer  # customer ID
                    output[2] = str(customer_data['DealerCustomerId'])  # ecid
                    output[3] = str(self.dealer_id)  # Dealer ID
                    output[4] = str(customer_data['SubDealerId'])  # Subdealer ID
                    output[5] = customer_data['ServicePlanInfo']['PackageDescription']  # Package Desc
                    output[6] = customer_data['ModemInfo']['IMEI']  # IMEI
                    output[7] = device.xpath('.//span[@class="main-device-desc"]//text()')[0].strip()  # Device Name
                    output[8] = device.xpath('.//span[@class="secondary-device-desc"]//text()')[0].strip()  # Secondary Name
                    output[9] = device.xpath('.//label[contains(text(),"Status") and not(contains(text(),"Date"))]//..//..//span//descendant-or-self::text()')[-1].strip()  # Status
                    try:
                        output[10] = device.xpath('.//label[contains(text(),"Link Quality")]//..//..//div[contains(@class,"link-quality-row")]//text()')[0].strip()
                    except Exception:
                        output[10] = ""
                    index = 11
                    for i , attribute in enumerate(attributes):
                        try:
                            output[index + i] = device.xpath(attribute_xpath.replace('{%ATTRIBUTE%}' , attribute))[0].strip()
                        except Exception:
                            output[index + i] = ""
                    if neighbor_data:
                        neighbors = next(item for item in neighbor_data if item['LocalNetworkId'] == output[12])
                        try:
                            output.append(str(len(neighbors['Neighbors']['Neighbor'])))
                        except Exception:
                            output.append("")
                    else:
                        output.append("")
                    final_device_output.append(output)
                diagnostic_output = []
                counters_data = tree.xpath('//tr[@id="ctl00_phBody_UcsZWaveDevices_ZWaveDiagnosticTable_panelDiagnostics"]//span//text()')
                diagnostic_output.append(self.start_time)
                diagnostic_output.append(str(customer_id))
                for counter in counters_data:
                    diagnostic_output.append(counter.strip())
                final_diagnostic_output.append(diagnostic_output)
            except Exception as e:
                fail_count += 1
                with open("zwave_info_error.log" , "a") as f:
                    f.write(url + " " + str(e) + "\n")
                continue
            if c_counter % 101 == 0:
                time.sleep(random.randint(1 , 20))
                self.write_to_file(final_device_output)
                c_counter = 1
            c_counter += 1
        time.sleep(random.randint(1 , 20))
        self.write_to_file(final_device_output)
        diagnostics_log = self.log_file.replace('.log' , "") + '(diagnostic counters).log'
        self.write_to_file(final_diagnostic_output , diagnostics_log)

    def get_security_sensor_strength(self , customer_list):
        self.time_stamp_format = "%Y-%m-%d %I:%M:%S %p"
        final_device_output = []
        fail_count = 0
        self.login()
        self.create_adc_webservices_api()
        self.WebServicesAPI.create_customer_info_input()
        self.WebServicesAPI.get_latest_caller_version()
        c_counter = 1
        sensor_attributes = ['DeviceId' ,
                             'DeviceName' ,
                             'SensorGroup' ,
                             'SensorType' ,
                             'CentralStationReporting' ,
                             'Partition' ,
                             'State' ,
                             'ActivityMonitoring' ,
                             'Eligibility' ,
                             'RadioFrequency']
        for customer in customer_list:
            try:
                customer_id = int(customer.rstrip())
                url = 'https://alarmadmin.alarm.com/Support/AirFx/rt_SensorSignalStrength.aspx?customer_id=' + str(customer)
                customer_data = self.WebServicesAPI.get_customer_info(customer_id)
                if customer_data['IsTerminated'] or customer_data['CommitmentDetail']:
                    continue
                a = self.session.get(url)
                tree = html.fromstring(a.text)
                base_xpath = '//tr[contains(@class,"Row") and not(contains(@class,"header"))]'
                devices = tree.xpath(base_xpath)
                sensor_summary_url = 'https://alarmadmin.alarm.com/Support/Commands/GetSensorNamesV2.aspx?customer_id=' + str(customer)
                b = self.session.get(sensor_summary_url)
                sensor_tree = html.fromstring(b.text)
                sensors = sensor_tree.xpath('//table[@id="ctl00_phBody_sensorList_AlarmDataGridSensor"]//tr[contains(@class,"Row") and not(contains(@class,"header"))]')
                change_sensor_group_url = 'https://alarmadmin.alarm.com/Support/AirFx/rt_ChangeSensorGroup.aspx?customer_id=' + str(customer)
                c = self.session.get(change_sensor_group_url)
                dl_code_tree = html.fromstring(c.text)
                dl_codes = dl_code_tree.xpath(base_xpath)
                sensor_summary = []
                for sensor in sensors:
                    sensor_dict = {}
                    sensor_data = [s.strip() for s in sensor.xpath('.//td//text()')][:-1]
                    while "" in sensor_data: sensor_data.remove("")
                    if len(sensor_data) != len(sensor_attributes):
                        continue
                    for i , attribute in enumerate(sensor_attributes):
                        sensor_dict[attribute] = sensor_data[i].strip()
                    sensor_summary.append(sensor_dict)
                dl_code_summary = []
                xpath = './/td[not(contains(@class,"new-type-id")) and not(contains(@class,"new-group-id")) and not(contains(text(),"Partition")) and not(contains(@class,"hidden"))]//text()'
                for dl_code in dl_codes:
                    dl_code_data = [s.strip() for s in dl_code.xpath(xpath)][:-1]
                    while "" in dl_code_data: dl_code_data.remove("")
                    if len(dl_code_data) == 0:
                        continue
                    dl_code_summary.append(dl_code_data)
                for device in devices:
                    output = [""] * 20
                    output[0] = self.start_time
                    output[1] = customer  # customer ID
                    output[2] = str(customer_data['DealerCustomerId'])  # ecid
                    output[3] = str(self.dealer_id)  # Dealer ID
                    output[4] = str(customer_data['SubDealerId'])  # Subdealer ID
                    output[5] = customer_data['ServicePlanInfo']['PackageDescription']  # Package Desc
                    output[6] = customer_data['ModemInfo']['IMEI']  # IMEI
                    device_data = [d.strip() for d in device.xpath('.//td//text()')]
                    while "" in device_data: device_data.remove("")
                    index = 7
                    for j , data in enumerate(device_data):
                        try:
                            output[index + j] = data.strip()
                        except Exception as e:
                            print(e)
                            output[index + j] = ""
                    sensor_summary_data = next((item for item in sensor_summary if item['DeviceId'] == output[7]) , '')
                    try:
                        output[13] = sensor_summary_data['CentralStationReporting']
                        output[14] = sensor_summary_data['Partition']
                        output[15] = sensor_summary_data['State']
                        output[16] = sensor_summary_data['ActivityMonitoring']
                        output[17] = sensor_summary_data['Eligibility']
                        output[18] = sensor_summary_data['RadioFrequency']
                    except Exception as e:
                        output.append("")
                    dl_code_summary_data = next((item for item in dl_code_summary if item[0] == output[7]) , '')
                    try:
                        output[19] = dl_code_summary_data[4]
                    except Exception as e:
                        output.append("")
                    final_device_output.append(output)
            except Exception as e:
                fail_count += 0
                with open("sensor_info_error.log" , "a") as f:
                    f.write(url + " " + str(e) + "\n")
                continue
            if not self.log_file:
                return final_device_output
            if c_counter % 101 == 0:
                time.sleep(random.randint(1 , 20))
                self.write_to_file(final_device_output)
                c_counter = 1
            c_counter += 1
        time.sleep(random.randint(1 , 20))
        self.write_to_file(final_device_output)