* Compilacion a codigo TM
* Archivo: codigo.tm
* Preludio estandar:
  0:     LD  6,0(0) 	load maxaddress from location 0
  1:     ST  0,0(0) 	clear location 0
* Fin del preludio.
  2:    LDC  0,16(0) 	direccion de la cadena
  3:    OUT  0,2,0 	write cadena
  4:     IN  0,0,0 	read integer value
  5:     ST  0,0(5) 	read: guarda
* -> assign
* -> Const
  6:    LDC  0,1(0) 	load const
* <- Const
  7:     ST  0,1(5) 	assign: guarda el valor
* <- assign
* -> assign
* -> Const
  8:    LDC  0,0(0) 	load const
* <- Const
  9:     ST  0,7(5) 	assign: guarda el valor
* <- assign
* -> assign
* -> Const
 10:    LDC  0,0(0) 	load const
* <- Const
 11:     ST  0,8(5) 	assign: guarda el valor
* <- assign
* -> assign
* -> Const
 12:    LDC  0,0(0) 	load const
* <- Const
 13:     ST  0,9(5) 	assign: guarda el valor
* <- assign
* -> assign
* -> Const
 14:    LDC  0,0(0) 	load const
* <- Const
 15:     ST  0,10(5) 	assign: guarda el valor
* <- assign
* -> assign
* -> Const
 16:    LDC  0,0(0) 	load const
* <- Const
 17:     ST  0,11(5) 	assign: guarda el valor
* <- assign
* -> assign
* -> Const
 18:    LDC  0,0(0) 	load const
* <- Const
 19:     ST  0,13(5) 	assign: guarda el valor
* <- assign
* -> assign
* -> Const
 20:    LDC  0,0(0) 	load const
* <- Const
 21:     ST  0,14(5) 	assign: guarda el valor
* <- assign
* -> assign
 22:    LDC  0,0(0) 	load bool
 23:     ST  0,15(5) 	assign: guarda el valor
* <- assign
* -> do-while
* do: el cuerpo regresa aqui
 24:    LDC  0,41(0) 	direccion de la cadena
 25:    OUT  0,2,0 	write cadena
* -> Id
 26:     LD  0,1(5) 	load id value
* <- Id
 27:    OUT  0,0,0 	write int
 28:     IN  0,0,0 	read integer value
 29:     ST  0,2(5) 	read: guarda
 30:    LDC  0,85(0) 	direccion de la cadena
 31:    OUT  0,2,0 	write cadena
* -> Id
 32:     LD  0,1(5) 	load id value
* <- Id
 33:    OUT  0,0,0 	write int
 34:     IN  0,0,0 	read integer value
 35:     ST  0,3(5) 	read: guarda
 36:    LDC  0,129(0) 	direccion de la cadena
 37:    OUT  0,2,0 	write cadena
* -> Id
 38:     LD  0,1(5) 	load id value
* <- Id
 39:    OUT  0,0,0 	write int
 40:     IN  0,0,0 	read integer value
 41:     ST  0,4(5) 	read: guarda
 42:    LDC  0,173(0) 	direccion de la cadena
 43:    OUT  0,2,0 	write cadena
* -> Id
 44:     LD  0,1(5) 	load id value
* <- Id
 45:    OUT  0,0,0 	write int
 46:     IN  0,0,0 	read integer value
 47:     ST  0,5(5) 	read: guarda
 48:    LDC  0,217(0) 	direccion de la cadena
 49:    OUT  0,2,0 	write cadena
* -> Id
 50:     LD  0,1(5) 	load id value
* <- Id
 51:    OUT  0,0,0 	write int
 52:     IN  0,0,0 	read integer value
 53:     ST  0,6(5) 	read: guarda
* -> assign
* -> Op
* -> Id
 54:     LD  0,7(5) 	load id value
* <- Id
 55:     ST  0,0(6) 	op: push left
* -> Id
 56:     LD  0,2(5) 	load id value
* <- Id
 57:     LD  1,0(6) 	op: load left
 58:    ADD  0,1,0 	op +
* <- Op
 59:     ST  0,7(5) 	assign: guarda el valor
* <- assign
* -> assign
* -> Op
* -> Id
 60:     LD  0,8(5) 	load id value
* <- Id
 61:     ST  0,0(6) 	op: push left
* -> Id
 62:     LD  0,3(5) 	load id value
* <- Id
 63:     LD  1,0(6) 	op: load left
 64:    ADD  0,1,0 	op +
* <- Op
 65:     ST  0,8(5) 	assign: guarda el valor
* <- assign
* -> assign
* -> Op
* -> Id
 66:     LD  0,9(5) 	load id value
* <- Id
 67:     ST  0,0(6) 	op: push left
* -> Id
 68:     LD  0,4(5) 	load id value
* <- Id
 69:     LD  1,0(6) 	op: load left
 70:    ADD  0,1,0 	op +
