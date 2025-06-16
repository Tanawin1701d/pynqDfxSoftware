from pynq import Overlay  # import the overlay
from pynq import allocate  # import for CMA (contingeous memory allocation)
from pynq import DefaultIP  # import the ip connector library for extension
import copy



class Decoupler(DefaultIP):

    grps = dict()

    dcid = 0 # this is shared decoupler id

    def __init__(self, description):
        super().__init__(self, description= description)
        Decoupler.dcid = Decoupler.dcid + 1

    bindto = ['xilinx.com:ip:dfx_decoupler:1.0']

    def decup(self):
        self.write(0x0, 1)

    def recup(self):
        self.write(0x0, 0)

    def isDecup(self):
        return self.read(0x0)

    def setGrp(self, name: str):
        if name not in Decoupler.grps:
            Decoupler.grps[name] = list()
        Decoupler.grps[name].append(self)



DEFAULT_DECUP_GRP_NAME = "DEFAULT_DGN"
DCP_GRP_SET_MESG       = "the decouple group is not set yet please set the decouple group first"

class MyCusHLS(DefaultIP):  #### base driver for add/sub


    def __init__(self, description):
        super().__init__(description=description)
        self.dcpGrpName  = DEFAULT_DECUP_GRP_NAME
        self.relatedDcp  = list()
        self.autoDcpRecup   = False # stand for decouple_RECOUPLE
        self.autoDcpDecup   = False # stand for decouple_DECOUPLE



    def setAPtr(self, phyAddress):
        self.prepareOp()
        print("writing A address")
        self.write(0x10, phyAddress)
        self.write(0x14, 0)

    def setBPtr(self, phyAddress):
        self.prepareOp()
        print("writing B address")
        self.write(0x1c, phyAddress)
        self.write(0x20, 0)

    def start(self):
        self.prepareOp()
        print("start Address")
        self.write(0x00, 1)

    def decups(self):
        if not self.isDcpGrpSet():
            raise Exception(DCP_GRP_SET_MESG)
        for dcp in self.relatedDcp:
            dcp.decup()

    def recups(self):
        if not self.isDcpGrpSet():
            raise Exception(DCP_GRP_SET_MESG)
        for dcp in self.relatedDcp:
            dcp.recup()


    def rejectHardware(self):
        if (not self.isDcpGrpSet()):
            raise Exception(DCP_GRP_SET_MESG)
        passStatus = self.isAllDcpDecup()

        if self.autoDcpDecup:
            self.decups()
            passStatus = True

        if not passStatus:
            raise Exception("The decouple is not DEcouple properly, all command to this ip will be rejected")



    ##### this function should be used before PS interract with ip
    def prepareOp(self):
        # check dcp is set correctly
        if (not self.isDcpGrpSet()):
            raise Exception("the decouple group is not set yet please set the decouple group first")
        passStatus = self.isAllDcpRecup()

        if self.autoDcpRecup:
            self.recups()
            passStatus = True

        if not passStatus:
            raise Exception("The decouple is not REcouple properly, all command to this ip will be rejected")

    ##### set status, related dcp will be auto recouple when there is any operation
    def setAutoDcpRecup(self, status: bool):
        self.autoDcpRecup = status

    def setAutoDcpDecup(self, status: bool):
        self.autoDcpDecup = status

    def isDcpGrpSet(self):
        return self.dcpGrpName != DEFAULT_DECUP_GRP_NAME

    def setdcpGrp(self, grpName:str, decouplers: list):
        if self.isDcpGrpSet():
            raise Exception("group of this HLS IP is set, you cannot change its grp")
        preDcpList = [(not isinstance(dcp, Decoupler)) for dcp in decouplers]
        if (any(preDcpList)):
            print(preDcpList)
            raise Exception("there is class or obj in decouplers that is mismatch type")

        self.dcpGrpName = grpName
        self.relatedDcp = copy.copy(decouplers)

        for dcp in self.relatedDcp:
            dcp.setGrp(grpName)

    def isAllDcpRecup(self):
        return [(not dcp.isDecup()) for dcp in self.relatedDcp]

    def isAllDcpDecup(self):
        return [(not dcp.isRecup()) for dcp in self.relatedDcp]
