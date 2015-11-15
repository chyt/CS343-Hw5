import classifier
import os, os.path
import math
import sys
sys.setrecursionlimit(1000000)

def train():
    path = "./snapshots_training/"
    images = {}
    i = 0;
    for root, dirs, filenames in os.walk(path):
        for f in filenames:
	   if f=="1cube.png":
	   #if i < 9000:
	       print "loading image", f
               images[f] = classifier.load_image(path+f)
	       i = i+1
    
    for key in images:
	print "parsing image", key
	image_list = images[key]
	edge_array = image_list[0]
	# Cut out the background from the image
	edge_array = edge_array[280:]
	edge_array = edge_array[1:-1]
	# Remove 1px border from all sides
        for y in range(0, len(edge_array)):
            row = edge_array[y]
            edge_array[y][0] = 0
            edge_array[y][len(row)-1] = 0
	# Process the image
	edge_array = noise_reduction_edge_array(edge_array)
	paths = find_all_paths(edge_array, [])
	path_string = ""
	for path in paths:
	    path_string += path_string_from_array(path)
	    #print "-------- path ---------"
	    #print path_string_from_array(path)
	#print path_string
	sorted_paths = remove_tail(sorted(paths, key=len, reverse=True), 0.90)
	print "number of paths:", len(sorted_paths)

	# Generate full line segment list
	all_segments = []
	all_segments_string = ""
	for path in sorted_paths:
	    path_segments = find_segments_from_path(path, [])
	    print path
	    print "---------------"
	    all_segments_string += path_segments_string(path_segments)
	    #print path_segments_string(path_segments)
	    for path_segment in path_segments:
		all_segments.append(path_segment)
	#print "-----all segments"
	#print all_segments
	#print "-----all segments string"
	#print all_segments_string
	#print "number of line segments:", len(all_segments)

def remove_tail(sorted_paths, n):
    # Removes the "long tail" from a sorted path array, retaining only the first n percent of non-singular paths. This helps filter out noisy paths that were detected.
    length = 0
    filtered_paths = []
    for path in sorted_paths:
	if len(path)<3:
	    sorted_paths.remove(path)
	else:
	    length += len(path)
    filter_length = n*length
    total_path_length = 0
    for path in sorted_paths:
	if total_path_length < filter_length:
	    filtered_paths.append(path)
	    total_path_length += len(path)
    return filtered_paths

def path_segments_string(path_segments):
    # Generates a string that can be used to view the line segments at http://www.shodor.org/interactivate/activities/SimplePlot/.
    path_segments_list = []
    path_segments_list.append(path_segments[0][0])
    for line_segment in path_segments:
	path_segments_list.append(line_segment[1])
    return path_string_from_array(path_segments_list)

def find_segments_from_path(path, segment_array):
    # Recursively generates a set of line segments from the path.
    init_point = path[0]
    segment = []
    for i in range(0,len(path)):
	coordinate = path[i]
	if is_line_segment(segment, coordinate):
	    segment.append(coordinate)
	else:
	    segment_array.append([init_point, coordinate])
	    return find_segments_from_path(path[i:], segment_array)
    segment_array.append([init_point, path[-1]])
    return segment_array

def is_line_segment(a, b):
    # Returns whether the path between a known line segment a, and a new point b, is a vector.
    if len(a)==0:
	return True
    init_point = a[0]
    for point in a:
	distance = dist(init_point[0], init_point[1], b[0], b[1], point[0], point[1])
	if distance > math.sqrt(2):
	    return False
    return True
    
def dist(x1,y1, x2,y2, x3,y3):
    # Calculates the distance from a line segment with endpoints (x1, y1) and (x2, y2) to a point (x3,y3).
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
    # Generates a string which can be used to view the path at http://www.shodor.org/interactivate/activities/SimplePlot/.
    path_string = ""
    for edge in path_array:
	y = 600-edge[0]
	x = edge[1]
	path_string += "(%s,%s)" % (x, y)
    return path_string

def find_all_paths(edge_array, path_array):
    # Find all the paths in the edge space.
    for coordinate in edge_array:
	edge_array, path = path_from_pixel(edge_array, coordinate, [])
	path_array.append(path)
	return find_all_paths(edge_array, path_array)
    return path_array

def path_from_pixel(edge_array, coordinate, path):
    # Recursively generate a continuous path from a given initial coordinate in the edge_array.
    path.append(coordinate)
    edge_array.remove(coordinate)
    neighbors = neighbors_from_edge(coordinate)
    for edge in neighbors:
	if edge in edge_array:
	    return path_from_pixel(edge_array, edge, path)
    return (edge_array, path)

def neighbors_from_edge(coordinate):
    # Returns all of the neighbors of a given edge.
    y = coordinate[0]
    x = coordinate[1]
    return [[y-1, x-1], [y, x-1], [y+1, x-1], [y-1, x], [y+1, x], [y-1, x+1], [y, x+1], [y+1, x+1]]

def count_edges_in_array(array):
    # Counts the number of edges in the edge_array.
    edge_count = 0
    for y in range(0,len(array)):
	y_array = array[y]
	for x in range(0, len(y_array)):
	    pixel_value = array[y][x]
	    if pixel_value > 0:
		edge_count = edge_count + 1
    return edge_count

def noise_reduction_edge_array(array):
    # Filters the edge_array and only keeps objects that have a color value over a certain threshold.
    edge_array = []
    for y in range(0,len(array)):
	y_array = array[y]
	for x in range(0, len(y_array)):
	    pixel_value = array[y][x]
	    if pixel_value > 70:
		edge_array.append([y,x])
    return edge_array

train()
