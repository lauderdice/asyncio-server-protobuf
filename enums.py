import enum


class PersonName(enum.Enum):
    kristyna = 0
    jirka = 1
    petr = 2
    jana = 3


class DataTransferFormat(enum.Enum):
    JSON = "json"
    Protobuf = "proto"
    Avro = "avro"