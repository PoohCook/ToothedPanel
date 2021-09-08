#Author-Pooh
#Description-Craete a sketc of a toothed panel

import adsk.core, adsk.fusion, adsk.cam, traceback

from . import Logger

_app = None
_ui  = None

# Global set of event handlers
_handlers = []

_panel = None


class ToothedPanel():
    def __init__(self, inputs):
        global _app, _ui
        self.lines = None
        self.origin = adsk.core.Point3D.create(0,0,0)
        self.panelWidth = inputs.itemById("panel_width")
        self.panelHeight = inputs.itemById("panel_height")
        self.teethWidth = inputs.itemById("teeth_width")
        self.teethDepth = inputs.itemById("teeth_depth")

        self.topCount = inputs.itemById("top_teeth_count")
        self.leftCount = inputs.itemById("left_teeth_count")
        self.rightCount = inputs.itemById("right_teeth_count") 
        self.bottomCount = inputs.itemById("bottom_teeth_count")

        self.up = adsk.core.Vector3D.create(0, 1, 0)
        self.down = adsk.core.Vector3D.create(0, -1, 0)
        self.left = adsk.core.Vector3D.create(-1, 0, 0)
        self.right = adsk.core.Vector3D.create(1, 0, 0)

    def setOrigin(self, pnt):
        self.origin = pnt
        self.panelWidth.setManipulator(pnt, adsk.core.Vector3D.create(1, 0, 0))
        self.panelHeight.setManipulator(pnt, adsk.core.Vector3D.create(0, 1, 0))

        Logger.getLogger().info("origin set: %s, %s, %s" % (pnt.x, pnt.y, pnt.z)) 

    def createScaledVector(self, vector, scale):
            retVector = vector.copy()
            retVector.scaleBy(scale)
            return retVector
       
    def generateSide(self, vProgress, vRelief, length, tWidth, tDepth, tCount):
        vectors = []
        if tCount < 0:
            raise ValueError("invalid tCount")
        
        elif tCount == 0:
            vectors.append(self.createScaledVector(vProgress, length))
        
        elif tCount == 1:
            prog = (length - tWidth)/2.0
            vectors.append(self.createScaledVector(vProgress, prog))
            vectors.append(self.createScaledVector(vRelief, tDepth))
            vectors.append(self.createScaledVector(vProgress, tWidth))
            vectors.append(self.createScaledVector(vRelief, tDepth * -1))
            vectors.append(self.createScaledVector(vProgress, prog))

        else:
            prog = (length - (tCount * tWidth))/(tCount-1)
            for i in range(tCount-1):
                vectors.append(self.createScaledVector(vProgress, tWidth))
                vectors.append(self.createScaledVector(vRelief, tDepth))
                vectors.append(self.createScaledVector(vProgress, prog))
                vectors.append(self.createScaledVector(vRelief, tDepth * -1))
                
            vectors.append(self.createScaledVector(vProgress, tWidth))

        return vectors           

    def draw(self):
        try:
            width = self.panelWidth.value
            height = self.panelHeight.value
            tWidth = self.teethWidth.value
            tDepth = self.teethDepth.value

            topCnt = self.topCount.value
            leftCnt = self.leftCount.value
            rightCnt = self.rightCount.value
            bottomCnt = self.bottomCount.value

            Logger.getLogger().info("teeth:[%f:%f] %d,%d,%d,%d" % (tWidth, tDepth, topCnt, leftCnt, rightCnt, bottomCnt))

            # pnt0 = self.origin.copy()
            # pnt1 = self.origin.copy()
            # pnt1.translateBy( adsk.core.Vector3D.create( width, height, 0))

            vectors = []
            vectors += self.generateSide(self.up, self.right, height, tWidth, tDepth, leftCnt)
            vectors += self.generateSide(self.right, self.down, width, tWidth, tDepth, topCnt)
            vectors += self.generateSide(self.down, self.left, height, tWidth, tDepth, rightCnt)
            vectors += self.generateSide(self.left, self.up, width, tWidth, tDepth, bottomCnt)

            sketch = adsk.fusion.Sketch.cast(_app.activeEditObject)
            lines = sketch.sketchCurves.sketchLines
            points = sketch.sketchPoints
            firstPnt = points.add(self.origin)
            lastPnt = firstPnt
            nextPnt = self.origin.copy()
            for vector in vectors[:-1]:
                nextPnt.translateBy(vector)
                nextPnt = points.add(nextPnt)
                line = lines.addByTwoPoints(lastPnt, nextPnt)
                lastPnt = line.endSketchPoint
                nextPnt = lastPnt.geometry.copy()

            lines.addByTwoPoints(lastPnt, firstPnt)

            Logger.getLogger().info("drew box: %d" % (len(vectors)))

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class MySelectHandler(adsk.core.SelectionEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        global _app, _ui, _panel
        try:
            pnt = adsk.fusion.SketchPoint.cast(args.selection.entity).geometry
            args.isSelectable = True
            if _panel:
                _panel.setOrigin(pnt)
            
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class MyCommandExecutePreviewHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        global _app, _ui, _panel
        try:
            if _panel:
                _panel.draw()
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))                


