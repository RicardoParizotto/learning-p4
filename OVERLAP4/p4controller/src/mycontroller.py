#!/usr/bin/env python2
import argparse
import os
from time import sleep

# NOTE: Appending to the PYTHON_PATH is only required in the `solution` directory.
#       It is not required for mycontroller.py in the top-level directory.
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import p4runtime_lib.bmv2
import p4runtime_lib.helper



'''

:param p4info_helper: the P4Info helper
:param ingress_sw: the ingress switch connection
:param egress_sw: the egress switch connection
:param tunnel_id: the specified tunnel ID
:param dst_eth_addr: the destination IP to match in the ingress rule
:param dst_ip_addr: the destination Ethernet address to write in the
                    egress rule
'''


'''
def writeIpv4Rule(p4info_helper, ingress_sw, dst_ip_addr, switch_port):
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ipv4_lpm",
        match_fields={
            "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
        },
        action_name="MyIngress.ipv4_forward",
        action_params={
            "dstAddr": dst_ip_addr,
            "port": switch_port
        })
    ingress_sw.WriteTableEntry(table_entry)
    print "Installed ingress tunnel rule on %s" % ingress_sw.name  


    def writeTunnelIngress(p4info_helper, ingress_sw, dst_ip_addr, ecmp_base, ecmp_max):
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ipv4_lpm",
        match_fields={
            "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
        },
        action_name="MyIngress.myTunnel_ingress",
        action_params={
            "ecmp_base": ecmp_base,
            "ecmp_count": ecmp_max,
        })
    ingress_sw.WriteTableEntry(table_entry)
    print "Installed ingress tunnel rule on %s" % ingress_sw.name    
'''


def writeBalancingEntry(p4info_helper, ingress_sw, dst_ip_addr, ecmp_base, ecmp_count, prefix_size):
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyEgress.turn_the_gambia_on",
        match_fields={
            "hdr.ipv4.dstAddr": (dst_ip_addr, prefix_size)
        },
        action_name="MyEgress.set_ecmp",
        action_params={
            "ecmp_base": ecmp_base,
            "ecmp_count": ecmp_count
        })
    ingress_sw.WriteTableEntry(table_entry)
    print "Installed ingress tunnel rule on %s" % ingress_sw.name


def writeFknEgress(p4info_helper, ingress_sw, dst_ip_addr, dst_addr, switch_port):
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.myFkn_egress",
        match_fields={
            "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
        },
        action_name="MyIngress.ipv4_forward",
        action_params={
            "dstAddr": dst_addr,
            "port": switch_port
        })
    ingress_sw.WriteTableEntry(table_entry)
    print "Installed ingress tunnel rule on %s" % ingress_sw.name



'''
1) An tunnel ingress rule on the ingress switch in the ipv4_lpm table that
       encapsulates traffic into a tunnel with the specified ID
'''
def writeTunnelIngress(p4info_helper, ingress_sw, dst_ip_addr, tunnel_id, prefix_size):
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ipv4_lpm",
        match_fields={
            "hdr.ipv4.dstAddr": (dst_ip_addr, prefix_size)
        },
        action_name="MyIngress.myTunnel_ingress",
        action_params={
            "dst_id": tunnel_id,
        })
    ingress_sw.WriteTableEntry(table_entry)
    print "Installed ingress tunnel rule on %s" % ingress_sw.name

'''
2) A transit rule on the ingress switch that forwards traffic based on
       the specified ID

    # 2) Tunnel Transit Rule
    # The rule will need to be added to the myTunnel_exact table and match on
    # the tunnel ID (hdr.myTunnel.dst_id). Traffic will need to be forwarded
    # using the myTunnel_forward action on the port connected to the next switch.
    #
    # For our simple topology, switch 1 and switch 2 are connected using a
    # link attached to port 2 on both switches. We have defined a variable at
    # the top of the file, SWITCH_TO_SWITCH_PORT, that you can use as the output
    # port for this action.
    #
    # We will only need a transit rule on the ingress switch because we are
    # using a simple topology. In general, you'll need on transit rule for
    # each switch in the path (except the last switch, which has the egress rule),
    # and you will need to select the port dynamically for each switch based on
    # your topology.
'''
def writeTunnelSwitch(p4info_helper, ingress_sw, tunnel_id, switch_port):
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.myTunnel_exact",
        match_fields={
            "hdr.myTunnel.dst_id": tunnel_id
        },
        action_name="MyIngress.myTunnel_forward",
        action_params={
            "port": switch_port
        })
    ingress_sw.WriteTableEntry(table_entry)
    print "Installed transit tunnel rule on %s" % ingress_sw.name

