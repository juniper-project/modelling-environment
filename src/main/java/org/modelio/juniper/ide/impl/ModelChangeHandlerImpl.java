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
package org.modelio.juniper.ide.impl;

import java.util.HashSet;
import java.util.Set;

import org.eclipse.swt.widgets.Display;
import org.modelio.api.diagram.IDiagramHandle;
import org.modelio.api.diagram.style.IStyleHandle;
import org.modelio.api.model.IModelingSession;
import org.modelio.api.model.ITransaction;
import org.modelio.api.model.change.IModelChangeEvent;
import org.modelio.api.model.change.IModelChangeHandler;
import org.modelio.api.modelio.Modelio;
import org.modelio.api.module.IModule;
import org.modelio.metamodel.diagrams.AbstractDiagram;
import org.modelio.metamodel.diagrams.StaticDiagram;
import org.modelio.metamodel.factory.ExtensionNotFoundException;
import org.modelio.metamodel.uml.behavior.activityModel.OpaqueAction;
import org.modelio.metamodel.uml.infrastructure.Element;
import org.modelio.metamodel.uml.infrastructure.ModelElement;
import org.modelio.metamodel.uml.infrastructure.Note;
import org.modelio.metamodel.uml.infrastructure.Stereotype;
import org.modelio.metamodel.uml.statik.BindableInstance;
import org.modelio.metamodel.uml.statik.Class;
import org.modelio.metamodel.uml.statik.Instance;
import org.modelio.metamodel.uml.statik.Package;
import org.modelio.vcore.smkernel.mapi.MObject;

public class ModelChangeHandlerImpl implements IModelChangeHandler {

	public ModelChangeHandlerImpl(IModule mdac) {
		super();
	}

	private Set<MObject> visited = new HashSet<>();

	@Override
	public void handleModelChange(IModelingSession session,
			IModelChangeEvent event) {
		try (ITransaction t = session.createTransaction("auto modifying model")) {
			for (MObject topLevelElement : event.getCreationEvents()) {
				visitObject(session, (Element) topLevelElement);
			}
			t.commit();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	private void visitObject(IModelingSession session, MObject object)
			throws ExtensionNotFoundException {
		// TODO this is not an optimal implementation, but Modelio insists in
		// calling me twice!!!
		// apparently this is because Modelio doesn't call stop() when
		// upgrading!!
		// On top of that Modelio has loops on the composition relationship :(

		if (visited.contains(object)) {
			return;
		}

		visited.add(object);

		if (object instanceof BindableInstance
				&& (((ModelElement) object).isStereotyped("MARTEDesigner",
						"HwDrive_Instance"))) {
			BindableInstance p = (BindableInstance) object;
			Stereotype s = session.getMetamodelExtensions().getStereotype(
					"JuniperIDE", "CloudDisk", p.getMClass());
			p.getExtension().add(0, s);
		} else if (object instanceof BindableInstance
				&& (((ModelElement) object).isStereotyped("MARTEDesigner",
						"HwProcessor_Instance"))) {
			BindableInstance p = (BindableInstance) object;
			Stereotype s = session.getMetamodelExtensions().getStereotype(
					"JuniperIDE", "CloudNodeCPU", p.getMClass());
			p.getExtension().add(0, s);
		} else if (object instanceof Instance
				&& (((ModelElement) object).isStereotyped("MARTEDesigner",
						"HwComputingResource_Instance"))) {
			Instance p = (Instance) object;
			Stereotype s = session.getMetamodelExtensions().getStereotype(
					"JuniperIDE", "CloudNode", p.getMClass());
			p.getExtension().add(0, s);
		} else if (object instanceof OpaqueAction
				&& (((ModelElement) object).isStereotyped("MARTEDesigner",
						"RtAction_OpaqueAction"))) {
			OpaqueAction p = (OpaqueAction) object;
			Stereotype s = session.getMetamodelExtensions().getStereotype(
					"MARTEDesigner", "RtFeature_OpaqueAction", p.getMClass());
			p.getExtension().add(0, s);
			s = session.getMetamodelExtensions().getStereotype("MARTEDesigner",
					"ResourceUsage_ModelElement", p.getMClass());
			p.getExtension().add(s);
		} else if ((object instanceof Class)
				&& (((ModelElement) object).isStereotyped("JuniperIDE",
						"SwMutualExclusionResource"))) {
			OpaqueAction p = (OpaqueAction) object;
			Stereotype s = session.getMetamodelExtensions().getStereotype(
					"MARTEDesigner", "SwMutualExclusionResource_Classifier",
					p.getMClass());
			p.getExtension().add(s);
		} else if ((object instanceof BindableInstance)
				&& (((ModelElement) object).isStereotyped("JuniperIDE",
						"SwMutualExclusionResource"))) {
			OpaqueAction p = (OpaqueAction) object;
			Stereotype s = session.getMetamodelExtensions().getStereotype(
					"MARTEDesigner", "SwMutualExclusionResource_Instance",
					p.getMClass());
			p.getExtension().add(s);
		} else if ((object instanceof Package)
				&& (((ModelElement) object).isStereotyped("PersistentProfile",
						"DataModel"))) {
			Package p = (Package) object;
			Stereotype s = session.getMetamodelExtensions().getStereotype(
					"JavaDesigner", "JavaPackage", p.getMClass());
			p.getExtension().add(s);
		} else if ((object instanceof Package)
				&& (((ModelElement) object).isStereotyped("JuniperIDE",
						"SoftwareArchitectureModel"))) {
			Package p = (Package) object;
			p.putTagValue("JavaDesigner", "JavaName", "juniperApplication");
		} else if (object instanceof ModelElement
				&& ((ModelElement) object).isStereotyped("JuniperIDE",
						"RequestResponseStream")) {
			Note note = session.getModel().createNote(".*", "description",
					(ModelElement) object, "relDl=1\noccKind=(period=1)");
			note.setMimeType("text/plain");
		} else if (object instanceof StaticDiagram
				&& ((((ModelElement) object).isStereotyped("JuniperIDE",
						"SoftwareArchitectureDiagram")))) {
			applySoftwareDiagramStyle((StaticDiagram) object);
		} else if (object instanceof StaticDiagram
				&& (((ModelElement) object).isStereotyped("JuniperIDE",
						"BusinessObjectDiagram"))) {
			applySoftwareDiagramStyle((StaticDiagram) object);
		} 

		for (MObject child : object.getCompositionChildren()) {
			visitObject(session, child);
		}
	}

	private void applySoftwareDiagramStyle(StaticDiagram diagram) {
		Display.getDefault().syncExec(() -> {
			IStyleHandle style = Modelio.getInstance().getDiagramService()
					.getStyle("softwareDiagramStyle");
			IDiagramHandle diagramHandler = Modelio.getInstance()
					.getDiagramService()
					.getDiagramHandle((AbstractDiagram) diagram);
			diagramHandler.getDiagramNode().setStyle(style);
			diagramHandler.save();
			diagramHandler.close();			
		});
	}
}
