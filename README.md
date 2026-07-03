# BackTesting

## Setup
```
pip install -r requirements.txt
```

## Architecture (Psuedocode)
- Event→ Abstraction for different events that are used to signal specific functionalities
1. Data-Hander → provides/updates the available information (emits MarketEvent)
2. Strategy → react to MarketEvent and give a new directional signal (emits SignalEvent)
3. Portfolio → react to SignalEvent, and takes into account the current portfolio and gives a reasonable executable amount for those SignalEvent directions (via OrderEvent)
4. Execution → react to OrderEvent and execute the order (emit FillEvent)
5. Update → React to FillEvent and update the portfolio to reflect the fill order

```
while event_queue_isnt_empty():
    event = get_latest_event_from_queue();
    if event.type == "Market":
        strategy.calculate_trading_signals(event);
    else if event.type == "signal":
        portfolio.handle_signal(event);
    else if event.type == "order":
        execution.handle_order(event);
    else if event.type == "fill":
        portfolio.handle_fill(event)
```

## Setting up OLLAMA
## Reference
www.quantstart.com
