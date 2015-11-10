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
import os.path
from org.modelio.metamodel.uml.statik import Class, Interface
from modelling import applyToFirstLetter, hasStereotype, addTagValue, \
				      setTagValue, hasTagValue, getTagValues, getTagValue, \
					  createTraceabilityLink, getJavaClassName, \
					  createOperation, createParameterIO, createAttribute, \
					  createAttributeJavaType 

# Utilities
def setBusinessObjectsAsSerializable(package):
	for jclass in [ jclass for jclass in package.getOwnedElement(Class) if hasStereotype(jclass, 'Entity')]:
		stereoImplements = [it for it in getTagValues(jclass, 'JavaImplements') if 'Serializable' in it] 
		modelImplements = [ ir for ir in jclass.getRealized() if ir.getImplemented().getName() == 'Serializable' ]
		if not stereoImplements and not modelImplements:
			addTagValue(jclass, "JavaImport", "java.io.Serializable")
			addTagValue(jclass, "JavaImplements", "Serializable")
	for subPackage in package.getOwnedElement(Package):
		setBusinessObjectsAsSerializable(subPackage)

def getNodeForProgram(program):
	model = swPlat.getOwner()
	return [ node for hwPlat in model.getOwnedElement() \
				  for node in hwPlat.getDeclared() \
				  for programInst in node.getPart() \
				  		if programInst.getBase() == program][0]

from org.eclipse.swt.widgets import MessageBox
from org.eclipse.swt.widgets import Display
from org.eclipse.swt import SWT
def hardwareModelIsMissingMessageBox(programs):
	for program in programs :
		if not program.getRepresenting():
			msg = MessageBox(Display.getCurrent().getActiveShell(), SWT.ICON_WARNING|SWT.OK)
			msg.setText("Update or generate code")
			msg.setMessage("Warn : generate hardware model please.")
			msg.open()
			return False
	return True


def getNodeIP(node): return getTagValues(node, 'ip')
def getFullJavaName(el): return getJavaClassName(el)
def getFullClassName(jclass): return getJavaClassName(jclass)
def getFullInterfaceName(iface): return getJavaClassName(iface)

model = selectedElements.get(0)
swPlat = [p for p in model.getOwnedElement(Package) if hasStereotype(p, 'SoftwareArchitectureModel')][0]
hwPlat = [p for p in model.getOwnedElement(Package) if hasStereotype(p, 'HardwarePlatformModel')][0]
programs = [ el for el in swPlat.getOwnedElement(Class) if hasStereotype(el, 'JUNIPERProgram') ]
if not hardwareModelIsMissingMessageBox(programs) :
	class InvalidHardwareModelException(Exception):
		pass
	raise InvalidHardwareModelException()
 
projectName = hwPlat.getOwner().getName()

defaultLibFolder = getTagValue(swPlat, 'libfolder')
if not defaultLibFolder:
	defaultLibFolder = 'lib'

cmdLineOptionsValues = swPlat.getTagValues('JuniperIDE','javacmdline')
if cmdLineOptionsValues:
    cmdLineOptions = " ".join(cmdLineOptionsValues)
else:
    cmdLineOptions = ""

jdesigner = Modelio.getInstance().getModuleService().getPeerModule("JavaDesigner")
config = jdesigner.getConfiguration()
genPath = config.getProjectSpacePath().toString() + "/code/"+projectName
    
defaultClassPath = '.:`pwd`/'+defaultLibFolder+'/commons-lang-2.6.jar:`pwd`/'+defaultLibFolder+'/commons-logging-1.2.jar:`pwd`/'+defaultLibFolder+'/javadesigner.jar:`pwd`/'+defaultLibFolder+'/mpi.jar:`pwd`/'+defaultLibFolder+'/JuniperAPI.1.149.jar:`pwd`/'+defaultLibFolder+'/juniper-platform-20150907_1727-SOFT.jar:`pwd`/'+defaultLibFolder+'/async-http-client-1.7.7.jar:`pwd`/'+defaultLibFolder+'/commons-logging-1.2.jar:`pwd`/'+defaultLibFolder+'/httpclient-4.1.jar:`pwd`/'+defaultLibFolder+'/httpcore-4.1.jar:`pwd`/'+defaultLibFolder+'/json-simple-1.1.jar:`pwd`/'+defaultLibFolder+'/javadesigner.jar:`pwd`/'+defaultLibFolder+'/MonLib-20150416.jar:`pwd`/'+defaultLibFolder+'/amqp-client-3.1.4.jar:`pwd`/'+defaultLibFolder+'/jackson-core-2.3.1.jar:`pwd`/'+defaultLibFolder+'/jackson-databind-2.3.1.jar:`pwd`/'+defaultLibFolder+'/jackson-annotations-2.3.0.jar:`pwd`/'+defaultLibFolder+'/postgresql-9.4-1201.jdbc4.jar:`pwd`/'+defaultLibFolder+'/mongo-java-driver-2.12.3.jar:`pwd`/'+defaultLibFolder+'/rmq-commons-1.9.jar:`pwd`/'+defaultLibFolder+'/juniper-sa-monitoring-agent-0.1-SNAPSHOT-jar-with-dependencies.jar:`pwd`/bin'

