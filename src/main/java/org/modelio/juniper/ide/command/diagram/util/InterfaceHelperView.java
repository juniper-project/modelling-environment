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

import org.modelio.api.ui.ModelioDialog;
import org.eclipse.jface.dialogs.IDialogConstants;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.FormAttachment;
import org.eclipse.swt.layout.FormData;
import org.eclipse.swt.layout.FormLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Shell;
import org.modelio.metamodel.uml.statik.Interface;
public class InterfaceHelperView extends ModelioDialog implements Listener {

	private String title;
	private List<Interface> interfaces;
	private Interface selectedInterface;
	private Combo serviceCombo;
	private Button ok;
	private String subtitle;

	public InterfaceHelperView(Shell parentShell, String title,String subtitle,List<Interface> interfaces) {
		super(parentShell);
		this.setShellStyle(SWT.DIALOG_TRIM | SWT.RESIZE | SWT.MAX);
		this.title = title;
		this.subtitle = subtitle;
		this.interfaces = interfaces;
	}

	@Override
	public void addButtonsInButtonBar(Composite parent) {
		this.ok = createButton(parent, IDialogConstants.OK_ID, IDialogConstants.OK_LABEL, true);
		createButton(parent, IDialogConstants.CANCEL_ID, IDialogConstants.CLOSE_LABEL, false);
		
	}

	@Override
	public Control createContentArea(Composite parent) {
		Composite composite = new Composite(parent, SWT.NONE);
		composite.setLayout(new FormLayout());
		composite.setLayoutData(new GridData(GridData.FILL_BOTH));

		final Label interface_label = new Label(composite, SWT.NONE);
		final FormData formData = new FormData();
		formData.bottom = new FormAttachment(0, 60);
		formData.top = new FormAttachment(0, 41);
		formData.right = new FormAttachment(0, 185);
		formData.left = new FormAttachment(0, 5);
		interface_label.setLayoutData(formData);
		interface_label.setText("Interfaces");

		this.serviceCombo = new Combo(composite, SWT.NONE);
		final FormData formData_2 = new FormData();
		formData_2.bottom = new FormAttachment(0, 60);
		formData_2.right = new FormAttachment(100, -34);
		formData_2.top = new FormAttachment(0, 40);
		formData_2.left = new FormAttachment(0, 200);
		this.serviceCombo.setLayoutData(formData_2);

		String[] item_name = new String[this.interfaces.size()+1];
		for (int i = 0; i < this.interfaces.size(); i++) {
			item_name[i] = this.interfaces.get(i).getName();
		}
		item_name[this.interfaces.size()] = "** NEW INTERFACE **"; // Add a token interface name at the end of the list so we create a new one

		this.serviceCombo.setItems(item_name);
		this.serviceCombo.select(0);

		return composite;
		
	}

	@Override
	protected void okPressed() {
		if (this.interfaces.size() > 0) {
			int index = this.serviceCombo.getSelectionIndex();
			if (index < interfaces.size()) {
				this.selectedInterface = this.interfaces.get(index);
			} else {
				this.selectedInterface = null;
			}
		}
		super.okPressed();
	}

	@Override
	public void init() {
		Shell shell = getShell();
		shell.setSize(600, 420);
		int x = (this.getShell().getSize().x / 2) - 250;
		int y = (this.getShell().getSize().y / 2) - 100;
		shell.setLocation(x, y);
		shell.setMinimumSize(400, 220);
		shell.setText("Modelio");
		setTitle(this.title);
		setMessage(this.subtitle);
		
	}

	@Override
	public void handleEvent(Event arg0) {
		// TODO Auto-generated method stub
		
	}

	public Interface getSelectedInterface() {
		return this.selectedInterface;
	}
}
