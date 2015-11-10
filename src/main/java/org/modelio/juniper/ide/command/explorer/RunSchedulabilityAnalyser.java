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

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;

import javax.script.ScriptEngine;
import javax.script.ScriptException;

import org.modelio.api.model.IModelingSession;
import org.modelio.api.model.ITransaction;
import org.modelio.api.modelio.Modelio;
import org.modelio.api.module.IModule;
import org.modelio.api.module.commands.DefaultModuleCommandHandler;
import org.modelio.metamodel.uml.infrastructure.ModelElement;
import org.modelio.vcore.smkernel.mapi.MObject;

public class RunSchedulabilityAnalyser extends DefaultModuleCommandHandler {

	@Override
	public boolean accept(List<MObject> selectedElements, IModule module) {
		return selectedElements.size() == 1;
	}

	@Override
	public void actionPerformed(List<MObject> selectedElements, IModule module) {
		IModelingSession session = Modelio.getInstance().getModelingSession();

		try (ITransaction transaction = session
				.createTransaction("RunAnalysis")) {
			transaction.commit();
			ModelElement model = (ModelElement) selectedElements.get(0);

			File xmlFile = getTempFile(runScript(module, "exportXML", model));
			ScriptEngine jythonEngine = module.getJythonEngine();
			jythonEngine.put("dag_path_parameter", module.getConfiguration().getParameterValue("schedanalyser.path"));
			jythonEngine.put("input_path_parameter", xmlFile.getAbsolutePath());

			runScript(module, "runDag", model);
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	private File getTempFile(String content) throws IOException {
		File file = File.createTempFile("model", ".xml");
		PrintWriter pw = new PrintWriter(file);
		pw.append(content);
		pw.close();
		return file;
	}

	private String runScript(IModule module, String scriptName,
			ModelElement selectedElement) throws FileNotFoundException,
			ScriptException {
		List<MObject> selectedElements = new ArrayList<MObject>();
		selectedElements.add(selectedElement);

		ScriptEngine jythonEngine = module.getJythonEngine();
		IModelingSession session = Modelio.getInstance().getModelingSession();

		jythonEngine.put("selectedElement", selectedElements.get(0));
		jythonEngine.put("modellingSession", session);
		jythonEngine.put("selectedElements", selectedElements);

		String path = getScriptPath(module, "/res/scripts/" + scriptName
				+ ".py");
		jythonEngine.eval(new FileReader(path));

		return (String) jythonEngine.get("resultFile");
	}

	private String getScriptPath(IModule module, String scriptName) {
		String path = module.getConfiguration().getModuleResourcesPath()
				.toString()
				+ scriptName;
		return path;
	}
}
