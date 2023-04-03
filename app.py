
from flask import Flask, render_template
from pysnmp.hlapi import *

app = Flask(__name__)

community_string = "public"
ip_address = "192.168.0.1"


@app.route('/')
def index():
    info = {
        'ip_address': '192.168.0.1',
        'mac_address': getMacAddress(),
        'ram': getRAMUtilization(),
        'cpu': getCPUDetails()
    }
     
    return render_template('index.html', data=info)
    

def getMacAddress():
    oid = ".1.3.6.1.2.1.2.2.1.6.2"

    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community_string),
               UdpTransportTarget((ip_address, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    )

    if errorIndication:
        return "Error: " + errorIndication
    elif errorStatus:
        return "Error: " + errorStatus.prettyPrint()
    else:       
        mac_address =':'.join([hex(x)[2:].zfill(2) for x in varBinds[0][1]])
        return mac_address

def getRAMUtilization():
    # OID for total RAM
    total_ram_oid = "1.3.6.1.4.1.2021.4.5.0"
    # OID for used RAM
    used_ram_oid = "1.3.6.1.4.1.2021.4.6.0"
    
    # Get total RAM
    errorIndication, errorStatus, errorIndex, total_ram = next(
        getCmd(SnmpEngine(),
               CommunityData(community_string),
               UdpTransportTarget((ip_address, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(total_ram_oid)))
    )
    
    if errorIndication:
        return "Error: " + errorIndication
    elif errorStatus:
        return "Error: " + errorStatus.prettyPrint()
    
    # Get used RAM
    errorIndication, errorStatus, errorIndex, used_ram = next(
        getCmd(SnmpEngine(),
               CommunityData(community_string),
               UdpTransportTarget((ip_address, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(used_ram_oid)))
    )
    
    if errorIndication:
        return "Error: " + errorIndication
    elif errorStatus:
        return "Error: " + errorStatus.prettyPrint()
    
    # Calculate memory usage
    total_ram = int(total_ram[0][1])
    used_ram = int(used_ram[0][1])
    memory_percentage = (used_ram / total_ram) * 100
    return {"used_ram": int(used_ram/1024), "total_ram": int(total_ram/1024), "memory_percentage": int(memory_percentage)}


def getCPUDetails():
    # SNMP OIDs for CPU load
    # CPU utilization This OID refers to the CPU utilization of a network device, 
    # which indicates the percentage of time the CPU is busy processing data.
    oid1 = "1.3.6.1.4.1.2021.11.11.0" 

    # ssCpuUser This OID refers to the amount of CPU time utilized by user processes on a network device.
    oid2 = '1.3.6.1.4.1.2021.11.50.0' 

    # ssCpuSystem This OID refers to the amount of CPU time utilized by system processes on a network device.
    oid3 = '1.3.6.1.4.1.2021.11.52.0'

    # ssCpuIdle This OID refers to the amount of CPU time that is idle or not being utilized on a network device. 
    # It is the opposite of CPU utilization, indicating the percentage of time the CPU is not busy processing data.

    oid4 = '1.3.6.1.4.1.2021.11.53.0' 

    errorIndication, errorStatus, errorIndex, var_binds = next(
        getCmd(SnmpEngine(),
               CommunityData(community_string),
               UdpTransportTarget((ip_address, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid1)),
               ObjectType(ObjectIdentity(oid2)),
               ObjectType(ObjectIdentity(oid3)),
               ObjectType(ObjectIdentity(oid4)),
               ))

    if errorIndication:
        return "Error: " + errorIndication
    elif errorStatus:
        return "Error: " + errorStatus.prettyPrint()
    else:
        # Parse the CPU load information from the SNMP response
        cpu_utilisation = int(var_binds[0][1].prettyPrint())
        user_load = int(var_binds[1][1].prettyPrint())
        system_load = int(var_binds[2][1].prettyPrint())
        idle_load = int(var_binds[3][1].prettyPrint())
    
        # Return the CPU load information as a dictionary
        return {
            'cpu_utilisation': cpu_utilisation,   
            'user_load': user_load,
            'system_load': system_load,
            'idle_load': idle_load,
        }