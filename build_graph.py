import sys
import scipy.io
import random
from snap import *
from numpy.random import geometric

def get_coo_from_mat_v1(mat_file):
  mat = scipy.io.loadmat(mat_file)
  return mat['Problem'][0][0][2].tocoo()

def get_directed_graph_from_coo(coo):
  G = TNGraph.New()
  for node_id in range(coo.shape[0]):
    G.AddNode(node_id)
  for edges_id in range(len(coo.row)):
    G.AddEdge(int(coo.row[edges_id]), int(coo.col[edges_id])) 
  return G

def get_undirected_graph_from_coo(coo):
  pass

def get_undirected_graph_from_dblp_v1(dblp_file):
  G = TUNGraph.New()
  raw_data = open(dblp_file).read().split('\n')[0:-1]
  for i in range(4, len(raw_data)):
    temp = raw_data[i].split('\t')
    src_id = int(temp[0])
    dst_id = int(temp[1])
    if not G.IsNode(src_id):
      G.AddNode(src_id)
    if not G.IsNode(dst_id):
      G.AddNode(dst_id)
    G.AddEdge(src_id, dst_id)
  return G

def get_directed_graph_from_p2p_v1(p2p_file):
  G = TNGraph.New()
  raw_data = open(p2p_file).read().split('\r\n')[0:-1]
  for i in range(4, len(raw_data)):
    temp = raw_data[i].split('\t')
    src_id = int(temp[0])
    dst_id = int(temp[1])
    if not G.IsNode(src_id):
      G.AddNode(src_id)
    if not G.IsNode(dst_id):
      G.AddNode(dst_id)
    G.AddEdge(src_id, dst_id)
  return G

##################################
# undirected

def random_node_sample_graph_from_undirected(G, density):
  new_G = TUNGraph.New()
  for node_id in range(G.GetNodes()):
    if random.random() < density:
      new_G.AddNode(node_id)
  
  for edges in G.Edges():
    src_id = edges.GetSrcNId()
    dst_id = edges.GetDstNId()
    if new_G.IsNode(src_id) and new_G.IsNode(dst_id):
      new_G.AddEdge(src_id, dst_id)
  
  return new_G

def random_edge_sample_graph_from_undirected(G, density):
  new_G = TUNGraph.New()
  for edges in G.Edges():
    if random.random() < density:
      src_id = edges.GetSrcNId()
      dst_id = edges.GetDstNId()
      if not new_G.IsNode(src_id):
        new_G.AddNode(src_id)
      if not new_G.IsNode(dst_id):
        new_G.AddNode(dst_id)
      new_G.AddEdge(src_id, dst_id)

  return new_G

def random_walking_sample_graph_from_undirected(G, density, prob_jump_to_start = 0.15, max_iter_without_found = 100):
  start_id_list = []

  new_G = TUNGraph.New()
  num_nodes_new_G = 0
  
  num_nodes_G = G.GetNodes()
  while num_nodes_new_G < num_nodes_G * density:
    
    # find the start point id
    found = False
    while not found:
      start_id = G.GetRndNId()
      if not start_id in start_id_list:
        found = True
    
    # add new point to list
    start_id_list.append(start_id)

    # if not new_G.IsNode(start_id):
    if not new_G.IsNode(start_id):
      new_G.AddNode(start_id)
      num_nodes_new_G = num_nodes_new_G + 1
    
    current_id = start_id
    times_iter_without_found = 0
    while num_nodes_new_G < num_nodes_G * density:
      found = False

      if random.random() < prob_jump_to_start:
        current_id = start_id
      
      num_out_edges = sum(1 for x in G.GetNI(current_id).GetOutEdges())
      num_iterated_edges = 0

      last_id = current_id
      for out_edge_id in G.GetNI(current_id).GetOutEdges():
        if random.random() * (num_out_edges - num_iterated_edges) < 1:
          current_id = out_edge_id
          break;
        num_iterated_edges = num_iterated_edges + 1

      if not new_G.IsNode(current_id):
        new_G.AddNode(current_id)
        num_nodes_new_G = num_nodes_new_G + 1
        found = True

      if not new_G.IsEdge(last_id, current_id):
        new_G.AddEdge(last_id, current_id)
        found = True

      if found:
        times_iter_without_found = 0
      else:
        times_iter_without_found = times_iter_without_found + 1
        if times_iter_without_found >= max_iter_without_found:
          break

  return new_G

