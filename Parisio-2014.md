# Un Enfoque de MPC para la Optimización de Operaciones de Microrredes

**Traducido por Deepseek**

Alessandra Parisio, Member, IEEE, Evangelos Rikos, and Luigi Glielmo, Senior Member, IEEE

**Abstract:** Las microrredes son subsistemas de la red de distribución que comprenden capacidades de generación, dispositivos de almacenamiento y cargas controlables, operando como un único sistema controlable ya sea conectado o aislado de la red eléctrica convencional (red de servicio). En este paper, presentamos un estudio sobre la aplicación de un enfoque de control predictivo basado en modelos al problema de optimizar eficientemente las operaciones de una microrred mientras se satisface una demanda variable en el tiempo y las restricciones operativas. El problema general se formula utilizando programación lineal entera mixta (MILP), que puede resolverse de manera eficiente mediante el uso de solvers comerciales sin recurrir a heurísticas complejas o técnicas de descomposición. Por lo tanto, la formulación MILP conduce a mejoras significativas en la calidad de la solución y la carga computacional. Se emplea un caso de estudio de una microrred para evaluar el rendimiento de la estrategia de control basada en optimización en línea y se discuten los resultados de simulación. El método se aplica a una microrred experimental ubicada en Atenas, Grecia. Los resultados experimentales muestran la viabilidad y efectividad del enfoque propuesto.

**Términos de índice:** Microrredes, sistemas dinámicos lógicos mixtos, programación lineal entera mixta (MILP), control predictivo basado en modelos (MPC), optimización.

## I. INTRODUCCIÓN

LA NECESIDAD de satisfacer la creciente demanda de energía de manera sostenible requiere redes de distribución de energía activas, es decir, redes de distribución con la posibilidad de flujos de energía bidireccionales que controlen una combinación de recursos energéticos distribuidos (DERs), como generadores distribuidos (DGs) y dispositivos de energía renovable. En este escenario, el concepto de microrred es un enfoque prometedor. Es un sistema energético integrado que consiste en cargas y DERs interconectados, que pueden operar en paralelo con la red o en un modo de isla intencional (ver [1] y [2]). Una microrred típica comprende: 1) unidades de almacenamiento; 2) DGs, que son unidades controlables; 3) recursos de energía renovable (RESs), que son dispositivos no controlables; y 4) cargas controlables, que pueden ser recortadas (o desconectadas) cuando sea más conveniente. Además, una microrred puede comprar y vender energía a sus proveedores de energía.

Una de las motivaciones principales detrás del uso de microrredes es que son capaces de gestionar y coordinar DGs, almacenamientos y cargas de manera más descentralizada, reduciendo la necesidad de coordinación y gestión centralizada [3]. Por lo tanto, la optimización de las operaciones de la microrred es extremadamente importante para gestionar sus recursos energéticos de manera rentable [2], [4].

En este escenario, se necesitan nuevos requisitos de modelado, por ejemplo, el modelado del almacenamiento debe incorporarse en el problema de planificación de operaciones para coordinar el uso del almacenamiento con la generación de RES y los precios de la energía, y abordar la complejidad del programa de carga/descarga [5]. Es importante notar que no existen herramientas de modelado actuales que incluyan cargas controlables y modelado de almacenamiento de energía en un entorno de red inteligente [6].

Obsérvese además que una formulación completa del problema de planificación de operación óptima de una microrred incluye el modelado de almacenamientos, políticas del lado de la demanda para cargas controlables [gestión del lado de la demanda (DSM)], intercambio de energía con la red eléctrica convencional. El modelado de la microrred necesita tanto variables de decisión continuas (como tasas de carga/descarga del almacenamiento) como discretas (como estados ON/OFF de los DGs y cargas controladas por DSM), y el problema se formula generalmente como un problema no lineal entero mixto (MINLP) (ver [7]-[9]), para el cual no existe una técnica de solución exacta.

Otro aspecto relevante en la gestión de microrredes, que la complica aún más, es hacer frente a la incertidumbre en la demanda de energía, la generación de RES y los precios de la energía.

Las capacidades de modelado y los avances computacionales de los algoritmos de problemas enteros mixtos (MIP), han llevado a varios operadores de sistemas independientes y organizaciones regionales de transmisión a implementar métodos de solución basados en MIP para encontrar una mejor solución para resolver los problemas del mercado diario y en tiempo real [10]; es decir, no resolver los problemas de compromiso de unidades con optimalidad completa puede causar varios problemas [11].

Por lo tanto, es necesario encontrar una formulación manejable del problema de optimización de operación de microrredes, que incluya las características clave específicas de una microrred.

En este paper, abordamos la planificación óptima de operación de una microrred. Este problema tiene como objetivo minimizar los costos operativos generales de la microrred para satisfacer la demanda de carga prevista de un período determinado (típicamente un día) mientras se satisfacen restricciones operativas complejas, como el balance de energía, y las restricciones de los generadores controlables (tiempo mínimo de operación y tiempo mínimo de parada).

### 1.A. Revisión de la Literatura

Debido a la complejidad del problema de optimización de microrredes y a los grandes beneficios económicos que podrían derivarse de su mejor solución, se está dedicando una atención considerable al desarrollo de mejores algoritmos de optimización y marcos de modelado adecuados. Se han propuesto metaheurísticas y heurísticas para resolver el problema de despacho de energía para microrredes, como algoritmos genéticos [12], estrategias evolutivas y algoritmos de búsqueda tabú [13].

Los estudios han sugerido que las microrredes pueden lograr un alto rendimiento a través de: 1) algoritmos de control avanzados que tengan en cuenta la incertidumbre del sistema y se basen en condiciones futuras previstas; 2) implementación de respuesta a la demanda; 3) uso óptimo de dispositivos de almacenamiento para compensar los desequilibrios físicos; y 4) aplicación de enfoques óptimos en lugar de basados en heurísticas (ver [14]-[17] y las referencias en ellos). Típicamente, los enfoques propuestos son computacionalmente intensivos y no adecuados para aplicaciones en tiempo real, o pueden producir soluciones subóptimas (ver [17]-[19]). Además, en los trabajos antes mencionados, o el problema de optimización permanece no lineal u otras características importantes, como los tiempos mínimos de encendido y apagado y los programas del lado de la demanda, son descuidadas. Por ejemplo, en [20] el problema de optimización de microrredes se aborda resolviendo varios MINLPs (por ejemplo, un problema separado para el compromiso de unidades, uno para la gestión del almacenamiento, y así sucesivamente).

Recientemente, el control predictivo por modelos (MPC) ha llamado la atención de la comunidad de sistemas de energía debido a varios factores [21]: 1) se basa en el comportamiento futuro del sistema y en predicciones, lo cual es atractivo para sistemas que dependen en gran medida de la demanda y de pronósticos de generación de energía renovable; 2) proporciona un mecanismo de retroalimentación, que hace que el sistema sea más robusto frente a la incertidumbre; y 3) puede manejar restricciones del sistema de energía, como la capacidad del generador y las restricciones de tasa de rampa. Se ha propuesto comúnmente un método MPC para resolver el problema de compromiso de unidades con generación de energía eólica (ver [22]). Además, se acaba de desarrollar un esquema de control de voltaje y var dinámico basado en MPC para el control de potencia reactiva, con el fin de evitar condiciones de voltaje inestables en microrredes, especialmente durante la operación en modo isla sin soporte de la red eléctrica convencional [23].

Se pueden encontrar algunos trabajos en la literatura que abordan el MPC para el despacho óptimo en sistemas de energía. Los autores en [24] modelan una planta de ciclo combinado utilizando sistemas híbridos para describir tanto las dinámicas continuas/discretas como el cambio entre diferentes condiciones de operación. Luego, las operaciones de la planta se optimizan económicamente a través de MPC teniendo en cuenta la variabilidad temporal tanto de los precios como de las demandas de electricidad/vapor. Ferrari-Trecate et al. [24] proponen un algoritmo MPC para resolver el problema de despacho económico con una gran presencia de recursos intermitentes. Sin embargo, muchas características clave de las microrredes, como los programas del lado de la demanda, los almacenamientos y los estados ON/OFF de los generadores no son consideradas. En [26] y [27], se aplica un MPC para gestionar los flujos de energía dentro de un sistema doméstico equipado con una unidad de micro-cogeneración de calor y electricidad (micro-CHP). Además, el hogar puede comprar y vender electricidad al proveedor de energía y el calor y la electricidad pueden almacenarse en dispositivos de almacenamiento específicos. Hooshmand et al. [28] y Xia et al. [29] aplican un marco MPC para resolver el despacho económico dinámico, que tiene como objetivo minimizar el costo de generación durante un intervalo de tiempo particular (el intervalo de despacho). Luego, el objetivo es decidir el despacho de energía para satisfacer la demanda al mínimo costo sujeto a límites en la generación de energía y las tasas de rampa.

En [30], se diseña un sistema de control supervisorio mediante MPC para un sistema de generación de energía eólica/solar, que calcula las referencias de potencia para los subsistemas eólico y solar en cada instante de muestreo mientras minimiza una función de costo adecuada. Las referencias de potencia se envían a dos controladores locales, que llevan a los dos subsistemas a las referencias de potencia solicitadas. En [31], el controlador MPC supervisorio centralizado se reemplaza con dos controladores MPC supervisorios distribuidos, cada uno responsable de proporcionar trayectorias de referencia óptimas al controlador local del subsistema correspondiente. El problema de optimización supervisorio resuelto es no lineal y no convexo, y no se abordan varios problemas, por ejemplo, el arranque o parada del sistema.

En [32], se propone un sistema de gestión de energía basado en una estrategia de horizonte móvil para una microrred en isla que comprende paneles fotovoltaicos (PV), dos turbinas eólicas, un generador diésel y un sistema de almacenamiento de energía. El problema incluye varias restricciones no lineales asociadas con el modelado de las dos unidades controlables (el generador diésel y el sistema de almacenamiento). Las restricciones no lineales se aproximan mediante modelos lineales por partes y el problema de optimización se resuelve utilizando programación lineal entera mixta (MILP), produciendo soluciones subóptimas.

Finalmente, nos gustaría señalar que cuando se consideran elementos de almacenamiento, generalmente el almacenamiento se modela como un sistema de primer orden en tiempo discreto con dos variables continuas que representan la potencia de carga y descarga multiplicadas por eficiencias de carga y descarga adecuadas, y diferentes. Ese enfoque no descarta la posibilidad de que la solución óptima contemple la carga y descarga simultánea del almacenamiento, una política físicamente irrealizable. Tal resultado puede ocurrir como consecuencia matemática de un excedente de potencia generada por RES no previsto, límites en la potencia intercambiada con la red eléctrica convencional y costos del nivel de almacenamiento. Este problema nunca ha sido discutido en los estudios correspondientes. Debido al diferente factor multiplicativo en la carga y descarga, una variable continua, que puede tomar valores tanto positivos como negativos, no puede representar correctamente el comportamiento del almacenamiento. De manera similar, la interacción con la red eléctrica convencional debe modelarse para evitar la venta y compra simultánea bajo ciertas circunstancias del mercado.

