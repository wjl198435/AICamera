import json
import requests
import logging
import hashlib
import time
# from fake_useragent import UserAgent
# from uuid import uuid4
# from .camera import EzvizCamera
# # from pyezviz.camera import EzvizCamera


from frigate.utils.logger import debug, info,setInfo,setDebug,error

COOKIE_NAME = "sessionId"
CAMERA_DEVICE_CATEGORY = "IPC"

API_BASE_URI = "https://open.ys7.com"

API_GET_TOKEN = "/api/lapp/token/get"
API_LIVE_ADDRESS = "/api/lapp/live/address/get"
API_DEVICE_INFO = "/api/lapp/device/info"


API_ENDPOINT_LOGIN = "/v3/users/login"
API_ENDPOINT_CLOUDDEVICES = "/api/cloud/v2/cloudDevices/getAll"
API_ENDPOINT_PAGELIST = "/v3/userdevices/v1/devices/pagelist"
API_ENDPOINT_DEVICES = "/v3/devices/"
API_ENDPOINT_SWITCH_STATUS = '/api/device/switchStatus'
API_ENDPOINT_PTZCONTROL = "/ptzControl"
API_ENDPOINT_ALARM_SOUND = "/alarm/sound"
API_ENDPOINT_DATA_REPORT = "/api/other/data/report"
API_ENDPOINT_DETECTION_SENSIBILITY = "/api/device/configAlgorithm"
API_ENDPOINT_DETECTION_SENSIBILITY_GET = "/api/device/queryAlgorithmConfig"

ACCESS_TOKEN = API_BASE_URI + API_GET_TOKEN
LIVE_ADDRESS = API_BASE_URI + API_LIVE_ADDRESS
DEVICE_INFO = API_BASE_URI + API_DEVICE_INFO

LOGIN_URL = API_BASE_URI + API_ENDPOINT_LOGIN
CLOUDDEVICES_URL = API_BASE_URI + API_ENDPOINT_CLOUDDEVICES
DEVICES_URL = API_BASE_URI + API_ENDPOINT_DEVICES
PAGELIST_URL = API_BASE_URI + API_ENDPOINT_PAGELIST
DATA_REPORT_URL = API_BASE_URI + API_ENDPOINT_DATA_REPORT

SWITCH_STATUS_URL = API_BASE_URI + API_ENDPOINT_SWITCH_STATUS
DETECTION_SENSIBILITY_URL = API_BASE_URI + API_ENDPOINT_DETECTION_SENSIBILITY
DETECTION_SENSIBILITY_GET_URL = API_BASE_URI + API_ENDPOINT_DETECTION_SENSIBILITY_GET



DEFAULT_TIMEOUT = 10
MAX_RETRIES = 3


class PyEzvizError(Exception):
    pass


