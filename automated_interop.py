from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import time
from tqdm import trange
import argparse
import automated_interop_test_cases
import automated_interop_assets
from datetime import datetime
import pytz

cust_user_name = None #username of the customer account
cust_password = None #password of the customer account
pp_user_name = None #username of the partner portal account
pp_password = None #password of the partner portal account
selectedCamera = None #name of the camera under test
model = None #model of the camera under test
selectedCameraMAC = None #MAC address of the camera under test
selectedCustomerID = None #ADC ID of the customer account
selected_device_ID = None #Device ID of the camera under test
selectedGateway = None #gateway under test
dealer_ID = None #Dealer ID of customer account
Panel = automated_interop_assets.Panel()
Panel.panel_id = None #Panel ID
Panel.panel_port = None #Panel Port
Panel.panel_setup()
panelID = None #Panel ID repeated. To be consolidated with Panel.panel_id



log_file = datetime.now(pytz.timezone('Canada/Mountain')).strftime("%m-%d-%YT%H_%M") + \
        '-' + selectedCamera + '-' + selectedGateway + '-interop-log.csv'
cycles = 1
ignored_exceptions=(StaleElementReferenceException,)
driver = webdriver.Chrome(ChromeDriverManager().install())
automated_interop_test_cases = automated_interop_test_cases.testcases(driver)
automated_interop_test_cases.logInToPartnerPortal(driver, pp_user_name, pp_password)
wait = WebDriverWait(driver, 5)

######### Fill in all GUI logins and passwords, and Wi-Fi SSID and Passwords in this section
automated_interop_test_cases.t3200_gui_url = None
automated_interop_test_cases.t3200_user_name = None
automated_interop_test_cases.t3200_password = None
automated_interop_test_cases.boostv2_user_name = None
automated_interop_test_cases.boostv2_password = None
automated_interop_test_cases.arcboostv2_gui_url = None
automated_interop_test_cases.tchboostv2_user_name = None
automated_interop_test_cases.tchboostv2_password = None
automated_interop_test_cases.web_username = None
automated_interop_test_cases.web_password = None
automated_interop_test_cases.airties_SSID = None
automated_interop_test_cases.airties_SSID_password = None
automated_interop_test_cases.t3200SmartSteeringSSID = None
automated_interop_test_cases.t3200_24SSID = None
automated_interop_test_cases.t3200_5SSID = None
automated_interop_test_cases.t3200SmartDeviceSSID = None
automated_interop_test_cases.t3200_SSID_PW = None
automated_interop_test_cases.t3200_SmartDeviceSSID_PW = None
automated_interop_test_cases.boostSSID = None
automated_interop_test_cases.boostSmartDeviceSSID = None
automated_interop_test_cases.boost_SSID_PW = None
automated_interop_test_cases.twh_SSID = None
automated_interop_test_cases.twhSmartDeviceSSID = None
automated_interop_test_cases.twh_SSID_PW = None
automated_interop_test_cases.twhSmartDeviceSSIDPW = None
automated_interop_test_cases.twh_gui_url = None
automated_interop_test_cases.twh_user_name = None
automated_interop_test_cases.twh_password = None
automated_interop_test_cases.arcboostv2_SSID = None
automated_interop_test_cases.arcboostv2SmartDeviceSSID24 = None
automated_interop_test_cases.arcboostv2SmartDeviceSSID5 = None
automated_interop_test_cases.arcboostv2_SSID_PW = None
automated_interop_test_cases.arcboostv2SmartDeviceSSID_PW = None
automated_interop_test_cases.arcboostv2_gui_url = None
automated_interop_test_cases.tchboostv2SmartSteeringSSID = None
automated_interop_test_cases.tchboostv2_24SSID = None
automated_interop_test_cases.tchboostv2_5SSID = None
automated_interop_test_cases.tchboostv2SmartDeviceSSID = None
automated_interop_test_cases.tchboostv2PW = None
#########

