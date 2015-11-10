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

def hasStereotype(el, stn):
                 for stereo in el.getExtension():
                                 if stereo.getName() == stn:
                                                 return True
                 return False

def putStereotype(el, st):
    stEl = modelingSession.getMetamodelExtensions().getStereotype(".*", st, el.getMClass());
    el.getExtension().add(stEl)

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

def hasTagValue(el, tag):
    return len([x for x in el.getTag() if x.getDefinition().getName() == tag])>0

def getJavaClassName(jclass):
	packageName = getTagValue(jclass.getOwner(), 'JavaName')
	if packageName:
		packagePrefix = packageName + '.'
	else:
		packagePrefix = ''
	return packagePrefix+jclass.getName()

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

def getAdviceFilename():
    from org.eclipse.swt.widgets import FileDialog, Display
    from org.eclipse.swt import SWT
    from java.lang import Runnable

    class ShowDialog(Runnable):
          def run(self):
              dialog = FileDialog(Display.getDefault().getActiveShell(), SWT.SAVE)
              self.filename = dialog.open()

    selectDialogRun = ShowDialog()
    Display.getDefault().syncExec(selectDialogRun)

    return selectDialogRun.filename

filename = getAdviceFilename()

if not filename:
   sys.exit()

tree = ET.parse(filename)
root = tree.getroot()
advicesPackage = selectedElements.get(0)
model = advicesPackage.getOwner()

def processObjIds(idsDict, root, tag):
    def findInXML(root, attributeSelectorName, attributeSelectorValue, attributeReturn):
	   return [tag.get(attributeReturn) for tag in root.iter() if tag.get(attributeSelectorName) == attributeSelectorValue]
    def findJuniperProgram(root, mpiglobalrank):
    	programName = findInXML(root, 'mpiglobalrank', mpiglobalrank, 'programName')[0]
    	javaClass = findInXML(root, 'name', programName, 'javaclass')[0]
        return javaClass
       
    def getJuniperId(tag):
        if tag.tag == 'program':
           return ('program', str(tag.get('javaClass')))
        elif tag.tag == 'cloudNode' or tag.tag == 'cloudnode':
           return ('program', findJuniperProgram(root, tag.get('mpiglobalrank')))
        elif tag.tag == 'cpu':
           return ('cpu', str(tag.get('id')))
        else:
           return ('unknown', tag)

    objId = tag.get('{http://www.fit.vutbr.cz/homes/rychly/juniper/scheduling-advisor}objId')
    if objId is not None:
       idsDict[objId] = getJuniperId(tag)

    for subtag in tag:
        processObjIds(idsDict, root, subtag)

def findReferredElement(element, ref):
    def getObjRef(element):
        if hasStereotype(element, 'JUNIPERProgram'):
           return ('program', str(getJavaClassName(element)))
        elif hasStereotype(element, 'CloudNode'):
           return ('cloudNode', str(element.getName()))
        elif hasStereotype(element, 'CloudNodeCPU'):
           return ('cpu', str(element.getUuid().toString()))
        else:
           return ('unknown', element)

    if getObjRef(element) == ref:
       return element

    for subelement in element.getOwnedElement():
        found = findReferredElement(subelement, ref)
        if found:
           return found
    
    return None

print 'attachments: '

attObjIds = {}
attClasses = {}

for attachment in [attachment for attachment in root if attachment.tag == '{http://www.fit.vutbr.cz/homes/rychly/juniper/scheduling-advisor}attachment']:
    contentType = attachment[0].get('{http://www.w3.org/2005/05/xmlmime}contentType')
    attId = attachment.get('attId')
    filename = attachment.get('filename')
    print attId, filename, contentType

    if filename:
        attachmentName = filename
    else:
        attachmentName = attId

    attachmentClass = modelingSession.getModel().createClass(attachmentName, advicesPackage)
    putStereotype(attachmentClass, 'Attachment')
    attachmentClass.putTagValue('JuniperIDE', 'id', attId) # id not unique :(
    attachmentClass.putTagValue("JuniperIDE", 'filename', str(filename)) # can't use setTagValue, name not unique :(
    attachmentClass.putTagValue("JuniperIDE", 'contentType', contentType) # can't use setTagValue, name not unique :(

    attClasses[attId] = attachmentClass

    if contentType == 'application/xml':
       contentTag = attachment[0][0]
       content = ET.tostring(contentTag, encoding='utf-8')

       objIds = {}
       processObjIds(objIds, contentTag, contentTag)
       attObjIds[attId] = objIds

       note = modelingSession.getModel().createNote("JuniperIDE", "content", attachmentClass, content)
       note.setMimeType('text/plain')
    else:
       # just ignore the other types for now
       # I can't/won't do anything with them anyway ;)
       pass

print attObjIds

adviceCounter = 0

print 'advices: '
for advice in [advice for advice in root if advice.tag == '{http://www.fit.vutbr.cz/homes/rychly/juniper/scheduling-advisor}advice']:
    print advice.get('category'), advice.get('severity')

    adviceClass = modelingSession.getModel().createClass('advice'+str(adviceCounter), advicesPackage)
    adviceCounter = adviceCounter + 1

    adviceClass.addStereotype('JuniperIDE', 'Advice') # for some reason, putStereotype doesn't work
    adviceClass.putTagValue('JuniperIDE', 'category', advice.get('category'))
    adviceClass.putTagValue('JuniperIDE', 'severity', advice.get('severity'))

    note = modelingSession.getModel().createNote("JuniperIDE", "originalXML", adviceClass,  ET.tostring(advice, encoding='utf-8'))
    note.setMimeType('text/plain')
    referredElements = []

    for tag in advice:
        if tag.tag == '{http://www.fit.vutbr.cz/homes/rychly/juniper/scheduling-advisor}problem':
           print tag.text
           for element in tag:
               if element.tag == '{http://www.fit.vutbr.cz/homes/rychly/juniper/scheduling-advisor}objectRef':
                    attId = element.get('attId')
                    objId = element.get('objId')
                    print attId, objId
                    if attId in attObjIds and objId in attObjIds[attId]:
                        ref = attObjIds[attId][objId]
                        refObj = findReferredElement(model, ref)
                        print 'objectRef', ref, refObj
                        
                        if refObj and not refObj in referredElements:
                          referredElements.append(refObj)
                          dep = modelingSession.getModel().createDependency(adviceClass, refObj, "JuniperIDE", "ObjectReference")
                          dep.putTagValue('JuniperIDE', 'objAttId', attId) # attId not unique :(
                          setTagValue(dep, 'objId', objId)
               elif element.tag == '{http://www.fit.vutbr.cz/homes/rychly/juniper/scheduling-advisor}attachmentRef':
                    attId = element.get('attId')
                    print 'attachmentRef', attId, element.text

                    dep = modelingSession.getModel().createDependency(adviceClass, attClasses[element.get('attId')], "JuniperIDE", "AttachmentReference")
                    dep.putTagValue("JuniperIDE", 'attId', attId) # attId not unique :(
               else:
                    print dir(element)

               print element.tail
