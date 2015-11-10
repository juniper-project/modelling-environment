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

import java.util.List;
import java.util.Map;

import org.modelio.api.module.IModule;
import org.modelio.api.module.commands.CommandScope;
import org.modelio.api.module.commands.DefaultModuleCommandHandler;
import org.modelio.juniper.ide.impl.MDACConfigurator;
import org.modelio.vcore.smkernel.mapi.MObject;

public class DefaultCommandHandler extends DefaultModuleCommandHandler {
	private DefaultModuleCommandHandler command;

	public void initialize(List<CommandScope> scopes,
			Map<String, String> hParameters) {
		super.initialize(scopes, hParameters);

		if ("elementFactory".equals(this.getParameter("type"))) {
			command = new MDACConfigurator.CallElementFactoryMdacCommand(
					this.getParameter("name"));
		} else if ("element".equals(this.getParameter("type"))) {
			try {
				command = new MDACConfigurator.CreateSingleElementMdacCommand(
						this.getParameter("metaclass"),
						this.getParameter("stereotypeModule"),
						this.getParameter("stereotype"),
						this.getParameter("addOp"));
			} catch (Exception e) {
				e.printStackTrace();
			}
		} else if ("script".equals(this.getParameter("type"))) {
			command = new MDACConfigurator.RunScriptMdacCommand(
					this.getParameter("path"));
		} else if ("java".equals(this.getParameter("type"))) {
			command = new MDACConfigurator.RunJavaMdacCommand(
					this.getParameter("command"));
			// TODO: Migrate and test Java commands
		}

	}

	public boolean accept(List<MObject> selectedElements, IModule module) {
		return command != null && super.accept(selectedElements, module) && command.accept(selectedElements, module);
	}

	public void actionPerformed(List<MObject> selectedElements, IModule module) {
		if (command == null) {
			System.err.println("ActionPerformed: command is null!");
		} else {
			this.command.actionPerformed(selectedElements, module);
		}
	}

	@Override
	public boolean isActiveFor(List<MObject> selectedElements, IModule module) {
		return this.command != null
				&& super.isActiveFor(selectedElements, module) 
				&& this.command.isActiveFor(selectedElements, module);
	}

}
