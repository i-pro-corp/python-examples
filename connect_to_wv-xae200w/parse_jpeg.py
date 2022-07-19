'''
Copyright 2022 i-PRO Co., Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

'''
[Abstract]
    This program extracts the recognition result of WV-XAE200WUX (AI-VMD) from the JPEG file.
    WV-XAE200W (AI-VMD) の認識結果を JPEG ファイルから取り出します。

[Details]
    This program has been confirmed to work with WV-XAE200WUX Ver. 2.20.
    
[Author]
    kinoshita hidetoshi (木下英俊)

[Library install]

'''

import struct


def ParseAivmdResult(data):
    '''
    This function gets the recognition result in dictionary format from the WV-XAE200WUX (AI-VMD) recognition result.
    WV-XAE200W (AI-VMD) 認識結果から辞書形式の認識結果を取得する。

    Args:
        data            [i] WV-XAE200WUX (aivmd) recognition result.
    Returns:
        result          True:   success
                        False:  failure
        aivmd_result    the recognition result in dictionary format.
    Raises
        None
    '''
    result = {}
    result['detectResult'] = []
    length = len(data)

    UTCClock, timeZone, timeZoneMinute, frameTime   = struct.unpack('>LBBH', data[ 0: 8])
    algorithmId, resultInfo, resultInfoLength       = struct.unpack('>HHH',  data[ 8:14])
    areaInfo, imageWidth, imageHeight               = struct.unpack('>HHH',  data[14:20])
    areaNum = (areaInfo >> 10) & 0x3f
    areaLength = areaInfo & 0x3ff
    timeZoneDirection = (timeZone >> 6) & 0x01
    summerTime = (timeZone >> 5) & 0x01
    if timeZoneDirection == 0:
        timeZoneHour = + (timeZone & 0x1f)
    else:
        timeZoneHour = - (timeZone & 0x1f)
    resultInfoFlag = (resultInfo >> 1) & 0x01
    uniqueinfoflag = (resultInfo >> 0) & 0x01

    result['UTCClock']          = UTCClock
    result['timeZoneDirection'] = timeZoneDirection
    result['summerTime']        = summerTime
    result['timeZoneHour']      = timeZoneHour
    result['timeZoneMinute']    = timeZoneMinute
    result['frameTime']         = frameTime
    result['algorithmId']       = algorithmId           # 0x0100 fixed.
    result['resultInfoFlag']    = resultInfoFlag        # 0: detection,  1: no detection
    result['uniqueinfoflag']    = uniqueinfoflag
    result['resultInfoLength']  = resultInfoLength      # areaNum * areaLength [bytes]
    result['areaNum']           = areaNum
    result['areaLength']        = areaLength 
    result['imageWidth']        = imageWidth
    result['imageHeight']       = imageHeight

    offset = length - resultInfoLength

    if (algorithmId==0x0100) and (resultInfoLength == areaNum * areaLength):
        for i in range(areaNum):
            areaId, detectArea, alarm   = struct.unpack('>HHH10x', data[offset+areaLength*i:offset+areaLength*(i+1)])
            hstart, vstart, hcnt, vcnt  = struct.unpack('>8xHHHH', data[offset+areaLength*i:offset+areaLength*(i+1)])
            almType = (alarm >> 12) & 0x0f      
            direction = (alarm >> 8) & 0x0f     
            almObj = (alarm & 0xff)             

            detectResult = {}
            detectResult['areaId']      = areaId
            detectResult['detectArea']  = detectArea
            detectResult['almType']     = almType       # 1:Intruders, 2:Loitering, 3:Direction, 4:Object, 5:Cross line, 8:AI
            detectResult['Dir']         = direction     # 1:Up, 2:Up right, 3:Right, 4:Down right, 5:Down, 6:Down left, 7:Left, 8:Up left,
                                                        # 9:A→B, 10:B→A, 11:A⇔B
            detectResult['almObj']      = almObj        # 1: Person, 2: Car, 3: Bike, 4: Unknown
            detectResult['hstart']      = hstart
            detectResult['vstart']      = vstart
            detectResult['hcnt']        = hcnt
            detectResult['vcnt']        = vcnt

            result['detectResult'].append(detectResult)

    return result


def ParseJpegComment(data):
    '''
    This function obtains the WV-XAE200WUX (aivmd) recognition result from the JPEG comment data.
    JPEG コメントデータから WV-XAE200WUX (aivmd) 認識結果を取得する。

    Args:
        data            [i] JPEG comment data.
    Returns:
        result          True:   success
                        False:  failure
        aivmd_result    The WV-XAE200WUX (aivmd) recognition result.
    Raises
        None
    '''
    result = False
    aivmd_result = None
    length = len(data)

    while True:
        if length >= 4:
            tag, data_length = struct.unpack('>HH', data[0:4])
            if data_length <= length:
                data_interior = data[4: data_length]
                data = data[data_length:]
                length -= data_length

                if tag == 0x002f:   # 0x002f means AI-VMD meta information.
                    aivmd_result = ParseAivmdResult(data_interior)
                    result = True
                    break
            else:
                break
        else:
            break
    
    return result, aivmd_result


def ParseJpegHeadder(data):
    '''
    Get Tag, Length, Value (data_interior), the following data from JPEG header data.
    JPEG ヘッダデータから Tag, Length, Value(data_interior), 次のデータ を取得する。

    Args:
        data            [i] Data to be confirmed.
    Returns:
        result          True:   success
                        False:  failure
        tag             Tag
        length          Length
        data_interior   Value. If it does not exist, it will be None.
        data_next       The following data after data_interior. If it does not exist, it will be None.
    Raises
        None
    '''
    result = False
    tag = 0
    length = 0
    data_length = len(data)
    data_interior = None
    data_next = None

    if data_length >= 4:
        tag, length, = struct.unpack('>HH', data[0:4])
        if tag & 0xff00 == 0xff00:
            if length + 2 <= data_length:
                data_interior = data[4:length+2]
                data_next = data[length+2:data_length]
                result = True

    return result, tag, length, data_interior, data_next


def IsJpegFile(data):
    '''
    Check if data is JPEG data.
    data が JPEG データであることを確認する。

    Args:
        data            [i] Data to be confirmed.
    Returns:
        True            Data is JPEG.
        False           Data is not JPEG.
    Raises
        None
    '''
    result = False

    length = len(data)
    if length >= 4:
        SOI, = struct.unpack('>H', data[0:2])
        EOI, = struct.unpack('>H', data[length-2:length])
        if SOI == 0xffd8 and EOI == 0xffd9:
            result = True

    return result


def ParseJpegFile(data):
    '''
    This function obtains the WV-XAE200WUX (aivmd) recognition results from the JPEG data.
    JPEG データから WV-XAE200WUX (aivmd) 認識結果を取得する。

    Args:
        data            [i] Data to be confirmed.
    Returns:
        result          True:   success
                        False:  failure
        aivmd_result    The WV-XAE200WUX (aivmd) recognition result.
    Raises
        None
    '''
    result = False
    aivmd_result = None

    if IsJpegFile(data) == True:
        next_data = data[2:]
        while True:
            result, tag, length, data, next_data = ParseJpegHeadder(next_data)

            if tag == 0xffda:   # SOS (Start Of Scan)
                break
            if result==False:
                break
            if tag == 0xfffe:   # COM (Comment)
                result, aivmd_result = ParseJpegComment(data)
                break

    return result, aivmd_result


if __name__ == "__main__":
    '''
    __main__ function.

    Raises
        FileNotFoundError
    '''
    filename = 'image_000001.jpg'

    with open(filename, 'rb') as fin:
        binaryData = fin.read()

    result, aivmd_result = ParseJpegFile(binaryData)
    if result==True:
        print(aivmd_result)
    else:
        print('Failure.')