def forest_fire_sample_graph_from_undirected(G, density, p = 0.2):
  id_list_buffer = []

  new_G = TUNGraph.New()
  num_nodes_G = G.GetNodes()

  head = 0
  tail = 0

  while tail < num_nodes_G * density:

    # find the start point id
    found = False
    while not found:
      start_id = G.GetRndNId()
      if not start_id in id_list_buffer:
        found = True

    id_list_buffer.append(start_id)
    tail = tail + 1

    new_G.AddNode(start_id)

    while head<tail:
      current_id = id_list_buffer[head]
      x = geometric(p=p, size=1)

      num_out_edges = sum(1 for x in G.GetNI(current_id).GetOutEdges())

      old_tail = tail
      num_iterated_edges = 0
      selected = 0
      for out_edge_id in G.GetNI(current_id).GetOutEdges():
        num_iterated_edges = num_iterated_edges + 1
        if out_edge_id in id_list_buffer:
          continue;
        if random.random() * (num_out_edges + 1 - num_iterated_edges) < (x - selected):
          selected = selected + 1
          id_list_buffer.append(out_edge_id)
          tail = tail + 1

      for new_id_pos in range(old_tail, tail):
        new_G.AddNode(id_list_buffer[new_id_pos])
        new_G.AddEdge(current_id, id_list_buffer[new_id_pos])

      head = head + 1

      if tail > num_nodes_G * density:
        break;

  return new_G

#################################
# directed

def random_node_sample_graph_from_directed(G, density):
  new_G = TNGraph.New()
  for node_id in range(G.GetNodes()):
    if random.random() < density:
      new_G.AddNode(node_id)
  
  for edges in G.Edges():
    src_id = edges.GetSrcNId()
    dst_id = edges.GetDstNId()
    if new_G.IsNode(src_id) and new_G.IsNode(dst_id):
      new_G.AddEdge(src_id, dst_id)
  
  return new_G

def random_edge_sample_graph_from_directed(G, density):
  new_G = TNGraph.New()
  for edges in G.Edges():
    if random.random() < density:
      src_id = edges.GetSrcNId()
      dst_id = edges.GetDstNId()
      if not new_G.IsNode(src_id):
        new_G.AddNode(src_id)
      if not new_G.IsNode(dst_id):
        new_G.AddNode(dst_id)
      new_G.AddEdge(src_id, dst_id)

  return new_G

def random_walking_sample_graph_from_directed(G, density, prob_jump_to_start = 0.15, max_iter_without_found = 100):
  start_id_list = []

  new_G = TNGraph.New()
  num_nodes_new_G = 0
  
  num_nodes_G = G.GetNodes()
  while num_nodes_new_G < num_nodes_G * density:
    
    # find the start point id
    found = False
    while not found:
      start_id = G.GetRndNId()
      if not start_id in start_id_list:
        found = True
    
    # add new point to list
    start_id_list.append(start_id)

    # if not new_G.IsNode(start_id):
    if not new_G.IsNode(start_id):
      new_G.AddNode(start_id)
      num_nodes_new_G = num_nodes_new_G + 1
    
    current_id = start_id
    times_iter_without_found = 0
    while num_nodes_new_G < num_nodes_G * density:
      found = False

      if random.random() < prob_jump_to_start:
        current_id = start_id
      
      num_out_edges = sum(1 for x in G.GetNI(current_id).GetOutEdges())
      num_iterated_edges = 0

      last_id = current_id
      for out_edge_id in G.GetNI(current_id).GetOutEdges():
        if random.random() * (num_out_edges - num_iterated_edges) < 1:
          current_id = out_edge_id
          break;
        num_iterated_edges = num_iterated_edges + 1

      if not new_G.IsNode(current_id):
        new_G.AddNode(current_id)
        num_nodes_new_G = num_nodes_new_G + 1
        found = True

      if not new_G.IsEdge(last_id, current_id):
        new_G.AddEdge(last_id, current_id)
        found = True

      if found:
        times_iter_without_found = 0
      else:
        times_iter_without_found = times_iter_without_found + 1
        if times_iter_without_found >= max_iter_without_found:
          break

  return new_G

