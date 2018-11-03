
"""
This component is the hub controller.
    
It acts as a simple hub -- all network traffic is flooded on all ports except the port that it arrived in.

Author: Ard Kastrati
(The code is adapted from the tutorial example in OpenFlow website.)
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class Controller (object):
    """
    A Controller object is created for each switch that connects.
    A Connection object for that switch is passed to the __init__ function.
    """

    def __init__ (self, connection):
        # Keep track of the connection to the switch so that we can
        # send it messages!
        self.connection = connection
        # This binds our PacketIn event listener
        connection.addListeners(self)
        
    def resend_packet (self, packet_in, out_port):
        """
        Instructs the switch to resend a packet that it had sent to us.
        "packet_in" is the ofp_packet_in object the switch had sent to the
        controller due to a table-miss.
        """
        msg = of.ofp_packet_out()
        msg.data = packet_in

        # Add an action to send to the specified port
        action = of.ofp_action_output(port = out_port)
        msg.actions.append(action)

        # Send message to switch
        self.connection.send(msg)
        
        
    def act_like_hub (self, packet, packet_in):
        """
        Implement hub-like behavior -- send all packets to all ports besides the input port.
        """
        
        # We want to output to all ports -- we do that using the special
        # OFPP_ALL port as the output port.  (We could have also used
        # OFPP_FLOOD (if we want to not forward to the ports that are disabled by Spanning Tree Protocol.)
        self.resend_packet(packet_in, of.OFPP_ALL)
        
        
    def _handle_PacketIn (self, event):
        """
        Handles packet in messages from the switch.
        """
        
        packet = event.parsed # This is the parsed packet data.
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return
                    
        packet_in = event.ofp  # The actual ofp_packet_in message.
        self.act_like_hub(packet, packet_in)


def launch ():
    """
    Starts the component
    """
    def start_switch (event):
        log.debug("Controlling %s" % (event.connection,))
        Controller(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)

