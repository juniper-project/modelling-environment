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
package org.modelio.juniper.ide.audit.rules;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import javax.script.ScriptEngine;
import javax.script.ScriptException;

import org.modelio.api.module.IModule;
import org.modelio.metamodel.uml.behavior.activityModel.Activity;
import org.modelio.metamodel.uml.behavior.activityModel.ActivityEdge;
import org.modelio.metamodel.uml.behavior.activityModel.ActivityGroup;
import org.modelio.metamodel.uml.behavior.activityModel.ActivityNode;
import org.modelio.metamodel.uml.behavior.activityModel.ActivityPartition;
import org.modelio.metamodel.uml.behavior.activityModel.ControlFlow;
import org.modelio.metamodel.uml.behavior.activityModel.InitialNode;
import org.modelio.metamodel.uml.behavior.activityModel.OpaqueAction;
import org.modelio.metamodel.uml.infrastructure.ModelElement;
import org.modelio.metamodel.uml.statik.Instance;
import org.modelio.modelvalidator.engine.IModelValidator;
import org.modelio.modelvalidator.engine.impl.AbstractSimplifiedRule;
import org.modelio.temp.audit.service.AuditSeverity;
import org.modelio.vcore.smkernel.mapi.MObject;

public class OverallStructureValidator {
	public static void init(IModelValidator modelValidator, IModule module) {
		modelValidator.registerRule(
				new AbstractSimplifiedRule("OVER_001",
						org.modelio.metamodel.uml.statik.Class.class) {
					@Override
					public boolean check(MObject obj, List<Object> linked) {
						org.modelio.metamodel.uml.statik.Class el = (org.modelio.metamodel.uml.statik.Class) obj;
						if (el.isStereotyped("JuniperIDE", "JUNIPERProgram")) {
							if (el.getRepresenting().isEmpty()) {
								return false;
							}
						}
						return true;
					}
				},
				AuditSeverity.AuditError,
				"Every JUNIPER program should be deployed onto a JUNIPER node.",
				"help");

		modelValidator.registerRule(
				new AbstractSimplifiedRule("OVER_002a",
						org.modelio.metamodel.uml.statik.Instance.class) {
					@Override
					public boolean check(MObject obj, List<Object> linked) {
						org.modelio.metamodel.uml.statik.Instance el = (org.modelio.metamodel.uml.statik.Instance) obj;
						boolean check = false;
						if (el.isStereotyped("JuniperIDE", "CloudNode")) {
							List<MObject> childs = (List<MObject>) obj
									.getCompositionChildren();
							for (MObject child : childs) {
								if (child instanceof org.modelio.metamodel.uml.statik.BindableInstance) {
									org.modelio.metamodel.uml.statik.BindableInstance childBindable = (org.modelio.metamodel.uml.statik.BindableInstance) child;
									if (childBindable.isStereotyped(
											"JuniperIDE", "CloudNodeCPU")) {
										check = true;
										break;
									}

								}
							}

						}
						return check;
					}
				},
				AuditSeverity.AuditWarning,
				"Every cloud node should contain at least a CPU node. This model is not analysable.",
				"help");

		modelValidator.registerRule(
				new AbstractSimplifiedRule("OVER_002b",
						org.modelio.metamodel.uml.statik.Instance.class) {
					@Override
					public boolean check(MObject obj, List<Object> linked) {
						org.modelio.metamodel.uml.statik.Instance el = (org.modelio.metamodel.uml.statik.Instance) obj;

						boolean checkIp = false;
						if (el.isStereotyped("JuniperIDE", "CloudNode")) {

							if (el.getTagValues("JuniperIDE", "ip") != null) {
								checkIp = true;
							}

						}
						return checkIp;
					}
				},
				AuditSeverity.AuditWarning,
				"Every cloud node should define ip(s). This model is not analysable.",
				"help");

		modelValidator
				.registerRule(
						new AbstractSimplifiedRule(
								"OVER_003",
								org.modelio.metamodel.uml.behavior.activityModel.Activity.class) {
							@Override
							public boolean check(MObject obj,
									List<Object> linked) {
								org.modelio.metamodel.uml.behavior.activityModel.Activity el = (org.modelio.metamodel.uml.behavior.activityModel.Activity) obj;
								for (ActivityNode node : getActivityNodes(el)) {

									if (startsCycle(node,
											new HashSet<ActivityNode>())) {
										linked.add(node);
										return false;
									}
								}
								return true;
							}

							private boolean startsCycle(ActivityNode node,
									HashSet<ActivityNode> visited) {
								if (visited.contains(node)) {
									return true;
								} else {
									visited.add(node);
									for (ActivityNode successor : getSuccessors(node)) {
										if (startsCycle(successor, visited)) {
											return true;
										}
									}
									visited.remove(node);
								}
								return false;
							}

							private Set<ActivityNode> getSuccessors(
									ActivityNode node) {
								Set<ActivityNode> nodes = new HashSet<ActivityNode>();
								for (ActivityEdge edge : node.getOutgoing()) {
									ActivityNode successor = edge.getTarget();
									nodes.add(successor);
								}
								return nodes;
							}

							private List<ActivityNode> getActivityNodes(
									Activity activity) {
								List<ActivityNode> activityNodes = new ArrayList<ActivityNode>();
								for (ActivityGroup child : activity
										.getOwnedGroup()) {
									for (ActivityNode childActivityNode : ((ActivityPartition) child)
											.getContainedNode()) {
										activityNodes.add(childActivityNode);
									}
								}
								return activityNodes;
							}
						},
						AuditSeverity.AuditWarning,
						"A behavior model should be a DAG, your model is not analysable.",
						"help");

		modelValidator.registerRule(
				new AbstractSimplifiedRule("OVER_004",
						org.modelio.metamodel.uml.statik.Class.class) {
					@Override
					public boolean check(MObject obj, List<Object> linked) {
						org.modelio.metamodel.uml.statik.Class el = (org.modelio.metamodel.uml.statik.Class) obj;

						if (el.isStereotyped("JuniperIDE", "JUNIPERProgram")) {

							return el.getRepresenting().size() == 1;
						}

						return true;
					}
				}, AuditSeverity.AuditError,
				"Each JuniperProgram should be intantiated only once.", "help");

		modelValidator.registerRule(
				new AbstractSimplifiedRule("OVER_005",
						org.modelio.metamodel.uml.statik.Instance.class) {
					@Override
					public boolean check(MObject obj, List<Object> linked) {
						org.modelio.metamodel.uml.statik.Instance el = (org.modelio.metamodel.uml.statik.Instance) obj;

						if (el.isStereotyped("JuniperIDE", "CloudNode")) {
							int nbJuniperChilds = 0;
							for (MObject child : el.getCompositionChildren()) {
								
								if (((ModelElement) child).isStereotyped(
										"JuniperIDE", "ProgramInstance")
										&& ((Instance) child).getBase()
												.isStereotyped("JuniperIDE",
														"JUNIPERProgram")) {
									nbJuniperChilds++;
								}
							}
							return nbJuniperChilds == 1;
						}
						return true;
					}
				}, AuditSeverity.AuditError,
				"Each node should contain a single program instance.", "help");
		
		modelValidator.registerRule(
				new AbstractSimplifiedRule("OVER_006",
						org.modelio.metamodel.uml.statik.Port.class) {
					@Override
					public boolean check(MObject obj, List<Object> linked) {
						org.modelio.metamodel.uml.statik.Port el = (org.modelio.metamodel.uml.statik.Port) obj;
						
						if (el.isStereotyped("JuniperIDE", "RequestResponseStream")) {
							String path = module.getConfiguration().getModuleResourcesPath().toString()+"/res/scripts/requestResponseValidationRule.py";
							ScriptEngine jythonEngine = module.getJythonEngine();
							jythonEngine.put("selectedElement", el);
							try {
								jythonEngine.eval(new FileReader(path));
							} catch (FileNotFoundException e) {
								
								e.printStackTrace();
							} catch (ScriptException e) {
								
								e.printStackTrace();
							}
							Boolean res = (Boolean) jythonEngine.get("result");
							return res;
						}
						return true;
					}
				}, AuditSeverity.AuditError,
				"value of relDl and occKind should be strictly greater than 0.", "help");
		
		modelValidator.registerRule(
				new AbstractSimplifiedRule("OVER_007a",
						org.modelio.metamodel.uml.behavior.activityModel.ControlFlow.class) {
					@Override
					public boolean check(MObject obj, List<Object> linked) {
						org.modelio.metamodel.uml.behavior.activityModel.ControlFlow el = (org.modelio.metamodel.uml.behavior.activityModel.ControlFlow) obj;
						
						if (el instanceof ControlFlow) {
							String path = module.getConfiguration().getModuleResourcesPath().toString()+"/res/scripts/flowProbDescriptionRule.py";
							ScriptEngine jythonEngine = module.getJythonEngine();
							jythonEngine.put("selectedElement", el);
							
							try {
								jythonEngine.eval(new FileReader(path));
							} catch (FileNotFoundException e) {
								
								e.printStackTrace();
							} catch (ScriptException e) {
								
								e.printStackTrace();
							}
							Boolean res = (Boolean) jythonEngine.get("result");
							
							return res;
						}
						return true;
					}
				}, AuditSeverity.AuditError,
				"prob constraint is mandatory and should be strictly greater than 0.", "help");
		
		modelValidator.registerRule(
				new AbstractSimplifiedRule("OVER_007b",
						org.modelio.metamodel.uml.behavior.activityModel.ControlFlow.class) {
					@Override
					public boolean check(MObject obj, List<Object> linked) {
						org.modelio.metamodel.uml.behavior.activityModel.ControlFlow el = (org.modelio.metamodel.uml.behavior.activityModel.ControlFlow) obj;
						
						if (el instanceof ControlFlow) {
							String path = module.getConfiguration().getModuleResourcesPath().toString()+"/res/scripts/flowOtherDescriptionRule.py";
							ScriptEngine jythonEngine = module.getJythonEngine();
							jythonEngine.put("selectedElement", el);
							
							try {
								jythonEngine.eval(new FileReader(path));
							} catch (FileNotFoundException e) {
								
								e.printStackTrace();
							} catch (ScriptException e) {
								
								e.printStackTrace();
							}
							Boolean res = (Boolean) jythonEngine.get("result");
							
							return res;
						}
						return true;
					}
				}, AuditSeverity.AuditError,
				"best, worst, value constraints should be strictly greater than 0.", "help");
		
		modelValidator.registerRule(
				new AbstractSimplifiedRule("OVER_008a",
						org.modelio.metamodel.uml.behavior.activityModel.InitialNode.class) {
					@Override
					public boolean check(MObject obj, List<Object> linked) {
						org.modelio.metamodel.uml.behavior.activityModel.InitialNode el = (org.modelio.metamodel.uml.behavior.activityModel.InitialNode) obj;
						
						if (el instanceof InitialNode) {
							String path = module.getConfiguration().getModuleResourcesPath().toString()+"/res/scripts/flowProbDescriptionRule.py";
							ScriptEngine jythonEngine = module.getJythonEngine();
							jythonEngine.put("selectedElement", el);
							
							try {
								jythonEngine.eval(new FileReader(path));
							} catch (FileNotFoundException e) {
								
								e.printStackTrace();
							} catch (ScriptException e) {
								
								e.printStackTrace();
							}
							Boolean res = (Boolean) jythonEngine.get("result");
							
							return res;
						}
						return true;
					}
				}, AuditSeverity.AuditError,
				"prob constraint is mandatory and should be strictly greater than 0.", "help");

		modelValidator.registerRule(
				new AbstractSimplifiedRule("OVER_008b",
						org.modelio.metamodel.uml.behavior.activityModel.InitialNode.class) {
					@Override
					public boolean check(MObject obj, List<Object> linked) {
						org.modelio.metamodel.uml.behavior.activityModel.InitialNode el = (org.modelio.metamodel.uml.behavior.activityModel.InitialNode) obj;
						
						if (el instanceof InitialNode) {
							String path = module.getConfiguration().getModuleResourcesPath().toString()+"/res/scripts/flowOtherDescriptionRule.py";
							ScriptEngine jythonEngine = module.getJythonEngine();
							jythonEngine.put("selectedElement", el);
							
							try {
								jythonEngine.eval(new FileReader(path));
							} catch (FileNotFoundException e) {
								
								e.printStackTrace();
							} catch (ScriptException e) {
								
								e.printStackTrace();
							}
							Boolean res = (Boolean) jythonEngine.get("result");
							
							return res;
						}
						return true;
					}
				}, AuditSeverity.AuditError,
				"best, worst, value constraints should be strictly greater than 0.", "help");
		
		modelValidator.registerRule(
				new AbstractSimplifiedRule("OVER_009a",
						org.modelio.metamodel.uml.behavior.activityModel.OpaqueAction.class) {
					@Override
					public boolean check(MObject obj, List<Object> linked) {
						org.modelio.metamodel.uml.behavior.activityModel.OpaqueAction el = (org.modelio.metamodel.uml.behavior.activityModel.OpaqueAction) obj;
						
						if (el instanceof OpaqueAction) {
							String path = module.getConfiguration().getModuleResourcesPath().toString()+"/res/scripts/flowProbDescriptionRule.py";
							ScriptEngine jythonEngine = module.getJythonEngine();
							jythonEngine.put("selectedElement", el);
							
							try {
								jythonEngine.eval(new FileReader(path));
							} catch (FileNotFoundException e) {
								
								e.printStackTrace();
							} catch (ScriptException e) {
								
								e.printStackTrace();
							}
							Boolean res = (Boolean) jythonEngine.get("result");
							
							return res;
						}
						return true;
					}
				}, AuditSeverity.AuditError,
				"prob constraint is mandatory and should be strictly greater than 0.", "help");

		modelValidator.registerRule(
				new AbstractSimplifiedRule("OVER_009b",
						org.modelio.metamodel.uml.behavior.activityModel.OpaqueAction.class) {
					@Override
					public boolean check(MObject obj, List<Object> linked) {
						org.modelio.metamodel.uml.behavior.activityModel.OpaqueAction el = (org.modelio.metamodel.uml.behavior.activityModel.OpaqueAction) obj;
						
						if (el instanceof OpaqueAction) {
							String path = module.getConfiguration().getModuleResourcesPath().toString()+"/res/scripts/flowOtherDescriptionRule.py";
							ScriptEngine jythonEngine = module.getJythonEngine();
							jythonEngine.put("selectedElement", el);
							
							try {
								jythonEngine.eval(new FileReader(path));
							} catch (FileNotFoundException e) {
								
								e.printStackTrace();
							} catch (ScriptException e) {
								
								e.printStackTrace();
							}
							Boolean res = (Boolean) jythonEngine.get("result");
							
							return res;
						}
						return true;
					}
				}, AuditSeverity.AuditError,
				"best, worst, value constraints should be strictly greater than 0.", "help");
	}
}