* <- Op
 71:     ST  0,9(5) 	assign: guarda el valor
* <- assign
* -> assign
* -> Op
* -> Id
 72:     LD  0,10(5) 	load id value
* <- Id
 73:     ST  0,0(6) 	op: push left
* -> Id
 74:     LD  0,5(5) 	load id value
* <- Id
 75:     LD  1,0(6) 	op: load left
 76:    ADD  0,1,0 	op +
* <- Op
 77:     ST  0,10(5) 	assign: guarda el valor
* <- assign
* -> assign
* -> Op
* -> Id
 78:     LD  0,11(5) 	load id value
* <- Id
 79:     ST  0,0(6) 	op: push left
* -> Id
 80:     LD  0,6(5) 	load id value
* <- Id
 81:     LD  1,0(6) 	op: load left
 82:    ADD  0,1,0 	op +
* <- Op
 83:     ST  0,11(5) 	assign: guarda el valor
* <- assign
* -> assign
* -> Op
* -> Op
* -> Op
* -> Op
* -> Id
 84:     LD  0,2(5) 	load id value
* <- Id
 85:     ST  0,0(6) 	op: push left
* -> Id
 86:     LD  0,3(5) 	load id value
* <- Id
 87:     LD  1,0(6) 	op: load left
 88:    ADD  0,1,0 	op +
* <- Op
 89:     ST  0,0(6) 	op: push left
* -> Id
 90:     LD  0,4(5) 	load id value
* <- Id
 91:     LD  1,0(6) 	op: load left
 92:    ADD  0,1,0 	op +
* <- Op
 93:     ST  0,0(6) 	op: push left
* -> Id
 94:     LD  0,5(5) 	load id value
* <- Id
 95:     LD  1,0(6) 	op: load left
 96:    ADD  0,1,0 	op +
* <- Op
 97:     ST  0,0(6) 	op: push left
* -> Id
 98:     LD  0,6(5) 	load id value
* <- Id
 99:     LD  1,0(6) 	op: load left
