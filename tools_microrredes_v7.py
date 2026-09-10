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
        # NUEVO: desagregado por generador/periodo, para graficos de composicion
        # de costo y costo marginal diesel (ver plot_cost_breakdown()).
        'sigma_vals': {g: [pe.value(m.sigma[g, t]) for t in T] for g in GENERATORS},
        'num_startup_vals': {g: [int(round(pe.value(m.num_startup[g, t]))) for t in T] for g in GENERATORS},
        'num_shutdown_vals': {g: [int(round(pe.value(m.num_shutdown[g, t]))) for t in T] for g in GENERATORS},
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
    plt.close(fig)


def plot_cost_breakdown(scenarios, GENERATORS, cost_per_hour, startup_cost, shutdown_cost,
                         price_buy, price_sell, filename):
    """
    Para cada escenario (r, titulo) en `scenarios`, grafica una fila con:
      - Costo marginal horario del diesel [$/kWh] vs. precios de compra/venta
        de la red, sombreando las horas en que se importa.
      - Composicion del costo operativo total (O&M fijo, combustible,
        arranque, apagado, red compra/venta), como barras horizontales.

    Version V7.1 del grafico de composicion de costos de UC_v6.ipynb
    (celda 'Composicion_costo_total'), generalizado a N escenarios (p.ej.
    los extremos min-costo / min-emisiones del frente epsilon-constraint)
    y usando los campos ya calculados por extract_common_results() en vez
    de recalcular todo desde el modelo pyomo resuelto.

    `r` debe tener, ademas de los campos usuales: 'pbuy_vals', 'psell_vals',
    'num_active_vals', 'sigma_vals', 'num_startup_vals', 'num_shutdown_vals',
    'diesel_vals' y 'c_op' (costo operativo total, usado como denominador
    de los porcentajes).
    """
    n = len(scenarios)
    fig, axes = plt.subplots(n, 2, figsize=(14, 4.2 * n), squeeze=False)
    hours = list(range(len(scenarios[0][0]['diesel_vals'])))

    for row, (r, title) in enumerate(scenarios):
        cost_om_h    = [sum(cost_per_hour[g] * r['num_active_vals'][g][t] for g in GENERATORS) for t in hours]
        cost_fuel_h  = [sum(r['sigma_vals'][g][t] for g in GENERATORS) for t in hours]
        cost_start_h = [sum(startup_cost[g] * r['num_startup_vals'][g][t] for g in GENERATORS) for t in hours]
        cost_stop_h  = [sum(shutdown_cost[g] * r['num_shutdown_vals'][g][t] for g in GENERATORS) for t in hours]
        hourly_diesel_cost = [cost_om_h[t] + cost_fuel_h[t] + cost_start_h[t] + cost_stop_h[t] for t in hours]
        diesel_total = r['diesel_vals']
        costo_marginal = [hourly_diesel_cost[t] / diesel_total[t] if diesel_total[t] > 1 else None for t in hours]

        # ── Costo marginal horario vs. precios de red ────────────────────
        ax1 = axes[row][0]
        valid_h = [h for h in hours if costo_marginal[h] is not None]
        valid_c = [costo_marginal[h] for h in valid_h]
        ax1.plot(valid_h, valid_c, 'steelblue', lw=2, marker='o', ms=4, label='C.marginal diesel ($/kWh)')
        ax1.step(hours, [price_buy[t] for t in hours], where='post', color='#e74c3c', lw=1.5, label='price_buy')
        ax1.step(hours, [price_sell[t] for t in hours], where='post', color='#2ecc71', lw=1.5, ls='--', label='price_sell')
        for t in hours:
            if r['pbuy_vals'][t] > 0.1:
                ax1.axvspan(t, t + 1, alpha=0.12, color='#9b59b6')
        ax1.set_xlabel('Hora'); ax1.set_ylabel('$/kWh')
        ax1.set_title(f'Costo Marginal Diesel vs. Precios de Red — {title}\n(sombreado = horas con importacion)')
        ax1.set_xticks(range(0, 24, 3)); ax1.set_xticklabels([f'{h:02d}' for h in range(0, 24, 3)])
        ax1.legend(loc='center', bbox_to_anchor=(0.2, 0.6), fontsize=8)
        ax1.grid(alpha=0.3)

        # ── Composicion del costo total ───────────────────────────────────
        c_om_total    = sum(cost_om_h)
        c_fuel_total  = sum(cost_fuel_h)
        c_start_total = sum(cost_start_h)
        c_stop_total  = sum(cost_stop_h)
        total_cost_buy  = sum(price_buy[t] * r['pbuy_vals'][t] for t in hours)
        total_rev_sell  = sum(price_sell[t] * r['psell_vals'][t] for t in hours)
        costo_total = r['c_op']

        ax2 = axes[row][1]
        cost_components = {'O&M fijo': c_om_total, 'Combustible': c_fuel_total,
                            'Arranque': c_start_total, 'Apagado': c_stop_total,
                            'Red compra': total_cost_buy, 'Red venta': -total_rev_sell}
        colors_bar = ['#3498db', '#e67e22', '#2ecc71', '#e74c3c', '#9b59b6', '#1abc9c']
        labels_c = list(cost_components.keys())
        values_c = list(cost_components.values())
        bars = ax2.barh(labels_c, values_c, color=colors_bar, edgecolor='white', height=0.5)
        for bar, val in zip(bars, values_c):
            pct = 100 * val / costo_total
            x_lbl = bar.get_width() + costo_total * 0.01 if val >= 0 else bar.get_width() - costo_total * 0.01
            ha = 'left' if val >= 0 else 'right'
            ax2.text(x_lbl, bar.get_y() + bar.get_height() / 2,
                     f'${val:,.0f} ({pct:.1f}%)', ha=ha, va='center', fontsize=8)
        ax2.axvline(0, color='black', lw=0.8)
        ax2.set_xlabel('Costo [$]')
        ax2.set_title(f'Composicion del Costo Total — {title}\n${costo_total:,.2f}')
        ax2.invert_yaxis(); ax2.grid(alpha=0.3, axis='x')
        ax2.spines[['top', 'right']].set_visible(False)

    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.show()
    plt.close(fig)


