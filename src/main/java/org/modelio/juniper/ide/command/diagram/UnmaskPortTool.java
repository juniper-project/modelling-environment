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
package org.modelio.juniper.ide.command.diagram;

import java.util.List;

import org.eclipse.draw2d.geometry.Rectangle;
import org.eclipse.swt.widgets.Display;
import org.modelio.api.diagram.IDiagramGraphic;
import org.modelio.api.diagram.IDiagramHandle;
import org.modelio.api.diagram.IDiagramNode;
import org.modelio.api.model.IModelingSession;
import org.modelio.api.model.ITransaction;
import org.modelio.api.modelio.Modelio;
import org.modelio.juniper.ide.command.diagram.util.SimpleBoxTool;
import org.modelio.metamodel.uml.infrastructure.ModelElement;
import org.modelio.metamodel.uml.statik.Port;
import org.modelio.vcore.smkernel.mapi.MObject;

public class UnmaskPortTool extends SimpleBoxTool {

	protected void unmaskElement(final IDiagramHandle representation,
			final Rectangle rec, final ModelElement child) {
		Display.getDefault().syncExec(new Runnable() {

			@Override
			public void run() {

				IModelingSession session = Modelio.getInstance()
						.getModelingSession();

				try (ITransaction transaction = session.createTransaction("");) {
					List<IDiagramGraphic> graph = representation.unmask(child,
							rec.x, rec.y);

					if (graph.size() > 0)
						((IDiagramNode) graph.get(0)).setBounds(rec);

					for (MObject composition : child.getCompositionChildren()) {
						if (composition instanceof Port) {

							representation.unmask(composition, rec.x, rec.y);

						}
					}
					representation.save();
					transaction.commit();
				} catch (Exception e) {
					e.printStackTrace();
				}
			}

		});
	}

}
