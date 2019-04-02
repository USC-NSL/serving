#!/usr/bin/env python2.7
from __future__ import print_function

import grpc
import time
import numpy as np
from concurrent import futures

import tensorflow as tf
tf.logging.set_verbosity(tf.logging.ERROR)

import sys
sys.path.append('/home/yitao/Documents/fun-project/tensorflow-related/Caesar-Edge/')
from modules_actdet.data_reader import DataReader

from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import olympian_master_pb2_grpc
from tensorflow_serving.apis import olympian_worker_pb2_grpc
from tensorflow_serving.apis import olympian_client_pb2_grpc

from tensorflow.python.framework import tensor_util

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
MAX_MESSAGE_LENGTH = 1024 * 1024 * 64
MAX_WORKERS = 600

tf.app.flags.DEFINE_string('client', 'localhost:50201', 'Olympian client host:port')
tf.app.flags.DEFINE_string('chain_name', 'chain_mobilenet', 'name of the chain')
FLAGS = tf.app.flags.FLAGS

route_table = ""

if (FLAGS.chain_name == "chain_actdet"):
  actdet_reader = DataReader()
  actdet_reader.Setup("/home/yitao/Documents/fun-project/tensorflow-related/Caesar-Edge/indoor_two_ppl.avi")

class OlympianClient(olympian_client_pb2_grpc.OlympianClientServicer):

  def load_labels(self):
    label_file = ("/home/yitao/Documents/fun-project/tensorflow-related/tensorflow-for-poets-2/tf_files/retrained_labels.txt")
    label = []
    proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
    for l in proto_as_ascii_lines:
      label.append(l.rstrip())
    return label

  def Predict(self, request, context):
    if ("update_route_table" in request.inputs):
      print("[%s][Client] Received retrospect message from Master" % (str(time.time())))
      global route_table
      previous_route_table = route_table
      route_table = tensor_util.MakeNdarray(request.inputs["update_route_table"])
      print("[%s][Client] Changed route table from %s to %s" % (str(time.time()), previous_route_table, route_table))

    elif ("FINAL" in request.inputs):
      final_result_value = tensor_util.MakeNdarray(request.inputs["FINAL"])
      frame_info = tensor_util.MakeNdarray(request.inputs["frame_info"])
      print("[%s][Client] Received final result w/ frame_info = %s" % (str(time.time()), frame_info))

      # Mobilenet specific
      if (request.model_spec.name == "chain_mobilenet"):
        labels = self.load_labels()
        results = np.squeeze(final_result_value)
        top_k = results.argsort()[-5:][::-1]
        for i in top_k:
          print("    ", labels[i], results[i])
      elif (request.model_spec.name == "chain_nlp_speech"):
        tt = str(final_result_value).decode('utf-8')
        print(tt)
      elif (request.model_spec.name == "chain_nlp_transform"):
        tt = str(final_result_value).decode('utf-8')
        print(tt)
      elif (request.model_spec.name == "chain_actdet"):
        output = final_result_value
        print(output)
      else:
        print("Not implemented yet...")

    else:
      print("[%s][Client] Something is wrong..." % (str(time.time())))

    # default dumb OK message...
    dumbresult = predict_pb2.PredictResponse()
    dumbresult.outputs["message"].CopyFrom(tf.make_tensor_proto("OK"))
    return dumbresult

def getFirstStub(route_table):
  tmp = route_table.split("-")[0].split(":")
  first_stub = "%s:%s" % (tmp[1], tmp[2])
  return first_stub

def getClientInput(chain_name):
  if (chain_name == "chain_mobilenet"):
    return "/home/yitao/Documents/fun-project/tensorflow-related/tensorflow-for-poets-2/tf_files/flower_photos/daisy/21652746_cc379e0eea_m.jpg"
  elif (chain_name == "chain_nlp_speech"):
    return "It's well-known that Kobe Bryant is the best basketball player in the world."
  elif (chain_name == "chain_nlp_transform"):
    return "It's well-known that Kobe Bryant is the best basketball player in the world."
  elif (chain_name == "chain_actdet"):
    global actdet_reader
    frame_data = actdet_reader.PostProcess()
    return frame_data['img']
  else:
    return "Error..."