def forest_fire_sample_graph_from_directed(G, density, p = 0.2, r = 0.4):
  id_list_buffer = []

  new_G = TNGraph.New()
  num_nodes_G = G.GetNodes()

  head = 0
  tail = 0

  while tail < num_nodes_G * density:

    # find the start point id
    found = False
    while not found:
      start_id = G.GetRndNId()
      if not start_id in id_list_buffer:
        found = True

    id_list_buffer.append(start_id)
    tail = tail + 1

    new_G.AddNode(start_id)

    while head<tail:
      current_id = id_list_buffer[head]
      x = geometric(p=p, size=1)
      y = geometric(p=r*p, size=1)

      num_out_edges = sum(1 for x in G.GetNI(current_id).GetOutEdges())
      num_in_edges = sum(1 for x in G.GetNI(current_id).GetInEdges())

      old_tail = tail
      num_iterated_edges = 0
      selected = 0
      for out_edge_id in G.GetNI(current_id).GetOutEdges():
        num_iterated_edges = num_iterated_edges + 1
        if out_edge_id in id_list_buffer:
          continue;
        if random.random() * (num_out_edges + 1 - num_iterated_edges) < (x - selected):
          selected = selected + 1
          id_list_buffer.append(out_edge_id)
          tail = tail + 1

      for new_id_pos in range(old_tail, tail):
        new_G.AddNode(id_list_buffer[new_id_pos])
        new_G.AddEdge(current_id, id_list_buffer[new_id_pos])

      old_tail = tail
      num_iterated_edges = 0
      selected = 0
      for in_edge_id in G.GetNI(current_id).GetInEdges():
        num_iterated_edges = num_iterated_edges + 1
        if in_edge_id in id_list_buffer:
          continue;
        if random.random() * (num_in_edges + 1 - num_iterated_edges) < (y - selected):
          selected = selected + 1
          id_list_buffer.append(in_edge_id)
          tail = tail + 1

      for new_id_pos in range(old_tail, tail):
        new_G.AddNode(id_list_buffer[new_id_pos])
        new_G.AddEdge(id_list_buffer[new_id_pos], current_id)

      head = head + 1

      if tail > num_nodes_G * density:
        break;

  return new_G

############################################
# original

def get_full_graph_from_coo(coo):
  G = TNGraph.New()
  for node_id in range(coo.shape[0]):
    G.AddNode(node_id)
  for edges_id in range(len(coo.row)):
    G.AddEdge(int(coo.row[edges_id]), int(coo.col[edges_id])) 
  return G

def random_node_sample_graph_from_full(G, density):
  new_G = TNGraph.New()
  for node_id in range(G.GetNodes()):
    if random.random() < density:
      new_G.AddNode(node_id)
  
  for edges in G.Edges():
    src_id = edges.GetSrcNId()
    dst_id = edges.GetDstNId()
    if new_G.IsNode(src_id) and new_G.IsNode(dst_id):
      new_G.AddEdge(src_id, dst_id)
  
  return new_G

def random_edge_sample_graph_from_full(G, density):
  new_G = TNGraph.New()
  for edges in G.Edges():
    if random.random() < density:
      src_id = edges.GetSrcNId()
      dst_id = edges.GetDstNId()
      if not new_G.IsNode(src_id):
        new_G.AddNode(src_id)
      if not new_G.IsNode(dst_id):
        new_G.AddNode(dst_id)
      new_G.AddEdge(src_id, dst_id)

  return new_G

def random_walking_sample_graph_from_full(G, density, prob_jump_to_start = 0.15, max_iter_without_found = 100):
  start_id_list = []

  new_G = TNGraph.New()
  num_nodes_new_G = 0
  
  num_nodes_G = G.GetNodes()
  while num_nodes_new_G < num_nodes_G * density:
    
    # find the start point id
    found = False
    while not found:
      start_id = G.GetRndNId()
      if not start_id in start_id_list:
        found = True
    
    # add new point to list
    start_id_list.append(start_id)

    # if not new_G.IsNode(start_id):
    if not new_G.IsNode(start_id):
      new_G.AddNode(start_id)
      num_nodes_new_G = num_nodes_new_G + 1
    
    current_id = start_id
    times_iter_without_found = 0
    while num_nodes_new_G < num_nodes_G * density:
      found = False

      if random.random() < prob_jump_to_start:
        current_id = start_id
      
      num_out_edges = sum(1 for x in G.GetNI(current_id).GetOutEdges())
      num_iterated_edges = 0

      last_id = current_id
      for out_edge_id in G.GetNI(current_id).GetOutEdges():
        if random.random() * (num_out_edges - num_iterated_edges) < 1:
          current_id = out_edge_id
          break;
        num_iterated_edges = num_iterated_edges + 1

      if not new_G.IsNode(current_id):
        new_G.AddNode(current_id)
        num_nodes_new_G = num_nodes_new_G + 1
        found = True

      if not new_G.IsEdge(last_id, current_id):
        new_G.AddEdge(last_id, current_id)
        found = True

      if found:
        times_iter_without_found = 0
      else:
        times_iter_without_found = times_iter_without_found + 1
        if times_iter_without_found >= max_iter_without_found:
          break

  return new_G

