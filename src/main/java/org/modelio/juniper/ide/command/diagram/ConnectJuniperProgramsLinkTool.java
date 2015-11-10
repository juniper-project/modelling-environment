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

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import org.eclipse.draw2d.geometry.Point;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.swt.widgets.Shell;
import org.modelio.api.diagram.IDiagramGraphic;
import org.modelio.api.diagram.IDiagramHandle;
import org.modelio.api.diagram.IDiagramLink.LinkRouterKind;
import org.modelio.api.diagram.ILinkPath;
import org.modelio.api.model.IModelingSession;
import org.modelio.api.model.ITransaction;
import org.modelio.api.model.IUmlModel;
import org.modelio.api.modelio.Modelio;
import org.modelio.juniper.ide.command.diagram.util.InterfaceHelperView;
import org.modelio.juniper.ide.command.diagram.util.SimpleLinkTool;
import org.modelio.metamodel.uml.infrastructure.ModelTree;
import org.modelio.metamodel.uml.statik.Interface;
import org.modelio.metamodel.uml.statik.NameSpace;
import org.modelio.metamodel.uml.statik.NaryConnector;
import org.modelio.metamodel.uml.statik.NaryConnectorEnd;
import org.modelio.metamodel.uml.statik.Port;
import org.modelio.metamodel.uml.statik.ProvidedInterface;
import org.modelio.metamodel.uml.statik.RequiredInterface;

public class ConnectJuniperProgramsLinkTool extends SimpleLinkTool {
	public void actionPerformed(IDiagramHandle representation,
			IDiagramGraphic graphic_source, IDiagramGraphic graphic_target,
			LinkRouterKind kind, ILinkPath path) {
		Port source = (Port) graphic_source.getElement();
		Port target = (Port) graphic_target.getElement();
		NaryConnector conn = null;

		IModelingSession session = Modelio.getInstance().getModelingSession();
		try (ITransaction transaction = session.createTransaction("creating link");) {

			conn = createProgramsLink(session.getModel(), source, target);
			Point  conn_position = computeConnectionPosition(path);
			
			representation.unmask(conn, conn_position.x, conn_position.y);
			
			representation.save();
			transaction.commit();
		} catch (Exception e) {
			e.printStackTrace();
		}
		
		try (ITransaction transaction = session.createTransaction("setting interface");) {
			ModelTree programSource = source.getInternalOwner();
			ModelTree programTarget = target.getInternalOwner();

			if (programSource.isStereotyped("JuniperIDE", "JUNIPERProgram") && programTarget.isStereotyped("JuniperIDE", "JUNIPERProgram")) {
				Interface iface = selectInterface(session.getModel(), (NameSpace) source.getInternalOwner().getOwner(),
						 programSource.getName()+"_"+programTarget.getName()+"_Interface");
				conn.getNaryLinkEnd().stream().forEach(e -> {
					if (e.getConsumer() != null) {
						e.getConsumer().getRequiredElement().add(iface);
					}
					if (e.getProvider() != null) {
						e.getProvider().getProvidedElement().add(iface);
					}
				});
			}
			
			transaction.commit();
		} catch (Exception e) {
			e.printStackTrace();
		}			

	}

	private Point computeConnectionPosition(ILinkPath path) {
		Point p = new Point();
		for(Point p1 : path.getPoints()) {
			p.x += p1.x;
			p.y += p1.y;
		}
		p.x /= path.getPoints().size();
		p.y /= path.getPoints().size();
		return p;
	}

	private Interface selectInterface(IUmlModel factory, NameSpace owner, String defaultInterfaceName) {		
		List<Interface> ifaces = owner.getOwnedElement().stream()
										.filter(i -> i.isStereotyped("JavaDesigner", "JavaInterface"))
										.map(i -> (Interface)i)
										.collect(Collectors.toList());
		if (!ifaces.isEmpty()) {
			InterfaceHelperView ihw = new InterfaceHelperView(new Shell(), "Interfaces","Please select an interface to connect Juniper programs", ifaces);
			ihw.open();
			Interface selectedInterface = ihw.getSelectedInterface();
			if (selectedInterface == null) {
				return factory.createInterface(defaultInterfaceName, owner);			
			} else {
				return selectedInterface;
			}
		} else {
			return factory.createInterface(defaultInterfaceName, owner);			
		}
	}

	private NaryConnector createProgramsLink(IUmlModel factory, Port source,
			Port target) {
		List<Interface> ifaces = new ArrayList<Interface>(0);
		
		RequiredInterface req = factory.createRequiredInterface(source, ifaces);
		ProvidedInterface prov = factory.createProvidedInterface(target, ifaces);
				
		NaryConnectorEnd end = factory.createNaryConnectorEnd();
		NaryConnectorEnd end1 = factory.createNaryConnectorEnd();
		
		end.setConsumer(req);
		end.setSource(target);
		
		end1.setProvider(prov);
		
		NaryConnector conn = factory.createNaryConnector();
		conn.getNaryLinkEnd().add(end);
		conn.getNaryLinkEnd().add(end1);
		
		return conn;
	}
	
	
}
