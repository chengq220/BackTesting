# BackTesting

## Setup
```
pip install -r requirements.txt
```

## Architecture (Psuedocode)
```
while event_queue_isnt_empty():
    event = get_latest_event_from_queue();
    if event.type == "tick":
        strategy.calculate_trading_signals(event);
    else if event.type == "signal":
        portfolio.handle_signal(event);
    else if event.type == "order":
        portfolio.handle_order(event);
    else if event.type == "fill":
        portfolio.handle_fill(event)
```

