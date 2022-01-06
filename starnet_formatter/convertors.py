from decimal import Decimal

def gons_to_degress(gons):
    """Function that converts 
    gons to decimal degrees"""
    return Decimal(gons) * Decimal(0.9)

def degress_to_dms(dd):
    """Fucntion that returns a tuple of (Deg, Min, Sec)
    based on positive degrees"""
    mnt,sec = divmod(dd*3600,60)
    deg,mnt = divmod(mnt,60)
    return int(deg), int(mnt),sec
    
def gons_to_dms(gons):
    """Function that returns a tuple of 
    (D
    eg, Min, Sec) based on deciaml gon"""
    return degress_to_dms(
        gons_to_degress(gons)
    )
  
def dms_to_str(dms, places=2):
    """Function that returns a dms tuple
    to a string"""
    # Horrible need to refactor
    deg = dms[0]
    if deg < 10:
        deg = '0'+'0'+ str(deg)
    elif deg < 100:
        deg = '0' + str(deg)
    else:
        deg = str(deg)
    
    m = dms[1]
    if m < 10:
        m = '0' + str(m)
    else:
        m = str(m)
    
    s = dms[2]
    if s < 10:
        s = '0' + '{m:.{places}f}'.format(m=s, places=places)
    else:
        s = '{m:.{places}f}'.format(m=s, places=places)

    return  deg +'-'+ m +'-'+ s

def gons_to_dms_str(gons, places=2):
    return dms_to_str(gons_to_dms(gons), places)
