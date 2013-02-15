
"""
The purpose of this module is to create a 1:1 split horizon IP mapping
that will map external IPs to RFC-1918 IPs.  This would be a replacement
for split horizon DNS that would work in a dynamic fashion.
"""

#
# Unbound hooks
#
def init(mid , cfg):
    """
    Called upon initialization
    """
    return True

def deinit(mid):
    """
    Called at shutdown
    """
    return True

def inform_super(mid , qstate , superqstate , qdata):
    return True

def operate(mid , event , qstate , qdata):
    return True
