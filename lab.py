#!/usr/bin/env python3

from util import read_osm_data, great_circle_distance, to_local_kml_url

# NO ADDITIONAL IMPORTS!


ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
}


DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
}


def build_auxiliary_structures(nodes_filename, ways_filename):
    """
    Create any auxiliary structures you are interested in, by reading the data
    from the given filenames (using read_osm_data)
    """
    #create a function that returns neighboring nodes
    #dictionary of node where keys are neighbors and values are weights
    # ways = read_osm_data(ways_filename)
    #nodes = read_osm_data(nodes_filename)
    d = {'d1': {}, 'd2': {}, 'limits': {}}
    #rename
    
    for way in read_osm_data(ways_filename):
        if 'highway' in way['tags'] and way['tags'].get('highway') in ALLOWED_HIGHWAY_TYPES:
            
            if 'maxspeed_mph' in way['tags']:
                speed_value = way['tags']['maxspeed_mph']
            else: 
                highway_type = way['tags']['highway']
                speed_value = DEFAULT_SPEED_LIMIT_MPH[highway_type]
                
            for i in range(len(way['nodes'])-1):
                 first_node = way['nodes'][i]
                 second_node = way['nodes'][i+1]
                 #distance = great_circle_distance(flipped_dict[first_node], flipped_dict[second_node]) 
                 
                 if first_node not in d['d1']:
                     d['d1'][first_node] = {}
                     
                 if second_node not in d['d1']:
                     d['d1'][second_node] = {}
                     
                 if first_node not in d['limits']:
                     d['limits'][first_node] = set()
                     
                 if second_node not in d['limits']:
                     d['limits'][second_node] = set()
                     
                 if way['tags'].get('oneway') == 'yes':
                    d['d1'][first_node][second_node] = 0
                    d['limits'][first_node].add((second_node, speed_value))
                    #d['d2'][first_node] = flipped_dict[first_node]
                    #d['d2'][second_node] = flipped_dict[second_node]
                    
                 else: 
                    d['d1'][first_node][second_node] = 0 
                    d['d1'][second_node][first_node] = 0
                    d['limits'][first_node].add((second_node, speed_value))
                    d['limits'][second_node].add((first_node, speed_value))
                    #d['d2'][first_node] = flipped_dict[first_node]
                    #d['d2'][second_node] = flipped_dict[second_node]
                    
    
    for node in read_osm_data(nodes_filename): 
        if node['id'] in d['d1']: 
            d['d2'][node['id']] = (node['lat'], node['lon'])
        
    for node1 in d['d1']: 
        for node2 in d['d1'][node1]:
            d['d1'][node1][node2] = great_circle_distance(d['d2'][node1], d['d2'][node2])
            
                                         
    return d 
       
        

def find_short_path_nodes(aux_structures, node1, node2):
    """
    Return the shortest path between the two nodes

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        node1: node representing the start location
        node2: node representing the end location

    Returns:
        a list of node IDs representing the shortest path (in terms of
        distance) from node1 to node2
    """
    agenda = [(0, [node1], 0)]
    #added third value for f(n)
    expanded = set()
    #store agenda of paths to consider and expanded set containing everything that we've seen before
     
    if node1 == node2:
        return [node1] 
    
    count = 0 
    while len(agenda) != 0: 
        #while agenda
        #remove path with lowest cost from agenda
    
        #finding minimum value and index of minimum value
        vals = []
        for i in range(len(agenda)):
            #append based off of f(n)
            vals.append(agenda[i][0])
        
        #need f(n)
        minimum_val = min(vals)
        min_val_index = vals.index(minimum_val)
        
        #remove path with lowest cost and get the value with pop function 
        path = agenda.pop(min_val_index)
        
        count += 1
        
        terminal_vertex = path[1][-1]
        
        if terminal_vertex in expanded: #terminal vertex in expanded set 
            #ignore and move on to next path
            continue 
            
        if terminal_vertex == node2:
            #if terminal vertex is the goal, return that path
            print(count)
            return path[1]
        
        else: #add terminal vertex to expanded set 
            expanded.add(terminal_vertex)

        #loop through the children of terminal vertex
        for child in aux_structures['d1'][terminal_vertex].keys(): 
            if child in expanded: 
                continue  #skip
            else: 
                #add path to agenda 
                new_path = path[1] + [child]
                weight = path[0] + aux_structures['d1'][terminal_vertex][child]
                #g(n)
                heuristic_weight = weight + great_circle_distance(aux_structures['d2'][child], aux_structures['d2'][node2]) 
                agenda.append((weight, new_path, heuristic_weight))
                
                
                
 
def find_closest_node(aux_structures, loc):
    """
    Returns the closest node to a particular location 
    
    Parameters: 
        aux_structures: the result of calling in build_auxilliary_structures
        loc: a tuple representing the location of input
        
    Returns:
        The closest known location to the arbitrary input
    """
#    loc = []
#    keys = []
#    for location in aux_structures['d2']:
#        distance = great_circle_distance(aux_structures['d2'][location], (lat, lon)) 
#        loc.append(distance)
#        keys.append(location)
#    min_val = min(loc)
#    min_val_index = loc.index(min_val)
#    min_id = keys[min_val_index]
    return min(aux_structures['d2'], key=lambda key: great_circle_distance(aux_structures['d2'][key], loc))

        
    
    
def find_short_path(aux_structures, loc1, loc2):
    """
    Return the shortest path between the two locations

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """
    
    new_loc1 = find_closest_node(aux_structures, loc1)
    new_loc2 = find_closest_node(aux_structures, loc2)
    
    locations = find_short_path_nodes(aux_structures, new_loc1, new_loc2)
    
    tuple_loc = []
    
    if locations == None :
        return None
    
    for location in locations: 
        tuple_loc.append(aux_structures['d2'][location]) 
        
    return tuple_loc 
        


