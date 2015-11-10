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
package org.modelio.juniper.ide.command.diagram.util;

import java.util.List;
import java.util.Map;

import org.eclipse.gef.palette.PaletteDrawer;
import org.eclipse.gef.palette.PaletteRoot;
import org.modelio.api.diagram.IDiagramCustomizer;
import org.modelio.api.diagram.IDiagramService;
import org.modelio.api.diagram.tools.PaletteEntry;
import org.modelio.api.modelio.Modelio;
import org.modelio.api.module.IModule;

public class JuniperDiagramCustomizer implements IDiagramCustomizer {

	@Override
	public void fillPalette(PaletteRoot paletteRoot) {

		IDiagramService toolRegistry = Modelio.getInstance()
				.getDiagramService();
		
		final PaletteDrawer juniperGroup = new PaletteDrawer(
				"Juniper program tool", null);
		juniperGroup.setInitialState(PaletteDrawer.INITIAL_STATE_OPEN);
		juniperGroup.add(toolRegistry
				.getRegisteredTool("CreateJuniperProgramTool"));
		juniperGroup.add(toolRegistry
				.getRegisteredTool("ConnectJuniperProgramTool"));
		paletteRoot.add(juniperGroup);

		/*
		 * final PaletteDrawer commonGroup = new
		 * PaletteDrawer("PALETTE_Default", null);
		 * commonGroup.setInitialState(PaletteDrawer.INITIAL_STATE_OPEN);
		 * commonGroup.add(new SelectionToolEntry()); commonGroup.add(new
		 * MarqueeToolEntry()); paletteRoot.add(commonGroup);
		 */
		final PaletteDrawer storageGroup = new PaletteDrawer("Storage program",
				null);
		storageGroup.setInitialState(PaletteDrawer.INITIAL_STATE_OPEN);
		final PaletteDrawer datamodelGroup = new PaletteDrawer("Noeuds",
				null);
		datamodelGroup.setInitialState(PaletteDrawer.INITIAL_STATE_OPEN);
		datamodelGroup.add(toolRegistry
				.getRegisteredTool("DataModelDiagramCommande"));
		paletteRoot.add(datamodelGroup);
		boolean storageProgram = false;
		if (Modelio.getInstance().getModuleService()
				.getPeerModule("MongoDBModeler") != null) {

			storageGroup.add(toolRegistry
					.getRegisteredTool("CreateMongoDBServerTool"));

			storageProgram = true;
		}
		if (Modelio.getInstance().getModuleService()
				.getPeerModule("PostgreSQLModeler") != null) {

			storageGroup.add(toolRegistry
					.getRegisteredTool("CreatePostgreSQLServerTool"));

			storageProgram = true;
		}
		if (storageProgram) {
			paletteRoot.add(storageGroup);
			final PaletteDrawer dependencyGroup = new PaletteDrawer("Links",
					null);
			dependencyGroup.setInitialState(PaletteDrawer.INITIAL_STATE_OPEN);
			dependencyGroup.add(toolRegistry
					.getRegisteredTool("CreateStoresDependency"));
			paletteRoot.add(dependencyGroup);

		}
	}

	@Override
	public Map<String, String> getParameters() {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public void initialize(IModule arg0, List<PaletteEntry> arg1,
			Map<String, String> arg2, boolean arg3) {

	}

	@Override
	public boolean keepBasePalette() {

		return true;
	}

}
