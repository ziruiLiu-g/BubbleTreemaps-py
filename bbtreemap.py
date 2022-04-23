import copy
import Box2D

from Hierarcy import Hierarchy
from tool_classes import *

FLOATINGPOINT_EPSILON = 0.00001


class BubbleTreeMap:
    def __init__(self, data):
        self.padding =  50
        self.curvature = 100
        self.colormap = []
        self.width = 800
        self.height = 800
        self.hierarchyRoot = self.hierarchyRoot(data)
        self.contours = []

    def hierarchyRoot(self, _):
        hierarchyRoot = Hierarchy()
        hierarchyRoot.build(_)
        return hierarchyRoot

    def doLayout(self):
        self.lp(self.hierarchyRoot, self.padding, self.width, self.height)
        return self

    def getContour(self):
        self.contours = self.contourHierarchy(self.hierarchyRoot, self.padding, self.curvature)
        return self.contours

    def doColoring(self):
        colorInd = 0
        childs = self.hierarchyRoot.children
        for c in childs:
            for d in c.descendants():
                d.color = self.colormap[colorInd % len(self.colormap)]
            colorInd += 1

    def contourHierarchy(self, hierarchyRoot, padding, curvature):
        contour = []
        depth = self.hierarchyRoot.height - 1
        while depth >= 0:
            layerClusters = self.getLayerClusters(hierarchyRoot, depth, padding)

            for cluster in layerClusters:
                genedContour = self.contour(cluster['nodes'], curvature)  # c.nodes

                for seg in genedContour:
                    seg['strokeWidth'] = cluster['parent'].uncertainty

                contour += genedContour
            depth -= 1

        return contour

    def contour(self, nodes, curvature):
        circles = []
        for n in nodes:
            circles.append(Circle(n.x, n.y, n.r + n.contourPadding))

        outerCircleRing = self.getOuterCircleRing(circles, curvature)

        arcs = []

        arcs += self.generateCircleArcs(outerCircleRing)
        arcs += self.generateTangentArcs(outerCircleRing, curvature)
        return self.arcsToPaths(arcs)

    def getOuterCircleRing(self, circles, curvature):
        circlesEnlarged = []
        for c in circles:
            circlesEnlarged.append(copy.copy(c))

        for c in circlesEnlarged:
            c.radius += curvature

        leftmostCircleIndex = 0
        i = 1
        while i < len(circlesEnlarged):
            if (circlesEnlarged[i].center.x - circlesEnlarged[i].radius < circlesEnlarged[
                leftmostCircleIndex].center.x - circlesEnlarged[leftmostCircleIndex].radius):
                leftmostCircleIndex = i
            i += 1

        outerCircleRing = []
        index = leftmostCircleIndex
        referenceDirection = Vec2(-1, 0)
        while True:
            intersection = self.getNextClockwiseIntersection(index, circlesEnlarged, referenceDirection)
            if intersection == None:
                break

            index = intersection['circleIndex']
            circle = circles[index]
            referenceDirection = intersection['intersectionPoint'].sub(circle.center)

            if (len(outerCircleRing) > 0 and index == outerCircleRing[
                0]['circleIndex'] and intersection['intersectionPoint'].distance(
                outerCircleRing[0]['intersectionPoint']) < FLOATINGPOINT_EPSILON):
                break

            outerCircleRing.append({
                'circle':circle,
                'intersectionPoint': intersection['intersectionPoint'],
                'circleIndex': index
            })

        return outerCircleRing

    def getNextClockwiseIntersection(self, currentCircleIndex, circleArray, direction):
        currentCircle = circleArray[currentCircleIndex]
        allIntersection = []

        for i in range(len(circleArray)):
            if i != currentCircleIndex:
                if circleArray[i].intersects(circleArray[currentCircleIndex]):
                    intersectionPoints = circleArray[i].intersectionPoints(circleArray[currentCircleIndex])

                    allIntersection.append({
                        'intersectionPoint': intersectionPoints[0],
                        'circleIndex': i
                    })

                    allIntersection.append({
                        'intersectionPoint': intersectionPoints[1],
                        'circleIndex': i
                    })

        smallestAngle = 7
        intersectionWithSmallestAngle = None
        for inters in allIntersection:
            angle = direction.angle(inters['intersectionPoint'].sub(currentCircle.center))
            if angle > FLOATINGPOINT_EPSILON and angle < smallestAngle:
                smallestAngle = angle
                intersectionWithSmallestAngle = inters

        return intersectionWithSmallestAngle

    def generateCircleArcs(self, outerCircleRing):
        arcs = []
        for i in range(len(outerCircleRing)):
            circle = outerCircleRing[i]['circle']
            firstIntersection = outerCircleRing[i]['intersectionPoint']
            secondIntersection = outerCircleRing[(i + 1) % len(outerCircleRing)]['intersectionPoint']

            centerToFirstIntersection = firstIntersection.sub(circle.center)
            centerToSecondIntersection = secondIntersection.sub(circle.center)
            arcStartAngle = Vec2(0, -1).angle(centerToFirstIntersection)
            arcEndAngle = Vec2(0, -1).angle(centerToSecondIntersection)

            arcs.append(Arc(circle.center.x, circle.center.y, arcStartAngle, arcEndAngle, circle.radius))

        return arcs

    def generateTangentArcs(self, outerCircleRing, curvature):
        arcs = []
        for i in range(len(outerCircleRing)):
            intersection = outerCircleRing[i]['intersectionPoint']
            firstCircle = outerCircleRing[i - 1 if i > 0 else len(outerCircleRing) - 1]['circle']
            secondCircle = outerCircleRing[i]['circle']

            intersectionToFirstCenter = firstCircle.center.sub(intersection)
            intersectionToSecondCenter = secondCircle.center.sub(intersection)
            arcEndAngle = Vec2(0, -1).angle(intersectionToFirstCenter)
            arcStartAngle = Vec2(0, -1).angle(intersectionToSecondCenter)

            arcs.append(Arc(intersection.x, intersection.y, arcStartAngle, arcEndAngle, curvature))

        return arcs

    def arcsToPaths(self, arcs):
        path = []

        for arc in arcs:
            startAngleTmp = arc.startAngle
            if startAngleTmp > arc.endAngle:
                startAngleTmp -= 2*math.pi

            path.append({
                'd': ArcGen(startAngleTmp, arc.endAngle, arc.radius, arc.radius),
                'x': arc.center.x,
                'y': arc.center.y
            })

        return path

    def getLayerClusters(self, hierarchyRoot, depth, padding):
        clusters = []
        layerNodes = hierarchyRoot.search_level(depth)

        for node in layerNodes:
            clusterNodes = node.leaves()
            clusterParent = []
            for anc in node.ancestors():
                if anc.level == depth:
                    clusterParent.append(anc)
            clusterParent = clusterParent[0]

            for cnode in clusterNodes:
                path = cnode.path(clusterParent)
                if (len(path) > 2):
                    path = path[1:-1]
                else:
                    path = []

                uncertaintySum = 0
                for p in path:
                    uncertaintySum += p.uncertainty

                contourClusterParentUncertainty = clusterParent.uncertainty / 2
                planckClusterParentUncertainty = 0 if clusterParent == cnode else clusterParent.uncertainty
                interClusterSpacing = 0 if len(clusterNodes) == 1 else padding / 2.0

                cnode.contourPadding = (
                                              cnode.level - clusterParent.level) * padding + uncertaintySum + contourClusterParentUncertainty

                cnode.planckPadding = (
                                             cnode.level - clusterParent.level) * padding + uncertaintySum + planckClusterParentUncertainty + interClusterSpacing


            clusters.append({'nodes': clusterNodes, 'parent': clusterParent})
        return clusters

    def lp(self, hierarchyRoot, padding, width, height):
        layerDepth = self.hierarchyRoot.height - 1
        while layerDepth >= 0:
            layerClusters = self.getLayerClusters(hierarchyRoot, layerDepth, padding)
            pps = []

            for c in layerClusters:
                pps.append(c['parent'].parent)

            for p in pps:
                currentPPClusters = []
                for c in layerClusters:
                    if c['parent'].parent == p:
                        currentPPClusters.append(c)

                circleList = []
                for c in currentPPClusters:
                    circleList += c['nodes']

                centroid = self.getCircleCentroid(circleList)
                self.layoutClusters(currentPPClusters, centroid)
            layerDepth -= 1

    def getCircleCentroid(self, circles):
        circleMassSum = 0
        centroid = Box2D.b2Vec2_zero

        for c in circles:
            circleMass = c.r * c.r * math.pi
            circleMassSum += circleMass
            centroid.x += c.x * circleMass
            centroid.y += c.y * circleMass

        centroid.x *= (1.0 / circleMassSum)
        centroid.y *= (1.0 / circleMassSum)

        return centroid

    def layoutClusters(self, layerClusters, centroid):
        world = Box2D.b2World(gravity=Box2D.b2Vec2(0,0))

        layerClusterBodies  = []
        for c in layerClusters:
            layerClusterBodies.append(self.createClusterBody(c, world))

        attractorBody = world.CreateBody(position = Box2D.b2Vec2(centroid.x, centroid.y))

        for b in layerClusterBodies:
            world.CreateDistanceJoint(frequencyHz=0.9,
                                      length=0,
                                      dampingRatio=0.001,
                                      bodyA=attractorBody,
                                      bodyB=b)

        timestep = 1.0/60.0
        velocityIterations = 6
        positionIterations = 2

        for i in range(1000):
            world.Step(timestep, velocityIterations, positionIterations)

        for body in world.bodies:
            for fixture in body.fixtures:
                if fixture.shape.type == 0:
                    center = body.GetWorldPoint(fixture.shape.pos)
                    rawCircle = fixture.userData
                    rawCircle.x = center.x
                    rawCircle.y = center.y


    def createClusterBody(self, layerCluster, world):
        bodyCentroid = self.getCircleCentroid(layerCluster['nodes'])
        body = world.CreateDynamicBody(position=(bodyCentroid.x, bodyCentroid.y))

        for n in layerCluster['nodes']:
            centerGlobal = Box2D.b2Vec2(n.x, n.y)
            centerLocal = centerGlobal - bodyCentroid
            fixture = Box2D.b2FixtureDef(shape = Box2D.b2CircleShape(pos = centerLocal,radius=n.r + n.planckPadding), density=1.0, friction=0.00001)
            fixture.userData = n
            body.CreateFixture(fixture)

        return body

    def set_padding(self, padding):
        self.padding = padding
        return self

    def set_curvature(self, curvature):
        self.curvature = curvature
        return self

    def set_colormap(self, colormap):
        self.colormap = colormap
        self.doColoring()
        return self

    def set_width(self, width):
        self.width = width
        return self

    def set_height(self, height):
        self.height = height
        return self