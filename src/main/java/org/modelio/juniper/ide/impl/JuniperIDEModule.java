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

import java.io.File;

import javax.script.ScriptEngine;
import javax.script.ScriptException;

import org.modelio.api.model.IModelingSession;
import org.modelio.api.model.ITransaction;
import org.modelio.api.model.IUmlModel;
import org.modelio.api.modelio.Modelio;
import org.modelio.api.module.AbstractJavaModule;
import org.modelio.api.module.IParameterEditionModel;
import org.modelio.api.module.IModuleAPIConfiguration;
import org.modelio.api.module.IModuleSession;
import org.modelio.api.module.IModuleUserConfiguration;
import org.modelio.api.module.paramEdition.ParameterGroupModel;
import org.modelio.api.module.paramEdition.ParametersEditionModel;
import org.modelio.api.module.paramEdition.StringParameterModel;
import org.modelio.juniper.ide.audit.rules.OverallStructureValidator;
import org.modelio.metamodel.mda.ModuleComponent;
import org.modelio.metamodel.mda.Project;
import org.modelio.modelvalidator.ModelValidatorFacade;
import org.modelio.modelvalidator.engine.IModelValidator;
import org.modelio.vcore.smkernel.mapi.MObject;

/**
 * Implementation of the IModule interface.
 * <br>All Modelio java modules should inherit from this class.
 * 
 */
public class JuniperIDEModule extends AbstractJavaModule {

	private JuniperIDEPeerModule peerModule = null;

	private JuniperIDEModuleSession session = null;

	@Override
	public JuniperIDEPeerModule getPeerModule() {
		return this.peerModule;
	}

	/**
	 * Return the session attached to the current module.
	 * <p>
	 * <p>
	 * This session is used to manage the module lifecycle by declaring the
	 * desired implementation on start, select... methods.
	 */
	@Override
	public IModuleSession getSession() {
		return this.session;
	}

	/**
	 * Method automatically called just after the creation of the module.
	 * <p>
	 * <p>
	 * The module is automatically instanciated at the beginning of the MDA
	 * lifecycle and constructor implementation is not accessible to the module
	 * developer.
	 * <p>
	 * <p>
	 * The <code>init</code> method allows the developer to execute the desired initialization code at this step. For
     * example, this is the perfect place to register any IViewpoint this module provides.
	 *
	 *
	 * @see org.modelio.api.module.AbstractJavaModule#init()
	 */
	@Override
	public void init() {
		// Add the module initialization code
	    super.init();
	    
	    // marking the root package
	    markRootPackage();	    
	    
		// installing validation rules
		installValidationRules();
		// setting default classpath for scripts importing
		String path = this.getConfiguration().getModuleResourcesPath()
				.toString()
				+ "/res/scripts/";
		ScriptEngine jythonEngine = this.getJythonEngine();
		try {
			jythonEngine.put("scriptsPath", new File(path).getAbsolutePath());
			jythonEngine.eval("sys.path.append(scriptsPath)");
		} catch (ScriptException e) {
			e.printStackTrace();
		}	    
	}

	private void markRootPackage() {
		IModelingSession session = Modelio.getInstance().getModelingSession();
				
	    try(ITransaction transaction = session.createTransaction("Marking root")) {
			IUmlModel factory = session.getModel();
			
			for(MObject root : factory.getModelRoots()) {
				if (root instanceof Project && !root.getStatus().isCmsReadOnly()) {
					Project p = (Project) root;
					p.getModel().addStereotype("JuniperIDE", "RootPackage");					
				}
			}
			transaction.commit();
		} catch(Exception e) {
			e.printStackTrace();
		}
	}
	
	private void installValidationRules() {
		IModelValidator modelValidator = ModelValidatorFacade.getInstance().getModelValidator();
		OverallStructureValidator.init(modelValidator,this);
		
	}
		
    /**
     * Method automatically called just before the disposal of the module.
     * <p>
     * <p>
     * 
     * 
     * The <code>uninit</code> method allows the developer to execute the desired un-initialization code at this step.
     * For example, if IViewpoints have been registered in the {@link #init()} method, this method is the perfect place
     * to remove them.
     * <p>
     * <p>
     * 
     * This method should never be called by the developer because it is already invoked by the tool.
     * 
     * @see org.modelio.api.module.AbstractJavaModule#uninit()
     */
    @Override
    public void uninit() {
        // Add the module un-initialization code
        super.uninit();
    }
    
	/**
	 * Builds a new module.
	 * <p>
	 * <p>
	 * This constructor must not be called by the user. It is automatically
	 * invoked by Modelio when the module is installed, selected or started.
     * @param modelingSession the modeling session this module is deployed into.
     * @param model the model part of this module.
     * @param moduleConfiguration the module configuration, to get and set parameter values from the module itself.
     * @param peerConfiguration the peer module configuration, to get and set parameter values from another module. 
	 */
	public JuniperIDEModule(IModelingSession modelingSession, ModuleComponent moduleComponent, IModuleUserConfiguration moduleConfiguration, IModuleAPIConfiguration peerConfiguration) {
	    super(modelingSession, moduleComponent, moduleConfiguration);
		this.session = new JuniperIDEModuleSession(this);
		this.peerModule = new JuniperIDEPeerModule(this, peerConfiguration);
		this.peerModule.init();
	}

	/**
	 * @see org.modelio.api.module.AbstractJavaModule#getParametersEditionModel()
	 */
	@Override
	public IParameterEditionModel getParametersEditionModel() {
	    if (this.parameterEditionModel == null) {
	    	this.parameterEditionModel = new ParametersEditionModel(this);
	    	ParameterGroupModel group = new ParameterGroupModel("Schedulability Analyser", "Schedulability Analyser");
	    	group.addParameter(new StringParameterModel(this.getConfiguration(), "schedanalyser.path", "Path", "Path to executable", ""));
	    	this.parameterEditionModel.getGroups().add(group);
	    	
	    }
		return this.parameterEditionModel;
	}
	
	@Override
    public String getModuleImagePath() {
        return "/res/icons/juniper_icon_16.png";
    }

}
