# The World in One Day: Friday 20 November 2026

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/syhham/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/syhham/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

One picture that sums up Friday 20 November 2026: 36 stories from 7 regions, on a single front page.

## The lead

The war reached NATO. Russia's biggest barrage of the month hit three Dnipro bridges in Kyiv, and two missiles and a drone came down in Poland. Eight people were killed across Ukraine. NATO called it a grave violation. That is the one big hero at the top, because it is the story that changes what the day means.

## What is inside

- The day in numbers: 3 Dnipro bridges hit, 8 killed across Ukraine, 300,000+ evacuated for Cyclone Akvan, the S&P 500 down 3.7%, Bayer's $7.25bn Roundup deal, 100,000 youth visas in the EU-UK reset.
- Two more heroes: Wall Street's AI boom turning to bust, and Cyclone Akvan making landfall with the shelters holding.
- Ten drawn cards, only for the heavy stories: the COP31 talks running past their deadline, a tanker burning in the Strait of Hormuz, the EU-UK reset, Estonia sealing its border with Russia, Baghdad walking back into a militia town, Gaza, Bangladesh, Bayer, a 6.7 quake in Peru, and Europe weighing Putin's Moscow invitation.
- A world map with numbered pins for stories 1 to 13, and 23 numbered briefs for the rest of the day.
- A DATE CHECK box at the bottom that names the Thursday 19 November news left out on purpose: the Trump-Xi-Putin declaration in Shenzhen, the ICJ Myanmar ruling, Anthropic's IPO day, and GTA VI's launch day.
- Every drawn story carries a REPORTED or CLAIM label. REPORTED means named sources. CLAIM means one side says so.

## How it was built

The hero and card pictures are AI-generated illustrations with no text in them. The headlines, numbers, map, and briefs are composited on top with PIL by `build_image.py`, so the text stays sharp and the facts stay consistent. `main.py` copies the finished `entry.png` to `/output/entry.png` using the standard library only. Two runs write identical bytes.

Sources: Reuters, AP, AFP, BBC, Al Jazeera, IMD, WSJ. All pictures are AI-generated illustrations. The map is drawn in code.

## Run it

```sh
python3 main.py
```

That writes the front page to `/output/entry.png`.

---

<sub>Entered on [make.fun](https://make.fun/?ref=4347jd65&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