libraries = swPlat.getTagValues('JuniperIDE','libraries')
if libraries:
	stringLib =  ":".join(libraries)
	defaultClassPath = defaultClassPath + ':'+ stringLib

import os
try:
    os.makedirs(genPath)
except: # it raises an error if the directory already exists
    pass

try:
    os.makedirs(genPath+"/src")
except:  # it raises an error if the directory already exists
    pass

hostsFileContent = ''

setBusinessObjectsAsSerializable(swPlat)

# generate application model

app = ET.Element('application')
app.set('name', model.getName())

progModelTag = ET.SubElement(app, 'ProgramModel')
deplModelTag = ET.SubElement(app, 'DeploymentModel')
topoModelTag = ET.SubElement(app, 'GroupModel')

commModelTag = ET.SubElement(app, 'CommunicationModel')

mpiGlobalRank = 0
mpiGroups = {}

# VALIDATION: each Juniper Program can only be instantiated ONCE!
# Set up program groups and ranks
for node in [ node for node in hwPlat.getDeclared() if hasStereotype(node, 'CloudNode') ]:
	mpiLocalRank = 0
	for programInst in [program for program in node.getPart() if hasStereotype(program, 'ProgramInstance') \
																	and hasStereotype(program.getBase(), 'JUNIPERProgram')]:
		program = programInst.getBase()

		if not program in mpiGroups.keys():
			mpiGroups[program] = []

		groupName = 'group_' + node.getName()
		mpiGroupTag = ET.SubElement(topoModelTag, 'mpigroup')
		mpiGroupTag.set('name',  groupName)
		mpiGroups[program].append(groupName)		

		for i in range(max(1,int(node.getMultiplicityMin()))):
			cloudNode = ET.SubElement(deplModelTag, 'cloudnode')

			ipaddrs = getTagValues(node, 'ip')
			if len(ipaddrs) > i:
				ipaddr = ipaddrs[i]
			else:
				ipaddr = '127.0.0.1'

			hostsFileContent += ipaddr + '\n'
			cloudNode.set('hostipaddr', ipaddr)
			cloudNode.set('mpiglobalrank', str(mpiGlobalRank))
				
			memberTag = ET.SubElement(mpiGroupTag, 'member')
			memberTag.set('mpiglobalrank', str(mpiGlobalRank))
			memberTag.set('mpilocalrank', str(mpiLocalRank))
			memberTag.set('programName', program.getName())
	
			mpiGlobalRank = mpiGlobalRank + 1
			mpiLocalRank  = mpiLocalRank  + 1

numberOfPrograms = mpiGlobalRank

for program in mpiGroups.keys():
	programTag = ET.SubElement(progModelTag, 'program')
	programTag.set('name', program.getName())
	programTag.set('javaclass', getFullClassName(program))

# Handles inter program connection
connection = 0	
connections = []
for program in mpiGroups.keys():
	p = [ (rend.getConsumer().getRequiring().getInternalOwner(), iface) \
		for port in program.getInternalStructure()\
		for prov in  port.getProvided()\
		for iface in prov.getProvidedElement() \
		for pend in prov.getNaryConsumer()\
		for rend in pend.getNaryLink().getNaryLinkEnd() if rend is not pend and rend.getConsumer()]

	for (jclass, interface) in p:
		for groupJ in mpiGroups[program]:
			for groupI in mpiGroups[jclass]:
				if not (groupI, groupJ) in connections:
					connections.append((groupI, groupJ))
					connectionName = 'connection_' + groupI + '_' + groupJ

					dataCTag = ET.SubElement(commModelTag, 'dataconnection')
					dataCTag.set('name', connectionName)
					dataCTag.set('sendingGroup', groupI)
					dataCTag.set('receiverMpiGroup', groupJ)

					nodeJ = [ inst.getCluster() for inst in program.getRepresenting()  ] [0]
					nodeI = [ inst.getCluster() for inst in jclass.getRepresenting()  ] [0]

					multI = int(nodeI.getMultiplicityMin())
					multJ = int(nodeJ.getMultiplicityMin())

					if multI == multJ:
						dataCTag.set('type', 'symmetric')

						# for each symmetric data connection generate a new one on the other direction for method returns
						dataCTag = ET.SubElement(commModelTag, 'dataconnection')
						dataCTag.set('name', connectionName + '_return')
						dataCTag.set('sendingGroup', groupJ)
						dataCTag.set('receiverMpiGroup', groupI)
						dataCTag.set('type', 'symmetric')
					elif multI > 1 and multJ == 1:
						dataCTag.set('type', 'all_to_one')
					elif multI == 1 and multJ > 1:
						dataCTag.set('type', 'one_to_all')
					else:
						dataCTag.set('type', 'unsupported_' + str(multI) + '_' + str(multJ))
	
