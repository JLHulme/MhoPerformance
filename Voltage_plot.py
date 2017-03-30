#Required imports
import math
import matplotlib.pyplot as plt
#Create time vector, in terms of samples, for a time period of 30cycles
length = 30     #cycles
sampleRate = 4  # samples per cycle
time = []
#create global definition for a
deg120 = (math.pi/180) * 120
a = math.cos(deg120)+math.sin(deg120)*1j

for x in range(sampleRate*length):
    time.append(x/4.0)

#Define function for voltage memory
class V_Mem:
    vMem = complex(0+0j)
    vMemN2 = complex(0+0j)
    vMemN1 = complex(0+0j)
    def __init__(self, startVoltage):
        self.vMem = startVoltage
        self.vMemN1 = startVoltage
        self.vMemN2 = startVoltage

    def updateVoltage(self, currentVoltage):
        self.vMemN2 = self.vMemN1
        self.vMemN1 = self.vMem
        self.vMem = (1.0/16.0)*currentVoltage + (15.0/16.0)*self.vMemN2 #+ instead of - as we dont update measured phasor

    def getVoltage(self):
        return self.vMem

#create a class for to use as a Mho object
class Phase_Mho:
    #v1Mem = V_Mem
    #Z1L
    #mho

    def __init__(self, initialV1Mem, lineZ1):
        self.v1Mem = V_Mem(initialV1Mem)
        self.Z1L = lineZ1

    def update(self, V1Fault, IA, IB):
        #fault values = [v1Mem, IA, IB]
        self.v1Mem.updateVoltage(V1Fault)
        #print(faultValues)
        currentV1Mem = self.v1Mem.getVoltage()
        #print(currentV1Mem)
        VA = V1Fault                 #V1F
        VB = (a**2) * V1Fault        #V1F@-120
        VAB = VA - VB
        IAB = IA - IB
        VPolA = currentV1Mem
        VPolB = currentV1Mem * (a**2)
        VPolAB = VPolA - VPolB
        #print(VAB)
        #print(VA)
        #print(VB)
        torqNum = VAB * VPolAB.conjugate()
        #print(torqNum.real)
        torqDen = VPolAB.conjugate() * IAB * (self.Z1L / abs(self.Z1L))
        #print(torqDen.real)
        self.mho = torqNum.real / torqDen.real
        #print(self.mho)

    def getMho(self):
        return self.mho

    def getVMem(self):
        return self.v1Mem.getVoltage()

#Simulation vlaues
#Prefault voltage
V1 = 230000/math.sqrt(3)    #VLN
#Fault values:
IA = 568.2-2673j            #2733@-78
IB = -2599+844.5j           #2733@162
V1F = 4173-11464j           #12200@-70
lineImp = 0.0843+0.817j     #0.82@84.1
#in secondary values
PTR = 2000
CTR = 400
IA = IA / CTR
IB = IB / CTR
V1F = V1F / PTR
V1 = V1 / PTR
lineImp = lineImp * CTR / PTR

#create relay mho obj
rlyMho = Phase_Mho(V1, lineImp)

#simulate
rlyImpedance = []
rlySetting = []
rlyVMem = []
vtest = []
zone2_setting = 0.53
for t in time:
    rlyMho.update(V1F, IA, IB)
    rlyImpedance.append(rlyMho.getMho())
    rlySetting.append(zone2_setting)
    v = rlyMho.getVMem()
    vtest.append(v)
    rlyVMem.append(abs(v))

#plot
plt.plot(time, rlyVMem , 'b', label="V1MEM")
#plt.plot(time, rlySetting, 'r--', label="Trip Setting")
#plt.axvline(3.5, color='k', linestyle='--', label="3.5cy")
#plt.axvline(5.5, color='b', linestyle='--', label="5.5cy")
plt.xlabel('Time (cycles)')
plt.ylabel('Measured Voltage (Vsec)')
plt.legend(shadow=True, loc=4)
plt.show()
