from __future__ import division
from collections import OrderedDict
import os, os.path
import math
import sys
sys.setrecursionlimit(1000000)
import operator
import classifier

SINGLE_VALIDATION = False

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
    path = "./snapshots_extra/"
    images = {}
    i = 0
    number_correct = 0

    for root, dirs, filenames in os.walk(path):
        for f in filenames:
           #if f=="104lady.png":
           if i < 9000:
           #if "tree" in f:
               print "Loading image", f
               images[f] = classifier.load_image(path+f)
               i = i+1
    
    for image in images:
        print "\n--------------------------------------------- PARSING IMAGE", image
        image_list = images[image]
        edge_array = image_list[0]
        segments = get_segments_from_edges(edge_array)

        x_ranges = find_object_x_ranges(segments)
        obj_num = 1
        for range in x_ranges:
            print "------------------ IDENTIFYING OBJECT %s OF %s ------------------" % (obj_num, len(x_ranges))
            obj_num +=1
            range_segments = find_segments_in_range(range, segments)
            total_segment_length = length_of_all_segments(range_segments)
            if len(range_segments) <= 1:
                print "Object disregarded, only contains one path"
            elif total_segment_length < 50:
                print "Object disregarded, segments not long enough"
            else:
                best_guess = single_object_classifier(image, range_segments)
            print "\n"

            if SINGLE_VALIDATION:
                if best_guess.lower() in image.lower():
                    number_correct += 1
    if SINGLE_VALIDATION:
        print "\n--------------------------------------------- RESULTS"
        print "Correctly identified %s/%s objects." % (number_correct, len(images))

# -------------------- multiple object classifier (extra credit) --------------------

def length_of_all_segments(range_segments):
    total_length = 0
    for segment in range_segments:
        total_length += length(segment)
    return total_length

def find_segments_in_range(range, segments):
    # Filter all the segments in the image, by a given range of x values. This should identify a single object in the image. From here, we can run the classifier on the single image, and thus support multiple object recognition within a single image.
    min_x = range[0]
    max_x = range[1]
    range_segments = []
    for segment in segments:
        a = segment[0][1]
        b = segment[1][1]
        min_seg_x = min(a,b)
        max_seg_x = max(a,b)
        if min_seg_x >= min_x and max_seg_x <= max_x:
            range_segments.append(segment)
    return range_segments

def find_object_x_ranges(segments):
    # Assuming that each object occupies separate ranges of x values, we can identify objects by looking for clusters of x values. Returns an array containing all the clusters that were found, given by initial and ending point.
    x_values = []
    for segment in segments:
        a = segment[0][1]
        b = segment[1][1]
        for i in range(min(a,b), max(a,b)+1):
            x_values.append(i)
    x_values = list(set(x_values))
    ranges = find_ranges(x_values, [])
    return ranges

def find_ranges(x_values, range_array):
    # Recursively find x ranges that are occupied by objects, and returns the result in range_array.
    if len(x_values) > 0:
        init_point = 0
        for i in range(0, 800):
            if i in x_values:
                init_point = i
                break
        end_point = init_point
        # Allows a maximum gap of max_gap, due to potential inaccuracies in the segment detection algorithm
        max_gap = 2 * MINIMUM_VALID_PATH_LENGTH + 1
        gap = 0
        while end_point in x_values or gap < max_gap:
            if end_point in x_values:
                x_values.remove(end_point)
                gap = 0
            else:
                gap += 1
            end_point += 1
        range_array.append([init_point, end_point-1])
        return find_ranges(x_values, range_array)
    return range_array

# -------------------- single object classifier --------------------

