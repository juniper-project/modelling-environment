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
import xml.etree.ElementTree as ET
from org.modelio.metamodel.uml.statik import Class, Interface, Package
from org.modelio.metamodel.uml.behavior.activityModel import Activity, ActivityPartition, ActivityFinalNode

def hasStereotype(el, stn):
	for stereo in el.getExtension():
		if stereo.getName() == stn:
			return True
	return False

def getTagValues(el, tagName):
    lists = [y.getActual() for y in el.getTag() if y.getDefinition().getName() == tagName ]
    values = [x.getValue() for list in lists for x in list]
    return values

def getTagValue(el, tagName, default=None):
    list = getTagValues(el, tagName)
    if len(list)>0:
        return list[0]
    else:
        return default

def getJavaPackageName(pkg):
    if (hasStereotype(pkg, 'JavaPackage')):
       return getJavaPackageName(pkg.getOwner())+ getTagValue(pkg, 'JavaName', default=pkg.getName())+'.'
    else:
       return ''

def getParameterType(par):
    if par:
    	 type = par.getType()
    	 if (hasStereotype(type, 'JavaClass')):
    	    return getJavaPackageName(type.getOwner())+type.getName()
    	 else:
    	    return type.getName()
    else:
    	 return 'void'

def isExternalProgram(jclass):
	return not jclass.getOwner() == swPlat

def getFullInterfaceName(iface):
	return getJavaClassName(iface)
    	
def getJavaClassName(jclass):
	packageName = getTagValue(jclass.getOwner(), 'JavaName')
	if packageName:
		packagePrefix = packageName + '.'
	else:
		packagePrefix = ''
	return packagePrefix+jclass.getName()	

def interpretConstraint(str):
	def interpretVardefs(str, split='\n'):
		ret = {}
		for vardef in str.split(split):
			arr = vardef.partition('=')
			varname = arr[0].strip()
			varval  = arr[2].strip()

			if varval.startswith('('):
				varval = interpretVardefs(varval[1:-1], split=',')
			elif varval[:1].isalpha():
				paridx = varval.find('(')
				vartype = varval[0:paridx]
				varval = interpretVardefs(varval[paridx+1:-1], split=',')
				varval['type'] = vartype
			if varname:
			   ret[varname] = varval
		return ret
	return interpretVardefs(str)

def fillTag(tag, structure, topLevel=True):
    if isinstance(structure, dict):
       for name in structure.keys():
       	   value = structure[name]
       	   if isinstance(value, dict) or topLevel:
       	   	ntag = ET.SubElement(tag, name)
       	   	fillTag(ntag, value, False)
       	   else:
       	   	tag.set(name, str(value))
    else:
     	 tag.text = str(structure)

def getDescriptor(el, model='description'):
    return [ note for note in el.getDescriptor() if note.getModel().getName() == model ]

def translateRtSpec(el, parentTag):
    if getDescriptor(el):
	    constraintNote = getDescriptor(el)[0]
	    constraintStructure = interpretConstraint(constraintNote.getContent())
	    rtSpecTag =  ET.SubElement(parentTag, 'rtSpecification')
	    fillTag(rtSpecTag, constraintStructure)
	    return rtSpecTag

model = selectedElements.get(0)

juniper = ET.Element('juniper')
app = ET.SubElement(juniper, 'application')
app.set('name', model.getName())

swPlat = [p for p in model.getOwnedElement(Package) if hasStereotype(p, 'SoftwareArchitectureModel')][0]
hwPlat = [p for p in model.getOwnedElement(Package) if hasStereotype(p, 'HardwarePlatformModel')][0]

## SW Platform
swTag = ET.SubElement(app, 'softwareModel')
programs   = [ el for el in swPlat.getOwnedElement(Class) if hasStereotype(el, 'JUNIPERProgram') ]
bindings = []

