from __future__ import division
from collections import OrderedDict
import os, os.path
import math
import sys
sys.setrecursionlimit(1000000)
import classifier

NOISE_FILTER_THRESHOLD = 100
LINE_SEGMENT_PIXEL_DEVIATION = 3
MINIMUM_VALID_PATH_LENGTH = 3
LONG_TAIL = 0.90

# Used for calculating averages
values = {"cube": [sys.maxint, 0], "tree": [sys.maxint, 0], "steve": [sys.maxint, 0], "lady": [sys.maxint, 0]}
below_8 = {"cube": 0, "lady": 0, "tree": 0, "steve": 0}
cube_sum = 0
tree_sum = 0
lady_sum = 0
steve_sum = 0

def train():
    path = "./snapshots_training/"
    images = {}
    i = 0

    for root, dirs, filenames in os.walk(path):
        for f in filenames:
	   #if f=="9tree.png":
	   #if i < 9000:
	   if "lady" in f: 
	       print "loading image", f
               images[f] = classifier.load_image(path+f)
	       i = i+1
    
    for key in images:
	print "parsing image", key
	image_list = images[key]
	edge_array = image_list[0]
	segments = get_segments_from_edges(edge_array)
	#calculate_average_and_range(segments, key)
        print "FEATURE 1 (number of line segments):", len(segments)   
	intersection_position = vertical_intersection_point(segments)
	print "FEATURE 2 (vertical intersection position):", ("ABOVE" if  (intersection_position == 1) else "BELOW")
    #print_averages_and_ranges()

# -------------------- association matrix ---------------------

def association_matrix(edge_array):
    association_matrix = []
    # FEATURE 1: NUMBER OF LINE SEGMENTS IS LESS THAN OR EQUAL TO 8
    # FEATURE 2: VERTICAL INTERSECTION POSITION ABOVE
    # FEATURE 3: VERTICAL INTERSECTION POSITION BELOW
    #             steve      lady      cube      tree
    feature1 = [  0/57,      3/57,    27/57,     27/57    ]
    feature2 = [  7/38,      5/38,     0/38,     26/38    ]
    feature3 = [  20/70,     22/70,    27/70,     1/70    ]
    
    association_matrix.append(feature1)
    association_matrix.append(feature2)
    association_matrix.append(feature2)
    return association_matrix

# -------------------- methods for finding vertical intersection points from line segments --------------------

def vertical_intersection_point(segments):
    # Finds the point of intersection of the two longest near-vertical lines created from the line segments. If the point of intersection is above the two line segments, returns 1. Otherwise, returns 0.
    n = 2
    x = get_longest_vertical_lines(segments, n)
    if len(x) < n:
	return 0
    segment1 = x[0][1]
    segment2 = x[1][1]
    intersection = find_intersection(segment1, segment2)
    #print "segment %s has length %s" % (segment1, x[0][0])
    #print "segment %s has length %s" % (segment2, x[1][0])
    #print "intersection:", intersection
    y = intersection[1]
    max_y = max(segment1[0][1], segment1[1][1], segment2[0][1], segment2[1][1])
    if y > max_y:
        return 1
    return 0

def find_intersection(segment_a, segment_b):
    # Calculates the point of intersection of two line segments.
    slope_a, intercept_a = segment_equation(segment_a)
    slope_b, intercept_b = segment_equation(segment_b)
    x = (intercept_b - intercept_a)/(slope_a - slope_b)
    y = slope_a * x + intercept_a
    return (x, y)

def segment_equation(segment):
    # Returns the slope and intercept of a line defined by two points.
    x1 = segment[0][0]
    y1 = segment[0][1]
    x2 = segment[1][0]
    y2 = segment[1][1]
    slope = (y1-y2)/(x1-x2)
    intercept = y1-(slope * x1)
    return (slope, intercept)

def get_longest_vertical_lines(segments_array, n):
    # Returns a sorted dictionary of the top n line segments that have a slope greater than 0.5 or less than -0.5.
    length_with_segments = {}
    for segment in segments_array:
	y1 = 600-segment[0][0]
        y2 = 600-segment[1][0]
	x1 = segment[0][1]
        x2 = segment[1][1]
	if x1 != x2:
	    slope = (y1-y2)/(x1-x2)
	    if slope > 0.5 or slope < -0.5:
		xy_coordinates = [(x1, y1), (x2, y2)]
		length_with_segments[length(xy_coordinates)] = xy_coordinates
    sorted_segments = OrderedDict(sorted(length_with_segments.items(), key=lambda t: t[0], reverse=True))
    return sorted_segments.items()[0:n]

def length(segment):
    # Returns the length of a segment specified by its endpoints.
    x1 = segment[0][0]
    y1 = segment[0][1]
    x2 = segment[1][0]
    y2 = segment[1][1]
    value = math.pow(x2-x1, 2) + math.pow(y2-y1, 2)
    return math.sqrt(value) 