def single_object_classifier(image, segments):
    print "----- FEATURES -----"
    print "Feature 1/4 (number of line segments):", len(segments)

    intersection_position = vertical_intersection_point(segments)
    print "Feature 2/3 (vertical intersection position):", ("ABOVE" if  (intersection_position == 1) else "BELOW")

    best_fit = best_fit_area_segments(segments)
    print "Feature 5/6 (best fit):", ("STEVE" if (best_fit==1) else "LADY")

    print "----- PROBABILITIES -----"
    prob_dict = prob_by_features(len(segments), intersection_position, best_fit)
    for key, value in prob_dict.items():
        print "Probability that object is %s is %s" % (key, value)

    print "----- BEST GUESS -----"
    best_guess = max(prob_dict.iteritems(), key=operator.itemgetter(1))[0]
    print "File name: %s | Best guess: %s" % (image, best_guess)
    return best_guess

# -------------------- classifier --------------------

def prob_by_features(num_segments, intersection_position, best_fit_area_segments):
    # Classifies an object based on 6 features described by three properties: number of line segments, vertical intersection position, and best fit based on area and number of segments
    matrix = association_matrix()

    # Classify by feature 1: number of segments is <= 8
    prob_feature1_steve = prob_feature1_lady = prob_feature1_cube =  prob_feature1_tree = 1
    if num_segments <= 8:
        prob_feature1_steve = matrix[0][0]
        prob_feature1_lady = matrix[0][1]
        prob_feature1_cube = matrix[0][2]
        prob_feature1_tree = matrix[0][3]

    # Classify by feature 2: vertical intersection position is ABOVE
    prob_feature2_steve = prob_feature2_lady = prob_feature2_cube = prob_feature2_tree = 1.0
    if intersection_position == 1:
        prob_feature2_steve = matrix[1][0]
        prob_feature2_lady = matrix[1][1]
        prob_feature2_cube = matrix[1][2]
        prob_feature2_tree = matrix[1][3]

    # Classify by feature 3: vertical intersection position is BELOW
    prob_feature3_steve = prob_feature3_lady = prob_feature3_cube = prob_feature3_tree = 1.0
    if intersection_position == 0:
        prob_feature3_steve = matrix[2][0]
        prob_feature3_lady = matrix[2][1]
        prob_feature3_cube = matrix[2][2]
        prob_feature3_tree = matrix[2][3]

    # Classify by feature 4: number of segments is > 8
    prob_feature4_steve = prob_feature4_lady = prob_feature4_cube = prob_feature4_tree = 1.0
    if num_segments > 8:
        prob_feature4_steve = matrix[3][0]
        prob_feature4_lady = matrix[3][1]
        prob_feature4_cube = matrix[3][2]
        prob_feature4_tree = matrix[3][3]

    # Classify by feature 5: ratio of number of segments to frame area fits best to STEVE
    prob_feature5_steve = prob_feature5_lady = prob_feature5_cube = prob_feature5_tree = 1.0
    if best_fit_area_segments == 1:
        prob_feature5_steve = matrix[4][0]
        prob_feature5_lady = matrix[4][1]
        prob_feature5_cube = matrix[4][2]
        prob_feature5_tree = matrix[4][3]

    # Classify by feature 6: ratio of number of segments to frame area fits best to LADY
    prob_feature6_steve = prob_feature6_lady = prob_feature6_cube = prob_feature6_tree = 1.0
    if best_fit_area_segments == 0:
        prob_feature6_steve = matrix[5][0]
        prob_feature6_lady = matrix[5][1]
        prob_feature6_cube = matrix[5][2]
        prob_feature6_tree = matrix[5][3]

    # Calculate probablibility of each object based on the features of the snapshot

    # P(C) = 0.25, because we have equal number of images for each object in our training set
    p_c = 0.25

    # Probability of Steve
    prob_steve = p_c * prob_feature1_steve * prob_feature2_steve * prob_feature3_steve * prob_feature4_steve * prob_feature5_steve * prob_feature6_steve

    # Probability of Lady
    prob_lady = p_c * prob_feature1_lady * prob_feature2_lady * prob_feature3_lady * prob_feature4_lady * prob_feature5_lady * prob_feature6_lady

    # Probability of Cube
    prob_cube = p_c * prob_feature1_cube * prob_feature2_cube * prob_feature3_cube * prob_feature4_cube * prob_feature5_cube * prob_feature6_cube

    # Probability of Tree
    prob_tree = p_c * prob_feature1_tree * prob_feature2_tree * prob_feature3_tree * prob_feature4_tree * prob_feature5_tree * prob_feature6_tree

    return { "Steve": prob_steve, "Lady": prob_lady, "Cube": prob_cube, "Tree": prob_tree }    

