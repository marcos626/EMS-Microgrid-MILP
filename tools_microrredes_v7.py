"""
uc_lib_v7.py
------------
Funciones compartidas del modelo UC de microrred (V7.1), extraidas de
UC_v7_1.ipynb para evitar duplicar la construccion del modelo entre
build_and_solve() (suma ponderada) y build_and_solve_epsilon()
(epsilon-constraint), que eran ~95% identicas.

Cambios V7.1 respecto a V7 (incorporados aca, no solo en el notebook):
  1. Cota superior explicita de sigma (costo de combustible linealizado).
  2. Big-M dinamico por periodo y sentido (compra/venta), en vez de un
     unico BIG_M = PCC_LIMIT global.
  3. Restriccion de reserva formulada sobre "headroom" real (capacidad
     activa menos produccion ya despachada), no sobre capacidad bruta
     comprometida. La version anterior subestimaba la reserva real en
     los periodos con exportacion (p_sell > 0): ver discusion en el
     notebook, celda markdown "V7.1".
"""
import time
import pyomo.environ as pe
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ──────────────────────────────────────────────────────────────────────────
# Preparacion de parametros derivados (Big-M dinamico, cota de sigma)
# ──────────────────────────────────────────────────────────────────────────

def compute_dynamic_big_m(expected_demand, pv_output, num_available, max_output,
                           pcc_limit, T):
    """
    Cotas Big-M ajustadas por periodo para las restricciones de exclusion
    mutua compra/venta (is_buying), en vez de un unico valor global.

    Cuando is_buying[t]=1 (comprando), p_sell[t]=0 y el balance de demanda
    implica p_buy[t] = D_t - PV_t - sum(output_diesel) <= D_t - PV_t
    (pues output_diesel >= 0). Cota ajustada: min(PCC_LIMIT, D_t - PV_t).

    Cuando is_buying[t]=0 (vendiendo), p_buy[t]=0 y el balance implica
    p_sell[t] = sum(output_diesel) + PV_t - D_t
              <= capacidad_diesel_total + PV_t - D_t.
    Cota ajustada: min(PCC_LIMIT, max(0, capacidad_diesel_total + PV_t - D_t)).

    Retorna dos dicts {t: valor}, indexados igual que T.
    """
    total_diesel_capacity = sum(num_available[g] * max_output[g] for g in max_output)
    big_m_buy, big_m_sell = {}, {}
    for t in T:
        big_m_buy[t]  = min(pcc_limit, max(expected_demand[t] - pv_output[t], 0.0))
        big_m_sell[t] = min(pcc_limit, max(total_diesel_capacity + pv_output[t] - expected_demand[t], 0.0))
    return big_m_buy, big_m_sell


def compute_sigma_upper_bound(generators, quad_params, max_output):
    """
    Cota superior de sigma[g,t]: el valor de la curva de costo CUADRATICA
    real evaluada en max_output[g] (el mayor valor de la envolvente de
    segmentos, ya que sigma aproxima por arriba una funcion convexa).

    No es estrictamente necesaria para la optimalidad (el objetivo minimiza
    sigma con signo positivo, y las restricciones ya lo empujan a su valor
    mas bajo factible), pero deja el modelo acotado explicitamente: mas
    robusto ante instancias mal escaladas o degeneradas.
    """
    return {g: quad_params[g]['a'] * max_output[g]**2 + quad_params[g]['b'] * max_output[g]
            for g in generators}


# ──────────────────────────────────────────────────────────────────────────
# Construccion del modelo (parte comun a suma ponderada y epsilon-constraint)
# ──────────────────────────────────────────────────────────────────────────

