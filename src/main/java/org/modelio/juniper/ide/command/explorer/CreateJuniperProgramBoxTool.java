/**
 * Copyright 2014 Modeliosoft
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.modelio.juniper.ide.command.explorer;

import java.util.ArrayList;
import java.util.List;

import org.modelio.api.model.ITransaction;
import org.modelio.api.modelio.Modelio;
import org.modelio.api.module.IModule;
import org.modelio.juniper.ide.command.diagram.util.ElementCreatorCommand;
import org.modelio.metamodel.factory.ExtensionNotFoundException;
import org.modelio.metamodel.uml.infrastructure.ModelElement;
import org.modelio.metamodel.uml.infrastructure.Note;
import org.modelio.metamodel.uml.infrastructure.Stereotype;
import org.modelio.metamodel.uml.statik.Class;
import org.modelio.metamodel.uml.statik.NameSpace;
import org.modelio.metamodel.uml.statik.Operation;
import org.modelio.metamodel.uml.statik.Port;
import org.modelio.vcore.smkernel.mapi.MObject;

public class CreateJuniperProgramBoxTool extends ElementCreatorCommand {
	
		public boolean accept(List<MObject> selectedElements, IModule module) {
	   	 return true;
	    }
	
	    public void actionPerformed(List<MObject> selectedElements, IModule module) {
	    	ModelElement software = (ModelElement) selectedElements.get(0);
		 try (ITransaction transaction = Modelio.getInstance().getModelingSession().createTransaction("createJuniperProgramTool")){
			software.addStereotype("JavaDesigner", "JavaPackage");

			if (software.getTagValue("JavaDesigner", "JavaName") == null) {
				software.putTagValue(".*", "JavaName", "JuniperApplication");
			}

			Class jclass = Modelio.getInstance().getModelingSession().getModel()
					.createClass("JuniperProgram", (NameSpace) software);
			jclass.addStereotype("JavaDesigner", "JavaClass");

			jclass.putTagValue(".*", "JavaExtends",
					"org.modelio.juniper.platform.JuniperProgram");

			jclass.addStereotype("MARTEDesigner", "ResourceUsage_ModelElement");
			jclass.addStereotype("MARTEDesigner", "RtUnit_Class");
			Stereotype stereotype = Modelio.getInstance().getModelingSession()
					.getMetamodelExtensions()
					.getStereotype(".*", "JUNIPERProgram", jclass.getMClass());
			jclass.getExtension().add(0, stereotype);

			createOperation(jclass, "execute",
					"// add your code here or remove this method");
			Port port = Modelio.getInstance().getModelingSession().getModel()
					.createPort("MPI Communication Channel", jclass);
			port.addStereotype("JuniperIDE", "Channel");
			port.addStereotype("MARTEDesigner", "RtFeature_Port");
			port.addStereotype("MARTEDesigner", "ResourceUsage_ModelElement");

			Note note = Modelio.getInstance()
					.getModelingSession()
					.getModel()
					.createNote("MARTEDesigner",
							"RtFeature_Port_specification", port, "");
			note.setMimeType("text/plain");
			transaction.commit();
			
			setLastCreatedElement(jclass);
//			return jclass;
		} catch (Exception e) {			
			e.printStackTrace();
//			return null;
		}
	}

	private Operation createOperation(Class jclass, String name, String code) throws ExtensionNotFoundException {
		List<Operation> existing = new ArrayList<Operation>();
		for (Operation op : jclass.getOwnedOperation()) {
			if (op.getName() == name) {
				existing.add(op);
			}
		}
		if (existing.size() == 0) {
			Operation jop = Modelio.getInstance().getModelingSession()
					.getModel().createOperation(name, jclass);
			jop.removeNotes("JavaDesigner", "JavaCode");
			Note note =Modelio.getInstance().getModelingSession().getModel()
					.createNote("JavaDesigner", "JavaCode", jop, code);
			note.setMimeType("text/plain");
			return jop;
		} else {
			return existing.get(0);
		}
	}

}
