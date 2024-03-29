import numpy as np
import random
from PIL import Image
import itertools
import operator

#"""
from trainer import get_segments_from_edges
from trainer import find_object_x_ranges
from trainer import find_segments_in_range
from trainer import length_of_all_segments
from trainer import single_object_classifier
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
        x_ranges = find_object_x_ranges(segments)
        objects = []
        obj_num = 1
        for range in x_ranges:
            self.append_log("------------------ IDENTIFYING OBJECT %s OF %s ------------------" % (obj_num, len(x_ranges)))
            obj_num +=1
            range_segments = find_segments_in_range(range, segments)
            total_segment_length = length_of_all_segments(range_segments)
            if len(range_segments) <= 1:
                self.append_log("Object disregarded, only contains one path")
            elif total_segment_length < 50:
                self.append_log("Object disregarded, segments not long enough")
            else:
                best_guess = single_object_classifier("Live Image", range_segments)
                objects.append(best_guess)
            self.append_log("\n")
        return ", ".join(objects)

    def append_log(self, text):
        self.log_text.append(text)
	
    def logtext(self):
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
