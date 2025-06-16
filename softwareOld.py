# import the library
from pynq import Overlay  # import the overlay
from pynq import allocate  # import for CMA (contingeous memory allocation)
from pynq import DefaultIP  # import the ip connector library for extension


class Decoupler(DefaultIP):  ##### driver for all decoupler
    def __init__(self, description):
        super().__init__(description=description)

    bindto = ['xilinx.com:ip:dfx_decoupler:1.0']

    def decup(self):
        self.write(0x0, 1);

    def recup(self):
        self.write(0x0, 0);


class MyCusHLS(DefaultIP):  #### base driver for add/sub
    def __init__(self, description):
        super().__init__(description=description)

    def setAPtr(self, phyAddress):
        print("writing A address")
        self.write(0x10, phyAddress);
        self.write(0x14, 0);

    def setBPtr(self, phyAddress):
        print("writing B address")
        self.write(0x1c, phyAddress);
        self.write(0x20, 0);

    def start(self):
        self.write(0x00, 1)


class CusAdd(MyCusHLS):  #### add driver
    bindto = ['xilinx.com:hls:cusAdder:1.0']

    def __init__(self, description):
        super().__init__(description=description)


class CusSub(MyCusHLS):  #### subtract driver
    bindto = ['xilinx.com:hls:cusSub:1.0']

    def __init__(self, description):
        super().__init__(description=description)


#### import overlay (main bit stream file)
overlay = Overlay('/home/xilinx/jupyter_notebooks/dfx0/system.bit')
help(overlay)

##### define the static block
prResetBlock = overlay.axi_gpio_0
deco0 = overlay.dfx_decoupler_0
deco1 = overlay.dfx_decoupler_1

# start reconfig

##### reset the reconfigurable block, it is negative edge clock reset
prResetBlock.write(0, 0)

##### decouple
deco0.decup()
deco1.decup()

##### load partial reconfiguration module
overlay.par0.download("/home/xilinx/jupyter_notebooks/dfx0/adder.bit")
help(overlay.par0)

#### recouple the module
deco0.recup()
deco1.recup()

#### release the reset signal (active low)
prResetBlock.write(0, 1)

help(overlay.par0)

#### get custom ip
cusAdder = overlay.par0.cusAdder_0

#### allocate data for the ip (CMA)
input_A = allocate(shape=(1024,), dtype='int32')
input_B = allocate(shape=(1024,), dtype='int32')
for i in range(50):
    input_A[i] = i + 1
    input_B[i] = i

#### flush (evict from cache)
input_A.flush()
input_B.flush()

print(input_A[:55])
print(input_B[:55])
print("input A phyAddress is ", hex(input_A.physical_address))
print("input B phyAddress is ", hex(input_B.physical_address))

###### set address to the partial ip
cusAdder.setAPtr(input_A.physical_address)
cusAdder.setBPtr(input_B.physical_address)

##### start add
cusAdder.start()

##### invalidate any data in cache
input_A.invalidate()

print("output is ", input_A[0: 55])

# start reconfig the subtractor

##### reset the block, it is negative edge clock reset
prResetBlock.write(0, 0)

##### decouple
deco0.decup()
deco1.decup()

##### write the partial bit stream for sub
overlay.par0.download("/home/xilinx/jupyter_notebooks/dfx0/sub.bit")
help(overlay.par0)

deco0.recup()
deco1.recup()

prResetBlock.write(0, 1)

cusSub = overlay.par0.cusSub_0

input_A = allocate(shape=(1024,), dtype='int32')
input_B = allocate(shape=(1024,), dtype='int32')
for i in range(50):
    input_A[i] = i + 1
    input_B[i] = i

input_A.flush()
input_B.flush()

print(input_A[:55])
print(input_B[:55])
print("input A phyAddress is ", hex(input_A.physical_address))
print("input B phyAddress is ", hex(input_B.physical_address))

cusSub.setAPtr(input_A.physical_address)
cusSub.setBPtr(input_B.physical_address)

cusSub.start()

input_A.invalidate()

print("output is ", input_A)
