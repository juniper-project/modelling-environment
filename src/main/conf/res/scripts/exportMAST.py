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

from org.modelio.metamodel.uml.statik import Class

def interpretConstraint(str):	
	def interpretVardefs(str, split='\n'):
		ret = {}
		for vardef in str.split(split):
			arr = vardef.partition('=')
			varname = arr[0].strip()
			varval      = arr[2].strip()
		
			if varval.startswith('('):
				varval = interpretVardefs(varval[1:-1], split=',')				
			elif varval[:1].isalpha():
				paridx = varval.find('(')
				vartype = varval[0:paridx]
				varval = interpretVardefs(varval[paridx+1:-1], split=',')
				varval['type'] = vartype
			ret[varname] = varval
		return ret
	return interpretVardefs(str)

def hasStereotype(el, stn):
	for stereo in el.getExtension():
		if stereo.getName() == stn:
			return True
	return False


text = ''
def emit(str):
	global text
	text = text + str + '\n'
	print str

def getPriority(programInst):
	# TODO get note from the right place!!!
	constraintNote = programInst.getBase().getDescriptor()[0]	
	return interpretConstraint(constraintNote.getContent())['priority']

def getWCET(programInst):
	# TODO
	return 1

def getRequestStreamRT(port):
	# TODO get note from the right place!!!
	constraintNote = port.getDescriptor()[0]	
	constraint = interpretConstraint(constraintNote.getContent())['occKind']
	streamName = port.getName()
	
	if constraint['type'] == 'periodic':
		return 'Type => Periodic, Name => E_' + streamName + ', Period => ' + constraint['period']  
	elif constraint['type'] == 'burst':
		return 'Type => Bursty, Name => E_' + streamName + ', Max_Arrivals => ' + constraint['burstSize'] + ', Bound_Interval => ' + constraint['maxInterval']   
	else:
		return ''

def getRequestStreamDeadline(port):
	# TODO get note from the right place!!!
	constraintNote = port.getDescriptor()[0]	
	return interpretConstraint(constraintNote.getContent())['relDl']
	
def getResourceList(programInst):
	# TODO
	return getNodeName(programInst.getCluster())

def getProgramInstRT(programInst):
	# TODO get note from the right place!!!
	constraintNote = programInst.getBase().getDescriptor()[0]	
	constraint = interpretConstraint(constraintNote.getContent())['relDl']
	
	if isinstance(constraint, dict):
		ret = ''
		
		if constraint['value']:
			ret += ', Avg_Case_Execution_Time => ' + constraint['value']
		
		if constraint['worst']:
			ret += ', Worst_Case_Execution_Time => ' + constraint['worst']

		if constraint['best']:
			ret += ', Best_Case_Execution_Time => ' + constraint['best']
			
		return ret
	else:
		return ', Avg_Case_Execution_Time => ' + constraint
	
def getProgramCalls(programInst):
	calls = [getProgramInstName(programInst)+'_Run']
	
	program = programInst.getBase()
	r = [ (pend.getProvider().getProviding().getInternalOwner(), iface) \
		for port in program.getInternalStructure()\
		for req in  port.getRequired()\
		for iface in req.getRequiredElement() \
		for rend in req.getNaryProvider()\
		for pend in rend.getNaryLink().getNaryLinkEnd() if pend is not rend]

	for (jclass, iface) in r:
	    calls.append(jclass.getName()+'_Call')
	
	return ','.join(calls)

def getNodeName(node):
	return 'Node_'+node.getName().replace('.', '_')
def getProgramInstName(programInst):
	return programInst.getBase().getName()
	
model = selectedElements.get(0)
		
for node in [node \
			for hwplat in model.getOwnedElement() if hasStereotype(hwplat, 'HardwarePlatformModel') \
			for node in hwplat.getDeclared()]:
   processorName = 'Processor_'+node.getName().replace('.', '_')				
   emit('Processing_Resource(Type => Fixed_Priority_Processor, Name =>'+processorName+');')				

   nodeName = getNodeName(node)				
   emit('Shared_Resource(Type => Immediate_Ceiling_Resource, Name => '+nodeName+');')				
   
   # TODO: support disks, etc.

   for programInst in [ programInst for programInst in node.getPart() if hasStereotype(programInst, 'ProgramInstance')]:
      emit('Scheduling_Server(Type => Fixed_Priority, Name => '+getProgramInstName(programInst)+'_SS,	Server_Sched_Parameters	=> (Type => Fixed_Priority_policy, The_Priority	=> '+str(getPriority(programInst))+', Preassigned => No), Server_Processing_Resource => '+processorName+');')
      emit('Operation (Type => Simple, Name => '+getProgramInstName(programInst)+'_Run,  Shared_Resources_List => ('+getResourceList(programInst)+')'+getProgramInstRT(programInst)+');')
      emit('Operation (Type => Composite, Name => '+getProgramInstName(programInst)+'_Call, Composite_Operation_List  => ('+getProgramCalls(programInst)+'));')

      for port in [ port for port in programInst.getBase().getInternalStructure() if not port.getRequired() and not port.getProvided()]:
		streamName = port.getName()
		# TODO extract RT values
		emit('Transaction (Type => Regular, Name => '+streamName+'_Stream, External_Events => (('+getRequestStreamRT(port)+')), Internal_Events => ((Type => regular, name => O_'+streamName+', Timing_Requirements => (Type => Hard_Global_Deadline, Deadline => '+getRequestStreamDeadline(port)+', Referenced_Event => E_'+streamName+'))), Event_Handlers => ((Type => Activity, Input_Event => E_'+streamName+', Output_Event => O_'+streamName+', Activity_Operation => '+getProgramInstName(programInst)+'_Call, Activity_Server => '+getProgramInstName(programInst)+'_SS)));')
			    
from org.modelio.api.modelio import Modelio
jdesigner = Modelio.getInstance().getModuleService().getPeerModule("JavaDesigner")

# generate app context file
javaConfiguration = jdesigner.getConfiguration();
genPath = javaConfiguration.getParameterValue("GenerationPath").replace(u'$(Project)', javaConfiguration.getProjectSpacePath().toString())

f = open(genPath+'/mast.txt', 'w')
f.write(text)
f.close()

