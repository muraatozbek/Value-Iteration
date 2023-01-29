from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import time
import random


"""
    Function for printing an 2D array to terminal
"""
def Print2DArray(arr):
    for row in arr:
        print(row)


"""
    Function for reading grid information from a text file
    
    data_type int or float
"""
def ReadGridFromText(file_path, data_type=int):
    data = []
    try:
        with open(file_path, "r") as dosya:
            text = dosya.read().splitlines()
            rowCount, columnCount = map(int, text[0].split())
            for i in range(1, rowCount+1):
                data.append( list(map(data_type, text[i].split())) )
            
    except IOError as e:
        print("Unable to open file ", file_path, ",", e)
        exit(1)
    
    
    return data



"""
    Function for drawing the grid with its statae values
"""
def DrawStateImage(stateValues, occupancyMap, terminalStateMask, numRows, numCols):
    width = 500
    height = 500
    numRows = numRows
    numCols = numCols
    
    dWidth = int(width/numCols)
    dHeight = int(height/numRows)

    #  create empty image
    img = Image.new(mode="RGBA", size=(width, height), color=(255, 255, 255, 255))
    
    #  initialize drawer object
    draw = ImageDraw.Draw(img)

    y_start = 0
    y_end = height
    y_step = int(height / numRows)
    
    x_start = 0
    x_end = width
    x_step = int(width / numCols)


    #  draw horizontal lines
    for y in range(y_start, y_end, y_step):
        line = ((x_start, y), (x_end, y))
        draw.line(line, fill=(0, 0, 0, 255))
    
    #  draw vertical lines
    for x in range(x_start, x_end, x_step):
        line = ((x, y_start), (x, y_end))
        draw.line(line, fill=(0, 0, 0, 255))
    
    #  draw borders expilicity
    bottomLine = ((0, height-1), (width, height-1))
    draw.line(bottomLine, fill=(0, 0, 0, 255))
    rightLine = ((width-1, 0), (width-1, height-1))
    draw.line(rightLine, fill=(0, 0, 0, 255))
    
    
    #  used when drawing rectangles so rectangle does not overlap with border completely
    borderMarginX = 1
    borderMarginY = 1
    
    for rowIndex in range(numRows):
        for colIndex in range(numCols):
            topLeftX = (width/numCols) * colIndex
            topLeftY = (height/numRows) * rowIndex
            #print("({}, {})".format(topLeftX, topLeftY))
            centerX = topLeftX + dWidth/2
            centerY = topLeftY + dHeight/2
            botRightX = topLeftX + dWidth
            botRightY = topLeftY + dHeight
            
            
            #  check if cell is blocked
            if (occupancyMap[rowIndex][colIndex] != 0):
                #  draw a gray rectangle block
                draw.rectangle([topLeftX+borderMarginX, topLeftY+borderMarginY, botRightX-borderMarginX, botRightY-borderMarginY], fill=(127, 127, 127, 255))
            else:
                #  check if state is a terminal state
                if (terminalStateMask[rowIndex][colIndex] != 0):
                    #  terminal state
                    #check whether value of terminal state is positive or negative
                    if (stateValues[rowIndex][colIndex] > 0):
                        #  draw a green rectangle
                        #draw.rectangle([topLeftX+borderMarginX, topLeftY+borderMarginY, botRightX-borderMarginX, botRightY-borderMarginY], fill=(0, 200, 0, 255))
                        pass
                    elif (stateValues[rowIndex][colIndex] < 0):
                        #  draw a blue rectangle
                        #draw.rectangle([topLeftX+borderMarginX, topLeftY+borderMarginY, botRightX-borderMarginX, botRightY-borderMarginY], fill=(0, 0, 200, 255))
                        pass
                else:
                    #  not a terminal state
                    pass
                
                #  draw value of the state
                #draw.text((centerX, centerY), "{:.3f}".format(stateValues[rowIndex][colIndex]), font=ImageFont.truetype("Arial.ttf", 12), fill=(255, 0, 0, 255))
                draw.text((centerX, centerY), "{:.3f}".format(stateValues[rowIndex][colIndex]), font=ImageFont.truetype("LiberationSans-Regular.ttf", 12), fill=(255, 0, 0, 255))

  
    #img.save("q_values_100.png")
    img.show()
    
    return img
















