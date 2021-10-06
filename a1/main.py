# Convex hull
#
# Usage: python main.py [-d] file_of_points
#
# You can press ESC in the window to exit.
#
# You'll need Python 3 and must install these packages:
#
#   PyOpenGL, GLFW


import sys, os, math

try: # PyOpenGL
  from OpenGL.GL import *
except:
  print( 'Error: PyOpenGL has not been installed.' )
  sys.exit(0)

try: # GLFW
  import glfw
except:
  print( 'Error: GLFW has not been installed.' )
  sys.exit(0)



# Globals

window = None

windowWidth  = 1000 # window dimensions
windowHeight = 1000

minX = None # range of points
maxX = None
minY = None
maxY = None

r  = 0.01 # point radius as fraction of window size

numAngles = 32
thetas = [ i/float(numAngles)*2*3.14159 for i in range(numAngles) ] # used for circle drawing

allPoints = [] # list of points

lastKey = None  # last key pressed

discardPoints = False

# Point
#
# A Point stores its coordinates and pointers to the two points beside
# it (CW and CCW) on its hull.  The CW and CCW pointers are None if
# the point is not on any hull.
#
# For debugging, you can set the 'highlight' flag of a point.  This
# will cause the point to be highlighted when it's drawn.

class Point(object):

    def __init__( self, coords ):

      self.x = float( coords[0] ) # coordinates
      self.y = float( coords[1] )

      self.ccwPoint = None # point CCW of this on hull
      self.cwPoint  = None # point CW of this on hull

      self.highlight = False # to cause drawing to highlight this point


    def __repr__(self):
      return 'pt(%g,%g)' % (self.x, self.y)


    def drawPoint(self):

      # Highlight with yellow fill
      
      if self.highlight:
          glColor3f( 0.9, 0.9, 0.4 )
          glBegin( GL_POLYGON )
          for theta in thetas:
              glVertex2f( self.x+r*math.cos(theta), self.y+r*math.sin(theta) )
          glEnd()

      # Outline the point
      
      glColor3f( 0, 0, 0 )
      glBegin( GL_LINE_LOOP )
      for theta in thetas:
          glVertex2f( self.x+r*math.cos(theta), self.y+r*math.sin(theta) )
      glEnd()

      # Draw edges to next CCW and CW points.

      if self.ccwPoint:
        glColor3f( 1, 0, 0 )
        drawArrow( self.x, self.y, self.ccwPoint.x, self.ccwPoint.y )

      if self.cwPoint:
        glColor3f( 0, 0, 1 )
        drawArrow( self.x, self.y, self.cwPoint.x, self.cwPoint.y )



# Draw an arrow between two points, offset a bit to the right

def drawArrow( x0,y0, x1,y1 ):

    d = math.sqrt( (x1-x0)*(x1-x0) + (y1-y0)*(y1-y0) )

    vx = (x1-x0) / d      # unit direction (x0,y0) -> (x1,y1)
    vy = (y1-y0) / d

    vpx = -vy             # unit direction perpendicular to (vx,vy)
    vpy = vx

    xa = x0 + 1.5*r*vx - 0.4*r*vpx # arrow tail
    ya = y0 + 1.5*r*vy - 0.4*r*vpy

    xb = x1 - 1.5*r*vx - 0.4*r*vpx # arrow head
    yb = y1 - 1.5*r*vy - 0.4*r*vpy

    xc = xb - 2*r*vx + 0.5*r*vpx # arrow outside left
    yc = yb - 2*r*vy + 0.5*r*vpy

    xd = xb - 2*r*vx - 0.5*r*vpx # arrow outside right
    yd = yb - 2*r*vy - 0.5*r*vpy

    glBegin( GL_LINES )
    glVertex2f( xa, ya )
    glVertex2f( xb, yb )
    glEnd()

    glBegin( GL_POLYGON )
    glVertex2f( xb, yb )
    glVertex2f( xc, yc )
    glVertex2f( xd, yd )
    glEnd()
      
      

# Determine whether three points make a left or right turn

LEFT_TURN  = 1
RIGHT_TURN = 2
COLLINEAR  = 3

def turn( a, b, c ):

    det = (a.x-c.x) * (b.y-c.y) - (b.x-c.x) * (a.y-c.y)

    if det > 0:
        return LEFT_TURN
    elif det < 0:
        return RIGHT_TURN
    else:
        return COLLINEAR


# Build a convex hull from a set of point
#
# Use the method described in class


