import xml.etree.ElementTree as ET

def assignDcpToCusIp(overlay, grpInstanceName: str, handOffFilePath: str):

    dcps = getConsecutiveDecoupler(overlay, grpInstanceName, handOffFilePath);

    ipHiracNames = overlay.ip_dict.keys()

    for ipHiracName in ipHiracNames:
        ipHiracNameList = ipHiracName.split("/")
        if grpInstanceName in ipHiracNameList:
            ip = overlay.ip_dict[ipHiracName]['device']
            ip.setdcpGrp(grpInstanceName, list(dcps))




def getConsecutiveDecoupler(overlay, grpInstanceName: str, handOffFilePath: str):

    tree = ET.parse(handOffFilePath)
    root = tree.getroot()

    resultName = set()

    foundParRegion    = False
    foundDfxDecoupler = False

    modules = root.find("MODULES")
    for module in modules.findall('MODULE'):
        curInstName = module.get("INSTANCE")
        if curInstName != grpInstanceName:
            continue

        print("found the blockName " + grpInstanceName)
        foundParRegion = True

        ports = module.find("PORTS")
        for port in ports.findall("PORT"):
            for connection in port.find("CONNECTIONS").findall("CONNECTION"):
                grpInstanceName = connection.get("INSTANCE")
                if "dfx_decoupler" in grpInstanceName:
                    resultName.add(grpInstanceName)
                    foundDfxDecoupler = True


    if not foundParRegion:
        print("warning, we can't found partial region instance, so the decoupler is not set as well")
        return set()

    if not foundDfxDecoupler:
        print("warning, we can't found dfx decoupler region instance, so the decoupler is not set as well")

    return resultName


result = getConsecutiveDecoupler(None, "heir_0","/media/tanawin/tanawin1701e/project6/hardwares/demoDfx/systemTest.hwh")

print(result)