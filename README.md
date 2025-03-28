This is a demo example of how to incorporate an LLM to be able to trade on the HyperLiquid blockchain. We trade using HYPE only for now.
It is meant to show how one may implement incorporating market data into an LLM which can then make predictions as to what types of bets to make.

Currently we support basic SHORT/LONG positions where one can specify TAKEPROFIT/STOPLOSS or both.

High Level Overview
-------------------
0. The driver code can be found in `src/main.py` which runs the main flow.
1. The flow starts as follows. every 120 seconds, we provide some context to the LLM (refer to the folder `src/contexts`). We provide the current open bets, the history of the price of HYPE coin, and some social media context (this doesn't work as it requires a paid API key) and provides it to the LLM, which will predict what trade to run. The code is in `src/llm/basic_trading_agent.py`
2. Given the extracted strategy, we maintain a order queue which takes a queue of the trades to run. We support basic take profit and stop loss bets. The take profit orders have to be split into two separate orders, the logic of which can be found in `src/trade/order_queue.py`. There is a poller run every 20 seconds which will clean up any bids which have succesfully run on the blockchain and remove it from our internal memory, and schedule any follow up bids if required.

Instructions
------------
1. Open the project in vscode.
2. Fill in the configuration in `config.json` in the root folder. Take `config.json.example` as an example.
3. In vscode, run the configuration `Run Me`.
4. Warning: The trader is not perfect, it is just a prototype. Don't run it with actual funds. In the current setup, the code runs on the test chain, but you would need some Perpetual futures attached to your account so see orders getting placed onto the blockchain.