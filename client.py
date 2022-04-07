import asyncio
import datetime
import random

from measurement_pb2 import MeasurementRecord, RequestMessage, ResponseMessage
import constants as C
from enums import PersonName

people = [person.value for person in list(PersonName)]

def get_random_message() -> RequestMessage:

    reqm = RequestMessage()
    record = MeasurementRecord()
    record.id = random.randint(1,100000)
    record.measurerName = random.choice(people)
    record.download.extend([random.random() for i in range(C.MEASUREMENT_ARRAY_SIZE)])
    record.upload.extend([random.random() for i in range(C.MEASUREMENT_ARRAY_SIZE)])
    record.ping.extend([random.random() for i in range(C.MEASUREMENT_ARRAY_SIZE)])
    record.timestamp = int(datetime.datetime.now().timestamp())
    reqm.measurement_records.extend([record] * C.NUM_MEASUREMENT_RECORDS)
    return reqm

async def run_single_client(req_count: int, address: str, port: int):
    reader, writer = await asyncio.open_connection(address, port)
    for req in range(req_count):
        message = get_random_message()
        serialized_message = message.SerializeToString()
        writer.write(str(len(serialized_message)).encode() + C.END_OF_MESSAGE)
        await writer.drain()
        writer.write(serialized_message)
        await writer.drain()
        print("Wrote message {} to server".format(req))

        length_data: bytes = await reader.readuntil(separator=C.END_OF_MESSAGE)
        message_size = int(length_data[:-1].decode())
        message_data: bytes = await reader.readexactly(message_size)
        received_message = ResponseMessage()
        received_message.ParseFromString(message_data)
        print("Received {} calculated records".format(len(received_message.measurement_averages)))
    print('Closing the connection..')
    writer.close()
    await writer.wait_closed()

async def test_client_heavy_traffic(clients: int, req_count_per_client: int, address: str, port: int):
    x = await asyncio.gather(
        *(run_single_client(req_count_per_client, address, port)
                               for cl in range(clients))
    )

if __name__ == '__main__':
    asyncio.run(test_client_heavy_traffic(C.CLIENTS, C.REQUEST_COUNT_PER_CLIENT, C.ADDRESS, C.PORT))