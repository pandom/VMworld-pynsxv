import os


a = 0
while a < 10:
    print "Creating Logical Switch VMworld-pynsxv-%s" %
    os.system("pynsxv lswitch create -n VMworld-pynsxv-$s" % a)
    a = a + 1
