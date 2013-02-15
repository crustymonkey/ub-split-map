== About ==
The purpose of this module is to create a 1:1 split horizon IP mapping
that will map external IPs to RFC-1918 IPs.  This would be a replacement
for split horizon DNS that would work in a dynamic fashion.

For example, if you had an A record for "www.example.com" that pointed to
an external IP address of 1.2.3.4 that mapped to a web server on your 
192.168.0.10 on your internal network.  Normally you would have to set 
up an internal DNS server to return the 192.168.0.10 address as you wouldn't
be able to route to the 1.2.3.4 address.