### 1.B. Suposiciones Principales

En una estructura de control de microrredes, se deben abordar varios aspectos, cuyos requisitos involucran diferentes enfoques de control y diferentes escalas de tiempo: 1) control eléctrico rápido de la fase, frecuencia y voltaje de los componentes individuales. En una jerarquía de controladores, nuestro objetivo es una optimización de alto nivel de las operaciones de la microrred; se supone que la estabilidad de voltaje, la calidad de la energía y la frecuencia tienen mayor prioridad y que son controladas en el nivel de control inferior. Notablemente, enfocamos nuestro estudio en el modo conectado a la red, lo que implica que la frecuencia de la microrred se mantiene dentro de un rango estrecho por la red eléctrica convencional. Además, al limitar la capacidad de la línea en el problema de optimización, se preserva la calidad de la energía en estado estacionario, es decir, nuestro enfoque no viola los límites de voltaje según la red y no causa congestión en las líneas. 2) El controlador de alto nivel se ocupa del comportamiento a largo plazo del sistema y es muy débilmente dependiente del comportamiento transitorio de las dinámicas rápidas. Por lo tanto, se puede hacer una suposición de estado estacionario para los componentes de la microrred de manera segura sin mucha pérdida de precisión. 3) El controlador de alto nivel de la microrred tiene conocimiento de la red gestionada; conoce la capacidad de generación existente, la capacidad de almacenamiento, las restricciones de la red, los precios de la energía del mercado y los contratos bilaterales. 4) El operador de la microrred es la entidad única a cargo de la gestión, con el objetivo de optimizar las ganancias. Puede tomar decisiones económicas, como vender o comprar energía dependiendo de las capacidades y costos de generación locales y los precios de la energía. 5) Debido al tiempo de muestreo constante $\Delta T = t_{k + 1} - t_k$ , existe una relación constante entre energía y potencia en cada intervalo.

### 1.C. Contribuciones Principales

Presentamos un enfoque orientado al control para el modelado y la optimización de alto nivel de microrredes y proponemos el uso de MPC en combinación con MILP [34], [35]. Las operaciones de la microrred se deciden sobre la base de predicciones del comportamiento futuro del sistema y de pronósticos de generación de energía renovable y demanda.

Para garantizar un comportamiento factible para el almacenamiento y la interacción con la red (por ejemplo, carga y descarga no simultáneas, compra y venta), utilizamos el enfoque descrito en [36] y empleamos el marco de sistemas dinámicos lógicos mixtos. Nos gustaría señalar que en la formulación del problema propuesta, solo las funciones de consumo de combustible y emisiones de los generadores se aproximan en caso de que deban expresarse como funciones no lineales, lo cual no siempre es necesario para los componentes de la microrred. Asumimos funciones no lineales de consumo de combustible y emisiones de los generadores para plantear la formulación del problema de la manera más general posible.

En nuestro enfoque, nos esforzamos por incluir tantos detalles como fuera posible, y por utilizar y mantener el problema de optimización de la microrred resoluble sin recurrir a técnicas de descomposición o heurísticas. Además, modelamos las características técnicas y físicas de los generadores utilizando el menor número posible de restricciones y variables.

Además, se introduce un mecanismo de retroalimentación (MPC), que compensa la incertidumbre en las operaciones de la microrred asociada con: 1) las salidas de potencia de los RES; 2) la carga variable en el tiempo; y 3) los precios de la energía variables en el tiempo. Adicionalmente, dado que el óptimo se alcanza en un tiempo de cómputo razonable, se puede utilizar un tiempo de muestreo más corto (por ejemplo, 15 minutos, en lugar de 30 o 60), lo que permite calcular soluciones más precisas y efectivas.

Este artículo extiende el estudio preliminar presentado en [37] mediante: 1) la discusión de resultados experimentales obtenidos de una microrred ubicada en Atenas, Grecia; 2) la inclusión de resultados de simulación adicionales y una comparación con un algoritmo heurístico; y 3) la consideración de los costos de la potencia intercambiada con la unidad de almacenamiento en la función objetivo. Además, se calculan los pronósticos de generación de energía renovable y de demanda.

En resumen, nuestras contribuciones son: 1) el desarrollo de un modelo novedoso del sistema de microrred en su conjunto adoptando un enfoque de modelado formalizado, que es adecuado para ser utilizado en esquemas de optimización en línea; 2) el desarrollo de un esquema MPC para minimizar los costos operativos de la microrred; 3) la presentación de resultados de simulación que muestran la efectividad de la rutina de optimización propuesta; y 4) la aplicación del método a una microrred experimental ubicada en Atenas, Grecia, y la estimación de todos los parámetros y costos requeridos para llevar a cabo los experimentos.

### 1.D. Estructura del Documento

Este paper se organiza además de la siguiente manera: 1) el sistema de microrred se describe y el enfoque de modelado de la microrred se esboza en la Sección II; 2) la optimización de operaciones se describe luego en la Sección III; 3) algunos resultados de simulación se discuten en las Secciones IV y V y en la Sección VI se presentan los resultados experimentales; y 4) finalmente, se extraen conclusiones en la Sección VII.

### 1.E. Nomenclatura

Los pronósticos, los parámetros y las variables de decisión utilizados en la formulación propuesta se describen, respectivamente, en las Tablas I-III, donde, por simplicidad, omitimos el subíndice $i$ cuando nos referimos a la $i$-ésima unidad.

Observamos que el costo de consumo de combustible para una unidad DG se asume tradicionalmente como una función cuadrática de la forma $C^{\mathrm{DG}}(P) = a_1P^2 + a_2P + a_3$.

En las siguientes secciones, los vectores y matrices se denotan en negrita.

**TABLA I** PARÁMETROS

| Parámetros | Descripción |
|------------|-------------|
| $N_g, N_l, N_c$ | número respectivamente de unidades DG, cargas críticas y cargas controlables |
| $C^{\mathrm{DG}}(P)$ | curva de costo de consumo de combustible de una unidad DG dependiendo de la potencia generada |
| $a_1, a_2, a_3$ | coeficientes de costo de $C^{\mathrm{DG}}(P)$ [€/kWh]², €/kWh, €] |
| $OM$ | costo operativo y de mantenimiento de una unidad DG [€/h] |
| $OM^b$ | costo operativo y de mantenimiento de la potencia intercambiada con la unidad de almacenamiento [€/kWh] |
| $R_{i,max}$ | límite de rampa de una unidad DG [kWh] |
| $T^{up}, T^{down}$ | tiempo mínimo de encendido y apagado de una unidad DG [unidades de tiempo] |
| $x^{sb}$ | pérdida de energía 'fisiológica' del almacenamiento [kWh] |
| $x^{b}_{min}, x^{b}_{max}$ | nivel de energía mínimo, máximo de la unidad de almacenamiento [kWh] |
| $C^b$ | límite de potencia de salida del almacenamiento [kW] |
| $T^g$ | límite máximo de flujo de potencia de interconexión (en el punto de acoplamiento común) [kW] |
| $P_{min}, P_{max}$ | nivel de potencia mínimo, máximo de una unidad DG [kW] |
| $\eta_c, \eta_d$ | eficiencias de carga y descarga del almacenamiento |
| $\beta_{min}, \beta_{max}$ | recorte mínimo, máximo permitido de una carga controlable |
| $c^{SU}, c^{SD}$ | costos de arranque y parada de una unidad DG [€] |
| $P^c$ | nivel de potencia preferido de una carga controlable [kW] |
| $\rho_c$ | peso de penalización sobre los recortes |

**TABLA II** PRONÓSTICOS

| Pronósticos | Descripción |
|-------------|-------------|
| $P^{res}$ | suma de producción de potencia de los RES [kW] |
| $D$ | nivel de potencia requerido de una carga crítica [kW] |
| $c^P, c^S$ | precios de compra y venta de energía [€/kWh] |

**TABLA III** VARIABLES DE DECISIÓN Y LÓGICAS

| Variables | Descripción |
|-----------|-------------|
| $\delta$ | estado apagado(0)/encendido(1) de una unidad DG |
| $\delta^b$ | modo de descarga(0)/carga(1) de la unidad de almacenamiento |
| $\delta^g$ | modo de exportación(0)/importación(1) hacia/desde la red eléctrica convencional |
| $P$ | nivel de potencia de una unidad DG [kW] |
| $P^b$ | potencia intercambiada (positiva para carga) con la unidad de almacenamiento [kW] |
| $P^g$ | nivel de potencia de importación(positiva)/exportación(negativa) desde/hacia la red eléctrica convencional [kW] |
| $x^b$ | nivel de energía almacenada [kWh] |
| $\beta$ | porcentaje de potencia recortada |

## II. DESCRIPCIÓN DEL SISTEMA, MODELADO Y RESTRICCIONES

Aquí, describimos brevemente las características clave de la arquitectura de microrred considerada en este paper y asociamos una posible configuración de modelado con el objetivo de mantener el problema tratable y adecuado para el cálculo en tiempo real.

### 2.A. Cargas

Consideramos dos tipos de cargas:

1) cargas críticas, es decir, niveles de demanda relacionados con procesos esenciales que deben ser siempre satisfechos;
2) cargas controlables, es decir, cargas que pueden ser reducidas o desconectadas durante restricciones de suministro o situaciones de emergencia (por ejemplo, dispositivos en espera, iluminación diurna).

En los programas de respuesta a la demanda, los clientes especifican el nivel de recorte de las cargas controlables. Las cargas controlables tienen un nivel preferido, pero su magnitud es flexible para que el nivel de demanda pueda reducirse cuando sea conveniente o necesario (por ejemplo, en modo isla). Esto conduce a incomodidad para los usuarios, por lo tanto, se asocia un cierto costo con el recorte/desconexión de carga (una penalización para la microrred). Definimos una variable continua, $0\leq \beta_{c}(k)\leq 1$, asociada a cada carga controlable $c$ y a cada instante de muestreo $k$. Esta variable representa el porcentaje del nivel de potencia preferido que se recortará en el tiempo $k$ para mantener las operaciones de la microrred factibles (por ejemplo, en modo isla) o más económicamente convenientes. Si no se permite ningún recorte en un cierto tiempo $\hat{k}$, se puede establecer una restricción de igualdad, $\beta_{c}(\hat{k}) = 0$.

