import io

import avroschema
import avro.io
import constants as C
import click
import asyncio
from asyncio import StreamReader, StreamWriter, IncompleteReadError

from avroschema.avroschema import REQ_SCHEMA, RESP_SCHEMA
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
            except ConnectionResetError:
                print("Client ended the connection. Exiting..")
                break

    async def handle_avro_data(self, reader: StreamReader, writer: StreamWriter):
        data_processor = DataProcessor()
        while True:
            try:
                length_data: bytes = await reader.readuntil(separator=C.END_OF_MESSAGE)
                message_size = int(length_data[:-1].decode())
                message_data: bytes = await reader.readexactly(message_size)

                message_buf = io.BytesIO(message_data)
                reader = avro.io.DatumReader(REQ_SCHEMA)
                decoder = avro.io.BinaryDecoder(message_buf)
                event_dict = reader.read(decoder)
                response_message = data_processor.calculate_averages_avro(event_dict)
                datumwriter = avro.io.DatumWriter(RESP_SCHEMA)
                bytes_writer = io.BytesIO()
                encoder = avro.io.BinaryEncoder(bytes_writer)
                # example_response = {
                #     "records":[{'id': 1569741360, 'measureName': 'jirka', 'timestamp': 1652606880144, 'download': 48029.0, 'upload': 6447.0, 'ping': 515.0}]
                # }
                datumwriter.write(response_message, encoder)
                await self.send_response(bytes_writer.getvalue(), writer)
            except IncompleteReadError:
                print("EOF detected. Exiting..")
                break
            except ConnectionResetError:
                print("Client ended the connection. Exiting..")
                break
    async def _handle_connection(self, reader: StreamReader, writer: StreamWriter):
        if self._format == DataTransferFormat.Protobuf:
            await self.handle_proto_data(reader, writer)
        elif self._format == DataTransferFormat.JSON:
            print("Not implemented")
        elif self._format == DataTransferFormat.Avro:
            await self.handle_avro_data(reader, writer)

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
@click.option('--dataformat', default=DataTransferFormat.Protobuf.value, help='proto', prompt='Data transfer format can be of 1 type: proto')
@click.option('--port', default=C.PORT, prompt='Port to run the server on')
@click.option('--address', default=C.ADDRESS,prompt='Address to run the server on')
def main(address: str, port: int, dataformat: str):
    try:
        dformat = DataTransferFormat(dataformat)
    except ValueError:
        raise NotImplementedError("This format is not yet supported. We chose to implement Protobuf.")
    s = Server(address, port, DataTransferFormat(dformat))
    s.run()


if __name__ == '__main__':
    main()



