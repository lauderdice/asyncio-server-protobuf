## Demonstration of an asynchronous Python server receiving Protobuf messages

First it is necessary to install the requirements.

    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

To run the server: In window 1 run:
    
    python server.py --address=127.0.0.1 --port=12345 --dataformat=proto

or just:

    python server.py

which uses defaults in constants.py.

To run a test client: In window 2 run:

    python client.py