# Here we finally generate some code ;)
for program in programs:
    p = [ (rend.getConsumer().getRequiring().getInternalOwner(), iface) \
		for port in program.getInternalStructure()\
		for prov in  port.getProvided()\
		for iface in prov.getProvidedElement() \
		for pend in prov.getNaryConsumer()\
		for rend in pend.getNaryLink().getNaryLinkEnd() \
				if rend is not pend and rend.getConsumer() and rend.getConsumer().getRequiring().getInternalOwner()]

    r = [ (pend.getProvider().getProviding().getInternalOwner(), iface) \
		for port in program.getInternalStructure()\
		for req in  port.getRequired()\
		for iface in req.getRequiredElement() \
		for rend in req.getNaryProvider()\
		for pend in rend.getNaryLink().getNaryLinkEnd() \
				if pend is not rend and pend.getProvider() and pend.getProvider().getProviding().getInternalOwner()]
	
    for (jclass, iface) in p:
		ifname = iface.getName()
		fjcname = getFullClassName(jclass)
		fifname = getFullInterfaceName(iface)	
		vname = applyToFirstLetter(ifname, unicode.lower)+"Impl"
    
		# TODO: update this attribute somehow
		jatts = [ x for x in program.getOwnedAttribute() if x.getName() == vname]
		if len(jatts)==0:
		   jatt = createAttribute(program, vname, iface, "")
		   jatt.setValue("new " + fifname + "() {}")
		   note = modelingSession.getModel().createNote("JavaDesigner", "JavaAnnotation", jatt, "@Provided")
		   note.setMimeType('text/plain')
		   addTagValue(program, "JavaImport", "org.modelio.juniper.platform.Provided")
		else:
		   jatt = jatts[0]

    storagePrograms = [ pend.getProvider().getProviding().getInternalOwner()
            for port in program.getInternalStructure()\
            for req in port.getRequired()\
            for rend in req.getNaryProvider()\
            for pend in rend.getNaryLink().getNaryLinkEnd()
                                       if pend is not rend and\
                                           pend.getProvider() and\
                                           pend.getProvider() and\
                                           pend.getProvider().getProviding().getInternalOwner() and\
                                           hasStereotype(pend.getProvider().getProviding().getInternalOwner(), 'JUNIPERStorageProgram')\
    ]

    for storageProgram in storagePrograms: 
    	vname = applyToFirstLetter(storageProgram .getName(), unicode.lower)
    	jatts = [ x for x in program.getOwnedAttribute() if x.getName() == vname]

    	if len(jatts)==0:
    	   jatt = createAttribute(program, vname, storageProgram,"" )
    	   jatt.setValue("new " + storageProgram.getName() + "()")

    rank = mpiGroups[program][0]  # only one instance per program supported for now

    for (jclass, iface) in r:
		ifname = iface.getName()
		fifname = getFullInterfaceName(iface)
		fjcname = getFullClassName(jclass)
		vname = applyToFirstLetter(jclass.getName() + ifname, unicode.lower)

		jatt = createAttribute(program, vname, iface, \
				"(" + fifname + ") communicationToolkit.getProxyToInterface("+fjcname+".class, " + fifname + ".class)")

# Now time to generate the miriad of helper files and scripts
# First the ones that are not dependent on Jamaica / not Jamaica
with open(genPath+'/src/excludeList', 'w') as f:
     interfaces = [ el for el in swPlat.getOwnedElement(Interface) ]
     for interface in interfaces:
        for toExclude in [dep.getDependsOn() for dep in interface.getDependsOnDependency() if hasStereotype(dep, 'excludes') ]:
        	f.write('{0},{1}#{2}\n'.format(getFullClassName(interface),  getFullClassName(toExclude.getOwner()), toExclude.getName()))
        for operation in interface.getOwnedOperation():
        	for toExclude in [dep.getDependsOn() for dep in operation.getDependsOnDependency() if hasStereotype(dep, 'excludes') ]:
        		f.write('{0}#{1},{2}#{3}\n'.format(getFullClassName(interface), operation.getName(), \
														getFullClassName(toExclude.getOwner()), toExclude.getName()))
