# 2025-FMCWRadar

<p align="left">
  <img src="https://skillicons.dev/icons?i=python,pytorch,opencv,docker" />
</p>


### View our documentation website below:
[![Docs](https://img.shields.io/badge/docs-website-blue)](https://spe-uob.github.io/2025-FMCWRadar)

## Table of Contents

- [Project Overview](#project-overview)
- [Stakeholders](#stakeholders)
- [User Stories](#user-stories)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Architecture diagram](#architecture-diagram)
- [Industrial Visualiser User Instructions](#industrial-visualiser-user-instructions)
- [Launching the docs website](#launching-the-docs-website)
- [Internal Links](#internal-links)
- [Team Members](#team-members)
- [Client Contacts](#client-contacts)

## Project Overview
This project examines Texas Instruments (TI) FMCW radar sensors as compact, single-chip devices for human-motion analysis. These sensors integrate radio, processing, and antenna resources to estimate target distance, motion, and bearing, with the advantage of functioning in varied environments, lighting conditions and mitigating privacy concerns. These sensors are commonly applied to people-sensing tasks in indoor environments.

Our work during this project will begin with a research-first baseline. We will study the official TI materials and documentation to understand the sensor outputs and processing pipeline, define a clear data-collection and labelling protocol, assemble an internal dataset using the FMCW radar, and develop a machine learning model trained on the internal dataset to identify different people based on movement characteristics such as their unique walking gait. A visualisation tool will be created in order to view the captured radar data so results can be reviewed immediately.

## Stakeholders
**Texas Instruments’ (TI) Staff**: 
- Product & Solutions team: Require a robust, reproducible demo using FMCW radar outputs to validate people-sensing use cases and surface documentation gaps to test their technology.
  
- Sales team: Require clear examples, data formats, and reference flows to help market their radars to customers.

**Texas Instruments’ (TI) customers**:
- Civil tech companies: Want to implement reliable occupancy sensing technology for public facilities and stations.
  
- Healthcare technology providers: These companies seek privacy preserving patient movement monitoring systems, and Texas Instruments’ radars allow for that privacy.
  
- Automotive & Mobility companies: These businesses are interested in hands free vehicle access and in-cabin/approach detection technology that is robust in a variety of conditions and lighting.

**End Users**:
- Security Guards: Benefit from timely presence alerts when they’re not actively watching monitors.
  
- Patients in clinical rooms & elderly at home: Gain discreet safety monitoring without the use of cameras to prevent accidents from happening.
  
- Car Owners: Expect doors to open hands free without false triggers.


## User Stories
- **Car owners:**  
  As a *car owner*, I want to be able to open my car door hands free, so that I don’t have to put down my shopping, child, or anything else I'm carrying. This also prevents my hands from getting wet from a wet handle.
  
- **Security personnel:**  
  As a *security guard*, I want there to be an early warning system when people are detected, so that if I am not actively monitoring the surveillance systems, there is an extra layer of security.

- **Healthcare:**  
  As a *nurse*, I want ensure that patients under care are stable, without breaching their privacy.

- **Civil infrastructure:**  
  As a *civil engineer*, I want to design a public bathroom that will automatically lock or unclock depending on occupancy.

- **Texas Instruments (TI):**  
  As a *Texas Instruments (TI) Solutions Engineer*, I want a robust, reproducible demo and evaluation using our FMCW Radar outputs so that we can validate people-sensing use cases and identify gaps in our documentation and examples.

## Project Structure
The below showcase how our sprints have been structed for the FMCW Radar project since TB2:
- [All Sprints](docs/docs/general/sprints)
- [Sprint 1](docs/docs/general/sprints/sprint-1.md)
- [Sprint 2](docs/docs/general/sprints/sprint-2.md)
- [Sprint 3](docs/docs/general/sprints/sprint-3.md)

It is recommended to view the above using our documentation website.

## Tech Stack
### Hardware
- [**TI IWRL6432BOOST Radar**](https://www.ti.com/tool/IWRL6432BOOST?keyMatch=iwrl6432boost&tisearch=universal_search)
- [Logitech C720 Webcam](https://www.logitech.com/en-gb/shop/p/c270-hd-webcam)

### Software
- [**Python (3.10)**](https://www.python.org)
- [**Jupyter Notebook**](https://jupyter.org)
- [**PyTorch**](https://pytorch.org)

### Developer tools
| Tool | Why we use it |
|---|---|
| [TI mmWave Software Development Kit](https://www.ti.com/tool/MMWAVE-L-SDK) | TI’s official kit providing firmware, drivers, and reference demos/tools for configuring the sensor and processing mmWave data. |
| [Code Composer Studio (CCS)](https://www.ti.com/tool/CCSTUDIO) | TI’s IDE for building, flashing, and debugging code on TI devices. |
| [Docusaurus](https://spe-uob.github.io/2025-FMCWRadar/) | Builds and hosts the documentation website. |
| [PySide2](https://pypi.org/project/PySide2/) | Desktop GUI framework for building the visualiser UI. |
| [PyOpenGL](https://pypi.org/project/PyOpenGL/) | Hardware-accelerated 2D/3D rendering. |
| [pyqtgraph](https://www.pyqtgraph.org/) | Fast real-time plotting for streaming signals. |
| [pyserial](https://pypi.org/project/pyserial/) | Reads radar frames over UART/serial. |
| [NumPy](https://numpy.org/) | Efficient numerical processing on incoming frames/point clouds. |
| [OpenCV](https://pypi.org/project/opencv-python/) | Image-style processing and display utilities. |
| [json-fix](https://pypi.org/project/json-fix/) | More robust JSON handling for config files. |
| [PyInstaller](https://pyinstaller.org/) | Packages the visualiser into a standalone executable for distribution. |
| [Git](https://git-scm.com/about) + [GitHub](https://github.com/) | Version control and collaboration. |
| [ONNX](https://onnx.ai/) | We use ONNX to export trained PyTorch models into a portable format that can be compiled into C/C++ binaries for the Radar. |
## Architecture diagram

![Architecture Diagram](</images/TI diagram.png>)

## Industrial Visualiser User Instructions 

<details>
<summary><strong>Click to expand</strong></summary>

### In Applications_Visualizer\Industrial_Visualizer open IndustrialVisualiser.exe
![Industrial Visualiser setup](</images/Industrial_Visualiser_1.jpg>)
### 1. choose xWRL6432 device
### 2.  a) device manager find UART prt number
  ![Device manager COM port](</images/Device_manager.jpg>)
### b) Enter the COM port number in CLI port feld
### 3. Choose x432 Out of Box Demo in demo field
---
### Functionality:
- Press the connect button, then press the Select config button.
- In Applications_Visualizer\Industrial_Visualizer\chrip_configs choose one of the config files and press Open. 
![Chrip config load](</images/Industrial_Visualiser_2.jpg>)
- Press the Start and Send configuration button.
- To record data: set the time in seconds (3 seconds is the default) and press the Record Data button.
![Data record button](</images/Industrial_Visualiser_3.jpg>)
- Recorded data will be located in Applications_Visualizer\Industrial_Visualizer\binData

</details>

## Launching the docs website

1. install [node.js & npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
2. Follow the step by step instructions in [`/docs/README.md`](/docs/README.md)

## Internal Links

- [Kanban Board](https://github.com/orgs/spe-uob/projects/343)
- [Gantt Chart](https://github.com/orgs/spe-uob/projects/343/views/2)

## Team Members

| Name            | Email                             |
|-----------------|-----------------------------------|
| Alina Zubova    | wn23635@bristol.ac.uk             |
| Dan Robb        | ff24459@bristol.ac.uk             |
| Henry Edwards   | ym24345@bristol.ac.uk             |
| Talal Aljallal  | talal.aljallal.2023@bristol.ac.uk |
| Tom Lam         | tom.lam.2024@bristol.ac.uk        |  
| Michal Berkasiuk| qk24603@bristol.ac.uk             | 

## Client Contacts

| Name            | Email                             |
|-----------------|-----------------------------------|
| Greg Peake      | g-peake@ti.com                    |
| Pedrhom Nafisi  | p-nafisi@ti.com                   |











