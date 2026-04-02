OPENQASM 2.0;
include "qelib1.inc";

gate cswap a,b,c {
    cx c,b;
    ccx a,b,c;
    cx c,b;
}

qreg q[5];
creg c[5];

x q[0];
h q[4];

measure q[4] -> c[0];
reset q[4];

h q[4];
cx q[4],q[2];
cx q[4],q[0];

if(c[0]==1) u1(pi/2) q[4];

h q[4];
measure q[4] -> c[1];
reset q[4];

h q[4];

cswap q[4],q[1],q[0];
cswap q[4],q[2],q[1];
cswap q[4],q[3],q[2];

cx q[4],q[3];
cx q[4],q[2];
cx q[4],q[1];
cx q[4],q[0];

if(c[1]==1) u1(pi/2) q[4];

h q[4];
measure q[4] -> c[2];