"""
    All 2D grid arrays are row-major. For example:
        currentStateValues[i1][i2] gives you value of the cell at
        position row=i1, column=i2.
        In the given homework files, your grid has 3 rows and 4 columns.

    occupancyMap: 2D array, 1 if cell is occupied (blocked), and 0 if 
        cell is empty. Blocked means your agent can not go through that cell.
    
    currentStateValues: 2D array (of floats), 
        currentStateValues[row][column] corresponds to value of grid
        cell at (row, column).
    
    terminalStateMask: 2D array, 1 if cell is a terminal cell, 0 otherwise.
    
    stepCost: A penalty for each action your agent performs. This penalty
        is applied even if you end up in the same state (like when you 
        try to walk towards a wall or out of bounds).
    
    discountFactor: Discount factor in the Bellman equation, see lecture
        slides for details.
"""
def GridValueIteration(occupancyMap, currentStateValues, terminalStateMask, stepCost=-0.04, discountFactor=1.0):
    #  read dimension information of our grid environment
    rowCount = len(occupancyMap)
    columnCount = len(occupancyMap[0])
    
    #  create an array of zeroes with the same size
    #you will fill this array with new values calculated in this function
    newStateValues = [ [0.0]*columnCount for i in range(rowCount) ]
    
    
    """
        YOUR CODE STARTS BELOW
    """
    directions = {"R": (0, 1), "U": (-1, 0), "L": (0, -1), "D": (1, 0)}

    ###---Finds Terminal States Positions---###
    terminalStateCoordinates = []
    for i in range(rowCount):
        for j in range(columnCount):
            if terminalStateMask[i][j] == 1:
                    terminalStateCoordinates.append((i,j))

    ###---Finds Wall Positions---###
    wallCoordinates = []
    for k in range(rowCount):
        for l in range(columnCount):
            if occupancyMap[k][l] == 1:
                wallCoordinates.append((k,l))

    ###---Value Iteration---###
    for x in range(rowCount):
        for y in range(columnCount):
            ###---Checking If Coordinate is a Terminal or Wall---###
            if ((x,y) in wallCoordinates) or ((x,y) in terminalStateCoordinates):
                continue

            valuesU =[]
            ###---For Every Cardinal Direction---###
            for direction in directions.keys():
                ###---Finding Up, Right, Left Directions of Caardinal Direction---###
                directionList = list(directions.keys())
                if direction == "R" or direction == "L":
                    directionList.remove("R")
                    directionList.remove("L")
                elif direction == "U" or direction == "D":
                    directionList.remove("D")
                    directionList.remove("U")

                ###---Calculating Up, Left, Right Values---###
                up = (x+directions[direction][0], y+directions[direction][1])
                left = (x+directions[directionList[0]][0], y+directions[directionList[0]][1])
                right = (x+directions[directionList[1]][0], y+directions[directionList[1]][1])
                dirValues = [left,up,right]

                ###---Finding U Value in Old State Matrix---###
                oldUValue = []
                for dir in dirValues:
                    if dir[0] < 0 or dir[1] < 0 or dir[0] > rowCount - 1 or dir[1] > columnCount - 1 or (dir in wallCoordinates):
                        oldUValue.append(currentStateValues[x][y]) 
                    else:
                        oldUValue.append(currentStateValues[dir[0]][dir[1]])

                ###---Finding U Values for Caardinal Directions---###
                U = stepCost + (0.1 * discountFactor * oldUValue[0]) + (0.8 * discountFactor * oldUValue[1]) + (0.1 * discountFactor * oldUValue[2])
                valuesU.append(U)

            ###---Choosing Biggest U Value Possible---###
            newStateValues[x][y] = max(valuesU)

    ###---Appending Terminal Values to New State Matrix---###
    for terminal in terminalStateCoordinates:
        newStateValues[terminal[0]][terminal[1]] =  currentStateValues[terminal[0]][terminal[1]]
    """
        YOUR CODE ENDS HERE
    """
    
    return newStateValues





















#  read map info from file
occupancyMap = ReadGridFromText("map.txt", int)
print("--- 2D Map Array ---")
Print2DArray(occupancyMap)

#  read initial state values from file
initialStateValues = ReadGridFromText("initial_state_values.txt", float)    
print("--- Initial State Values Array ---")
Print2DArray(initialStateValues)

#  read information of which states are terminal state 
terminalStateMask = ReadGridFromText("terminal_state_mask.txt", int)
print("--- Terminal State Mask ---")
Print2DArray(terminalStateMask)

#  get grid dimension info
numRows = len(occupancyMap)
numCols = len(occupancyMap[0])  #  assuming all rows have same number of columns


#  create a new variable for current state values
stateValues = initialStateValues


#  perform value iteration for 200 iterations
for i in range(200):
    stateValues = GridValueIteration(occupancyMap, stateValues, terminalStateMask, stepCost=-0.04, discountFactor=1.0)

#  draw final values of each state
DrawStateImage(stateValues, occupancyMap, terminalStateMask, numRows=numRows, numCols=numCols)