# -------------------- methods for finding average and range of segment length -------------------

def print_averages_and_ranges():
    print "below 8:", below_8
    print values
    print "cube_average", cube_sum/27
    print "tree_average", tree_sum/27
    print "lady_average", lady_sum/27
    print "cube_average", steve_sum/27

def calculate_average_and_range(segments, key):
    global lady_sum
    global cube_sum
    global tree_sum
    global steve_sum = 0
    n = 8
    num_edges = len(segments)
    if "cube" in key:
        if num_edges < n:
            below_8["cube"] += 1
        cube_sum += num_edges
        if num_edges < values["cube"][0]:
            values["cube"][0] = num_edges
        if num_edges > values["cube"][1]:
            values["cube"][1] = num_edges
    elif "tree" in key:
        if num_edges < n:
            below_8["tree"] += 1
        tree_sum += num_edges
        if num_edges < values["tree"][0]:
            values["tree"][0] = num_edges
        if num_edges > values["tree"][1]:
            values["tree"][1] = num_edges
    elif "steve" in key:
        if num_edges < n:
            below_8["steve"] += 1
        steve_sum += num_edges
        if num_edges < values["steve"][0]:
            values["steve"][0] = num_edges
        if num_edges > values["steve"][1]:
            values["steve"][1] = num_edges
    elif "lady" in key:
        if num_edges < n:
            below_8["lady"] += 1
        lady_sum += num_edges
        if num_edges < values["lady"][0]:
            values["lady"][0] = num_edges
        if num_edges > values["lady"][1]:
            values["lady"][1] = num_edges

# -------------------- methods for finding line segments --------------------

def get_segments_from_edges(edge_array):
    # Returns the set of line segments from a given edge array
    # Cut out the background from the image
    edge_array = edge_array[280:]
    edge_array = edge_array[1:-1]
    # Remove 1px border from all sides
    for y in range(0, len(edge_array)):
	row = edge_array[y]
	edge_array[y][0] = 0
        edge_array[y][-1] = 0
    # Process the image
    edge_array = noise_reduction_edge_array(edge_array)
    paths = find_all_paths(edge_array, [])
    path_string = ""
    for path in paths:
	path_string += path_string_from_array(path)
    #print path_string
    sorted_paths = remove_tail(sorted(paths, key=len, reverse=True), LONG_TAIL)
    #print "number of paths:", len(sorted_paths)

    # Generate full line segment list
    all_segments = []
    all_segments_string = ""
    for path in sorted_paths:
	path_segments = find_segments_from_path(path, [])
	all_segments_string += path_segments_string(path_segments)
	#print path_segments_string(path_segments)
        for path_segment in path_segments:
	    all_segments.append(path_segment)
    #print "----- all segments -----"
    #print all_segments
    #print "----- all segments string -----"
    #print all_segments_string
    f = open('segments_string.txt', 'w')
    f.write(all_segments_string)
    f.close()
    return all_segments

def remove_tail(sorted_paths, n):
    # Removes the "long tail" from a sorted path array, retaining only the first n percent of non-singular paths. This helps filter out noisy paths that were detected.
    length = 0
    filtered_paths = []
    for path in sorted_paths:
	if len(path) < MINIMUM_VALID_PATH_LENGTH:
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
    # Returns whether the path between a known line segment a, and a new point b, is a line segment.
    if len(a)==0:
	return True
    init_point = a[0]
    for point in a:
	distance = dist(init_point[0], init_point[1], b[0], b[1], point[0], point[1])
	if distance > LINE_SEGMENT_PIXEL_DEVIATION:
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
    if len(edge_array) > 0:
	edge_array, path = path_from_edge_array(edge_array, edge_array[0], [])
	path_array.append(path)
	return find_all_paths(edge_array, path_array)
    return path_array

def path_from_edge_array(edge_array, coordinate, path):
    # Recursively generate a continuous path from a given initial coordinate in the edge_array.
    neighbors = neighbors_from_edge(coordinate, edge_array)
    for edge in neighbors:
	path.append(edge)
	edge_array.remove(edge)
    for edge in neighbors:
	edge_neighbors = neighbors_from_edge(edge, edge_array)
	if len(edge_neighbors) > 0:
	    return path_from_edge_array(edge_array, edge, path)
    return (edge_array, path)

def neighbors_from_edge(coordinate, edge_array):
    # Returns all of the neighbors of a given edge.
    y = coordinate[0]
    x = coordinate[1]
    neighbors = [[y-1, x-1], [y, x-1], [y+1, x-1], [y-1, x], [y, x], [y+1, x], [y-1, x+1], [y, x+1], [y+1, x+1]]
    valid_neighbors = []
    for neighbor in neighbors:
	if neighbor in edge_array:
	    valid_neighbors.append(neighbor)
    return valid_neighbors

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
	    if pixel_value > NOISE_FILTER_THRESHOLD:
		edge_array.append([y,x])
    return edge_array

train()
