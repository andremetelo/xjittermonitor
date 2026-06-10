# xjittermonitor

This is a small Python 3 app to test round-trip and jitter to specific servers on the Internet.

So, I was running into some weird video conferencing issues. I suspected there were latency and jitter problems, but I needed data. Therefore, I did what geeks do, I wrote a small piece of code to collect some statistics for these metrics on specific servers. 

It started with pings, then TCP requests, and eventually, I got a graphic mode to make it look good and show my wife something that made sense for her. I know, I still prefer the CLI version, but I understand why the boss wants a pretty picture.

There are some dependencies, but nothing crazy:
os, sys, subprocess, time, re, statistics, collections, socket, argparse, and matplotlib.

Feel free to use it however you feel like, and maybe give some feedback with ideas.

Enjoy

