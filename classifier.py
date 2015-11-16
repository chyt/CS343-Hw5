import numpy as np
import random
import Image
import itertools
import operator

#from trainer import association_matrix
#from trainer import get_segments_from_edges
#from trainer import vertical_intersection_point

"""
This is your object classifier. You should implement the train and
classify methods for this assignment.
"""
class ObjectClassifier():
    log_text = []
    
    """
    Everytime a snapshot is taken, this method is called and
    the result is displayed on top of the four-image panel.
    """
    def classify(self, edge_pixels, orientations):
	# Get the trained association matrix
	matrix = association_matrix()
	
	# Get feature 1: number of line segments
	segments = get_segments_from_edges(edge_pixels)
	self.append_log("Feature 1: number of line segments: %s" % (len(segments)))
	self.append_log("%s" % (segments))
	prob_feature1_steve = prob_feature1_lady = prob_feature1_cube = prob_feature1_tree = 1
        if len(segments) <= 8:
            prob_feature1_steve = matrix[0][0]
	    prob_feature1_lady = matrix[0][1]
	    prob_feature1_cube = matrix[0][2]
	    prob_feature1_tree = matrix[0][3]

	intersection_position = vertical_intersection_point(segments)
	self.append_log("Feature 2/3 (vertical intersection position): %s" % ("ABOVE" if  (intersection_position == 1) else "BELOW"))

	# Get feature 2: vertical intersection position above
	prob_feature2_steve = prob_feature2_lady = prob_feature2_cube = prob_feature2_tree = 1.0
        if intersection_position == 1:
            prob_feature2_steve = matrix[1][0]
	    prob_feature2_lady = matrix[1][1]
	    prob_feature2_cube = matrix[1][2]
	    prob_feature2_tree = matrix[1][3]

	# Get feature 3: vertical intersection position below
	prob_feature3_steve = prob_feature3_lady = prob_feature3_cube = prob_feature3_tree = 1.0
        if intersection_position == 0:
            prob_feature3_steve = matrix[2][0]
	    prob_feature3_lady = matrix[2][1]
	    prob_feature3_cube = matrix[2][2]
	    prob_feature3_tree = matrix[2][3]

	# P(C) = 0.25, because we have equal number of images for each object in our training set
	p_c = 0.25
	p_steve = p_c * prob_feature1_steve * prob_feature2_steve * prob_feature3_steve
	p_lady = p_c * prob_feature1_lady * prob_feature2_lady * prob_feature3_lady
	p_cube = p_c * prob_feature1_cube * prob_feature2_cube * prob_feature3_cube
	p_tree = p_c * prob_feature1_tree * prob_feature2_tree * prob_feature3_tree

	self.append_log("p(steve): %s | p(lady): %s | p(cube): %s | p(tree): %s" % (p_steve, p_lady, p_cube, p_tree))
	p_dict = { "Steve":p_steve, "Lady":p_lady, "Cube":p_cube, "Tree":p_tree }
	return max(p_dict.iteritems(), key=operator.itemgetter(1))[0]
    
    """
    This is your training method. Feel free to change the
    definition to take a directory name or whatever else you
    like. The load_image (below) function may be helpful in
    reading in each image from your datasets.
    """
    def train(self):
        pass
    
    def append_log(self, text):
	self.log_text.append(text)
	
    def logtext(self):
	#return self.log_text
	return '\n\n'.join(self.log_text);

def stringify(array):
    return_string = ""
    for inner_array in array:
	return_string = return_string + "["

	for item in inner_array:
	    return_string = return_string + ", " + str(item)
	return_string = return_string + "],"
    return return_string

"""
Loads an image from file and calculates the edge pixel orientations.
Returns a tuple of (edge pixels, pixel orientations).
"""
def load_image(filename):
    im = Image.open(filename)
    np_edges = np.array(im)
    upper_left = push(np_edges, 1, 1)
    upper_center = push(np_edges, 1, 0)
    upper_right = push(np_edges, 1, -1)
    mid_left = push(np_edges, 0, 1)
    mid_right = push(np_edges, 0, -1)
    lower_left = push(np_edges, -1, 1)
    lower_center = push(np_edges, -1, 0)
    lower_right = push(np_edges, -1, -1)
    vfunc = np.vectorize(find_orientation)
    orientations = vfunc(upper_left, upper_center, upper_right, mid_left, mid_right, lower_left, lower_center, lower_right)
    return (np_edges, orientations)

        
"""
Shifts the rows and columns of an array, putting zeros in any empty spaces
and truncating any values that overflow
"""
def push(np_array, rows, columns):
    result = np.zeros((np_array.shape[0],np_array.shape[1]))
    if rows > 0:
        if columns > 0:
            result[rows:,columns:] = np_array[:-rows,:-columns]
        elif columns < 0:
            result[rows:,:columns] = np_array[:-rows,-columns:]
        else:
            result[rows:,:] = np_array[:-rows,:]
    elif rows < 0:
        if columns > 0:
            result[:rows,columns:] = np_array[-rows:,:-columns]
        elif columns < 0:
            result[:rows,:columns] = np_array[-rows:,-columns:]
        else:
            result[:rows,:] = np_array[-rows:,:]
    else:
        if columns > 0:
            result[:,columns:] = np_array[:,:-columns]
        elif columns < 0:
            result[:,:columns] = np_array[:,-columns:]
        else:
            result[:,:] = np_array[:,:]
    return result

# The orientations that an edge pixel may have.
np_orientation = np.array([0,315,45,270,90,225,180,135])

"""
Finds the (approximate) orientation of an edge pixel.
"""
def find_orientation(upper_left, upper_center, upper_right, mid_left, mid_right, lower_left, lower_center, lower_right):
    a = np.array([upper_center, upper_left, upper_right, mid_left, mid_right, lower_left, lower_center, lower_right])
    return np_orientation[a.argmax()]
