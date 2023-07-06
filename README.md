
# Man vs Machine Resource Scheduling demo

The user can compare themselves to three AI algorithms in optimizing system metrics,
currently sum rate, fairness, ambulance timeouts, and mixed performance, by intelligent resource scheduling.
There is also a countdown challenge mode.

The relevant file to start the GUI demo is src/analysis/gui.py

Talking points:
- What is optimization criterion? Data Throughput? Fairness (How do we define that?)?
Special Objectives, e.g., ambulance traffic? Usually a mixed objective, depending on operator,
area (urban, non-urban, ...) -> Complex
- How does the Reinforcement Learned algorithm learn the relative importance of these factors? -> 
Trial and error, just like the player would when playing the demo
- You will notice: AI Algorithms are not trained to convergence, i.e., Max Fairness will not always find
the fairest allocation etc. This is not immediately obvious -> we must be mindful of that when applying AI
algorithms in practice

#### Folder Structure

|                  |                                                  |
|------------------|--------------------------------------------------|
| models           | trained models                                   |
| src              |                                                  |
| ├─ analysis      | GUI                                              |
| ├─ config        | configuration files                              |
| ├─ data          | data generation, loading, etc.                   |
| └─ models        | model training and inference                     |
| .gitignore       | .gitignore                                       |
| README.md        | readme                                           |
| requirements.txt | pip freeze > requirements.txt                    |