def find_fast_path(aux_structures, loc1, loc2):
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.
    """

    node1 = find_closest_node(aux_structures, loc1)
    node2 = find_closest_node(aux_structures, loc2)
    agenda = [(0, [node1])]
    #added third value for f(n)
    expanded = set()
    #store agenda of paths to consider and expanded set containing everything that we've seen before
     
    if node1 == node2:
        return [aux_structures['d2'][node1]]
    
    while agenda: 
        #while agenda not empty
        #remove path with lowest cost from agenda
    
        #finding minimum value and index of minimum value
        vals = []
        for i in range(len(agenda)):
            #append based off of f(n)
            vals.append(agenda[i][0])
            #time = distance/speed 
        #need f(n)
        minimum_val = min(vals)
        min_val_index = vals.index(minimum_val)
        
        #remove path with lowest cost and get the value with pop function 
        path = agenda.pop(min_val_index)
        
        
        terminal_vertex = path[1][-1]
        
        if terminal_vertex in expanded: #terminal vertex in expanded set 
            #ignore and move on to next path
            continue 
            
        if terminal_vertex == node2:
            #if terminal vertex is the goal, return that path
    
            tuple_loc = []
    
    
            for location in path[1]: 
                tuple_loc.append(aux_structures['d2'][location]) 
        
            return tuple_loc 
        
        expanded.add(terminal_vertex)

        #loop through the children of terminal vertex
        for child in aux_structures['limits'][terminal_vertex]:
            #child = (id, speed)
            if child[0] in expanded: 
                continue  #skip
            else: 
                #add path to agenda 
                new_path = path[1] + [child[0]]
                time = path[0] + great_circle_distance(aux_structures['d2'][child[0]], aux_structures['d2'][terminal_vertex])/child[1]
                agenda.append((time, new_path))
                #to package, 
                
            
                
        
                
                


if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
#    i = 0 
#    for node in read_osm_data('resources/cambridge.nodes'):
#        i += 1
#    print(i)
#    #use counter, adding to list allocates space in memory
    
#    i=0
#    for node in read_osm_data('resources/cambridge.nodes'):
#        if 'name' in node['tags']: 
#            i+=1
#    print(i)
#   #check to see if names in dictionary
    
#    data = read_osm_data('resources/cambridge.nodes')
#    print(next(data))
#    
#    for node in read_osm_data('resources/cambridge.nodes'):
#        if 'name' in node['tags']:
#            if node['tags']['name'] == '77 Massachusetts Ave':
#                print(node['id'])
    
    
#    i = 0 
#    for way in read_osm_data('resources/cambridge.ways'):
#        i += 1
#    print(i)
    
#    i=0
#    for way in read_osm_data('resources/cambridge.ways'):
#        if 'oneway' in way['tags']:
#            if way['tags']['oneway'] == 'yes':
#                i+=1
#    print(i)
    
#    print(great_circle_distance((42.363745, -71.100999), (42.361283, -71.239677)))
#    
#    for node in read_osm_data('resources/midwest.nodes'):
#        if node['id'] == 233941454:
#            print(node['lat'], node['lon'])
#        if node['id'] == 233947199:
#            print(node['lat'], node['lon'])
#        
#    print(great_circle_distance((41.422729 ,-89.21953), (41.452578, -89.627043)))
#   
    
#    for way in read_osm_data('resources/midwest.ways'):
#        if way['id'] == 21705939:
#            a = way['nodes']
#            print(way)
#
#    loc = []
#    for node in read_osm_data('resources/midwest.nodes'):
#        if node['id'] in a:
#            loc.append((node['lat'], node['lon']))
#       
#    a = great_circle_distance((41.447604, -89.393558), (41.447601, -89.394215)) 
#    b = great_circle_distance((41.447601, -89.394215), (41.447611, -89.395527)) 
#    c = great_circle_distance((41.447611, -89.395527), (41.447611, -89.396958))        
#    d = great_circle_distance((41.447611, -89.396958), (41.447607, -89.402144))
#    e = great_circle_distance((41.447607, -89.402144), (41.447677, -89.403083))
#    f = great_circle_distance((41.447677, -89.403083), (41.447795, -89.404006))
#    g = great_circle_distance((41.447795, -89.404006), (41.447801, -89.404476))
#    h = great_circle_distance((41.447801, -89.404476), (41.447801, -89.404946))
#    i = great_circle_distance((41.447801, -89.404946), (41.447773, -89.407548))
#            
    #print(a+b+c+d+e+f+g+h+i)
#    print('nodes')
#    for node in read_osm_data('resources/mit.nodes'):
#        print(node)
#        
    print('ways')
    for way in read_osm_data('resources/mit.ways'):
        print(way)
#        
    
        
    #print(build_auxiliary_structures('resources/mit.nodes', 'resources/mit.ways'))
#    a = build_auxiliary_structures('resources/mit.nodes', 'resources/mit.ways')
#    print(find_short_path_nodes(a, 1, 2))
#    
#    for node in read_osm_data('resources/midwest.nodes'):
#        print(node)
    
#    b = build_auxiliary_structures('resources/cambridge.nodes', 'resources/cambridge.ways')
#    print(find_short_path(b, (42.3858, -71.0783), (42.5465, -71.1787)))
    
    print(build_auxiliary_structures('resources/mit.nodes', 'resources/mit.ways')['limits'])
    
    