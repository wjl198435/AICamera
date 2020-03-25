
import argparse
import sys
import json
import logging
# import pandas


from frigate.camera.ezviz import EzvizClient, EzvizCamera

if __name__ == '__main__':
    deviceSerial = "D77692005"
    appKey = "e947f6cde1c54ce5b721efa6e929efda"
    appSecret = "a3f849864180739ddf11227f0b3f3501"
    ez = EzvizClient(deviceSerial,appKey,appSecret)
    print(ez.get_access_token())
    print(ez.get_device_live_address())
    print(ez.get_device_info())