class EzvizClient(object):
    # def __init__(self,deviceSerial = "", appKey = "", appSecret = ""):
    #     self._deviceSerial = deviceSerial
    #     self._appKey = appKey
    #     self._appSecret = appSecret
    #
    #     self.expireTime = 0
    #     self.accessToken = None
    #
    #     self.live_address = None

    def __init__(self,conf,serial):
        self.camera_conf = conf
        self._deviceSerial = serial
        self._appKey = conf['appKey']
        self._appSecret = conf['appSecret']

        # info("9999999")
        # info(self._appKey)
        # info(self._appSecret)
        # info(serial)
        # info("9999999")

        self.expireTime = 0
        self.accessToken = None

        self.live_address = None
        self.device_info = None

        # self.get_access_token()
        self.get_device_live_address()
        self.get_device_info()


    def __repr__(self):
        return '%s(%r,%s)' % (self.__class__.__name__, self._deviceSerial,self.accessToken )


    def get_access_token(self):
        if self.check_token_is_expired() or self.accessToken is None:
            r = requests.post(ACCESS_TOKEN, data={'appKey':self._appKey,'appSecret':self._appSecret})
            token_result = r.json()
            debug(token_result)
            if (token_result['code']=='200'):
                self.accessToken = token_result['data']['accessToken']
                self.expireTime = token_result['data']['expireTime']
                return self.accessToken
            else:
                error("Could not get ezviz access_token: Got appKey= %s : appSecret= %s result: %s)",str(self._appKey), str(self._appSecret),str(token_result))
                return False
        else:
            return self.accessToken

    def check_token_is_expired(self):
        now = int(round(time.time() * 1000))
        if (now > (self.expireTime-1000)):
            return True
        else:
            return False

    def get_device_live_address(self,rtmp = "rtmp"):
        r = requests.post(LIVE_ADDRESS, data={'accessToken':self.get_access_token(),'source':self._deviceSerial+":1"})
        # debug("accessToken={},deviceSerial={}".format(self.accessToken,self.deviceSerial))
        debug(r)
        result = r.json()
        # print(result)
        if (result['code'] == '200'):
            self.live_address = result['data'][0][rtmp]
            # debug("live_address={}".format(self.live_address))
            return self.live_address
        else:
            error("Could not get ezviz device_live_address: Got _deviceSerial= %s  result: %s)",str(self._deviceSerial) ,str(result))
            return False
            # raise

    def get_device_info(self):
        r = requests.post(DEVICE_INFO, data={'accessToken':self.get_access_token(),'deviceSerial':self._deviceSerial})
        result = r.json()
        # info(result)
        if (result['code'] == '200'):
            # print(result)
            self.device_info = result['data']
            return True
        else:
            error("Cant get device info deviceSerial: {}".format(self._deviceSerial))
            return False

