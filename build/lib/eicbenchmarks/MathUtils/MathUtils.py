import math

def ThetaToEta(theta):

    return -1 * math.log(math.tan(theta / 2))

def EtaToTheta(eta):

    return 2 * math.atan(math.exp(-1 * eta))

