def hex_to_rgb(hex)->tuple:
    hex = hex.lstrip('#')
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
    
def rgb_to_hex(rgb:tuple)->str:
    hex = "#{:02X}{:02X}{:02X}".format(*rgb[:3])
    if len(rgb) == 4:
        hex += f"{int(rgb[3]*256):02X}"
    return hex 
    
def rgb_to_cmyk(r, g, b)->tuple:
    r, g, b = r / 255, g / 255, b / 255

    k = 1 - max(r, g, b)
    if k == 1:
        c, m, y = 0, 0, 0
    else:
        c = (1 - r - k) / (1 - k)
        m = (1 - g - k) / (1 - k)
        y = (1 - b - k) / (1 - k)

    return c, m, y, k