def main(_):
  global route_table

  # start client's sstub
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS), options=[('grpc.max_send_message_length', MAX_MESSAGE_LENGTH), 
                                                                    ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
                                                                    ('grpc.max_message_length', MAX_MESSAGE_LENGTH)])
  olympian_client_pb2_grpc.add_OlympianClientServicer_to_server(OlympianClient(), server)
  server.add_insecure_port(FLAGS.client)
  server.start()

  print("[%s][Client] client's sstub started..." % (str(time.time())))

  # setup client's cstubs
  cstubs = dict()

  # worker_list = ["localhost:50101", "localhost:50102"]
  worker_list = ["localhost:50101"]
  for w in worker_list:
    channel = grpc.insecure_channel(w)
    stub = olympian_worker_pb2_grpc.OlympianWorkerStub(channel)
    cstubs[w] = stub

  master_list = ["localhost:50051"]
  for m in master_list:
    channel = grpc.insecure_channel(m)
    stub = olympian_master_pb2_grpc.OlympianMasterStub(channel)
    cstubs[m] = stub

  # client sends request for sess id and route table
  sess_setup_request = predict_pb2.PredictRequest()
  sess_setup_request.model_spec.name = FLAGS.chain_name
  sess_setup_request.model_spec.signature_name = "chain_specification"
  sess_setup_request.inputs["sess_setup"].CopyFrom(
    tf.make_tensor_proto(FLAGS.client))
  sess_setup_request.inputs["sess_requirement"].CopyFrom(
    tf.make_tensor_proto("None"))

  print("[%s][Client] Ready to send sess_setup_request for %s!" % (str(time.time()), FLAGS.chain_name))
  sess_setup_result = cstubs[master_list[0]].Predict(sess_setup_request, 10.0)

  sess_id = str(tensor_util.MakeNdarray(sess_setup_result.outputs["sess_id"]))
  route_table = str(tensor_util.MakeNdarray(sess_setup_result.outputs["route_table"]))

  first_stub = getFirstStub(route_table)
  print("[%s][Client] Received sess_id = %s" % (str(time.time()), sess_id))
  print("                                 first_stub = %s\n" % (first_stub))

  # the duration that this client will keep sending requests
  sess_duration = 10 #sec
  
  t_end = time.time() + sess_duration
  frame_id = -1

  # while time.time() < t_end:
  while frame_id < 48:
    frame_id += 1
    client_input = getClientInput(FLAGS.chain_name)
    frame_info = "%s-%s" % (sess_id, frame_id)

    # print("client_input.dtype = %s" % str(client_input.dtype))

    request = predict_pb2.PredictRequest()
    request.model_spec.name = FLAGS.chain_name
    request.model_spec.signature_name = "chain_specification"
    request.inputs["client_input"].CopyFrom(
      tf.make_tensor_proto(client_input, dtype = client_input.dtype, shape = client_input.shape))
    request.inputs["frame_info"].CopyFrom(
      tf.make_tensor_proto(frame_info))
    request.inputs["route_table"].CopyFrom(
      tf.make_tensor_proto(route_table))
    request.inputs["route_index"].CopyFrom(
      tf.make_tensor_proto(0, dtype=tf.int32))

    print("[%s][Client] Ready to send client's %dth input!" % (str(time.time()), frame_id))

    # async way
    result_future = cstubs[first_stub].Predict.future(request, 10.0)
    time.sleep(1) # mimic input fps of 1

  try:
    while True:
      time.sleep(_ONE_DAY_IN_SECONDS)
  except KeyboardInterrupt:
    server.stop(0)

if __name__ == '__main__':
  tf.app.run()