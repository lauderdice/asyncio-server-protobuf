from typing import Tuple

import numpy as np

from measurement_pb2 import RequestMessage, ResponseMessage, MeasurementRecord, MeasurementAverage


class DataProcessor():
    def calculate_averages(self,message: RequestMessage) -> Tuple[ResponseMessage,int]:
        calculated_averages = [self._get_maverage_from_mrecord(x) for x in message.measurement_records]
        resp = ResponseMessage()
        resp.measurement_averages.extend(calculated_averages)
        return resp, len(message.measurement_records)

    def _get_maverage_from_mrecord(self, mrecord: MeasurementRecord) -> MeasurementAverage:
        avg_rec = MeasurementAverage()
        avg_rec.id = mrecord.id
        avg_rec.measurerName = mrecord.measurerName
        avg_rec.download = float(np.mean(mrecord.download))
        avg_rec.upload = float(np.mean(mrecord.upload))
        avg_rec.ping = float(np.mean(mrecord.ping))
        avg_rec.timestamp = mrecord.timestamp
        return avg_rec