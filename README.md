<h1 align="center">Explain Youtube Video To Me Like I'm 5</h1>

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

Have a 5-hour YouTube video but no time to watch it? This tool pulls the main topics and explains them in simple terms, so you can catch up in just minutes.

<div align="center">
  <img src="./examples/front.png" width="700"/>
</div>


- **Design Doc:** [docs/design.md](docs/design.md)

- **Built With:** [Pocket Flow](https://github.com/The-Pocket/PocketFlow), a 100-line LLM framework that lets you build AI apps by chatting with LLM agents.

- I created this in just a few hours using Pocket Flow + Cursor AI, and you can, too.
 
-  A **step-by-step coding video tutorial** is on the way—stay tuned!

## How to Run

1. Implement `call_llm` in `utils/call_llm.py` so it takes a string and returns a string.

2. Install the dependencies and run the program:
```bash
pip install -r requirements.txt
python main.py --url "https://www.youtube.com/watch?v=example"
```

3. When it’s done, open output.html (created in the project folder) to see the results.