def forest_fire_sample_graph_from_full(G, density, p = 0.2, r = 0.4):
  id_list_buffer = []

  new_G = TNGraph.New()
  num_nodes_G = G.GetNodes()

  head = 0
  tail = 0

  while tail < num_nodes_G * density:

    # find the start point id
    found = False
    while not found:
      start_id = G.GetRndNId()
      if not start_id in id_list_buffer:
        found = True

    id_list_buffer.append(start_id)
    tail = tail + 1

    new_G.AddNode(start_id)

    while head<tail:
      current_id = id_list_buffer[head]
      x = geometric(p=p, size=1)
      y = geometric(p=r*p, size=1)

      num_out_edges = sum(1 for x in G.GetNI(current_id).GetOutEdges())
      num_in_edges = sum(1 for x in G.GetNI(current_id).GetInEdges())

      old_tail = tail
      num_iterated_edges = 0
      selected = 0
      for out_edge_id in G.GetNI(current_id).GetOutEdges():
        num_iterated_edges = num_iterated_edges + 1
        if out_edge_id in id_list_buffer:
          continue;
        if random.random() * (num_out_edges + 1 - num_iterated_edges) < (x - selected):
          selected = selected + 1
          id_list_buffer.append(out_edge_id)
          tail = tail + 1

      for new_id_pos in range(old_tail, tail):
        new_G.AddNode(id_list_buffer[new_id_pos])
        new_G.AddEdge(current_id, id_list_buffer[new_id_pos])

      old_tail = tail
      num_iterated_edges = 0
      selected = 0
      for in_edge_id in G.GetNI(current_id).GetInEdges():
        num_iterated_edges = num_iterated_edges + 1
        if in_edge_id in id_list_buffer:
          continue;
        if random.random() * (num_in_edges + 1 - num_iterated_edges) < (y - selected):
          selected = selected + 1
          id_list_buffer.append(in_edge_id)
          tail = tail + 1

      for new_id_pos in range(old_tail, tail):
        new_G.AddNode(id_list_buffer[new_id_pos])
        new_G.AddEdge(id_list_buffer[new_id_pos], current_id)

      head = head + 1

      if tail > num_nodes_G * density:
        break;

  return new_G

def main():
  # coo1 = get_coo_from_mat_v1('source/amazon0505.mat')
  # G1 = get_full_graph_from_coo(coo1)
  # # new_G1 = random_node_sample_graph_from_full(G1, 0.2)
  # # new_G2 = random_edge_sample_graph_from_full(G1, 0.4)
  # # new_G3 = random_walking_sample_graph_from_full(G1, 0.1, 0.15)
  # new_G4 = forest_fire_sample_graph_from_full(G1, 0.1)
  # G = new_G4
  # print G.GetNodes()
  # print G.GetEdges()
  # G = get_directed_graph_from_p2p_v1("source/p2p08/p2p-Gnutella08/p2p-Gnutella08.txt")
  # G = get_directed_graph_from_p2p_v1("source/p2p31/p2p-Gnutella31/p2p-Gnutella31.txt")
  G = get_undirected_graph_from_dblp_v1("source/com-DBLP/com-dblp.ungraph/com-dblp.ungraph.txt")
  G1 = random_node_sample_graph_from_undirected(G, 0.2)
  G2 = random_edge_sample_graph_from_undirected(G, 0.2)
  G3 = random_walking_sample_graph_from_undirected(G, 0.2)
  G4 = forest_fire_sample_graph_from_undirected(G, 0.2)
  print G.GetNodes()
  print G.GetEdges()
  print G1.GetNodes()
  print G1.GetEdges()
  print G2.GetNodes()
  print G2.GetEdges()
  print G3.GetNodes()
  print G3.GetEdges()
  print G4.GetNodes()
  print G4.GetEdges()

if __name__ == '__main__':
  sys.exit(int(main() or 0))
