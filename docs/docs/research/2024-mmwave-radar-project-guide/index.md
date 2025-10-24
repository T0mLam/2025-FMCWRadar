---
title: 2024-mmWaveRadarSensors project instructions
---

# Instructions for running the 2024-mmWaveRadarSensors project

This page contains the guide for running the human pose recognition model on TI IWRL6432.

## Download the zip file for the 2024-mmWaveRadarSensors project

[-> Download link](https://github.com/spe-uob/2024-mmWaveRadarSensors/archive/refs/heads/dev.zip)

![Download Project ZIP FILE](./download_project_zip.png)

## Install MMWAVE-L-SDK 05.04

:::important
MMWAVE-L-SDK 05.04 is **not** the latest version, it is an old version released in 2024. Please install this along with the latest version. You wouldn't be able to build last year's project with the new SDK.
:::

[-> Installation Link](https://www.ti.com/tool/download/MMWAVE-L-SDK/05.04.00.01)

Make sure the MMWAVE-L-SDK 05.04 is present in the `C:\ti` folder

![TI Folder](./ti_folder.png)


## Update CCS Settings

1. Navigate to `File -> Preferences -> Code Composer Studio Settings` 
    ![CCS Settings](./ccs_settings.png)
2. Refresh the *Discovered Products*
    ![Refresh Discovered Products](./refresh_discovered_products.png)
3. Make sure the MMWAVE-L-SDK 05.04 is the only entry showing up for mmWave low-power SDK
    ![Discovered Products](./discovered_products.png)

:::tip
Move the newer version of the MMWAVE-L-SDK out of the `C:\ti` directory temporarily if multiple versions are detected to ensure the project is compiled with version 05.04.
:::

## Build the project

1. Open the `ccs_demo_POSE_RELATIVE_Y` folder in CCS
    ![CCS Demo Folder](./ccs_demo_POSE_RELATIVE_Y_folder.png)
2. Press *Clean projects* then *Build projects*
    ![Build Projects](./build_projects.png)

## Run the build    

:::tip
**Make sure you have plugged in the board on your laptop and test the connection**
![Target Config Basic](./target_config_basic.png)
![Test Connection](./test_connection.png)
:::

1. Press `Start Debugging`
    ![Start Debugging](./start_debugging.png)
2. Navigate to the Debug tab on the left sidebar and press `Continue`
    ![Continue Debugging](./continue_debugging.png)
3. Observe the terminal output, the program should be running properly when you see the following CIO output
    ![CIO Output](./cio_output.png)

**If it does not work, press the small button on the board to reset and try again**

## Launch the visualizer

1. Navigate to `/path/to/2024-mmWaveRadarSensors/visualiser` (replace /path/to/... with the link of the visualizer folder)
2. Run the following command in the terminal 
    ```bash
    python main.py
    ```
3. Select the correct UART port, you can find it from device manager (in this example my webcam is blocked but it shouldn't affect the result anyways)
    ![Visualizer](./visualizer.png)
    ![Device Manager](./device_manager.png)
    