MeetupNetDublin
===============

Code and data for community analysis of the Dublin Meetup.com network is provided here for reproducibility purposes, and to support the analysis of Meetup networks in other locations.

Full details of our methodology are provided in the paper [[PDF]](https://arxiv.org/pdf/1810.03046.pdf):

        MeetupNet Dublin: Discovering Communities in Dublin's Meetup Network (2018)
        Arjun Pakrashi, Elham Alghamdi, Brian Mac Namee, Derek Greene
        https://arxiv.org/abs/1810.03046

Code tested with Python 3.6. Dependencies: Pandas, Scikit-learn, NetworkX, Matplotlib.

### Data

The Meetup.com website provides [an open API](https://www.meetup.com/meetup_api/) that allows access to data from its platform. In September 2018 we used this to collect information about all meetups in Dublin, Ireland. This data was used to construct a weighted network, where each unique meetup is represented as a node, and a weighted edge between two nodes represents an association between the two meetups represented by its endpoint. The file [meetup-normalised-comembership.edges](data/meetup-normalised-comembership.edges) contains this network, in edge list format: (i.e. `node_id1 node_id2 weight`). The corresponding file [meetup-metadata.csv](data/meetup-metadata.csv) contains the corresponding metadata for each node.

### Step 1: Network Characterisation

The IPython notebook *Meetup Network Characterisation.ipynb* applies a number of standard network characterisation approaches to explore the Dublin meetup network.

### Step 2: Community Finding

To apply the Python wrapper for OSLOM algorithm to the meetup network, run the script *py-oslom.py*:

	python py-oslom.py data/meetup-normalised-comembership.edges --iters 20 --minsize 2 -r 0.1 -t 0.1 -o results/oslom-communities.comm

Note: Requires the compiled binary of the OSLOM C++ sources, which are available [from here](http://www.oslom.org/software.htm).

### Step 3: Community Analysis

The IPython notebook *Meetup Community Analysis.ipynb* analyses the results of applying OSLOM community finding to the Dublin meetup network, using both network-based and text-based techniques.


