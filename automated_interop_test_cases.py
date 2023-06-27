from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException, NoAlertPresentException, ElementNotInteractableException
from selenium.webdriver.common.alert import Alert
import time
from tqdm import trange
import argparse
import SmartHomeSecurityAssets
import threading
from datetime import datetime

class testcases(object):
    t3200_gui_url = ""
    t3200_user_name = ""
    t3200_password = ""
    twh_user_name = ""
    twh_password = ""
    boostv2_user_name = ""
    boostv2_password = ""
    arcboostv2_gui_url = ""
    tchboostv2_user_name = ""
    tchboostv2_password = ""
    web_username = ""
    web_password = ""
    airties_SSID = ""
    airties_SSID_password = ""
    t3200SmartSteeringSSID = ""
    t3200_24SSID = ""
    t3200_5SSID = ""
    t3200SmartDeviceSSID = ""
    t3200_SSID_PW = ""
    t3200_SmartDeviceSSID_PW = ""
    boostSSID = ""
    boostSmartDeviceSSID = ""
    boost_SSID_PW = ""
    twh_gui_url = ""
    twh_SSID = ""
    twhSmartDeviceSSID = ""
    twh_SSID_PW = ""
    twhSmartDeviceSSIDPW = ""
    arcboostv2_SSID = ""
    arcboostv2SmartDeviceSSID24 = ""
    arcboostv2SmartDeviceSSID5 = ""
    arcboostv2_SSID_PW = ""
    arcboostv2SmartDeviceSSID_PW = ""
    tchboostv2SmartSteeringSSID = ""
    tchboostv2_24SSID = ""
    tchboostv2_5SSID = ""
    tchboostv2SmartDeviceSSID = ""
    tchboostv2_SSID_PW = ""
    ignored_exceptions = (StaleElementReferenceException,)

    def __init__(self, driver):
        self.driver = driver

    def logInToPartnerPortal(self, driver, pp_user_name, pp_password):
        try:
            driver.get("https://alarmadmin.alarm.com/HomeNew.aspx")
            element = driver.find_element_by_id("txtUsername")
            element.send_keys(pp_user_name)
            element = driver.find_element_by_id("txtPassword")
            element.send_keys(pp_password)
            element.send_keys(Keys.RETURN)
        except:
            return

    def logInToCustomerPortal(self, driver, cust_user_name, cust_password):
        driver.get("https://www.alarm.com/login.aspx")
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_loginform_txtUserName")))
        element.send_keys(cust_user_name)
        element = driver.find_element_by_xpath("""//*[@id="aspnetForm"]/div[4]/div[1]/div[1]/div/div[3]/input""")
        element.send_keys(cust_password)
        element.send_keys(Keys.RETURN)
        try:
            wait = WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.XPATH, """//*[@id="app-nav"]/div/nav/ul/li[8]/a/p""")))
        except:
            pass
        page_title = driver.title
        # print(page_title)
        try:
            assert page_title == "Home | TELUS SmartHome Security / Maison connectee"
            time.sleep(3)
        except AssertionError:
            time.sleep(3)
            page_title = driver.title

    def confirmPanelStream(self, Panel):
        counter = 0
        successMessage = "Success"
        failMessage = "Fail"
        while counter < 5:
            Panel.scroll_to_live_videos()
            Panel.play_cam_stream()
            if Panel.confirm_db_video_loaded():
                Panel.close_stream()
                while not Panel.confirm_lock_screen():
                    Panel.swipe_right()
                return successMessage
            else:
                if Panel.check_stream_failed():
                    Panel.close_stream()
                    counter += 1
        return failMessage

    def enterIFrame(self, driver):
        frame = driver.find_element_by_tag_name("iframe")
        driver.switch_to.frame(frame)
        return

    def cameraInstall(self, driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera, selectedCameraMAC, selectedCustomerID, selected_device_ID, model, Panel):
        self.logInToCustomerPortal(driver, cust_user_name, cust_password)
        driver.get("https://www.alarm.com/web/Video/AddVideoDevice.aspx") #Go to add video device page
        wait = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.ID, "app-content")))
        page_title = driver.title
        # print(page_title)
        # Get current fwv
        try:
            assert page_title == "Video Device Setup | TELUS SmartHome Security / Maison connectee"
            #print(page_title)
        except AssertionError:
            time.sleep(5)
            page_title = driver.title
        wait = WebDriverWait(driver, 5)
        self.enterIFrame(driver)
        try:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, """//*[@id="divAddVideoDeviceContainer"]/div[7]/a[1]"""))).click()
        except:
            pass
        try:
            element = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, "video-device-name-" + str(selectedCameraMAC))))
            element.send_keys(selectedCamera)
            element = WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.XPATH,"""//*[@id="divAddVideoDeviceContainer"]/div[4]/div[2]/div[2]/div[3]/div[2]/a[1]"""))).click()
        except TimeoutException:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, """//*[@id="ctl00_phBody_TextBoxMac"]""")))
            element.send_keys(selectedCameraMAC)
            element = driver.find_element_by_xpath(
                """//*[@id="divAddVideoDeviceContainer"]/div[8]/div/div/input""").click()
            installElementID = "video-device-name-" + str(selectedCameraMAC)
            element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID,installElementID)))
            element.send_keys(selectedCamera)
            #element = driver.find_element_by_xpath(
                #"""//*[@id="divAddVideoDeviceContainer"]/div[4]/div[2]/div[2]/div[3]/div[2]/a[1]""").click()
            element = driver.find_element_by_xpath(
            """//*[@id="deviceReadyModalBody"]/div/div/div[2]/div[3]/div[2]/a[1]""").click()
            element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
                (By.XPATH, """//*[@id="ctl00_modalPlaceholder_checkAndAddMacModal"]/div/div/div[3]/input"""))).click()
        for waitTime in trange(500, leave=False):
            try:
                element = WebDriverWait(driver, 10, ignored_exceptions=self.ignored_exceptions) \
                    .until(EC.presence_of_element_located(
                    (By.XPATH,
                     """//*[@id="divAddVideoDeviceContainer"]/div[4]/div[2]/div[2]/div[3]/div[1]/div[3]/div[1]/div[1]/span"""))).text
                # element = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.ID, "ctl00_phBody_ucsVideoDeviceManualFirmwareUpgrade_tbLog"))).text
                #if "READY" in element:
                if "Checking" in element:
                    break
                else:
                    time.sleep(1)
            except:
                continue
        for installTime in trange(600, leave=False):
            try:
                element = WebDriverWait(driver, 10, ignored_exceptions=self.ignored_exceptions) \
                    .until(EC.presence_of_element_located(
                    (By.XPATH,
                     """//*[@id="divAddVideoDeviceContainer"]/div[4]/div[2]/div[2]/div[1]/div[5]/div[2]/span[1]"""))).text
                # element = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.ID, "ctl00_phBody_ucsVideoDeviceManualFirmwareUpgrade_tbLog"))).text
                if "READY" in element:
                    print("Install completed in " + str(installTime) + " seconds")
                    break
                elif installTime == 599:
                    print("Install timed out. Exiting now")
                    driver.close()
                    exit()
                else:
                    time.sleep(1)
            except:
                continue
        driver.get("https://www.alarm.com/web/Video/SettingsOverview_V2.aspx")
        wait = time.sleep(5)
        try:
            self.enterIFrame(driver)
        except:
            wait = time.sleep(100)
            self.enterIFrame(driver)
        select = Select(
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "ctl00_phBody_CamSelector_ddlCams"))))
        select.select_by_visible_text(selectedCamera)
        driver.switch_to.default_content()
        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, """//*[@id="app-page"]/header/div[1]/div/button"""))) #find page refresh button
        element.click() #click on page refresh button
        time.sleep(5)
        try:
            self.enterIFrame(driver) #enter lower section of page
        except:
            time.sleep(100)
            self.enterIFrame(driver)
        if model == "ADC-VDB770":
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,
                                                """//*[@id="ctl00_phBody_mainPanel"]/div[3]/div[8]/div[2]/a""")))  # find stream to panel menu option
        elif model == "ADC-VDB750":
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,
                                                """//*[@id="ctl00_phBody_mainPanel"]/div[3]/div[6]/div[2]/a""")))  # find stream to panel menu option
        elif model == "ADC-V523" or "ADC-V723" or "ADC-V723X" or "ADC-V523X":
            #element = WebDriverWait(driver, 10).until(
                #EC.presence_of_element_located((By.XPATH, """//*[@id="ctl00_phBody_mainPanel"]/div[3]/div[8]/div[2]/a"""))) #find stream to panel menu option
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,
                                                """//*[@id="ctl00_phBody_mainPanel"]/div[3]/div[8]/div[2]/a/div[1]""")))  # find stream to panel menu option

        element.click() #click on stream to panel menu option
        driver.switch_to.default_content()
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, """//button[@class='btn btn-sm btn-link ember-view']"""))) #find stream to panel checkbox
        element.click() #click on stream to panel checkbox
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, """//button[@class='btn btn-primary ember-view']"""))) #Find submit button
        element.click() #click on submit button
        driver.get("https://www.alarm.com/web/system/video/live-view?cameraGroupId=all")
        print("Please verify live stream on portal and on panel")
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, """//*[@id="player-99672440-2070"]/div/div[2]/div[1]/div[1]/div[1]/label[1]""")))  # find loading button to show load
        except:
            pass
        try:
            element = WebDriverWait(driver, 20).until(
                EC.invisibility_of_element_located(
                    (By.XPATH, """//*[@id="player-99672440-2070"]/div/div[2]/div[1]/div[1]/div[1]/label[1]""")))  # find loading button to show load
            webStream = "Success"
        except:
            webStream = "Fail"
        print("Live view on web: " + webStream)
        return installTime, webStream

    def panelTest(self, Panel):
        time.sleep(25)
        panelStream = self.confirmPanelStream(Panel)
        print("Live view on panel: " + panelStream)
        return panelStream

    def updateCameraSettings(self, selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID):
        print("Updating camera wifi")
        adcapi = SmartHomeSecurityAssets.WebServicesAPI(dealer_ID)
        adcapi.authenticate()
        adcapi.create_camera_wifi_settings_input()
        wifi_credentials = {
            "ssid": SSID,
            "password": gwPassword,
            "encryption": "Wpa2",
            "encryption_algorithm": "Aes"
        }
        test = adcapi.set_camera_wifi(selectedCustomerID, selectedCameraMAC, wifi_credentials)
        return test
        # if "True" in test:
        #     return
        # else:
        #     fail_string = "Setting wifi credentials failed"
        #     return fail_string

    def updatePanelSettings(self, selectedCustomerID, panelID, SSID, gwPassword, dealer_ID):
        print("Connecting panel to " + SSID)
        adcapi = SmartHomeSecurityAssets.WebServicesAPI(dealer_ID)
        adcapi.authenticate()
        adcapi.create_wifi_input()
        wifi_credentials = {
            "ssid": SSID,
            "password": gwPassword,
            "encryption": "Wpa2",
            "encryption_algorithm": "Aes"
        }
        test = adcapi.set_wifi(selectedCustomerID, panelID, wifi_credentials)
        return test

    def deleteCamera(self, driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera):
        print("Deleting camera")
        self.logInToPartnerPortal(driver, pp_user_name, pp_password)
        driver.get("https://alarmadmin.alarm.com/Support/CameraInfo.aspx?customer_id=" + selectedCustomerID + "&device_id=" + selected_device_ID)
        wait = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,"""//*[@id="ctl00_phBody_drpCamera"]""")))
        element = driver.find_element_by_xpath("""//*[@id="content_container"]/div/div[2]/table/tbody/tr[1]/td[2]/span""").text
        try:
            assert element == selectedCamera
            time.sleep(3)
        except AssertionError:
            select = Select(driver.find_element_by_xpath("""//*[@id="ctl00_phBody_drpCamera"]"""))
            select.select_by_visible_text(selectedCamera)
            wait = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, """//*[@id="content_container"]/div/div[1]/input[4]""")))
        select = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, """//*[@id="content_container"]/div/div[1]/input[4]"""))).click()
        time.sleep(2)
        alert = Alert(driver)
        try:
            alert.accept()
            time.sleep(2)
        except NoAlertPresentException:
            time.sleep(2)
            pass
        return

    def rebootCamera(self, driver, selectedCustomerID, selected_device_ID):
        print("Rebooting camera")
        driver.get("https://alarmadmin.alarm.com/Support/CameraInfo.aspx?customer_id=" + selectedCustomerID + "&device_id=" + selected_device_ID)
        wait = WebDriverWait(driver, 5)
        select = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, """//*[@id="content_container"]/div/div[1]/input[2]"""))).click()
        time.sleep(2)
        alert = Alert(driver)
        try:
            alert.accept()
        except NoAlertPresentException:
            pass
        return

    def openT3200GUI(self, driver):
        print("Navigating to Gateway GUI")
        driver.get(self.t3200_gui_url + "/index.html")
        page_title = driver.title
        try:
            assert page_title == "Home"
            time.sleep(3)
        except AssertionError:
            time.sleep(3)
            driver.get(self.t3200_gui_url + "/index.html")
            page_title = driver.title

    def openTWHGUI(self, driver):
        print("Navigating to Gateway GUI")
        driver.get(self.twh_gui_url +"/index.htm")
        #driver.get("http://192.168.3.254/index.htm")
        page_title = driver.title
        try:
            assert page_title == "Telus"
            time.sleep(3)
        except AssertionError:
            time.sleep(3)
            driver.get(self.twh_gui_url + "/index.htm")
            #driver.get("http://192.168.3.254/index.htm")
            page_title = driver.title

    def openARCBoostv2GUI(self, driver):
        print("Navigating to Gateway GUI")
        driver.get (self.arcboostv2_gui_url + "/index.htm")

    def openTCHBoostv2GUI(self, driver):
        print("Navigating to Gateway GUI")
        driver.get("http://192.168.5.3")

    def openWebGUI(self, driver):
        print("Navigating to Gateway GUI")
        driver.get("http://192.168.1.64/main.html")


    def testWifiConnection(self, dealer_ID, selectedCameraMAC):
        print("Testing Wifi Reconnect")
        result = False
        while not result:
            adcapi = SmartHomeSecurityAssets.WebServicesAPI(dealer_ID)
            adcapi.authenticate()
            adcapi.create_test_connectivity_input()
            test = adcapi.test_video_device_connection(selectedCameraMAC)
            result = test['Success']
            print(result)
            if result:
                print("Successful Wi-Fi connection")
                return result
            else:
                time.sleep(5)

    def t3200testcase(self, driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera, selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID, log_file, model, Panel, panelID):
        print("Starting install on T3200M - SmartSteering")
        smartsteeringTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cameraInstall, webStream, = self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera, selectedCameraMAC, selectedCustomerID, selected_device_ID, model, Panel)
        t3200SmartSteeringPanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.t3200SmartDeviceSSID, self.t3200_SmartDeviceSSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        t3200SmartDevicePanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.boostSSID, self.boost_SSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        boostDataPanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.boostSmartDeviceSSID, self.boost_SSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        boostSmartDevicePanelStream = self.panelTest(Panel)
        print("Successful camera install on T3200 - SmartSteering")
        with open(log_file, 'a',newline='') as f:
            print(smartsteeringTime, file=f, end="")
            print(",", file=f, end="")
            print("SmartSteering", file=f, end="")
            print(",", file=f, end="")
            print(str(cameraInstall), file=f, end="")
            print(",", file=f, end="")
            print(str(webStream), file=f, end="")
            print(",", file=f, end="")
            print(str(t3200SmartSteeringPanelStream), file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print(str(t3200SmartDevicePanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(boostDataPanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(boostSmartDevicePanelStream), file=f, end="")
            print(",", file=f, end="")
            print("Pass" + "\n", file=f, end="")
        SSID, gwPassword = self.t3200_24SSID, self.t3200_SSID_PW
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                                                args=(
                                                    selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        self.openT3200GUI(driver)
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, """//*[@id="admin_user_name"]""")))
            element.send_keys(self.t3200_user_name)
            element = driver.find_element_by_xpath("""//*[@id="admin_password"]""")
            element.send_keys(self.t3200_password)
            element.send_keys(Keys.RETURN)
        except:
            pass
        driver.get(self.t3200_gui_url + "/wirelesssetup_band_steering.html")
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "off")))
        element.click()
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btn_apply")))
        element.click()
        time.sleep(2)
        alert = Alert(driver)
        try:
            alert.accept()
        except NoAlertPresentException:
            pass
        self.testWifiConnection(dealer_ID, selectedCameraMAC)
        print("Starting install on T3200M - 2.4G")
        twofourtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cameraInstall, webStream = self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera, selectedCameraMAC, selectedCustomerID, selected_device_ID, model, Panel)
        t320024GHzPanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.t3200_5SSID, self.t3200_SSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        t32005GHzPanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.t3200SmartDeviceSSID, self.t3200_SmartDeviceSSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        t3200SmartDevicePanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.boostSSID, self.boost_SSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        boostDataPanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.boostSmartDeviceSSID, self.boost_SSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        boostSmartDevicePanelStream = self.panelTest(Panel)
        print("Successful camera install on T3200 - 2.4")
        with open(log_file, 'a',newline='') as f:
            print(twofourtime, file=f, end="")
            print(",", file=f, end="")
            print("2.4GHz", file=f, end="")
            print(",", file=f, end="")
            print(str(cameraInstall), file=f, end="")
            print(",", file=f, end="")
            print(str(webStream), file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print(str(t320024GHzPanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(t32005GHzPanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(t3200SmartDevicePanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(boostDataPanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(boostSmartDevicePanelStream), file=f, end="")
            print(",", file=f, end="")
            print("Pass" + "\n", file=f, end="")
        SSID, gwPassword = self.t3200_5SSID, self.t3200_SSID_PW
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                                                args=(
                                                    selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        self.testWifiConnection(dealer_ID, selectedCameraMAC)
        print("Starting install on T3200M - 5GHz")
        fivetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cameraInstall, webStream = self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera, selectedCameraMAC, selectedCustomerID, selected_device_ID, model, Panel)
        t32005GHzPanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.t3200_24SSID, self.t3200_SSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        t320024GHzPanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.t3200SmartDeviceSSID, self.t3200_SmartDeviceSSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        t3200SmartDevicePanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.boostSSID, self.boost_SSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        boostDataPanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.boostSmartDeviceSSID, self.boost_SSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        boostSmartDevicePanelStream = self.panelTest(Panel)
        print("Successful camera install on T3200 - 5GHz")
        with open(log_file, 'a',newline='') as f:
            print(fivetime, file=f, end="")
            print(",", file=f, end="")
            print("5GHz", file=f, end="")
            print(",", file=f, end="")
            print(str(cameraInstall), file=f, end="")
            print(",", file=f, end="")
            print(str(webStream), file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print(str(t320024GHzPanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(t32005GHzPanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(t3200SmartDevicePanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(boostDataPanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(boostSmartDevicePanelStream), file=f, end="")
            print(",", file=f, end="")
            print("Pass" + "\n", file=f, end="")
        SSID, gwPassword = self.t3200SmartDeviceSSID, self.t3200_SmartDeviceSSID_PW
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                                                args=(
                                                    selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        self.testWifiConnection(dealer_ID, selectedCameraMAC)
        print("Starting install on T3200M - SmartHome SSID")
        shstime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cameraInstall, webStream = self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera, selectedCameraMAC, selectedCustomerID, selected_device_ID, model, Panel)
        t3200SmartDevicePanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.t3200_24SSID, self.t3200_SSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        t320024GHzPanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.t3200_5SSID, self.t3200_SSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        t32005GHzPanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.boostSSID, self.boost_SSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        boostDataPanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.boostSmartDeviceSSID, self.boost_SSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        boostSmartDevicePanelStream = self.panelTest(Panel)
        print("Successful camera install on T3200 - SmartHomeSSID")
        with open(log_file, 'a',newline='') as f:
            print(shstime, file=f, end="")
            print(",", file=f, end="")
            print("Smart Device", file=f, end="")
            print(",", file=f, end="")
            print(str(cameraInstall), file=f, end="")
            print(",", file=f, end="")
            print(str(webStream), file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print(str(t320024GHzPanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(t32005GHzPanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(t3200SmartDevicePanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(boostDataPanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(boostSmartDevicePanelStream), file=f, end="")
            print(",", file=f, end="")
            print("Pass" + "\n", file=f, end="")
        SSID, gwPassword = self.boostSSID, self.boost_SSID_PW
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                                                args=(
                                                    selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        self.testWifiConnection(dealer_ID, selectedCameraMAC)
        print("Starting install on T3200M + Boostv1 - Data SSID")
        boosttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cameraInstall, webStream = self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera, selectedCameraMAC, selectedCustomerID, selected_device_ID, model, Panel)
        boostDataPanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.t3200_24SSID, self.t3200_SSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        t320024GHzPanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.t3200_5SSID, self.t3200_SSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        t32005GHzPanelStream= self.panelTest(Panel)
        SSID, gwPassword = self.t3200SmartDeviceSSID, self.t3200_SmartDeviceSSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        t3200SmartDevicePanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.boostSmartDeviceSSID, self.boost_SSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        boostSmartDevicePanelStream = self.panelTest(Panel)
        print("Successful camera install on T3200 +Boostv1 - Data SSID")
        with open(log_file, 'a', newline='') as f:
            print(boosttime, file=f, end="")
            print(",", file=f, end="")
            print("Boost - Data", file=f, end="")
            print(",", file=f, end="")
            print(str(cameraInstall), file=f, end="")
            print(",", file=f, end="")
            print(str(webStream), file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print(str(t320024GHzPanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(t32005GHzPanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(t3200SmartDevicePanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(boostDataPanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(boostSmartDevicePanelStream), file=f, end="")
            print(",", file=f, end="")
            print("Pass" + "\n", file=f, end="")
        SSID, gwPassword = self.boostSmartDeviceSSID, self.boost_SSID_PW
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                                                args=(
                                                    selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        self.testWifiConnection(dealer_ID, selectedCameraMAC)
        print("Starting install on T3200M + Boostv1 - SmartHome SSID")
        boostshstime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cameraInstall, webStream = self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera, selectedCameraMAC, selectedCustomerID, selected_device_ID, model, Panel)
        boostSmartDevicePanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.t3200_24SSID, self.t3200_SSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        t320024GHzPanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.t3200_5SSID, self.t3200_SSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        t32005GHzPanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.t3200SmartDeviceSSID, self.t3200_SmartDeviceSSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        t3200SmartDevicePanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.boostSSID, self.boost_SSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        boostDataPanelStream = self.panelTest(Panel)
        print("Successful camera install on T3200 + Boostv1 - SmartHomeSSID")
        with open(log_file, 'a', newline='') as f:
            print(boostshstime, file=f, end="")
            print(",", file=f, end="")
            print("Boost - Smart Device", file=f, end="")
            print(",", file=f, end="")
            print(str(cameraInstall), file=f, end="")
            print(",", file=f, end="")
            print(str(webStream), file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print(str(t320024GHzPanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(t32005GHzPanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(t3200SmartDevicePanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(boostDataPanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(boostSmartDevicePanelStream), file=f, end="")
            print(",", file=f, end="")
            print("Pass" + "\n", file=f, end="")
        print("restoring settings to beginning")
        SSID, gwPassword = self.t3200SmartSteeringSSID, self.t3200_SSID_PW
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                                                args=(
                                                    selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        self.openT3200GUI(driver)
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, """//*[@id="admin_user_name"]""")))
            element.send_keys(self.t3200_user_name)
            element = driver.find_element_by_xpath("""//*[@id="admin_password"]""")
            element.send_keys(self.t3200_password)
            element.send_keys(Keys.RETURN)
        except TimeoutException:
            pass
        driver.get(self.t3200_gui_url + "/wirelesssetup_band_steering.html")
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "on")))
        element.click()
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btn_apply")))
        element.click()
        time.sleep(2)
        alert = Alert(driver)
        try:
            alert.accept()
        except NoAlertPresentException:
            pass
        self.testWifiConnection(dealer_ID, selectedCameraMAC)

    def t3200webtestcase(self, driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera, selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID, log_file, model):
        print("Starting install on T3200M - SmartSteering")
        self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera, selectedCameraMAC, selectedCustomerID, selected_device_ID, model)
        print("Successful camera install on T3200 - SmartSteering")
        SSID, gwPassword = "WiFiPlus6547-2.4G", "tsecurity1"
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                                                args=(
                                                    selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        self.openT3200GUI(driver)
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, """//*[@id="admin_user_name"]""")))
        element.send_keys(self.t3200_user_name)
        element = driver.find_element_by_xpath("""//*[@id="admin_password"]""")
        element.send_keys(self.t3200_password)
        element.send_keys(Keys.RETURN)
        driver.get("http://192.168.1.254/wirelesssetup_band_steering.html")
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "off")))
        element.click()
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btn_apply")))
        element.click()
        time.sleep(2)
        alert = Alert(driver)
        try:
            alert.accept()
        except NoAlertPresentException:
            pass
        self.testWifiConnection(dealer_ID, selectedCameraMAC)
        print("Starting install on T3200M - 2.4G")
        self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                           selectedCameraMAC, selectedCustomerID, selected_device_ID, model)
        print("Successful camera install on T3200 - 2.4")
        SSID, gwPassword = "WiFiPlus6547-5G", "tsecurity1"
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                                                args=(
                                                    selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        self.testWifiConnection(dealer_ID, selectedCameraMAC)
        print("Starting install on T3200M - 5GHz")
        self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                           selectedCameraMAC, selectedCustomerID, selected_device_ID,model)
        print("Successful camera install on T3200 - 5GHz")
        # SSID, gwPassword = "TELUSSmartDevice5432", "f8fc9a74ce08c4"
        # updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
        #                                         args=(
        #                                             selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        # updateCameraSettings.start()
        # self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        # self.testWifiConnection(dealer_ID, selectedCameraMAC)
        # print("Starting install on T3200M - SmartHome SSID")
        # self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
        #                    selectedCameraMAC, selectedCustomerID, selected_device_ID,model)
        # print("Successful camera install on T3200 - SmartHomeSSID")

    def twhtestcase(self, driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                      selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID, log_file,model,Panel, panelID):
        print("Starting install on TWH - SmartSteering")
        smartsteeringTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.testWifiConnection(dealer_ID,selectedCameraMAC)
        cameraInstall, webStream = self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera, selectedCameraMAC, selectedCustomerID, selected_device_ID, model, Panel)
        twhSmartSteeringPanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.twhSmartDeviceSSID, self.twhSmartDeviceSSIDPW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        twhSmartDeviceSSIDPanelStream = self.panelTest(Panel)
        print("Successful camera install on TWH - SmartSteering")
        with open(log_file, 'a',newline='') as f:
            print(smartsteeringTime, file=f, end="")
            print(",", file=f, end="")
            print("SmartSteering", file=f, end="")
            print(",", file=f, end="")
            print(str(cameraInstall), file=f, end="")
            print(",", file=f, end="")
            print(str(webStream), file=f, end="")
            print(",", file=f, end="")
            print(str(twhSmartSteeringPanelStream), file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print(str(twhSmartDeviceSSIDPanelStream), file=f, end="")
            print(",", file=f, end="")
            print("Pass" + "\n", file=f, end="")
        SSID, gwPassword = self.twh_SSID, self.twh_SSID_PW
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                             args=(selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        #updateCameraSettings = self.updateCameraSettings(selectedCustomerID, selectedCameraMAC, SSID, gwPassword,
                                                         #dealer_ID)
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        self.openTWHGUI(driver)
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, """//*[@id="login_field"]/table/tbody/tr[3]/td[3]/span/div/div/input""")))
        element.send_keys(self.twh_user_name)
        element = driver.find_element_by_xpath("""//*[@id="login_field"]/table/tbody/tr[4]/td[3]/span/div/div/input""")
        element.send_keys(self.twh_password)
        element.send_keys(Keys.RETURN)
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "group_2"))) #select wifi tab
        element.click()
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "idx_42"))) #select 5GHz tab
        element.click() #Click on 5GHz tab
        self.enterIFrame(driver)
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, """//*[@id="contentbody"]/form/table/tbody/tr[1]/td/table/tbody/tr[1]/td[2]/div/div/a"""))).click() #select dropdown
        driver.find_element_by_xpath(
            """//*[@id="contentbody"]/form/table/tbody/tr[1]/td/table/tbody/tr[1]/td[2]/div/ul/li[1]/a""").click() #select 5g-l
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, """//*[@id="contentbody"]/form/table/tbody/tr[1]/td/table/tbody/tr[2]/td[2]/span[2]/a""")))
        element.click()  # Click on 5GHz low off
        alert = Alert(driver)
        try:
            time.sleep(1)
            alert.accept()
        except NoAlertPresentException:
            pass
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, """//*[@id="save"]/span[2]""")))
        element.click()  # Click on save settings
        time.sleep(60)
        element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH,
                                        """//*[@id="contentbody"]/form/table/tbody/tr[1]/td/table/tbody/tr[1]/td[2]/div/div/a"""))).click()  # select dropdown
        driver.find_element_by_xpath(
            """//*[@id="contentbody"]/form/table/tbody/tr[1]/td/table/tbody/tr[1]/td[2]/div/ul/li[2]/a""").click()  # select 5g-h
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, """//*[@id="contentbody"]/form/table/tbody/tr[1]/td/table/tbody/tr[2]/td[2]/span[2]/a""")))
        element.click()  # Click on 5GHz low off
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, """//*[@id="save"]/span[2]""")))
        element.click()  # Click on save settings
        time.sleep(60)
        print("Starting install on TWH - 2.4G")
        twofourtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.testWifiConnection(dealer_ID, selectedCameraMAC)
        cameraInstall, webStream = self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera, selectedCameraMAC, selectedCustomerID, selected_device_ID, model, Panel)
        twh24GHzPanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.twhSmartDeviceSSID, self.twhSmartDeviceSSIDPW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        twhSmartDeviceSSIDPanelStream = self.panelTest(Panel)
        print("Successful camera install on TWH - 2.4")
        with open(log_file, 'a') as f:
            print(twofourtime, file=f, end="")
            print(",", file=f, end="")
            print("2.4GHz", file=f, end="")
            print(",", file=f, end="")
            print(str(cameraInstall), file=f, end="")
            print(",", file=f, end="")
            print(str(webStream), file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print(str(twh24GHzPanelStream), file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print(str(twhSmartDeviceSSIDPanelStream), file=f, end="")
            print(",", file=f, end="")
            print("Pass" + "\n", file=f, end="")
        SSID, gwPassword = self.twh_SSID, self.twh_SSID_PW
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                                                args=(
                                                selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        self.openTWHGUI(driver) #adjust settings to 5GHz only
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, """//*[@id="login_field"]/table/tbody/tr[3]/td[3]/span/div/div/input""")))
            element.send_keys(self.twh_user_name)
            element = driver.find_element_by_xpath("""//*[@id="login_field"]/table/tbody/tr[4]/td[3]/span/div/div/input""")
            element.send_keys(self.twh_password)
            element.send_keys(Keys.RETURN)
        except:
            pass
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "group_2"))) #select wifi tab
        element.click()
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "idx_42")))
        element.click()  # Click on 5GHz tab
        self.enterIFrame(driver)
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                                        """//*[@id="contentbody"]/form/table/tbody/tr[1]/td/table/tbody/tr[1]/td[2]/div/div/a"""))).click()  # select dropdown
        driver.find_element_by_xpath(
            """//*[@id="contentbody"]/form/table/tbody/tr[1]/td/table/tbody/tr[1]/td[2]/div/ul/li[1]/a""").click()  # select 5g-l
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, """//*[@id="contentbody"]/form/table/tbody/tr[1]/td/table/tbody/tr[2]/td[2]/span[1]/a""")))
        element.click()  # Click on 5GHz low off
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, """//*[@id="save"]/span[2]""")))
        element.click()  # Click on save settings
        time.sleep(60)
        element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH,
                                        """//*[@id="contentbody"]/form/table/tbody/tr[1]/td/table/tbody/tr[1]/td[2]/div/div/a"""))).click()  # select dropdown
        driver.find_element_by_xpath(
            """//*[@id="contentbody"]/form/table/tbody/tr[1]/td/table/tbody/tr[1]/td[2]/div/ul/li[2]/a""").click()  # select 5g-h
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, """//*[@id="contentbody"]/form/table/tbody/tr[1]/td/table/tbody/tr[2]/td[2]/span[1]/a""")))
        element.click()  # Click on 5GHz low off
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, """//*[@id="save"]/span[2]""")))
        element.click()  # Click on save settings
        time.sleep(60) #allow GUI 60s for WLAN sync
        driver.switch_to.default_content() #enter top part of page
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "idx_41"))) #open 2.4G tab
        element.click()  # Click on 2.4GHz tab
        self.enterIFrame(driver) #enter lowersection of page
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, """//*[@id="contentbody"]/form/table/tbody/tr[1]/td/table/tbody/tr[1]/td[2]/span[2]/a"""))) #find 5g-l off button
        element.click()  # Click on 5GHz low off
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, """//*[@id="save"]/span[2]"""))) #find save button
        element.click()  # Click on save settings
        time.sleep(60)
        print("Starting install on TWH - 5G")
        fiveTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.testWifiConnection(dealer_ID, selectedCameraMAC)
        cameraInstall, webStream = self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera, selectedCameraMAC, selectedCustomerID, selected_device_ID, model, Panel)
        twh5GHzPanelStream = self.panelTest(Panel)
        print("Successful camera install on TWH - 5G")
        with open(log_file, 'a') as f:
            print(fiveTime, file=f, end="")
            print(",", file=f, end="")
            print("5G", file=f, end="")
            print(",", file=f, end="")
            print(str(cameraInstall), file=f, end="")
            print(",", file=f, end="")
            print(str(webStream), file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print(str(twh5GHzPanelStream), file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print(str(twhSmartDeviceSSIDPanelStream), file=f, end="")
            print(",", file=f, end="")
            print("Pass" + "\n", file=f, end="")
        SSID, gwPassword = self.twhSmartDeviceSSID, self.twhSmartDeviceSSIDPW
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                                                args=(
                                                selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        self.openTWHGUI(driver)  # adjust settings to 5GHz only
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, """//*[@id="login_field"]/table/tbody/tr[3]/td[3]/span/div/div/input""")))
            element.send_keys(self.twh_user_name)
            element = driver.find_element_by_xpath(
                """//*[@id="login_field"]/table/tbody/tr[4]/td[3]/span/div/div/input""")
            element.send_keys(self.twh_password)
            element.send_keys(Keys.RETURN)
        except:
            pass
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "group_2")))
        element.click()
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "idx_41"))) #select 2.4G tab
        element.click()  # Click on 2.4GHz tab
        self.enterIFrame(driver) #enter lower section of page
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, """//*[@id="contentbody"]/form/table/tbody/tr[1]/td/table/tbody/tr[1]/td[2]/span[1]/a"""))) #find 5G-l off button
        element.click()  # Click on 5GHz low off
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, """//*[@id="save"]/span[2]""")))
        element.click()  # Click on save settings
        time.sleep(60)
        self.testWifiConnection(dealer_ID, selectedCameraMAC)
        print("Starting install on TWH - SmartHome SSID")
        shsTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cameraInstall, webStream = self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera, selectedCameraMAC, selectedCustomerID, selected_device_ID, model, Panel)
        twhSmartDeviceSSIDPanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.twh_SSID, self.twh_SSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        twhSmartSteeringPanelStream = self.panelTest(Panel)
        print("Successful camera install on TWH - SmartHome SSID")
        with open(log_file, 'a') as f:
            print(shsTime, file=f, end="")
            print(",", file=f, end="")
            print("SmartHome SSID", file=f, end="")
            print(",", file=f, end="")
            print(str(cameraInstall), file=f, end="")
            print(",", file=f, end="")
            print(str(webStream), file=f, end="")
            print(",", file=f, end="")
            print(str(twhSmartSteeringPanelStream), file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print(str(twhSmartDeviceSSIDPanelStream), file=f, end="")
            print(",", file=f, end="")
            print("Pass" + "\n", file=f, end="")
        SSID, gwPassword = self.twh_SSID, self.twh_SSID_PW
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                                                args=(
                                                selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        self.testWifiConnection(dealer_ID, selectedCameraMAC)

    def nahARCBoostv2_ss(self, driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                      selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID, log_file,model, Panel, panelID):
        print("Starting install on NAH + ARC Boostv2 - SmartSteering")
        smartsteeringTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.testWifiConnection(dealer_ID, selectedCameraMAC)
        cameraInstall, webStream = self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password,
                                           selectedCamera,
                                           selectedCameraMAC, selectedCustomerID, selected_device_ID, model, Panel)
        ARCBoostv2_ssPanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.arcboostv2SmartDeviceSSID24, self.arcboostv2SmartDeviceSSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        ARCBoostv2SmartDeviceSSID24PanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.arcboostv2SmartDeviceSSID5, self.arcboostv2SmartDeviceSSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        ARCBoostv2SmartDeviceSSID5PanelStream = self.panelTest(Panel)
        print("Successful camera install on TWH - SmartSteering")
        with open(log_file, 'a', newline='') as f:
            print(smartsteeringTime, file=f, end="")
            print(",", file=f, end="")
            print("SmartSteering", file=f, end="")
            print(",", file=f, end="")
            print(str(cameraInstall), file=f, end="")
            print(",", file=f, end="")
            print(str(webStream), file=f, end="")
            print(",", file=f, end="")
            print(str(ARCBoostv2_ssPanelStream), file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print(str(ARCBoostv2SmartDeviceSSID24PanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(ARCBoostv2SmartDeviceSSID5PanelStream), file=f, end="")
            print(",", file=f, end="")
            print("Pass" + "\n", file=f, end="")

    def nahARCBoostv2_24(self, driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                         selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID, log_file, model, Panel, panelID):
        SSID, gwPassword = self.arcboostv2_SSID, self.arcboostv2_SSID_PW
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                                                args=(
                                                selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        self.openARCBoostv2GUI(driver)
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, """//*[@id="login_field"]/table/tbody/tr[3]/td[3]/span/div/div/input""")))
            element.send_keys(self.boostv2_user_name)
            element = driver.find_element_by_xpath("""//*[@id="psw_id"]""")
            element.send_keys(self.boostv2_password)
            element.send_keys(Keys.RETURN)
        except:
            pass
        time.sleep(2)
        driver.switch_to.default_content()
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "leftFrame")))
        element = driver.find_element_by_xpath("""//*[contains(text(), "Wi-Fi")]""").click()  # select wifi tab
        driver.switch_to.default_content()
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "topFrame")))
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "idx_10")))  # select 5GHz-low tab
        element.click()  # Click on 5GHz tab
        driver.switch_to.default_content()
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "main2")))
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, """//*[@id="radio_enable_1"]/tbody/tr/td[2]/span[2]/a"""))).click()  # select 5G-l off
        time.sleep(2)
        element = driver.find_element_by_xpath(
            """/html/body/table/tbody/tr/td/div/form/table[2]/tbody/tr/td[3]/div/a/span[2]""").click()
        time.sleep(60)  # allow time for settings to be applied
        driver.switch_to.default_content()
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "topFrame")))
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "idx_11"))).click()  # select 5GHz-high tab
        driver.switch_to.default_content()
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "main2")))
        # driver.switch_to.frame(
        # driver.find_element_by_xpath("""//*[@id="frm_main2"]"""))  # enter main lower section of page
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, """//*[@id="radio_enable_1"]/tbody/tr/td[2]/span[2]/a"""))).click()  # select 5G-h off
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                                        """/html/body/table/tbody/tr/td/div/form/table[2]/tbody/tr/td[3]/div/a/span[2]"""))).click()  # click save button
        time.sleep(60)  # allow time for settings to be applied
        print("Starting install on Boostv2 - 2.4G")
        twofourtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.testWifiConnection(dealer_ID, selectedCameraMAC)
        cameraInstall, webStream = self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password,
                                           selectedCamera,
                                           selectedCameraMAC, selectedCustomerID, selected_device_ID, model, Panel)
        ARCBoostv2_24PanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.arcboostv2SmartDeviceSSID24, self.arcboostv2SmartDeviceSSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        ARCBoostv2SmartDeviceSSID24PanelStream = self.panelTest(Panel)
        print("Successful camera install on Boostv2 - 2.4")
        with open(log_file, 'a') as f:
            print(twofourtime, file=f, end="")
            print(",", file=f, end="")
            print("2.4GHz", file=f, end="")
            print(",", file=f, end="")
            print(str(cameraInstall), file=f, end="")
            print(",", file=f, end="")
            print(str(webStream), file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print(str(ARCBoostv2_24PanelStream), file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print(str(ARCBoostv2SmartDeviceSSID24PanelStream), file=f, end="")
            print(",", file=f, end="")
            print("Pass" + "\n", file=f, end="")

    def nahARCBoostv2_5(self, driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                         selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID, log_file, model, Panel, panelID):
        SSID, gwPassword = self.arcboostv2_SSID, self.arcboostv2_SSID_PW
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                                                args=(
                                                selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        self.openARCBoostv2GUI(driver) #adjust settings to 5GHz only
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, """//*[@id="login_field"]/table/tbody/tr[3]/td[3]/span/div/div/input""")))
            element.send_keys(self.boostv2_user_name)
            element = driver.find_element_by_xpath("""//*[@id="psw_id"]""")
            element.send_keys(self.boostv2_password)
            element.send_keys(Keys.RETURN)
        except:
            pass
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "leftFrame"))) # enter left tab section of page
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, """//*[contains(text(), "Wi-Fi")]""")))  # select wifi tab
        element.click()
        driver.switch_to.default_content()
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "topFrame")))  # enter top tab section of page
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "idx_9"))).click()  # select 2.4GHz tab
        driver.switch_to.default_content()
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "main2")))  # enter main lower section of page
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, """//*[@id="radio_enable_1"]/tbody/tr/td[2]/span[2]/a"""))).click()  # select 2.4 off
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, """/html/body/table/tbody/tr/td/div/form/table[2]/tbody/tr/td[3]/div/a/span[2]"""))).click()  # click save button
        time.sleep(60)  # allow time for settings to be applied
        driver.switch_to.default_content()
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "topFrame")))  # enter top tab section of page
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "idx_10")))  # select 5GHz-low tab
        element.click()  # Click on 5GHz tab
        driver.switch_to.default_content()
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "main2")))  # enter main lower section of page
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, """//*[@id="radio_enable_1"]/tbody/tr/td[2]/span[1]/a"""))).click()  # select 5G-l on
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, """/html/body/table/tbody/tr/td/div/form/table[2]/tbody/tr/td[3]/div/a/span[2]"""))).click()  # click save button
        time.sleep(60)  # allow time for settings to be applied
        driver.switch_to.default_content()
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "topFrame")))  # enter top tab section of page
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "idx_11"))).click()  # select 5GHz-high tab
        driver.switch_to.default_content()
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "main2"))) # enter main lower section of page
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, """//*[@id="radio_enable_1"]/tbody/tr/td[2]/span[1]/a"""))).click()  # select 5G-h on
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, """/html/body/table/tbody/tr/td/div/form/table[2]/tbody/tr/td[3]/div/a/span[2]"""))).click()  # click save button
        time.sleep(60)  # allow time for settings to be applied
        print("Starting install on Boostv2 - 5G")
        fiveTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.testWifiConnection(dealer_ID, selectedCameraMAC)
        cameraInstall, webStream = self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password,
                                           selectedCamera,
                                           selectedCameraMAC, selectedCustomerID, selected_device_ID,model, Panel)
        ARCBoostv2_5PanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.arcboostv2SmartDeviceSSID5, self.arcboostv2SmartDeviceSSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        ARCBoostv2SmartDeviceSSID5PanelStream = self.panelTest(Panel)
        print("Successful camera install on Boostv2 - 5G")
        with open(log_file, 'a') as f:
            print(fiveTime, file=f, end="")
            print(",", file=f, end="")
            print("5G", file=f, end="")
            print(",", file=f, end="")
            print(str(cameraInstall), file=f, end="")
            print(",", file=f, end="")
            print(str(webStream), file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print(str(ARCBoostv2_5PanelStream), file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print(str(ARCBoostv2SmartDeviceSSID5PanelStream), file=f, end="")
            print(",", file=f, end="")
            print("Pass" + "\n", file=f, end="")

    def nahARCBoostv2_shs_24(self, driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                        selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID, log_file, model, Panel, panelID):
        # SSID, gwPassword = "SmartHome0454", "GfHK4dD9YbGEAe"
        SSID, gwPassword = self.arcboostv2SmartDeviceSSID24, self.arcboostv2SmartDeviceSSID_PW
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                                                args=(
                                                    selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        self.openARCBoostv2GUI(driver)  # turn all radios back on
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, """//*[@id="login_field"]/table/tbody/tr[3]/td[3]/span/div/div/input""")))
            element.send_keys(self.boostv2_user_name)
            element = driver.find_element_by_xpath("""//*[@id="psw_id"]""")
            element.send_keys(self.boostv2_password)
            element.send_keys(Keys.RETURN)
        except:
            pass
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.NAME, "leftFrame")))  # enter left tab section of page
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, """//*[contains(text(), "Wi-Fi")]""")))  # select wifi tab
        element.click()
        driver.switch_to.default_content()
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.NAME, "topFrame")))  # enter top tab section of page
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "idx_9"))).click()  # select 2.4GHz tab
        driver.switch_to.default_content()
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.NAME, "main2")))  # enter main lower section of page
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, """//*[@id="radio_enable_1"]/tbody/tr/td[2]/span[1]/a"""))).click()  # select 2.4 on
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                                        """/html/body/table/tbody/tr/td/div/form/table[2]/tbody/tr/td[3]/div/a/span[2]"""))).click()  # click save button
        time.sleep(60)  # allow time for settings to be applied
        print("Starting install on Boostv2 - SmartHome SSID 2.4GHz")
        shsTime2 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.testWifiConnection(dealer_ID, selectedCameraMAC)
        cameraInstall, webStream = self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password,
                                           selectedCamera,
                                           selectedCameraMAC, selectedCustomerID, selected_device_ID, model, Panel)
        ARCBoostv2SmartDeviceSSID24PanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.arcboostv2_SSID, self.arcboostv2_SSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        ARCBoostv2_ssPanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.arcboostv2SmartDeviceSSID5, self.arcboostv2SmartDeviceSSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        ARCBoostv2SmartDeviceSSID5PanelStream = self.panelTest(Panel)
        print("Successful camera install on Boostv2 - SmartHome SSID 2.4GHz")
        with open(log_file, 'a') as f:
            print(shsTime2, file=f, end="")
            print(",", file=f, end="")
            print("2.4GHz SmartHome SSID", file=f, end="")
            print(",", file=f, end="")
            print(str(cameraInstall), file=f, end="")
            print(",", file=f, end="")
            print(str(webStream), file=f, end="")
            print(",", file=f, end="")
            print(str(ARCBoostv2_ssPanelStream), file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print(str(ARCBoostv2SmartDeviceSSID24PanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(ARCBoostv2SmartDeviceSSID5PanelStream), file=f, end="")
            print(",", file=f, end="")
            print("Pass" + "\n", file=f, end="")

    def nahARCBoostv2_shs_5(self, driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                             selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID, log_file, model, Panel, panelID):
        SSID, gwPassword = self.arcboostv2SmartDeviceSSID5, self.arcboostv2SmartDeviceSSID_PW
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                                                args=(
                                                    selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        print("Starting install on Boostv2 - SmartHome SSID 5GHz")
        shsTime5 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cameraInstall, webStream = self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password,
                                           selectedCamera,
                                           selectedCameraMAC, selectedCustomerID, selected_device_ID, model, Panel)
        ARCBoostv2SmartDeviceSSID5PanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.arcboostv2_SSID, self.arcboostv2_SSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        ARCBoostv2_ssPanelStream = self.panelTest(Panel)
        SSID, gwPassword = self.arcboostv2SmartDeviceSSID5, self.arcboostv2SmartDeviceSSID_PW
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        ARCBoostv2SmartDeviceSSID24PanelStream = self.panelTest(Panel)
        print("Successful camera install on Boostv2 - SmartHome SSID 5GHz")
        with open(log_file, 'a') as f:
            print(shsTime5, file=f, end="")
            print(",", file=f, end="")
            print("5GHz SmartHome SSID", file=f, end="")
            print(",", file=f, end="")
            print(str(cameraInstall), file=f, end="")
            print(",", file=f, end="")
            print(str(webStream), file=f, end="")
            print(",", file=f, end="")
            print(str(ARCBoostv2_ssPanelStream), file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print("N/A", file=f, end="")
            print(",", file=f, end="")
            print(str(ARCBoostv2SmartDeviceSSID24PanelStream), file=f, end="")
            print(",", file=f, end="")
            print(str(ARCBoostv2SmartDeviceSSID5PanelStream), file=f, end="")
            print(",", file=f, end="")
            print("Pass" + "\n", file=f, end="")

    def nahARCBoostv2_restore_2_normal(self, driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                            selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID, log_file, model, panelID):
        SSID, gwPassword = self.arcboostv2_SSID, self.arcboostv2_SSID_PW
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                                                args=(
                                                    selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        updatePanelSettings = threading.Thread(target=self.updatePanelSettings,
                                               args=(selectedCustomerID, panelID, SSID, gwPassword, dealer_ID))
        updatePanelSettings.start()
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        self.testWifiConnection(dealer_ID, selectedCameraMAC)

    def airties_restore_2_normal(self, driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                            selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID, log_file, model):
        SSID, gwPassword = "TELUS0579", "sEFRDVstG8cb"
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                                                args=(
                                                    selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        self.openARCBoostv2GUI(driver)  # turn all radios back on
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, """//*[@id="login_field"]/table/tbody/tr[3]/td[3]/span/div/div/input""")))
            element.send_keys(self.boostv2_user_name)
            element = driver.find_element_by_xpath("""//*[@id="psw_id"]""")
            element.send_keys(self.boostv2_password)
            element.send_keys(Keys.RETURN)
        except:
            pass
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.NAME, "leftFrame")))  # enter left tab section of page
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, """//*[contains(text(), "Wi-Fi")]""")))  # select wifi tab
        element.click()
        driver.switch_to.default_content()
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.NAME, "topFrame")))  # enter top tab section of page
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "idx_9"))).click()  # select 2.4GHz tab
        driver.switch_to.default_content()
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.NAME, "main2")))  # enter main lower section of page
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, """//*[@id="radio_enable_1"]/tbody/tr/td[2]/span[1]/a"""))).click()  # select 2.4 on
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                                        """/html/body/table/tbody/tr/td/div/form/table[2]/tbody/tr/td[3]/div/a/span[2]"""))).click()  # click save button
        time.sleep(60)  # allow time for settings to be applied
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        self.testWifiConnection(dealer_ID, selectedCameraMAC)

    def nahARCboostv2testcase(self, driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                      selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID, log_file,model,Panel,panelID):
        self.nahARCBoostv2_ss(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                      selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID, log_file,model,Panel, panelID)
        self.nahARCBoostv2_24(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                      selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID, log_file,model,Panel, panelID)
        self.nahARCBoostv2_5(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                              selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID, log_file, model,Panel,panelID)
        self.nahARCBoostv2_shs_24(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                             selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID, log_file, model, Panel,panelID)
        #self.nahARCBoostv2_shs_5(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                                  #selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID, log_file, model,Panel,panelID)
        self.nahARCBoostv2_restore_2_normal(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                                 selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID, log_file, model, panelID)

    def airtiestestcase(self, driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                              selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID, log_file, model):
        self.nahARCBoostv2_ss(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                              selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID, log_file, model)
        self.nahARCBoostv2_24(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                              selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID, log_file, model)
        self.nahARCBoostv2_5(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                             selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID, log_file, model)
        self.airties_restore_2_normal(driver, cust_user_name, cust_password, pp_user_name, pp_password,
                                            selectedCamera,
                                            selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID,
                                            log_file, model)





    def nahTCHboostv2testcase(self, driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                      selectedCameraMAC, selectedCustomerID, selected_device_ID, dealer_ID, log_file,model):
        print("Starting install on NAH + TCH Boostv2 - SmartSteering")
        smartsteeringTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.testWifiConnection(dealer_ID,selectedCameraMAC)
        cameraInstall = self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password,
                                           selectedCamera,
                                           selectedCameraMAC, selectedCustomerID, selected_device_ID,model)
        print("Successful camera install on NAH + TCH Boostv2 - SmartSteering")
        with open(log_file, 'a',newline='') as f:
            print(smartsteeringTime, file=f, end="")
            print(",", file=f, end="")
            print("SmartSteering", file=f, end="")
            print(",", file=f, end="")
            print("Success", file=f, end="")
            print(",", file=f, end="")
            print(str(cameraInstall) + "\n", file=f, end="")
        SSID, gwPassword = "TELUS0067", "tsecurity1"
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                             args=(selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        self.openTCHBoostv2GUI(driver)
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, """//*[@id="srp_username"]""")))
            #element.send_keys(self.tchboostv2_user_name)
            element = driver.find_element_by_xpath("""//*[@id="srp_password"]""")
            element.send_keys(self.tchboostv2_password)
            element.send_keys(Keys.RETURN)
        except:
            pass
        WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,"""//*[@id="Wireless"]/i"""))).click() #open wireless tab
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, """//*[@id="Radio"]"""))).click() #open the radio tab
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, """//*[@id="Wireless_Tab_4"]"""))).click() #open the 5g low tab
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element((By.XPATH, """//*[@id="Poptxt"]""")))
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, """//*[@id="wireless-ap-modal-newEM"]/div[2]/form/div[2]/fieldset/div[1]/div/div"""))).click() #switch off 5g low
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,"""//*[@id="save-config"]"""))).click() #save changes
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element((By.XPATH, """//*[@id="Poptxt"]""")))
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, """//*[@id="Wireless_Tab_7"]"""))).click()  # open the 5g high tab
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element((By.XPATH, """//*[@id="Poptxt"]""")))
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                                        """//*[@id="wireless-ap-modal-newEM"]/div[2]/form/div[2]/fieldset/div[1]/div/div"""))).click()  # switch off 5g high
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, """//*[@id="save-config"]"""))).click()  # save changes
        print("Starting install on Boostv2 - 2.4G")
        twofourtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.testWifiConnection(dealer_ID, selectedCameraMAC)
        cameraInstall = self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password, selectedCamera,
                           selectedCameraMAC, selectedCustomerID, selected_device_ID,model)
        print("Successful camera install on Boostv2 - 2.4")
        with open(log_file, 'a') as f:
            print(twofourtime, file=f, end="")
            print(",", file=f, end="")
            print("2.4GHz", file=f, end="")
            print(",", file=f, end="")
            print("Success", file=f, end="")
            print(",", file=f, end="")
            print(str(cameraInstall) + "\n", file=f, end="")
        SSID, gwPassword = "TELUS0067", "tsecurity1"
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                                                args=(
                                                selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        self.openTCHBoostv2GUI(driver) #adjust settings to 5GHz only
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, """//*[@id="srp_username"]""")))
            # element.send_keys(self.tchboostv2_user_name)
            element = driver.find_element_by_xpath("""//*[@id="srp_password"]""")
            element.send_keys(self.tchboostv2_password)
            element.send_keys(Keys.RETURN)
        except:
            pass
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, """//*[@id="Wireless"]/i"""))).click()  # open wireless tab
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, """//*[@id="Radio"]"""))).click()  # open the radio tab
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, """//*[@id="Wireless_Tab_4"]"""))).click()  # open the 5g low tab
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element((By.XPATH, """//*[@id="Poptxt"]""")))
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                                        """//*[@id="wireless-ap-modal-newEM"]/div[2]/form/div[2]/fieldset/div[1]/div/div"""))).click()  # switch on 5g low
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, """//*[@id="save-config"]"""))).click()  # save changes
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element((By.XPATH, """//*[@id="Poptxt"]""")))
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, """//*[@id="Wireless_Tab_7"]"""))).click()  # open the 5g high tab
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element((By.XPATH, """//*[@id="Poptxt"]""")))
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                                        """//*[@id="wireless-ap-modal-newEM"]/div[2]/form/div[2]/fieldset/div[1]/div/div"""))).click()  # switch on 5g high
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, """//*[@id="save-config"]"""))).click()  # save changes
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element((By.XPATH, """//*[@id="Poptxt"]""")))
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, """//*[@id="Wireless_Tab_1"]"""))).click()
        # open the 2.4g tab
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element((By.XPATH, """//*[@id="Poptxt"]""")))
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                                        """//*[@id="wireless-ap-modal-newEM"]/div[2]/form/div[2]/fieldset/div[1]/div/div"""))).click()  # switch off 2.4g
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, """//*[@id="save-config"]"""))).click()  # save changes
        print("Starting install on Boostv2 - 5G")
        fiveTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.testWifiConnection(dealer_ID, selectedCameraMAC)
        cameraInstall = self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password,
                                           selectedCamera,
                                           selectedCameraMAC, selectedCustomerID, selected_device_ID,model)
        print("Successful camera install on Boostv2 - 5G")
        with open(log_file, 'a') as f:
            print(fiveTime, file=f, end="")
            print(",", file=f, end="")
            print("5G", file=f, end="")
            print(",", file=f, end="")
            print("Success", file=f, end="")
            print(",", file=f, end="")
            print(str(cameraInstall) + "\n", file=f, end="")
        SSID, gwPassword = "SmartHome0067", "pRJtrZmU9cywJf"
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                                                args=(
                                                selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        self.openTCHBoostv2GUI(driver)  #turn all radios back on
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, """//*[@id="srp_username"]""")))
            # element.send_keys(self.tchboostv2_user_name)
            element = driver.find_element_by_xpath("""//*[@id="srp_password"]""")
            element.send_keys(self.tchboostv2_password)
            element.send_keys(Keys.RETURN)
        except:
            pass
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, """//*[@id="Wireless"]/i"""))).click()  # open wireless tab
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, """//*[@id="Radio"]"""))).click()  # open the radio tab
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, """//*[@id="Wireless_Tab_1"]"""))).click() # open the 5g low tab
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element((By.XPATH, """//*[@id="Poptxt"]""")))
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                                        """//*[@id="wireless-ap-modal-newEM"]/div[2]/form/div[2]/fieldset/div[1]/div/div"""))).click()  # switch on 5g low
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, """//*[@id="save-config"]"""))).click()  # save changes
        print("Starting install on Boostv2 - SmartHome SSID 2.4GHz")
        shsTime2 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.testWifiConnection(dealer_ID, selectedCameraMAC)
        cameraInstall = self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password,
                                           selectedCamera,
                                           selectedCameraMAC, selectedCustomerID, selected_device_ID,model)
        print("Successful camera install on Boostv2 - SmartHome SSID 2.4GHz")
        with open(log_file, 'a') as f:
            print(shsTime2, file=f, end="")
            print(",", file=f, end="")
            print("2.4GHz SmartHome SSID", file=f, end="")
            print(",", file=f, end="")
            print("Success", file=f, end="")
            print(",", file=f, end="")
            print(str(cameraInstall) + "\n", file=f, end="")
        SSID, gwPassword = "SmartHome0067-5G", "pRJtrZmU9cywJf"
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                                                args=(
                                                    selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        print("Starting install on Boostv2 - SmartHome SSID 5GHz")
        shsTime5 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cameraInstall = self.cameraInstall(driver, cust_user_name, cust_password, pp_user_name, pp_password,
                                           selectedCamera,
                                           selectedCameraMAC, selectedCustomerID, selected_device_ID, model)
        print("Successful camera install on Boostv2 - SmartHome SSID 5GHz")
        with open(log_file, 'a') as f:
            print(shsTime5, file=f, end="")
            print(",", file=f, end="")
            print("5GHz SmartHome SSID", file=f, end="")
            print(",", file=f, end="")
            print("Success", file=f, end="")
            print(",", file=f, end="")
            print(str(cameraInstall) + "\n", file=f, end="")
        SSID, gwPassword = "TELUS0454", "tsecurity1"
        updateCameraSettings = threading.Thread(target=self.updateCameraSettings,
                                                args=(
                                                selectedCustomerID, selectedCameraMAC, SSID, gwPassword, dealer_ID))
        updateCameraSettings.start()
        self.deleteCamera(driver, selectedCustomerID, selected_device_ID, pp_user_name, pp_password, selectedCamera)
        self.testWifiConnection(dealer_ID, selectedCameraMAC)
