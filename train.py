import classifier
import os, os.path

def train():
    path = "./snapshots_training/edges/"
    images = {}
    i = 0;
    for root, dirs, filenames in os.walk(path):
        for f in filenames:
	   if i < 1:
	       print "loading image" + f
               images[f] = classifier.load_image(path+f)
	       i = i+1
    
    for key in images:
	image_list = images[key]
	edge_array = image_list[0]
	#cutting out the background from the image
	edge_array = edge_array[280:]
	edge_array = edge_array[1:-1]
        print "total number of edge pixels: ", count_edges_in_array(edge_array)
        for y in range(0, len(edge_array)):
            row = edge_array[y]
            edge_array[y][0] = 0
            edge_array[y][len(row)-1] = 0
        print "number of edge pixels after removing border: ", count_edges_in_array(edge_array)
	#implement threshold
	edge_array = noise_reduction_edge_array(edge_array)
	print "number of edge pixels after filter: ", count_edges_in_array(edge_array)
	path_array = find_all_paths(edge_array)

    #print images

def find_all_paths(edge_array):
    for y in range(0,len(array)):
	y_array = array[y]
	for x in range(0, len(y_array)):
	    pixel_value = array[y][x]
	    path = path_from_pixel(array, y, x, [])
	    #remove all items in path from edge_array
	    #call find_all_paths again
	    break

def path_from_pixel(array, y, x, path_list):
    

def count_edges_in_array(array):
    edge_count = 0
    for y in range(0,len(array)):
	y_array = array[y]
	for x in range(0, len(y_array)):
	    pixel_value = array[y][x]
	    if pixel_value > 0:
		edge_count = edge_count + 1
    return edge_count

def noise_reduction_edge_array(array):
    for y in range(0,len(array)):
	y_array = array[y]
	for x in range(0, len(y_array)):
	    pixel_value = array[y][x]
	    if pixel_value < 75:
		array[y][x] = 0
	    else:
		array[y][x] = 1
    return array

train()