### 2.B. Dinámica del Almacenamiento

Para una unidad de almacenamiento, denotando por $x^{b}(k)$ el nivel de energía almacenada en el tiempo $k$ dividido por $\Delta T$ y por $P^{b}(k)$ la potencia intercambiada con el dispositivo de almacenamiento en el tiempo $k$, consideramos el siguiente modelo en tiempo discreto de una unidad de almacenamiento:

$$x^{b}(k + 1) = x^{b}(k) + \eta P^{b}(k) - x^{sb} \quad (1)$$

donde

$$\eta = \left\{ \begin{array}{ll}\eta^{c}, & \mathrm{si} \ P^{b}(k) > 0 \ \mathrm{(modo~carga)}\\ 1 / \eta^{d}, & \mathrm{en~caso~contrario} \end{array} \right. \quad (2)$$

con $0< \eta^{c},\eta^{d}< 1$

Las eficiencias de carga y descarga contabilizan las pérdidas y $x_{sb}$ denota una degradación constante de la energía almacenada en el intervalo de muestreo. Si la potencia intercambiada en el tiempo $k$, $P^{b}(k)$, es mayor que cero, esto cargará el dispositivo de almacenamiento; de lo contrario, el dispositivo de almacenamiento se descargará.

Usando el enfoque estándar descrito en [36], introducimos una variable binaria $\beta^{b}(k)$ y una variable auxiliar $z^{b}(k) = \beta^{b}(k)P^{b}(k)$ para modelar la siguiente condición lógica y la dinámica del almacenamiento:

$$P^{b}(k)\geq 0\Longleftrightarrow \beta^{b}(k) = 1 \quad (3)$$

y

$$x^{b}(k + 1) = \left\{ \begin{array}{ll}x^{b}(k) + \eta^{c}P^{b}(k) - x^{sb}, & \mathrm{si} \ \beta^{b}(k) = 1\\ x^{b}(k) + 1 / \eta^{d}P^{b}(k) - x^{sb}, & \mathrm{en~caso~contrario} \end{array} \right.$$

luego, expresamos las condiciones lógicas como desigualdades lineales enteras mixtas. Al recopilar tales desigualdades, podemos reescribir la dinámica del almacenamiento y las restricciones correspondientes en la siguiente forma compacta (el lector interesado puede consultar [36] para detalles guía):

$$x^{b}(k + 1) = x^{b}(k) + (\eta^{c} - 1 / \eta^{d})z^{b}(k) + 1 / \eta^{d}P^{b}(k) - x^{sb}$$
$$\mathrm{sujeto~a~}\mathbf{E}_{1}^{b}\beta^{b}(k) + \mathbf{E}_{2}^{b}z^{b}(k)\leq \mathbf{E}_{3}^{b}P^{b}(k) + \mathbf{E}_{4}^{b}$$

donde los vectores columna $\mathbf{E}_{1}^{b},\mathbf{E}_{2}^{b},\mathbf{E}_{3}^{b},\mathbf{E}_{4}^{b}$ se derivan fácilmente de las seis desigualdades lineales enteras mixtas que modelan las condiciones if...then descritas en (3) y la variable auxiliar

$$z^{b}(k) = \beta^{b}(k)P^{b}(k) \quad (5)$$

que oculta una no linealidad. Las desigualdades enteras mixtas se proporcionan en el Apéndice C, (18) y (19) con $m = - C^{b}$, $M = C^b$, $f(k) = P^b (k)$ y $\delta = \delta^b (k)$. Por ejemplo, la condición lógica (3) puede reescribirse como [ver (18) en el Apéndice C]

$$\left\{ \begin{array}{ll}C^b \delta^b (k) & \leq P^b (k) + C^b \\ -(C^b +\epsilon) \delta^b (k) & \leq -P^b (k) - \epsilon . \end{array} \right. \quad (6)$$

Entonces, los dos primeros elementos de los vectores columna en (4) son

$$\mathbf{E}_1^{\mathbf{b}'} = \left[C^b - (C^b +\epsilon)\dots \right]$$
$$\mathbf{E}_2^{\mathbf{b}'} = \left[0 0\dots \right]$$
$$\mathbf{E}_3^{\mathbf{b}'} = \left[1 - 1\dots \right]$$
$$\mathbf{E}_4^{\mathbf{b}'} = \left[C^b -\epsilon \dots \right].$$

Los otros elementos se obtienen imponiendo las desigualdades (19) del Apéndice C a la variable $z^b (k)$, con $f(k) = P^b (k)$ y $\delta = \delta^b (k)$. Se proporcionan más detalles en el Apéndice.

El balance entre la producción y el consumo de energía debe cumplirse en cada instante $k$, por lo que se impone la siguiente restricción de igualdad:

$$ \begin{array}{l}{P^b (k) = \sum_{j = 1}^{N_g}P_i(k) + P^{\mathrm{res}}(k) + P^g (k)}\\ {-\sum_{j = 1}^{N_l}D_j(k) - \sum_{h = 1}^{N_c}[1 - \beta_h(k)]D_h^c (k).} \end{array} \quad (7)$$

Si recopilamos todas las variables de decisión en el vector $\mathbf{u}(k)$ y todas las perturbaciones conocidas (obtenidas mediante pronósticos) en el vector $\mathbf{w}(k)$, podemos reescribir $P^b (k)$ de la siguiente manera:

$$P^b (k) = \mathbf{F}^\prime (k)\mathbf{u}(k) + \mathbf{f}^\prime \mathbf{w}(k) \quad (8)$$

con

$$ \begin{array}{rl} & {\mathbf{u}(k) = \left[\mathbf{P}^\prime (k)P^g (k)\beta^\prime (k)\delta^\prime (k)\right]^\prime \in \mathbb{R}^{N_u}\times \{0,1\}^{N_g}}\\ & {\mathbf{w}(k) = \left[P^{\mathrm{res}}(k)\mathbf{D}^\prime (k)\mathbf{D}^\prime (k)\right]^\prime \in \mathbb{R}^{N_w}} \end{array} \quad (8)$$

donde $N_u = N_g + 1 + N_c$, $N_{w} = 1 + N_{l} + N_{c}$, $\mathbf{P}(k)$, $\delta (k)$, $\mathbf{D}(k)$, $\mathbf{D}^\epsilon (k)$ y $\beta (k)$ son vectores columna que contienen, respectivamente, todos los niveles de potencia, los estados APAGADO/ENCENDIDO de los generadores, la demanda crítica, los niveles de potencia de las cargas controlables y los recortes. Los vectores $\mathbf{F}^\prime (k)$ y $\mathbf{f}^\prime$ se proporcionan en el Apéndice A.

Por lo tanto, el nivel de almacenamiento puede expresarse como una función afín sustituyendo (8) en (4) de la siguiente manera:

$$ \begin{array}{r}x^{b}(k + 1) = x^{b}(k) + (\eta^{c} - 1 / \eta^{d})z^{b}(k)\\ +1 / \eta^{d}[\mathbf{F}^{\prime}(k)\mathbf{u}(k) + \mathbf{f}^{\prime}\mathbf{w}(k)] - x^{b}. \end{array} \quad (9)$$

### 2.C. Interacción con la red de servicio

Cuando está conectada a la red, la microrred puede vender y comprar energía a/de la red de servicio. Siguiendo el mismo procedimiento descrito anteriormente, introducimos una variable binaria $\delta^g (k)$ y una variable auxiliar $C^g (k)$ para modelar la posibilidad de comprar o vender energía a la red de servicio. Las siguientes declaraciones lógicas se cumplen:

$$P^g (k)\geq 0\iff \delta^g (k) = 1$$

y

$$C^g (k) = \left\{ \begin{array}{ll}c^P (k)P^g (k), & \mathrm{si} \ \delta^g (k) = 1 \\ c^S (k)P^g (k), & \mathrm{en~caso~contrario} \end{array} \right.$$

nuevamente, expresamos las condiciones if... then como desigualdades lineales enteras mixtas. Entonces, el comportamiento de compra/venta de la microrred puede expresarse mediante las siguientes desigualdades lineales enteras mixtas en forma compacta:

$$\mathbf{E}_1^g \delta^g (k) + \mathbf{E}_2^g C^g (k) \leq \mathbf{E}_3^g (k)P^g (k) + \mathbf{E}_4^g. \quad (10)$$

Los vectores columna $\mathbf{E}_1^g,\mathbf{E}_2^g,\mathbf{E}_3^g (k),\mathbf{E}_4^g$ se proporcionan en el Apéndice A. La matriz $\mathbf{E}_3^g (k)$ es generalmente variable en el tiempo debido a los precios de la energía variables en el tiempo. Recordamos que la interacción con la red eléctrica convencional solo se permite cuando la microrred está en modo conectado a la red.

### 2.D. Condiciones de Operación del Generador

Las restricciones operativas, en cada instante de muestreo $k$ sobre la cantidad mínima de tiempo durante la cual una unidad de generación controlable debe mantenerse ENCENDIDA/APAGADA (tiempos mínimos de encendido/apagado) pueden expresarse mediante las siguientes desigualdades lineales enteras mixtas sin recurrir a ninguna variable adicional:

$$\begin{array}{rl} & {\delta_i(k) - \delta_i(k - 1)\leq \delta_i(\tau),\ (\text{ OFF/ON switch})}\\ & {\delta_i(k - 1) - \delta_i(k)\leq 1 - \delta_i(\tau),\ (\text{ON/OFF switch})} \end{array} \quad (11)$$

con $i = 1,\ldots ,N_g$, $\tau = k + 1,\ldots ,\min (k + T_i^{\mathrm{up}} - 1,T)$ si consideramos las restricciones sobre el tiempo mínimo de encendido o $\tau = k + 1,\ldots ,\min (k + T_i^{\mathrm{down}} - 1,T)$ en caso contrario.

Considere, por ejemplo, la $i$-ésima unidad en el paso de tiempo $\hat{k}$ con $\delta_i(\hat{k} - 1) = 0$ lo que significa que la unidad estaba APAGADA durante el período de muestreo anterior. Si se asigna el valor 1 a la variable de optimización $\delta_i(\hat{k})$ las primeras $T_i^{\mathrm{up}} - 1$ restricciones en (11) forzarán a todas las variables de optimización binarias correspondientes al estado ENCENDIDO/APAGADO de la unidad a ser iguales a 1 para los siguientes $T_i^{\mathrm{up}} - 1$ instantes de muestreo. Es decir, para $T_i^{\mathrm{up}} = 3$

$$\begin{array}{rl} & {\delta_i(\hat{k}) - \delta_i(\hat{k} - 1)\leq \delta_i(\hat{k} +1)}\\ & {\delta_i(\hat{k}) - \delta_i(\hat{k} - 1)\leq \delta_i(\hat{k} +2)} \end{array} \quad (12)$$

lo que fuerza al lado derecho de las desigualdades (12) a ser igual a 1 para satisfacer las restricciones.

También modelamos el comportamiento de arranque y parada de la unidad DG para contabilizar los costos correspondientes. Por esta razón, se introducen dos variables auxiliares, $SU_i(k)$ y $SD_i(k)$, que representan, respectivamente, el costo de arranque y el costo de parada para la $i$-ésima unidad de generación DG en el tiempo $k$. Estas variables auxiliares deben satisfacer las siguientes restricciones lineales enteras mixtas:

$$\begin{array}{rl} & {SU_i(k)\geq c_i^{SU}(k)[\delta_i(k) - \delta_i(k - 1)]}\\ & {SD_i(k)\geq c_i^{SD}(k)[\delta_i(k - 1) - \delta_i(k)]}\\ & {SU_i(k)\geq 0}\\ & {SD_i(k)\geq 0} \end{array} \quad (13)$$

con $i = 1,\ldots ,N_g$ (ver [38] y las referencias en él).

## III. OPTIMIZACIÓN DE OPERACIONES

El problema de optimización de operaciones de la microrred consiste en decidir lo siguiente:

1) cuándo debe arrancarse y detenerse cada unidad de generación (compromiso de unidades);
2) cuánto debe generar cada unidad para satisfacer esta demanda al mínimo costo (despacho económico);
3) cuándo debe cargarse o descargarse el dispositivo de almacenamiento;
4) cuándo y cuánta energía debe comprarse o venderse a la red eléctrica convencional (cuando la microrred está en modo conectado a la red);
5) programa de recorte (qué cargas controlables deben ser desconectadas/recortadas y cuándo);
6) cuánta energía debe almacenarse.

Utilizando el enfoque de modelado de la Sección II, el problema puede formularse como un problema de optimización MILP, que genera un plan óptimo. Este plan estará sujeto a incertidumbre, el modelo será imperfecto, el estado del sistema no evolucionará como se predijo. El MILP único es una solución en lazo abierto, que no tiene en cuenta estas incertidumbres. Un posible remedio es incrustar las optimizaciones MILP dentro de un marco MPC, de modo que pueda implementarse una ley de control con retroalimentación y la incertidumbre pueda ser potencialmente compensada. En ausencia de incertidumbre, estas dos soluciones coinciden.

Para formular el problema MPC, a continuación definimos la función de costo asociada al MILP.

### 3.A. Aproximación Lineal de la Función de Costo de Consumo de Combustible

Dado que la experiencia ha demostrado que los programas lineales enteros mixtos son computacionalmente más eficientes que los programas cuadráticos [39], la función de costo de combustible de un generador DG, $C^{\mathrm{DG}}(P) = a_1P^2 + a_2P + a_3$ se aproxima por el máximo de funciones afines sin introducir variables binarias [40]

$$C^{\mathrm{DG}}(P)\approx \max_{j = 1,\dots,n}\{S_jP + s_j\} = \| \mathbf{S}P + \mathbf{s}\|_{\infty} \quad (14)$$

donde $P$ es la potencia generada, y $S$ y $s$ se obtienen linealizando la función en $n$ puntos (el subíndice $j$ extrae la $j$-ésima fila de $S$ y $s$).

### 3.B. Función de Costo

La optimización económica de la microrred se logra eligiendo una función objetivo que represente los costos operativos a minimizar. La siguiente función cuadrática incluye costos asociados con la producción de energía y las decisiones de arranque y parada, junto con posibles ganancias y penalizaciones por recorte:

$$ \begin{array}{l}\sum_{k = 0}^{T - 1}\sum_{i = 1}^{N_g}[C_i^{\mathrm{DG}}(P_i(k)) + OM_i\delta_i(k) + SU_i(k) + SD_i(k)]\\ \displaystyle +\mathrm{OM}^b [2z^b (k) - P^b (k)] + C^g (k) + \rho_c\sum_{h = 1}^{N_c}\beta_h(k)D_h^c (k) \end{array} \quad (15)$$

donde $k$ es el instante de tiempo, $T$ es la longitud del horizonte de predicción, y $2z^b (k) - P^b (k)$ modela el valor absoluto de la potencia intercambiada con la unidad de almacenamiento utilizando (5) y (8). Observamos que es posible considerar también costos operativos y de mantenimiento de la $i$-ésima unidad DG que dependen de la potencia generada; en este caso, el término $OM_iP_i(k)$ debe añadirse en la función objetivo. El término $\mathrm{OM}^b [2z^b (k) - P^b (k)]$ reduce la frecuencia de carga y descarga. Recordamos que $C^g (k)$ puede ser negativa, es decir, la energía se vende a la red eléctrica convencional, lo que representa una ganancia para el sistema de microrred.

Para escribir el funcional de costo en una forma más compacta, introducimos, para cada instante $k$, la variable auxiliar $\sigma_i(k)$ que contabiliza la aproximación de los costos de generación de la $i$-ésima unidad DG, y el vector $\mathbf{z}(k)$ que recopila todas las variables auxiliares de la siguiente manera:

$$\mathbf{z}(k) = \left[\pmb {\sigma}^{\prime}(k)C^{g}(k)\mathbf{S}\mathbf{U}^{\prime}(k)\mathbf{S}\mathbf{D}^{\prime}(k)z^{b}(k)\right]^{\prime}\in \mathbb{R}^{3N_{g} + 2}$$

donde $\pmb {\sigma}(k),\mathbf{SU}(k)$ y $\mathbf{SD}(k)$ son vectores columna que contienen, respectivamente, todos los $\sigma_i(k)$, los costos de arranque y parada de los generadores. Además, denotamos por $\mathbf{u}_k^{T - 1}$ la secuencia de entrada $\mathbf{u}_k^{T - 1} = (\mathbf{u}(k),\ldots ,\mathbf{u}(k + T - 1))$ diseñada en el instante $k$, donde $\mathbf{u}(k)$ se ha introducido en (8).

Entonces, el funcional de costo puede reescribirse como

$$\sum_{k = 0}^{T - 1}[\mathbf{c}_{\mathbf{u}}^{\prime}(k)\mathbf{u}(k) - \mathbf{OM}^{b}\mathbf{F}^{\prime}(k)\mathbf{u}(k) - \mathbf{OM}^{b}\mathbf{f}^{\prime}\mathbf{w}(k) + \mathbf{c}_{\mathbf{z}}^{\prime}\mathbf{z}(k)]$$

donde el término $- \mathrm{OM}^b \mathbf{F}(k) \mathbf{u}(k) - \mathrm{OM}^b \mathbf{f}' \mathbf{w}(k)$ se deriva del término $- \mathrm{OM}^b P^b (k)$ en (15), con $P^b (k)$ dado por (8); los vectores columna $\mathbf{c}_z$ y $\mathbf{c}_u$ se proporcionan en el Apéndice A.

### 3.C. Restricciones de Capacidad y Terminales

Para plantear el problema de optimización MILP final, deben cumplirse restricciones operativas adicionales

$$ \begin{array}{c}{x_{\min}^b\leq x^b (k)\leq x_{\max}^b}\\ {P_i,\min \delta_i(k)\leq P_i(k)\leq P_i,\max \delta_i(k)}\\ {|P_i(k + 1) - P_i(k)|\leq R_i,\max \delta_i(k)}\\ {\beta_{h,\min}\leq \beta_h(k)\leq \beta_{h,\max}} \end{array} \quad (16b)$$

con $i = 1,\ldots ,N_g$ y $h = 1,\ldots ,N_c$. Las restricciones anteriores modelan los límites físicos en el dispositivo de almacenamiento (16a), los límites de flujo de potencia de las unidades DG (16b) y sus tasas de rampa ascendente y descendente (16c), los límites en los recortes de cargas controlables (16d).

Nótese que la variable binaria $\delta_i(k)$ será igual a 1 si la potencia $P_i(k)$ generada por la $i$-ésima unidad DG en el instante $k$ es estrictamente positiva e igual a 0 si $P_i(k) = 0$. Cuando $P_{i,\min} = 0$, se puede evitar una asignación incorrecta de la variable $\delta_{i}(k)$ en la desigualdad (16b) asignando a $P_{i,\min}$ un valor positivo muy pequeño.

### 3.D. Problema de Control Predictivo por Modelos

En esta sección, formulamos el problema de optimización MPC cuya solución produce una trayectoria de entradas y estados hacia el futuro que satisfacen la dinámica y las restricciones de las operaciones de la microrred mientras optimizan algún criterio dado. En términos de control de microrredes, esto significa que, en el instante actual, se formula un plan óptimo (generalmente para las $24\mathrm{h}$) basado en predicciones de la demanda próxima, la producción de unidades de energía renovable y los precios de la energía. Solo se implementa la primera muestra de la secuencia de entrada y, posteriormente, se desplaza el horizonte. En el siguiente instante de muestreo, se mide o estima el nuevo estado del sistema, y se resuelve un nuevo problema de optimización utilizando esta nueva información. Mediante este enfoque de horizonte móvil, el nuevo plan óptimo puede potencialmente compensar cualquier perturbación que haya actuado mientras tanto sobre el sistema. Para presentar la política MPC, denotamos por $x^{b}(k + j|k)$, con $j > 0$, el estado en el paso de tiempo $k + j$ predicho en el instante $k$ empleando el modelo de almacenamiento (9).

En cada instante $k$, dado un estado inicial de almacenamiento $x_{k}^{b}$ y una duración de tiempo $T$, el esquema MPC calcula la secuencia de control óptima $\mathbf{u}_{k}^{T - 1}$ resolviendo el siguiente problema de control óptimo de horizonte finito:

$$ \begin{array}{rl} & {J(x_k^b) = \underset {\mathbf{u}_k^T - 1}{\min}\sum_{j = 0}^{T-1}[\mathbf{c}_{\mathbf{u}}'(k + j)\mathbf{u}(k + j) + \mathbf{c}_z'\mathbf{z}(k + j)}\\ & {\qquad -\mathbf{OM}^b\mathbf{F}'(k + j)\mathbf{u}(k + j) - \mathbf{OM}^b\mathbf{f}'\mathbf{w}(k + j)]} \end{array} \quad (17)$$

sujeto a

$$ \begin{array}{rl} & {\text{modelo de almacenamiento (9) en la variable }x^b (\cdot |k);}\\ & {\text{restricciones (10), (11), (13);}}\\ & {\text{restricciones (16);}}\\ & {S_i\cdot P_i(k + j) + s_i\leq \sigma_i(k + j);\ i = 1\ldots N_g}\\ & {x^b (k|k) = x^b (k)} \end{array} \quad (17)$$

donde $S_{i}$ y $s_{i}$ están definidos en (14). Recordamos que se supone que el vector de perfiles de perturbaciones, $\mathbf{w}(k + j)$, es conocido en el horizonte de predicción, para $j = 0,\ldots ,T - 1$; por lo tanto, el término $\mathbf{OM}^b\mathbf{f}'\mathbf{w}(k + j)$ en la función objetivo no afecta la solución óptima.

De acuerdo con la estrategia de horizonte móvil, solo se aplica el primer elemento de la secuencia óptima $\mathbf{u}(k)$. El problema de optimización (17) se repite en el instante $k + 1$, con el nuevo estado medido/estimado $x_{k + 1|k + 1}^{b} = x_{k + 1}^{b}$. Al hacerlo, se diseña una política con retroalimentación.

Nótese que en el esquema MPC aplicado en este artículo, el controlador toma su decisión de control asumiendo que las predicciones son correctas (es decir, equivalencia de certeza).

### 3.E. Condiciones Iniciales

En cada instante $k$, el modelo del sistema se inicializa con el estado actual medido/estimado de los componentes de la microrred, es decir, el nivel de energía actual del almacenamiento, las cargas, el estado ENCENDIDO/APAGADO y los niveles de potencia generados por las unidades de generación no controlables.

### 3.F. Resolución del Problema de Optimización

El problema de optimización MPC es un problema MILP. Las técnicas de ramificación y acotamiento (branch-and-bound) se aplican mayoritariamente a problemas MILP [41], [42]. La principal ventaja del método de ramificación y acotamiento es que si se alcanza una solución, se sabe que la solución es globalmente óptima.

### 3.G. Detalles de Implementación

La formulación presentada en la Sección III-F se implementó utilizando MATLAB. Utilizamos ILOG CPLEX 12.0 [43] (un solver eficiente basado en el algoritmo de ramificación y acotamiento) para resolver las optimizaciones MILP. Todos los cálculos se realizan en un Intel Core 2 Duo CPU, 2 GHz.

## IV. CONFIGURACIÓN DE LA SIMULACIÓN

La microrred que consideramos en las simulaciones se muestra en la Fig. 1; está en modo conectado a la red y comprende paneles PV con una potencia máxima de $16\mathrm{kW}$ y cuatro unidades DG. Se incluye un almacenamiento de energía, limitado entre 25 y $250\mathrm{kWh}$ y con tasas máximas de carga y descarga, respectivamente, de 150 y $-150\mathrm{kW}$. Las eficiencias de carga y descarga son ambas iguales a 0.9. La Tabla IV describe los parámetros de las unidades DG, basados en datos proporcionados en [38] y [44]. La microrred está conectada a la red eléctrica convencional, por lo que se puede comprar o vender energía. Los precios spot diarios (de la EEX, Bolsa Europea de Energía, en un día determinado) se muestran en la Fig. 2. Para el estudio de simulación, elegimos un tiempo de muestreo de $1\mathrm{h}$ y un horizonte de predicción de $24\mathrm{h}$. Las simulaciones se realizan durante un día.

<center>Fig. 1. Esquema de la microrred considerada en las simulaciones.</center>

<center>Fig. 2. Precios spot de la energía.</center>

**Tabla IV** PARÁMETROS DEL GENERADOR

| Unidad DG | Pmin | Pmax | a1 | a2 | a3 |
|-----------|------|------|----|----|----|
| Unidad 1 | 0 | 6 | 0.005 | 0.062 | 1.34 |
| Unidad 2 | 0 | 16.49 | 0.0020 | 0.057 | 1.14 |
| Unidad 3 | 0 | 16 | 0.0004 | 0.06 | 1.14 |
| Unidad 4 | 0 | 12.37 | 0.0006 | 0.058 | 1.9 |

### 4.A. Comparación de Estrategias de Control

Comparamos las siguientes estrategias para el problema de optimización de microrredes.

1) **Heurística:** Es el algoritmo heurístico descrito a continuación en la Sección IV-A1.
2) **MILP:** Es la solución en lazo abierto obtenida resolviendo un único problema MILP.
3) **MPC-MILP:** Es la ley de control con retroalimentación calculada a través del esquema de control MPC. Como se dijo antes, en MPC-MILP se aplica un enfoque de equivalencia de certeza, lo que significa que se asume que las predicciones son perfectas en el problema MPC, es decir, no afectadas por errores. La incertidumbre se compensa entonces mediante el mecanismo de retroalimentación.
4) **Referencia (Benchmark):** El plan de horizonte de 24 h obtenido resolviendo el problema de optimización asumiendo que no hay errores en los pronósticos, lo que significa que el planificador conoce todos los valores reales de cargas y generación de RES durante todo el horizonte de predicción. La referencia nunca puede alcanzarse, pero proporciona un valor ideal para evaluar una estrategia.

