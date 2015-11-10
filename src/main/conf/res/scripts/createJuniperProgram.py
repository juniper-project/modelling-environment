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
# selection:
# SoftwareArchitectureModel package
el = selectedElements.get(0)

# output:
# creates a JUNIPER program

from org.modelio.metamodel.uml.behavior.activityModel import \
                OpaqueAction, ObjectFlow, AcceptSignalAction, \
                AcceptTimeEventAction, ActivityFinalNode, ActivityPartition, \
                ControlFlow, OutputPin, InputPin
from org.modelio.metamodel.uml.statik import Operation, Association, Class, KindOfAccess
from modelling import applyToFirstLetter, putStereotype, putStereotypeFirst, \
                      addTagValue, setTagValue, getTagValues, getTagValue, \
                      hasTagValue, hasTagValueSuch, getTargets, createTraceabilityLink 

def createJavaClass(el, name):
    jclass = modelingSession.getModel().createClass(name, el.getOwner())
    jclass.addStereotype("JavaDesigner", "JavaClass")        
    return jclass

def createConstant(jclass, name, type, value):
    existing = [ x for x in jclass.getOwnedAttribute() if x.getName() == name] 
    if len(existing) == 0:
        jatt = modelingSession.getModel().createAttribute(name, type, jclass)
        jatt.setIsClass(True)
        jatt.setValue(str(value))
        jatt.setChangeable(KindOfAccess.ACCESNONE)
        return jatt
    else:
        return existing[0]
        
def createOperation(jclass, name, code):
    existing = [ x for x in jclass.getOwnedOperation() if x.getName() == name] 
    if len(existing) == 0:
        jop = modelingSession.getModel().createOperation(name, jclass)
        jop.removeNotes("JavaDesigner", "JavaCode")
        note = modelingSession.getModel().createNote("JavaDesigner", "JavaCode", jop, code)
        note.setMimeType('text/plain')
        return jop
    else:
        return existing[0]

def createParameterIO(jop, name):
    existing = [ x for x in jop.getIO() if x.getName() == name] 
    if len(existing) == 0:
        jpar = modelingSession.getModel().createParameter()
        jpar.setName(name)
        jop.getIO().add(jpar)
        return jpar
    else:
        return existing[0]

def createParameterReturn(jop):
    if jop.getReturn() is  None:
        jpar = modelingSession.getModel().createParameter()
        jop.setReturn(jpar)
        return jpar
    else:
        return jop.getReturn()

def makeTypeSerializable(jclass):
    if not hasTagValueSuch(jclass, "JavaImplements", lambda x : "Serializable" in x):
        addTagValue(jclass, "JavaImplements", "java.io.Serializable")

def getJavaMethodName(el):
    name = el.getName()
    if " " in name:
        title = "".join(name.title().split())
    else:
        title = name
    return applyToFirstLetter(title, unicode.lower)


def getJavaClassName(el):
    return applyToFirstLetter(getJavaMethodName(el), unicode.upper)

putStereotype(el, 'JavaPackage')

#if not hasTagValue(el, "JavaName"):
	#addTagValue(el, "JavaName", "juniperApplication")

jclass = createJavaClass(el, 'JuniperProgram')
jclass.setOwner(el)
#addTagValue(jclass, "JavaImport", "java.util.logging.Logger")
addTagValue(jclass, "JavaExtends", "org.modelio.juniper.platform.JuniperProgram")
#addTagValue(jclass, "JavaImport", "mpi.MPI")
#addTagValue(jclass, "JavaImport", "org.modelio.juniper.CommunicationToolkit")

putStereotype(jclass, 'ResourceUsage_ModelElement')

#rankAtt = createConstant(jclass, "RANK", modelingSession.getModel().getUmlTypes().getINTEGER(), '0')
#addTagValue(rankAtt, "JavaFinal", "true")

# create log attribute
#logatt = modelingSession.getModel().createAttribute()
#logatt.setName("log")
#logatt.setOwner(jclass)
#logatt.setIsClass(True)
#logatt.setValue("Logger.getLogger(JuniperProgram.class.getName())")
#logatt.setChangeable(KindOfAccess.ACCESNONE)
#addTagValue(logatt, "JavaFinal", "true")
#addTagValue(logatt, "JavaTypeExpr", "Logger")

# create toolkit attribute
#tktatt = modelingSession.getModel().createAttribute()
#tktatt.setName("communicationToolkit")
#tktatt.setOwner(jclass)
#tktatt.setIsClass(True)
#tktatt.setValue("new CommunicationToolkit()")
#tktatt.setChangeable(KindOfAccess.ACCESNONE)
#addTagValue(tktatt, "JavaFinal", "true")
#addTagValue(tktatt, "JavaTypeExpr", "CommunicationToolkit")

putStereotype(jclass, 'RtUnit_Class')
putStereotypeFirst(jclass, 'JUNIPERProgram')

# generate main & execute
#mainOp = createOperation(jclass, "main", "\t\t\tMPI.Init(args);\n\t\t\tinitProvidedInterfaces();\n\t\t\twhile(true) {\n\t\t\t\tThread.yield();\n\t\t\t\tif (execute()) break;\n\t\t\t}\n\t\t\tMPI.Finalize();\n")
#mainOp.setIsClass(True)
#par = createParameterIO(mainOp, "args")
#par.setMultiplicityMax("*")
#par.setType(modelingSession.getModel().getUmlTypes().getSTRING())
#setTagValue(mainOp, "JavaThrownException", "java.lang.Exception")        
#setTagValue(par, "type", "Array")
        
#initProvided = createOperation(jclass, "initProvidedInterfaces", "")
#initProvided.setIsClass(True)

executeOp = createOperation(jclass, "execute", "// add your code here or remove this method")#\n\t\treturn true;\n")
#executeOp.setIsClass(True)
#par = createParameterReturn(executeOp)
#par.setType(modelingSession.getModel().getUmlTypes().getBOOLEAN())

port = modelingSession.getModel().createPort("MPI Communication Channel", jclass)
putStereotype(port, 'Channel')
putStereotype(port, 'RtFeature_Port')
putStereotype(port, 'ResourceUsage_ModelElement')

modelingSession.getModel().createNote("MARTEDesigner", "RtFeature_Port_specification", port, "")

createdElement = jclass