def buildHull( points ):

    ##### Handle base cases of two or three points #####

    #### build hull with 2 points ####
    if len(points) == 2:
        for i in range(len(points)):
            points[i].ccwPoint = points[(i-1)%len(points)]
            points[i].cwPoint = points[(i-1)]

    #### build hull with 3 points ####
    elif len(points) == 3:
        # check if points (0, 1, 2) form left turn
        if turn(points[0], points[1], points[2]) == 1:
            for i in range(len(points)):
                points[i].ccwPoint = points[(i+1)%len(points)]
                points[i].cwPoint = points[(i-1)]

        # check if points (0, 1, 2) form right turn
        elif turn(points[0], points[1], points[2]) == 2:
            for i in range(len(points)):
                points[i].ccwPoint = points[(i-1)]
                points[i].cwPoint = points[(i+1)%len(points)]
        
        # on piazza, prof. Stewart mentioned that it can be assumed that groups of > 2 points will not be colinear
        # https://piazza.com/class/kt4lblombqn4u2?cid=55
        else:
            print("Error: colinear points")
    
    # Handle recursive case.
    #
    # After you get the hull-merge working, do the following: For each
    # point that was removed from the convex hull in a merge, set that
    # point's CCW and CW pointers to None.  You'll see that the arrows
    # from interior points disappear after you do this.
    #
    # [YOUR CODE HERE]

    #### build hull with > 3 points ####
    else:

        ### split points into two groups and recursively build the hulls for each group ###

        # find index of the middle point in the x-direction
        midIdx = round(len(points)/2)

        # split points into two groups: left of the middle point and right of the middle point
        leftPoints = points[:midIdx]
        rightPoints = points[midIdx:]

        # build the hull for the left group and the right group
        buildHull(leftPoints)
        buildHull(rightPoints)

        ### combine the left hull and the right hull ###

        ## walking upwards ##

        # assign l to the rightmost point in the left group
        l = leftPoints[-1]

        # assign r to the leftmost point in the right group
        r = rightPoints[0]

        # initialize list of middle points (not in hull)
        mid = []

        # check if l or r are in the middle of a left turn
        while (turn(l.ccwPoint, l, r) == 1) or (turn(l, r, r.cwPoint) == 1):
            # if l is in the middle of a left turn: add l to list of middle points and move l ccw
            if turn(l.ccwPoint, l, r) == 1:
                mid.append(l)
                l = l.ccwPoint
            # if r is in the middle of a left turn: add r to list of middle points and move r cw
            elif turn(l, r, r.cwPoint) == 1:
                mid.append(r)
                r = r.cwPoint

        # save the top points of the left and right groups
        ltop = l
        rtop = r

        ## walking downwards ##

        # reassign l and r to edges of hull
        l = leftPoints[-1]
        r = rightPoints[0]
        
        # check if l and r are in the middle of a right turn
        while (turn(l.cwPoint, l, r) == 2) or (turn(l, r, r.ccwPoint) == 2):
            # if l is in the middle of a right turn: add l to list of middle points and move l cw
            if turn(l.cwPoint, l, r) == 2:
                mid.append(l)
                l = l.cwPoint
            # if r is in the middle of a right turn: add r to list of middle points and move r ccw
            elif turn(l, r, r.ccwPoint):
                mid.append(r)
                r = r.ccwPoint

        # save the bottom points of the left and right groups
        lbottom = l
        rbottom = r

        # connect the top points together
        ltop.cwPoint = rtop
        rtop.ccwPoint = ltop

        # connect the bottom points together
        lbottom.ccwPoint = rbottom
        rbottom.cwPoint = lbottom

        # remove top and bottom points from list of middle points
        topbottom = [ltop, lbottom, rtop, rbottom]
        mid = [point for point in mid if point not in topbottom]

        # remove cw and ccw pointers for middle points (points not in hull)
        for point in mid:
            point.cwPoint = None
            point.ccwPoint = None
        

    # You can do the following to help in debugging.  This highlights
    # all the points, then shows them, then pauses until you press
    # 'p'.  While paused, you can click on a point and its coordinates
    # will be printed in the console window.  If you are using an IDE
    # in which you can inspect your variables, this will help you to
    # identify which point on the screen is which point in your data
    # structure.
    #
    # This is good to do, for example, after you have recursively
    # built two hulls, to see that the two hulls look right.
    #
    # This can also be done immediately after you have merged to hulls
    # ... again, to see that the merged hull looks right.
    #
    # Always after you have inspected things, you should remove the
    # highlighting from the points that you previously highlighted.

    for p in points:
        p.highlight = True
    display(wait=True)

    # At the very end of buildHull(), you should display the result
    # after every merge, as shown below.  This call to display() does
    # not pause.
    
    display()

  

windowLeft   = None
windowRight  = None
windowTop    = None
windowBottom = None


# Set up the display and draw the current image