'''
3) An tunnel egress rule on the egress switch that decapsulates traffic
       with the specified ID and sends it to the host

    # 3) Tunnel Egress Rule
    # For our simple topology, the host will always be located on the
    # SWITCH_TO_HOST_PORT (port 1).
    # In general, you will need to keep track of which port the host is
    # connected to.

'''
def writeTunnelEgress(p4info_helper, egress_sw, tunnel_id, dst_eth_addr, switch_port):
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.myTunnel_exact",
        match_fields={
            "hdr.myTunnel.dst_id": tunnel_id
        },
        action_name="MyIngress.myTunnel_egress",
        action_params={
            "dstAddr": dst_eth_addr,
            "port": switch_port
        })
    egress_sw.WriteTableEntry(table_entry)
    print "Installed egress tunnel rule on %s" % egress_sw.name


def readTableRules(p4info_helper, sw):
    '''
    Reads the table entries from all tables on the switch.

    :param p4info_helper: the P4Info helper
    :param sw: the switch connection
    '''
    print '\n----- Reading tables rules for %s -----' % sw.name
    for response in sw.ReadTableEntries():
        for entity in response.entities:
            entry = entity.table_entry
            # TODO For extra credit, you can use the p4info_helper to translate
            #      the IDs the entry to names
            table_name = p4info_helper.get_tables_name(entry.table_id)
            print '%s: ' % table_name,
            for m in entry.match:
                print p4info_helper.get_match_field_name(table_name, m.field_id),
                print '%r' % (p4info_helper.get_match_field_value(m),),
            action = entry.action.action
            action_name = p4info_helper.get_actions_name(action.action_id)
            print '->', action_name,
            for p in action.params:
                print p4info_helper.get_action_param_name(action_name, p.param_id),
                print '%r' % p.value,
            print

def printCounter(p4info_helper, sw, counter_name, index):
    '''
    Reads the specified counter at the specified index from the switch. In our
    program, the index is the tunnel ID. If the index is 0, it will return all
    values from the counter.

    :param p4info_helper: the P4Info helper
    :param sw:  the switch connection
    :param counter_name: the name of the counter from the P4 program
    :param index: the counter index (in our case, the tunnel ID)
    '''
    for response in sw.ReadCounters(p4info_helper.get_counters_id(counter_name), index):
        for entity in response.entities:
            counter = entity.counter_entry
            print "%s %s %d: %d packets (%d bytes)" % (
                sw.name, counter_name, index,
                counter.data.packet_count, counter.data.byte_count
            )


