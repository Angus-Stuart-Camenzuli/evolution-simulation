# Ecosystem Evolutionary Simulation
This is an ecosystem evolution simulation where each organism has its own simple neural network for a brain. The organisms goal is to eat food represented by the little green squares to gain enough energy to reproduce. 

Reproduction is built to model evolution in the way that offspring have a random chance to mutate the weights and biases. So in a sense its a visual representation of a genetic algorithm. 

## Requirements
Python 3.9+

## Setup

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python world.py
```

**Windows (PowerShell)**
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py world.py
```

**Windows (Command Prompt)**
```cmd
py -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
py world.py
```

To leave the environment: `deactivate`

## New Ideas/Features
- Increase size when eat food. This could also increase move costs and reproduction costs. 
- Change starting traits