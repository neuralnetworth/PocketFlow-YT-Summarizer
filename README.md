<h1 align="center">Explain Youtube Video To Me Like I'm 5</h1>

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

Have a 5-hour YouTube video but no time to watch it? This LLM application pulls the main topics and explains to you like you are 5, so you can catch up in just minutes.

<div align="center">
  <img src="./assets/front.png" width="700"/>
</div>

Design Doc: [docs/design.md](docs/design.md), Flow Source Code: [flow.py](flow.py)



## I built this in just an hour, and you can, too.

- Built With [Pocket Flow](https://github.com/The-Pocket/PocketFlow), a 100-line LLM framework that lets LLM Agents (e.g., Cursor AI) build Apps for you

- **Check out the Step-by-Step YouTube Tutorial:**
 
<br>
<div align="center">
  <a href="https://youtu.be/wc9O-9mcObc" target="_blank">
    <img src="./assets/youtube.png" width="500" alt="IMAGE ALT TEXT" style="cursor: pointer;">
  </a>
</div>
<br>

## Example Outputs

|  [<img src="https://img.youtube.com/vi/7ARBJQn6QkM/maxresdefault.jpg" width=200> ](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/NVIDIA%20CEO%20Jensen%20Huang's%20Vision%20for%20the%20Future.html) <br> **NVIDIA CEO Jensen Huang's Vision for the Future**  | [<img src="https://img.youtube.com/vi/_1f-o0nqpEI/maxresdefault.jpg" width=200> ](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/DeepSeek%2C%20China%2C%20OpenAI%2C%20NVIDIA%2C%20xAI%2C%20TSMC%2C%20Stargate%2C%20and%20AI%20Megaclusters%20%7C%20Lex%20Fridman%20Podcast%20%23459.html) <br> DeepSeek, China, OpenAI, NVIDIA, xAI, TSMC, Stargate, and AI Megaclusters | [<img src="https://img.youtube.com/vi/qTogNUV3CAI/maxresdefault.jpg" width=200> ](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/Demis%20Hassabis%20–%20Scaling%2C%20Superhuman%20AIs%2C%20AlphaZero%20atop%20LLMs%2C%20AlphaFold.html) <br> Demis Hassabis – Scaling, Superhuman AIs, AlphaZero atop LLMs, AlphaFold | [<img src="https://img.youtube.com/vi/JN3KPFbWCy8/maxresdefault.jpg" width=200> ](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/Elon%20Musk%3A%20War%2C%20AI%2C%20Aliens%2C%20Politics%2C%20Physics%2C%20Video%20Games%2C%20and%20Humanity%20%7C%20Lex%20Fridman%20Podcast%20%23400.html) <br> Elon Musk: War, AI, Aliens, Politics, Physics, Video Games, and Humanity |
| :-------------: | :-------------: | :-------------: | :-------------: |
|[<img src="https://img.youtube.com/vi/CnxzrX9tNoc/maxresdefault.jpg" width=200> ](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/In%20conversation%20with%20Elon%20Musk%3A%20Twitter's%20bot%20problem%2C%20SpaceX's%20grand%20plan%2C%20Tesla%20stories%20%26%20more.html) <br> **In conversation with Elon Musk: Twitter's bot problem, SpaceX's grand plan, Tesla stories & more** | [<img src="https://img.youtube.com/vi/blqIZGXWUpU/maxresdefault.jpg" width=200> ](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/In%20conversation%20with%20President%20Trump.html) <br> **In conversation with President Trump** |  [<img src="https://img.youtube.com/vi/v0gjI__RyCY/maxresdefault.jpg" width=200> ](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/Jeff%20Dean%20%26%20Noam%20Shazeer%20–%2025%20years%20at%20Google%3A%20from%20PageRank%20to%20AGI.html) <br> **Jeff Dean & Noam Shazeer – 25 years at Google: from PageRank to AGI** |  [<img src="https://img.youtube.com/vi/4pLY1X46H1E/maxresdefault.jpg" width=200> ](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/In%20conversation%20with%20Tucker%20Carlson%2C%20plus%20OpenAI%20chaos%20explained.html) <br> **In conversation with Tucker Carlson, plus OpenAI chaos explained** | 
 |[<img src="https://img.youtube.com/vi/xBMRL_7msjY/maxresdefault.jpg" width=200> ](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/Jonathan%20Ross%2C%20Founder%20%26%20CEO%20%40%20Groq%3A%20NVIDIA%20vs%20Groq%20-%20The%20Future%20of%20Training%20vs%20Inference%20%7C%20E1260.html) <br> **Jonathan Ross, Founder & CEO @ Groq: NVIDIA vs Groq - The Future of Training vs Inference** | [<img src="https://img.youtube.com/vi/u321m25rKXc/maxresdefault.jpg" width=200>](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/Volodymyr%20Zelenskyy%3A%20Ukraine%2C%20War%2C%20Peace%2C%20Putin%2C%20Trump%2C%20NATO%2C%20and%20Freedom%20%7C%20Lex%20Fridman%20Podcast%20%23456.html) <br>**Volodymyr Zelenskyy: Ukraine, War, Peace, Putin, Trump, NATO, and Freedom** |  [<img src="https://img.youtube.com/vi/YcVSgYz5SJ8/maxresdefault.jpg" width=200> ](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/Sarah%20C.%20M.%20Paine%20-%20Why%20Dictators%20Keep%20Making%20the%20Same%20Fatal%20Mistake.html) <br> **Sarah C. M. Paine - Why Dictators Keep Making the Same Fatal Mistake** |  [<img src="https://img.youtube.com/vi/4GLSzuYXh6w/maxresdefault.jpg" width=200> ](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/Satya%20Nadella%20–%20Microsoft’s%20AGI%20Plan%20%26%20Quantum%20Breakthrough.html) <br> **Satya Nadella – Microsoft’s AGI Plan & Quantum Breakthrough** | 
 |[<img src="https://img.youtube.com/vi/qpoRO378qRY/maxresdefault.jpg" width=200> ](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/Full%20interview%3A%20"Godfather%20of%20artificial%20intelligence"%20talks%20impact%20and%20potential%20of%20AI.html) <br> **Full interview: "Godfather of artificial intelligence" talks impact and potential of AI** |  [<img src="https://img.youtube.com/vi/OxP55dZjqZs/maxresdefault.jpg" width=200> ](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/The%20Stablecoin%20Future%2C%20Milei's%20Memecoin%2C%20DOGE%20for%20the%20DoD%2C%20Grok%203%2C%20Why%20Stripe%20Stays%20Private.html) <br> **The Stablecoin Future, Milei's Memecoin, DOGE for the DoD, Grok 3, Why Stripe Stays Private**   | [<img src="https://img.youtube.com/vi/oX7OduG1YmI/maxresdefault.jpg" width=200> ](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/The%20Future%20Mark%20Zuckerberg%20Is%20Trying%20To%20Build.html) <br> **The Future Mark Zuckerberg Is Trying To Build** |  [<img src="https://img.youtube.com/vi/f_lRdkH_QoY/maxresdefault.jpg" width=200> ](https://the-pocket.github.io/Tutorial-Youtube-Made-Simple/examples/Tucker%20Carlson%3A%20Putin%2C%20Navalny%2C%20Trump%2C%20CIA%2C%20NSA%2C%20War%2C%20Politics%20%26%20Freedom%20%7C%20Lex%20Fridman%20Podcast%20%23414.html) <br> **Tucker Carlson: Putin, Navalny, Trump, CIA, NSA, War, Politics & Freedom** | 

## How to Run

1. Implement `call_llm` in `utils/call_llm.py` so it takes a string and returns a string.

2. Install the dependencies and run the program:
```bash
pip install -r requirements.txt
python main.py --url "https://www.youtube.com/watch?v=example"
```

3. When it’s done, open output.html (created in the project folder) to see the results.