def build_base_model(data):
    """
    Construye la parte COMUN del modelo UC: conjuntos, parametros, variables
    y restricciones. No agrega funcion objetivo: eso lo define cada llamador
    (build_and_solve o build_and_solve_epsilon) segun el metodo biobjetivo.

    'data' es un dict con las estructuras ya calculadas en el notebook:
        GENERATORS, T, SEGMENTS,
        num_available, min_output, max_output, cost_per_hour,
        startup_cost, shutdown_cost, min_up_time, min_down_time,
        ramp_limit, state0, expected_demand, pv_output,
        price_buy, price_sell, PCC_LIMIT,
        big_m_buy, big_m_sell,      # dict {t: valor}, ver compute_dynamic_big_m
        reserve_margin,             # float, p.ej. 0.15
        lin_segments,               # dict {g: {'slopes':[...], 'intercepts':[...]}}
        sigma_cap                   # dict {g: valor}, ver compute_sigma_upper_bound

    Retorna el pe.ConcreteModel() ya construido (sin objetivo).
    """
    G, T, SEGMENTS = data['GENERATORS'], data['T'], data['SEGMENTS']

    m = pe.ConcreteModel()
    m.G = pe.Set(initialize=G, ordered=True)
    m.T = pe.Set(initialize=T, ordered=True)
    m.J = pe.Set(initialize=SEGMENTS)

    m.num_available = pe.Param(m.G, initialize=data['num_available'])
    m.min_output    = pe.Param(m.G, initialize=data['min_output'])
    m.max_output    = pe.Param(m.G, initialize=data['max_output'])
    m.cost_per_hour = pe.Param(m.G, initialize=data['cost_per_hour'])
    m.startup_cost  = pe.Param(m.G, initialize=data['startup_cost'])
    m.shutdown_cost = pe.Param(m.G, initialize=data['shutdown_cost'])
    m.min_up_time   = pe.Param(m.G, initialize=data['min_up_time'])
    m.min_down_time = pe.Param(m.G, initialize=data['min_down_time'])
    m.ramp_limit    = pe.Param(m.G, initialize=data['ramp_limit'])
    m.state0        = pe.Param(m.G, initialize=data['state0'])
    m.expected_demand = pe.Param(m.T, initialize=data['expected_demand'])
    m.pv_output     = pe.Param(m.T, initialize=data['pv_output'])
    m.price_buy     = pe.Param(m.T, initialize=data['price_buy'])
    m.price_sell    = pe.Param(m.T, initialize=data['price_sell'])
    m.pcc_limit     = pe.Param(initialize=data['PCC_LIMIT'])

    # NUEVO V7.1: Big-M dinamico por periodo y sentido (antes: un solo BIG_M)
    m.big_m_buy  = pe.Param(m.T, initialize=data['big_m_buy'])
    m.big_m_sell = pe.Param(m.T, initialize=data['big_m_sell'])

    # NUEVO V7.1: reserva formulada como headroom (antes: capacidad >= 1.15*D)
    m.reserve_margin = pe.Param(initialize=data['reserve_margin'])

    slope_data     = {(g, j): data['lin_segments'][g]['slopes'][j]     for g in G for j in SEGMENTS}
    intercept_data = {(g, j): data['lin_segments'][g]['intercepts'][j] for g in G for j in SEGMENTS}
    m.lin_slope     = pe.Param(m.G, m.J, initialize=slope_data)
    m.lin_intercept = pe.Param(m.G, m.J, initialize=intercept_data)

    # NUEVO V7.1: cota superior explicita de sigma (antes: sin cota)
    m.sigma_cap = pe.Param(m.G, initialize=data['sigma_cap'])

    # ── Variables ──────────────────────────────────────────────────────
    m.output = pe.Var(m.G, m.T, within=pe.NonNegativeReals)
    m.sigma  = pe.Var(m.G, m.T, within=pe.NonNegativeReals)

    def na_bounds(m2, g, t): return (0, m2.num_available[g])
    m.num_active   = pe.Var(m.G, m.T, within=pe.NonNegativeIntegers, bounds=na_bounds)
    m.num_startup  = pe.Var(m.G, m.T, within=pe.NonNegativeIntegers)
    m.num_shutdown = pe.Var(m.G, m.T, within=pe.NonNegativeIntegers)

    def pcc_b(m2, t): return (0, m2.pcc_limit)
    m.p_buy     = pe.Var(m.T, within=pe.NonNegativeReals, bounds=pcc_b)
    m.p_sell    = pe.Var(m.T, within=pe.NonNegativeReals, bounds=pcc_b)
    m.is_buying = pe.Var(m.T, within=pe.Binary)

    # ── Restricciones ──────────────────────────────────────────────────
    def demand_rule(m2, t):
        return (sum(m2.output[g, t] for g in m2.G) + m2.pv_output[t]
                + m2.p_buy[t] - m2.p_sell[t] == m2.expected_demand[t])
    m.demand_constraint = pe.Constraint(m.T, rule=demand_rule)

    # NUEVO V7.1: reserva por headroom, no por capacidad bruta comprometida.
    # La version anterior (sum(max_output*num_active) >= 1.15*D) no restaba
    # la produccion ya despachada, por lo que en periodos con exportacion
    # (p_sell > 0) el margen real de headroom podia caer por debajo del 15%
    # nominal sin que la restriccion lo detectara.
    def reserve_rule(m2, t):
        headroom = sum(m2.max_output[g] * m2.num_active[g, t] - m2.output[g, t] for g in m2.G)
        return headroom >= m2.reserve_margin * m2.expected_demand[t]
    m.reserve_constraint = pe.Constraint(m.T, rule=reserve_rule)

    def out_lo(m2, g, t): return m2.output[g, t] >= m2.min_output[g] * m2.num_active[g, t]
    def out_hi(m2, g, t): return m2.output[g, t] <= m2.max_output[g] * m2.num_active[g, t]
    m.output_lower = pe.Constraint(m.G, m.T, rule=out_lo)
    m.output_upper = pe.Constraint(m.G, m.T, rule=out_hi)

    def su_rule(m2, g, t):
        if t == m2.T.first(): return pe.Constraint.Skip
        return m2.num_startup[g, t] >= m2.num_active[g, t] - m2.num_active[g, m2.T.prev(t)]
    m.startup_constraint = pe.Constraint(m.G, m.T, rule=su_rule)

    def su0_rule(m2, g):
        return m2.num_startup[g, m2.T.first()] >= m2.num_active[g, m2.T.first()] - m2.state0[g]
    m.initial_startup = pe.Constraint(m.G, rule=su0_rule)

    def sd_rule(m2, g, t):
        if t == m2.T.first(): return pe.Constraint.Skip
        return m2.num_shutdown[g, t] >= m2.num_active[g, m2.T.prev(t)] - m2.num_active[g, t]
    m.shutdown_constraint = pe.Constraint(m.G, m.T, rule=sd_rule)

    def sd0_rule(m2, g):
        return m2.num_shutdown[g, m2.T.first()] >= m2.state0[g] - m2.num_active[g, m2.T.first()]
    m.initial_shutdown = pe.Constraint(m.G, rule=sd0_rule)

    def mut_rule(m2, g, t):
        mut = int(pe.value(m2.min_up_time[g]))
        if mut <= 1: return pe.Constraint.Skip
        tl = list(m2.T)
        if t < mut - 1: return pe.Constraint.Skip
        w = [tl[tau] for tau in range(t - mut + 1, t) if tau >= 0]
        return sum(m2.num_startup[g, tau] for tau in w) <= m2.num_active[g, tl[t]]
    m.min_up_time_constraint = pe.Constraint(m.G, m.T, rule=mut_rule)

    def mdt_rule(m2, g, t):
        mdt = int(pe.value(m2.min_down_time[g]))
        if mdt <= 1: return pe.Constraint.Skip
        tl = list(m2.T)
        if t < mdt - 1: return pe.Constraint.Skip
        w = [tl[tau] for tau in range(t - mdt + 1, t) if tau >= 0]
        return sum(m2.num_shutdown[g, tau] for tau in w) <= m2.num_available[g] - m2.num_active[g, tl[t]]
    m.min_down_time_constraint = pe.Constraint(m.G, m.T, rule=mdt_rule)

    def fuel_rule(m2, g, t, j):
        return m2.sigma[g, t] >= m2.lin_slope[g, j] * m2.output[g, t] + m2.lin_intercept[g, j] * m2.num_active[g, t]
    m.fuel_cost_linearization = pe.Constraint(m.G, m.T, m.J, rule=fuel_rule)

    # NUEVO V7.1: cota superior explicita de sigma
    def sigma_ub_rule(m2, g, t):
        return m2.sigma[g, t] <= m2.sigma_cap[g] * m2.num_active[g, t]
    m.sigma_upper = pe.Constraint(m.G, m.T, rule=sigma_ub_rule)

    def ru_rule(m2, g, t):
        if t == m2.T.first(): return pe.Constraint.Skip
        return (m2.output[g, t] - m2.output[g, m2.T.prev(t)]
                <= m2.ramp_limit[g] * m2.num_active[g, m2.T.prev(t)] + m2.max_output[g] * m2.num_startup[g, t])
    m.ramp_up_constraint = pe.Constraint(m.G, m.T, rule=ru_rule)

    def rd_rule(m2, g, t):
        if t == m2.T.first(): return pe.Constraint.Skip
        return (m2.output[g, m2.T.prev(t)] - m2.output[g, t]
                <= m2.ramp_limit[g] * m2.num_active[g, t] + m2.max_output[g] * m2.num_shutdown[g, t])
    m.ramp_down_constraint = pe.Constraint(m.G, m.T, rule=rd_rule)

    # NUEVO V7.1: Big-M dinamico por periodo (antes: m.big_m unico global)
    def nbs_buy(m2, t):  return m2.p_buy[t]  <= m2.big_m_buy[t]  * m2.is_buying[t]
    def nbs_sell(m2, t): return m2.p_sell[t] <= m2.big_m_sell[t] * (1 - m2.is_buying[t])
    m.no_buy_sell_buy  = pe.Constraint(m.T, rule=nbs_buy)
    m.no_buy_sell_sell = pe.Constraint(m.T, rule=nbs_sell)

    return m


