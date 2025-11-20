# Local File Imports
from parse_common import *
from parse_tlvs import *


def parseStandardFrame(frameData, DEBUG):
    headerStruct = 'Q8I'
    frameHeaderLen = struct.calcsize(headerStruct)
    tlvHeaderLength = 8
    frameNum = 0
    totalPacketLen = 0
    numDetectedObj = 0
    numTLVs = 0

    outputDict = {}
    outputDict['error'] = 0

    try:
        # Read in frame Header
        magic, version, totalPacketLen, platform, frameNum, timeCPUCycles, numDetectedObj, numTLVs, subFrameNum = struct.unpack(
            headerStruct, frameData[:frameHeaderLen])
    except:
        print('Error: Could not read frame header')
        outputDict['error'] = 1

    if DEBUG: print("\nframe, numObjs:", frameNum, numDetectedObj)
    if DEBUG: print("numTLV's:", numTLVs)

    # Move frameData ptr to start of 1st TLV
    frameData = frameData[frameHeaderLen:]

    # Save frame number to output
    outputDict['frameNum'] = frameNum
    outputDict['totalPacketLen'] = totalPacketLen

    # Initialize the point cloud struct since it is modified by multiple TLV's
    # Each point has the following: X, Y, Z, Doppler, SNR, Noise, Track index
    outputDict['pointCloud'] = np.zeros((numDetectedObj, 7), np.float64)
    # Initialize the track indexes to a value which indicates no track
    outputDict['pointCloud'][:, 6] = 255

    # Find and parse all TLV's
    for i in range(numTLVs):
        # print ("Frame Data at start of TLV: ", frameData[:10])
        try:
            tlvType, tlvLength = tlvHeaderDecode(frameData[:tlvHeaderLength])
            frameData = frameData[tlvHeaderLength:]
            # deb_gp         tlvLength = tlvLength - tlvHeaderLength     # removed for the presence demo.
            if DEBUG: print("TLV type, headerlength, datalength:", tlvType, tlvHeaderLength, tlvLength)
        except:
            print('TLV Header Parsing Failure')
            outputDict['error'] = 2
        # print ("Frame Data before tlv parse: ", frameData[:10])

        if (outputDict['error'] == 2):
            print("Ignored frame due to parsing error")
            break
        # Detected Points
        if (tlvType == MMWDEMO_OUTPUT_MSG_DETECTED_POINTS):
            outputDict['numDetectedPoints'], outputDict['pointCloud'] = parsePointCloudTLV(frameData[:tlvLength],
                                                                                           tlvLength,
                                                                                           outputDict['pointCloud'])
        # Range Profile gen1,2
        elif (tlvType == MMWDEMO_OUTPUT_MSG_RANGE_PROFILE):
            outputDict['rangeProfile'] = parseRangeProfileTLV(frameData[:tlvLength])
        # Range Profile Major
        elif (tlvType == MMWDEMO_OUTPUT_EXT_MSG_RANGE_PROFILE_MAJOR):
            outputDict['rangeProfileMajor'] = parseRangeProfileTLV(frameData[:tlvLength])
            # print("TLV Type: MMWDEMO_OUTPUT_EXT_MSG_RANGE_PROFILE_MAJOR")
            # print(outputDict['rangeProfileMajor'])
        # Range Profile Minor
        elif (tlvType == MMWDEMO_OUTPUT_EXT_MSG_RANGE_PROFILE_MINOR):
            outputDict['rangeProfileMinor'] = parseRangeProfileTLV(frameData[:tlvLength])
        # Noise Profile
        elif (tlvType == MMWDEMO_OUTPUT_MSG_NOISE_PROFILE):
            pass
        # Static Azimuth Heatmap
        elif (tlvType == MMWDEMO_OUTPUT_MSG_AZIMUT_STATIC_HEAT_MAP):
            pass
        # Range Doppler Heatmap
        elif (tlvType == MMWDEMO_OUTPUT_MSG_RANGE_DOPPLER_HEAT_MAP):
            pass
        # Performance Statistics
        elif (tlvType == MMWDEMO_OUTPUT_MSG_STATS):
            pass
        # Side Info
        elif (tlvType == MMWDEMO_OUTPUT_MSG_DETECTED_POINTS_SIDE_INFO):
            outputDict['pointCloud'] = parseSideInfoTLV(frameData[:tlvLength], tlvLength, outputDict['pointCloud'])
        # Azimuth Elevation Static Heatmap
        elif (tlvType == MMWDEMO_OUTPUT_MSG_AZIMUT_ELEVATION_STATIC_HEAT_MAP):
            pass
        # Temperature Statistics
        elif (tlvType == MMWDEMO_OUTPUT_MSG_TEMPERATURE_STATS):
            pass
        # Spherical Points
        elif (tlvType == MMWDEMO_OUTPUT_MSG_SPHERICAL_POINTS):
            outputDict['numDetectedPoints'], outputDict['pointCloud'] = parseSphericalPointCloudTLV(
                frameData[:tlvLength], tlvLength, outputDict['pointCloud'])
        # Target 3D
        elif (tlvType == MMWDEMO_OUTPUT_MSG_TRACKERPROC_3D_TARGET_LIST):
            outputDict['numDetectedTracks'], outputDict['trackData'] = parseTrackTLV(frameData[:tlvLength], tlvLength)
        elif (tlvType == MMWDEMO_OUTPUT_MSG_TRACKERPROC_TARGET_HEIGHT):
            outputDict['numDetectedHeights'], outputDict['heightData'] = parseTrackHeightTLV(frameData[:tlvLength],
                                                                                             tlvLength)
        # Target index
        elif (tlvType == MMWDEMO_OUTPUT_MSG_TRACKERPROC_TARGET_INDEX):
            outputDict['trackIndexes'] = parseTargetIndexTLV(frameData[:tlvLength], tlvLength)
        # Capon Compressed Spherical Coordinates
        elif (tlvType == MMWDEMO_OUTPUT_MSG_COMPRESSED_POINTS):
            outputDict['numDetectedPoints'], outputDict['pointCloud'] = parseCompressedSphericalPointCloudTLV(
                frameData[:tlvLength], tlvLength, outputDict['pointCloud'])
        # Occupancy State Machine
        elif (tlvType == MMWDEMO_OUTPUT_MSG_OCCUPANCY_STATE_MACHINE):
            outputDict['occupancy'] = parseOccStateMachTLV(frameData[:tlvLength])
        elif (tlvType == MMWDEMO_OUTPUT_MSG_VITALSIGNS):
            outputDict['vitals'] = parseVitalSignsTLV(frameData[:tlvLength], tlvLength)
        elif (tlvType == MMWDEMO_OUTPUT_EXT_MSG_DETECTED_POINTS):

            outputDict['numDetectedPoints'], outputDict['pointCloud'] = parsePointCloudExtTLV(frameData[:tlvLength],
                                                                                              tlvLength,
                                                                                              outputDict['pointCloud'])

            ## 1. Extract the range, height (90deg rotated board) and SNR the objects detected
            ## ignore the first nearfield measurement.
            # y = []
            # x = []
            # SNR = []
            # for i in range(outputDict['numDetectedPoints']):
            #     y.append(outputDict['pointCloud'][i][1])
            #     x.append(outputDict['pointCloud'][i][0])
            #     SNR.append(outputDict['pointCloud'][i][4])
            #     # if DEBUG:
            #     if (y[i] > 0.10):  # only print if > 10cm
            #         print(f'PC Range: {y[i]:.3f}, SNR: {SNR[i]}')
            #         print(f'PC Height: {x[i]:.3f}, SNR: {SNR[i]}\n')
            ## End 1

            ## 2. Extract the range and SNR the objects detected with corner reflector at fixed distance.
            ## ignore the first nearfield measurement.
            ## using the high accuracy levels sensing lab
            # y = []
            # SNR = []
            # Noise = []
            # for i in range(outputDict['numDetectedPoints']):
            #     y.append(outputDict['pointCloud'][i][1])
            #     SNR.append(outputDict['pointCloud'][i][4])
            #     Noise.append(outputDict['pointCloud'][i][5])
            #     if DEBUG:
            #         if (y[i] > 0.10):  # only print if > 10cm
            #             print(f'Range: {y[i]:.3f}, SNR: {SNR[i]}')
            ## End 2

            ## 3. extract the y-axis 5 closest values and print them out"
            # values = []
            # for i in range(outputDict['numDetectedPoints']):
            ##     " Y is the second value of each point cloud entry"
            #     values.append(list(outputDict['pointCloud'][i][1:2]))
            ## " sort from closest to furthest"
            # values.sort()
            ## " convert from list to array"
            # y_array = np.array(values)
            # print(y_array[:5])
            ## End 3

        # Presence Indication
        elif (tlvType == MMWDEMO_OUTPUT_MSG_PRESCENCE_INDICATION):
            pass
        elif (tlvType == MMWDEMO_OUTPUT_EXT_MSG_ENHANCED_PRESENCE_INDICATION):
            outputDict['presence_indication'] = frameData[:tlvLength]
        # print(outputDict['presence'])
        # Performance Statistics
        elif (tlvType == MMWDEMO_OUTPUT_MSG_EXT_STATS):
            outputDict['procTimeData'], outputDict['powerData'], outputDict['tempData'] = parseExtStatsTLV(
                frameData[:tlvLength],
                tlvLength,
                outputDict
            )
            if DEBUG == 1:
                print(outputDict['tempData'])

        # 3D target list and index
        elif (tlvType == MMWDEMO_OUTPUT_EXT_MSG_TARGET_LIST):
            outputDict['target_list'] = frameData[:tlvLength]
            outputDict['tlvLength'] = tlvLength

        elif (tlvType == MMWDEMO_OUTPUT_EXT_MSG_TARGET_INDEX):
            outputDict['target_index'] = frameData[:tlvLength]
            " Number of Points x 1 Byte	Contains target ID, allocating every point to a specific target or no target"
            # print(outputDict['target_index'])

        # micro doppler outputs
        elif (tlvType == MMWDEMO_OUTPUT_EXT_MSG_MICRO_DOPPLER_RAW_DATA):
            outputDict['micro_doppler_raw'] = frameData[:tlvLength]
        elif (tlvType == MMWDEMO_OUTPUT_EXT_MSG_MICRO_DOPPLER_FEATURES):
            outputDict['micro_doppler_features'] = frameData[:tlvLength]
        elif (tlvType == MMWDEMO_OUTPUT_EXT_MSG_CLASSIFIER_INFO):
            outputDict['classifier_info'] = frameData[:tlvLength]
        elif (tlvType == MMWDEMO_OUTPUT_MSG_ML_CLASSIFICATION):
            outputDict['classifier_info'] = frameData[:tlvLength]
            outputDict['mlType'], outputDict['mlResult'], outputDict['mlProbabilities'] = parseClassTLV(
                frameData[:tlvLength], tlvLength)
            # parseClassTLV(frameData[:tlvLength], tlvLength)
            # print(outputDict['mlType'], ": ", outputDict['mlResult'])
        elif (tlvType == MMWDEMO_OUTPUT_MSG_GESTURE_PRESENCE_x432):
            print(frameData[:tlvLength])
            outputDict['presence'] = parseGesturePresenceTLV6432(frameData[:tlvLength], tlvLength)
            # print(outputDict['presence'])
        elif (tlvType == MMWDEMO_OUTPUT_MSG_GESTURE_CLASSIFIER_6432):
            gestureDict = {b'\x01': 'Left-to-Right', b'\x02': 'Right-to-Left',
                           b'\x03': 'Up-to-Down', b'\x04': 'Down-to-Up',
                           b'\x05': 'Push', b'\x06': 'Pull'}

            gestureInput = frameData[:tlvLength]
            if gestureInput != b'\x00':
                print(gestureDict[gestureInput])

        elif (tlvType == MMWDEMO_OUTPUT_MSG_GESTURE_FEATURES_6432):
            # outputDict['presence'] = parseGesturePresenceTLV6432(frameData[:tlvLength], tlvLength)
            # print(outputDict['presence'])
            pass
        elif (tlvType == MMWDEMO_OUTPUT_MSG_GESTURE_PRESENCE_THRESH_x432):
            # outputDict['presence'] = parseGesturePresenceTLV6432(frameData[:tlvLength], tlvLength)
            # print(outputDict['presence'])
            pass
        elif (tlvType == MMWDEMO_OUTPUT_EXT_MSG_RX_CHAN_COMPENSATION_INFO):
            compStruct = '13f'  # One byte per index
            compSize = struct.calcsize(compStruct)
            coefficients = np.empty(compSize)
            coefficients = struct.unpack(compStruct, frameData[:tlvLength])
            print(coefficients)
            outputDict['RXChanCompInfo'] = coefficients

        else:
            print("Warning: invalid TLV type: %d" % (tlvType))

        # Move to next TLV
        frameData = frameData[tlvLength:]
    return outputDict


# Decode TLV Header
def tlvHeaderDecode(data):
    tlvType, tlvLength = struct.unpack('2I', data)
    return tlvType, tlvLength