# Event handler that reacts to any changes the user makes to any of the command inputs.
class MyCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        global _app, _ui, _panel
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            inputs = eventArgs.inputs
            cmdInput = eventArgs.input


        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler that reacts to when the command is destroyed. This terminates the script.            
class MyCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        global _app, _ui, _panel
        try:
            cmdArgs = adsk.core.CommandEventArgs.cast(args)
            Logger.getLogger().info('Execute: %s' % cmdArgs.command)

            inputs = cmdArgs.command.commandInputs
            if _panel:
                _panel.draw()
 
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler that reacts to when the command is destroyed. This terminates the script.            
class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        global _app, _ui
        try:
            # When the command is done, terminate the script
            # This will release all globals which will remove all event handlers
            cmdArgs = adsk.core.CommandEventArgs.cast(args)

            Logger.delLogger()
            adsk.terminate()
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler that creates my Command.
class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def createMainTab(self, id, name, inputs):
        tabCmdInput = inputs.addTabCommandInput(id, name)
        mainInputs = tabCmdInput.children

        # Create a selection input.
        selectionInput = mainInputs.addSelectionInput('origin_select', 'Origin', 'where to originate the panel')
        selectionInput.addSelectionFilter(adsk.core.SelectionCommandInput.SketchPoints)
        selectionInput.setSelectionLimits(1,1)

        mainInputs.addValueInput('teeth_width', 'Teeth Width', 'mm', adsk.core.ValueInput.createByString("thickness * 2"))
        mainInputs.addValueInput('teeth_depth', 'Teeth depth', 'mm', adsk.core.ValueInput.createByString("thickness"))

        # Create distance value input X.
        distanceValueInput = mainInputs.addDistanceValueCommandInput('panel_width', 'Panel Width', adsk.core.ValueInput.createByReal(1))
        distanceValueInput.setManipulator(adsk.core.Point3D.create(0, 0, 0), adsk.core.Vector3D.create(1, 0, 0))
        distanceValueInput.expression = '10 mm'
        distanceValueInput.hasMinimumValue = False
        distanceValueInput.hasMaximumValue = False
        
        # Create distance value input Y.
        distanceValueInput2 = mainInputs.addDistanceValueCommandInput('panel_height', 'Panel Height', adsk.core.ValueInput.createByReal(1))
        distanceValueInput2.setManipulator(adsk.core.Point3D.create(0, 0, 0), adsk.core.Vector3D.create(0, 1, 0))
        distanceValueInput2.expression = '10 mm'
        distanceValueInput2.hasMinimumValue = False
        distanceValueInput2.hasMaximumValue = False

    def createSideTab(self, id, name, inputs):
        # Create a tab input.
        tabCmdInput = inputs.addTabCommandInput(id, name)
        tabInputs = tabCmdInput.children

        tabInputs.addIntegerSpinnerCommandInput('%s_teeth_count' % id, 'Teeth', 0 , 100 , 1, int(0))
        tabInputs.addValueInput('%s_teeth_width' % id, 'Teeth Width', 'mm', adsk.core.ValueInput.createByString("thickness * 2"))
        tabInputs.addValueInput('%s_teeth_depth' % id, 'Teeth depth', 'mm', adsk.core.ValueInput.createByString("thickness"))

    def notify(self, args):
        global _app, _ui, _panel
        try:
            # Get the command that was created.
            cmd = adsk.core.Command.cast(args.command)

            # Connect to the command destroyed event.
            onDestroy = MyCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

            # Connect to the input changed event.           
            onInputChanged = MyCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)    

            # Connect to the execute event.           
            onExecute = MyCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute) 

            onSelect = MySelectHandler()
            cmd.select.add(onSelect)
            _handlers.append(onSelect) 

            onExecutePreview = MyCommandExecutePreviewHandler()
            cmd.executePreview.add(onExecutePreview)
            _handlers.append(onExecutePreview)        

            # Get the CommandInputs collection associated with the command.
            inputs = cmd.commandInputs

            self.createMainTab("main", "Main", inputs)
            self.createSideTab("top", "Top", inputs)
            self.createSideTab("right", "Right", inputs)
            self.createSideTab("bottom", "Bottom", inputs)
            self.createSideTab("left", "Left", inputs)
    
            _panel = ToothedPanel(inputs)

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface


        Logger.getLogger().error("hello")

        # Get the existing command definition or create it if it doesn't already exist.
        cmdDef = _ui.commandDefinitions.itemById('cmdToothedPanel')
        if not cmdDef:
            cmdDef = _ui.commandDefinitions.addButtonDefinition('cmdToothedPanel', 
                                                                'Created Toothed Panel',
                                                                'My first command')

        # Connect to the command created event.
        onCommandCreated = MyCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

        # Execute the command definition.
        cmdDef.execute()

        # Prevent this module from being terminated when the script returns.
        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))