def solve_model(m, solver_factory='appsi_highs', verbose=False):
    """Configura opciones del solver y resuelve. Retorna (resultado_pyomo, cpu_time)."""
    solver = pe.SolverFactory(solver_factory)
    if solver_factory in ['appsi_highs', 'highs']:
        solver.options['mip_rel_gap'] = 0.0
        solver.options['log_to_console'] = True if verbose else False
    else:
        solver.options['MIPGap'] = 0
        solver.options['MIPFocus'] = 1
        solver.options['OutputFlag'] = 1 if verbose else 0

    t0 = time.time()
    res = solver.solve(m, tee=verbose)
    cpu = time.time() - t0
    return res, cpu


def extract_common_results(m, GENERATORS, T, BETA_DIESEL, BETA_GRID, ALPHA_CO2):
    """
    Extrae del modelo resuelto los campos comunes a build_and_solve() y
    build_and_solve_epsilon(), evitando duplicar este bloque en ambas.
    """
    e_diesel_val = sum(pe.value(m.output[g, t]) for g in GENERATORS for t in T)
    e_buy_val    = sum(pe.value(m.p_buy[t]) for t in T)
    e_sell_val   = sum(pe.value(m.p_sell[t]) for t in T)

    em_diesel_kg = sum(BETA_DIESEL[g] * pe.value(m.output[g, t]) for g in GENERATORS for t in T)
    em_grid_kg   = sum(BETA_GRID[t] * pe.value(m.p_buy[t]) for t in T)
    em_total_kg  = em_diesel_kg + em_grid_kg
    c_em_cost = ALPHA_CO2 * em_total_kg

    return {
        'e_diesel': e_diesel_val,
        'e_buy': e_buy_val,
        'e_sell': e_sell_val,
        'c_em_cost': c_em_cost,
        'c_em_kg': em_total_kg,
        'c_em_diesel': em_diesel_kg,
        'c_em_grid': em_grid_kg,
        'pbuy_vals': [pe.value(m.p_buy[t]) for t in T],
        'psell_vals': [pe.value(m.p_sell[t]) for t in T],
        'diesel_vals': [sum(pe.value(m.output[g, t]) for g in GENERATORS) for t in T],
        'num_active_vals': {g: [int(round(pe.value(m.num_active[g, t]))) for t in T] for g in GENERATORS},
        'output_vals': {g: [pe.value(m.output[g, t]) for t in T] for g in GENERATORS},
    }


