#
# Copyright 2014 Modeliosoft
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from org.modelio.metamodel.uml.statik import Class, Interface, Package
from org.modelio.metamodel.uml.behavior.activityModel import Activity, ActivityPartition, ActivityFinalNode

def hasStereotype(el, stn):
	for stereo in el.getExtension():
		if stereo.getName() == stn:
			return True
	return False

def neighbors(program):
	return [\
		pend.getProvider().getProviding().getInternalOwner()\
		for port in program.getInternalStructure()\
			for req in  port.getRequired()\
				for iface in req.getRequiredElement() \
					for rend in req.getNaryProvider()\
						for pend in rend.getNaryLink().getNaryLinkEnd() if pend is not rend and pend.getProvider() and pend.getProvider().getProviding().getInternalOwner()]
def ioStreams(swPlat):
	return [ port for program in swPlat.getOwnedElement(Class) if hasStereotype(program, 'JUNIPERProgram') \
			     for port in program.getInternalStructure() if hasStereotype(port, 'RequestResponseStream')]

def computePaths(swPlat):
	ret = []

	def dfs_(node, path):
		if node not in path:
			path.append(node)
			nextNodes = neighbors(node)
			print 'neighbors for ', node.getName(), ': ', nextNodes
			if nextNodes:
				for nextNode in nextNodes:
					dfs_(nextNode, path)
			else:
				ret.append(list(path))
			path.remove(node) # allows dfs to continue exploring other node at the same position
		else:
			path.append(node) # allows a path to finish with the same node in case there's a cycle
			ret.append(list(path)) # if you found a cycle, end the path here

	consideredPrograms = []
	for stream in ioStreams(swPlat):
		program = stream.getInternalOwner()
		print 'considering: ', program.getName()
		if program not in consideredPrograms:
			consideredPrograms.append(program)
			dfs_(program, [])
	return ret

def getBehaviorModelsPackage(swPlat):
	packages = [ package for package in swPlat.getOwnedElement(Package) if package.getName() == 'BehaviorModels' ]
	if packages:
		return packages[0]
	else:
		return factory.createPackage('BehaviorModels', swPlat)

factory = modelingSession.getModel()
def generateBehaviorModels(swPlat):
    package = getBehaviorModelsPackage(swPlat)

    paths = computePaths(swPlat)
    print 'paths: ', paths
    for path in paths:
    	activity = factory.createActivity()
    	activity.setName('BehaviorSpecification')
    	package.getOwnedBehavior().add(activity)

    	actions = {}
    	partitions = {}

    	for i in range(len(path)):
    		if (path[i] in partitions):
    			partition = partitions[path[i]]
    		else:
    			partition = factory.createActivityPartition()
    			activity.getOwnedGroup().add(partition)
    			partition.setRepresented(path[i].getRepresenting()[0])
    			partitions[path[i]] = partition

    		if i:
    			actions[i] = factory.createOpaqueAction()
    			actions[i].setName('chunk')
    		else:
    			actions[i] = factory.createInitialNode()

    		note = factory.createNote('.*', 'description', actions[i], '')
    		note.setMimeType('text/plain')
    		note.setContent('relDl=(worst=1, best=1, value=1, prob=1.0)')
    		partition.getContainedNode().add(actions[i])

    		if i == len(path)-1:
    			finalNode = factory.createActivityFinalNode()
    			partition.getContainedNode().add(finalNode)
    			actions[i+1] = finalNode

    	for i in range(len(path)):
    		edge = factory.createControlFlow()
    		actions[i].getOutgoing().add(edge)
    		edge.setTarget(actions[i+1])
    		if i != len(path)-1:
    			note = factory.createNote('.*', 'description', edge, '')
    			note.setMimeType('text/plain')
    			note.setContent('relDl=(worst=1, best=1, value=1, prob=1.0)')

from org.eclipse.swt.widgets import MessageBox
from org.eclipse.swt.widgets import Display
from org.eclipse.swt import SWT
def hardwareModelIsMissingMessageBox(programs):
	for program in programs :
		if not program.getRepresenting():
			msg = "Warn : Program {0} not found in hardware model.".format(program.getName())
			print msg
			showDialogBox("Please fix hardware model", msg)
			return False
	return True

def showDialogBox(text, message):      	 
	from org.eclipse.swt.widgets import Display
	from java.lang import Runnable
	
	class ShowDialogBox(Runnable):
	    def __init__(self):
	        pass
	
	    def run(self):
			m = MessageBox(Display.getDefault().getActiveShell(), SWT.ICON_WARNING|SWT.OK)
			m.setText(text)
			m.setMessage(message)
			m.open()
	
	Display.getDefault().syncExec(ShowDialogBox())
      	 
model = selectedElements.get(0)
swPlat = [p for p in model.getOwnedElement(Package) if hasStereotype(p, 'SoftwareArchitectureModel')][0]
hwPlat = [p for p in model.getOwnedElement(Package) if hasStereotype(p, 'HardwarePlatformModel')][0]
programs = [ el for el in swPlat.getOwnedElement(Class) if hasStereotype(el, 'JUNIPERProgram') ]

if not hardwareModelIsMissingMessageBox(programs) :
	class InvalidHardwareModelException(Exception):
	    pass   
	raise InvalidHardwareModelException()

generateBehaviorModels(swPlat)
