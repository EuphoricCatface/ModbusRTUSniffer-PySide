#  -- from pymodbus/factory.py --  #
from pymodbus.pdu import bit_read_message as bit_r_msg
from pymodbus.pdu import bit_write_message as bit_w_msg
# from pymodbus.pdu import diag_message as diag_msg
# from pymodbus.pdu import file_message as file_msg
# from pymodbus.pdu import mei_message as mei_msg
# from pymodbus.pdu import other_message as o_msg
# from pymodbus.pdu import pdu
from pymodbus.pdu import register_read_message as reg_r_msg
from pymodbus.pdu import register_write_message as reg_w_msg

function_table_rw = [
    reg_r_msg.ReadHoldingRegistersRequest,
    bit_r_msg.ReadDiscreteInputsRequest,
    reg_r_msg.ReadInputRegistersRequest,
    bit_r_msg.ReadCoilsRequest,
    bit_w_msg.WriteMultipleCoilsRequest,
    reg_w_msg.WriteMultipleRegistersRequest,
    reg_w_msg.WriteSingleRegisterRequest,
    bit_w_msg.WriteSingleCoilRequest,
    # reg_r_msg.ReadWriteMultipleRegistersRequest,
    # diag_msg.DiagnosticStatusRequest,
    # o_msg.ReadExceptionStatusRequest,
    # o_msg.GetCommEventCounterRequest,
    # o_msg.GetCommEventLogRequest,
    # o_msg.ReportSlaveIdRequest,
    # file_msg.ReadFileRecordRequest,
    # file_msg.WriteFileRecordRequest,
    # reg_w_msg.MaskWriteRegisterRequest,
    # file_msg.ReadFifoQueueRequest,
    # mei_msg.ReadDeviceInformationRequest,
    # ---- #
    reg_r_msg.ReadHoldingRegistersResponse,
    bit_r_msg.ReadDiscreteInputsResponse,
    reg_r_msg.ReadInputRegistersResponse,
    bit_r_msg.ReadCoilsResponse,
    bit_w_msg.WriteMultipleCoilsResponse,
    reg_w_msg.WriteMultipleRegistersResponse,
    reg_w_msg.WriteSingleRegisterResponse,
    bit_w_msg.WriteSingleCoilResponse,
    # reg_r_msg.ReadWriteMultipleRegistersResponse,
    # diag_msg.DiagnosticStatusResponse,
    # o_msg.ReadExceptionStatusResponse,
    # o_msg.GetCommEventCounterResponse,
    # o_msg.GetCommEventLogResponse,
    # o_msg.ReportSlaveIdResponse,
    # file_msg.ReadFileRecordResponse,
    # file_msg.WriteFileRecordResponse,
    # reg_w_msg.MaskWriteRegisterResponse,
    # file_msg.ReadFifoQueueResponse,
    # mei_msg.ReadDeviceInformationResponse,
]