# ──────────────────────────────────────────────────────────────────────────
# Post-procesamiento / graficos (heatmaps de despacho)
# ──────────────────────────────────────────────────────────────────────────

def build_dispatch_matrices(r, GENERATORS):
    """Matrices [generador x hora] de unidades activas y potencia despachada."""
    hours_lbl = [f'{h:02d}:00' for h in range(len(r['diesel_vals']))]
    active_matrix = pd.DataFrame(
        index=GENERATORS, columns=hours_lbl,
        data=[r['num_active_vals'][g] for g in GENERATORS])
    output_matrix = pd.DataFrame(
        index=GENERATORS, columns=hours_lbl,
        data=[[round(v, 1) for v in r['output_vals'][g]] for g in GENERATORS])
    return active_matrix, output_matrix


def plot_dispatch_heatmap(r, GENERATORS, label, filename):
    """
    Grafica el par de heatmaps (unidades activas / produccion) para un
    resultado r, con titulo descriptivo `label` (p.ej. 'eps=... (min costo)')
    y lo guarda en `filename`. Reemplaza el codigo duplicado que antes
    vivia en las celdas heatmap-costo-v7 y heatmap-emisiones-v7.
    """
    active_matrix, output_matrix = build_dispatch_matrices(r, GENERATORS)

    fig, axes = plt.subplots(2, 1, figsize=(14, 6))
    sns.heatmap(active_matrix, annot=True, fmt='d', cmap='YlOrRd',
                linewidths=0.5, cbar_kws={'label': 'Unidades activas'}, ax=axes[0])
    axes[0].set_title(f'Unidades Activas por Clase y Periodo — {label}')
    sns.heatmap(output_matrix, annot=True, fmt='.0f', cmap='Blues',
                linewidths=0.5, cbar_kws={'label': 'Produccion [kW]'},
                annot_kws={'size': 9, 'rotation': 90}, ax=axes[1])
    axes[1].set_title('Produccion Total Diesel [kW] por Clase y Periodo')
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.show()
    return fig