def display( wait=False ):

    global lastKey, windowLeft, windowRight, windowBottom, windowTop
    
    # Handle any events that have occurred

    glfw.poll_events()

    # Set up window

    glClearColor( 1,1,1,0 )
    glClear( GL_COLOR_BUFFER_BIT )
    glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )

    glMatrixMode( GL_PROJECTION )
    glLoadIdentity()

    glMatrixMode( GL_MODELVIEW )
    glLoadIdentity()

    if maxX-minX > maxY-minY: # wider point spread in x direction
        windowLeft = -0.1*(maxX-minX)+minX
        windowRight = 1.1*(maxX-minX)+minX
        windowBottom = windowLeft
        windowTop    = windowRight
    else: # wider point spread in y direction
        windowTop    = -0.1*(maxY-minY)+minY
        windowBottom = 1.1*(maxY-minY)+minY
        windowLeft   = windowBottom
        windowRight  = windowTop

    glOrtho( windowLeft, windowRight, windowBottom, windowTop, 0, 1 )

    # Draw points and hull

    for p in allPoints:
        p.drawPoint()

    # Show window

    glfw.swap_buffers( window )

    # Maybe wait until the user presses 'p' to proceed
    
    if wait:

        sys.stderr.write( 'Press "p" to proceed ' )
        sys.stderr.flush()

        lastKey = None
        while lastKey != 80: # wait for 'p'
            glfw.wait_events()
            display()

        sys.stderr.write( '\r                     \r' )
        sys.stderr.flush()


    

# Handle keyboard input

def keyCallback( window, key, scancode, action, mods ):

    global lastKey
    
    if action == glfw.PRESS:
    
        if key == glfw.KEY_ESCAPE:      # quit upon ESC
            sys.exit(0)
        else:
            lastKey = key



# Handle window reshape


def windowReshapeCallback( window, newWidth, newHeight ):

    global windowWidth, windowHeight

    windowWidth  = newWidth
    windowHeight = newHeight



# Handle mouse click/release

def mouseButtonCallback( window, btn, action, keyModifiers ):

    if action == glfw.PRESS:

        # Find point under mouse

        x,y = glfw.get_cursor_pos( window ) # mouse position

        wx = (x-0)/float(windowWidth)  * (windowRight-windowLeft) + windowLeft
        wy = (windowHeight-y)/float(windowHeight) * (windowTop-windowBottom) + windowBottom

        minDist = windowRight-windowLeft
        minPoint = None
        for p in allPoints:
            dist = math.sqrt( (p.x-wx)*(p.x-wx) + (p.y-wy)*(p.y-wy) )
            if dist < r and dist < minDist:
                minDist = dist
                minPoint = p

        # print point and toggle its highlight

        if minPoint:
            minPoint.highlight = not minPoint.highlight
            print( minPoint )

        
    
# Initialize GLFW and run the main event loop

def main():

    global window, allPoints, minX, maxX, minY, maxY, r, discardPoints
    
    # Check command-line args

    if len(sys.argv) < 2:
        print( 'Usage: %s filename' % sys.argv[0] )
        sys.exit(1)

    args = sys.argv[1:]
    while len(args) > 1:
        print( args )
        if args[0] == '-d':
            discardPoints = not discardPoints
        args = args[1:]

    # Set up window
  
    if not glfw.init():
        print( 'Error: GLFW failed to initialize' )
        sys.exit(1)

    window = glfw.create_window( windowWidth, windowHeight, "Assignment 1", None, None )

    if not window:
        glfw.terminate()
        print( 'Error: GLFW failed to create a window' )
        sys.exit(1)

    glfw.make_context_current( window )
    glfw.swap_interval( 1 )
    glfw.set_key_callback( window, keyCallback )
    glfw.set_window_size_callback( window, windowReshapeCallback )
    glfw.set_mouse_button_callback( window, mouseButtonCallback )

    # Read the points

    with open( args[0], 'rb' ) as f:
      allPoints = [ Point( line.split(b' ') ) for line in f.readlines() ]

    # Get bounding box of points

    minX = min( p.x for p in allPoints )
    maxX = max( p.x for p in allPoints )
    minY = min( p.y for p in allPoints )
    maxY = max( p.y for p in allPoints )

    # Adjust point radius in proportion to bounding box
    
    if maxX-minX > maxY-minY:
        r *= maxX-minX
    else:
        r *= maxY-minY

    # Sort by increasing x.  For equal x, sort by increasing y.
    
    allPoints.sort( key=lambda p: (p.x,p.y) )

    # Run the code
    
    buildHull( allPoints )

    # Wait to exit

    while not glfw.window_should_close( window ):
        glfw.wait_events()

    glfw.destroy_window( window )
    glfw.terminate()
    


if __name__ == '__main__':
    main()
