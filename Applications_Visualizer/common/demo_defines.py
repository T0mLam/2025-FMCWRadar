# OOB demo names must be different
DEMO_OOB_x432 = 'x432 Out of Box Demo'

DEMO_3D_PEOPLE_TRACKING = '3D People Tracking'
DEMO_VITALS = 'Vital Signs with People Tracking'
DEMO_GESTURE = 'Gesture Recognition'
DEMO_SURFACE = 'Surface Classification'
DEMO_PC_CLASS = 'Point Cloud Classification'

# Com Port names
CLI_XDS_SERIAL_PORT_NAME = 'XDS110 Class Application/User UART'
DATA_XDS_SERIAL_PORT_NAME = 'XDS110 Class Auxiliary Data Port'
CLI_SIL_SERIAL_PORT_NAME = 'Enhanced COM Port'
DATA_SIL_SERIAL_PORT_NAME = 'Standard COM Port'

BUSINESS_DEMOS = {
    "Industrial": [
        DEMO_OOB_x432
    ],
    "BAC": [
       DEMO_OOB_x432, DEMO_3D_PEOPLE_TRACKING, DEMO_GESTURE
    ]
}

# Populated with all devices and the demos each of them can run
DEVICE_DEMO_DICT = {
    "xWRL6432": {
        "isxWRx843": False,
        "isxWRLx432": True,
        "isxWRLx844" : False,
        "singleCOM": True,
        "demos": [DEMO_OOB_x432]
    }
}