def plot_emissions_stacked(scenarios, GENERATORS, BETA_DIESEL, BETA_GRID, filename):
    """
    Para cada escenario (r, titulo) en `scenarios`, grafica una fila con un
    barras apiladas por hora: emisiones de la microrred (diesel, abajo) +
    emisiones de la red por la energia importada (arriba), en kg de CO2.
    Compara visualmente cuanto de la huella horaria total viene de generar
    localmente vs. de comprarle a la red (cuyo factor de emision `BETA_GRID`
    varia con la hora, ver celda de parametros de emisiones).
    """
    n = len(scenarios)
    fig, axes = plt.subplots(n, 1, figsize=(14, 4 * n), sharex=True, squeeze=False)
    hours = list(range(len(scenarios[0][0]['diesel_vals'])))

    for row, (r, title) in enumerate(scenarios):
        diesel_em = [sum(BETA_DIESEL[g] * r['output_vals'][g][t] for g in GENERATORS) for t in hours]
        grid_em   = [BETA_GRID[t] * r['pbuy_vals'][t] for t in hours]

        ax = axes[row][0]
        ax.bar(hours, diesel_em, color='#3498db', label='Microrred (diesel)',
               width=0.8, edgecolor='white', lw=0.4)
        ax.bar(hours, grid_em, bottom=diesel_em, color='#e74c3c', label='Red (importacion)',
               width=0.8, edgecolor='white', lw=0.4)
        ax.set_ylabel('CO2 [kg]')
        ax.set_title(f'{title}  —  Total: {sum(diesel_em) + sum(grid_em):.0f} kg CO2')
        ax.legend(fontsize=8, loc='upper right')
        ax.grid(alpha=0.3, axis='y')

    axes[-1][0].set_xlabel('Hora')
    axes[-1][0].set_xticks(range(0, 24, 3))
    axes[-1][0].set_xticklabels([f'{h:02d}' for h in range(0, 24, 3)])
    fig.suptitle('Emisiones CO2 horarias: Microrred (diesel) vs. Red de servicio (importacion)',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.show()
    plt.close(fig)
