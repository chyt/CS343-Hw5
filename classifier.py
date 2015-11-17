import numpy as np
import random
import Image
import itertools
import operator

#"""
from trainer import get_segments_from_edges
from trainer import vertical_intersection_point
from trainer import best_fit_area_segments
from trainer import prob_by_features
#"""

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
	self.append_log("---------- FEATURES: ----------")
	segments = get_segments_from_edges(edge_pixels)
        self.append_log("Feature 1/4 (number of line segments): %s" % (len(segments)))
  
	intersection_position = vertical_intersection_point(segments)
	self.append_log("Feature 2/3 (vertical intersection position): %s" % (("ABOVE" if  (intersection_position == 1) else "BELOW")))

	best_fit = best_fit_area_segments(segments)
	self.append_log("Feature 5/6 (best fit): %s" % (("STEVE" if (best_fit==1) else "LADY")))

	self.append_log("\n")
	self.append_log("---------- PROBABILITIES: ----------")
	prob_dict = prob_by_features(len(segments), intersection_position, best_fit)
	for key, value in prob_dict.items():
	    self.append_log("Probability that object is %s is %s" % (key, value))
	
	best_guess = max(prob_dict.iteritems(), key=operator.itemgetter(1))[0]
	return best_guess
    
    def append_log(self, text):
	self.log_text.append(text)
	
    def logtext(self):
	#return self.log_text
	return '\n'.join(self.log_text);

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
