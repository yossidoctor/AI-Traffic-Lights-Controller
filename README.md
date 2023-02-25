# AI-Traffic-Lights-Controller

***Traffic Light Coordination using Q-Learning and Genetic Algorithms***

Traffic congestion has a non-negligible impact on health, the economy, and the quality of life. Inefficient traffic lights may cause congestion, impacting economic productivity, health, and quality of life. To address this issue, we built AI agents that used Q-Learning and genetic algorithms to coordinate traffic signal schedules and reduce waiting times.

## Table of Contents

- [Methodology](#Methodology)
- [Experimentation](#Experimentation)
- [Results](#Results)
- [Installation](#Installation)
- [Usage](#Usage)

## Methodology

We used a simulation of a single-lane two-way junction with two main phases of green-red light and two intermediate phases of yellow light. 

Our Q-Learning agent's state space was defined with the following parameters: the state of the traffic signal at the junction, the number of vehicles on the north-south route, the number of cars on the east-west highway, and an indicator of whether the junction is free of cars. The capacity of roads in each direction is 14 vehicles (without counting cars inside the junction), so the state space size is 784. The action space consists of two actions: changing the traffic flow direction or doing nothing.

The reward for each state was given according to the change in vehicle flow - the difference in the number of vehicles on the inbound roads between the current and the previous state.

Our genetic algorithm allowed us to look at a sequence of multiple actions at a time, rather than just a single action. This is better for our purpose because the cars on the roads and at the junction need time to accelerate to pass the junction once the traffic light switches from red to green, and they need time to slow down once it switches back from green to red. 

To decide what chain of actions to do next, the agent takes a snapshot of the simulation and tries to maximize the number of cars passing the junction. It generates a default set of sequences, checking if any of them passed at least 50% of the vehicles through at a fast enough rate. If it finds such a sequence, no evolution is done. Otherwise, using crossover and mutations, it generates sequences until it finds one good enough.

## Experimentation

We measured the default behavior of traffic lights using a timer-based system (fixed cycle) and a sensor-based system (longest queue first) and found that the sensor-based system performed better for every cycle length. We then trained our Q-Learning agent for 10,000 episodes, each containing 50 vehicles. The agent cut down the average waiting time of vehicles by up to 11% compared to the default behavior. Additionally, the collision rate went down. Interestingly, training for 20,000 and 50,000 episodes did not improve the results further.

## Results

Our Q-Learning agent reduced the average waiting time of vehicles by up to 11%, and the genetic algorithm-based agent reduced the waiting time by up to 7%, compared to the default behavior. These results demonstrate the effectiveness of our approach to coordinating traffic lights using AI.

## Installation

```bash
git clone https://github.com/yossidoctor/AI-Traffic-Lights-Controller.git
cd AI-Traffic-Lights-Controller
pip install -r requirements.txt
```


## Usage

```bash
python main.py -m [method] -e [number of episodes] -r
```

- -m or --method: specifies which method to use for the traffic light controller. The available methods are 'fc', 'lqf', 'qlearning', and 'search'.
- -e or --episodes: specifies the number of evaluation episodes to run.
- -r or --render: optional flag - displays the simulation window if included.
    
    
For example, this will run the default cycle method for 10 episodes and display the simulation window:
```bash
python main.py -m fc -e 10 -r
```
