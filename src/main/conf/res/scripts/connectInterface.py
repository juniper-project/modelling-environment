#
# Copyright 2014 Modeliosoft
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from org.modelio.metamodel.uml.statik import NaryConnector, Interface

connector = [el for el in selectedElements if isinstance(el, NaryConnector)][0]
interface    = [el for el in selectedElements if isinstance(el, Interface)][0]

ends = connector.getNaryLinkEnd()
for end in ends:
	if end.getProvider():
		end.getProvider().getProvidedElement().add(interface)
	if end.getConsumer():
		end.getConsumer().getRequiredElement().add(interface)

