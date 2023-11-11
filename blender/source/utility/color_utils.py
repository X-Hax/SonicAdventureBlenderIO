def _srgb2lin(s):
    if s <= 0.0404482362771082:
        lin = s / 12.92
    else:
        lin = pow(((s + 0.055) / 1.055), 2.4)
    return lin


def _lin2srgb(lin):
    if lin > 0.0031308:
        s = 1.055 * (pow(lin, (1.0 / 2.4))) - 0.055
    else:
        s = 12.92 * lin
    return s


def linear_to_srgb(color: tuple[float, float, float, float]):
    if len(color) == 4:
        return (
            _lin2srgb(color[0]),
            _lin2srgb(color[1]),
            _lin2srgb(color[2]),
            color[3])
    else:
        return (
            _lin2srgb(color[0]),
            _lin2srgb(color[1]),
            _lin2srgb(color[2]))


def srgb_to_linear(color: tuple[float, float, float, float]):
    if len(color) == 4:
        return (
            _srgb2lin(color[0]),
            _srgb2lin(color[1]),
            _srgb2lin(color[2]),
            color[3])
    else:
        return (
            _srgb2lin(color[0]),
            _srgb2lin(color[1]),
            _srgb2lin(color[2]))
