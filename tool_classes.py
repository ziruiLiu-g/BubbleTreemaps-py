import math


class Vec2:
    def __init__(self,x ,y):
        self.x = x
        self.y = y

    def distance(self, vec):
        deltaX = self.x - vec.x
        deltaY = self.y - vec.y
        return math.sqrt((deltaX * deltaX) + (deltaY * deltaY))

    def sub(self, vec):
        return Vec2(self.x - vec.x, self.y - vec.y)

    def add(self, vec):
        return Vec2(self.x + vec.x, self.y + vec.y)

    def scale(self, scale):
        return Vec2(self.x * scale, self.y * scale)

    def angle(self, vec):
        result = math.atan2(vec.y, vec.x) - math.atan2(self.y, self.x)
        if result < 0:
            result += 2 * math.pi
        return result

    def magnitude(self):
        return math.sqrt((self.x * self.x) + (self.y * self.y))

    def toUnitVector(self):
        return self.scale(1.0/self.magnitude())


class Arc:
    def __init__(self, x, y, startAngle, endAngle, radius):
        self.center = Vec2(x,y)
        self.startAngle = startAngle
        self.endAngle = endAngle
        self.radius = radius

class ArcGen:
    def __init__(self, startAngle, endAngle, innerRadius, outerRadius):
        self.startAngle = startAngle
        self.endAngle = endAngle
        self.innerRadius = innerRadius
        self.outerRadius = outerRadius

class Circle:
    def __init__(self, x, y, radius):
        self.center = Vec2(x, y)
        self.radius = radius

    def intersects(self, circle):
        distance = self.center.distance(circle.center)

        if distance > self.radius + circle.radius:
            return False
        if distance < abs(self.radius - circle.radius):
            return False
        return True

    def intersectionPoints(self, circle):
        p0 = self.center
        p1 = circle.center

        d = self.center.distance(circle.center)
        a = (self.radius * self.radius - circle.radius * circle.radius + d * d) / (2 * d)
        h = math.sqrt(self.radius * self.radius - a * a)

        p2 = p1.sub(p0).scale(a/d).add(p0)

        x3 = p2.x + h * (p1.y - p0.y) / d
        y3 = p2.y - h * (p1.x - p0.x) / d
        x4 = p2.x - h * (p1.y - p0.y) / d
        y4 = p2.y + h * (p1.x - p0.x) / d

        return [Vec2(x3, y3), Vec2(x4, y4)]