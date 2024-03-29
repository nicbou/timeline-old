import math


def dms_to_decimal(dms, ref):
    degrees = dms[0]
    minutes = dms[1] / 60.0
    seconds = dms[2] / 3600.0
    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds

    decimal = round(degrees + minutes + seconds, 5)
    if math.isnan(decimal):
        raise ValueError
    return decimal