
"""
The purpose of this module is to create a 1:1 split horizon IP mapping
that will map external IPs to RFC-1918 IPs.  This would be a replacement
for split horizon DNS that would work in a dynamic fashion.
"""

from ConfigParser import SafeConfigParser
from fnmatch import fnmatch
import os , socket

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

CONFIG_SEARCH.append('/home/jay/sandbox/ub-split-map/ub-split-map.ini')

class Globals(object):
    conf = None

class MyConfigParser(SafeConfigParser):
    """
    Subclass to make some particular lookups easier
    """
    # This is a cached set of the domainSections
    __domSections = None
    # This is cached version of previously matched domains and their
    # section names
    prevMatches = {}

    def getDomSections(self):
        """
        Returns a list of the of the domain sections and caches them in
        the domSections class variable once found
        """
        if self.__domSections is not None:
            return self.__domSections
        self.__domSections = set()
        toSkip = set(['main' , 'maps'])
        for s in self.sections():
            if s not in toSkip:
                self.__domSections.add(s)
        return self.__domSections

    def qnameMatch(self , qname):
        """
        Based on the qname, returns the dictionary of matches for a
        particular query name

        qname:str       The domain query name

        returns:dict
        """
        if self.get('main' , 'scan_type') == 'all':
            # Just return the maps section if we are scanning all
            return dict(self.items('maps'))
        # Check to see if this qname has matched previously
        if qname in self.prevMatches:
            return dict(self.items(self.prevMatches[qname]))
        # Check the qname vs all the section headings
        sects = self.getDomSections()
        for s in sects:
            if fnmatch(qname , s):
                # Cache it and return the results
                self.prevMatches[qname] = s
                return dict(self.items(s))
        return None

def getConf():
    conf = MyConfigParser()
    conf.read(CONFIG_SEARCH)
    return conf

def unpackIP(strIP):
    """
    Converts the packed wire IP to a dotted quad.  The first 2 bytes of the
    string passed in are the short representing the length
    """
    return socket.inet_ntoa(strIP[2:])

def processRRSets(qstate , qname , ipMap):
    msg = DNSMessage(qstate.qinfo.qname_str , RR_TYPE_A , RR_CLASS_IN ,
        PKT_QR | PKT_RA)
    rep = qstate.return_msg.rep
    for i in xrange(rep.an_numrrsets):
        if rep.rrsets[i].rk.type_str == 'A':
            # Only want the A records
            data = rep.rrsets[i].entry.data
            for j in xrange(data.count):
                ip = unpackIP(data.rr_data[j])
                if ip in ipMap:
                    # We have a match to replace
                    msg.answer.append('%s %d IN A %s' % (qname , 
                        data.rr_ttl[j] , ipMap[ip]))
                    modified = True
                else:
                    msg.answer.append('%s %d IN A %s' % (qname ,
                        data.rr_ttl[j]  , ip))
    if not msg.set_return_msg(qstate):
        raise ModuleError('Can\'t set the return message')                   

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
        # Check to see that an A record was queried (all that is supported
        # for now)
        if qstate.qinfo.qtype_str != 'A':
            qstate.ext_state[mid] = MODULE_FINISHED
            return True
        # If we get here, we are going to see if we have a match
        qn = qstate.qinfo.qname_str.rstrip('.')
        match = conf.qnameMatch(qn)
        if not match:
            # We don't have to do anything more, set finished and return
            qstate.ext_state[mid] = MODULE_FINISHED
            return True
        try:
            # Time to modify the IPs that were returned
            invalidateQueryInCache(qstate , qstate.return_msg.qinfo)
            processRRSets(qstate , qn , match)
            storeQueryInCache(qstate , qstate.return_msg.qinfo ,
                qstate.return_msg.rep , 0)
        except Exception , e:
            log_err('An error occurred during modification: %s' % e)
            qstate.ext_state[mid] = MODULE_ERROR
            return False
    qstate.ext_state[mid] = MODULE_FINISHED
    return True
