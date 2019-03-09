# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tensorflow_serving/apis/olympian_master.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from tensorflow.core.framework import tensor_pb2 as tensorflow_dot_core_dot_framework_dot_tensor__pb2
from tensorflow_serving.apis import model_pb2 as tensorflow__serving_dot_apis_dot_model__pb2
from tensorflow_serving.apis import predict_pb2 as tensorflow__serving_dot_apis_dot_predict__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='tensorflow_serving/apis/olympian_master.proto',
  package='tensorflow.serving',
  syntax='proto3',
  serialized_pb=_b('\n-tensorflow_serving/apis/olympian_master.proto\x12\x12tensorflow.serving\x1a&tensorflow/core/framework/tensor.proto\x1a#tensorflow_serving/apis/model.proto\x1a%tensorflow_serving/apis/predict.proto2d\n\x0eOlympianMaster\x12R\n\x07Predict\x12\".tensorflow.serving.PredictRequest\x1a#.tensorflow.serving.PredictResponseB\x03\xf8\x01\x01\x62\x06proto3')
  ,
  dependencies=[tensorflow_dot_core_dot_framework_dot_tensor__pb2.DESCRIPTOR,tensorflow__serving_dot_apis_dot_model__pb2.DESCRIPTOR,tensorflow__serving_dot_apis_dot_predict__pb2.DESCRIPTOR,])



_sym_db.RegisterFileDescriptor(DESCRIPTOR)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\370\001\001'))

_OLYMPIANMASTER = _descriptor.ServiceDescriptor(
  name='OlympianMaster',
  full_name='tensorflow.serving.OlympianMaster',
  file=DESCRIPTOR,
  index=0,
  options=None,
  serialized_start=185,
  serialized_end=285,
  methods=[
  _descriptor.MethodDescriptor(
    name='Predict',
    full_name='tensorflow.serving.OlympianMaster.Predict',
    index=0,
    containing_service=None,
    input_type=tensorflow__serving_dot_apis_dot_predict__pb2._PREDICTREQUEST,
    output_type=tensorflow__serving_dot_apis_dot_predict__pb2._PREDICTRESPONSE,
    options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_OLYMPIANMASTER)

DESCRIPTOR.services_by_name['OlympianMaster'] = _OLYMPIANMASTER

# @@protoc_insertion_point(module_scope)
