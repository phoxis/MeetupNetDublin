import os, subprocess, operator
from tempfile import mkstemp
import logging as log

# --------------------------------------------------------------

def read_weighted_edgelist( in_path, sep = " " ):
    g = nx.Graph()
    fin = open(in_path,"r")
    for line in fin.readlines():
        parts = line.strip().split(sep)
        # assume node identifiers are integers
        g.add_edge( int(parts[0]), int(parts[1]), weight=float(parts[2]) )
    fin.close()
    return g

def filter_communities( communities, min_size ):
	""" 
	Remove communities below the specified minimum size. 
	Returns:
		A new filtered set of communities.
	"""
	filtered = []
	for comm in communities:
		if len(comm) >= min_size:
			filtered.append( comm )
	return filtered

def create_community_map( g, communities ):
	cmap = {}
	for i, comm in enumerate(communities):
		for node in comm:
			# already have the key?
			if node in cmap:
				cmap[node] = "Multi"
			else:
				cmap[node] = "C%02d" % (i+1)
	return cmap

def community_sizes( communities ):
	"""
	Return a list containing the number of nodes in each one of the specified communities.
	"""
	return [ len(comm) for comm in communities ]

def assigned_nodes( communities ):
	assigned = set()
	for comm in communities:
		for node in comm:
			assigned.add( node )
	return assigned

def assigned_count( communities ):
	return len( assigned_nodes(communities) )

def write_communities( out_path, communities ):
	"""
	Write community memberships as a list of node identifiers, one community per line
	"""
	with open(out_path, "w") as fout:
		for comm in communities:
			s = ""
			for c in comm:
				s += str(c) + " "
			fout.write( "%s\n" % s.strip() )
		fout.close()

def read_communities( in_path, min_community_size = 5 ):
    """
    Read community memberships from a while with a list of node identifiers (assumed to be integers), 
    one community per line. Ignore communities below a specific size.
    """
    fin = open(in_path,"r")
    communities = []
    num_filtered = 0
    for line in fin.readlines():
        parts = line.strip().split(" ")
        if len(parts) == 0:
            continue
        comm = set()
        for node in parts:
            comm.add( int(node) )
        if len(comm) < min_community_size:
            num_filtered += 1
        else:
            communities.append( comm )
    print("Found %d communities, after filtering %d communities of size < %d" % ( len(communities), num_filtered, min_community_size ) )
    return communities

def sort_communities_by_size( communities ):
	sizes = {}
	for comm in communities:
		comm = frozenset(comm)
		sizes[comm] = len(comm)
	return sorted(sizes.items(), key=operator.itemgetter(1), reverse=True)

# --------------------------------------------------------------
    
def execute( cmd, args, display_output = False ):
	# hack to get args processed correctly
	args = ' '.join(args).split(" ")
	cmd.extend(args)
	log.info( "Running: %s" % ' '.join(cmd) )
	p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	(output, err) = p.communicate()
	if not err is None:
		log.error("Failed to execute command: '%s'" %  ' '.join(cmd) )
		return None
	if display_output:
		log.info(output)
	# convert from bytes to string
	return output.decode(errors="ignore")

class OSLOM:
	""" 
	Wrapper class for the OSLOM community finding algorithm.
	See: http://www.oslom.org
	"""
	def __init__( self, dir_bin ):
		self.dir_bin = dir_bin
		self.weighted = False
		self.resolution = 0.01
		self.threshold = 0.1
		self.max_iterations = 20
		self.seed = 1000
		self.singlet = True

	def find_communities( self, g ):
		graph_directed = g.is_directed()
		graph_weighted = True
		# map nodes, counting from 1
		node_map = {}
		for node in g.nodes():
			# index from 1
			node_map[node] = len(node_map) + 1
		# cache graph
		fd, temp_path = mkstemp()
		log.info("Writing OSLOM graph to %s ..." % temp_path )
		fout = open(temp_path,"w")
		# what format?
		for e in g.edges( data=True ):
			if graph_weighted:
				if self.weighted:
					#fout.write("%d %d %.6f\n" % ( node_map[e[0]], node_map[e[1]], e[2]["weight"] ) )
					fout.write("%d %d %.6f 1\n" % ( node_map[e[0]], node_map[e[1]], e[2]["weight"] ) )
				else:
					# write integer weights
					fout.write("%d %d %.0f\n" % ( node_map[e[0]], node_map[e[1]], e[2]["weight"] ) )
			else:
				fout.write("%d %d\n" % ( node_map[e[0]], node_map[e[1]] ) )
		fout.close()
		# Create command line and run
		(cmd,args) = self._create_command_line( temp_path, graph_directed )		
		output = execute( cmd, args )
		if output is None:
			log.info("Failed to run OSLOM")
			return None
		# Parse the output 
		return self._read_results( node_map, temp_path )

	def _create_command_line( self, temp_path, directed ):
		# apply directed or undirected OSLOM?
		if directed:
			cmd = [ os.path.join( self.dir_bin, "oslom_dir" ) ]
		else:
			cmd = [ os.path.join( self.dir_bin, "oslom_undir" ) ]
		args = [ "-f %s" % temp_path]
		if self.weighted: 
			args.append( "-w" )
		else:
			args.append( "-uw" )
		args += [ "-seed %d" % self.seed, "-cp %f" % self.resolution, "-r %d" % self.max_iterations, "-t %f" % self.threshold  ]
		if self.singlet:
			args += ["-all"]
		return (cmd,args)

	def _read_results( self, node_map, temp_path ):
		# ensure we have the results
		dir_res = "%s_oslo_files" % temp_path
		if not os.path.exists(dir_res):
			log.info("ERROR: No output files found: %s" % dir_res )
			return None
		res_path = os.path.join(dir_res,"tp")
		if not os.path.exists(res_path):
			log.info("ERROR: No community file found: %s" % res_path )
			return None
		# create reverse map
		reverse_node_map = dict((v, k) for k, v in node_map.items())
		# read the output
		log.info("Reading output from %s ..." % res_path )
		lines = open(res_path,"r").readlines()
		communities = []
		current = None
		for l in lines:
			parts = l.strip().split(" ")
			if len(parts) == 0:
				continue
			if parts[0] == "#module":
				if len(parts) > 1:
					current = set()
			elif not current is None:
				for p in parts:
					# map back
					current.add( reverse_node_map[int(p)] )
				communities.append(current)
				current = None
		return communities
