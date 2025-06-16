import xml.etree.ElementTree as ET

def getConsecutiveDecoupler(overlay, instanceName: str, handOffFilePath):

    tree = ET.parse(handOffFilePath)
    root = tree.getroot()

    resultName = set()

    foundParRegion    = False
    foundDfxDecoupler = False

    modules = root.find("MODULES")
    for module in modules.findall('MODULE'):
        curInstName = module.get("INSTANCE")
        if curInstName != instanceName:
            continue

        print("found the blockName " + instanceName)
        foundParRegion = True

        ports = module.find("PORTS")
        for port in ports.findall("PORT"):
            for connection in port.find("CONNECTIONS").findall("CONNECTION"):
                instanceName = connection.get("INSTANCE")
                if "dfx_decoupler" in instanceName:
                    resultName.add(instanceName)
                    foundDfxDecoupler = True


    if not foundParRegion:
        print("warning, we can't found partial region instance, so the decoupler is not set as well")
        return set()

    if not foundDfxDecoupler:
        print("warning, we can't found dfx decoupler region instance, so the decoupler is not set as well")

    return resultName


result = getConsecutiveDecoupler(None, "heir_0","/media/tanawin/tanawin1701e/project6/hardwares/demoDfx/systemTest.hwh")

print(result)