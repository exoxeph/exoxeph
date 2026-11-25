# A tiny isometric camera, the same projection as the Bench stages and the dev room on exoxeph.github.io:
# 30 degrees of elevation and a negative azimuth, so every box shows its top, its front (+y) and its left end
# (-x), drawn in three tones. Boxes further along x and further back in y must be drawn first.
import math


class Camera:
    def __init__(self, ox, oy, s, az=-30):
        a, e = math.radians(az), math.pi / 6
        self.ox, self.oy, self.s = ox, oy, s
        self.ca, self.sa, self.se, self.ce = math.cos(a), math.sin(a), math.sin(e), math.cos(e)

    def at(self, x, y, z=0.0):
        return (self.ox + self.s * (x * self.ca - y * self.sa),
                self.oy + self.s * self.se * (x * self.sa + y * self.ca) - self.s * self.ce * z)

    def pts(self, lst):
        return " ".join(f"{px:.1f},{py:.1f}" for px, py in (self.at(*p) for p in lst))

    def prism(self, x0, y0, z0, x1, y1, z1, top, front, end, stroke=None, sw=0.6):
        st = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"' if stroke else ""
        e = self.pts([(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)])
        f = self.pts([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)])
        t = self.pts([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)])
        return (f'<polygon points="{e}" fill="{end}"{st}/><polygon points="{f}" fill="{front}"{st}/>'
                f'<polygon points="{t}" fill="{top}"{st}/>')

    def quad(self, lst, fill, extra=""):
        return f'<polygon points="{self.pts(lst)}" fill="{fill}" {extra}/>'
