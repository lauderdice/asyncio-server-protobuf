import json
import avro.schema
REQ_SCHEMA = avro.schema.parse(json.dumps({
  "type": "record",
  "namespace": "cz.esw.serialization.client.avro",
  "name": "RequestMessage",
  "fields": [
    {
      "name": "records",
      "type": {
        "type": "array",
        "items": {
          "type": "record",
          "name": "MeasurementRecord",
          "fields": [
            {
              "name": "id",
              "type": "int"
            },
            {
              "name": "measureName",
              "type": "string"
            },
            {
              "name": "timestamp",
              "type": "long"
            },
            {
              "name": "download",
              "type": {
                "type": "array",
                "items": "double",
                "default": []
              }
            },
            {
              "name": "upload",
              "type": {
                "type": "array",
                "items": "double",
                "default": []
              }
            },
            {
              "name": "ping",
              "type": {
                "type": "array",
                "items": "double",
                "default": []
              }
            }
          ]
        }
      }
    }
  ]
}))
RESP_SCHEMA = avro.schema.parse(json.dumps({
  "type": "record",
  "namespace": "cz.esw.serialization.client.avro",
  "name": "ResponseMessage",
  "fields": [
    {
      "name": "records",
      "type": {
        "type": "array",
        "items": {
          "type": "record",
          "name": "MeasurementAverage",
          "fields": [
            {
              "name": "id",
              "type": "int"
            },
            {
              "name": "measureName",
              "type": "string"
            },
            {
              "name": "timestamp",
              "type": "long"
            },
            {
              "name": "download",
              "type": "double"
            },
            {
              "name": "upload",
              "type": "double"
            },
            {
              "name": "ping",
              "type": "double"
            }
          ]
        }
      }
    }
  ]
}))