# -------------------- association matrix ---------------------

def association_matrix():
    # There are 27 of each object in our training data
    n = 27
    # FEATURE 1: NUMBER OF LINE SEGMENTS IS LESS THAN OR EQUAL TO 8
    # FEATURE 2: VERTICAL INTERSECTION POSITION IS ABOVE
    # FEATURE 3: VERTICAL INTERSECTION POSITION IS BELOW
    # FEATURE 4: NUMBER OF LINE SEGMENTS IS GREATER THAN 8
    # FEATURE 5: BEST FIT (# SEGMENTS, AREA) IS STEVE
    # FEATURE 6: BEST FIT (# SEGMENTS, AREA) IS LADY
    # 
    #             steve      lady      cube      tree
    feature1 = [   0/n,       3/n,     27/n,      27/n    ]
    feature2 = [   7/n,       5/n,      0/n,      26/n    ]
    feature3 = [  20/n,      22/n,     27/n,       1/n    ]
    feature4 = [  27/n,      24/n,      0/n,       0/n    ]
    feature5 = [  27/n,       0/n,      0/n,       0/n    ]
    feature6 = [   0/n,      27/n,     27/n,      27/n    ]
    
    association_matrix = [feature1, feature2, feature3, feature4, feature5, feature6]
    return association_matrix

# -------------------- methods for fitting object segments:area to training vectors for lady and steve --------------------

def best_fit_area_segments(segments):
    # Using the training data, we found a strong correlation between the area and number of segments for steve and lady. Here we define vectors to describe this correlation for each object, and match the object described by the segments to either steve of lady. Returns 1 for steve, 0 for lady.
    area = frame_area(segments)
    # Steve training data best fit line:
    # y = 667.03x - 21976, r^2 = 0.822
    steve_0 = (0, -21976)
    steve_1 = (1, -21308.97)
    # Lady training data best fit line:
    # y = 1395.7x - 11967, r^2 = 0.803
    lady_0 = (0, -11967)
    lady_1 = (1, -10571.3)

    coordinate = (len(segments), area)
    dist_from_steve_ratios = vector_dist(steve_0, steve_1, coordinate)
    dist_from_lady_ratios = vector_dist(lady_0, lady_1, coordinate)
    #print "distance from steve:", dist_from_steve_ratios
    #print "distance from lady:", dist_from_lady_ratios

    # Closer to steve
    if dist_from_steve_ratios < dist_from_lady_ratios:
        return 1
    # Closer to lady
    return 0

def vector_dist(a, b, c):
    # Create a vector from two given points, a and b, and find the shortest distance from point c to the vector
    t = b[0]-a[0], b[1]-a[1]           # Vector ab
    dd = math.sqrt(t[0]**2+t[1]**2)    # Length of ab
    t = t[0]/dd, t[1]/dd               # unit vector of ab
    n = -t[1], t[0]                    # normal unit vector to ab
    ac = c[0]-a[0], c[1]-a[1]          # vector ac
    # Projection of ac to n (the minimum distance)
    return math.fabs(ac[0]*n[0]+ac[1]*n[1])

def frame_area(segments):
    # Given the segments that make up an object, find the smallest pixel area that contains all of the segments.
    all_y = []
    all_x = []
    for segment in segments:
        y1 = 600-segment[0][0]
        y2 = 600-segment[1][0]
        x1 = segment[0][1]
        x2 = segment[1][1]
        all_y.append(y1)
        all_y.append(y2)
        all_x.append(x1)
        all_x.append(x2)
    min_x = min(all_x)
    max_x = max(all_x)
    min_y = min(all_y)
    max_y = max(all_y)
    area = (max_x - min_x) * (max_y - min_y)
    return area

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
    global steve_sum
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
    edge_array = edge_array[270:]
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
