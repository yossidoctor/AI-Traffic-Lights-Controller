# AI-Traffic-Lights-Controller

The project uses reinforcement learning and genetic algorithms to improve traffic flow and reduce vehicle waiting times in a single-lane two-way junction simulator by coordinating traffic signal schedules. 

[A complete 7-page project report is available  here](https://github.com/yossidoctor/AI-Traffic-Lights-Controller/blob/main/Traffic%20Control%20With%20AI%20-%20Project%20Report.pdf).


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
