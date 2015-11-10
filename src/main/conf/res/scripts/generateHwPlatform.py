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

def hasStereotype(el, stn):
	for stereo in el.getExtension():
		if stereo.getName() == stn:
			return True
	return False

def isExternalProgram(jclass):
	return not jclass.getOwner() == swPlat

model = selectedElements.get(0)
swPlat = [p for p in model.getOwnedElement(Package) if hasStereotype(p, 'SoftwareArchitectureModel')][0]
hwPlat = [p for p in model.getOwnedElement(Package) if hasStereotype(p, 'HardwarePlatformModel')][0]

def create_node(hwPlat, name='node'):
	node = modelingSession.getModel().createInstance(name, hwPlat)
	node.addStereotype('MARTEDesigner', 'HwComputingResource_Instance')
	node.addStereotype('JuniperIDE', 'CloudNode')
	
	cpu = modelingSession.getModel().createBindableInstance()
	cpu.setName('CPU')
	node.getPart().add(cpu)
	cpu.addStereotype('MARTEDesigner', 'HwProcessor_Instance')
	cpu.addStereotype('JuniperIDE', 'CloudNodeCPU')
	return node

def create_program_instance(hwPlat, program):
	node = create_node(hwPlat, 'node_'+program.getName())
	pInst = modelingSession.getModel().createBindableInstance()
	pInst.setName(program.getName())
	node.getPart().add(pInst)
	pInst.addStereotype('JuniperIDE', 'ProgramInstance')
	pInst.setBase(program)
		
programs = [ el for el in swPlat.getOwnedElement(Class) if hasStereotype(el, 'JUNIPERProgram')]
externalPrograms = [ externalProgram \
			for program in programs\
			for port in program.getInternalStructure()\
			for req in  port.getRequired()\
			for iface in req.getRequiredElement() \
			for rend in req.getNaryProvider()\
			for pend in rend.getNaryLink().getNaryLinkEnd() if pend is not rend and pend.getProvider()\
			for externalProgram in [pend.getProvider().getProviding().getInternalOwner()] if externalProgram and isExternalProgram(externalProgram)]
programs.extend(externalPrograms)

for program in programs:
	create_program_instance(hwPlat, program)	
