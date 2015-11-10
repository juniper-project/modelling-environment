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
def interpretConstraint(str):
	def interpretVardefs(str, split='\n'):
		ret = {}
		for vardef in str.split(split):
			arr = vardef.partition('=')
			varname = arr[0].strip()
			varval  = arr[2].strip()

			if varval.startswith('('):
				varval = interpretVardefs(varval[1:-1], split=',')
			elif varval[:1].isalpha():
				paridx = varval.find('(')
				vartype = varval[0:paridx]
				varval = interpretVardefs(varval[paridx+1:-1], split=',')
				varval['type'] = vartype
			if varname:
			   ret[varname] = varval
		return ret
	return interpretVardefs(str)

					  
rRStream = selectedElement
print "rRStream : ",rRStream
note = rRStream.getDescriptor().get(0)
print "note : ",note
noteContent = note.getContent()
print "noteContent : ",noteContent
values = interpretConstraint(noteContent)
print "values : ",values
if int(values['relDl']) <= 0 :
	result = False
elif int(values['occKind']['period']) <= 0 :
	result = False
else :
	result = True