Cuando se aplican las estrategias MILP y MPC-MILP, también incluimos en la evaluación de la estrategia el costo de comprar la cantidad necesaria de energía de la red eléctrica convencional en caso de que haya un excedente de demanda debido a predicciones erróneas de la carga y la generación de energía de RES. Consideramos además los planes de horizonte de 24 h obtenidos cuando se emplea un almacenamiento de 250 kWh.

#### 1) Algoritmo Heurístico:
Teníamos en mente comparar el enfoque propuesto con un algoritmo heurístico de gestión de microrredes pero, según nuestro conocimiento, no se ha propuesto ninguno en la literatura hasta ahora, ni tenemos conocimiento de enfoques prácticos para el problema, más allá del simple equilibrio de las potencias suministradas y demandadas, que no tenga en cuenta el lado económico del problema. Por lo tanto, proponemos uno aquí.

Por simplicidad, asumimos que no hay costos de mantenimiento, arranque y parada. Además, no se utiliza ninguna unidad de almacenamiento, de modo que no es necesario tener en cuenta la dinámica. Las cargas son todas críticas. Al hacerlo, las posibles combinaciones de entradas de potencia pueden ser manejadas más fácilmente (también por un operador humano); es decir, el operador de la microrred puede decidir sobre la generación de la unidad DG y la interacción con la red eléctrica convencional. Además de eso, se asume que los tiempos mínimos de encendido y apagado son iguales a 1 tiempo de muestreo. Se consideran las restricciones de capacidad, aunque asumimos que el contrato bilateral entre la microrred y la red eléctrica convencional asegurará que el balance de energía sea siempre alcanzable, lo que significa que al operador de la microrred siempre se le permitirá comprar o vender a la red eléctrica convencional la cantidad necesaria de energía. Finalmente, asumimos que una unidad DG encendida siempre generará la potencia máxima disponible.

