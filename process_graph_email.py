import sys
import json
from datetime import *
from time import *
from build_graph import *
from snap import *
import collections
# import warnings

# with warnings.catch_warnings():
#   warnings.filterwarnings("ignore", category = DeprecationWarning)

def node_degree_distribution(G):
  num_nodes_G = G.GetNodes()

  degrees = []
  max_degree = 0
  for node in G.Nodes():
    degrees.append(node.GetInDeg() + node.GetOutDeg())
    if degrees[-1]>max_degree:
      max_degree=degrees[-1]
  degrees_counter = collections.Counter(degrees)
  degrees_frequency = [None]*(max_degree+1)
  for i in range(max_degree+1):
    degrees_frequency[i] = float(degrees_counter[i])/num_nodes_G

  cumulative_frequency = degrees_frequency
  for i in range(len(cumulative_frequency)-1):
    cumulative_frequency[i+1] = cumulative_frequency[i+1] + cumulative_frequency[i]

  return cumulative_frequency

def clustering_coefficient_distribution(G, num_segments):
  coefficient = []
  for node in G.Nodes():
    nodes = TIntV()
    for out_node_id in node.GetOutEdges():
      nodes.Add(out_node_id)
    for in_node_id in node.GetInEdges():
      if not in_node_id in nodes:
        nodes.Add(in_node_id)
    subgraph = GetSubGraph(G, nodes)
    d_v = len(nodes)
    if d_v <= 1:
      coefficient.append(0)
    else:
      coefficient.append(float(subgraph.GetNodes())/(d_v)/(d_v-1))
  
  coefficient = sorted(coefficient)
  cumulative_frequency = [None]*(num_segments+1)
  
  pos = 0
  for i in range(num_segments+1):
    while (pos<len(coefficient) and coefficient[pos]<= 1./num_segments * i):
      pos = pos + 1
    cumulative_frequency[i] = pos

  return [float(x)/pos for x in cumulative_frequency]

def generate_sample_collection_file(inputDir, outputDir, dataSet, sampleNumber, methodChoose):
  print 'current time : %s' % str(datetime.now())
  startTime = time()

  if dataSet == 1:
    tempCoo = get_coo_from_mat_v1(inputDir)
    fullGraph = get_full_graph_from_coo(tempCoo)    
  elif dataSet == 2:
    fullGraph = get_undirected_graph_from_dblp_v1(inputDir)
  elif dataSet == 3:
    fullGraph = get_directed_graph_from_Email_v1(inputDir)
  else:
    fullGraph = get_directed_graph_from_p2p_v1(inputDir)



  jsonData1 = []
  jsonData2 = []

  outputDir += str(methodChoose)
  outputDir += '_'

  for i in range(sampleNumber):
    if methodChoose == 1:
      sampleGraph = random_node_sample_graph_from_full(fullGraph, 0.2)
    elif methodChoose == 2:
      sampleGraph = random_edge_sample_graph_from_full(fullGraph, 0.4)
    elif methodChoose == 3:
      sampleGraph = random_walking_sample_graph_from_full(fullGraph, 0.1, 0.5)
    else:
      sampleGraph = forest_fire_sample_graph_from_full(fullGraph, 0.1)

    outputDir1 = outputDir
    outputDir1 += str(i + 1)
    outputDir1 += '_'
    outputDir1 += '1.json'   
    print 'file path & name: %s' % outputDir1   
    outputFile1 = open(outputDir1, 'w')
    # distribution = 1
    sampleList_1 = node_degree_distribution(sampleGraph)
    jsonItem_1 = {'sample' + str(i + 1): sampleList_1}
    jsonData1.append(jsonItem_1)
    json.dump(jsonData1, outputFile1)
    outputFile1.close()

    outputDir2 = outputDir
    outputDir2 += str(i + 1)
    outputDir2 += '_'
    outputDir2 += '2.json'     
    print 'file path & name: %s' % outputDir2
    outputFile2 = open(outputDir2, 'w')    
    # distribution = 2
    sampleList_2 = clustering_coefficient_distribution(sampleGraph, 10)
    jsonItem_2 = {'sample' + str(i + 1): sampleList_2}
    jsonData2.append(jsonItem_2)
    json.dump(jsonData2, outputFile2)
    outputFile2.close()

  # outputDir += str(sampleNumber)
  # outputDir += str(methodChoose)
  # outputDir += str(distribution)
  # outputDir += '.json'
  # outputFile = open(outputDir, 'w') 
  # print 'file path & name: %s' % outputDir
  # # jsonData = [];
  # for i in range(sampleNumber):
  #   if methodChoose == 1:
  #     sampleGraph = random_node_sample_graph_from_full(G1, 0.2)
  #   elif methodChoose == 2:
  #     sampleGraph = random_edge_sample_graph_from_full(G1, 0.4)
  #   elif methodChoose == 3:
  #     sampleGraph = random_walking_sample_graph_from_full(G1, 0.1, 0.5)
  #   else:
  #     sampleGraph = forest_fire_sample_graph_from_full(G1, 0.1)

  #   if distribution == 1:
  #     sampleList = node_degree_distribution(sampleGraph)
  #   else:
  #     sampleList = clustering_coefficient_distribution(sampleGraph, 10)

  #   jsonItem = {'sample' + str(i + 1): sampleList}
  #   jsonData.append(jsonItem)
    
  # json.dump(jsonData, outputFile)
  # outputFile.close()
  
  endTime = time()
  print 'costs: %f seconds' % (endTime - startTime)
  print '\n' 

