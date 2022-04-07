import constants as C
import click
import asyncio
from asyncio import StreamReader, StreamWriter, IncompleteReadError

from data_processor import DataProcessor
from enums import DataTransferFormat
from measurement_pb2 import RequestMessage


class Server():

    def __init__(self, address: str, port: int, format: DataTransferFormat):
        self._address = address
        self._port = port
        self._format = format

    def run(self):
        try:
            asyncio.run(self._run_server())
        except KeyboardInterrupt:
            print("Stopping the server..")

    async def handle_proto_data(self, reader: StreamReader, writer: StreamWriter):
        data_processor = DataProcessor()
        while True:
            try:
                length_data: bytes = await reader.readuntil(separator=C.END_OF_MESSAGE)
                message_size = int(length_data[:-1].decode())
                message_data: bytes = await reader.readexactly(message_size)
                received_message = RequestMessage()
                received_message.ParseFromString(message_data)

                response_message, number_of_records = data_processor.calculate_averages(received_message)
                serialized_response = response_message.SerializeToString()
                await self.send_response(serialized_response, writer)
                print("Calculated averages for {} measurement records".format(number_of_records))

            except IncompleteReadError:
                print("EOF detected. Exiting..")
                break


    async def _handle_connection(self, reader: StreamReader, writer: StreamWriter):
        if self._format == DataTransferFormat.Protobuf:
            await self.handle_proto_data(reader, writer)
        elif self._format == DataTransferFormat.JSON:
            print("Not implemented")
        elif self._format == DataTransferFormat.Avro:
            print("Not implemented")

        print("Closing the connection..")
        writer.close()

    async def _run_server(self):
        server = await asyncio.start_server(
            self._handle_connection, self._address, self._port)
        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        print("Serving on {}".format(addrs))
        async with server:
            await server.serve_forever()


    async def send_response(self, serialized_response: bytes, writer: StreamWriter):
        writer.write(str(len(serialized_response)).encode() + C.END_OF_MESSAGE)
        await writer.drain()
        writer.write(serialized_response)
        await writer.drain()


@click.command()
@click.option('--dataformat', default=DataTransferFormat.Protobuf.value, help='json, proto, avro', prompt='Data transfer format can be 3 types: json, proto, avro')
@click.option('--port', default=C.PORT, prompt='Port to run the server on')
@click.option('--address', default=C.ADDRESS,prompt='Address to run the server on')
def main(address: str, port: int, dataformat: str):
    dformat = None
    try:
        dformat = DataTransferFormat(dataformat)
    except ValueError:
        exit("Unknown data format")
    s = Server(address, port, DataTransferFormat(dformat))
    s.run()


if __name__ == '__main__':
    main()