externalProgramsUses = [ (program, externalProgram) \
		for program in programs\
		for port in program.getInternalStructure()\
		for req in  port.getRequired()\
		for iface in req.getRequiredElement() \
		for rend in req.getNaryProvider()\
		for pend in rend.getNaryLink().getNaryLinkEnd() if pend is not rend and pend.getProvider()\
		for externalProgram in [pend.getProvider().getProviding().getInternalOwner()] if externalProgram and isExternalProgram(externalProgram)]

programs.extend(set([externalProgram for (program, externalProgram) in externalProgramsUses]))

for program in programs:
	programTag =  ET.SubElement(swTag, 'program')
	programTag.set('javaClass', getJavaClassName(program))


	p = [ (rend.getConsumer().getRequiring().getInternalOwner(), iface) \
		for port in program.getInternalStructure()\
		for prov in  port.getProvided()\
		for iface in prov.getProvidedElement() \
		for pend in prov.getNaryConsumer()\
		for rend in pend.getNaryLink().getNaryLinkEnd() if rend is not pend and rend.getConsumer()]

	for (jclass, interface) in p:
	    bindings.append((program, jclass, interface))

	for interface in set([interface for (jclass, interface) in p]):
	    for operation in interface.getOwnedOperation():
			channelTag =  ET.SubElement(programTag, 'communicationChannel')
			channelTag.set('interface', getFullInterfaceName(interface))
			channelTag.set('operation', operation.getName())
			if operation.getReturn():
				channelTag.set('requiresResponse', 'true')
			else:
				channelTag.set('requiresResponse', 'false')

			translateRtSpec(operation, channelTag)

	for port in program.getInternalStructure():
		if hasStereotype(port, 'RequestResponseStream'):
			streamTag =  ET.SubElement(programTag, 'requestResponseStream')
			streamTag.set('name', port.getName())
			streamTag.set('id',   port.getUuid().toString())
			streamTag.set('requiresResponse',   getTagValue(port, 'requiresResponse', 'false'))

			translateRtSpec(port, streamTag)

	translateRtSpec(program, programTag)

	# translate complex resource usage
	for dep in  program.getDependsOnDependency():
	    constraintNote = getDescriptor(dep)[0]
	    constraintStructure = interpretConstraint(constraintNote.getContent())
	    resTag =  ET.SubElement(programTag, 'resourceUsage')
	    resTag.set('resourceID', dep.getDependsOn().getUuid().toString())
	    fillTag(resTag, constraintStructure)

for (program, jclass, iface) in bindings:
	bindingTag =  ET.SubElement(swTag, 'binding')
	bindingTag.set('provider',  getJavaClassName(program))
	bindingTag.set('requirer',  getJavaClassName(jclass))
	bindingTag.set('interface', getJavaClassName(iface))

# TODO: support non preemptive sw regions

## HW Platform
hwTag = ET.SubElement(app, 'hardwareModel')
for node in [ node for node in hwPlat.getDeclared() if hasStereotype(node, 'CloudNode') ]:
	nodeTag =  ET.SubElement(hwTag, 'cloudNode')
	nodeTag.set('name', node.getName())
	nodeTag.set('ip', getTagValue(node, 'ip', ''))
	nodeTag.set('hwClass', getTagValue(node, 'hwClass', ''))

	for cpu in [cpu for cpu in node.getPart() if hasStereotype(cpu, 'CloudNodeCPU')]:
		cpuNode = ET.SubElement(nodeTag, 'cpu')
		cpuNode.set('id', cpu.getUuid().toString())
	for disk in [disk for disk in node.getPart() if hasStereotype(disk, 'CloudDisk')]:
		diskNode = ET.SubElement(nodeTag, 'disk')
		diskNode.set('id', disk.getUuid().toString())
	for program in [program for program in node.getPart() if hasStereotype(program, 'ProgramInstance')]:
		programNode = ET.SubElement(nodeTag, 'programInstance')
		programNode.set('ref', getJavaClassName(program.getBase()))

	if node.getMultiplicityMin() != '1':
	   nodeTag.set('minGroup', node.getMultiplicityMin())
	if node.getMultiplicityMax() != '1':
	   nodeTag.set('maxGroup', node.getMultiplicityMax())