with open(genPath+'/hosts', 'w') as f:
	f.write(hostsFileContent)

with open(genPath+'/rte_sync.sh', 'w') as f:
	f.write("#!/bin/bash\n\n")
	f.write("app_path=`pwd`\n")
	f.write("cat hosts |\n")
	f.write("while read -r host ; do\n")
	f.write("    echo Deploying on $host at $app_path\n")
	f.write("    rsync -ru $app_path/* $host:$app_path\n")
	f.write("done\n")
#new
with open(genPath+'/rte_sync2.sh', 'w') as f:
	f.write("#!/bin/bash\n\n")
	f.write("app_path=`pwd`\n")
	f.write("echo Make sure the application is compiled\n")
	f.write("while read host || [ -n \"$host\" ]\ndo\n")
	f.write("    echo Deploying on $host at $app_path\n")
	f.write("    rsync -rua $app_path/* $host:$app_path\n")
	f.write("done < hosts\n")
	
with open(genPath+'/rte_deployment_plan.xml', 'w') as f:
	f.write('<?xml version="1.0"?>' + ET.tostring(app, encoding='utf-8'))

# Running the application without Jamaica
with open(genPath+'/rte_compile.sh', 'w') as f:
	f.write('#!/bin/bash\n\n')
	f.write('if [ -d "bin" ]; then\n')
	f.write('	rm -r bin/*\n')
	f.write('else\n')
	f.write('	mkdir bin\n')
	f.write('fi\n\n')
	f.write('files=`find src -type f -name \'*.java\'`\n')
	f.write('mpijavac $files -d bin -cp '+defaultClassPath+' -Xlint:unchecked\n')

with open(genPath+'/rte_run.sh', 'w') as f:
	f.write('mpirun -machinefile hosts -np '+str(numberOfPrograms)+' java -cp '+defaultClassPath+' ' + cmdLineOptions + ' eu.juniper.platform.Rte `pwd`/rte_deployment_plan.xml')

# Now we generate Jamaica specific files
with open(genPath+'/rte_deployment_plan_jamaica_profiling.xml', 'w') as f:
	for node in app.findall(".//cloudnode"):
		node.set('hostipaddr', '127.0.0.1') # Running all Juniper programs in the current VM
	f.write('<?xml version="1.0"?>' + ET.tostring(app, encoding='utf-8'))

with open(genPath+'/jamaica.mk', 'w') as f:
	f.write('ll: target/linux-x86_64/OnlineBuild\n')
	f.write('\n')
	f.write('run: target/linux-x86_64/OnlineBuild\n')
	f.write('        ./jamaica_run.sh\n')
	f.write('\n')
	f.write('target/linux-x86_64/OnlineBuild: Rte-0.prof\n')
	f.write('        ant -f jamaica_ant.xml\n')
	f.write('\n')
	f.write('Rte-0.prof: bin/\n')
	f.write('        sleep 30 && pkill -2 jamaicavm &\n')
	f.write('        -./jamaica_run.sh -profile\n')
	f.write('\n')
	f.write('clean:\n')
	f.write('	rm -f target/linux-x86_64/OnlineBuild\n')
	f.write('	rm -f *.prof\n')

with open(genPath+'/rte_jamaica_run.sh', 'w') as f:
	f.write('#!/bin/bash\n')
	f.write('if [ "$1" = "-profile" ]; then\n')
	f.write('  mpirun -np '+str(numberOfPrograms)+' bash -c \'/usr/local/jamaica/bin/jamaicavmp -cp '+defaultClassPath+' -XprofileFilename Rte-$OMPI_COMM_WORLD_RANK.prof ' + cmdLineOptions + ' eu.juniper.platform.Rte rte_deployment_plan_jamaica_profiling.xml\'\n')
	f.write('else\n')
	f.write('  mpirun -np '+str(numberOfPrograms)+' ' + cmdLineOptions + ' target/linux-x86_64/OnlineBuild rte_deployment_plan.xml\n')
	f.write('fi\n')

