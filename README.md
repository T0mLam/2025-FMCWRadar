# 2025-FMCWRadar

[![Docs](https://img.shields.io/badge/docs-website-blue)](https://spe-uob.github.io/2025-FMCWRadar)

## Project Overview
This project examines Texas Instruments (TI) FMCW radar sensors as compact, single-chip devices for human-motion analysis. These sensors integrate radio, processing, and antenna resources to estimate target distance, motion, and bearing, with the advantage of functioning in varied environments, lighting conditions and mitigating privacy concerns. These sensors are commonly applied to people-sensing tasks in indoor environments.

Our work during this project will begin with a research-first baseline. We will study the official TI materials and documentation to understand the sensor outputs and processing pipeline, define a clear data-collection and labelling protocol, assemble an internal dataset using the FMCW radar, and develop a machine learning model trained on the internal dataset to identify different people based on movement characteristics such as their unique walking gait. A visualisation tool will be created in order to view the captured radar data so results can be reviewed immediately.

## (Potential) Stakeholders
- End users such as:
    - Car owners using it to open their car
    - Security personnel using it as part of a security system
    - Healthcare
    - Civil infrustructure

## User stories
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





