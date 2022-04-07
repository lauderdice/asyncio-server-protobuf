## Demonstration of an asynchronous Python server receiving Protobuf messages

In window 1 run:
    
    python server.py --address=127.0.0.1 --port=12345 --dataformat=proto

or just:

    python server.py

which uses defaults in constants.py.

In window 2 run:

    python client.py

