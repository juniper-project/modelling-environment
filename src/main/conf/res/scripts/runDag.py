from subprocess import CalledProcessError

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

try: 
    dag_path = dag_path_parameter
except NameError:
    dag_path = '/media/sf_Dropbox/Projects/JUNIPER/WP5/libdag/dag'
        
try:
    input_path = input_path_parameter
except NameError:
    input_path = '/media/sf_Dropbox/Projects/JUNIPER/WP5/libdag/xml/taskset.xml'

import subprocess
try:
    output = subprocess.check_output([dag_path, input_path])
except CalledProcessError as e:
    output = e.output
    
    from org.eclipse.swt.widgets import MessageBox
    from org.eclipse.swt.widgets import Display
    from org.eclipse.swt import SWT
    
    m = MessageBox(Display.getCurrent().getActiveShell(), SWT.ICON_ERROR|SWT.OK)
    m.setText("JuniperIDE")
    m.setMessage("Error running Schedulability analyser!")
    m.open()
    
from tempfile import NamedTemporaryFile
output_file = NamedTemporaryFile(delete=False)
output_file.write(output)
output_file.close()

from org.modelio.api.modelio import Modelio
from org.modelio.api.editor import EditorType
from java.io import File
Modelio.getInstance().getEditionService().openEditor(selectedElements.get(0), File(output_file.name), EditorType.TXTEditor, True)

import os
os.remove(output_file.name)