## Behavior model
bhTag = ET.SubElement(app, 'behaviorModel')

for activity in [activity for package in swPlat.getOwnedElement(Package) for activity in package.getOwnedBehavior(Activity)]:
    bhSpecTag = ET.SubElement(bhTag, 'behaviorSpecification')
    bhSpecTag.set('id', activity.getUuid().toString())
    
    translateRtSpec(activity, bhSpecTag)
    chunks = [ action \
    	   for partition in activity.getOwnedGroup(ActivityPartition)\
	   for action in partition.getContainedNode() if not isinstance(action, ActivityFinalNode) ]

    for chunk in chunks:
    	chunkTag = ET.SubElement(bhSpecTag, 'chunk')
    	translateRtSpec(chunk, chunkTag)

    	chunkTag.set('id', chunk.getUuid().toString())

    	programInst = chunk.getOwnerPartition().getRepresented()
    	chunkTag.set('program', getJavaClassName(programInst.getBase()))

    	targets =[dep.getDependsOn() \
      		for dep in  chunk.getDependsOnDependency()]
    	if targets:
    		chunkTag.set('schedNode', targets[0].getUuid().toString())
    	else:
    		chunkTag.set('schedNode', programInst.getCluster().getName())

    	for successorEdge in [ edge for edge in chunk.getOutgoing() if not isinstance(edge.getTarget(), ActivityFinalNode) ]:
    	    successor = successorEdge.getTarget()

    	    succTag = ET.SubElement(chunkTag, 'successor')
    	    succTag.set('id', successorEdge.getUuid().toString())

    	    edgeChunkTag = ET.SubElement(bhSpecTag, 'chunk')
    	    edgeChunkTag.set('id', successorEdge.getUuid().toString())
    	    edgeChunkTag.set('program', chunkTag.get('program'))
    	    edgeChunkTag.set('schedNode', 'netnode')

    	    edgeSuccTag = ET.SubElement(edgeChunkTag, 'successor')
    	    edgeSuccTag.set('id', successor.getUuid().toString())

    	    translateRtSpec(successorEdge, edgeChunkTag)

## Shed Nodes for the Schedullability analyser
smTag = ET.SubElement(app, 'schedModel')
netNodeTag = ET.SubElement(smTag, 'schedNode')
netNodeTag.set('name', 'netnode')
netTag = ET.SubElement(netNodeTag, 'net')
netTag.set('id', 'netnode')

for node in [ node for node in hwPlat.getDeclared() if hasStereotype(node, 'CloudNode') ]:
	nodeTag =  ET.SubElement(smTag, 'schedNode')
	nodeTag.set('name', node.getName())
	nodeTag.set('ip', getTagValue(node, 'ip', ''))
	nodeTag.set('hwClass', getTagValue(node, 'hwClass', ''))

	for cpu in [cpu for cpu in node.getPart() if hasStereotype(cpu, 'CloudNodeCPU')]:
		cpuNode = ET.SubElement(nodeTag, 'cpu')
		cpuNode.set('id', cpu.getUuid().toString())

	for disk in [disk for disk in node.getPart() if hasStereotype(disk, 'CloudDisk')]:
		nodeTag =  ET.SubElement(smTag, 'schedNode')
		nodeTag.set('name', disk.getUuid().toString())
		diskNode = ET.SubElement(nodeTag, 'disk')
		diskNode.set('id', disk.getUuid().toString())

	if node.getMultiplicityMin() != '1':
	   nodeTag.set('minGroup', node.getMultiplicityMin())
	if node.getMultiplicityMax() != '1':
	   nodeTag.set('maxGroup', node.getMultiplicityMax())
# TODO: support clocks!!

resultFile = '<?xml version="1.0"?>' + ET.tostring(juniper, encoding='utf-8')
print resultFile