if __name__ == '__main__':
    deviceSerial = "D77692005"
    appKey = "e947f6cde1c54ce5b721efa6e929efda"
    appSecret = "a3f849864180739ddf11227f0b3f3501"
    ez = EzvizClient(deviceSerial,appKey,appSecret)
    print(ez.get_access_token())
    print(ez.get_device_live_address())
    print(ez.get_device_info())


    # def __init__(self, account, password, session=None, sessionId=None, timeout=None, cloud=None, connection=None):
    #     """Initialize the client object."""
    #     self.account = account
    #     self.password = password
    #     # self._user_id = None
    #     # self._user_reference = None
    #     self._session = session
    #     self._sessionId = sessionId
    #     self._data = {}
    #     self._timeout = timeout
    #     self._CLOUD = cloud
    #     self._CONNECTION = connection

    # def _login(self):
    #     """Login to Ezviz' API."""
    #
    #     # Ezviz API sends md5 of password
    #     m = hashlib.md5()
    #     m.update(self.password.encode('utf-8'))
    #     md5pass = m.hexdigest()
    #     payload = {"account": self.account, "password": md5pass, "featureCode": "92c579faa0902cbfcfcc4fc004ef67e7"}
    #
    #     try:
    #         req = self._session.post(LOGIN_URL,
    #                                  data=payload,
    #                                  headers={"Content-Type": "application/x-www-form-urlencoded",
    #                                           "clientType": "1",
    #                                           "customNo": "1000001"},
    #                                  timeout=self._timeout)
    #     except OSError:
    #         raise PyEzvizError("Can not login to API")
    #
    #     if req.status_code == 400:
    #         raise PyEzvizError("Login error: Please check your username/password: %s ", str(req.text))
    #
    #     # let's parse the answer, session is in {.."loginSession":{"sessionId":"xxx...}
    #     try:
    #         response_json = req.json()
    #         sessionId = str(response_json["loginSession"]["sessionId"])
    #         if not sessionId:
    #             raise PyEzvizError("Login error: Please check your username/password: %s ", str(req.text))
    #         self._sessionId = sessionId
    #
    #     except (OSError, json.decoder.JSONDecodeError) as e:
    #         raise PyEzvizError("Impossible to decode response: \nResponse was: [%s] %s", str(e), str(req.status_code), str(req.text))
    #
    #
    #     return True
    #
    # def _get_pagelist(self, filter=None, json_key=None, max_retries=0):
    #     """Get data from pagelist API."""
    #
    #     if max_retries > MAX_RETRIES:
    #         raise PyEzvizError("Can't gather proper data. Max retries exceeded.")
    #
    #     if filter == None:
    #         raise PyEzvizError("Trying to call get_pagelist without filter")
    #
    #     try:
    #         req = self._session.get(PAGELIST_URL,
    #                                 params={'filter': filter},
    #                                 headers={ 'sessionId': self._sessionId},
    #                                 timeout=self._timeout)
    #
    #     except OSError as e:
    #         raise PyEzvizError("Could not access Ezviz' API: " + str(e))
    #
    #     if req.status_code == 401:
    #         # session is wrong, need to relogin
    #         self.login()
    #         logging.info("Got 401, relogging (max retries: %s)",str(max_retries))
    #         return self._get_pagelist(max_retries+1)
    #
    #     if req.text is "":
    #         raise PyEzvizError("No data")
    #
    #     try:
    #         json_output = req.json()
    #     except (OSError, json.decoder.JSONDecodeError) as e:
    #         raise PyEzvizError("Impossible to decode response: " + str(e) + "\nResponse was: " + str(req.text))
    #
    #     if json_key == None:
    #         json_result = json_output
    #     else:
    #         json_result = json_output[json_key]
    #
    #     if not json_result:
    #         raise PyEzvizError("Impossible to load the devices, here is the returned response: %s ", str(req.text))
    #
    #     return json_result
    #
    # def _switch_status(self, serial, status_type, enable, max_retries=0):
    #     """Switch status on a device"""
    #
    #     try:
    #         req = self._session.post(SWITCH_STATUS_URL,
    #                                  data={  'sessionId': self._sessionId,
    #                                          'enable': enable,
    #                                          'serial': serial,
    #                                          'channel': '0',
    #                                          'netType' : 'WIFI',
    #                                          'clientType': '1',
    #                                          'type': status_type},
    #                                  timeout=self._timeout)
    #
    #
    #         if req.status_code == 401:
    #             # session is wrong, need to relogin
    #             self.login()
    #             logging.info("Got 401, relogging (max retries: %s)",str(max_retries))
    #             return self._switch_status(serial, type, enable, max_retries+1)
    #
    #         response_json = req.json()
    #         if response_json['resultCode'] != '0':
    #             raise PyEzvizError("Could not set the switch, maybe a permission issue ?: Got %s : %s)",str(req.status_code), str(req.text))
    #             return False
    #     except OSError as e:
    #         raise PyEzvizError("Could not access Ezviz' API: " + str(e))
    #
    #     return True
    #
    # def _switch_devices_privacy(self, enable=0):
    #     """Switch privacy status on ALL devices (batch)"""
    #
    #     #  enable=1 means privacy is ON
    #
    #     # get all devices
    #     devices = self._get_devices()
    #
    #     # foreach, launch a switchstatus for the proper serial
    #     for idx, device in enumerate(devices):
    #         serial = devices[idx]['serial']
    #         self._switch_status(serial, TYPE_PRIVACY_MODE, enable)
    #
    #     return True
    #
    # def load_cameras(self):
    #     """Load and return all cameras objects"""
    #
    #     # get all devices
    #     devices = self.get_DEVICE()
    #     cameras = []
    #
    #     # foreach, launch a switchstatus for the proper serial
    #     for idx, device in enumerate(devices):
    #         if devices[idx]['deviceCategory'] == CAMERA_DEVICE_CATEGORY:
    #             camera = EzvizCamera(self, device['deviceSerial'])
    #             camera.load()
    #             cameras.append(camera.status())
    #
    #     return cameras
    #
    # def ptzControl(self, command, serial, action, speed=5, max_retries=0):
    #     """PTZ Control by API."""
    #     if max_retries > MAX_RETRIES:
    #         raise PyEzvizError("Can't gather proper data. Max retries exceeded.")
    #
    #     if command == None:
    #         raise PyEzvizError("Trying to call ptzControl without command")
    #     if action == None:
    #         raise PyEzvizError("Trying to call ptzControl without action")
    #
    #
    #     try:
    #         req = self._session.put(DEVICES_URL + serial + API_ENDPOINT_PTZCONTROL,
    #                                 data={'command': command,
    #                                       'action': action,
    #                                       'channelNo': "1",
    #                                       'speed': speed,
    #                                       'uuid': str(uuid4()),
    #                                       'serial': serial},
    #                                 headers={ 'sessionId': self._sessionId,
    #                                           'clientType': "1"},
    #                                 timeout=self._timeout)
    #
    #     except OSError as e:
    #         raise PyEzvizError("Could not access Ezviz' API: " + str(e))
    #
    #     if req.status_code == 401:
    #         # session is wrong, need to re-log-in
    #         self.login()
    #         logging.info("Got 401, relogging (max retries: %s)",str(max_retries))
    #         return self.ptzControl(max_retries+1)
    #
    # def login(self):
    #     """Set http session."""
    #     if self._sessionId is None:
    #         self._session = requests.session()
    #         # adding fake user-agent header
    #         self._session.headers.update({'User-agent': str(UserAgent().random)})
    #
    #     return self._login()
    #
    # def data_report(self, serial, enable=1, max_retries=0):
    #     """Enable alarm notifications."""
    #     if max_retries > MAX_RETRIES:
    #         raise PyEzvizError("Can't gather proper data. Max retries exceeded.")
    #
    #     # operationType = 2 if disable, and 1 if enable
    #     operationType = 2 - int(enable)
    #     print(f"enable: {enable}, operationType: {operationType}")
    #
    #     try:
    #         req = self._session.post(DATA_REPORT_URL,
    #                                  data={  'clientType': '1',
    #                                          'infoDetail': json.dumps({
    #                                              "operationType" : int(operationType),
    #                                              "detail" : '0',
    #                                              "deviceSerial" : serial + ",2"
    #                                          }, separators=(',',':')),
    #                                          'infoType': '3',
    #                                          'netType': 'WIFI',
    #                                          'reportData': None,
    #                                          'requestType': '0',
    #                                          'sessionId': self._sessionId
    #                                          },
    #                                  timeout=self._timeout)
    #
    #     except OSError as e:
    #         raise PyEzvizError("Could not access Ezviz' API: " + str(e))
    #
    #     if req.status_code == 401:
    #         # session is wrong, need to re-log-in
    #         self.login()
    #         logging.info("Got 401, relogging (max retries: %s)",str(max_retries))
    #         return self.data_report(serial, enable, max_retries+1)
    #
    #     return True
    # # soundtype: 0 = normal, 1 = intensive, 2 = disabled ... don't ask me why...
    #
    # def detection_sensibility(self, serial, sensibility=3, max_retries=0):
    #     """Enable alarm notifications."""
    #     if max_retries > MAX_RETRIES:
    #         raise PyEzvizError("Can't gather proper data. Max retries exceeded.")
    #
    #     if sensibility not in [0,1,2,3,4,5,6]:
    #         raise PyEzvizError("Unproper sensibility (should be within 1 to 6).")
    #
    #     try:
    #         req = self._session.post(DETECTION_SENSIBILITY_URL,
    #                                  data={  'subSerial' : serial,
    #                                          'type': '0',
    #                                          'sessionId': self._sessionId,
    #                                          'value': sensibility,
    #                                          },
    #                                  timeout=self._timeout)
    #
    #     except OSError as e:
    #         raise PyEzvizError("Could not access Ezviz' API: " + str(e))
    #
    #     if req.status_code == 401:
    #         # session is wrong, need to re-log-in
    #         self.login()
    #         logging.info("Got 401, relogging (max retries: %s)",str(max_retries))
    #         return self.detection_sensibility(serial, enable, max_retries+1)
    #
    #     return True
    #
    # def get_detection_sensibility(self, serial, max_retries=0):
    #     """Enable alarm notifications."""
    #     if max_retries > MAX_RETRIES:
    #         raise PyEzvizError("Can't gather proper data. Max retries exceeded.")
    #
    #     try:
    #         req = self._session.post(DETECTION_SENSIBILITY_GET_URL,
    #                                  data={  'subSerial' : serial,
    #                                          'sessionId': self._sessionId,
    #                                          'clientType': 1
    #                                          },
    #                                  timeout=self._timeout)
    #
    #     except OSError as e:
    #         raise PyEzvizError("Could not access Ezviz' API: " + str(e))
    #
    #     if req.status_code == 401:
    #         # session is wrong, need to re-log-in
    #         self.login()
    #         logging.info("Got 401, relogging (max retries: %s)",str(max_retries))
    #         return self.get_detection_sensibility(serial, enable, max_retries+1)
    #     elif req.status_code != 200:
    #         raise PyEzvizError("Could not get detection sensibility: Got %s : %s)",str(req.status_code), str(req.text))
    #
    #     response_json = req.json()
    #     if response_json['resultCode'] != '0':
    #         # raise PyEzvizError("Could not get detection sensibility: Got %s : %s)",str(req.status_code), str(req.text))
    #         return 'Unknown'
    #     else:
    #         return response_json['algorithmConfig']['algorithmList'][0]['value']
    #
    # def alarm_sound(self, serial, soundType, enable=1, max_retries=0):
    #     """Enable alarm sound by API."""
    #     if max_retries > MAX_RETRIES:
    #         raise PyEzvizError("Can't gather proper data. Max retries exceeded.")
    #
    #     if soundType not in [0,1,2]:
    #         raise PyEzvizError("Invalid soundType, should be 0,1,2: " + str(soundType))
    #
    #     try:
    #         req = self._session.put(DEVICES_URL + serial + API_ENDPOINT_ALARM_SOUND,
    #                                 data={  'enable': enable,
    #                                         'soundType': soundType,
    #                                         'voiceId': '0',
    #                                         'deviceSerial': serial
    #                                         },
    #                                 headers={ 'sessionId': self._sessionId},
    #                                 timeout=self._timeout)
    #
    #     except OSError as e:
    #         raise PyEzvizError("Could not access Ezviz' API: " + str(e))
    #
    #     if req.status_code == 401:
    #         # session is wrong, need to re-log-in
    #         self.login()
    #         logging.info("Got 401, relogging (max retries: %s)",str(max_retries))
    #         return self.alarm_sound(serial, enable, soundType, max_retries+1)
    #     elif req.status_code != 200:
    #         logging.error("Got %s : %s)",str(req.status_code), str(req.text))
    #
    #     return True
    #
    # def switch_devices_privacy(self,enable=0):
    #     """Switch status on all devices."""
    #     return self._switch_devices_privacy(enable)
    #
    # def switch_status(self, serial, status_type, enable=0):
    #     """Switch status of a device."""
    #     return self._switch_status(serial, status_type, enable)
    #
    # def get_PAGE_LIST(self, max_retries=0):
    #     return self._get_pagelist(filter='CLOUD,TIME_PLAN,CONNECTION,SWITCH,STATUS,WIFI,STATUS_EXT,NODISTURB,P2P,TTS,KMS,HIDDNS', json_key=None)
    #
    # def get_DEVICE(self, max_retries=0):
    #     return self._get_pagelist(filter='CLOUD',json_key='deviceInfos')
    #
    # def get_CONNECTION(self, max_retries=0):
    #     return self._get_pagelist(filter='CONNECTION',json_key='connectionInfos')
    #
    # def get_STATUS(self, max_retries=0):
    #     return self._get_pagelist(filter='STATUS',json_key='statusInfos')
    #
    # def get_SWITCH(self, max_retries=0):
    #     return self._get_pagelist(filter='SWITCH',json_key='switchStatusInfos')
    #
    # def get_WIFI(self, max_retries=0):
    #     return self._get_pagelist(filter='WIFI',json_key='wifiInfos')
    #
    # def get_NODISTURB(self, max_retries=0):
    #     return self._get_pagelist(filter='NODISTURB',json_key='alarmNodisturbInfos')
    #
    # def get_P2P(self, max_retries=0):
    #     return self._get_pagelist(filter='P2P',json_key='p2pInfos')
    #
    # def get_KMS(self, max_retries=0):
    #     return self._get_pagelist(filter='KMS',json_key='kmsInfos')
    #
    # def get_TIME_PLAN(self, max_retries=0):
    #     return self._get_pagelist(filter='TIME_PLAN',json_key='timePlanInfos')
    #
    # def close_session(self):
    #     """Close current session."""
    #     self._session.close()
    #     self._session = None