if selectedGateway == "T3200M":
    with open(log_file, 'w', newline='') as f:
        print("T3200M + Boostv1 Interop\n", file=f, end="", )
        print("Time,Connection Type,Install Time,Web Stream,Panel Stream SmartSteering SSID, Panel Stream 2.4 GHz, Panel Stream 5 GHz, Panel Stream Smart Device SSID, Panel Stream Boost Data SSID, Panel Stream Boost Smart Device SSID,Test Result\n", file=f, end="", )
    for i in range(cycles):
        automated_interop_test_cases.t3200testcase(driver, cust_user_name, cust_password, pp_user_name, pp_password,
                                                 selectedCamera, selectedCameraMAC, selectedCustomerID,
                                                 selected_device_ID, dealer_ID, log_file, model, Panel, panelID)
elif selectedGateway == "TWH":
    with open(log_file, 'w',newline='') as f:
        print("TWH Interop\n",file=f, end="",)
        print("Time,Connection Type,Install Time,Web Stream,Panel Stream SmartSteering SSID, Panel Stream 2.4 GHz, Panel Stream 5 GHz, Panel Stream Smart Device SSID,Test Result\n", file=f, end="", )
    for i in range(cycles):
        automated_interop_test_cases.twhtestcase(driver, cust_user_name, cust_password, pp_user_name, pp_password,
                                                selectedCamera, selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID,log_file, model, Panel, panelID)
elif selectedGateway == "TWHBoost":
    with open(log_file, 'w', newline='') as f:
        print("TWH + Boost Interop\n", file=f, end="", )
        print("Time,Connection Type,Success/Fail,Install Time\n", file=f, end="", )
    for i in range(cycles):
        automated_interop_test_cases.twhtestcase(driver, cust_user_name, cust_password, pp_user_name, pp_password,
                                                 selectedCamera, selectedCameraMAC, selectedCustomerID,
                                                 selected_device_ID, dealer_ID, log_file, model, Panel)
elif selectedGateway == "ARCBoostv2":
    with open(log_file, 'w', newline='') as f:
        print("NAH + Boostv2 Interop\n", file=f, end="", )
        print("Time,Connection Type,Install Time,Web Stream,Panel Stream SmartSteering SSID, Panel Stream 2.4 GHz, Panel Stream 5 GHz, Panel Stream 2.4 GHz Smart Device SSID,Test Result, Panel Stream 5 GHz Smart Device SSID,Test Result\n", file=f, end="", )
    for i in range(cycles):
        automated_interop_test_cases.nahARCboostv2testcase(driver, cust_user_name, cust_password, pp_user_name, pp_password,
                                                 selectedCamera, selectedCameraMAC, selectedCustomerID,
                                                 selected_device_ID, dealer_ID, log_file, model, Panel,panelID)
elif selectedGateway == "TCHBoostv2":
    with open(log_file, 'w', newline='') as f:
        print("NAH + Boostv2 Interop\n", file=f, end="", )
        print("Time,Connection Type,Success/Fail,Install Time\n", file=f, end="", )
    for i in range(cycles):
        automated_interop_test_cases.nahTCHboostv2testcase(driver, cust_user_name, cust_password, pp_user_name, pp_password,
                                                 selectedCamera, selectedCameraMAC, selectedCustomerID,
                                                 selected_device_ID, dealer_ID, log_file, model)
elif selectedGateway == "WEB6000Q":
    with open(log_file, 'w', newline='') as f:
        print("T3200M + WEB6000Q Interop\n", file=f, end="", )
        print("Time,Connection Type,Success/Fail,Install Time\n", file=f, end="", )
    for i in range(cycles):
        automated_interop_test_cases.t3200webtestcase(driver, cust_user_name, cust_password, pp_user_name, pp_password,
                                                 selectedCamera, selectedCameraMAC, selectedCustomerID,
                                                 selected_device_ID, dealer_ID, log_file, model)

elif selectedGateway == "Airties":
    with open(log_file, 'w', newline='') as f:
        print("NAH + Boostv2 + Airties Interop\n", file=f, end="", )
        print("Time,Connection Type,Success/Fail,Install Time\n", file=f, end="", )
    for i in range(cycles):
        automated_interop_test_cases.airtiestestcase(driver, cust_user_name, cust_password, pp_user_name, pp_password,
                                                 selectedCamera, selectedCameraMAC, selectedCustomerID,
                                                 selected_device_ID, dealer_ID, log_file, model)
else:
    exit()
#automated_interop_test_cases.testcase(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera, selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID)