if not os.path.exists(genPath+'/jamaica_build.properties'):
	with open(genPath+'/jamaica_build.properties', 'w') as f:
		f.write('jamaicaInstallationDir=c:\\\\Program Files (x86)\\\\Jamaica-6.3-1\n')
		f.write('online.classpath=bin:'+defaultClassPath+'\n')
		#f.write('offline.classpath=bin;C:\\\\Users\\\\malmeida\\\\workspace\\\\OfflineMPI\\\\mpi.jar;C:\\\\Users\\\\malmeida\\\\workspace\\\\JUNIPERCodeGenerationHelper\\\\target\\\\JuniperIDECodeGenerationHelper-0.1.jar\n')
		#f.write('offline.target=windows-x86\n')
		#f.write('offline.main=sampleWrapper.OfflineMain\n')
		f.write('online.target=linux-x86_64\n')
		f.write('accesspoint.keyfile=\n')
		f.write('accesspoint.address=\n')
		f.write('accesspoint.username=\n')
		#f.write('deployment.path=\n')

f = open(genPath+'/jamaica_ant.xml', 'w')
project = ET.Element('project')
project.set('basedir', '.')
project.set('default', 'build_online_main')

property = ET.SubElement(project, 'property')
property.set('file', 'jamaica_build.properties')

pathTag = ET.SubElement(project, 'path')
pathTag.set('id', 'jamaica.classpath')
fileSetTag = ET.SubElement(pathTag, 'fileset')
fileSetTag.set('file', '${jamaicaInstallationDir}\\lib\\JamaicaTools.jar')

taskdef = ET.SubElement(project, 'taskdef')
taskdef.set('classname', 'com.aicas.jamaica.tools.ant.JamaicaTask')
taskdef.set('classpathref', 'jamaica.classpath')
taskdef.set('name', 'jamaicabuilder')

# build_online_all TASK
targetAllOn = ET.SubElement(project, 'target')
targetAllOn.set('name', 'build_online_main')

jbuilder = ET.SubElement(targetAllOn, 'jamaicabuilder')
jbuilder.set('jamaica', '${jamaicaInstallationDir}')

ttarget  = ET.SubElement(jbuilder, 'target')
ttarget.set('value', '${online.target}')

main     = ET.SubElement(jbuilder, 'main')
main.set('value', 'eu.juniper.platform.Rte')

destination = ET.SubElement(jbuilder, 'destination')
destination.set('value', 'target/${online.target}/OnlineBuild')

tmpdir   = ET.SubElement(jbuilder, 'tmpdir')
tmpdir.set('value', 'tmp')

classpath = ET.SubElement(jbuilder, 'classpath')
classpath.set('append', 'true')
classpath.set('value', '${online.classpath}')

userProfile = ET.SubElement(jbuilder, 'userProfile')
userProfile.set('append', 'true')
userProfile.set('value', ':'.join(['Ret-'+str(rank)+'.prof' for rank in range(numberOfPrograms)]))

includeJAR = ET.SubElement(jbuilder, 'includeJAR')
includeJAR.set('append', 'true')
includeJAR.set('value', '${online.classpath}')

# deploy ANT TASK
targetDeploy = ET.SubElement(project, 'target')
targetDeploy.set('name', 'deploy')
targetDeploy.set('description', '')

zip = ET.SubElement(targetDeploy, 'zip')
zip.set('destfile', 'target.zip')
zip.set('basedir', 'target/')

for node in hwPlat.getDeclared():
	for ip in getNodeIP(node):
		scp = ET.SubElement(targetDeploy, 'scp')
		scp.set('file', 'target.zip')
		scp.set('todir', 'root@'+ip+':${deployment.path}')
		scp.set('keyfile', '${accesspoint.keyfile}')
		scp.set('forwardingHost', '${accesspoint.address}')
		scp.set('forwardingUserName', '${accesspoint.username}')
		scp.set('passphrase', '')
		scp.set('trust', 'on')
		scp.set('verbose', 'on')

f.write('<?xml version="1.0"?>' + ET.tostring(project, encoding='utf-8'))
f.close()

# Make Jdesigner re-generate Java files
from org.modelio.api.modelio import Modelio
from org.modelio.module.javadesigner.api import JavaDesignerParameters
config.setParameterValue(JavaDesignerParameters.GENDOCPATH, "$(Project)/code/"+projectName+"/doc")
config.setParameterValue(JavaDesignerParameters.GENERATIONPATH, "$(Project)/code/"+projectName+"/src")
config.setParameterValue(JavaDesignerParameters.JARFILEPATH, "$(Project)/code/"+projectName+"/src")
config.setParameterValue(JavaDesignerParameters.JAVAHGENERATIONPATH, "$(Project)/code/"+projectName+"/src")

from org.eclipse.swt.widgets import Display
from java.lang import Runnable

class RunGeneration(Runnable):
    def __init__(self):
        pass

    def run(self):
    	jdesigner.generate(swPlat, True)

Display.getDefault().asyncExec(RunGeneration())
