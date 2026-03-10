import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import os

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Electrical Calculator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .result-card {
        background: #f8f9fa;
        border-left: 4px solid #1a6fc4;
        border-radius: 4px;
        padding: 14px 18px;
        margin: 8px 0;
    }
    .result-card .label { font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: 0.08em; }
    .result-card .value { font-size: 1.8rem; font-weight: 700; color: #1a6fc4; }
    .result-card .value.danger { color: #d32f2f; }
    .result-card .value.ok    { color: #2e7d32; }

    .method-row {
        display: flex;
        align-items: center;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 10px 16px;
        margin: 5px 0;
        background: #fff;
    }
    .method-name    { color: #555; font-size: 14px; flex: 0 0 180px; }
    .method-section { color: #1a6fc4; font-size: 1.3rem; font-weight: 700; flex: 0 0 100px; text-align: right; }
    .method-cap     { color: #2e7d32; font-size: 13px; font-family: monospace; flex: 1; text-align: right; }
    .method-cap.warn   { color: #e65100; }
    .method-cap.danger { color: #d32f2f; }

    .hist-card {
        background: #f0f4ff;
        border: 1px solid #c5d5f5;
        border-radius: 4px;
        padding: 10px 14px;
        margin: 4px 0;
        font-size: 13px;
    }
    .hist-card .htime { color: #999; font-size: 11px; }
    .hist-card .hval  { font-weight: 700; color: #1a6fc4; }

    .compare-col {
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 14px;
        background: #fafafa;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# PASSWORD
# ─────────────────────────────────────────────────────────────
def check_password():
    if st.session_state.get("password_correct", False):
        return True
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        st.markdown("## ⚡ Elec Calc")
        pwd = st.text_input("Password", type="password")
        if st.button("Log in", use_container_width=True):
            if pwd == st.secrets.get("password", ""):
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Incorrect password")
    return False

if not check_password():
    st.stop()


# ─────────────────────────────────────────────────────────────
# DATA TABLES (DS 60364)
# Al conductors < 16 mm² stored as 0 (not permitted per standard)
# ─────────────────────────────────────────────────────────────
SECTIONS = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300]

def get_ds60364_data(insulation, loaded_cond, material="Cu"):
    """Return ampacity table for given insulation, number of loaded conductors and material."""

    # ── ALUMINIUM ──────────────────────────────────────────────
    if material == "Al":
        if insulation == "PVC":
            if loaded_cond == 2:
                return {
                    "Cable Tray (E)":        [0, 23, 31, 39, 54, 73, 89, 111, 135, 173, 210, 244, 282, 322, 380, 439],
                    "In Conduit (B2)":       [0, 17.5, 24, 30, 41, 54, 71, 86, 104, 131, 157, 181, 201, 230, 269, 308],
                    "Pipe in Ground (D1)":   [0, 22, 29, 36, 47, 61, 77,  93, 109, 135, 159, 180, 204, 228, 262, 296],
                    "Direct in Ground (D2)": [0, 0, 0, 0, 0, 63, 82, 98, 117, 145, 173, 200, 224, 255, 298, 336],
                }
            else:  # 3 loaded conductors
                return {
                    "Cable Tray (E)":        [0, 19.5, 26, 33, 46, 61, 78, 96, 117, 150, 183, 212, 245, 280, 330, 381],
                    "In Conduit (B2)":       [0, 15.5, 21, 27, 36, 48, 62, 77, 92, 116, 139, 160, 176, 199, 232, 265],
                    "Pipe in Ground (D1)":   [0, 18.5, 24, 30, 39, 50, 64, 77, 91, 112, 132, 150, 169, 190, 218, 247],
                    "Direct in Ground (D2)": [0, 0, 0, 0, 0, 53, 69, 83, 99, 122, 148, 169, 189, 214, 250, 282],
                }
        else:  # XLPE
            if loaded_cond == 2:
                return {
                    "Cable Tray (E)":        [0, 28, 38, 49, 67, 91, 108, 135, 164, 211, 257, 300, 346, 397, 470, 543],
                    "In Conduit (B2)":       [0, 23, 31, 40, 54, 72, 94, 115, 138, 175, 210, 242, 261, 300, 358, 415],
                    "Pipe in Ground (D1)":   [0, 26, 33, 42, 55, 71, 90, 108, 128, 158, 186, 211, 238, 267, 307, 346],
                    "Direct in Ground (D2)": [0, 0, 0, 0, 0, 76.0, 98, 117, 139, 170, 204, 223, 261, 296, 343, 386],
                }
            else:
                return {
                    "Cable Tray (E)":        [0, 24, 32, 42, 58, 77, 97, 120, 146, 187, 227, 263, 304, 347, 409, 471],
                    "In Conduit (B2)":       [0, 21, 28, 35, 48, 64, 84, 103, 124, 156, 188, 216, 240, 272, 318, 364],
                    "Pipe in Ground (D1)":   [0, 22, 28, 35, 46, 59, 75, 90, 106, 130, 154, 174, 197, 220, 253, 286],
                    "Direct in Ground (D2)": [0, 0, 0, 0, 0, 64, 82, 98, 117, 144, 172, 197, 220, 250, 290, 326],
                }

    # ── COPPER (default) ───────────────────────────────────────
    if insulation == "PVC":
        if loaded_cond == 2:
            return {
                "Cable Tray (E)":        [22, 30, 40, 51, 70, 94, 119, 148, 180, 232, 282, 328, 379, 434, 514, 593],
                "In Conduit (B2)":       [16.5, 23, 30, 38, 52,  69,  90, 111, 133, 168, 201, 232, 258, 294, 344, 394],
                "Pipe in Ground (D1)":   [22, 29, 37, 46, 60,  78,  99, 119, 140, 173, 204, 231, 261, 292, 336, 379],
                "Direct in Ground (D2)": [22, 28, 38, 48, 64,  83, 110, 132, 156, 192, 230, 261, 293, 331, 382, 427],
            }
        else:
            return {
                "Cable Tray (E)":        [18.5, 25, 34, 43, 60,  80, 101, 126, 153, 196, 238, 276, 319, 364, 430, 497],
                "In Conduit (B2)":       [15, 20, 27, 34, 46,  62,  80,  99, 118, 149, 179, 206, 225, 255, 297, 339],
                "Pipe in Ground (D1)":   [18, 24, 30, 38, 50,  64,  82,  98, 116, 143, 169, 192, 217, 243, 280, 316],
                "Direct in Ground (D2)": [19, 24, 33, 41, 54,  70,  92, 110, 130, 162, 193, 220, 246, 278, 320, 359],
            }
    else:  # XLPE
        if loaded_cond == 2:
            return {
                "Cable Tray (E)":        [26, 36, 49, 63, 86, 115, 149, 185, 225, 289, 352, 410, 473, 542, 641, 741],
                "In Conduit (B2)":       [22, 30, 40, 51, 69,  91, 119, 146, 175, 221, 265, 305, 334, 384, 459, 532],
                "Pipe in Ground (D1)":   [25, 33, 43, 53, 71,  91, 116, 139, 164, 203, 239, 271, 306, 343, 395, 446],
                "Direct in Ground (D2)": [27, 35, 46, 58, 77, 100, 129, 155, 183, 225, 270, 306, 343, 387, 448, 502],
            }
        else:
            return {
                "Cable Tray (E)":        [23, 32, 42, 54, 75, 100, 127, 158, 192, 246, 298, 346, 399, 456, 538, 621],
                "In Conduit (B2)":       [19.5, 26, 35, 44, 60,  80, 105, 128, 154, 194, 233, 268, 300, 340, 398, 455],
                "Pipe in Ground (D1)":   [21, 28, 36, 44, 58,  75,  96, 115, 135, 167, 197, 223, 251, 281, 324, 365],
                "Direct in Ground (D2)": [23, 30, 39, 49, 65,  84, 107, 129, 153, 188, 226, 257, 287, 324, 375, 419],
            }


# ─────────────────────────────────────────────────────────────
# HISTORY HELPERS
# ─────────────────────────────────────────────────────────────
def init_history():
    if "calc_history" not in st.session_state:
        st.session_state.calc_history = []

def add_to_history(module_name, params, results):
    import datetime
    init_history()
    entry = {
        "module": module_name,
        "params": params,
        "results": results,
        "time": datetime.datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.calc_history.insert(0, entry)
    st.session_state.calc_history = st.session_state.calc_history[:10]

def show_history(module_name):
    init_history()
    entries = [e for e in st.session_state.calc_history if e["module"] == module_name]
    if not entries:
        return
    with st.expander(f"🕘 History — last {len(entries)} calculation(s)", expanded=False):
        for e in entries:
            params_str  = "  ·  ".join(f"{k}: **{v}**" for k, v in e["params"].items())
            results_str = "  ·  ".join(f"{k}: **{v}**" for k, v in e["results"].items())
            st.markdown(f"""
            <div class="hist-card">
                <span class="htime">{e['time']}</span><br>
                <span style="color:#555">{params_str}</span><br>
                <span class="hval">{results_str}</span>
            </div>""", unsafe_allow_html=True)
        if st.button("Clear history", key=f"clr_{module_name}"):
            st.session_state.calc_history = [
                e for e in st.session_state.calc_history if e["module"] != module_name
            ]
            st.rerun()


# ─────────────────────────────────────────────────────────────
# TOOLTIPS
# ─────────────────────────────────────────────────────────────
TT = {
    "u_pri":          "Rated primary voltage of the transformer (HV side), in kV.",
    "i_k_pri":        "Short-circuit current at the primary busbar. Type 'inf' if the upstream network is very stiff.",
    "s_r":            "Rated apparent power of the transformer in kVA. Found on the nameplate.",
    "u_n":            "Nominal secondary (LV) voltage. Typically 400 V for European 3-phase systems.",
    "u_k":            "Short-circuit impedance voltage in %. Typically 4–6% for distribution transformers. "
                      "Found on the nameplate. Higher u_k → lower fault current.",
    "ib":             "Design load current the cable must carry continuously.",
    "temp":           "Ambient temperature around the cable. Higher temp → lower cable capacity (derating).",
    "k2":             "Grouping / bunching derating factor. 1.0 = single cable or well-separated. "
                      "Decreases when cables are bundled (see DS 60364-5-52 Table B.52.3).",
    "n_par":          "Number of cables in parallel per phase. Each cable carries Ib / n.",
    "v_neu":          "Apply K3 = 0.86 when the neutral carries significant harmonic current "
                      "(e.g. many non-linear loads). Required by DS 60364-5-52.",
    "cos_phi":        "Power factor of the load. Purely resistive = 1.0. Induction motors ≈ 0.75–0.90. Use 0.85 if unknown.",
    "e_len":          "One-way cable length in metres.",
    "e_sect":         "Cross-sectional area of one conductor in mm².",
    "xlpe_vs_pvc":    "XLPE allows 90°C operating temperature vs 70°C for PVC → 15–25% higher capacity for the same section.",
    "cu_vs_al":       "Copper has lower resistivity than aluminium. Al needs ~1.5× larger section for the same capacity. "
                      "Al is lighter and cheaper for large sections (≥ 35 mm²). "
                      "Al conductors < 16 mm² are not permitted per DS 60364.",
    "install_method": "Installation method strongly affects Iz:\n"
                      "• Cable Tray (E): best airflow → highest Iz\n"
                      "• In Conduit (B2): heat trapped → lower Iz\n"
                      "• In Ground (D1/D2): depends on soil thermal resistivity",
}

def tip(key):
    return TT.get(key, "")


# ─────────────────────────────────────────────────────────────
# CHART HELPER
# ─────────────────────────────────────────────────────────────
def make_fig(w=5, h=2.2):
    fig, ax = plt.subplots(figsize=(w, h), dpi=220)
    ax.grid(True, linestyle='--', alpha=0.4, color='#cccccc')
    ax.tick_params(labelsize=7)
    return fig, ax


# ─────────────────────────────────────────────────────────────
# CABLE SIZING CALCULATION  (shared between single + compare)
# ─────────────────────────────────────────────────────────────
def calc_cable_sizing(ib, temp, k2, n, v_mat, v_ins, v_cond, v_neu):
    if v_ins == "XLPE":
        k1_table = [(30,1.0),(35,0.96),(40,0.91),(45,0.87),(50,0.82),
                    (55,0.76),(60,0.71),(65,0.65),(70,0.58),(999,0.50)]
    else:
        k1_table = [(30,1.0),(35,0.94),(40,0.87),(45,0.79),(50,0.71),
                    (55,0.61),(60,0.50),(999,0.40)]
    k1 = next(v for t_lim, v in k1_table if temp <= t_lim)
    k3 = 0.86 if v_neu else 1.0
    k_total = k1 * k2 * k3
    target  = ib / (k_total * n)
    load_per_cable = ib / n
    methods = get_ds60364_data(v_ins, v_cond, v_mat)   # pass material directly
    rows = []
    for m, vals in methods.items():
        # For Al, skip sections where val == 0 (< 16 mm²)
        idx = next((i for i, v in enumerate(vals) if v > 0 and v >= target), -1)
        if idx != -1:
            sect   = SECTIONS[idx]
            actual = vals[idx] * k_total
            pct    = (load_per_cable / actual) * 100
            rows.append({"method": m, "sect": sect, "actual": actual, "pct": pct, "ok": True})
        else:
            rows.append({"method": m, "sect": None, "actual": None, "pct": None, "ok": False})
    return k1, k3, k_total, target, rows


def render_sizing_rows(rows):
    for r in rows:
        if r["ok"]:
            cls = "danger" if r["pct"] > 100 else ("warn" if r["pct"] > 85 else "")
            st.markdown(f"""
            <div class="method-row">
                <span class="method-name">{r['method']}</span>
                <span class="method-section">{r['sect']} mm²</span>
                <span class="method-cap {cls}">{r['actual']:.1f} A  ({r['pct']:.0f}%)</span>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="method-row">
                <span class="method-name">{r['method']}</span>
                <span class="method-section" style="color:#d32f2f">N/A</span>
                <span class="method-cap danger">&gt; 300 mm²</span>
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)

st.sidebar.markdown("## ⚡ Elec Calc")
st.sidebar.caption("DS 60364 — Engineering Tools")

module = st.sidebar.radio("", [
    "1. Short Circuit",
    "2. Cable Sizing",
    "3. Voltage Drop",
    "4. Cable Capacity",
    "5. Parallel Cable Load",
    "6. Converter",
    "7. Battery / UPS"
])

st.sidebar.markdown("---")
st.sidebar.caption("Built & maintained by Ionut Vieru")


# ═════════════════════════════════════════════════════════════
# MODULE 1 — SHORT CIRCUIT
# ═════════════════════════════════════════════════════════════
if module == "1. Short Circuit":
    st.markdown("# ⚡ Short Circuit — Transformer")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        u_pri   = st.number_input("U_pri [kV]",         value=10.0,   step=0.5,   help=tip("u_pri"))
        i_k_pri = st.text_input( "I_k upstream [kA]",   value="inf",              help=tip("i_k_pri"))
        s_r     = st.number_input("S_r [kVA]",          value=1600.0, step=100.0, help=tip("s_r"))
    with col2:
        u_n = st.number_input("U_n [V]", value=400.0, step=10.0, help=tip("u_n"))
        u_k = st.number_input("u_k [%]", value=6.0,   step=0.5,  help=tip("u_k"))

    if st.button("CALCULATE & PLOT", type="primary"):
        try:
            IrT   = (s_r * 1000) / (np.sqrt(3) * u_n)
            Ikp_s = i_k_pri.strip().lower()
            ZQ    = 0.0 if Ikp_s in ["inf","infinity","∞"] else \
                    (1.05 * u_n**2) / (np.sqrt(3) * u_pri * 1000 * float(Ikp_s) * 1000)
            ZT    = (u_k / 100) * (u_n**2 / (s_r * 1000))
            RT    = 0.1 * ZT
            XT    = np.sqrt(max(ZT**2 - RT**2, 0))
            Ikmax = (1.05 * u_n) / (np.sqrt(3) * (ZQ + ZT))
            kappa = 1.02 + 0.98 * np.exp(-3 * (RT / XT)) if XT > 0 else 2.0
            ipeak = kappa * np.sqrt(2) * Ikmax

            m1, m2, m3 = st.columns(3)
            m1.metric("Nominal Current IrT", f"{IrT:.1f} A")
            m2.metric("I_k_max''",           f"{Ikmax/1000:.2f} kA")
            m3.metric("Peak Current ip",     f"{ipeak/1000:.2f} kA")

            add_to_history("1. Short Circuit",
                params={"S_r": f"{s_r} kVA", "u_k": f"{u_k}%", "U_n": f"{u_n} V"},
                results={"IrT": f"{IrT:.1f} A", "Ik''": f"{Ikmax/1000:.2f} kA",
                         "ip": f"{ipeak/1000:.2f} kA"})

            t     = np.linspace(0, 0.08, 2000)
            omega = 2 * np.pi * 50
            phi   = np.arctan(XT / RT) if RT != 0 else np.pi / 2
            tau   = (XT / omega) / RT  if RT != 0 else 0.045
            i_ac  = np.sqrt(2) * Ikmax * np.sin(omega * t - phi)
            i_dc  = np.sqrt(2) * Ikmax * np.sin(phi) * np.exp(-t / tau)
            i_tot = i_ac + i_dc

            fig, ax = make_fig(5, 2.2)
            ax.plot(t*1000, i_tot/1000, color='#d32f2f', lw=1.5, label='i(t)')
            ax.plot(t*1000, i_ac/1000,  color='#1976d2', lw=0.8, ls='--', alpha=0.7, label='AC')
            ax.plot(t*1000, i_dc/1000,  color='#388e3c', lw=0.8, ls='--', alpha=0.7, label='DC offset')
            ax.axhline(0, color='#999', lw=0.8)
            ax.axhline(ipeak/1000, color='#d32f2f', lw=0.7, ls=':', alpha=0.7,
                       label=f'ip={ipeak/1000:.2f} kA')
            ax.set_xlabel("Time [ms]", fontsize=8)
            ax.set_ylabel("Current [kA]", fontsize=8)
            ax.set_title("Short Circuit Waveform", fontsize=9, fontweight='bold')
            ax.legend(fontsize=7)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=False)

        except Exception as e:
            st.error(f"Error: {e}")

    show_history("1. Short Circuit")


# ═════════════════════════════════════════════════════════════
# MODULE 2 — CABLE SIZING
# ═════════════════════════════════════════════════════════════
elif module == "2. Cable Sizing":
    st.markdown("# 🔌 Cable Sizing")
    st.markdown("---")

    mode = st.radio("Mode", ["Single calculation", "Compare two scenarios"],
                    horizontal=True, label_visibility="collapsed")

    col1, col2, col3 = st.columns(3)
    with col1:
        ib   = st.number_input("Load Current Ib [A]",       value=160.0, help=tip("ib"))
        temp = st.number_input("Ambient Temperature [°C]",  value=30.0,  help=tip("temp"))
        k2   = st.number_input("Grouping Factor K2",        value=1.0,
                                min_value=0.1, max_value=1.0, step=0.01, help=tip("k2"))
        n    = st.number_input("Parallel Cables per phase", value=1,
                                min_value=1, max_value=6, help=tip("n_par"))
    with col2:
        v_cond = st.radio("Loaded Conductors", [3, 2])
        v_neu  = st.checkbox("Loaded Neutral \u2192 K3 = 0.86", value=False, help=tip("v_neu"))
    with col3:
        if mode == "Single calculation":
            v_mat_a = st.radio("Material", ["Cu", "Al"], key="mat_a", help=tip("cu_vs_al"))
            v_ins_a = st.radio("Insulation", ["XLPE", "PVC"], key="ins_a", help=tip("xlpe_vs_pvc"))
            if v_mat_a == "Al":
                st.info("⚠️  Al conductors < 16 mm² are not permitted per DS 60364.")
        else:
            sc1, sc2 = st.columns(2)
            with sc1:
                st.caption("Scenario A")
                v_mat_a = st.radio("Material A", ["Cu", "Al"], key="mat_a", help=tip("cu_vs_al"))
                v_ins_a = st.radio("Insulation A", ["XLPE", "PVC"], key="ins_a", help=tip("xlpe_vs_pvc"))
            with sc2:
                st.caption("Scenario B")
                v_mat_b = st.radio("Material B", ["Cu", "Al"], index=1, key="mat_b")
                v_ins_b = st.radio("Insulation B", ["XLPE", "PVC"], index=1, key="ins_b")

    if st.button("CALCULATE", type="primary"):
        try:
            k1_a, k3_a, kt_a, tgt_a, rows_a = calc_cable_sizing(
                ib, temp, k2, n, v_mat_a, v_ins_a, v_cond, v_neu)

            if mode == "Single calculation":
                fc1, fc2, fc3, fc4 = st.columns(4)
                fc1.metric("K1 (Temp)",    f"{k1_a:.3f}")
                fc2.metric("K2 (Group)",   f"{k2:.3f}")
                fc3.metric("K3 (Neutral)", f"{k3_a:.2f}")
                fc4.metric("K Total",      f"{kt_a:.3f}")
                st.markdown(f"""
                <div class="result-card">
                    <div class="label">Required Iz per cable (base rating)</div>
                    <div class="value">{tgt_a:.1f} A</div>
                </div>""", unsafe_allow_html=True)
                st.markdown("### Results")
                render_sizing_rows(rows_a)

                add_to_history("2. Cable Sizing",
                    params={"Ib": f"{ib}A", "Temp": f"{temp}°C", "K2": k2,
                            "Mat": v_mat_a, "Ins": v_ins_a},
                    results={"K_tot": f"{kt_a:.3f}", "Iz_req": f"{tgt_a:.1f}A",
                             "Tray": f"{rows_a[0]['sect']}mm²" if rows_a[0]['ok'] else "N/A"})

            else:
                k1_b, k3_b, kt_b, tgt_b, rows_b = calc_cable_sizing(
                    ib, temp, k2, n, v_mat_b, v_ins_b, v_cond, v_neu)

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"### 🅐  {v_mat_a} / {v_ins_a}")
                    st.metric("K Total", f"{kt_a:.3f}")
                    st.caption(f"Required Iz: {tgt_a:.1f} A")
                    render_sizing_rows(rows_a)
                with col_b:
                    st.markdown(f"### 🅑  {v_mat_b} / {v_ins_b}")
                    st.metric("K Total", f"{kt_b:.3f}")
                    st.caption(f"Required Iz: {tgt_b:.1f} A")
                    render_sizing_rows(rows_b)

                st.markdown("---")
                if rows_a[0]['ok'] and rows_b[0]['ok']:
                    sa, sb = rows_a[0]['sect'], rows_b[0]['sect']
                    winner = "🅐" if sa <= sb else "🅑"
                    st.info(f"**Cable Tray (E):**  🅐 {v_mat_a}/{v_ins_a} → **{sa} mm²**  "
                            f"vs  🅑 {v_mat_b}/{v_ins_b} → **{sb} mm²**  —  smaller: {winner}")

        except Exception as e:
            st.error(f"Error: {e}")

    show_history("2. Cable Sizing")


# ═════════════════════════════════════════════════════════════
# MODULE 3 — VOLTAGE DROP
# ═════════════════════════════════════════════════════════════
elif module == "3. Voltage Drop":
    st.markdown("# 📉 Voltage Drop & Dimensioning")
    st.markdown("---")

    mode = st.radio("Mode", ["Single calculation", "Compare two scenarios"],
                    horizontal=True, label_visibility="collapsed")

    # ── Common inputs ──
    col1, col2 = st.columns(2)
    with col1:
        e_len  = st.number_input("Cable Length [m]",    value=50.0, help=tip("e_len"))
        e_curr = st.number_input("Load Current Ib [A]", value=16.0, help=tip("ib"))
        cos_phi_val = st.number_input("Power Factor cos φ", value=0.85,
                                       min_value=0.5, max_value=1.0, step=0.01, help=tip("cos_phi"))
    with col2:
        v_sys  = st.selectbox("System Voltage [V]", [12,24,48,230,400,690], index=4)
        v_type = st.radio("Current Type", ["AC 3-phase", "AC 1-phase", "DC"])

    # ── Scenario inputs ──
    st.markdown("---")
    if mode == "Single calculation":
        sc1, sc2 = st.columns(2)
        with sc1:
            v_mat_a  = st.radio("Material", ["Cu","Al"], key="vd_mat_a", help=tip("cu_vs_al"))
        with sc2:
            e_sect_a = st.number_input("Section [mm\u00b2]", value=2.5, key="vd_sect_a", help=tip("e_sect"))
    else:
        sc1, sc2 = st.columns(2)
        with sc1:
            st.caption("Scenario A")
            v_mat_a  = st.radio("Material A", ["Cu","Al"], key="vd_mat_a", help=tip("cu_vs_al"))
            e_sect_a = st.number_input("Section A [mm\u00b2]", value=2.5, key="vd_sect_a", help=tip("e_sect"))
        with sc2:
            st.caption("Scenario B")
            v_mat_b  = st.radio("Material B", ["Cu","Al"], index=1, key="vd_mat_b")
            e_sect_b = st.number_input("Section B [mm\u00b2]", value=4.0, key="vd_sect_b")

    def vdrop_calc(mat, sect):
        rho = 0.0225 if mat == "Cu" else 0.036
        if v_type == "DC":
            factor, cph, sph = 2, 1.0, 0.0
        elif v_type == "AC 1-phase":
            factor, cph = 2, cos_phi_val
            sph = np.sqrt(max(1 - cos_phi_val**2, 0))
        else:
            factor, cph = np.sqrt(3), cos_phi_val
            sph = np.sqrt(max(1 - cos_phi_val**2, 0))
        x_l = 0.00008
        if v_type == "DC":
            dV = (factor * e_len * e_curr * rho) / sect
        else:
            R = (rho * e_len) / sect
            X = x_l * e_len
            dV = factor * e_curr * (R * cph + X * sph)
        return dV, (dV / v_sys) * 100, factor, cph

    def req_sections(factor, cph):
        rho = 0.0225
        out = {}
        for lim in [3, 5, 8]:
            lv  = (lim / 100) * v_sys
            req = (factor * e_len * e_curr * rho * cph) / lv
            match = next((s for s in SECTIONS if s >= req), None)
            out[lim] = (req, f"{match} mm²" if match else "> 300 mm²")
        return out

    if st.button("CALCULATE VOLTAGE DROP", type="primary"):
        try:
            dV_a, pct_a, factor_a, cph_a = vdrop_calc(v_mat_a, e_sect_a)
            color_a = "#d32f2f" if pct_a > 5 else ("#e65100" if pct_a > 3 else "#2e7d32")

            if mode == "Single calculation":
                c1, c2 = st.columns(2)
                c1.markdown(f"""
                <div class="result-card">
                    <div class="label">Voltage Drop ΔU</div>
                    <div class="value" style="color:{color_a};">{pct_a:.2f} %</div>
                </div>
                <div class="result-card">
                    <div class="label">Absolute drop</div>
                    <div class="value">{dV_a:.2f} V</div>
                </div>""", unsafe_allow_html=True)
                lims = req_sections(factor_a, cph_a)
                with c2:
                    st.markdown("**Min section per limit:**")
                    for lim, (req, match) in lims.items():
                        ok = "#2e7d32" if pct_a <= lim else "#e65100"
                        st.markdown(f"""
                        <div class="method-row">
                            <span class="method-name">Limit {lim}%</span>
                            <span class="method-section">{match}</span>
                            <span class="method-cap" style="color:{ok};">req. {req:.2f} mm²</span>
                        </div>""", unsafe_allow_html=True)

                fig, ax = make_fig(4.5, 2)
                ax.barh(["3%","5%","8%"], [3,5,8], color='#e0e0e0', height=0.5)
                ax.barh(["3%","5%","8%"],
                        [min(pct_a,3), min(pct_a,5), min(pct_a,8)],
                        color=color_a, height=0.5, alpha=0.85)
                ax.axvline(pct_a, color='#1976d2', lw=1.5, ls='--', label=f'ΔU={pct_a:.2f}%')
                ax.set_xlabel("Voltage Drop [%]", fontsize=8)
                ax.set_title("Drop vs. Limits", fontsize=9, fontweight='bold')
                ax.legend(fontsize=7)
                plt.tight_layout()
                st.pyplot(fig, use_container_width=False)

                add_to_history("3. Voltage Drop",
                    params={"L": f"{e_len}m", "Ib": f"{e_curr}A",
                            "S": f"{e_sect_a}mm²", "Mat": v_mat_a},
                    results={"ΔU": f"{pct_a:.2f}%", "ΔV": f"{dV_a:.2f}V"})

            else:
                dV_b, pct_b, factor_b, cph_b = vdrop_calc(v_mat_b, e_sect_b)
                color_b = "#d32f2f" if pct_b > 5 else ("#e65100" if pct_b > 3 else "#2e7d32")

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"### 🅐  {v_mat_a} / {e_sect_a} mm²")
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="label">Voltage Drop ΔU</div>
                        <div class="value" style="color:{color_a};">{pct_a:.2f} %  ({dV_a:.2f} V)</div>
                    </div>""", unsafe_allow_html=True)
                with col_b:
                    st.markdown(f"### 🅑  {v_mat_b} / {e_sect_b} mm²")
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="label">Voltage Drop ΔU</div>
                        <div class="value" style="color:{color_b};">{pct_b:.2f} %  ({dV_b:.2f} V)</div>
                    </div>""", unsafe_allow_html=True)

                fig, ax = make_fig(4, 2)
                bars = ax.bar(
                    [f"🅐 {v_mat_a}\n{e_sect_a}mm²", f"🅑 {v_mat_b}\n{e_sect_b}mm²"],
                    [pct_a, pct_b],
                    color=[color_a, color_b], alpha=0.85, edgecolor='white', width=0.4
                )
                for bar, val in zip(bars, [pct_a, pct_b]):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                            f'{val:.2f}%', ha='center', fontsize=8)
                ax.axhline(3, color='#e65100', lw=0.8, ls='--', alpha=0.6, label='3% limit')
                ax.axhline(5, color='#d32f2f', lw=0.8, ls='--', alpha=0.6, label='5% limit')
                ax.set_ylabel("ΔU [%]", fontsize=8)
                ax.set_title("Voltage Drop Comparison", fontsize=9, fontweight='bold')
                ax.legend(fontsize=7)
                plt.tight_layout()
                st.pyplot(fig, use_container_width=False)

                winner = "🅐" if pct_a <= pct_b else "🅑"
                st.info(f"Lower drop: {winner}  |  🅐 {pct_a:.2f}%  vs  🅑 {pct_b:.2f}%")

        except Exception as e:
            st.error(f"Error: {e}")

    show_history("3. Voltage Drop")


# ═════════════════════════════════════════════════════════════
# MODULE 4 — CABLE CAPACITY
# ═════════════════════════════════════════════════════════════
elif module == "4. Cable Capacity":
    st.markdown("# 📊 Cable Capacity (Iz)")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        sel_sect = st.selectbox("Cross-Section [mm²]", SECTIONS, index=5)
        v_mat    = st.radio("Material", ["Cu","Al"], help=tip("cu_vs_al"))
    with col2:
        v_ins  = st.radio("Insulation", ["XLPE","PVC"], help=tip("xlpe_vs_pvc"))
        v_cond = st.radio("Loaded Conductors", [3, 2])

    if st.button("GET CAPACITY", type="primary"):
        try:
            idx     = SECTIONS.index(sel_sect)
            methods = get_ds60364_data(v_ins, v_cond, v_mat)   # pass material

            if v_mat == "Al" and sel_sect < 16:
                st.warning("⚠️  Al conductors < 16 mm² are not permitted per DS 60364.")
                st.stop()

            cap_vals, cap_labels = [], []
            for m, vals in methods.items():
                cap = vals[idx]
                if cap == 0:
                    st.warning(f"⚠️  {m}: Al < 16 mm² — N/A")
                    continue
                cap_vals.append(cap)
                cap_labels.append(m)
                st.markdown(f"""
                <div class="method-row">
                    <span class="method-name">{m}</span>
                    <span class="method-section">{cap:.1f} A</span>
                </div>""", unsafe_allow_html=True)

            if cap_vals:
                add_to_history("4. Cable Capacity",
                    params={"S": f"{sel_sect}mm²", "Mat": v_mat, "Ins": v_ins, "Cond": v_cond},
                    results={cap_labels[0]: f"{cap_vals[0]:.1f}A",
                             cap_labels[1]: f"{cap_vals[1]:.1f}A"})

                fig, ax = make_fig(5, 2.2)
                colors_bar = ['#1976d2','#388e3c','#f57c00','#7b1fa2']
                bars = ax.bar(cap_labels, cap_vals, color=colors_bar[:len(cap_labels)],
                              alpha=0.8, edgecolor='white')
                for bar, val in zip(bars, cap_vals):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                            f'{val:.0f}A', ha='center', va='bottom', fontsize=7)
                ax.set_ylabel("Iz [A]", fontsize=8)
                ax.set_title(f"Capacity — {sel_sect} mm² {v_mat} {v_ins}", fontsize=9, fontweight='bold')
                ax.tick_params(axis='x', labelsize=7)
                plt.tight_layout()
                st.pyplot(fig, use_container_width=False)

        except Exception as e:
            st.error(f"Error: {e}")

    show_history("4. Cable Capacity")


# ═════════════════════════════════════════════════════════════
# MODULE 5 — PARALLEL CABLE LOAD
# ═════════════════════════════════════════════════════════════
elif module == "5. Parallel Cable Load":
    st.markdown("# ⚖️  Parallel Cable Load Distribution")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        i_total    = st.number_input("Total Load Current [A]", value=400.0)
        num_cables = st.number_input("Number of parallel cables", min_value=2, max_value=6, value=2)
    with col2:
        v_mat  = st.radio("Material", ["Cu", "Al"], help=tip("cu_vs_al"))
        v_ins  = st.radio("Insulation", ["XLPE","PVC"], help=tip("xlpe_vs_pvc"))
        v_meth = st.selectbox("Installation Method", [
            "Cable Tray (E)","In Conduit (B2)","Pipe in Ground (D1)","Direct in Ground (D2)"],
            help=tip("install_method"))

    st.markdown("#### Cable Specifications")
    cable_inputs = []
    cols = st.columns(int(num_cables))
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"**Cable {i+1}**")
            L = st.number_input("Length [m]",    value=10.0, key=f"L_{i}", help=tip("e_len"))
            S = st.selectbox("Section [mm²]", SECTIONS, index=10, key=f"S_{i}")
            cable_inputs.append({"L": L, "S": S})

    if st.button("CALCULATE", type="primary"):
        try:
            total_G  = sum(c["S"] / c["L"] for c in cable_inputs)
            tab_vals = get_ds60364_data(v_ins, 3, v_mat)[v_meth]   # pass material

            currents, max_izs, pcts = [], [], []
            for c in cable_inputs:
                i_c    = i_total * ((c["S"] / c["L"]) / total_G)
                iz_raw = tab_vals[SECTIONS.index(c["S"])]
                max_iz = iz_raw if iz_raw > 0 else float('nan')
                pct    = (i_c / max_iz) * 100 if max_iz > 0 else float('nan')
                currents.append(i_c); max_izs.append(max_iz); pcts.append(pct)

            for i, (c, i_c, max_iz, pct) in enumerate(zip(cable_inputs, currents, max_izs, pcts)):
                if np.isnan(pct):
                    st.markdown(f"""
                    <div class="method-row">
                        <span class="method-name">Cable {i+1} · {c['S']} mm² · {c['L']} m</span>
                        <span class="method-section danger">{i_c:.1f} A</span>
                        <span class="method-cap danger">⚠️ Al < 16 mm² — N/A</span>
                    </div>""", unsafe_allow_html=True)
                else:
                    cls    = "danger" if pct > 100 else ("warn" if pct > 85 else "ok")
                    status = "⛔ OVERLOADED" if pct > 100 else ("⚠️ HIGH" if pct > 85 else "✅ OK")
                    st.markdown(f"""
                    <div class="method-row">
                        <span class="method-name">Cable {i+1} · {c['S']} mm² · {c['L']} m</span>
                        <span class="method-section">{i_c:.1f} A</span>
                        <span class="method-cap {cls}">Max {max_iz:.0f} A · {pct:.1f}% {status}</span>
                    </div>""", unsafe_allow_html=True)

            add_to_history("5. Parallel Cable Load",
                params={"I_total": f"{i_total}A", "n": int(num_cables),
                        "Mat": v_mat, "Method": v_meth},
                results={f"C{i+1}": f"{c:.1f}A ({p:.0f}%)"
                         for i,(c,p) in enumerate(zip(currents,pcts)) if not np.isnan(p)})

            valid = [(c, iz, p) for c, iz, p in zip(currents, max_izs, pcts) if not np.isnan(p)]
            if valid:
                v_c, v_iz, v_p = zip(*valid)
                fig, ax = make_fig(5, 2.2)
                x = np.arange(len(valid))
                w = 0.35
                bc = ['#d32f2f' if p>100 else '#e65100' if p>85 else '#388e3c' for p in v_p]
                ax.bar(x-w/2, v_c,  w, label='Load [A]',   color=bc,       alpha=0.85, edgecolor='white')
                ax.bar(x+w/2, v_iz, w, label='Max Iz [A]', color='#1976d2', alpha=0.5, edgecolor='white')
                ax.set_xticks(x)
                ax.set_xticklabels([f"C{i+1}\n{cable_inputs[i]['S']}mm²" for i in range(len(valid))], fontsize=7)
                ax.set_ylabel("Current [A]", fontsize=8)
                ax.set_title("Load vs. Capacity", fontsize=9, fontweight='bold')
                ax.legend(fontsize=7)
                plt.tight_layout()
                st.pyplot(fig, use_container_width=False)

        except Exception as e:
            st.error(f"Error: {e}")

    show_history("5. Parallel Cable Load")


# ═════════════════════════════════════════════════════════════
# MODULE 6 — CONVERTER
# ═════════════════════════════════════════════════════════════
elif module == "6. Converter":
    st.markdown("# 🔄 Power & Current Converter")
    st.markdown("---")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        v_sys   = st.selectbox("System Voltage [V]", [12,24,48,230,400,690], index=4)
    with col_s2:
        cos_phi = st.number_input("Power Factor (cos φ)", value=0.85, step=0.05,
                                   min_value=0.1, max_value=1.0, help=tip("cos_phi"))

    phase_factor = np.sqrt(3) if v_sys in [400,690] else 1.0

    st.markdown("#### Enter ONE known value:")
    c1, c2, c3 = st.columns(3)
    with c1:
        kva_in  = st.number_input("Apparent Power [kVA]", value=0.0, min_value=0.0, key="kva")
        btn_kva = st.button("Convert from kVA", use_container_width=True)
    with c2:
        kw_in  = st.number_input("Active Power [kW]", value=0.0, min_value=0.0, key="kw")
        btn_kw = st.button("Convert from kW",  use_container_width=True)
    with c3:
        amp_in  = st.number_input("Current [A]", value=0.0, min_value=0.0, key="amp")
        btn_amp = st.button("Convert from A",   use_container_width=True)

    res_kva = res_kw = res_amp = None
    if btn_kva and kva_in > 0:
        res_kva = kva_in;  res_kw = kva_in * cos_phi
        res_amp = (kva_in * 1000) / (phase_factor * v_sys)
    elif btn_kw and kw_in > 0:
        res_kva = kw_in / cos_phi if cos_phi > 0 else 0;  res_kw = kw_in
        res_amp = (res_kva * 1000) / (phase_factor * v_sys)
    elif btn_amp and amp_in > 0:
        res_kva = (phase_factor * v_sys * amp_in) / 1000;  res_kw = res_kva * cos_phi
        res_amp = amp_in

    if res_kva is not None:
        st.markdown("---")
        r1, r2, r3 = st.columns(3)
        r1.markdown(f"""<div class="result-card">
            <div class="label">Apparent Power</div>
            <div class="value">{res_kva:.3f} kVA</div></div>""", unsafe_allow_html=True)
        r2.markdown(f"""<div class="result-card">
            <div class="label">Active Power</div>
            <div class="value ok">{res_kw:.3f} kW</div></div>""", unsafe_allow_html=True)
        r3.markdown(f"""<div class="result-card">
            <div class="label">Current</div>
            <div class="value danger">{res_amp:.1f} A</div></div>""", unsafe_allow_html=True)

        add_to_history("6. Converter",
            params={"V": f"{v_sys}V", "cosφ": cos_phi},
            results={"S": f"{res_kva:.2f}kVA", "P": f"{res_kw:.2f}kW", "I": f"{res_amp:.1f}A"})

        if res_kva > 0 and res_kw > 0:
            kvar = np.sqrt(max(res_kva**2 - res_kw**2, 0))
            fig, ax = make_fig(3.5, 3)
            ax.set_aspect('equal')
            tx = [0, res_kw, 0, 0];  ty = [0, 0, kvar, 0]
            ax.plot(tx, ty, color='#bbb', lw=1)
            ax.fill(tx[:3], ty[:3], alpha=0.08, color='#1976d2')
            ax.annotate('', xy=(res_kw,0),    xytext=(0,0),
                        arrowprops=dict(arrowstyle='->', color='#388e3c', lw=2))
            ax.annotate('', xy=(res_kw,kvar), xytext=(res_kw,0),
                        arrowprops=dict(arrowstyle='->', color='#d32f2f', lw=2))
            ax.annotate('', xy=(0,kvar),      xytext=(res_kw,kvar),
                        arrowprops=dict(arrowstyle='->', color='#1976d2', lw=2.5))
            ax.text(res_kw/2, -res_kva*0.07, f'P={res_kw:.2f}kW',
                    ha='center', color='#388e3c', fontsize=8)
            ax.text(res_kw*1.03, kvar/2, f'Q={kvar:.2f}kVAR', color='#d32f2f', fontsize=8)
            ax.text(res_kw/2-res_kva*0.08, kvar/2+res_kva*0.05,
                    f'S={res_kva:.2f}kVA', color='#1976d2', fontsize=8,
                    rotation=np.degrees(np.arctan2(kvar, res_kw)))
            angle = np.linspace(0, np.arctan2(kvar, res_kw), 40)
            r_arc = res_kva * 0.18
            ax.plot(r_arc*np.cos(angle), r_arc*np.sin(angle), color='#999', lw=1)
            ax.text(r_arc*1.1, r_arc*0.2,
                    f'φ={np.degrees(np.arctan2(kvar,res_kw)):.1f}°', color='#555', fontsize=7)
            ax.set_title("Power Triangle", fontsize=9, fontweight='bold')
            ax.axis('off')
            plt.tight_layout()
            st.pyplot(fig, use_container_width=False)

    show_history("6. Converter")


# ═════════════════════════════════════════════════════════════
# MODULE 7 — BATTERY / UPS
# ═════════════════════════════════════════════════════════════
elif module == "7. Battery / UPS":
    st.markdown("# 🔋 Battery / UPS Calculator")
    st.markdown("---")

    calc_mode = st.radio("What do you want to calculate?", [
        "Ah → kW / kVA  (battery capacity to power)",
        "kW → Ah  (power to required battery capacity)",
        "Autonomy  (how long will the battery last?)",
        "Ah/h consumption → UPS size  (what UPS do I need?)"
    ], label_visibility="collapsed")

    st.markdown("---")

    if calc_mode == "Ah → kW / kVA  (battery capacity to power)":
        st.markdown("### Battery Capacity → Power Output")
        col1, col2 = st.columns(2)
        with col1:
            ah       = st.number_input("Battery Capacity [Ah]", value=100.0, min_value=0.1)
            v_bat    = st.number_input("Battery Voltage [V]",   value=48.0,
                                        help="Nominal voltage of the battery bank (e.g. 12, 24, 48, 120, 230 V)")
            t_disch  = st.number_input("Discharge Time [h]",    value=1.0, min_value=0.1,
                                        help="Over how many hours is the energy delivered? (e.g. 1h = full discharge in 1 hour)")
        with col2:
            eta      = st.number_input("Efficiency [%]", value=90.0, min_value=50.0, max_value=100.0,
                                        help="Battery + inverter efficiency. Typical: 85–95%")
            cos_phi  = st.number_input("Power Factor cos φ", value=0.9, min_value=0.1, max_value=1.0,
                                        help=tip("cos_phi"))

        if st.button("CALCULATE", type="primary"):
            wh       = ah * v_bat
            kwh      = wh / 1000
            kw       = (kwh / t_disch) * (eta / 100)
            kva      = kw / cos_phi
            i_dc     = (kw * 1000) / v_bat
            i_ac_230 = (kva * 1000) / 230
            i_ac_400 = (kva * 1000) / (np.sqrt(3) * 400)

            m1, m2, m3 = st.columns(3)
            m1.metric("Energy stored",  f"{kwh:.2f} kWh")
            m2.metric("Power output P", f"{kw:.2f} kW")
            m3.metric("Apparent S",     f"{kva:.2f} kVA")

            m4, m5, m6 = st.columns(3)
            m4.metric("DC Current (battery)", f"{i_dc:.1f} A",
                      help=f"Current drawn from the {v_bat}V DC battery bank")
            m5.metric("AC Current 230V",      f"{i_ac_230:.1f} A",
                      help="Output current at 230V single-phase")
            m6.metric("AC Current 400V 3φ",   f"{i_ac_400:.1f} A",
                      help="Output current at 400V three-phase")

            st.markdown(f"""
            <div class="result-card">
                <div class="label">Summary</div>
                <div style="font-size:15px; margin-top:6px; line-height:1.9;">
                    <b>{ah} Ah</b> at <b>{v_bat} V DC</b> = <b>{kwh:.2f} kWh</b> stored<br>
                    Discharged over <b>{t_disch} h</b> at {eta}% efficiency →
                    <b style="color:#2e7d32;">{kw:.2f} kW  /  {kva:.2f} kVA</b><br>
                    DC side: <b>{i_dc:.1f} A @ {v_bat}V</b>  ·
                    AC side: <b>{i_ac_230:.1f} A @ 230V</b>  /  <b>{i_ac_400:.1f} A @ 400V</b>
                </div>
            </div>""", unsafe_allow_html=True)

            add_to_history("7. Battery / UPS",
                params={"Ah": ah, "V": f"{v_bat}V DC", "t": f"{t_disch}h"},
                results={"kWh": f"{kwh:.2f}", "kW": f"{kw:.2f}", "kVA": f"{kva:.2f}",
                         "I_DC": f"{i_dc:.1f}A", "I_AC230": f"{i_ac_230:.1f}A"})

            fig, ax = make_fig(4, 2)
            labels = ["Stored\nenergy (kWh)", f"Power\noutput (kW)\n÷{t_disch}h", "Apparent\npower (kVA)"]
            values = [kwh, kw, kva]
            colors = ['#1976d2', '#388e3c', '#f57c00']
            bars = ax.bar(labels, values, color=colors, alpha=0.8, edgecolor='white', width=0.4)
            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.02,
                        f'{val:.2f}', ha='center', fontsize=8)
            ax.set_title("Battery Power Summary", fontsize=9, fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig, use_container_width=False)

    elif calc_mode == "kW → Ah  (power to required battery capacity)":
        st.markdown("### Required Power → Battery Capacity")
        col1, col2 = st.columns(2)
        with col1:
            kw_need  = st.number_input("Required Power [kW]",   value=5.0,  min_value=0.01)
            t_need   = st.number_input("Autonomy needed [h]",   value=4.0,  min_value=0.1,
                                        help="How many hours must the battery sustain the load?")
            v_bat    = st.number_input("Battery Voltage [V]",   value=48.0)
        with col2:
            eta      = st.number_input("Efficiency [%]", value=90.0, min_value=50.0, max_value=100.0)
            dod      = st.number_input("Depth of Discharge DoD [%]", value=80.0,
                                        min_value=10.0, max_value=100.0,
                                        help="How much of the battery capacity you actually use. "
                                             "Lithium: 80–90%. Lead-acid: 50%. Higher DoD = shorter battery life.")

        if st.button("CALCULATE", type="primary"):
            kwh_need    = kw_need * t_need
            kwh_total   = kwh_need / (eta / 100)
            kwh_nominal = kwh_total / (dod / 100)
            ah_need     = (kwh_nominal * 1000) / v_bat

            m1, m2, m3 = st.columns(3)
            m1.metric("Energy needed",    f"{kwh_need:.2f} kWh")
            m2.metric("Nominal capacity", f"{kwh_nominal:.2f} kWh")
            m3.metric("Battery capacity", f"{ah_need:.0f} Ah")

            st.markdown(f"""
            <div class="result-card">
                <div class="label">Summary</div>
                <div style="font-size:15px; margin-top:6px;">
                    Load <b>{kw_need} kW</b> for <b>{t_need} h</b>
                    = <b>{kwh_need:.2f} kWh</b> needed<br>
                    With {eta}% efficiency and {dod}% DoD →
                    minimum battery: <b style="color:#2e7d32;">{ah_need:.0f} Ah at {v_bat} V</b>
                </div>
            </div>""", unsafe_allow_html=True)

            fig, ax = make_fig(3, 3)
            ax.set_aspect('equal')
            usable   = dod / 100
            reserve  = 1 - usable
            wedges, texts, autotexts = ax.pie(
                [usable, reserve],
                labels=["Usable", "Reserve"],
                autopct='%1.0f%%',
                colors=['#388e3c', '#e0e0e0'],
                startangle=90,
                wedgeprops=dict(width=0.5)
            )
            for t in texts + autotexts:
                t.set_fontsize(8)
            ax.set_title(f"DoD — {ah_need:.0f} Ah total", fontsize=9, fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig, use_container_width=False)

            add_to_history("7. Battery / UPS",
                params={"kW": kw_need, "t": f"{t_need}h", "V": f"{v_bat}V", "DoD": f"{dod}%"},
                results={"kWh needed": f"{kwh_need:.2f}", "Ah required": f"{ah_need:.0f}"})

    elif calc_mode == "Autonomy  (how long will the battery last?)":
        st.markdown("### Battery Autonomy")
        col1, col2 = st.columns(2)
        with col1:
            ah_avail = st.number_input("Battery Capacity [Ah]", value=200.0, min_value=0.1)
            v_bat    = st.number_input("Battery Voltage [V]",   value=48.0)
            dod      = st.number_input("Depth of Discharge DoD [%]", value=80.0,
                                        min_value=10.0, max_value=100.0,
                                        help="Lead-acid: max 50%. Lithium: 80–90%.")
        with col2:
            kw_load  = st.number_input("Load [kW]",        value=3.0,  min_value=0.01)
            eta      = st.number_input("Efficiency [%]",   value=90.0, min_value=50.0, max_value=100.0)

        if st.button("CALCULATE", type="primary"):
            kwh_stored  = (ah_avail * v_bat) / 1000
            kwh_usable  = kwh_stored * (dod / 100) * (eta / 100)
            hours       = kwh_usable / kw_load
            minutes     = (hours % 1) * 60

            m1, m2, m3 = st.columns(3)
            m1.metric("Energy stored",  f"{kwh_stored:.2f} kWh")
            m2.metric("Usable energy",  f"{kwh_usable:.2f} kWh")
            m3.metric("Autonomy",       f"{int(hours)}h {int(minutes)}min")

            st.markdown(f"""
            <div class="result-card">
                <div class="label">Summary</div>
                <div style="font-size:15px; margin-top:6px;">
                    <b>{ah_avail} Ah</b> at <b>{v_bat} V</b>
                    with {dod}% DoD and {eta}% efficiency<br>
                    sustains a <b>{kw_load} kW</b> load for
                    <b style="color:#2e7d32;">{int(hours)} hours {int(minutes)} minutes</b>
                </div>
            </div>""", unsafe_allow_html=True)

            fig, ax = make_fig(5, 1.5)
            ax.barh([""], [hours], color='#388e3c', alpha=0.8, edgecolor='white', height=0.4)
            ax.axvline(1,  color='#1976d2', lw=1, ls='--', alpha=0.6, label='1h')
            ax.axvline(4,  color='#f57c00', lw=1, ls='--', alpha=0.6, label='4h')
            ax.axvline(8,  color='#d32f2f', lw=1, ls='--', alpha=0.6, label='8h')
            ax.text(hours + 0.05, 0, f'{int(hours)}h {int(minutes)}min',
                    va='center', fontsize=8, color='#388e3c', fontweight='bold')
            ax.set_xlabel("Hours", fontsize=8)
            ax.set_title("Autonomy", fontsize=9, fontweight='bold')
            ax.legend(fontsize=7, loc='lower right')
            ax.grid(False)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=False)

            add_to_history("7. Battery / UPS",
                params={"Ah": ah_avail, "V": f"{v_bat}V", "Load": f"{kw_load}kW", "DoD": f"{dod}%"},
                results={"Autonomy": f"{int(hours)}h {int(minutes)}min",
                         "Usable": f"{kwh_usable:.2f}kWh"})

    else:  # Ah/h → UPS size
        st.markdown("### Ah/h Consumption → UPS Size")
        st.info("You know your load consumes X Ah per hour and you need Y hours of autonomy. "
                "This tells you exactly what UPS and battery to buy.")

        col1, col2 = st.columns(2)
        with col1:
            ah_per_h = st.number_input("Load consumption [Ah/h]", value=10.0, min_value=0.1,
                                        help="How many Ah your load draws per hour. "
                                             "Measure with a clamp meter or check device specs.")
            t_auto   = st.number_input("Required autonomy [h]",   value=5.0,  min_value=0.1,
                                        help="How many hours the UPS must sustain the load.")
            v_sys    = st.selectbox("System voltage [V]", [12, 24, 48, 120, 230], index=2,
                                     help="Nominal DC bus voltage of the UPS battery bank.")
        with col2:
            eta      = st.number_input("UPS efficiency [%]",          value=90.0,
                                        min_value=50.0, max_value=100.0,
                                        help="Typical UPS efficiency: 85–95%. Check datasheet.")
            dod      = st.number_input("Depth of Discharge DoD [%]",  value=80.0,
                                        min_value=10.0, max_value=100.0,
                                        help="Lead-acid: max 50% (longer life). Lithium: 80–90%.")
            cos_phi  = st.number_input("Load power factor cos φ",     value=0.9,
                                        min_value=0.1, max_value=1.0,
                                        help="IT equipment / servers: ~0.9. Pure resistive: 1.0.")

        if st.button("CALCULATE UPS SIZE", type="primary"):
            ah_raw      = ah_per_h * t_auto
            ah_losses   = ah_raw / (eta / 100)
            ah_nominal  = ah_losses / (dod / 100)
            kwh_nominal = (ah_nominal * v_sys) / 1000

            kw_load  = (ah_per_h * v_sys) / 1000
            kva_load = kw_load / cos_phi

            ups_sizes = [0.5, 0.65, 0.8, 1.0, 1.5, 2.0, 3.0, 5.0, 6.0, 8.0, 10.0, 15.0, 20.0]
            ups_rec   = next((s for s in ups_sizes if s >= kva_load * 1.25), ups_sizes[-1])

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Load power",       f"{kw_load:.2f} kW")
            m2.metric("Apparent power",   f"{kva_load:.2f} kVA")
            m3.metric("Battery needed",   f"{ah_nominal:.0f} Ah")
            m4.metric("Recommended UPS",  f"{ups_rec} kVA")

            color = "#2e7d32"
            st.markdown(f"""
            <div class="result-card">
                <div class="label">UPS Sizing Result</div>
                <div style="font-size:15px; margin-top:8px; line-height:1.9;">
                    Load: <b>{ah_per_h} Ah/h × {v_sys} V</b> = <b>{kw_load:.2f} kW  /  {kva_load:.2f} kVA</b><br>
                    Autonomy: <b>{t_auto} h</b>  →  raw energy needed: <b>{ah_raw:.0f} Ah</b><br>
                    After {eta}% efficiency + {dod}% DoD  →
                    <b style="color:{color};">battery minimum: {ah_nominal:.0f} Ah @ {v_sys} V</b><br>
                    With 25% safety margin  →
                    <b style="color:#1a6fc4;">buy a UPS rated ≥ {ups_rec} kVA</b>
                </div>
            </div>""", unsafe_allow_html=True)

            fig, ax = make_fig(5, 2.2)
            labels = ["Raw Ah\nneeded", "After\nefficiency", "After\nDoD\n(buy this)"]
            values = [ah_raw, ah_losses, ah_nominal]
            colors = ['#90caf9', '#42a5f5', '#1976d2']
            bars = ax.bar(labels, values, color=colors, alpha=0.85, edgecolor='white', width=0.4)
            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.02,
                        f'{val:.0f} Ah', ha='center', fontsize=8, fontweight='bold')
            ax.set_ylabel("Ah", fontsize=8)
            ax.set_title("Battery Capacity Breakdown", fontsize=9, fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig, use_container_width=False)

            add_to_history("7. Battery / UPS",
                params={"Consumption": f"{ah_per_h}Ah/h", "Autonomy": f"{t_auto}h",
                        "V": f"{v_sys}V", "DoD": f"{dod}%"},
                results={"Battery": f"{ah_nominal:.0f}Ah", "UPS": f"≥{ups_rec}kVA",
                         "Load": f"{kva_load:.2f}kVA"})

    show_history("7. Battery / UPS")


# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("⚡ Elec Calc  ·  DS 60364  ·  Built by Ionut Vieru")
