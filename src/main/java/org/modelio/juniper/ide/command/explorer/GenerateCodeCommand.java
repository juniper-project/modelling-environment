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

import java.io.FileReader;
import java.lang.reflect.Method;
import java.util.List;

import javax.script.ScriptEngine;

import org.modelio.api.model.IModelingSession;
import org.modelio.api.model.ITransaction;
import org.modelio.api.modelio.Modelio;
import org.modelio.api.module.IModule;
import org.modelio.api.module.IPeerModule;
import org.modelio.api.module.commands.DefaultModuleCommandHandler;
import org.modelio.metamodel.uml.statik.NameSpace;
import org.modelio.metamodel.uml.statik.Package;
import org.modelio.vcore.smkernel.mapi.MObject;

public class GenerateCodeCommand extends DefaultModuleCommandHandler {
	
    @Override
    public boolean accept(List<MObject> selectedElements, IModule module) {
        return selectedElements.size() == 1;
    }

    @Override
    public void actionPerformed(List<MObject> selectedElements, IModule module) {
		ScriptEngine jythonEngine = module.getJythonEngine();
		IModelingSession session = Modelio.getInstance().getModelingSession();

		jythonEngine.put("selectedElement", selectedElements.get(0));
		jythonEngine.put("modellingSession", session);
		jythonEngine.put("selectedElements", selectedElements);

		String path = getScriptPath(module, "/res/scripts/updateAndGenerateCode.py");

		try (ITransaction transaction = session
				.createTransaction("GeneratingCode")) {
			jythonEngine.eval(new FileReader(path));
			transaction.commit();

			// using reflection to access JavaDesigner methods because the module is not on the
			// public repository :-(
			IPeerModule jdesigner = Modelio.getInstance().getModuleService().getPeerModule("JavaDesigner");
			org.modelio.metamodel.uml.statik.Package model = (Package) selectedElements.get(0);
			for(org.modelio.metamodel.uml.statik.Package subModel : model.getOwnedElement(org.modelio.metamodel.uml.statik.Package.class)) {
				if (subModel.isStereotyped("JuniperIDE", "SoftwareArchitectureModel")) {
					Method m = jdesigner.getClass().getMethod("generate", new Class[]{NameSpace.class, boolean.class});
					m.invoke(jdesigner, new Object[]{subModel, true});
					break;
				}
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
    }

	private String getScriptPath(IModule module, String scriptName) {
		String path = module.getConfiguration().getModuleResourcesPath()
				.toString()
				+ scriptName;
		return path;
	}
}
