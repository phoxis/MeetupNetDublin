#!/usr/bin/env python
import os, os.path, sys
import logging as log
from optparse import OptionParser
import networkx as nx
import community

# --------------------------------------------------------------

def read_weighted_edgelist( in_path ):
	g = nx.Graph()
	fin = open(in_path,"r")
	for line in fin.readlines():
		parts = line.strip().split(" ")
		g.add_edge( parts[0], parts[1], weight=float(parts[2]) )
	fin.close()
	return g

# --------------------------------------------------------------

def main():
	parser = OptionParser(usage="usage: %prog [options] network_file")
	# algorithm parameters
	parser.add_option("--seed", action="store", type="int", dest="seed", help="initial random seed", default=1000)
	parser.add_option("-r", "--resolution", action="store", type="float", dest="resolution", help="OSLOM resolution parameter, controls community size. Must be in the interval (0, 1)", default=0.1)
	parser.add_option("-t", "--threshold", action="store", type="float", dest="threshold", help="OSLOM threshold parameter, controls number of modules", default=0.1)
	parser.add_option("-i", "--iters", action="store", type="int", dest="max_iterations", help="maximum number of OSLOM iterations, a larger value is slower", default=20)
	# general parameters
	parser.add_option("--dir", action="store", type="string", dest="dir_bin", help="path of directory containing OSLOM binary files", default="bin")
	parser.add_option("-m", "--minsize", action="store", type="int", dest="min_size", help="minimum community size, communities below this size are filtered", default=2)
	parser.add_option("-o", action="store", type="string", dest="out_path", help="community list output file path", default=None)
	(options, args) = parser.parse_args()
	if( len(args) < 1 ):
		parser.error( "Must specify a network file" )
	log.basicConfig(level=20, format='%(message)s')
	# by default, always assume a weighted network
	weighted = True

	# Read the input network file
	log.info( "Reading network from %s ..." % args[0])
	if args[0].endswith(".gexf"):
		g = nx.read_gexf( args[0] )
	else:
		if weighted:
			g = read_weighted_edgelist(args[0])
		else:
			g = nx.read_edgelist(args[0])
	log.info( "Network has %d nodes, %d edges - directed=%s" % ( g.number_of_nodes(), g.number_of_edges(), g.is_directed() ) )

	# Execute the OSLOM algorithm
	log.info( "Running OSLOM on network (seed=%d, weighted=%s, resolution=%.3f, threshold=%.3f) ..." 
		% (options.seed, weighted, options.resolution, options.threshold) )
	algorithm = community.OSLOM( options.dir_bin )
	algorithm.seed = options.seed
	algorithm.weighted = weighted
	algorithm.resolution = options.resolution
	algorithm.max_iterations = options.max_iterations
	algorithm.threshold = options.threshold
	communities = algorithm.find_communities( g )
	log.info("Algorithm found %d communities. Sizes = %s" % (len(communities), community.community_sizes(communities)))
	
	# Filter by size
	if options.min_size > 1:
		communities = community.filter_communities( communities, options.min_size )
		log.info("After filtering communities of size < %d, %d communities remain. Sizes = %s" 
			% (options.min_size, len(communities), community.community_sizes(communities) )  )
	log.info("Communities cover %d/%d nodes" % ( community.assigned_count(communities), g.number_of_nodes() ) )

	# Write community list?
	if not options.out_path is None:
		log.info("Writing %d communities to %s" %  ( len(communities), options.out_path) )
		community.write_communities( options.out_path, communities )

# --------------------------------------------------------------

if __name__ == "__main__":
	main()