def main(p4info_file_path, bmv2_file_path):
    # Instantiate a P4 Runtime helper from the p4info file
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)

    switches = {}

    # Create switch connection objects;
    # this is backed by a P4 Runtime gRPC connection

    switches["s1"] = p4runtime_lib.bmv2.Bmv2SwitchConnection('s1', 
                                                 address='127.0.0.1:50051',
                                                 device_id=0) 
    switches["s2"] = p4runtime_lib.bmv2.Bmv2SwitchConnection('s2', 
                                                 address='127.0.0.1:50052',
                                                 device_id=1)     
    switches["s3"] = p4runtime_lib.bmv2.Bmv2SwitchConnection('s3', 
                                                 address='127.0.0.1:50053',
                                                 device_id=2)
    switches["s4"] = p4runtime_lib.bmv2.Bmv2SwitchConnection('s4', 
                                                 address='127.0.0.1:50054',
                                                 device_id=3)
    switches["s5"] = p4runtime_lib.bmv2.Bmv2SwitchConnection('s5', 
                                                 address='127.0.0.1:50055',
                                                 device_id=4)
    switches["s6"] = p4runtime_lib.bmv2.Bmv2SwitchConnection('s6', 
                                                 address='127.0.0.1:50056',
                                                 device_id=5)
    switches["s7"] = p4runtime_lib.bmv2.Bmv2SwitchConnection('s7', 
                                                 address='127.0.0.1:50057',
                                                 device_id=6)

    # Install the P4 program on switches
    for k, sw in switches.items():
        sw.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                   bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForwardingPipelineConfig on %s" % sw.name



    # Write the rules that tunnel traffic from h1 to h3
    writeTunnelIngress(p4info_helper, ingress_sw=switches["s1"], dst_ip_addr="10.0.7.3", tunnel_id=3, prefix_size=32)          
    writeTunnelSwitch(p4info_helper, ingress_sw=switches["s1"], tunnel_id=3, switch_port=6)
    writeTunnelSwitch(p4info_helper, ingress_sw=switches["s4"], tunnel_id=3, switch_port=2)
    writeTunnelEgress(p4info_helper, egress_sw=switches["s7"], tunnel_id=3, dst_eth_addr="00:00:00:00:07:03", switch_port=1)

    #essa linha que tem que mudar
    writeTunnelIngress(p4info_helper, ingress_sw=switches["s7"], dst_ip_addr="10.0.1.0", tunnel_id=1, prefix_size=24)
    #jklasdfjalsjdf;asdf

    writeTunnelSwitch(p4info_helper, ingress_sw=switches["s7"], tunnel_id=1, switch_port=2)
    writeTunnelSwitch(p4info_helper, ingress_sw=switches["s4"], tunnel_id=1, switch_port=1)    
    writeTunnelEgress(p4info_helper, egress_sw=switches["s1"], tunnel_id=1, dst_eth_addr="00:00:00:00:01:04", switch_port=3)

    writeTunnelSwitch(p4info_helper, ingress_sw=switches["s7"], tunnel_id=2, switch_port=3)
    writeTunnelSwitch(p4info_helper, ingress_sw=switches["s5"], tunnel_id=2, switch_port=2)
    writeTunnelSwitch(p4info_helper, ingress_sw=switches["s2"], tunnel_id=2, switch_port=1)
    writeTunnelEgress(p4info_helper, egress_sw=switches["s1"], tunnel_id=2, dst_eth_addr="00:00:00:00:01:01", switch_port=1)   


    writeTunnelSwitch(p4info_helper, ingress_sw=switches["s1"], tunnel_id=4, switch_port=2) 
    writeTunnelSwitch(p4info_helper, ingress_sw=switches["s2"], tunnel_id=4, switch_port=2)
    writeTunnelSwitch(p4info_helper, ingress_sw=switches["s5"], tunnel_id=4, switch_port=3)
    writeTunnelEgress(p4info_helper, egress_sw=switches["s7"], tunnel_id=4, dst_eth_addr="00:00:00:00:07:03", switch_port=1)


    #writeBalancingEntry(p4info_helper, ingress_sw=switches['s7'], dst_ip_addr="10.0.1.0", ecmp_base=1, ecmp_count=2 , prefix_size=24)

    #back to the border switch
    writeFknEgress(p4info_helper, switches["s1"], "10.0.1.1", "00:00:00:00:01:01", 1)
    writeFknEgress(p4info_helper, switches["s1"], "10.0.1.5", "00:00:00:00:01:05", 3)
    writeFknEgress(p4info_helper, switches["s1"], "10.0.1.4", "00:00:00:00:01:04", 2)
    

    # TODO Uncomment the following two lines to read table entries from s1 and s2
    readTableRules(p4info_helper, switches["s1"])
    readTableRules(p4info_helper, switches["s2"])
    readTableRules(p4info_helper, switches["s5"])
    readTableRules(p4info_helper, switches["s7"])
    readTableRules(p4info_helper, switches["s4"])
    readTableRules(p4info_helper, switches["s3"])

    # polling information # could be dynamic
    # Print the tunnel counters every 2 seconds
    '''
    try:
        while True:
            sleep(2)
            print '\n----- Reading tunnel counters -----'
            printCounter(p4info_helper, s1, "MyIngress.ingressTunnelCounter", 1)
            printCounter(p4info_helper, s1, "MyIngress.transientTunnelCounter", 1)
            printCounter(p4info_helper, s1, "MyEgress.egressCounter", 1)
            printCounter(p4info_helper, s4, "MyIngress.transientTunnelCounter", 1)
            printCounter(p4info_helper, s4, "MyEgress.egressCounter", 1)
            printCounter(p4info_helper, s1, "MyIngress.egressTunnelCounter", 1)
    except KeyboardInterrupt:
        print " Shutting down."
    '''

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=False,
                        default='./build/advanced_tunnel.p4info')
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=False,
                        default='./build/advanced_tunnel.json')
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print "\np4info file not found: %s\nHave you run 'make'?" % args.p4info
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print "\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json
        parser.exit(1)

    main(args.p4info, args.bmv2_json)
