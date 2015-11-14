import classifier
import os, os.path
import math
import sys
sys.setrecursionlimit(1000000)

def train():
    path = "./snapshots_training/edges/"
    images = {}
    i = 0;
    for root, dirs, filenames in os.walk(path):
        for f in filenames:
	   if i < 9000:
	       print "loading image", f
               images[f] = classifier.load_image(path+f)
	       i = i+1
    
    for key in images:
	print "parsing image", key
	image_list = images[key]
	edge_array = image_list[0]
	#cutting out the background from the image
	edge_array = edge_array[280:]
	edge_array = edge_array[1:-1]
        #print "total number of edge pixels: ", count_edges_in_array(edge_array)
        for y in range(0, len(edge_array)):
            row = edge_array[y]
            edge_array[y][0] = 0
            edge_array[y][len(row)-1] = 0
        #print "number of edge pixels after removing border: ", count_edges_in_array(edge_array)
	edge_array = noise_reduction_edge_array(edge_array)
	#print "number of edge pixels after filter: ", len(edge_array)
	path = find_longest_path(edge_array, [])
	#print "longest path found has length", len(path)
	#print path_string_from_array(path)
	path_vectors = find_vectors_from_path(path, [])
	print path_vectors_string(path_vectors)
	print "number of vectors:", len(path_vectors)

def path_vectors_string(path_vectors):
    # generates a string that can be used to view the vectors at http://www.shodor.org/interactivate/activities/SimplePlot/
    path_vectors_list = []
    for line_segment in path_vectors:
	path_vectors_list.append(line_segment[0])
    path_vectors_list.append(path_vectors[-1][1])
    return path_string_from_array(path_vectors_list)

def find_vectors_from_path(path, vector_array):
    # recursively generates a set of vectors from the path
    init_point = path[0]
    vector = []
    for i in range(0,len(path)):
	coordinate = path[i]
	if is_vector(vector, coordinate):
	    vector.append(coordinate)
	else:
	    vector_array.append([init_point, coordinate])
	    return find_vectors_from_path(path[i:], vector_array)
    vector_array.append([init_point, path[-1]])
    return vector_array

def is_vector(a, b):
    # returns whether the path between a known vector set a, and a new point b, is a vector
    if len(a)==0:
	return True
    init_point = a[0]
    for point in a:
	distance = dist(init_point[0], init_point[1], b[0], b[1], point[0], point[1])
	#print "distance between line with endpoints ((%s,%s), (%s,%s)) and point (%s,%s) is %s" % (init_point[0], init_point[1], b[0], b[1], point[0], point[1], distance)
	if distance > math.sqrt(2):
	    return False
    return True
    
def dist(x1,y1, x2,y2, x3,y3):
    # calculates the distance from a line segment with endpoints (x1, y1) and (x2, y2) to a point (x3,y3)
    px = x2-x1
    py = y2-y1
    z = px*px + py*py
    u =  ((x3 - x1) * px + (y3 - y1) * py) / float(z)
    if u > 1:
        u = 1
    elif u < 0:
        u = 0
    x = x1 + u * px
    y = y1 + u * py
    dx = x - x3
    dy = y - y3
    dist = math.sqrt(dx*dx + dy*dy)
    return dist

def path_string_from_array(path_array):
    # generates a string which can be used to view the path at http://www.shodor.org/interactivate/activities/SimplePlot/
    path_string = ""
    for edge in path_array:
	y = 600-edge[0]
	x = edge[1]
	path_string += "(%s,%s)" % (x, y)
    return path_string

def find_longest_path(edge_array, path_array):
    # keep track of the longest continuous path, this is the object that is to be identified.
    for coordinate in edge_array:
	edge_array, path = path_from_pixel(edge_array, coordinate, [])
	if len(path) > len(path_array):
	    path_array = path
	return find_longest_path(edge_array, path_array)
    return path_array

def path_from_pixel(edge_array, coordinate, path):
    # recursively generate a continuous path from a given initial coordinate in the edge_array
    path.append(coordinate)
    edge_array.remove(coordinate)
    neighbors = neighbors_from_edge(coordinate)
    for edge in neighbors:
	if edge in edge_array:
	    return path_from_pixel(edge_array, edge, path)
    return (edge_array, path)

def neighbors_from_edge(coordinate):
    # returns all of the neighbors of a given edge
    y = coordinate[0]
    x = coordinate[1]
    return [[y-1, x-1], [y, x-1], [y+1, x-1], [y-1, x], [y+1, x], [y-1, x+1], [y, x+1], [y+1, x+1]]

def count_edges_in_array(array):
    # count the number of edges in the edge_array
    edge_count = 0
    for y in range(0,len(array)):
	y_array = array[y]
	for x in range(0, len(y_array)):
	    pixel_value = array[y][x]
	    if pixel_value > 0:
		edge_count = edge_count + 1
    return edge_count

def noise_reduction_edge_array(array):
    # filters the edge_array and only keeps objects that have a color value over a certain threshold
    edge_array = []
    for y in range(0,len(array)):
	y_array = array[y]
	for x in range(0, len(y_array)):
	    pixel_value = array[y][x]
	    if pixel_value > 75:
		edge_array.append([y,x])
    return edge_array

train()
