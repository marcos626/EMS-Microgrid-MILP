# Energy Management System para Microredes usando Programación Lineal Mixta Entera (MILP)

Optimización Matemática y Aplicaciones en Programación de la Producción
**UTN Facultad Regional Santa Fe** – 2° Cuatrimestre 2025
Trabajo Final

**Docente:** Ing. Pablo A. Marchetti  
**Alumno:** Marcos Santillán

---

## Descripción del Proyecto

Este proyecto desarrolla un Energy Management System (EMS) para una microred eléctrica mediante un modelo de optimización MILP (Mixed-Integer Linear Programming).

El objetivo principal es minimizar el costo operativo de la microred mientras se satisfacen las restricciones técnicas, de demanda y de generación de energías renovables. El modelo decide cuándo encender/apagar generadores (Unit Commitment), cuánto generar con cada unidad (Despacho Económico), y transacciones con la red eléctrica.

### Versiones del modelo
- `unit-commitment.ipynb` → Versión original [https://gurobipy-pandas.readthedocs.io/en/stable/examples/unit-commitment.html](https://gurobipy-pandas.readthedocs.io/en/stable/examples/unit-commitment.html) y en el Ejemplo 12.15 del libro [Model Building in Mathematical Programming](https://share.google/ovWcmGq54LiyOcWm8) de H. Paul Williams (5ª edición, págs. 270-271 y 325-326).
- `UC_v1.ipynb` → Versión en PYOMO basado en el modelo de Williams
- `UC_v2.ipynb` → Redimensionamiento a escala de microrred. Se reeplazaron los generadores térmicos por generadores diesel.
- `UC_v3.ipynb` → Se pasa de una representación agregada de la demanda en 5 bloques horarios a una discretización horaria completa (24 períodos), lo cual permite capturar con mayor fidelidad las rampas de demanda, especialmente en los períodos de transición (mañana y tarde).
- `UC_v4.ipynb` → Se agregan restricciones de rampa (ramp-up y ramp-down) para limitar la tasa de cambio de producción entre períodos consecutivos. Las restricciones se formulan de manera trivialmente satisfecha (ramp_limit = Pmax) dado que los generadores diesel tienen una dinámica de carga mucho más rápida que el paso de tiempo de 1 hora.
- `UC_v5.ipynb` → Se incorpora un generador fotovoltaico (GFV). Los datos de irradiancia y temperatura corresponden al parque solar de la UTN FR Santa Fe, día 01/01/2019 (promedios horarios).
- `UC_v6.ipynb` → Conexión a la red de servicio (grid-tied operation). La microrred puede importar energía del mercado (`p_buy[t]`) o exportar excedentes (`p_sell[t]`). Se agrega una variable binaria `is_buying[t]` para garantizar que importación y exportación sean mutuamente excluyentes en cada período. Los precios horarios de compra/venta se basan en el perfil dinámico de Nemati et al. (BDEW, mercado alemán), escalado a $/kWh.

---

## Herramientas utilizadas

- **Lenguaje:** Python
- **Optimización:** PuLP (o el solver que estés usando: CBC, Gurobi, etc.)
- **Visualización y análisis:** Pandas, Matplotlib, Jupyter Notebook
- **Entorno:** Jupyter Notebooks

---

## Referencias

