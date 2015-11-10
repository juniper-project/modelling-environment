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

# This module contains some helper functions in manipulating UML and JavaDesigner modules

from org.modelio.api.modelio import Modelio
modelingSession = Modelio.getInstance().getModelingSession()
#
# Manipulating tag values
#

def getTagValues(el, tagName):
    lists = [y.getActual() for y in el.getTag() if y.getDefinition().getName() == tagName]
    values = [x.getValue() for list in lists for x in list]
    return values

def getTagValue(el, tagName, default=None):
    list = getTagValues(el, tagName)
    if len(list)>0:
        return list[0]
    else:
        return default

def hasTagValue(el, tagName):
    return getTagValue(el, tagName) is not None

def hasTagValueSuch(el, tag, test):
    return len([x for x in getTagValues(el, tag) if test(x)])>0


def addTagValue(el, tag, value):
    el.putTagValue(".*", tag, value)

def setTagValue(el, tag, value):
    if hasTagValue(el, tag):    
        for x in el.getTag():
            if (x.getDefinition().getName() == tag):
                x.getActual()[0].setValue(value)
                break            
    else:
        addTagValue(el, tag, value)
#
# Manipulating stereotypes
#
def putStereotype(el, st):
    stEl = modelingSession.getMetamodelExtensions().getStereotype(".*", st, el.getMClass());
    el.getExtension().add(stEl)

def putStereotypeFirst(el, st):
    stEl = modelingSession.getMetamodelExtensions().getStereotype(".*", st, el.getMClass());
    el.getExtension().add(0, stEl)

def hasStereotype(el, stereotypeName):
    for stereo in el.getExtension():
        if stereo.getName() == stereotypeName:
            return True
    return False

def removeStereotype(el, stereotypeName):
	for stereo in el.getExtension():
		if stereo.getName() == stereotypeName:
			el.getExtension().remove(stereo)
			return

def copyStereotypes(frm, to):
	to.getExtension().addAll(frm.getExtension())


#
# Manipulating attributes
#

def getAttributeValue(el, attributeName, default=None):
	atts = [ att.getValue() for att in el.getOwnedAttribute() if att.getName() == attributeName]
	if atts: return atts[0]
	else: return default	

def hasAttributeValue(el, attributeName):
	return not getAttributeValue(el, attributeName, '') == ''  

#
# Manipulating dependencies
#

def getTargets(rule, stereo):
    targets =[dep.getDependsOn() \
      		for dep in  rule.getDependsOnDependency()\
		if hasStereotype(dep, stereo)]
    return targets

def getImpacts(rule, stereo):
    targets =[dep.getImpacted() \
      		for dep in  rule.getImpactedDependency()\
		if hasStereotype(dep, stereo)]
    return targets

def createTraceabilityLink(el, target):
	modelingSession.getModel().createDependency(el, target, ".*", "trace")

#
# Manipulating JavaDesigner modules
#

def applyToFirstLetter(s, f):
	return f(s[0]) + s[1:]

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

def getJavaClassName(el):
	parentName = getTagValue(el.getOwner(), 'JavaName')
	if parentName:
		parentPrefix = parentName + '.'
	else:
		parentPrefix = getJavaClassName(el.getOwner())+'.'
	return parentPrefix+getTagValue(el, 'JavaName', default=el.getName())

def createOperation(jclass, name):
    existing = [ x for x in jclass.getOwnedOperation() if x.getName() == name]
    if len(existing) == 0:
        jop = modelingSession.getModel().createOperation(name, jclass)
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

def createAttribute(jclass, name, type, value):
    existing = [ x for x in jclass.getOwnedAttribute() if x.getName() == name]
    jatt = None
    if len(existing) == 0:
        jatt = modelingSession.getModel().createAttribute(name, type, jclass)
        jatt.setIsClass(False)
    else:
        jatt =  existing[0]

    jatt.setValue(str(value))
    return jatt

def createAttributeJavaType(jclass, name, type, value):
    existing = [ x for x in jclass.getOwnedAttribute() if x.getName() == name]
    jatt = None
    if len(existing) == 0:
		jatt = modelingSession.getModel().createAttribute()
		jatt.setName(name)
		jatt.setOwner(jclass)
		jatt.setIsClass(False)
		addTagValue(jatt, "JavaTypeExpr", type)        
    else:
        jatt =  existing[0]

    jatt.setValue(str(value))
    return jatt
