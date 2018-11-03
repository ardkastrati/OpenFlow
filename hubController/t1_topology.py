"""Custom topology (Topology 1)
    
    Three directly connected switches plus two hosts for the first switch and three hosts for the last switch:
    
    host(2) --- switch --- switch --- switch --- host(3)
    
    Adding the 'topos' dict with a key/value pair to generate our newly defined
    topology enables one to pass in '--topo=mytopo' from the command line.
    """

from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."
    
    def __init__( self ):
        "Create custom topo."
        
        # Initialize topology
        Topo.__init__( self )
        
        # Add hosts and switches
        h1 = self.addHost( 'h1' )
        h2 = self.addHost( 'h2' )
        h3 = self.addHost( 'h3' )
        h4 = self.addHost( 'h4' )
        h5 = self.addHost( 'h5' )
        
        s1 = self.addSwitch( 's1' )
        s2 = self.addSwitch( 's2' )
        s3 = self.addSwitch( 's3' )
        
        # Add links
        self.addLink( s1, s2 )
        self.addLink( s2, s3 )
        self.addLink( h1, s1 )
        self.addLink( h2, s1 )
        self.addLink( s3, h3 )
        self.addLink( s3, h4 )
        self.addLink( s3, h5 )


topos = { 'mytopo': ( lambda: MyTopo() ) }

