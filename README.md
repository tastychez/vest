# Canary   
A digital canary for mines that detects dangerous gases in real time and maps their spread to prevent accidents and save lives. Built during YHack to explore low-cost, real-time safety systems for hazardous environments.

![IMG_5080](https://github.com/user-attachments/assets/d1e8b46a-199c-4837-937f-14cb1c8d3ec8)
![Assem](https://github.com/user-attachments/assets/2bf839d6-3684-4062-ab21-7aaa24be9c88)


## Purpose
Mining environments can become dangerous without warning due to toxic gas buildup and changing humidity conditions. Canary is designed to act as an early warning system by continuously monitoring environmental data, detecting hazardous conditions, and helping visualize how danger spreads through tunnels. 

## Tech Stack
* Raspberry Pi 4 Model B
* Depth camera module
* Python
* MQ-series gas sensors
* DHT11 humidity sensor

## System Flow
The system operates in a continuous loop to ensure real-time responsiveness:
1. Gas sensors and the humidity sensor constantly collect environmental data from the surroundings.
2. The system compares incoming readings against predefined safety thresholds for gas concentration and humidity levels.
![](https://i.imgur.com/0w1RnsA.png)
3. If conditions are safe, monitoring continues. If thresholds are exceeded, the system triggers alerts and updates a map to reflect hazardous zones and gas spread.
4. This cycle runs continuously, allowing Canary to provide live updates and evolving situational awareness.