def main():
  inputTestDir = 'source/Amazon/amazon0302.mat'

  inputDir_amazon = 'source/Amazon/amazon0312.mat'
  inputDir_dblp = 'source/com-DBLP/com-dblp.ungraph/com-dblp.ungraph.txt'
  inputDir_email = 'source/Email/Email-EuAll.txt'
  inputDir_p2p08 = 'source/p2p08/p2p-Gnutella08/p2p-Gnutella08.txt'
  inputDir_p2p31 = 'source/p2p31/p2p-Gnutella31/p2p-Gnutella31.txt'

  outputDir_amazon = 'data/amazon/amazon'
  outputDir_dblp = 'data/dblp/dblp'
  outputDir_email = 'data/email/email'
  outputDir_p2p08 = 'data/p2p08/pp'
  outputDir_p2p31 = 'data/p2p31/pp'
  # sampleNumber = 3
  # methodChoose = 1
  # # distribution = 2
  # generate_sample_collection_file(inputTestDir, outputDir, sampleNumber, methodChoose)

  sampleNumber = 50

  # for i in range(4):
  #   methodChoose = i + 1
  #   generate_sample_collection_file(inputDir_amazon, outputDir_amazon, 1, sampleNumber, methodChoose)

  # for i in range(4):
  #   methodChoose = i + 1
  #   generate_sample_collection_file(inputDir_dblp, outputDir_dblp, 2, sampleNumber, methodChoose)

  for i in range(4):
    methodChoose = i + 1
    generate_sample_collection_file(inputDir_email, outputDir_email, 3, sampleNumber, methodChoose)

  # for i in range(4):
  #   methodChoose = i + 1
  #   generate_sample_collection_file(inputDir_p2p08, outputDir_p2p08, 4, sampleNumber, methodChoose)

  # for i in range(4):
  #   methodChoose = i + 1
  #   generate_sample_collection_file(inputDir_p2p31, outputDir_p2p31, 5, sampleNumber, methodChoose)


  # time consuming
  # deprecated
  # for i in range(3):
  #   if i == 0:
  #     sampleNumber = 10
  #     for j in range(4):
  #       methodChoose = j + 1
  #       for k in range(2):
  #         distribution = k + 1
  #         generate_sample_collection_file(inputDir, outputDir, sampleNumber, methodChoose, distribution)

  #   elif i == 1:
  #     sampleNumber = 20
  #     for j in range(4):
  #       methodChoose = j + 1
  #       for k in range(2):
  #         distribution = k + 1
  #         generate_sample_collection_file(inputDir, outputDir, sampleNumber, methodChoose, distribution)

  #   else:
  #     sampleNumber = 50
  #     for j in range(4):
  #       methodChoose = j + 1
  #       for k in range(2):
  #         distribution = k + 1
  #         generate_sample_collection_file(inputDir, outputDir, sampleNumber, methodChoose, distribution)



  # for i in range(sampleNumber):
  #   if methodChoose == 1:
  #     sampleGraph = random_node_sample_graph_from_full(G1, 0.2)
  #   elif methodChoose == 2:
  #     sampleGraph = random_edge_sample_graph_from_full(G1, 0.4)
  #   elif methodChoose == 3:
  #     sampleGraph = random_walking_sample_graph_from_full(G1, 0.1, 0.5)
  #   else:
  #     sampleGraph = forest_fire_sample_graph_from_full(G1, 0.1)

  #   if distribution == 1:
  #     sampleList = node_degree_distribution(sampleGraph)
  #   else:
  #     sampleList = clustering_coefficient_distribution(sampleGraph, 10)

  #   json.dump(sampleList, outputFile)
  # outputFile.close()
  # new_G1 = random_node_sample_graph_from_full(G1, 0.2)
  # new_G2 = random_edge_sample_graph_from_full(G1, 0.4)
  # new_G3 = random_walking_sample_graph_from_full(G1, 0.1, 0.15)
  # new_G4 = forest_fire_sample_graph_from_full(G1, 0.1)
  # G = new_G1
  # print node_degree_distribution(G)
  # print clustering_coefficient_distribution(G, 10)


if __name__ == '__main__':
  sys.exit(int(main() or 0))
