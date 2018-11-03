
"""
This component is the microflow controller.
The implementation is similar to learning controller. First, it acts as a learning controller by memorizing from which port a packet came from, so that next time if the MAC dst address is the same it knows where to forward it. Next time, if the controller knows where this packet should be sent (we already learned it), it simply installs the flow entry in the switch, so it doesn't ask the controller again.
    
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
    
        # Use this table to keep track of which ethernet address is on
        # which switch port (keys are MACs, values are ports).
        self.mac_to_port = {}
        
        
    def resend_packet (self, packet_in, out_port):
        """
        This method is the same, as in the t1_controller.py and t2_controller.py
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
    
    
    def act_like_flow_based_switch (self, packet, packet_in):
        """
        Implement flow based switch-like behavior.
        """
        # logging the learning process
        if packet.src not in self.mac_to_port:
            log.debug(("DPID %s is learning that " + str(packet.src) + " is attached at port " + str(packet_in.in_port)) % self.connection.dpid)
        
        # Learn the port for the source MAC (the same as learning controller), doesn't need to be inside if-statement, we simply can update it.
        self.mac_to_port[packet.src] = packet_in.in_port
    
        if packet.dst in self.mac_to_port:
            """
            This is the part that differs from learningController
            """
            # logging the installation of a flow in the switch
            log.debug(("DPID %s is installing flow dest " + str(packet.dst) + " to port " + str(self.mac_to_port[packet.dst])) % self.connection.dpid)

            msg = of.ofp_flow_mod()

            # Set fields to match the received packets (the packets that have the destination that we already learned will be matched)
            msg.match = of.ofp_match(dl_dst = packet.dst)
            msg.idle_timeout = 1000
            msg.buffer_id = packet_in.buffer_id
            msg.actions.append(of.ofp_action_output(port = self.mac_to_port[packet.dst]))
            
            # Send packet to install the flow entry
            self.connection.send(msg)

        else:
            # Flood the packet out everything but the input port
            # (just like a normal hub)
            log.debug("DPID %s doesn't know where to send, so he is sending to all" % self.connection.dpid)
            self.resend_packet(packet_in, of.OFPP_ALL)
        
    def _handle_PacketIn (self, event):
        """
        Handles packet in messages from the switch.
        """
        
        packet = event.parsed # This is the parsed packet data.
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return
                    
        packet_in = event.ofp # The actual ofp_packet_in message.
        self.act_like_flow_based_switch(packet, packet_in)


def launch ():
    """
    Starts the component
    """
    def start_switch (event):
        log.debug("Controlling %s" % (event.connection,))
        Controller(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)

