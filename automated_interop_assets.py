# import libraries
import time
import subprocess
import os
import json
import string
from lxml import html
from random import randrange
from datetime import datetime , timedelta
import requests
from appium import webdriver as appium_webdriver
from appium.webdriver.common.touch_action import TouchAction
from selenium import webdriver as selenium_webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotVisibleException , NoSuchElementException , TimeoutException , ElementNotSelectableException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import re
from WebServicesAPI import WebServicesAPI
from WebServicesHTTP import WebServicesHTTP
from WebServicesELK import WebServicesELK
from CredentialsManager import CredentialsManager
from SensorManager import SensorManager
from ControlSystem import ControlSystem

# Object to interact with IQ Panel and IQ Remote
class Panel:
    panel_driver = None
    wait = None
    panel_id = None
    panel_port = None
    panel_name = ""
    device_name = 'IQPanel2'
    panel_status = "DISARMED"
    partitions_enabled = False
    dealer_code = ["2" , "2" , "2" , "2"]
    admin_code = ["1" , "2" , "3" , "4"]
    installer_code = ["1" , "1" , "1" , "1"]
    exit_delay = 90
    quick_exit_delay = 120
    bluetooth_timeout = 75
    bluetooth_disarm_enabled = False
    bluetooth_device_installed = False
    SensorManager = None
    sensors_installed = False
    sensor_registration_delay = 30
    wait_time = 60
    test_partition = "1"
    appium_url = ""
    add_sensors_with_webservices = False
    panel_type = 'IQ2'
    WebServicesAPI = None

    def __init__(self):
        self.SensorManager = SensorManager()

    pinpad = {}
    pinpad["1"] = "com.qolsys:id/tv_keyOne"
    pinpad["2"] = "com.qolsys:id/tv_keyTwo"
    pinpad["3"] = "com.qolsys:id/tv_keyThree"
    pinpad["4"] = "com.qolsys:id/tv_keyFour"
    pinpad["5"] = "com.qolsys:id/tv_keyFive"
    pinpad["6"] = "com.qolsys:id/tv_keySix"
    pinpad["7"] = "com.qolsys:id/tv_keySeven"
    pinpad["8"] = "com.qolsys:id/tv_keyEight"
    pinpad["9"] = "com.qolsys:id/tv_keyNine"
    pinpad["0"] = "com.qolsys:id/tv_zero"
    pinpad["clear"] = "com.qolsys:id/tv_clear"
    pinpad["back"] = "com.qolsys:id/img_back"

    partitions = {}
    partitions["1"] = "partition1"
    partitions["2"] = "partition2"
    partitions["3"] = "partition3"
    partitions["4"] = "partition4"

    def panel_setup(self):
        self.panel_driver = self.setup()
        self.wait = WebDriverWait(self.panel_driver , self.wait_time , poll_frequency=1 , ignored_exceptions=[ElementNotVisibleException , NoSuchElementException , TimeoutException])
        self.panel_driver.hide_keyboard()

    def setup(self):
        self.appium_url = 'http://127.0.0.1:' + self.panel_port + '/wd/hub'
        desired_caps = {}
        desired_caps['platformName'] = 'Android'
        desired_caps['platformVersion'] = "5.1"
        desired_caps['udid'] = self.panel_id
        desired_caps['automationName'] = 'UiAutomator1'
        desired_caps["deviceName"] = self.device_name
        desired_caps['appPackage'] = 'com.qolsys'
        desired_caps['appActivity'] = 'com.qolsys.activites.MainActivity'
        desired_caps['noReset'] = True
        desired_caps['newCommandTimeout'] = 86400
        desired_caps['adbExecTimeout'] = 40000
        # desired_caps['uiautomator2ServerInstallTimeout'] = 120000
        desired_caps['unicodeKeyboard'] = True
        desired_caps['resetKeyboard'] = True
        return appium_webdriver.Remote(self.appium_url , desired_caps)

    def tear_down(self):
        self.panel_driver.quit()

    def clean_up(self):
        if self.panel_status != "DISARMED":
            if self.partitions_enabled:
                self.disarm_partition(self.test_partition)
            else:
                self.disarm_panel()
        if self.bluetooth_device_installed:
            self.remove_bluetooth_devices()
        if self.bluetooth_disarm_enabled:
            self.disable_bluetooth_disarm()
        if self.partitions_enabled:
            self.disable_partitions()
        if self.sensors_installed:
            self.remove_powerg_sensors()
        self.tear_down()

    # Read the devices that connected from the command prompt
    def get_adb_devices(self):
        devicenames = subprocess.Popen("adb devices" , stdout=subprocess.PIPE)
        output = devicenames.communicate()
        stringValue = output[0].decode("UTF-8")
        # Split the string and read only device id
        devicesconnected = stringValue.split("\r\n" , 1)
        mydevice = devicesconnected[1].split("\r\n")
        for i in range(0 , len(mydevice)):
            mydevice[i] = mydevice[i].split("\t")[0]
        return mydevice

    def confirm_connection_to_appium(self):
        url = 'http://127.0.0.1:/wd/hub/sessions'
        output = json.loads(requests.get(url).text)['value']
        for device in output:
            if device['capabilities']['udid'] == self.panel_id:
                return True
        return False

    def instantiate_webservices(self):
        if not self.WebServicesAPI:
            self.WebServicesAPI = WebServicesAPI(self.dealer_id)
            self.WebServicesAPI.authenticate()

    def pair_to_panel(self):
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/pair_to_primary_button')))
        self.panel_driver.find_element_by_id('com.qolsys:id/pair_to_primary_button').click()

    def remote_setup(self):
        proc = subprocess.Popen(["adb" , "connect" , self.panel_id] , stdout=subprocess.PIPE)
        output = proc.communicate()[0].decode("UTF-8")
        if "connected to " + self.panel_id in output:
            self.device_name = "IQRemote"
            self.panel_setup()

    # Input codes

    def enter_pin(self , code):
        for num in code:
            self.panel_driver.find_element_by_id(self.pinpad[num]).click()
            time.sleep(0.25)

    # check if a pin has been entered
    def check_pin(self):
        pin = []
        try:
            checkboxes = self.panel_driver.find_elements_by_id("com.qolsys:id/unselected")
            i = 0
            while i < len(checkboxes):
                pin.append(str(randrange(10)))
                i += 1
            return pin
        except Exception as e:
            return False

    # User codes
    def input_admin_code(self):
        # click on the 1234
        self.enter_pin(self.admin_code)

    # Dealer codes
    def input_dealer_code(self):
        # Enter dealer code 2222
        self.enter_pin(self.dealer_code)

    # Scroll down
    def scroll(self):
        dimensions = self.panel_driver.get_window_size()
        start_y = dimensions["height"] * 0.8
        end_y = dimensions["height"] * 0.1
        start_x = dimensions['width'] * 0.5
        self.panel_driver.swipe(start_x , start_y , start_x , end_y , 2000)

    # Click home button
    def go_home(self):
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/ft_home_button')))
        self.panel_driver.find_element_by_id("com.qolsys:id/ft_home_button").click()
        return True

    # Read the current status of the panel.
    def read_status(self):
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/t3_tv_disarm")))
        return self.panel_driver.find_element_by_id("com.qolsys:id/t3_tv_disarm").text.upper()

    # Arm stay the panel.
    def arm_stay(self):
        # click on the icon displayed on home page to change the panel mode
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/disarmFullView")))
        self.panel_driver.find_element_by_id("com.qolsys:id/disarmFullView").click()
        # click on the Arm stay icon to change the panel mode to Arm stay.
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/img_arm_stay")))
        self.panel_driver.find_element_by_id("com.qolsys:id/img_arm_stay").click()
        # Read the panel text and validate the panel mode is now changed to "ARMED STAY"
        if self.read_status() == "ARMED STAY":
            return True
        else:
            self.disarm_panel()
            return False
        # Arm away the panel, for Arm away door sensor must be triggered(open/close)to change the mode to "ARMED AWAY"

    # Arm away the panel
    def arm_away(self):
        # click on the icon displayed on home page to change the panel mode
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/disarmFullView")))
        self.panel_driver.find_element_by_id("com.qolsys:id/disarmFullView").click()
        # click on the Arm away icon to change the panel mode to Arm away.
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/img_arm_away")))
        self.panel_driver.find_element_by_id('com.qolsys:id/img_arm_away').click()

    # After triggering door sensor, validate the panel mode is now changed to "ARMED AWAY"
    def verify_arm_away(self):
        if self.read_status() == "ARMED AWAY":
            return True
        else:
            # Disarm the panel
            self.disarm_panel()
            return False

    def disarm_panel(self , pin=False):
        # Read the panel status, if it is Armed stay/Armed away change the panel state to Disarmed
        panel_status = self.read_status()
        if (panel_status == "ARMED STAY") or (panel_status == "ARMED AWAY"):
            # click on the icon displayed on home page to change the panel mode
            self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/disarmFullView")))
            self.panel_driver.find_element_by_id("com.qolsys:id/disarmFullView").click()
            # Enter the user code 1234 to disarm the panel.
            if not pin:
                self.input_admin_code()
            else:
                self.enter_pin(pin)
            # Read the panel text and verify the panel mode is now changed to "DISARMED"
        if self.read_status() == "DISARMED":
            return True
        else:
            return False
        # Validate when the alarm is ON and disarm the system.

    def alarm_notification_panel(self , sensortype):
        # Read the text from the alarm page.
        if self.panel_driver.find_element_by_id('com.qolsys:id/txt_title').text == "AL ARM":
            # Read the type of sensor activated and the status of the sensor.
            sensorname = self.panel_driver.find_element_by_id('com.qolsys:id/tv_name').text
            sensorstatus = self.panel_driver.find_element_by_id('com.qolsys:id/tv_status').text

            if sensortype == "any" and ("door" in sensorname.lower() or "motion" in sensorname.lower()):
                success = True
            elif sensortype == "entry/exit" and (
                    sensorname.lower() == "door 1" or sensorname.lower() == "door 2" or sensorname.lower() == "door1" or sensorname.lower() == "door2"):
                success = True
            elif sensortype == "safety" and (
                    sensorname.lower() == "co" or sensorname.lower() == "smoke" or sensorname.lower() == "glass" or sensorname.lower() == "flood"):
                success = True
            else:
                success = False
            # Enter the user code to disarm the panel
            self.input_admin_code()
        else:
            print("Alarm page is not enabled")
        # Verify if the panel is put to Disarmed state
        panel_status = self.read_status()
        if panel_status == "DISARMED":
            success = True
        else:
            success = False
        return success

    def click_panel_wallpaper(self):
        # click on the wall paper screen if the panel is in sleep mode
        try:
            wallpaper_image = self.panel_driver.find_element_by_id('com.qolsys:id/viewFlipper')
            if wallpaper_image.is_displayed():
                wallpaper_image.click()
                time.sleep(3)
        except NoSuchElementException as e:
            return None

    def open_dropdown_menu(self):
        while True:
            try:
                self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/btn_drop')))
                self.panel_driver.find_element_by_id("com.qolsys:id/btn_drop").click()
                break
            except Exception as e:
                print("Unable to find and click on drop down menu")
                time.sleep(1)

    def lock_screen(self):
        self.open_dropdown_menu()
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/ui_icon_system_state")))
        self.panel_driver.find_element_by_id("com.qolsys:id/ui_icon_system_state").click()

    def close_keyboard(self):
        TouchAction(self.panel_driver).tap(None , 1260 , 730 , 1).perform()
        return True

    # navigate to advanced settings
    def go_to_advanced_settings(self):
        self.click_panel_wallpaper()
        # click on the settings drop down menu
        self.open_dropdown_menu()
        # click on settings
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/image_settings')))
        self.panel_driver.find_element_by_id("com.qolsys:id/image_settings").click()
        # click on advanced settings
        xpath = '//android.widget.TextView[' + self.xpath_translate('text' , 'advanced settings') + ']'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()
        try:
            self.input_dealer_code()
        except Exception as e:
            return None

    def go_to_installation(self):
        self.go_to_advanced_settings()
        xpath = '//android.widget.TextView[' + self.xpath_translate('text' , 'installation') + ']'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()

    def xpath_translate(self , attribute , value):
        return 'translate(@' + attribute + ',"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz")="' + value + '"'

    def go_to_user_management(self):
        self.go_to_advanced_settings()
        xpath = '//android.widget.TextView[' + self.xpath_translate('text' , 'user management') + ']'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()

    def get_user_codes(self):
        self.go_to_user_management()
        self.wait.until(ec.element_to_be_clickable((By.XPATH , '//android.widget.TextView[@resource-id="com.qolsys:id/name"]')))
        users = self.panel_driver.find_elements_by_xpath('//android.widget.TextView[@resource-id="com.qolsys:id/name"]')
        output = []
        for user in users:
            output.append(user.get_attribute('text'))
        self.go_home()
        return output

    def add_user_code(self , user_data , partition=False):
        self.go_to_user_management()
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/btnAdd')))
        self.panel_driver.find_element_by_id('com.qolsys:id/btnAdd').click()
        # input first name
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/username')))
        self.panel_driver.find_element_by_id('com.qolsys:id/username').set_value(user_data['first_name'])
        # input last name
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/lastname')))
        self.panel_driver.find_element_by_id('com.qolsys:id/lastname').set_value(user_data['last_name'])
        # input new user code
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/user_pin')))
        self.panel_driver.find_element_by_id('com.qolsys:id/user_pin').set_value(user_data['pin'])
        # confirm pin
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/confirm_pin')))
        self.panel_driver.find_element_by_id('com.qolsys:id/confirm_pin').set_value(user_data['pin'])
        if partition:
            xpath = '//android.widget.TextView[@text="PARTITION' + str(partition) + '"]//..//android.widget.CheckBox'
            self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
            self.panel_driver.find_element_by_xpath(xpath).click()
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/add')))
        self.panel_driver.find_element_by_id('com.qolsys:id/add').click()
        self.go_home()

    def delete_user_code(self , user_data):
        self.go_to_user_management()
        xpath = '//android.widget.TextView[@text="' + user_data['first_name'] + " " + user_data['last_name'] + '"]//..//android.widget.ImageView[@resource-id="com.qolsys:id/deleteImg"]'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/ok')))
        self.panel_driver.find_element_by_id('com.qolsys:id/ok').click()
        self.go_home()

    # navigate to dealer settings
    def go_to_dealer_settings(self):
        self.go_to_installation()
        xpath = '//android.widget.TextView[' + self.xpath_translate('text' , 'dealer settings') + ']'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()

    def go_to_sensors(self):
        self.go_to_installation()
        # click on devices
        xpath = '//android.widget.TextView[' + self.xpath_translate('text' , 'devices') + ']'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()
        # click on security sensors
        xpath = '//android.widget.TextView[' + self.xpath_translate('text' , 'security sensors') + ']'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()

    def go_to_add_sensor(self , auto_add_sensor=False):
        xpath = '//android.widget.TextView[' + self.xpath_translate('text' , 'add sensor') + ']'
        if auto_add_sensor:
            xpath = '//android.widget.TextView[' + self.xpath_translate('text' , 'auto learn sensor') + ']'
        # navigate to the add sensors page
        self.go_to_sensors()
        # click on add sensor
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()

    def hide_keyboard(self):
        try:
            self.panel_driver.hide_keyboard()
            return True
        except Exception as e:
            return False

    def auto_add_sensor(self , sensor , ControlSystem , sensor_group=None , partition=None):
        sensor_details = self.SensorManager.get_sensor_from_file(sensor)
        self.go_to_add_sensor(auto_add_sensor=True)
        ControlSystem.tamper_sensor(sensor)
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/message")))
        message = self.panel_driver.find_element_by_id('com.qolsys:id/message').text
        if sensor_details['DL_ID_PREFIX'] in message and sensor_details['DL_ID_SUFFIX'] in message:
            self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/ok')))
            self.panel_driver.find_element_by_id('com.qolsys:id/ok').click()
            self.add_sensor(sensor , sensor_group=sensor_group , partition=partition , auto_add_sensor=True , sensor_details=sensor_details)
            return True
        else:
            self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/cancel')))
            self.panel_driver.find_element_by_id('com.qolsys:id/cancel').click()
            self.go_home()
            return False

    def add_sensor(self , sensor , sensor_group=None , partition=None , auto_add_sensor=False , sensor_details=None , edit=False , customer_id=None):
        if self.add_sensors_with_webservices:
            self.WebServicesAPI.create_add_sensor_input()
            sensor_details = ControlSystem.SensorManager.get_sensor_from_file(sensor)
            sensor_info = {'sensor_id': sensor_details['SENSOR_ID'] ,
                           'group_id': sensor_details['GROUP_ID'] ,
                           'sensor_name': sensor_details['LABEL'] ,
                           'sensor_type_id': sensor_details['SENSOR_TYPE_ID'] ,
                           'signal_src': sensor_details['SOURCE_ID'] ,
                           'dlcode': sensor_details['DL_ID_PREFIX'] + sensor_details['DL_ID_SUFFIX']
                           }
            self.WebServicesAPI.add_sensor(customer_id , sensor_info , partition=partition)
            return True
        else:
            if not auto_add_sensor and not edit:
                sensor_details = self.SensorManager.get_sensor_from_file(sensor)
                self.go_to_add_sensor()
            if sensor_group:
                sensor_details['SENSOR_GROUP'] = sensor_group
            if partition:
                sensor_details["PARTITION"] = partition
            time.sleep(1)
            if (sensor_details["SOURCE"] == "PowerG"):
                if not auto_add_sensor:
                    if not edit:
                        # click on the source drop down menu
                        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/sensorprotocaltype")))
                        self.panel_driver.find_element_by_id("com.qolsys:id/sensorprotocaltype").click()
                        # click on the PowerG option
                        self.wait.until(ec.element_to_be_clickable((By.XPATH , '//android.widget.CheckedTextView[@text="PowerG"]')))
                        self.panel_driver.find_element_by_xpath('//android.widget.CheckedTextView[@text="PowerG"]').click()
                        # fill in the sensor ID
                        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/sensor_id")))
                        self.panel_driver.find_element_by_id("com.qolsys:id/sensor_id").clear()
                        self.panel_driver.find_element_by_id("com.qolsys:id/sensor_id").set_value(sensor_details["DL_ID_PREFIX"])
                        # self.panel_driver.hide_keyboard()
                        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/sensor_powerg_id")))
                        self.panel_driver.find_element_by_id("com.qolsys:id/sensor_powerg_id").clear()
                        self.panel_driver.find_element_by_id("com.qolsys:id/sensor_powerg_id").set_value(sensor_details["DL_ID_SUFFIX"])
                        # self.panel_driver.hide_keyboard()
                        '''
                        # fill in the sensor ID
                        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/sensor_id")))
                        sensor_ID_txt = self.panel_driver.find_element_by_id("com.qolsys:id/sensor_id")
                        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/sensor_powerg_id")))
                        powerG_ID_txt = self.panel_driver.find_element_by_id("com.qolsys:id/sensor_powerg_id")
                        sensor_ID_txt.clear()
                        sensor_ID_txt.set_value(sensor_details["DL_ID_PREFIX"])
                        if sensor_ID_txt.text == sensor_details["DL_ID_PREFIX"]:
                            self.hide_keyboard()
                        powerG_ID_txt.clear()
                        powerG_ID_txt.set_value(sensor_details["DL_ID_SUFFIX"])
                        if powerG_ID_txt.text == sensor_details["DL_ID_SUFFIX"]:
                            self.hide_keyboard()
                        '''
                        if sensor_details["DL_ID_PREFIX"] == "101":
                            self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/optionspinner")))
                            self.panel_driver.find_element_by_id("com.qolsys:id/optionspinner").click()
                            self.panel_driver.find_element_by_android_uiautomator('new UiSelector().text("Auxiliary Normally Closed")').click()
                # click on the sensor description drop down menu
                self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/sensor_desc")))
                self.panel_driver.find_element_by_id("com.qolsys:id/sensor_desc").click()
                # click on the Custom Description option
                self.wait.until(ec.element_to_be_clickable((By.XPATH , '//android.widget.CheckedTextView[@text="Custom Description"]')))
                self.panel_driver.find_element_by_xpath('//android.widget.CheckedTextView[@text="Custom Description"]').click()
                # fill in the sensor description
                self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/sensorDescText")))
                if edit:
                    self.panel_driver.find_element_by_id("com.qolsys:id/sensorDescText").clear()
                self.panel_driver.find_element_by_id("com.qolsys:id/sensorDescText").set_value(sensor_details["LABEL"])
                # self.panel_driver.hide_keyboard()

                '''
                self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/sensorDescText")))
                custom_desc_txt = self.panel_driver.find_element_by_id("com.qolsys:id/sensorDescText")
                custom_desc_txt.click()
                custom_desc_txt.clear()
                custom_desc_txt.set_value(sensor_details["LABEL"])
                '''
                '''
                if self.panel_driver.find_element_by_id("com.qolsys:id/sensorDescText").text == sensor_details["LABEL"]:
                    self.hide_keyboard()
                '''
                # fill in sensor group
                self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/grouptype")))
                self.panel_driver.find_element_by_id("com.qolsys:id/grouptype").click()
                self.panel_driver.find_element_by_android_uiautomator(
                    "new UiScrollable(new UiSelector().scrollable(true).instance(0)).scrollIntoView(new UiSelector().textContains(\"" +
                    sensor_details['SENSOR_GROUP'] + "\").instance(0))").click()
                # select partition
                if self.partitions_enabled:
                    self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/partition_name")))
                    self.panel_driver.find_element_by_id("com.qolsys:id/partition_name").click()
                    partition_xpath = '//android.widget.CheckedTextView[@text="' + self.partitions[sensor_details["PARTITION"]].capitalize() + '"]'
                    self.wait.until(ec.element_to_be_clickable((By.XPATH , partition_xpath)))
                    self.panel_driver.find_element_by_xpath(partition_xpath).click()
                self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/addsensor")))
                self.panel_driver.find_element_by_id("com.qolsys:id/addsensor").click()
                self.go_home()

    def go_to_edit_sensor(self):
        self.go_to_sensors()
        # click on edit sensor
        xpath = '//android.widget.TextView[' + self.xpath_translate('text' , 'edit sensor') + ']'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()

    def edit_sensor(self , sensor , sensor_details):
        self.go_to_edit_sensor()
        xpath = '//android.widget.TextView[@text="' + sensor + '"]//..//android.widget.RelativeLayout[@resource-id="com.qolsys:id/uiRL5"]'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()
        self.add_sensor(sensor , sensor_details=sensor_details , edit=True)

    def bulk_add_sensor(self):
        self.go_to_add_sensor()
        sensor_details = {}
        with open(self.sensors_file) as json_file:
            mySensors = json.loads(json_file.read())
            mySensors = mySensors["SENSORS"]
            for sensor in mySensors:
                sensor_details["LABEL"] = sensor["LABEL"]
                sensor_details["SENSOR_TYPE"] = sensor["SENSOR_TYPE"]
                sensor_details["SOURCE"] = sensor["SOURCE"]
                sensor_details["DL_ID_PREFIX"] = sensor["DL_ID_PREFIX"]
                sensor_details["DL_ID_SUFFIX"] = sensor["DL_ID_SUFFIX"]
                sensor_details["PARTITION"] = sensor["PARTITION"]
                self.add_sensor(sensor_details)
                time.sleep(5)
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/ft_home_button")))
        home_btn = self.panel_driver.find_element_by_id("com.qolsys:id/ft_home_button")
        home_btn.click()

    def go_to_sensor_status(self):
        self.go_to_sensors()
        # click on sensor status
        xpath = '//android.widget.TextView[' + self.xpath_translate('text' , 'sensor status') + ']'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()

    def go_to_wifi_devices(self):
        self.go_to_installation()
        # click on devices
        xpath = '//android.widget.TextView[' + self.xpath_translate('text' , 'devices') + ']'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()
        xpath = '//android.widget.TextView[' + self.xpath_translate('text' , 'wi-fi devices') + ']'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()

    def go_to_iq_remote_devices(self):
        self.go_to_wifi_devices()
        xpath = '//android.widget.TextView[' + self.xpath_translate('text' , 'iq remote devices') + ']'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()

    def add_iq_remote(self , Remote , partition="1"):
        self.go_to_iq_remote_devices()
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/btnAdd')))
        self.panel_driver.find_element_by_id('com.qolsys:id/btnAdd').click()
        Remote.pair_to_panel()
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/remote_device_name')))
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/remote_device_status')))
        counter = 0
        while True:
            if self.panel_driver.find_element_by_id('com.qolsys:id/remote_device_status').text == "Active" and counter > 3:
                break
            counter += 1
            time.sleep(3)
            self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/remote_device_status')))
        if self.partitions_enabled and partition != "1":
            self.edit_iq_remote_partition(Remote.panel_name , partition)
        self.go_home()
        return True

    def edit_iq_remote_partition(self , iq_remote , partition):
        xpath = '//android.widget.TextView[@text="' + iq_remote + '"]//following-sibling::android.widget.RelativeLayout[@resource-id="com.qolsys:id/uiRL5"]//android.widget.ImageView'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/partition_name')))
        self.panel_driver.find_element_by_id('com.qolsys:id/partition_name').click()
        xpath = '//android.widget.CheckedTextView[@text="Partition' + partition + '"]'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/save')))
        self.panel_driver.find_element_by_id('com.qolsys:id/save').click()

    def remove_iq_remotes(self , iq_remotes=["IQ Remote 1"]):
        self.go_to_iq_remote_devices()
        for iq_remote in iq_remotes:
            xpath = '//android.widget.TextView[@text="' + iq_remote + '"]//following-sibling::android.widget.RelativeLayout[@resource-id="com.qolsys:id/uiRL6"]//android.widget.ImageView'
            self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
            self.panel_driver.find_element_by_xpath(xpath).click()
            self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/ok')))
            self.panel_driver.find_element_by_id('com.qolsys:id/ok').click()
        self.go_home()
        return True

    def assign_iq_remote_to_partition(self):
        print(1)

    def get_sensor_status(self , labels):
        sensors = self.get_sensors()
        output = {}
        for label in labels:
            output[label] = next((item for item in sensors if item["device_name"] == label) , {'device_status': False})['device_status']
        return output

    def get_sensors(self):
        self.go_to_sensor_status()
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/uiLV')))
        try:
            self.panel_driver.find_elements_by_xpath('//android.widget.ListView[@resource-id="com.qolsys:id/uiLV"]//android.widget.LinearLayout')
            device_ids = self.panel_driver.find_elements_by_id('com.qolsys:id/textView1')
            dl_ids = self.panel_driver.find_elements_by_id('com.qolsys:id/textView3')
            signal_sources = self.panel_driver.find_elements_by_id('com.qolsys:id/textView4')
            device_names = self.panel_driver.find_elements_by_id('com.qolsys:id/textView5')
            device_types = self.panel_driver.find_elements_by_id('com.qolsys:id/textView6')
            device_groups = self.panel_driver.find_elements_by_id('com.qolsys:id/textView7')
            devices_statuses = self.panel_driver.find_elements_by_id('com.qolsys:id/textView8')
            output = []
            for i , sensor in enumerate(device_names):
                output.append({
                    'device_name': sensor.text ,
                    'device_id': device_ids[i].text ,
                    'dl_id': dl_ids[i].text ,
                    'signal_source': signal_sources[i].text ,
                    'device_type': device_types[i].text ,
                    'device_group': device_groups[i].text ,
                    'device_status': devices_statuses[i].text
                })
        except Exception:
            output = []
        self.go_home()
        return output

    # navigate to the delete sensors page
    def go_to_delete_sensors(self):
        self.go_to_sensors()
        # click on delete sensors
        xpath = '//android.widget.TextView[' + self.xpath_translate('text' , 'delete sensor') + ']'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()

    # navigates to the delete sensors page and deletes all security sensors
    def delete_all_sensors(self):
        self.go_to_delete_sensors()
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/checkBox1")))
        checkboxes = self.panel_driver.find_elements_by_id("com.qolsys:id/checkBox1")
        for e in checkboxes:
            e.click()
            time.sleep(1)
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/btnDelete")))
        self.panel_driver.find_element_by_id("com.qolsys:id/btnDelete").click()
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/ok")))
        self.panel_driver.find_element_by_id("com.qolsys:id/ok").click()
        self.go_home()

    def delete_sensors(self , labels):
        self.go_to_delete_sensors()
        for label in labels:
            xpath = '//android.widget.ListView[@resource-id="com.qolsys:id/uiLV"]//android.widget.TextView[contains(@text,"' + label + '")]//..//android.widget.CheckBox[@resource-id="com.qolsys:id/checkBox1"]'
            self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
            self.panel_driver.find_element_by_xpath(xpath).click()
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/btnDelete")))
        self.panel_driver.find_element_by_id("com.qolsys:id/btnDelete").click()
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/ok")))
        self.panel_driver.find_element_by_id("com.qolsys:id/ok").click()
        self.go_home()

    # removes all powerg sensors from the panel
    def remove_powerg_sensors(self):
        self.go_to_sensors()
        # click on remove all powerg sensors
        xpath = '//android.widget.TextView[' + self.xpath_translate('text' , 'remove all powerg sensors') + ']'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()
        # click on OK button
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/ok")))
        self.panel_driver.find_element_by_id("com.qolsys:id/ok").click()
        # click on OK button
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/ok")))
        self.panel_driver.find_element_by_id("com.qolsys:id/ok").click()
        self.go_home()

    def confirm_countdown(self):
        try:
            # self.wait.until(ec.element_to_be_clickable((By.ID , "tv_timer_count")))
            self.panel_driver.find_element_by_id("tv_timer_count")
            try:
                partition_name = self.panel_driver.find_element_by_id("com.qolsys:id/tv_pt_name")
                return partition_name.text
            except Exception as e:
                return True
        except Exception as e:
            return False

    def confirm_exit_delay(self):
        try:
            self.panel_driver.find_element_by_id("com.qolsys:id/t3_exit_progress")
            return True
        except Exception as e:
            return False

    def get_dealer_settings(self):
        self.go_to_dealer_settings();
        dealer_settings_src = self.panel_driver.page_source
        print(dealer_settings_src)

    def enable_partitions(self):
        self.go_to_dealer_settings()
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/search_ET')))
        self.panel_driver.find_element_by_id('com.qolsys:id/search_ET').set_value('Partitions')
        self.wait.until(ec.element_to_be_clickable((By.XPATH , '//android.widget.TextView[contains(@text,"Partitions are currently Disabled")]')))
        self.panel_driver.find_element_by_xpath('//android.widget.TextView[@text="Partitions"]').click()
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/ok")))
        self.panel_driver.find_element_by_id("com.qolsys:id/ok").click()

    def disable_partitions(self):
        self.go_to_dealer_settings()
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/search_ET')))
        self.panel_driver.find_element_by_id('com.qolsys:id/search_ET').set_value('Partitions')
        self.wait.until(ec.element_to_be_clickable((By.XPATH , '//android.widget.TextView[contains(@text,"Partitions are currently Enabled")]')))
        self.panel_driver.find_element_by_xpath('//android.widget.TextView[@text="Partitions"]').click()
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/ok")))
        self.panel_driver.find_element_by_id("com.qolsys:id/ok").click()

    def go_to_bluetooth_devices(self):
        self.go_to_installation()
        # click on Devices
        xpath = '//android.widget.TextView[' + self.xpath_translate('text' , 'devices') + ']'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()
        # click on Bluetooth Devices
        xpath = '//android.widget.TextView[' + self.xpath_translate('text' , 'bluetooth devices') + ']'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()

    def enable_bluetooth_disarm(self):
        self.go_to_bluetooth_devices()
        xpath = '//android.widget.TextView[' + self.xpath_translate('text' , 'settings') + ']'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()
        self.wait.until(ec.element_to_be_clickable((By.XPATH , '//android.widget.TextView[contains(@text,"Automatic Bluetooth Disarming is Disabled")]')))
        self.panel_driver.find_element_by_xpath('//android.widget.TextView[contains(@text,"Automatic Bluetooth Disarming is Disabled")]').click()
        self.go_home()

    def disable_bluetooth_disarm(self):
        self.go_to_bluetooth_devices()
        xpath = '//android.widget.TextView[' + self.xpath_translate('text' , 'settings') + ']'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()
        self.wait.until(ec.element_to_be_clickable((By.XPATH , '//android.widget.TextView[contains(@text,"Automatic Bluetooth Disarming is Enabled")]')))
        self.panel_driver.find_element_by_xpath('//android.widget.TextView[contains(@text,"Automatic Bluetooth Disarming is Enabled")]').click()
        self.go_home()

    def add_bluetooth_device(self , CustomerApp , partition=None):
        self.go_to_bluetooth_devices()
        CustomerApp.go_to_bluetooth_settings()
        xpath = '//android.widget.TextView[' + self.xpath_translate('text' , 'add phone') + ']'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/retry")))
        time.sleep(1)
        try:
            if self.panel_driver.find_element_by_id("com.qolsys:id/textView").text == CustomerApp.phone_name:
                self.panel_driver.find_element_by_id("com.qolsys:id/textView").click()
                self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/positive_button')))
                self.panel_driver.find_element_by_id('com.qolsys:id/positive_button').click()
                CustomerApp.pair_bluetooth()
                if partition is not None:
                    self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/partition_CheckBox')))
                    check_boxes = self.panel_driver.find_elements_by_id('com.qolsys:id/partition_CheckBox')
                    check_boxes[int(partition) - 1].click()
                self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/button')))
                self.panel_driver.find_element_by_id('com.qolsys:id/button').click()
                self.go_home()
                return True
        except Exception as e:
            print(e)
            return False

    def remove_bluetooth_devices(self):
        self.go_to_bluetooth_devices()
        xpath = '//android.widget.TextView[' + self.xpath_translate('text' , 'remove all devices') + ']'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/ok')))
        self.panel_driver.find_element_by_id('com.qolsys:id/ok').click()
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/ok')))
        self.panel_driver.find_element_by_id('com.qolsys:id/ok').click()
        self.go_home()

    def disable_siren(self):
        self.go_to_installation()
        xpath = '//android.widget.TextView[' + self.xpath_translate('text' , 'siren and alarms') + ']'
        self.wait.until(ec.element_to_be_clickable((By.XPATH , xpath)))
        self.panel_driver.find_element_by_xpath(xpath).click()
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/search_ET')))
        self.panel_driver.find_element_by_id('com.qolsys:id/search_ET').set_value('Panel Sirens')
        self.wait.until(ec.element_to_be_clickable((By.XPATH , '//android.widget.TextView[@text="Panel Sirens"]')))
        try:
            if self.panel_driver.find_element_by_xpath('//android.widget.TextView[@text="Currently all sirens are Enabled"]').text == "Currently all sirens are Enabled":
                self.panel_driver.find_element_by_xpath('//android.widget.TextView[@text="Panel Sirens"]').click()
                self.wait.until(ec.element_to_be_clickable((By.XPATH , '//android.widget.TextView[contains(@text,"INSTALLER/TEST MODE")]')))
                self.panel_driver.find_element_by_xpath('//android.widget.TextView[contains(@text,"INSTALLER/TEST MODE")]').click()
        except Exception as e:
            None
        self.go_home()

    def find_element_by_uiselector(self , text):
        try:
            self.panel_driver.find_element_by_android_uiautomator('new UiSelector().text(\"' + text + '\")')
            return
        except Exception as e:
            return False

    def confirm_lock_screen(self):
        try:
            self.panel_driver.find_element_by_id("com.qolsys:id/partitionName")
            return True
        except Exception as e:
            return False

    def arm_stay_partition(self , partition):
        text = self.partitions[partition]
        time.sleep(1)
        command = "new UiScrollable(new UiSelector().scrollable(true).instance(0)).setMaxSearchSwipes(4).scrollIntoView(new UiSelector().textContains(\"" + text + "\").instance(0))"
        self.panel_driver.find_element_by_android_uiautomator(command).click()
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/img_arm_stay")))
        self.panel_driver.find_element_by_id("com.qolsys:id/img_arm_stay").click()

    def arm_away_partition(self , partition):
        text = self.partitions[partition]
        time.sleep(1)
        command = "new UiScrollable(new UiSelector().scrollable(true).instance(0)).setMaxSearchSwipes(4).scrollIntoView(new UiSelector().textContains(\"" + text + "\").instance(0))"
        self.panel_driver.find_element_by_android_uiautomator(command).click()
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/img_arm_away")))
        self.panel_driver.find_element_by_id("com.qolsys:id/img_arm_away").click()

    def global_arm_stay(self):
        partition = "1"
        if self.find_partition_status(partition) == "DISARMED":
            try:
                self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/t3_img_disarm")))
                self.panel_driver.find_element_by_id("com.qolsys:id/t3_img_disarm").click()
                self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/select_all_partitions")))
                self.panel_driver.find_element_by_id("com.qolsys:id/select_all_partitions").click()
                self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/img_arm_stay")))
                self.panel_driver.find_element_by_id("com.qolsys:id/img_arm_stay").click()
            except Exception as e:
                return False
        else:
            return False

    def global_arm_away(self):
        partition = "1"
        if self.find_partition_status(partition) == "DISARMED":
            try:
                self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/t3_img_disarm")))
                self.panel_driver.find_element_by_id("com.qolsys:id/t3_img_disarm").click()
                self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/select_all_partitions")))
                self.panel_driver.find_element_by_id("com.qolsys:id/select_all_partitions").click()
                self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/img_arm_away")))
                self.panel_driver.find_element_by_id("com.qolsys:id/img_arm_away").click()
            except Exception as e:
                return False
        else:
            return False

    def disarm_partition(self , partition):
        text = self.partitions[partition]
        command = "new UiScrollable(new UiSelector().scrollable(true).instance(0)).setMaxSearchSwipes(4).scrollIntoView(new UiSelector().textContains(\"" + text + "\").instance(0))"
        time.sleep(1)
        if self.find_partition_status(partition) != "DISARMED":
            self.panel_driver.find_element_by_android_uiautomator(command).click()
            time.sleep(1)
            self.enter_pin(self.admin_code)
            return True
        else:
            return False

    def find_partition_status(self , partition):
        text = self.partitions[partition]
        command = "new UiScrollable(new UiSelector().scrollable(true).instance(0)).setMaxSearchSwipes(4).scrollIntoView(new UiSelector().textContains(\"" + text + "\").instance(0))"
        time.sleep(1)
        self.panel_driver.find_element_by_android_uiautomator(command)
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/t3_tv_disarm")))
        return self.panel_driver.find_element_by_id("com.qolsys:id/t3_tv_disarm").text

    def confirm_cam_video_loaded(self):
        counter = 0
        while counter < 100:
            try:
                self.panel_driver.find_element_by_id('com.qolsys:id/close_streaming')
                break
            except Exception:
                None
            counter += 1
            time.sleep(0.3)
        time.sleep(3)
        if self.check_stream_failed():
            return False
        self.panel_driver.find_element_by_id('com.qolsys:id/close_streaming').click()
        try:
            page = self.panel_driver.find_element_by_id('com.qolsys:id/tv_name')
            if page.text == "LIVE VIDEO CAMERAS":
                return True
            else:
                time.sleep(0.3)
        except Exception:
            time.sleep(0.3)
        return False

    def play_cam_stream(self):
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/leftPlayIcon')))
        self.panel_driver.find_element_by_id('com.qolsys:id/leftPlayIcon').click()

    def confirm_db_video_loaded(self):
        counter = 0
        while counter < 100:
            try:
                self.panel_driver.find_element_by_id('com.qolsys:id/close_session').click()
                break
            except Exception as e:
                None
            counter += 1
            time.sleep(0.3)
        try:
            page = self.panel_driver.find_element_by_id('com.qolsys:id/tv_name')
            if page.text == "LIVE VIDEO CAMERAS":
                return True
            else:
                time.sleep(0.3)
        except Exception as e:
            time.sleep(0.3)
        return False

    def swipe_right(self):
        self.wait.until(ec.element_to_be_clickable((By.ID , 'android:id/content')))
        TouchAction(self.panel_driver).press(x=1078 , y=374).move_to(x=131 , y=364).release().perform()
        return True

    def scroll_to_live_videos(self):
        while True:
            self.swipe_right()
            try:
                self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/tv_name')))
            except:
                pass
            try:
                if self.panel_driver.find_element_by_id('com.qolsys:id/tv_name').text == "LIVE VIDEO CAMERAS":
                    return True
            except:
                pass
            time.sleep(3)

    def scroll_to_locks(self):
        while True:
            self.swipe_right()
            try:
                self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/door_view_pager')))
                page = self.panel_driver.find_element_by_id('com.qolsys:id/door_view_pager')
                lock = page.find_element_by_id('doorLockName')
                if "FRONT DOOR" in lock.text:
                    return True
                time.sleep(3)
            except Exception as e:
                time.sleep(3)

    def read_lock_status(self):
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/doorLockStatus")))
        return self.panel_driver.find_element_by_id("com.qolsys:id/doorLockStatus").text

    def read_garage_door_status(self):
        self.wait.until(ec.element_to_be_clickable((By.ID , "com.qolsys:id/doorLockStatus")))
        return self.panel_driver.find_element_by_id("com.qolsys:id/doorLockStatus").text

    def lock_door(self):
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/doorStatusbutton')))
        self.panel_driver.find_element_by_id("com.qolsys:id/doorStatusbutton").click()
        while self.read_lock_status() != "LOCKED":
            time.sleep(0.3)
        return True

    def unlock_door(self):
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/doorStatusbutton')))
        self.panel_driver.find_element_by_id("com.qolsys:id/doorStatusbutton").click()
        while self.read_lock_status() != "UNLOCKED":
            time.sleep(0.3)
        return True

    def scroll_to_garage_doors(self):
        while True:
            self.swipe_right()
            try:
                self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/door_view_pager')))
                page = self.panel_driver.find_element_by_id('com.qolsys:id/door_view_pager')
                if "GARAGE DOOR" in page.find_element_by_id('doorLockName').text:
                    return True
                time.sleep(3)
            except Exception as e:
                time.sleep(3)

    def toggle_garage(driver):
        wait = WebDriverWait(driver , 120 , poll_frequency=1 ,
                             ignored_exceptions=[ElementNotVisibleException , NoSuchElementException ,
                                                 TimeoutException])
        wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/doorStatusbutton')))
        driver.find_element_by_id("com.qolsys:id/doorStatusbutton").click()

    def scroll_to_lights(self):
        while True:
            self.swipe_right()
            try:
                self.panel_driver.find_element_by_id('com.qolsys:id/uiTvlights')
                return True
            except Exception as e:
                time.sleep(3)

    def select_all_lights(self):
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/selectallbtn')))
        self.panel_driver.find_element_by_id('com.qolsys:id/selectallbtn').click()

    def turn_on_all_lights(self):
        self.select_all_lights()
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/allOn')))
        self.panel_driver.find_element_by_id('com.qolsys:id/allOn').click()

    def turn_off_all_lights(self):
        self.select_all_lights()
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/allOff')))
        self.panel_driver.find_element_by_id('com.qolsys:id/allOff').click()

    def refresh_light_status(self):
        self.select_all_lights()
        self.wait.until(ec.element_to_be_clickable((By.ID , 'com.qolsys:id/getStatusButton')))
        self.panel_driver.find_element_by_id('com.qolsys:id/getStatusButton').click()

    def check_panel_notification(self):
        try:
            return self.panel_driver.find_element_by_id("com.qolsys:id/tv_msg").text
        except Exception as e:
            return False

    def dismiss_doorbell(self):
        try:
            self.panel_driver.find_element_by_id("com.qolsys:id/negative_button").click()
            return True
        except Exception as e:
            return False

    def check_alarm_screen(self):
        try:
            alarm = self.panel_driver.find_element_by_id("com.qolsys:id/txt_title").text
            if self.panel_driver.find_element_by_id("com.qolsys:id/txt_title").text == "ALARM":
                try:
                    partition = self.panel_driver.find_element_by_id("com.qolsys:id/partition_name")
                    partition_name = partition.find_element_by_id("android:id/text1").text
                    return partition_name[5:]
                except Exception as e:
                    return True
            # ALâ€ŠARM
            elif alarm == "AL ARM":
                return True
            else:
                return False
        except Exception as e:
            return False
        return False

    def confirm_db_panel_notification(self , w):
        counter = 0;
        while counter < 12000:
            text = self.check_panel_notification()
            if text == False:
                time.sleep(0.3)
                counter += 1
                continue
            if "RINGING" in text:
                break
            counter += 1
            time.sleep(0.3)
        if counter >= 2000:
            return False
        w.put({"panel": datetime.now()})
        return datetime.now()

    def confirm_sensor_status(self , w):
        counter = 0;
        while counter < 12000:
            text = self.check_sensor_status("Door-Window 1")
            if text == False or text is None:
                time.sleep(0.3)
                counter += 1
                continue
            if "Open" in text:
                break
            counter += 1
            time.sleep(0.3)
        if counter >= 12000:
            return False
        w.put({"panel": datetime.now()})
        return datetime.now()

    def confirm_panel_disarmed(self , a):
        counter = 0
        while counter < 12000:
            text = self.read_status()
            if text == False:
                time.sleep(1)
                counter += 1
                continue
            if text == "DISARMED":
                break
            counter += 1
            time.sleep(1)
        if counter >= 12000:
            return False
        a.put({"panel": datetime.now()})
        return datetime.now()

    def confirm_panel_garage_closed(self , a):
        counter = 0
        while counter < 12000:
            text = self.read_garage_door_status()
            if text == False:
                time.sleep(1)
                counter += 1
                continue
            if text == "CLOSED":
                break
            counter += 1
            time.sleep(1)
        if counter >= 12000:
            return False
        a.put({"panel": datetime.now()})
        return datetime.now()

    def check_stream_failed(self):
        error_string = 'Video device not responding, check power and network connection'
        try:
            if self.panel_driver.find_element_by_id("com.qolsys:id/tv_msg").text == error_string:
                return True
            else:
                return False
        except Exception as e:
            return False

    def close_stream(self):
        try:
            self.panel_driver.find_element_by_id("com.qolsys:id/close_streaming").click()
            return True
        except Exception as e:
            return False