100:    ADD  0,1,0 	op +
* <- Op
101:     ST  0,12(5) 	assign: guarda el valor
* <- assign
102:    LDC  0,261(0) 	direccion de la cadena
103:    OUT  0,2,0 	write cadena
* -> Id
104:     LD  0,1(5) 	load id value
* <- Id
105:    OUT  0,0,0 	write int
106:    LDC  0,268(0) 	direccion de la cadena
107:    OUT  0,2,0 	write cadena
* -> Id
108:     LD  0,12(5) 	load id value
* <- Id
109:    OUT  0,0,0 	write int
* -> if
* -> Logic
* -> Op
* -> Id
110:     LD  0,1(5) 	load id value
* <- Id
111:     ST  0,0(6) 	op: push left
* -> Const
112:    LDC  0,1(0) 	load const
* <- Const
113:     LD  1,0(6) 	op: load left
114:    SUB  0,1,0 	op relacional
115:    JEQ  0,2(7) 	br if true
116:    LDC  0,0(0) 	false case
117:    LDA  7,1(7) 	unconditional jmp
118:    LDC  0,1(0) 	true case
* <- Op
119:     ST  0,0(6) 	op: push left
* -> Op
* -> Id
120:     LD  0,3(5) 	load id value
* <- Id
121:     ST  0,-1(6) 	op: push left
* -> Id
122:     LD  0,13(5) 	load id value
* <- Id
123:     LD  1,-1(6) 	op: load left
124:    SUB  0,1,0 	op relacional
125:    JGT  0,2(7) 	br if true
126:    LDC  0,0(0) 	false case
127:    LDA  7,1(7) 	unconditional jmp
128:    LDC  0,1(0) 	true case
* <- Op
129:     LD  1,0(6) 	op: load left
130:    ADD  0,1,0 	op ||
131:    JGT  0,2(7) 	br if true
132:    LDC  0,0(0) 	false case
133:    LDA  7,1(7) 	unconditional jmp
134:    LDC  0,1(0) 	true case
* <- Logic
135:    JEQ  0,5(7) 	if: salta al else
* if: salto al else va aqui
* -> assign
* -> Id
136:     LD  0,3(5) 	load id value
* <- Id
137:     ST  0,13(5) 	assign: guarda el valor
* <- assign
* -> assign
* -> Id
138:     LD  0,1(5) 	load id value
* <- Id
139:     ST  0,14(5) 	assign: guarda el valor
* <- assign
140:    LDA  7,0(7) 	salta al final
* if: salto al final va aqui
* <- if
* -> if
* -> Op
* -> Id
141:     LD  0,4(5) 	load id value
* <- Id
142:     ST  0,0(6) 	op: push left
* -> Const
143:    LDC  0,0(0) 	load const
* <- Const
144:     LD  1,0(6) 	op: load left
145:    SUB  0,1,0 	op relacional
146:    JEQ  0,2(7) 	br if true
147:    LDC  0,0(0) 	false case
148:    LDA  7,1(7) 	unconditional jmp
149:    LDC  0,1(0) 	true case
* <- Op
150:    JEQ  0,7(7) 	if: salta al else
* if: salto al else va aqui
* -> assign
151:    LDC  0,1(0) 	load bool
152:     ST  0,15(5) 	assign: guarda el valor
* <- assign
153:    LDC  0,285(0) 	direccion de la cadena
154:    OUT  0,2,0 	write cadena
* -> Id
155:     LD  0,1(5) 	load id value
* <- Id
156:    OUT  0,0,0 	write int
157:    LDA  7,0(7) 	salta al final
* if: salto al final va aqui
* <- if
* -> assign
* -> Op
* -> Id
158:     LD  0,1(5) 	load id value
* <- Id
159:     ST  0,0(6) 	op: push left
* -> Const
160:    LDC  0,1(0) 	load const
* <- Const
161:     LD  1,0(6) 	op: load left
162:    ADD  0,1,0 	op +
* <- Op
163:     ST  0,1(5) 	assign: guarda el valor
* <- assign
* -> Op
* -> Id
164:     LD  0,1(5) 	load id value
* <- Id
165:     ST  0,0(6) 	op: push left
* -> Id
166:     LD  0,0(5) 	load id value
* <- Id
167:     LD  1,0(6) 	op: load left
168:    SUB  0,1,0 	op relacional
169:    JLE  0,2(7) 	br if true
170:    LDC  0,0(0) 	false case
171:    LDA  7,1(7) 	unconditional jmp
172:    LDC  0,1(0) 	true case
* <- Op
173:    JNE  0,-150(7) 	do-while: repite si es verdadero
* <- do-while
174:    LDC  0,308(0) 	direccion de la cadena
175:    OUT  0,2,0 	write cadena
* -> Id
176:     LD  0,7(5) 	load id value
* <- Id
177:    OUT  0,0,0 	write int
178:    LDC  0,323(0) 	direccion de la cadena
179:    OUT  0,2,0 	write cadena
* -> Id
180:     LD  0,8(5) 	load id value
* <- Id
181:    OUT  0,0,0 	write int
182:    LDC  0,338(0) 	direccion de la cadena
183:    OUT  0,2,0 	write cadena
* -> Id
184:     LD  0,9(5) 	load id value
* <- Id
185:    OUT  0,0,0 	write int
186:    LDC  0,353(0) 	direccion de la cadena
187:    OUT  0,2,0 	write cadena
* -> Id
188:     LD  0,10(5) 	load id value
* <- Id
189:    OUT  0,0,0 	write int
190:    LDC  0,368(0) 	direccion de la cadena
191:    OUT  0,2,0 	write cadena
* -> Id
192:     LD  0,11(5) 	load id value
* <- Id
193:    OUT  0,0,0 	write int
194:    LDC  0,383(0) 	direccion de la cadena
195:    OUT  0,2,0 	write cadena
* -> Id
196:     LD  0,14(5) 	load id value
* <- Id
197:    OUT  0,0,0 	write int
198:    LDC  0,405(0) 	direccion de la cadena
199:    OUT  0,2,0 	write cadena
* -> Id
200:     LD  0,13(5) 	load id value
* <- Id
201:    OUT  0,0,0 	write int
* -> if
* -> Logic
* -> Id
202:     LD  0,15(5) 	load id value
* <- Id
203:    JEQ  0,2(7) 	br if true
204:    LDC  0,0(0) 	false case
205:    LDA  7,1(7) 	unconditional jmp
206:    LDC  0,1(0) 	true case
* <- Logic
207:    JEQ  0,3(7) 	if: salta al else
* if: salto al else va aqui
208:    LDC  0,433(0) 	direccion de la cadena
209:    OUT  0,2,0 	write cadena
210:    LDA  7,0(7) 	salta al final
* if: salto al final va aqui
* <- if
* Fin de la ejecucion.
211:   HALT  0,0,0 
* Cadenas en la memoria de datos
 16:  STR "ingrese el total de anos"
 41:  STR " ingrese cantidad de vinos tipo 1 en el ano"
 85:  STR " ingrese cantidad de vinos tipo 2 en el ano"
129:  STR " ingrese cantidad de vinos tipo 3 en el ano"
173:  STR " ingrese cantidad de vinos tipo 4 en el ano"
217:  STR " ingrese cantidad de vinos tipo 5 en el ano"
261:  STR "Anio: "
268:  STR "Total del anio: "
285:  STR "Anio sin vino tipo 3: "
308:  STR "Total vino 1: "
323:  STR "Total vino 2: "
338:  STR "Total vino 3: "
353:  STR "Total vino 4: "
368:  STR "Total vino 5: "
383:  STR "Anio con mas vino 2: "
405:  STR "Litros producidos ese ano: "
433:  STR "Todos los anios hubo vino tipo 3"
