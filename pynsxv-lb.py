### Modify existing LB
### VMworld NET 7514

import ConfigParser
from nsxramlclient.client import NsxClient
from pynsxv.library.nsx_logical_switch import *
from pynsxv.library.nsx_dlr import *
from pynsxv.library.nsx_esg import *
from pynsxv.library.nsx_dfw import *
from pynsxv.library.nsx_lb import *
from pynsxv.library.libutils import *

# Path for Windows
# nsxraml_file = 'c:\\nsxraml\\nsxvapi.raml'
# Path for Linux
nsxraml_file = 'library/api_spec/nsxvapi.raml'

# Read nsx.ini file
config = ConfigParser.ConfigParser()
config.read("nsx.ini")
nsxmanager = config.get('nsxv', 'nsx_manager'); nsx_username = config.get('nsxv', 'nsx_username'); nsx_password = config.get('nsxv', 'nsx_password')
vcenter = config.get('vcenter', 'vcenter'); vcenter_user = config.get('vcenter', 'vcenter_user'); vcenter_passwd = config.get('vcenter', 'vcenter_passwd')
transport_zone = config.get('defaults', 'transport_zone')
datacenter_name = config.get('defaults', 'datacenter_name'); edge_datastore = config.get('defaults', 'edge_datastore'); edge_cluster = config.get('defaults', 'edge_cluster')
# Collect vCenter MoID information
vccontent = connect_to_vc(vcenter, vcenter_user, vcenter_passwd)
datacentermoid = get_datacentermoid(vccontent, datacenter_name)
datastoremoid = get_datastoremoid(vccontent, edge_datastore)
resourcepoolid = get_edgeresourcepoolmoid(vccontent, edge_cluster)

# Connection to NSX-v Manager
client_session = NsxClient(nsxraml_file, nsxmanager, nsx_username,nsx_password, debug=False)
print ('Connection to NSX-v Manager')

esg_name = 'edge01'
# Configure Load Balancing
### Enable Load Balancing on the Edge
load_balancer(client_session, esg_name, enabled=True)

### Create the LB Application Profile
lb_app_profile = "pynsxv-ap_http"
lb_proto = "HTTP"
add_app_profile(client_session, esg_name, lb_app_profile, lb_proto)

### Create the LB Web Pool
lb_pool_name = "pynsxv-pool_web"
lb_monitor = "default_tcp_monitor"
add_pool(client_session, esg_name, lb_pool_name, monitor=lb_monitor)
add_member(client_session, esg_name, lb_pool_name, "web01", "10.1.1.11", port="80")
add_member(client_session, esg_name, lb_pool_name, "web02", "10.1.1.12", port="80")
print 'LB Pool {} population complete. Protected with {} monitor'.format(lb_pool_name, lb_monitor)

### Create the LB App Pool
lb_pool_name = "pynsxv-pool_app"
lb_monitor = "default_tcp_monitor"
add_pool(client_session, esg_name, lb_pool_name, monitor=lb_monitor)
add_member(client_session, esg_name, lb_pool_name, "app01", "10.1.2.11", port="80")
add_member(client_session, esg_name, lb_pool_name, "app02", "10.1.2.12", port="80")
print 'LB Pool {} population complete. Protected with {} monitor'.format(lb_pool_name, lb_monitor)

### Create the LB App VIP
lb_vip_name = "pynsxv-vip_app"
lb_vip_ip = "172.16.1.6"
lb_vip_port = "80"
esg_cfg_interface(client_session, esg_name, "1", "172.16.1.1", "255.255.255.0", secondary_ips=lb_vip_ip)
add_vip(client_session, esg_name, lb_vip_name, lb_app_profile, lb_vip_ip, lb_proto, lb_vip_port, lb_pool_name)
print 'VIP {} created with {}:{}'.format(lb_vip_name, lb_vip_ip, lb_vip_port)


### Create the LB Web VIP
lb_vip_name = "pynsxv-vip_web"
lb_vip_ip = "192.168.119.151"
lb_vip_port = "80"
#esg_cfg_interface(client_session, esg_name, "0", "192.168.100.150", "255.255.255.0", secondary_ips=lb_vip_ip)
add_vip(client_session, esg_name, lb_vip_name, lb_app_profile, lb_vip_ip, lb_proto, lb_vip_port, lb_pool_name)
print 'VIP {} created with {}:{}'.format(lb_vip_name, lb_vip_ip, lb_vip_port)

print 'LB {} configuration complete'.format(esg_name)

