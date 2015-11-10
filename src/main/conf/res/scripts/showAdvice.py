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
from tempfile import NamedTemporaryFile
from java.awt import Desktop
from java.io import File

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

def findReferredObj(advice, attId, objId):
    return [ dep.getDependsOn() for dep in advice.getDependsOnDependency() if getTagValue(dep, 'objAttId') == attId and getTagValue(dep, 'objId') == objId]

def findReferredAttachment(advice, attId):
	return [attachment for attachment in advice.getOwner().getOwnedElement() if getTagValue(attachment, 'id') == attId]
 #   #[ dep.getDependsOn() for dep in advice.getDependsOnDependency() if getTagValue(dep, 'attId') == attId]


advice = selectedElements.get(0)

originalXML = str(advice.getDescriptor()[0].getContent())
tree = ET.fromstring(originalXML)

output = NamedTemporaryFile(suffix='.html', delete=False)
print output.name

output.write('<html>\n')
output.write('<head><title>' + advice.getName() +'</title></head>\n')
output.write('<body style="background-color: #ffffe1; font-family: verdana; font-size:12px;">\n')

def interpretElement(advice, element):
    if element.tag == '{http://www.fit.vutbr.cz/homes/rychly/juniper/scheduling-advisor}objectRef':
        attId = element.get('attId')
        objId = element.get('objId')
        refObj = findReferredObj(advice, attId, objId)
        print attId, objId, refObj

        if refObj:
            output.write('<b>' + refObj[0].getName() + '</b>')
        else:
            output.write('<b>object ' + objId + ' from attachment ' + attId + '</b>')
    elif element.tag == '{http://www.fit.vutbr.cz/homes/rychly/juniper/scheduling-advisor}attachmentRef':
        attId = element.get('attId')
        refAtt = findReferredAttachment(advice, attId)

        print refAtt, attId

        #output.write('<a href="')
        #if refAtt:
            #output.write(getTagValue(refAtt[0], 'filename', getTagValue(refAtt[0], 'id')) )
        #else:
            #output.write(attId)
        #output.write('">')

        if element.text:
           output.write('<b>' + element.text + '</b>')
        else:
             if refAtt:
                output.write(refAtt[0].getName())
             else:
                output.write(attId)
        output.write(' (attachment)')                
        #output.write('</a>')

    elif element.tag == '{http://www.fit.vutbr.cz/homes/rychly/juniper/scheduling-advisor}link':
        output.write('<a href="'+element.get('{http://www.w3.org/1999/xlink}href')+'">' + element.text + '</a>')

for tag in tree:
    if tag.tag == '{http://www.fit.vutbr.cz/homes/rychly/juniper/scheduling-advisor}problem':
       output.write('<h3>Problem</h3>\n')
    if tag.tag == '{http://www.fit.vutbr.cz/homes/rychly/juniper/scheduling-advisor}solution':
       output.write('<h3>Solution</h3>\n')
    if tag.tag == '{http://www.fit.vutbr.cz/homes/rychly/juniper/scheduling-advisor}note':
       output.write('<h3>Note</h3>\n')
    if tag.tag == '{http://www.fit.vutbr.cz/homes/rychly/juniper/scheduling-advisor}sources':
       output.write('<h3>Sources</h3>\n')
       
    if tag.text:
    	output.write(str(tag.text))
    for element in tag:
       interpretElement(advice, element)
       if element.tail:
           output.write(str(element.tail))

output.write('</body>\n')
output.write('</html>')
output.close()

from org.eclipse.jface.dialogs import PopupDialog
from org.eclipse.swt.widgets import Shell, Display
from org.eclipse.swt.browser import Browser
from org.eclipse.swt.layout import GridLayout, GridData
from org.eclipse.swt import SWT
from java.lang import Runnable

class AlertDialog(PopupDialog):
      def __init__(self, advice):
          PopupDialog.__init__(self, 
                               Shell(),
                               PopupDialog.INFOPOPUPRESIZE_SHELLSTYLE, 
                               True, False, True, False, 
                               'Details about \'' + advice.getName() + '\'', 'Juniper IDE')

      def createDialogArea(self, parent):
          composite = self.super__createDialogArea(parent)

          glayout = GridLayout(1, False)
          composite.setLayout(glayout)

          data = GridData(SWT.FILL, SWT.FILL, True, True);
          data.widthHint = 800;
          data.heightHint = 350;
          composite.setLayoutData(data);

          browser = Browser(composite, SWT.NONE)
          browser.setUrl(File(output.name).toURI().toString())
          browser.setLayoutData(GridData(SWT.FILL, SWT.FILL, True, True));

          return composite

class ShowDialog(Runnable):
      def __init__(self, advice):
          self.advice = advice
      def run(self):
          AlertDialog(self.advice).open()

Display.getDefault().syncExec(ShowDialog(advice))