<h1 align="center">Explain Youtube Video To Me Like I'm 5</h1>

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

Have a 5-hour YouTube video but no time to watch it? This LLM application pulls the main topics and explains them in simple terms, so you can catch up in just minutes.

<div align="center">
  <img src="./examples/front.png" width="700"/>
</div>


- **Design Doc:** [docs/design.md](docs/design.md)

- **Built With:** [Pocket Flow](https://github.com/The-Pocket/PocketFlow), a 100-line LLM framework that lets you build AI apps by chatting with LLM agents.

- I built this in **just a few hours** using Pocket Flow + Cursor AI, and you can, too.
 
-  A **step-by-step coding video tutorial** is on the way—stay tuned!

## More Examples

|[<img src="https://img.youtube.com/vi/3Fx5Q8xGU8k/hqdefault.jpg" width=200>](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/Competition%20is%20for%20Losers%20with%20Peter%20Thiel.html) <br>Competition is for Losers with Peter Thiel | [<img src="https://img.youtube.com/vi/_1f-o0nqpEI/maxresdefault.jpg" width=200> ](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/DeepSeek%2C%20China%2C%20OpenAI%2C%20NVIDIA%2C%20xAI%2C%20TSMC%2C%20Stargate%2C%20and%20AI%20Megaclusters%20%7C%20Lex%20Fridman%20Podcast%20%23459.html) <br> DeepSeek, China, OpenAI, NVIDIA, xAI, TSMC, Stargate, and AI Megaclusters | [<img src="https://img.youtube.com/vi/_1f-o0nqpEI/maxresdefault.jpg" width=200> ](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/Demis%20Hassabis%20–%20Scaling%2C%20Superhuman%20AIs%2C%20AlphaZero%20atop%20LLMs%2C%20AlphaFold.html) <br> DeepSeek, China, OpenAI, NVIDIA, xAI, TSMC, Stargate, and AI Megaclusters | [<img src="https://img.youtube.com/vi/_1f-o0nqpEI/maxresdefault.jpg" width=200> ](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/Elon%20Musk%3A%20War%2C%20AI%2C%20Aliens%2C%20Politics%2C%20Physics%2C%20Video%20Games%2C%20and%20Humanity%20%7C%20Lex%20Fridman%20Podcast%20%23400.html) <br> DeepSeek, China, OpenAI, NVIDIA, xAI, TSMC, Stargate, and AI Megaclusters |
| :-------------: | :-------------: | :-------------: | :-------------: |
|[<img src="https://img.youtube.com/vi/3Fx5Q8xGU8k/hqdefault.jpg" width=200> ](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/In%20conversation%20with%20Elon%20Musk%3A%20Twitter's%20bot%20problem%2C%20SpaceX's%20grand%20plan%2C%20Tesla%20stories%20%26%20more.html) <br> **Competition is for Losers with Peter Thiel** | [<img src="https://img.youtube.com/vi/_1f-o0nqpEI/maxresdefault.jpg" width=200> ](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/In%20conversation%20with%20President%20Trump.html) <br> **DeepSeek, China, OpenAI, NVIDIA, xAI, TSMC, Stargate, and AI Megaclusters** |  [<img src="https://img.youtube.com/vi/_1f-o0nqpEI/maxresdefault.jpg" width=200> ](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/In%20conversation%20with%20President%20Trump.html) <br> **DeepSeek, China, OpenAI, NVIDIA, xAI, TSMC, Stargate, and AI Megaclusters** |  [<img src="https://img.youtube.com/vi/_1f-o0nqpEI/maxresdefault.jpg" width=200> ](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/In%20conversation%20with%20Tucker%20Carlson%2C%20plus%20OpenAI%20chaos%20explained.html) <br> **DeepSeek, China, OpenAI, NVIDIA, xAI, TSMC, Stargate, and AI Megaclusters** | 
 

## How to Run

1. Implement `call_llm` in `utils/call_llm.py` so it takes a string and returns a string.

2. Install the dependencies and run the program:
```bash
pip install -r requirements.txt
python main.py --url "https://www.youtube.com/watch?v=example"
```

3. When it’s done, open output.html (created in the project folder) to see the results.