<center>Fig. 3. Generación de potencia PV pronosticada y real durante 24 h.</center>

<center>Fig. 4. Demanda pronosticada y real durante 24 h.</center>

El algoritmo heurístico consta de tres pasos, aplicados en cada instante de muestreo; estos pasos se ilustran en el Apéndice B.

### 4.B. Pronósticos

Para aplicar la estrategia de control descrita en la Sección III, deben calcularse los pronósticos de potencia renovable y demanda. Las series de datos de potencia renovable y demanda generalmente exhiben fluctuaciones de alta frecuencia y desplazamientos de picos, también influenciados por factores meteorológicos, como la temperatura exterior y la irradiancia. Por lo tanto, es una tarea relativamente difícil capturar la dinámica de estas series y ajustar un modelo a partir del conjunto de datos dado. Las metodologías ampliamente explotadas para el pronóstico no lineal son las redes neuronales (NN) [45] y las máquinas de vectores de soporte (SVM). Estas últimas son un método estadístico potente que tiene como objetivo capturar la estructura subyacente en un conjunto de datos basado en datos de entrenamiento de entrada [46], [47]; recientemente, la técnica SVM se está aplicando con éxito al pronóstico de la demanda y para predecir la generación renovable [48], [49].

En este artículo, aplicamos SVM de mínimos cuadrados para regresión (regresión de vectores de soporte) con una ventana de tiempo móvil para pronosticar la generación de potencia renovable y la demanda para el día siguiente. Véase el Apéndice C para un esbozo del algoritmo y más detalles sobre el pronóstico en simulaciones y experimentos.

En las Figs. 3 y 4 se muestran, respectivamente, ejemplos de perfiles de producción de energía renovable y de demanda diaria empleados en la rutina de optimización.

## V. RESULTADOS DE LA SIMULACIÓN

Las Figs. 5 y 6 muestran, respectivamente, la potencia intercambiada con la red eléctrica convencional y la generación de potencia de las unidades DG obtenidas al aplicar las diferentes estrategias sin almacenamiento. Se muestra que el MPC-MILP conduce a una utilización más eficiente de las unidades DG y se vende una mayor cantidad de energía a la red eléctrica convencional.

<center>Fig. 5. Generación de potencia de las unidades DG durante 24 h. (a) Heurística. (b) MPC-MILP.</center>

<center>Fig. 6. Energía comprada/vendida durante 24 h. (a) Heurística. (b) MPC-MILP.</center>

**Tabla V** COMPARACIÓN DE ESTRATEGIAS DE OPTIMIZACIÓN DE OPERACIONES DE MICRORREDES SIN ALMACENAMIENTO

| Estrategia             | Costo total (€) | Costos de corrección (€) |
|------------------------|-----------------|--------------------------|
| Heurística             | 452.80          | -                        |
| MPC-MILP               | 418.95          | 9.5                      |
| Referencia (Benchmark) | 416.70          | -                        |

La Tabla V reporta el rendimiento de las estrategias descritas para la optimización de operaciones de microrredes sin utilización de almacenamiento. Muestra que el incremento de costo con respecto a la referencia es del $8.6\%$ para el algoritmo heurístico y solo del $0.5\%$ para el algoritmo propuesto.

Considérese ahora la posibilidad de emplear la unidad de almacenamiento de 250 kWh. La Fig. 7 muestra la utilización del almacenamiento durante el horizonte de planificación. La Tabla VI muestra que el almacenamiento hace que la microrred sea más eficiente económicamente. También se reporta que el MILP sin acción de retroalimentación produce resultados deficientes, debido a las incertidumbres en la demanda y en la generación de potencia PV. La Fig. 8 muestra que la estrategia MPC-MILP produce menos violaciones de las restricciones de capacidad del almacenamiento en comparación con MILP; la figura también muestra que la estrategia MPC-MILP produce en ambos casos una solución cercana a la referencia. Como el nivel de almacenamiento no puede ser inferior a la capacidad mínima de almacenamiento, la acción de corrección es comprar de la red eléctrica convencional la cantidad de energía necesaria para llevar el nivel de almacenamiento a su valor de capacidad mínima.

