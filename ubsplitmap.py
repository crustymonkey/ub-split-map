
"""
The purpose of this module is to create a 1:1 split horizon IP mapping
that will map external IPs to RFC-1918 IPs.  This would be a replacement
for split horizon DNS that would work in a dynamic fashion.
"""

from ConfigParser import SafeConfigParser
import os

CONFIG_SEARCH = [
    '/etc/ub-split-map.ini' ,
    '/etc/unbound/ub-split-map.ini' ,
    '/usr/local/etc/ub-split-map.ini' ,
    '/usr/local/etc/unbound/ub-split-map.ini' ,
]

if 'HOME' in os.environ:
    CONFIG_SEARCH.extend([
        os.path.join(os.environ['HOME'] , 'ub-split-map.ini') ,
        os.path.join(os.environ['HOME'] , '/unbound/ub-split-map.ini') ,
    ])

class Globals(object):
    conf = None

def getConf():
    conf = SafeConfigParser()
    conf.read(CONFIG_SEARCH)
    return conf

#
# Unbound hooks
#
def init(mid , cfg):
    """
    Called upon initialization
    """
    Globals.conf = getConf()
    return True

def deinit(mid):
    """
    Called at shutdown
    """
    return True

def inform_super(mid , qstate , superqstate , qdata):
    return True

def operate(mid , event , qstate , qdata):
    conf = Globals.conf
    if event in (MODULE_EVENT_NEW , MODULE_EVENT_PASS):
        qstate.ext_state[mid] = MODULE_WAIT_MODULE
        return True

    if event == MODULE_EVENT_MODDONE:
        if not qstate.return_msg or not qstate.return_msg.rep:
            qstate.ext_state[mid] = MODULE_FINISHED
            return True
        qn = qstate.qinfo.qname_str.rstrip('.')

    return True
