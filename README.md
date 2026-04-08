# Energy Management System para Microredes usando Programación Lineal Mixta Entera (MILP)

Trabajo Final - Optimización Matemática y Aplicaciones en Programación de la Producción  
**UTN Facultad Regional Santa Fe** – 2° Cuatrimestre 2025

**Docente:** Ing. Pablo A. Marchetti  
**Alumno:** Marcos [tu apellido]

---

## Descripción del Proyecto

Este proyecto desarrolla un Energy Management System (EMS) para una microred eléctrica mediante un modelo de optimización MILP (Mixed-Integer Linear Programming).

El objetivo principal es minimizar el costo operativo de la microred mientras se satisfacen las restricciones técnicas, de demanda y de generación de energías renovables. El modelo decide cuándo encender/apagar generadores (Unit Commitment), cuánto generar con cada unidad, el uso de baterías de almacenamiento y posibles intercambios con la red eléctrica.

### Versiones del modelo
- `unit-commitment.ipynb` → Versión inicial básica
- `UC_v1.ipynb` a `UC_v6.ipynb` → Versiones iterativas con mejoras progresivas (restricciones adicionales, mayor detalle, etc.)

---

## Herramientas utilizadas

- **Lenguaje:** Python
- **Optimización:** PuLP (o el solver que estés usando: CBC, Gurobi, etc.)
- **Visualización y análisis:** Pandas, Matplotlib, Jupyter Notebook
- **Entorno:** Jupyter Notebooks

---

## Referencias