<center>Fig. 7. Energía almacenada durante $24\mathrm{h}$.</center>

**Tabla VI** COMPARACIÓN DE ESTRATEGIAS DE OPTIMIZACIÓN DE OPERACIONES DE MICRORREDES CON ALMACENAMIENTO

| Estrategia | Costo total (€) | Costos de corrección (€) |
|------------|-----------------|--------------------------|
| MPC-MILP con almacenamiento | 403.34 | 9.8 |
| MILP con almacenamiento | 788.34 | 435.8 |
| Referencia (Benchmark) con almacenamiento | 391.50 | - |

<center>Fig. 8. Uso del almacenamiento bajo diferentes estrategias (los valores negativos significan que el almacenamiento prestaría energía, lo cual no es posible en el caso real).</center>

### 5.A. Complejidad Computacional

Es bien sabido que los problemas MILP son NP-completos y su complejidad computacional depende principalmente del número de variables enteras [39], [50]. Investigamos la carga computacional de los problemas de optimización MILP a resolver en línea, con el fin de evaluar la viabilidad del enfoque propuesto. Consideramos el caso de estudio reportado anteriormente, utilizando diferentes horizontes de predicción $T$. En cada instante de tiempo, se resuelve un problema MILP. La Tabla VII reporta los tiempos de cómputo (promedio y peor caso) necesarios para resolver los MILP, así como los tamaños del problema a medida que crece el horizonte de predicción. Los tiempos de cómputo aumentan a medida que el horizonte de predicción $T$ se alarga. Sin embargo, la solución al problema de optimización tomó como máximo $24.3\mathrm{s}$, un tiempo mucho más corto que el tiempo de muestreo de $1\mathrm{h}$. Un horizonte de predicción más largo normalmente no proporcionaría una mejora porque los pronósticos se degradan a medida que aumenta el tiempo, pero la Tabla VII muestra que la carga computacional puede ser asumible. Esto también puede significar que el tiempo de muestreo podría reducirse a costa de un aumento despreciable del esfuerzo computacional. En realidad, los experimentos se realizaron con un período de muestreo de 15 minutos.

**Tabla VII** TIEMPOS DE CÓMPUTO

| Horizonte | N° variables de decisión | N° restricciones | Tiempos promedio [s] | Tiempos de peor caso [s] |
|-----------|--------------------------|------------------|----------------------|--------------------------|
| 24        | 576                      | 3561             | 3.3 | 6.0 |
| 36        | 864 | 5397 | 5.5 | 7.4 |
| 48        | 1152 | 7232 | 9.1 | 12.2 |
| 60        | 1440 | 9070 | 12.6 | 19.3 |
| 72        | 1728 | 10907 | 17.7 | 24.3 |

## VI. RESULTADOS EXPERIMENTALES

La validación experimental del algoritmo de control se realizó en el Centro de Energías Renovables y Ahorro (CRES), Pikermi-Atenas, Grecia. Consideramos un período de muestreo de 15 minutos y los experimentos se realizaron durante $6\mathrm{h}$. La instalación utilizada para este propósito es la microrred experimental del CRES que comprende las siguientes unidades (Fig. 9).

<center>Fig. 9. Configuración de la microrred experimental.</center>

1) **RES:** Dos unidades PV con potencia máxima de 1.1 y $2.5\mathrm{kW}$.
2) **Unidades DG:** Una celda de combustible de membrana de intercambio de protones de $5\mathrm{kW}$ y un almacenamiento de batería utilizado para simular la operación de una unidad CHP. La potencia máxima del CHP se seleccionó en $2\mathrm{kW}$. Los costos operativos y de mantenimiento de la celda de combustible son de $0.16\mathrm{€}$ por período de muestreo (15 min). Los costos operativos y de mantenimiento del CHP son de $0.01\mathrm{€}$ por kW generado.
3) **Unidad de almacenamiento:** Un sistema de batería con capacidad máxima de $40\mathrm{-kW}$ y potencia máxima de $2.5\mathrm{-kW}$. Las eficiencias de carga y descarga son ambas iguales a 0.8. Asumimos que la batería nunca se descarga por debajo del $75\%$ de su capacidad máxima. Los costos operativos y de mantenimiento de la batería son de $0.0784\mathrm{€}$ por $\mathrm{kWh}$ intercambiado sin costos asociados de inversor.
4) **Cargas:** Se utilizó un banco de cargas resistivas. Específicamente, las cargas se dividieron en dos grupos (críticas y flexibles), cada una de las cuales se programó a través de una curva de carga específica con un tiempo de muestreo de 10 minutos. De acuerdo con los puntos de consigna de control, se recortó una cantidad de la carga controlable mientras que el consumo máximo de carga fue de aproximadamente $9\mathrm{kW}$.

Todas las unidades estaban interconectadas a través de la línea eléctrica trifásica de la microrred a la red pública.

Estaban disponibles controladores de bajo nivel para los componentes de la microrred.

1) Se empleó un integrador local para regular la frecuencia del inversor de la batería de acuerdo con el punto de consigna de potencia activa.
2) Se utilizó un integrador local para el inversor de la $\mu$-CHP.
3) La unidad de celda de combustible se reguló utilizando un integrador local y un comparador con el valor de referencia de potencia media.
4) En cuanto al banco de cargas, un controlador local seleccionó la combinación más apropiada de resistencias, que proporcionó el valor de consumo más cercano según el punto de consigna.

El algoritmo de control se implementó en una PC interfazada con el sistema SCADA de la microrred a través de la red de área local.

Todos los datos utilizados en los experimentos son realistas, basados en mediciones, hojas de datos y precios de mercado. Las cargas siguen un perfil realista derivado de mediciones de consumo reales en una microrred real. Los precios spot diarios se muestran en la Fig. 10.

<center>Fig. 10. Precios spot de la energía durante 24 pasos de tiempo (6 h) (todos los experimentos).</center>

Se presentan los resultados de tres experimentos.

1) **Experimento 1:** La microrred se opera sin control de alto nivel.
2) **Experimento 2:** Las operaciones de la microrred son gestionadas por el esquema de control MPC-MILP con un horizonte de planificación de 24 pasos.
3) **Experimento 3:** Las operaciones de la microrred son gestionadas por el esquema de control MPC-MILP con un horizonte de planificación de 72 pasos.

Los experimentos se realizan desde las 9:00 a.m. hasta las 3:00 p.m., por lo que las unidades PV generan algo de potencia en todos los pasos de tiempo (1 kW en promedio).

<center>Fig. 11. Uso de la batería durante 24 pasos de tiempo (6 h). (a) Experimento 1 (sin MPC). (b) Experimento 2 (MPC sobre 24 pasos de tiempo).</center>

<center>Fig. 12. Energía intercambiada con la red eléctrica convencional durante 24 pasos de tiempo (6 h). (a) Experimento 2 (MPC sobre 24 pasos de tiempo). (b) Experimento 3 (MPC sobre 72 pasos de tiempo).</center>

<center>Fig. 13. Energía intercambiada con la red eléctrica convencional durante 24 pasos de tiempo (6 h) para el Experimento 1 (sin MPC).</center>

<center>Fig. 14. Generación de potencia de la celda de combustible para el Experimento 1 (sin MPC).</center>

<center>Fig. 15. Recortes durante 24 pasos de tiempo (6 h).</center>

Durante los tres experimentos, el sistema se opera con los mismos perfiles de consumo. El propósito final del Experimento 1 es el balance de potencia entre producción y consumo. En otras palabras, el sistema operó para minimizar el flujo de potencia/energía hacia y desde la red pública. Este es el concepto fundamental de las microrredes ya que están diseñadas para explotar tanto como sea posible los beneficios de los DER [2].

La batería se emplea en gran medida en el Experimento 1; se utiliza mucho menos en el Experimento 2 y no se utiliza en absoluto en el Experimento 3 debido a sus altos costos de mantenimiento (Fig. 11). Se necesita comprar una menor cantidad de energía de la red eléctrica convencional durante el Experimento 1 en comparación con los experimentos realizados con el controlador de alto nivel (Figs. 12 y 13). Además, la celda de combustible se utiliza en el Experimento 1 (Fig. 14), mientras que siempre está APAGADA durante los experimentos con control de alto nivel debido a sus grandes costos operativos y de mantenimiento y su baja eficiencia en la generación de energía eléctrica. Es probable que se utilice en caso de que la demanda térmica y las emisiones se incluyeran en la formulación del problema.

La unidad CHP siempre funciona a su máxima potencia en estos experimentos.

El costo total para el Experimento 1 es de $27.4\mathrm{€}$, para el Experimento 2 es de $19.6\mathrm{€}$ y para el Experimento 3 es de $17.9\mathrm{€}$. Entonces, la estrategia MPC-MILP produce un ahorro del $28.5\%$ con $T = 24$ y un ahorro del $34.7\%$ con un horizonte de predicción más largo, $T = 72$.

Los recortes generalmente se penalizan ya que conducen a incomodidad del usuario; por lo tanto, no se realizan a menos que sean estrictamente convenientes o necesarios. Por lo tanto, todos los experimentos realizados con una penalización por recorte $\rho_{c}$ igual a 0.5 no muestran recorte. Realizamos otro experimento durante 24 pasos reduciendo $\rho_{c}$ a 0.1 en la última hora y la Fig. 15 muestra cómo el algoritmo de optimización utiliza esta relajación. El ahorro económico con respecto al experimento con $\rho_{c} = 0.5$ no es significativo porque la generación de potencia PV durante este experimento fue mucho menor, por lo que se necesitó comprar una mayor cantidad de energía de la red eléctrica convencional. Se puede lograr un compromiso entre el costo y la reducción de picos de demanda y la comodidad del usuario ajustando el parámetro $\rho_{c}$.

Vale la pena mencionar que bajo algunas circunstancias los valores de potencia reales se desviaron de los puntos de consigna debido a las siguientes razones.

1) El inversor de almacenamiento de batería presentó una reducción de potencia cuando se sobrecalentó. Esto llevó a una reducción de potencia. Como resultado, la microrred cubrió el déficit absorbiendo potencia de la red pública.
2) El segundo sistema de batería, que se utilizó para simular la unidad CHP, presentó en momentos específicos una tasa de descarga profunda debido al mal estado de salud de la batería. Debido a esto, fue necesario revertir manualmente la potencia durante pequeños intervalos de 15 minutos. Esto, aunque no se contabilizó como absorción de energía, se consideró como intervalos de producción cero, lo que llevó a una desviación de los puntos de consigna. El uso de una mejor batería puede resolver este problema.
3) En algunos experimentos, las condiciones climáticas llevaron a una reducción de la potencia de los PV y, por lo tanto, a una desviación de la potencia predicha.

## VII. CONCLUSIÓN

En este paper, proponemos un novedoso enfoque lineal entero mixto para el modelado y optimización de microrredes. Consideramos el compromiso de unidades, el despacho económico, el almacenamiento de energía, la venta y compra de energía a/de la red principal, y el programa de recorte. Primero, asumimos un conocimiento perfecto del estado de la microrred, la producción de recursos renovables, las cargas futuras, etc., lo cual es útil para resolver el problema de optimización. Además, para hacer frente a perturbaciones inevitables y errores de pronóstico, incorporamos esto en un marco MPC. El enfoque propuesto fue investigado en una microrred experimental ubicada en Atenas, Grecia. Los resultados experimentales muestran que nuestro esquema de control MPC-MILP es capaz de optimizar económicamente las operaciones de la microrred y ahorrar dinero en comparación con la práctica actual. Los resultados también evidencian que se puede lograr un compromiso entre la reducción de picos de demanda y la comodidad del usuario a través de recortes permitidos.

El trabajo futuro se centrará en relajar nuestras suposiciones para incluir la estimación del estado y el modelado de incertidumbre. Finalmente, las capacidades de recuperación de calor y la potencia reactiva no se consideran en el modelado de la microrred y la formulación del problema para limitar su complejidad. Somos conscientes de su importancia y su incorporación en el marco de control propuesto está bajo estudio actual.

## APÉNDICE A

**MATRICES**

$$ \begin{array}{rl} & {\mathbf{E}_1^b = \left[C^b -(C^b +\epsilon)C^b C^b -C^b -C^b\right]}\\ & {\mathbf{E}_2^b = [0 0 1 - 1 1 - 1]}\\ & {\mathbf{E}_3^b = [1 - 1 1 - 1 0 0]}\\ & {\mathbf{E}_4^b = \left[C^b -\epsilon C^b C^b 0 0\right]}\\ & {\mathbf{E}_1^G = \left[T^s -(T^s +\epsilon)M^s M^s -M^s -M^s\right]}\\ & {\mathbf{E}_3^G (k) = \left[1 - 1 c^P (k) - c^P (k) c^S (k) - c^S (k)\right]}\\ & {\mathbf{E}_4^G = \left[T^s -\epsilon M^s M^s 0 0\right]} \end{array} $$

donde $M^s = \max_k(c^P (k), c^S (k)) \cdot T^s$, $\epsilon$ es una pequeña tolerancia (típicamente la precisión de la máquina)

$$ \begin{array}{rl} & {\mathbf{F}^\prime (k) = [\underbrace{1\dots 1}_{N_g} 1 \underbrace{\dots D_1^c(k)\dots}_{N_c} 0\dots 0]}\\ & {\mathbf{f}^\prime = [1 \underbrace{- 1\dots - 1}_{N_l} \underbrace{- 1\dots - 1}_{N_c}]}\\ & {\mathbf{c}_z^\prime = [\underbrace{1\dots 1}_{N_g} 1 \underbrace{1\dots 1}_{2\cdot N_g} 2\cdot \mathbf{OM}^b]}\\ & {\mathbf{c}_\mathbf{u}(k)^\prime = [\underbrace{0\dots 0}_{N_g} 1 \underbrace{\dots \rho_i(k)D_i^c(k)\dots}_{N_c} \underbrace{\dots OM_i\dots}_{N_g}]}. \end{array} \quad (1)$$

## APÉNDICE B

**PASOS DEL ALGORITMO HEURÍSTICO**

El algoritmo heurístico consta de los siguientes pasos.

1) Se calcula la diferencia entre la potencia generada por todas las unidades de RES y la carga real. La potencia generada a partir de las fuentes de energía renovable se utiliza siempre para satisfacer la demanda. Si la diferencia es positiva, el excedente de potencia se vende a la red eléctrica convencional, el paso de tiempo se incrementa en uno y el algoritmo vuelve al paso 1; de lo contrario, procede al paso 2.
2) Si el costo de comprar el déficit de demanda de la red eléctrica convencional es menor que el costo mínimo entre los costos de generación de las unidades DG, el déficit se cubrirá comprando la cantidad correspondiente de energía de la red eléctrica convencional, el paso de tiempo se incrementa en uno y el algoritmo vuelve al paso 1; de lo contrario, procede al paso 3.
3) Las unidades DG se encienden desde la más barata hasta la más cara hasta que se cubra el excedente de demanda. Dado que las unidades DG funcionan a su máxima capacidad de potencia, es probable que haya un excedente de potencia una vez que se cumpla la demanda total; entonces, la energía correspondiente se vende a la red eléctrica convencional; el paso de tiempo se incrementa en uno y el algoritmo vuelve al paso 1.

## APÉNDICE C

**FUNDAMENTOS**

En esta sección, presentamos brevemente algunos conceptos básicos empleados en el diseño de la estrategia de control.

### A. Programación Lineal Entera Mixta

En un sistema de microrred, interactúan dinámicas de valor continuo y discreto. Las cantidades físicas, como los flujos de energía y potencia, pueden representarse mediante variables continuas, mientras que las características discretas de los componentes de la microrred (por ejemplo, el estado ON/OFF de los DGs, el estado de carga/descarga del almacenamiento y las restricciones de tiempo mínimo de encendido y apagado) pueden capturarse utilizando variables de decisión binarias. Además, el comportamiento de un sistema de microrred y sus componentes puede describirse mediante ecuaciones diferenciales o en diferencias (por ejemplo, dinámica del almacenamiento) y declaraciones lógicas, es decir, declaraciones de la forma if...then...else. Dado que estamos interesados en el control predictivo por modelos, necesitamos construir un modelo de predicción del sistema. En [36], se muestra cómo convertir una declaración lógica de una forma dada en restricciones lineales enteras mixtas, es decir, restricciones que involucran tanto variables continuas como discretas. A continuación, proporcionaremos algunos ejemplos, tomados de [36], de equivalencias entre declaraciones lógicas y restricciones lineales enteras mixtas; la declaración

$$f(k)\geq 0\Longleftrightarrow \delta = 1$$

$$ \text{es verdadera si y solo si} \left\{ \begin{array}{ll} -m\delta & \leq f(k) - m\\ -(M + \epsilon)\delta \leq - f(k) - \epsilon \end{array} \right. \quad (18)$$

de manera similar

$$ y = \delta f(k) \text{es equivalente a }\left\{ \begin{array}{l} y \leq M\delta \\ y \geq m\delta \\ y \leq f(k) - m(1 - \delta) \\ y \geq f(k) - M(1 - \delta) \end{array} \right. \quad (19)$$

donde $f$ es una función acotada superior e inferiormente por $M$ y $m$ respectivamente, $\delta$ es una variable binaria, $y$ es una variable real, y $\epsilon$ es una pequeña tolerancia (típicamente la precisión de la máquina). La tolerancia $\epsilon$ es necesaria para transformar una restricción de la forma $y < 0$ en $y \leq 0$, ya que los algoritmos de resolución de MILP solo manejan desigualdades no estrictas.

### B. Algoritmo de Entrenamiento de SVR

El algoritmo de entrenamiento de una SVR implica un programa de optimización cuadrática, que proporciona una solución única y no requiere la inicialización aleatoria de pesos, como en el entrenamiento de NN. El conjunto de datos de entrenamiento se define de la siguiente manera:

$$\{x_{i},y_{i}\} ,i = 1,\ldots ,N$$

donde $N$ es el número de muestras, $x_{i},y_{i}$ son patrones de entrada de valor real y salidas correspondientes, respectivamente. El algoritmo de entrenamiento SVR tiene como objetivo encontrar un mapeo no lineal $\phi (x)$ de los datos de entrada $x$ y luego resolver un problema de regresión lineal en este espacio de características. La función que representa la relación entre la salida y la entrada es

$$y_{i} = \sum_{i = 1}^{N}w_{i}\phi (x_{i}) + b_{i} \quad (20)$$

donde para cada muestra $i$, $b_{i}$ es el umbral escalar y $w_{i}$ es el coeficiente de peso. Luego, los parámetros $w_{i}$ y $b_{i}$ se estiman resolviendo el siguiente problema de regresión convexa en este espacio de características:

$$\min_{w,b,\xi ,\xi^{*}}0.5w^{T}w + C\sum_{i = 1}^{N}(\xi +\xi^{*})$$

s.a.

$$ \begin{array}{l} y_{i} - w^{T}\phi (x_{i}) - b_{i}\leq \epsilon +\xi^{*} \\ w^{T}\phi (x_{i}) + b_{i} - y_{i}\leq \epsilon +\xi \\ \xi ,\xi^{*}\geq 0,\qquad i = 1\ldots N \end{array} $$

donde el parámetro $C$ es el parámetro de regularización, que asigna penalización a los errores y determina un compromiso entre la planitud de la función de regresión y el error de entrenamiento, $\xi$ y $\xi^{*}$ son las variables de holgura de los límites superior e inferior del vector de entrenamiento, y $\epsilon$ es la tolerancia residual.

Todos los pronósticos se obtienen mediante la caja de herramientas SVM de MATLAB, un entorno de entrenamiento y simulación LS-SVM escrito en código C [51]. Los patrones se actualizan añadiendo el valor real más reciente y se elimina el valor más antiguo, y se calculan los pronósticos para los siguientes $T$ períodos de muestreo.

## REFERENCIAS

[1] R. Lasseter and P. Piagi, "Microgrid: A conceptual solution," in *Proc. IEEE Annu. Power Electron Specialists Conf.*, Jun. 2004, pp. 4285-4290.

[2] N. Hatziargyriou, H. Asano, R. Iravani, and C. Marnay, "Microgrids," *IEEE Power Energy Mag.*, vol. 5, no. 4, pp. 78-94, Jul./Aug. 2007.

[3] T. Ustun, C. Ozansoy, and A. Zayegh, "Recent developments in microgrids and example cases around the world: a review," *Renew. Sustain. Energy Rev.*, vol. 15, no. 8, pp. 4030-4041, 2011.

[4] (2008). *Strategic Deployment Document for Europe's Electricity Networks of the Future* [Online]. Available: http://www.smartgrids.eu/

[5] J. Ilic, M. Prica, S. Rabiei, J. Goellner, D. Wilson, C. Shih, et al., "Technical and economic analysis of various power generation resources coupled with CAES systems," *Nat. Energy Technol. Lab.*, Morgantown, WV, USA, Tech. Rep. DOE/NETL-2011/1472, Jun. 2011.

[6] M. Hoffman, M. Kintner-Meyer, A. Sadovsky, and J. DeSteese, "Analysis tools for sizing and placement of energy storage for grid applications—A literature review," *Pacific Northwest Nat. Lab.* (DOE/PNNL-19703), Richland, WA, USA, Tech. Rep., Sep. 2010.

[7] Y. Chen, S. Lu, Y. Chang, T. Lee, and M. Huc, "Economic analysis and optimal energy management models for microgrid systems: A case study in Taiwan," *Appl. Energy*, vol. 103, pp. 145-154, Mar. 2013.

[8] M. Marzband, A. Sumpter, J. Dominguez-Garcia, and R. Gumara-Ferret, "Experimental validation of a real time energy management system for microgrids in islanded mode using a local day-ahead electricity market and MINLP," *Energy Convers. Manag.*, vol. 76, pp. 314-322, Dec. 2013.

[9] Z. Dinghuan, R. Yang, and G. Hug-Glanzmann, "Managing microgrids with intermittent resources: A two-layer multi-step optimal control approach," in *Proc. NAPS*, Sep./Oct. 2010, pp. 1-8.

[10] R. O'Neill, T. Dautel, and E. Krall, "Recent ISO software enhancements and future software and modeling plans," *Staff Report, Federal Energy Regulatory Commission*, Washington, DC, USA, Tech. Rep., Nov. 2011.

[11] R. Sioshansi, R. O'Neill, and S. Oren, "Economic consequences of alternative solution methods for centralized unit commitment in day-ahead electricity markets," *IEEE Trans. Power Syst.*, vol. 23, no. 2, pp. 344-352, May 2008.

[12] G.-C. Liao, "Solve environmental economic dispatch of smart microgrid containing distributed generation system—Using chaotic quantum genetic algorithm," *Electr. Power Energy Syst.*, vol. 43, no. 1, pp. 779-787, 2012.

[13] A. Takeuchi, T. Hayashi, Y. Nozaki, and T. Shimakage, "Optimal scheduling using metaheuristics for energy networks," *IEEE Trans. Smart Grid*, vol. 3, no. 2, pp. 968-974, Jun. 2012.

[14] R. Firestone and C. Mamay, "Energy manager design for microgrids," *Lawrence Berkeley Nat. Lab.*, Berkeley, CA, USA, LBNL Rep. LBNL-54447, 2005.

[15] A. Siddiqui, C. Mamay, O. Bailey, and K. LaCommare, "Optimal selection of on-site power generation with combined heat and power applications," *Int. J. Distrib. Energy Resour.*, vol. 1, no. 1, pp. 33-62, 2005.

[16] G. Pepermans, J. Driesen, D. Haeseldonckx, R. Belmans, and W. D'haeseleer, "Distributed generation: Definition, benefits and issues," *Energy Policy*, vol. 33, no. 6, pp. 787-798, 2005.

[17] A. Siddiqui, C. Mamay, R. Firestone, and N. Zhou, "Distributed generation with heat recovery and storage," *J. Energy Eng.*, vol. 133, no. 3, pp. 181-210, 2007.

[18] F. Mohamed, "Microgrid modelling and online management," Ph.D. dissertation, Faculty of Electronics, Communications and Automation, Helsinki Univ. Technol., Espoo, Finland, 2008.

[19] C. Chen, S. Duan, T. Cai, B. Liu, and G. Hu, "Smart energy management system for optimal micro grid economic operation," *IET Renew. Power Generat.*, vol. 5, no. 3, pp. 258-267, 2011.

[20] P. Stluka, D. Godbole, and T. Samad, "Energy management for buildings and microgrids," in *Proc. IEEE Conf. Decision Control*, Orlando, FL, USA, Dec. 2011, pp. 5150-5157.

[21] B. Otomega, A. Marinakis, M. Glavic, and T. V. Cutsem, "Model predictive control to alleviate thermal overloads," *IEEE Trans. Power Syst.*, vol. 22, no. 3, pp. 1384-1385, Aug. 2007.

[22] P. Meibom, R. Barth, B. Hasche, H. Brand, C. Weber, and M. O'Malley, "Stochastic optimization model to study the operational impacts of high wind penetrations in Ireland," *IEEE Trans. Power Syst.*, vol. 26, no. 3, pp. 1367-1379, Aug. 2011.

[23] M. Falahi, K. Butler-Purry, and M. Ehsani, "Dynamic reactive power control of islanded microgrids," *IEEE Trans. Power Syst.*, vol. 28, no. 4, pp. 3649-3657, Nov. 2013.

[24] G. Ferrari-Trecate, E. Gallestey, P. Letizia, M. Spedicato, M. Morari, and M. Antoine, "Modeling and control of co-generation power plants: A hybrid system approach," *IEEE Trans. Control Syst. Technol.*, vol. 12, no. 5, pp. 694-705, Sep. 2004.

[25] L. Xie and M. Ilic, "Model predictive economic/environmental dispatch of power systems with intermittent resources," in *Proc. IEEE Power Energy Soc. General Meeting*, Jul. 2009, pp. 1-6.

[26] R. Negenborn, M. Houwing, J. D. Schutter, and J. Hellendoorn, "Model predictive control for residential energy resources using a mixed-logical dynamic model," in *Proc. IEEE ICNSC*, Okayama, Japan, Mar. 2009, pp. 702-707.

[27] P. Kriett and M. Salani, "Optimal control of a residential microgrid," *Energy*, vol. 42, no. 1, pp. 321-330, 2012.

[28] A. Hooshmand, H. Malki, and J. Mohammadpour, "Power flow management of microgrid networks using model predictive control," *Comput. Math. Appl.*, vol. 64, no. 5, pp. 869-876, 2012.

[29] X. Xia, J. Zhang, and A. Elaiw, "A model predictive control approach to dynamic economic dispatch problem," in *Proc. IEEE Bucharest Power Tech Conf.*, Bucharest, Romania, Jun./Jul. 2009, pp. 1-7.

[30] W. Qi, J. Liu, X. Chen, and P. Christofides, "Supervisory predictive control of standalone wind/solar energy generation systems," *IEEE Trans. Control Syst. Technol.*, vol. 19, no. 1, pp. 199-207, Jan. 2011.

[31] W. Qi, J. Liu, X. Chen, and P. Christofides, "Supervisory predictive control for long-term scheduling of an integrated wind/solar energy generation and water desalination system," *IEEE Trans. Control Syst. Technol.*, vol. 20, no. 2, pp. 504-512, Mar. 2012.

[32] R. Palma-Behnke, C. Benavides, F. Lanas, B. Severino, L. Reyes, J. Llanos, et al., "A microgrid energy management system based on the rolling horizon strategy," *IEEE Trans. Smart Grid*, vol. 4, no. 2, pp. 996-1006, Jun. 2013.

[33] A. Bidram and A. Davoudi, "Hierarchical structure of microgrids control system," *IEEE Trans. Smart Grid*, vol. 3, no. 4, pp. 1963-1976, Dec. 2012.

[34] J. Maciejowski, *Predictive Control with Constraints*. Harlow, U.K.: Prentice-Hall, 2002.

[35] D. Mayne, "Constrained optimal control," in *Proc. Eur. Control Conf.*, Plenary Lecture, Porto, Portugal, Sep. 2001.

[36] A. Bemporad and M. Morari, "Control of systems integrating logic, dynamics, and constraints," *Automatica*, vol. 35, no. 3, pp. 407-427, 1999.

[37] A. Parisio and L. Glielmo, "Energy efficient microgrid management using model predictive control," in *Proc. 50th IEEE Conf. Decision Control*, Orlando, FL, USA, Dec. 2011, pp. 5449-5454.

[38] M. Carrión and J. Arroyo, "A computationally efficient mixed-integer linear formulation for the thermal unit commitment problem," *IEEE Trans. Power Syst.*, vol. 21, no. 3, pp. 1371-1378, Aug. 2006.

[39] A. Richard and J. How, "Mixed-integer programming for control," in *Proc. Amer. Control Conf.*, vol. 4. Portland, OR, USA, Jun. 2005, pp. 2676-2683.

[40] A. Bemporad, "Tutorial on model predictive control of hybrid systems," in *Proc. Adv. Process Control Appl. Ind. Workshop*, Vancouver, BC, Canada, 2007.

[41] D. Bertsimas and J. Tsitsiklis, *Introduction to Linear Optimization*. Belmont MA, USA: Athena Scientific, 1997.

[42] C. Floudas, *Nonlinear and Mixed-Integer Programming-Fundamentals and Applications*. Oxford, U.K.: Oxford Univ. Press, 1995.

[43] *CPLEX 12.0 Users Manual*, ILOG, Sunnyvale, CA, USA, 2012.

[44] "DC2: Evaluation of the microgrid central controller strategies. Microgrids-large scale integration of micro-generation to low voltage grids," Tech. Rep. ENK5-CT-2002-00610, 2004.

[45] Y. Yafeng, L. Yue, G. Junjun, and T. Chongli, "A new fuzzy neural networks model for demand forecasting," in *Proc. IEEE Int. Conf. ICAL*, Sep. 2008, pp. 372-376.

[46] C. Cortes, "Support-vector networks," *Mach. Learn.*, vol. 20, no. 3, pp. 273-297, 1995.

[47] E. Osuna, R. Freund, and F. Girosi, "Support vector machines: Training and applications," *Comput. Sci. Artif. Intell. Lab (CSAIL)*, Massachusetts Institute of Technology, Cambridge, MA, USA, Tech. Rep. AIM-1602, Mar. 1997.

[48] L. Yue, Y. Yafeng, G. Junjun, and T. Chongli, "Demand forecasting by using support vector machine," in *Proc. 3rd Int. Conf. Natural Comput.*, vol. 3. Aug. 2007, pp. 272-276.

[49] N. Sharma, P. Sharma, D. Irwin, and P. Shenoy, "Predicting solar generation from weather forecasts using machine learning," in *Proc. 2nd IEEE Int. Conf. Smart Grid Commun.*, Brussels, Belgium, Oct. 2011, pp. 528-533.

[50] G. Nemhauser and L. Wolsey, *Integer and Combinatorial Optimization*. New York, NY, USA: Wiley, 1988.

[51] K. Pelckmans, J. Suykens, T. V. Gestel, J. D. Brabanter, L. Lukas, B. Hamers, et al., "LS-SVMlab: A MATLAB/C toolbox for least squares support vector machines," Tech. Rep., 1998.
