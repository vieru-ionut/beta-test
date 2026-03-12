import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import os

# PAGE CONFIG
st.set_page_config(
    page_title="CableCalc",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .result-card { background:#f8f9fa; border-left:4px solid #1a6fc4; border-radius:4px; padding:14px 18px; margin:8px 0; }
    .result-card .label { font-size:12px; color:#666; text-transform:uppercase; letter-spacing:0.08em; }
    .result-card .value { font-size:1.8rem; font-weight:700; color:#1a6fc4; }
    .result-card .value.danger { color:#d32f2f; }
    .result-card .value.ok    { color:#2e7d32; }
    .method-row { display:flex; align-items:center; border:1px solid #e0e0e0; border-radius:4px; padding:10px 16px; margin:5px 0; background:#fff; }
    .method-name    { color:#555; font-size:14px; flex:0 0 180px; }
    .method-section { color:#1a6fc4; font-size:1.3rem; font-weight:700; flex:0 0 100px; text-align:right; }
    .method-cap     { color:#2e7d32; font-size:13px; font-family:monospace; flex:1; text-align:right; }
    .method-cap.warn   { color:#e65100; }
    .method-cap.danger { color:#d32f2f; }
    .hist-card { background:#f0f4ff; border:1px solid #c5d5f5; border-radius:4px; padding:10px 14px; margin:4px 0; font-size:13px; }
    .hist-card .htime { color:#999; font-size:11px; }
    .hist-card .hval  { font-weight:700; color:#1a6fc4; }
</style>
""", unsafe_allow_html=True)

# PASSWORD
def check_password():
    if st.session_state.get("password_correct", False):
        return True
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        st.markdown("## ⚡ CableCalc")

		# --- PANOU WHAT'S NEW ---
        st.info("""
        **✨ What's new in Version 2.0:**
        * **Scenario Comparison:** Compare Cable A vs Cable B side-by-side.
        * **Expanded DB:** Support for Single Wire installation.
        """)
		
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
# DATA TABLES  DS 60364 / IEC 60364-5-52
# construction = "Multicore"   → Table B.52.2 (B2 conduit)
# construction = "Single Wire" → Table B.52.3 (B1 conduit, trefoil tray)
# Al values stored explicitly; 0 = not permitted for that section/method combination
# Multicore Al: Tray/B2/D1 start from 2.5 mm²; D2 only from 16 mm²
# Single Wire Al: all methods start from 16 mm²
# ─────────────────────────────────────────────────────────────
SECTIONS = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300]
# Short labels for chart x-axes
SHORT_M = {
    "Cable Tray (E)":                              "Tray (E)",
    "Cable Tray (F)":                              "Tray (F)",
    "Trefoil (F)":                                 "Trefoil (F)",
    "In Conduit (B1)":                             "Conduit B1",
    "In Conduit (B2)":                             "Conduit B2",
    "Pipe in Ground (D1)":                         "Ground D1",
    "Direct in Ground (D2)":                       "Ground D2",
    "Single layer with distance - horizontal (G)": "Horiz. (G)",
    "Single layer with distance - vertical (G)":   "Vert. (G)",
}
def short_m(m): return SHORT_M.get(m, m)
def get_ds60364_data(insulation, loaded_cond, material="Cu", construction="Multicore"):
    if construction == "Single Wire":
        if material == "Al":
            if insulation == "PVC":
                if loaded_cond == 2:
                    return {
                        "Cable Tray (F)":        [0,0,0,0,0,0,98,122,149,192,235,273,316,363,430,467],
                        "In Conduit (B1)":       [0,18.5,25,32,44,60,79,97,118,150,181,210,234,266,312,358],
                        "Pipe in Ground (D1)":   [0, 22, 29, 36, 47, 61, 77,  93, 109, 135, 159, 180, 204, 228, 262, 296],
                        "Direct in Ground (D2)": [0, 0, 0, 0, 0, 63, 82, 98, 117, 145, 173, 200, 224, 255, 298, 336],
                    }
                else:
                    return {
                        "Trefoil (F)":        [0,0,0,0,0,0, 84,105,128,166,203,237,274,315,375,434],
 						"Single layer with distance - horizontal (G)":        [0,0,0,0,0,0,112,139,169,217,265,308,356,407,482,557],
						"Single layer with distance - vertical (G)":        [0,0,0,0,0,0,99,124,152,196,241,282,327,376,447,519],
                        "In Conduit (B1)":       [0,16.5,22,28,39,53,70,86,104,133,161,186,204,230,269,306],
                        "Pipe in Ground (D1)":   [0, 18.5, 24, 30, 39, 50, 64, 77, 91, 112, 132, 150, 169, 190, 218, 247],
                        "Direct in Ground (D2)": [0, 0, 0, 0, 0, 53, 69, 83, 99, 122, 148, 169, 189, 214, 250, 282],
                    }
            else:  # XLPE
                if loaded_cond == 2:
                    return {
                        "Cable Tray (F)":        [0,0,0,0,0, 0,121,150,184,237,289,337,389,447,530,613],
                        "In Conduit (B1)":       [0,25,33,43,59, 79, 105,130,157,200,242,281,307,351,412,471],
                        "Pipe in Ground (D1)":   [0, 26, 33, 42, 55, 71, 90, 108, 128, 158, 186, 211, 238, 267, 307, 346],
                        "Direct in Ground (D2)": [0, 0, 0, 0, 0, 76.0, 98, 117, 139, 170, 204, 223, 261, 296, 343, 386],
                    }
                else:
                    return {
                        "Trefoil (F)":        [0,0,0,0,0,0, 103,129,159,206,253,296,343,395,471,547],
 						"Single layer with distance - horizontal (G)":        [0,0,0,0,0,0,138,172,210,271,332,387,448,515,611,708],
						"Single layer with distance - vertical (G)":        [0,0,0,0,0,0,122,153,188,244,300,351,408,470,561,652],
                        "In Conduit (B1)":       [0,22,29,38,52, 71, 93,116,140,179,217,251,267,300,351,402],
                        "Pipe in Ground (D1)":   [0, 22, 28, 35, 46, 59, 75, 90, 106, 130, 154, 174, 197, 220, 253, 286],
                        "Direct in Ground (D2)": [0, 0, 0, 0, 0, 64, 82, 98, 117, 144, 172, 197, 220, 250, 290, 326],
                    }
        # Cu Single Wire
        if insulation == "PVC":
            if loaded_cond == 2:
                return {
                    "Cable Tray (F)":        [0, 0, 0, 0, 0, 0, 131, 162, 196, 251, 304, 352, 406, 463, 546, 629],
                    "In Conduit (B1)":       [19, 27, 36, 46, 63,  83, 108, 133, 161, 202, 242, 278, 312, 359, 422, 485],
                    "Pipe in Ground (D1)":   [22,29,37,46,60, 78, 99,119,140,173,204,231,261,292,336,379],
                    "Direct in Ground (D2)": [22,28,38,48,64, 83,110,132,156,192,230,261,293,331,382,427],
                }
            else:
                return {
                    "Trefoil (F)":        [0,0,0,0,0,0, 110,137,167,216,264,308,356,409,485,561],
 		   			"Single layer with distance - horizontal (G)":        [0,0,0,0,0,0,146,181,219,281,341,396,456,521,615,709],
 		    		"Single layer with distance - vertical (G)":        [0,0,0,0,0,0,130,162,197,254,311,362,419,480,569,659],
                    "In Conduit (B1)":       [16, 22, 30, 38, 52,  68,  89, 110, 132, 166, 199, 230, 258, 295, 346, 396],
                    "Pipe in Ground (D1)":   [18, 24, 30, 38, 50,  64,  82,  98, 116, 143, 169, 192, 217, 243, 280, 316],
                    "Direct in Ground (D2)": [19, 24, 33, 41, 54,  70,  92, 110, 130, 162, 193, 220, 246, 278, 320, 359],
                }
        else:  # XLPE
            if loaded_cond == 2:
                return {
                    "Cable Tray (F)":        [0, 0, 0, 0,  0, 0, 161, 200, 242, 310, 377, 437, 504, 575, 679, 783],
                    "In Conduit (B1)":       [23, 32, 42, 54,  73,  96, 127, 155, 186, 237, 283, 326, 367, 420, 500, 578],
                    "Pipe in Ground (D1)":   [25, 33, 43, 53,  71,  91, 116, 139, 164, 203, 239, 271, 306, 343, 395, 446],
                    "Direct in Ground (D2)": [27, 35, 46, 58,  77, 100, 129, 155, 183, 225, 270, 306, 343, 387, 448, 502],
                }
            else:
                return {
                    "Trefoil (F)":        [0,0,0,0,0,0, 135,169,207,268,328,383,444,510,607,703],
 		    		"Single layer with distance - horizontal (G)":        [0,0,0,0,0,0,182,226,275,353,430,500,577,661,781,902],
		    		"Single layer with distance - vertical (G)":        [0,0,0,0,0,0,161,201,246,318,389,454,527,605,719,833],
                    "In Conduit (B1)":       [20, 28, 37, 47,  64,  84, 111, 136, 164, 207, 248, 286, 324, 370, 439, 507],
                    "Pipe in Ground (D1)":   [21, 28, 36, 44,  58,  75,  96, 115, 135, 167, 197, 223, 251, 281, 324, 365],
                    "Direct in Ground (D2)": [23, 30, 39, 49,  65,  84, 107, 129, 153, 188, 226, 257, 287, 324, 375, 419],
                }

    # MULTICORE
    if material == "Al":
        if insulation == "PVC":
            if loaded_cond == 2:
                return {
                    "Cable Tray (E)":        [0, 23,   31,   39,   54,   73,   89,  111,  135,  173,  210,  244,  282,  322,  380,  439],
                    "In Conduit (B2)":       [0, 17.5, 24,   30,   41,   54,   71,   86,  104,  131,  157,  181,  201,  230,  269,  308],
                    "Pipe in Ground (D1)":   [0, 22,   29,   36,   47,   61,   77,   93,  109,  135,  159,  180,  204,  228,  262,  296],
                    "Direct in Ground (D2)": [0,  0,    0,    0,    0,   63,   82,   98,  117,  145,  173,  200,  224,  255,  298,  336],
                }
            else:
                return {
                    "Cable Tray (E)":        [0, 19.5, 26,   33,   46,   61,   78,   96,  117,  150,  183,  212,  245,  280,  330,  381],
                    "In Conduit (B2)":       [0, 15.5, 21,   27,   36,   48,   62,   77,   92,  116,  139,  160,  176,  199,  232,  265],
                    "Pipe in Ground (D1)":   [0, 18.5, 24,   30,   39,   50,   64,   77,   91,  112,  132,  150,  169,  190,  218,  247],
                    "Direct in Ground (D2)": [0,  0,    0,    0,    0,   53,   69,   83,   99,  122,  148,  169,  189,  214,  250,  282],
                }
        else:  # XLPE
            if loaded_cond == 2:
                return {
                    "Cable Tray (E)":        [0, 28,   38,   49,   67,   91,  108,  135,  164,  211,  257,  300,  346,  397,  470,  543],
                    "In Conduit (B2)":       [0, 23,   31,   40,   54,   72,   94,  115,  138,  175,  210,  242,  261,  300,  358,  415],
                    "Pipe in Ground (D1)":   [0, 26,   33,   42,   55,   71,   90,  108,  128,  158,  186,  211,  238,  267,  307,  346],
                    "Direct in Ground (D2)": [0,  0,    0,    0,    0,   76,   98,  117,  139,  170,  204,  223,  261,  296,  343,  386],
                }
            else:
                return {
                    "Cable Tray (E)":        [0, 24,   32,   42,   58,   77,   97,  120,  146,  187,  227,  263,  304,  347,  409,  471],
                    "In Conduit (B2)":       [0, 21,   28,   35,   48,   64,   84,  103,  124,  156,  188,  216,  240,  272,  318,  364],
                    "Pipe in Ground (D1)":   [0, 22,   28,   35,   46,   59,   75,   90,  106,  130,  154,  174,  197,  220,  253,  286],
                    "Direct in Ground (D2)": [0,  0,    0,    0,    0,   64,   82,   98,  117,  144,  172,  197,  220,  250,  290,  326],
                }
    # Cu Multicore
    if insulation == "PVC":
        if loaded_cond == 2:
            return {
                "Cable Tray (E)":        [22,30,40,51,70,94,119,148,180,232,282,328,379,434,514,593],
                "In Conduit (B2)":       [16.5,23,30,38,52, 69, 90,111,133,168,201,232,258,294,344,394],
                "Pipe in Ground (D1)":   [22,29,37,46,60, 78, 99,119,140,173,204,231,261,292,336,379],
                "Direct in Ground (D2)": [22,28,38,48,64, 83,110,132,156,192,230,261,293,331,382,427],
            }
        else:
            return {
                "Cable Tray (E)":        [18.5,25,34,43,60, 80,101,126,153,196,238,276,319,364,430,497],
                "In Conduit (B2)":       [15,20,27,34,46, 62, 80, 99,118,149,179,206,225,255,297,339],
                "Pipe in Ground (D1)":   [18,24,30,38,50, 64, 82, 98,116,143,169,192,217,243,280,316],
                "Direct in Ground (D2)": [19,24,33,41,54, 70, 92,110,130,162,193,220,246,278,320,359],
            }
    else:
        if loaded_cond == 2:
            return {
                "Cable Tray (E)":        [26,36,49,63,86,115,149,185,225,289,352,410,473,542,641,741],
                "In Conduit (B2)":       [22,30,40,51,69, 91,119,146,175,221,265,305,334,384,459,532],
                "Pipe in Ground (D1)":   [25,33,43,53,71, 91,116,139,164,203,239,271,306,343,395,446],
                "Direct in Ground (D2)": [27,35,46,58,77,100,129,155,183,225,270,306,343,387,448,502],
            }
        else:
            return {
                "Cable Tray (E)":        [23,32,42,54,75,100,127,158,192,246,298,346,399,456,538,621],
                "In Conduit (B2)":       [19.5,26,35,44,60, 80,105,128,154,194,233,268,300,340,398,455],
                "Pipe in Ground (D1)":   [21,28,36,44,58, 75, 96,115,135,167,197,223,251,281,324,365],
                "Direct in Ground (D2)": [23,30,39,49,65, 84,107,129,153,188,226,257,287,324,375,419],
            }



# HISTORY
def init_history():
    if "calc_history" not in st.session_state:
        st.session_state.calc_history = []

def add_to_history(module_name, params, results):
    import datetime
    init_history()
    entry = {"module": module_name, "params": params, "results": results,
             "time": datetime.datetime.now().strftime("%H:%M:%S")}
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
            st.markdown(f"""<div class="hist-card"><span class="htime">{e['time']}</span><br>
                <span style="color:#555">{params_str}</span><br>
                <span class="hval">{results_str}</span></div>""", unsafe_allow_html=True)
        if st.button("Clear history", key=f"clr_{module_name}"):
            st.session_state.calc_history = [e for e in st.session_state.calc_history if e["module"] != module_name]
            st.rerun()
			
from fpdf import FPDF
import io

def generate_pdf(title, params: dict, results: dict, notes: str = "") -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "CableCalc — Calculation Report", ln=True)
    pdf.set_font("Helvetica", "", 10)
    import datetime
    pdf.cell(0, 6, f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d  %H:%M')}", ln=True)
    pdf.ln(4)

    # Title
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_fill_color(26, 111, 196)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 9, f"  {title}", ln=True, fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)

    # Input parameters
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Input Parameters", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for k, v in params.items():
        pdf.cell(70, 6, f"  {k}", border="B")
        pdf.cell(0,  6, str(v), border="B", ln=True)
    pdf.ln(4)

    # Results
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Results", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for k, v in results.items():
        pdf.set_fill_color(240, 244, 255)
        pdf.cell(70, 7, f"  {k}", border="B", fill=True)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0,  7, str(v), border="B", fill=True, ln=True)
        pdf.set_font("Helvetica", "", 10)
    pdf.ln(4)

    # Optional notes
    if notes:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(120, 120, 120)
        pdf.multi_cell(0, 5, notes)

    # Footer disclaimer
    pdf.set_y(-20)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, "⚠ Estimation tool only — does not replace professional design software or official standards.", ln=True)

    return bytes(pdf.output())

# TOOLTIPS
TT = {
    "u_pri":       "Rated primary voltage of the transformer (HV side), in kV.",
    "i_k_pri":     "Short-circuit current at the primary busbar. Type 'inf' if the upstream network is very stiff.",
    "s_r":         "Rated apparent power of the transformer in kVA. Found on the nameplate.",
    "u_n":         "Nominal secondary (LV) voltage. Typically 400 V for European 3-phase systems.",
    "u_k":         "Short-circuit impedance voltage in %. Typically 4-6% for distribution transformers.",
    "ib":          "Design load current the cable must carry continuously.",
    "temp":        "Ambient temperature around the cable. Higher temp = lower cable capacity (derating).",
    "k2":          "Grouping / bunching derating factor. 1.0 = single cable or well-separated.",
    "n_par":       "Number of cables in parallel per phase. Each cable carries Ib / n.",
    "v_neu":       "Apply K3 = 0.86 when the neutral carries significant harmonic current.",
    "cos_phi":     "Power factor. Purely resistive = 1.0. Induction motors ~0.75-0.90.",
    "e_len":       "One-way cable length in metres.",
    "e_sect":      "Cross-sectional area of one conductor in mm2.",
    "xlpe_vs_pvc": "XLPE allows 90C vs 70C for PVC => 15-25% higher capacity for same section.",
    "cu_vs_al":    "Al needs ~1.5x larger section. Multicore Al: Tray/Conduit/D1 permit from 2.5mm², D2 only from 16mm². Single Wire Al: from 16mm² only.",
    "construction":"Multicore: all conductors in one jacket (NYY, NAYY). Single Wire: each conductor separate (N2XH 1x). "
                   "Single wire allows higher ampacity on trays. Conduit method B1 (single) vs B2 (multi).",
    "install_method":"Cable Tray (E): best airflow. In Conduit (B1/B2): lower Iz. In Ground: depends on soil.",
}
def tip(k): return TT.get(k, "")

def make_fig(w=5, h=2.2):
    fig, ax = plt.subplots(figsize=(w, h), dpi=220)
    ax.grid(True, linestyle="--", alpha=0.4, color="#cccccc")
    ax.tick_params(labelsize=7)
    return fig, ax


# CABLE SIZING CALC
def calc_cable_sizing(ib, temp, k2, n, v_mat, v_ins, v_cond, v_neu, v_construction):
    if v_ins == "XLPE":
        k1_table = [(30,1.0),(35,0.96),(40,0.91),(45,0.87),(50,0.82),(55,0.76),(60,0.71),(65,0.65),(70,0.58),(999,0.50)]
    else:
        k1_table = [(30,1.0),(35,0.94),(40,0.87),(45,0.79),(50,0.71),(55,0.61),(60,0.50),(999,0.40)]
    k1 = next(v for t_lim, v in k1_table if temp <= t_lim)
    k3 = 0.86 if v_neu else 1.0
    k_total = k1 * k2 * k3
    target  = ib / (k_total * n)
    load_per_cable = ib / n
    methods = get_ds60364_data(v_ins, v_cond, v_mat, v_construction)
    rows = []
    for m, vals in methods.items():
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
            st.markdown(f"""<div class="method-row">
                <span class="method-name">{r['method']}</span>
                <span class="method-section">{r['sect']} mm2</span>
                <span class="method-cap {cls}">{r['actual']:.1f} A  ({r['pct']:.0f}%)</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="method-row">
                <span class="method-name">{r['method']}</span>
                <span class="method-section" style="color:#d32f2f">N/A</span>
                <span class="method-cap danger">&gt; 300 mm2</span>
                </div>""", unsafe_allow_html=True)


# SIDEBAR
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)
st.sidebar.markdown("## ⚡ CableCalc")
st.sidebar.caption("Design Tools")
module = st.sidebar.radio("", [
    "1. Short Circuit", "2. Cable Sizing", "3. Voltage Drop",
    "4. Cable Capacity", "5. Parallel Cable Load", "6. Converter", "7. Battery / UPS"
])
st.sidebar.markdown("---")
st.sidebar.caption("Built & maintained by Ionut Vieru")


# ═══════════════════════════════════
# MODULE 1 — SHORT CIRCUIT
# ═══════════════════════════════════
if module == "1. Short Circuit":
    st.markdown("# ⚡ Short Circuit — Transformer")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        u_pri   = st.number_input("U_pri [kV]",       value=10.0,   step=0.5,   help=tip("u_pri"))
        i_k_pri = st.text_input( "I_k upstream [kA]", value="inf",              help=tip("i_k_pri"))
        s_r     = st.number_input("S_r [kVA]",        value=1600.0, step=100.0, help=tip("s_r"))
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
                results={"IrT": f"{IrT:.1f} A", "Ik''": f"{Ikmax/1000:.2f} kA", "ip": f"{ipeak/1000:.2f} kA"})
            t = np.linspace(0, 0.08, 2000); omega = 2*np.pi*50
            phi = np.arctan(XT/RT) if RT != 0 else np.pi/2
            tau = (XT/omega)/RT if RT != 0 else 0.045
            i_ac = np.sqrt(2)*Ikmax*np.sin(omega*t-phi)
            i_dc = np.sqrt(2)*Ikmax*np.sin(phi)*np.exp(-t/tau)
            i_tot = i_ac + i_dc
            fig, ax = make_fig(5, 2.2)
            ax.plot(t*1000, i_tot/1000, color="#d32f2f", lw=1.5, label="i(t)")
            ax.plot(t*1000, i_ac/1000,  color="#1976d2", lw=0.8, ls="--", alpha=0.7, label="AC")
            ax.plot(t*1000, i_dc/1000,  color="#388e3c", lw=0.8, ls="--", alpha=0.7, label="DC offset")
            ax.axhline(0, color="#999", lw=0.8)
            ax.axhline(ipeak/1000, color="#d32f2f", lw=0.7, ls=":", alpha=0.7, label=f"ip={ipeak/1000:.2f} kA")
            ax.set_xlabel("Time [ms]", fontsize=8); ax.set_ylabel("Current [kA]", fontsize=8)
            ax.set_title("Short Circuit Waveform", fontsize=9, fontweight="bold"); ax.legend(fontsize=7)
            plt.tight_layout(); st.pyplot(fig, use_container_width=False)
        except Exception as e:
            st.error(f"Error: {e}")
    show_history("1. Short Circuit")
 
# ═══════════════════════════════════
# MODULE 2 — CABLE SIZING
# ═══════════════════════════════════
elif module == "2. Cable Sizing":
    st.markdown("# 🔌 Cable Sizing")
    st.markdown("---")
    mode = st.radio("Mode", ["Single calculation", "Compare two scenarios"], horizontal=True, label_visibility="collapsed")
    col1, col2, col3 = st.columns(3)
    with col1:
        ib   = st.number_input("Load Current Ib [A]",       value=160.0, help=tip("ib"))
        temp = st.number_input("Ambient Temperature [°C]",  value=30.0,  help=tip("temp"))
        k2   = st.number_input("Grouping Factor K2",        value=1.0, min_value=0.1, max_value=1.0, step=0.01, help=tip("k2"))
        n    = st.number_input("Parallel Cables per phase", value=1, min_value=1, max_value=6, help=tip("n_par"))
    with col2:
        v_cond = st.radio("Loaded Conductors", [3, 2])
        v_neu  = st.checkbox("Loaded Neutral -> K3 = 0.86", value=False, help=tip("v_neu"))
    with col3:
        if mode == "Single calculation":
            v_mat_a   = st.radio("Material",           ["Cu","Al"],                      key="mat_a", help=tip("cu_vs_al"))
            v_ins_a   = st.radio("Insulation",         ["XLPE","PVC"],                   key="ins_a", help=tip("xlpe_vs_pvc"))
            v_const_a = st.radio("Cable Construction", ["Multicore","Single Wire"],       key="cst_a", help=tip("construction"))
            if v_mat_a == "Al" and v_const_a == "Single Wire":
                st.info("Single Wire Al: sections < 16 mm² not permitted per DS 60364.")
        else:
            sc1, sc2 = st.columns(2)
            with sc1:
                st.caption("Scenario A")
                v_mat_a   = st.radio("Material A",      ["Cu","Al"],                 key="mat_a", help=tip("cu_vs_al"))
                v_ins_a   = st.radio("Insulation A",    ["XLPE","PVC"],              key="ins_a", help=tip("xlpe_vs_pvc"))
                v_const_a = st.radio("Construction A",  ["Multicore","Single Wire"], key="cst_a", help=tip("construction"))
            with sc2:
                st.caption("Scenario B")
                v_mat_b   = st.radio("Material B",      ["Cu","Al"],    index=1,     key="mat_b")
                v_ins_b   = st.radio("Insulation B",    ["XLPE","PVC"], index=1,     key="ins_b")
                v_const_b = st.radio("Construction B",  ["Multicore","Single Wire"], key="cst_b")
    if st.button("CALCULATE", type="primary"):
        try:
            k1_a, k3_a, kt_a, tgt_a, rows_a = calc_cable_sizing(ib, temp, k2, n, v_mat_a, v_ins_a, v_cond, v_neu, v_const_a)
            if mode == "Single calculation":
                fc1, fc2, fc3, fc4 = st.columns(4)
                fc1.metric("K1 (Temp)", f"{k1_a:.3f}"); fc2.metric("K2 (Group)", f"{k2:.3f}")
                fc3.metric("K3 (Neutral)", f"{k3_a:.2f}"); fc4.metric("K Total", f"{kt_a:.3f}")
                st.markdown(f"""<div class="result-card"><div class="label">Required Iz per cable (base rating)</div>
                    <div class="value">{tgt_a:.1f} A</div></div>""", unsafe_allow_html=True)
                st.markdown("### Results")
                render_sizing_rows(rows_a)
                add_to_history("2. Cable Sizing",
                    params={"Ib": f"{ib}A", "Temp": f"{temp}C", "K2": k2, "Mat": v_mat_a, "Ins": v_ins_a, "Constr": v_const_a},
                    results={"K_tot": f"{kt_a:.3f}", "Iz_req": f"{tgt_a:.1f}A",
                             "Tray": f"{rows_a[0]['sect']}mm2" if rows_a[0]["ok"] else "N/A"})
            else:
                k1_b, k3_b, kt_b, tgt_b, rows_b = calc_cable_sizing(ib, temp, k2, n, v_mat_b, v_ins_b, v_cond, v_neu, v_const_b)
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"### A  {v_mat_a} / {v_ins_a} / {v_const_a}")
                    st.metric("K Total", f"{kt_a:.3f}"); st.caption(f"Required Iz: {tgt_a:.1f} A")
                    render_sizing_rows(rows_a)
                with col_b:
                    st.markdown(f"### B  {v_mat_b} / {v_ins_b} / {v_const_b}")
                    st.metric("K Total", f"{kt_b:.3f}"); st.caption(f"Required Iz: {tgt_b:.1f} A")
                    render_sizing_rows(rows_b)
                st.markdown("---")
                if rows_a[0]["ok"] and rows_b[0]["ok"]:
                    sa, sb = rows_a[0]["sect"], rows_b[0]["sect"]
                    winner = "A" if sa <= sb else "B"
                    st.info(f"Cable Tray:  A {v_mat_a}/{v_ins_a}/{v_const_a} -> {sa} mm2  vs  B {v_mat_b}/{v_ins_b}/{v_const_b} -> {sb} mm2  |  smaller: {winner}")
        except Exception as e:
            st.error(f"Error: {e}")
    show_history("2. Cable Sizing")


# ═══════════════════════════════════
# MODULE 3 — VOLTAGE DROP
# ═══════════════════════════════════
elif module == "3. Voltage Drop":
    st.markdown("# 📉 Voltage Drop & Dimensioning")
    st.markdown("---")

    mode = st.radio(
        "Mode",
        ["Single calculation", "Compare two scenarios"],
        horizontal=True,
        label_visibility="collapsed"
    )

    col1, col2 = st.columns(2)
    with col1:
        e_len       = st.number_input("Cable Length [m]",    value=50.0,  min_value=0.1,  help=tip("e_len"))
        e_curr      = st.number_input("Load Current Ib [A]", value=16.0,  min_value=0.1,  help=tip("ib"))
        cos_phi_val = st.number_input("Power Factor cos φ",  value=0.85,  min_value=0.5,  max_value=1.0, step=0.01, help=tip("cos_phi"))
    with col2:
        # ── Track v_sys changes and reset v_type if needed ──────────────────
        if "vd_prev_vsys" not in st.session_state:
            st.session_state["vd_prev_vsys"] = None

        v_sys = st.selectbox("System Voltage [V]", [12, 24, 48, 230, 400, 690], index=3, key="vd_vsys")

        if st.session_state["vd_prev_vsys"] != v_sys:
            st.session_state["vd_prev_vsys"] = v_sys
            st.session_state.pop("vd_vtype", None)   # force radio reset

        # ── Restrict current type based on voltage ──────────────────────────
        if v_sys in [12, 24, 48]:
            allowed_types = ["DC"]
        elif v_sys == 230:
            allowed_types = ["AC 1-phase", "DC"]
        else:  # 400, 690
            allowed_types = ["AC 3-phase", "AC 1-phase", "DC"]

        v_type = st.radio("Current Type", allowed_types, key="vd_vtype")

        # cos φ is irrelevant for DC — show a note
        if v_type == "DC":
            st.caption("ℹ️ Power factor not used for DC.")

    st.markdown("---")

    # ── Section / material inputs ────────────────────────────────────────────
    if mode == "Single calculation":
        sc1, sc2 = st.columns(2)
        with sc1:
            v_mat_a  = st.radio("Conductor Material", ["Cu", "Al"], key="vd_mat_a", help=tip("cu_vs_al"))
        with sc2:
            e_sect_a = st.number_input("Section [mm²]", value=2.5, min_value=0.1, key="vd_sect_a", help=tip("e_sect"))
    else:
        sc1, sc2 = st.columns(2)
        with sc1:
            st.caption("Scenario A")
            v_mat_a  = st.radio("Material A", ["Cu", "Al"], key="vd_mat_a", help=tip("cu_vs_al"))
            e_sect_a = st.number_input("Section A [mm²]", value=2.5, min_value=0.1, key="vd_sect_a", help=tip("e_sect"))
        with sc2:
            st.caption("Scenario B")
            v_mat_b  = st.radio("Material B", ["Cu", "Al"], index=1, key="vd_mat_b")
            e_sect_b = st.number_input("Section B [mm²]", value=4.0, min_value=0.1, key="vd_sect_b")

    # ── Core calculation ─────────────────────────────────────────────────────
    def vdrop_calc(mat, sect):
        """
        IEC 60364-5-52 voltage drop formula.
        dU = factor × Ib × (R·cosφ + X·sinφ)   [AC]
        dU = 2 × Ib × R                          [DC]

        rho (resistivity at 70 °C):
          Cu  = 0.02363 (at 70°C) Ω·mm²/m  (~1/44 S·m/mm²)
          Al  = 0.03760 (at 70°C) Ω·mm²/m  (~1/28 S·m/mm²)
        x_l (reactance, generic):
          ≈ 0.08 mΩ/m  (suitable for common cable sections)
        """
        rho = 0.02363 if mat == "Cu" else 0.03760
        x_l = 0.08e-3   # Ω/m

        R = (rho * e_len) / sect   # total resistance [Ω]
        X = x_l * e_len            # total reactance  [Ω]

        if v_type == "DC":
            factor = 2
            cph, sph = 1.0, 0.0
            dV = factor * e_curr * R
        elif v_type == "AC 1-phase":
            factor = 2
            cph = cos_phi_val
            sph = np.sqrt(max(1.0 - cph**2, 0.0))
            dV = factor * e_curr * (R * cph + X * sph)
        else:  # AC 3-phase
            factor = np.sqrt(3)
            cph = cos_phi_val
            sph = np.sqrt(max(1.0 - cph**2, 0.0))
            dV = factor * e_curr * (R * cph + X * sph)

        pct = (dV / v_sys) * 100
        return dV, pct, factor, cph

    def req_sections(factor, cph, mat):
        """
        Minimum conductor section to stay within standard limits.
        Uses the simplified formula (reactance neglected) — conservative side.
        """
        rho = 0.02363 if mat == "Cu" else 0.03760  # 70°C operating temp
        out = {}
        for lim in [3, 5, 8]:
            lv  = (lim / 100.0) * v_sys
            # S_min = factor × Ib × rho × cosφ × L / dU_max
            req  = (factor * e_curr * rho * cph * e_len) / lv
            match = next((s for s in SECTIONS if s >= req), None)
            out[lim] = (req, f"{match} mm²" if match else "> 300 mm²")
        return out

    # ── Button & results ─────────────────────────────────────────────────────
    if st.button("CALCULATE VOLTAGE DROP", type="primary"):
        try:
            dV_a, pct_a, factor_a, cph_a = vdrop_calc(v_mat_a, e_sect_a)

            def drop_color(pct):
                if pct > 5:   return "#d32f2f"   # red
                if pct > 3:   return "#e65100"   # orange
                return "#2e7d32"                  # green

            color_a = drop_color(pct_a)

            # ── SINGLE ──────────────────────────────────────────────────────
            if mode == "Single calculation":
                c1, c2 = st.columns(2)

                with c1:
                    st.markdown(
                        f"""
                        <div class="result-card">
                            <div class="label">Voltage Drop dU</div>
                            <div class="value" style="color:{color_a};">{pct_a:.2f} %</div>
                        </div>
                        <div class="result-card">
                            <div class="label">Absolute drop</div>
                            <div class="value">{dV_a:.2f} V</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                lims = req_sections(factor_a, cph_a, v_mat_a)

                with c2:
                    st.markdown("**Min section per limit:**")
                    for lim, (req, match) in lims.items():
                        ok = "#2e7d32" if pct_a <= lim else "#e65100"
                        st.markdown(
                            f"""
                            <div class="method-row">
                                <span class="method-name">Limit {lim}%</span>
                                <span class="method-section">{match}</span>
                                <span class="method-cap" style="color:{ok};">req. {req:.2f} mm²</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                # Chart — fiecare bara e verde daca dU <= limita, rosu daca depaseste
                fig, ax = make_fig(4.5, 2)
                limits = [3, 5, 8]
                labels = ["3%", "5%", "8%"]
                bar_colors = ["#2e7d32" if pct_a <= l else "#d32f2f" for l in limits]
                ax.barh(labels, limits, color="#e0e0e0", height=0.5)
                for i, (lbl, lim, bcolor) in enumerate(zip(labels, limits, bar_colors)):
                    ax.barh(lbl, min(pct_a, lim), color=bcolor, height=0.5, alpha=0.85)
                ax.axvline(pct_a, color="#1976d2", lw=1.5, ls="--", label=f"dU = {pct_a:.2f}%")
                ax.set_xlabel("Voltage Drop [%]", fontsize=8)
                ax.set_title("Drop vs. Standard Limits", fontsize=9, fontweight="bold")
                ax.legend(fontsize=7)
                plt.tight_layout()
                st.pyplot(fig, use_container_width=False)

                # Calculation breakdown
                with st.expander("🔍 Calculation details"):
                    rho_a = 0.02363 if v_mat_a == "Cu" else 0.03760
                    R_a   = (rho_a * e_len) / e_sect_a
                    X_a   = 0.08e-3 * e_len
                    st.markdown(
                        f"""
                        | Parameter | Value |
                        |-----------|-------|
                        | ρ ({v_mat_a}) | {rho_a} Ω·mm²/m |
                        | R = ρ·L/S | {R_a:.4f} Ω |
                        | X = xₗ·L  | {X_a:.4f} Ω |
                        | cos φ     | {cos_phi_val:.2f} |
                        | sin φ     | {np.sqrt(max(1-cos_phi_val**2,0)):.3f} |
                        | dU        | {dV_a:.3f} V = **{pct_a:.2f}%** |
                        """
                    )

                add_to_history(
                    "3. Voltage Drop",
                    params={"L": f"{e_len} m", "Ib": f"{e_curr} A", "S": f"{e_sect_a} mm²", "Mat": v_mat_a, "Type": v_type},
                    results={"dU": f"{pct_a:.2f}%", "dV": f"{dV_a:.2f} V"}
                )

            # ── COMPARE ─────────────────────────────────────────────────────
            else:
                dV_b, pct_b, factor_b, cph_b = vdrop_calc(v_mat_b, e_sect_b)
                color_b = drop_color(pct_b)

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"### A — {v_mat_a} / {e_sect_a} mm²")
                    st.markdown(
                        f"""<div class="result-card">
                            <div class="label">dU</div>
                            <div class="value" style="color:{color_a};">{pct_a:.2f}% &nbsp;({dV_a:.2f} V)</div>
                        </div>""",
                        unsafe_allow_html=True
                    )
                with col_b:
                    st.markdown(f"### B — {v_mat_b} / {e_sect_b} mm²")
                    st.markdown(
                        f"""<div class="result-card">
                            <div class="label">dU</div>
                            <div class="value" style="color:{color_b};">{pct_b:.2f}% &nbsp;({dV_b:.2f} V)</div>
                        </div>""",
                        unsafe_allow_html=True
                    )

                fig, ax = make_fig(4, 2.5)
                labels = [f"A — {v_mat_a}\n{e_sect_a} mm²", f"B — {v_mat_b}\n{e_sect_b} mm²"]
                bars   = ax.bar(labels, [pct_a, pct_b], color=[color_a, color_b],
                                alpha=0.85, edgecolor="white", width=0.4)
                for bar, val in zip(bars, [pct_a, pct_b]):
                    ax.text(bar.get_x() + bar.get_width() / 2,
                            bar.get_height() + 0.05,
                            f"{val:.2f}%", ha="center", fontsize=8)
                ax.axhline(3, color="#e65100", lw=0.8, ls="--", alpha=0.7, label="3% limit")
                ax.axhline(5, color="#d32f2f", lw=0.8, ls="--", alpha=0.7, label="5% limit")
                ax.set_ylabel("dU [%]", fontsize=8)
                ax.set_title("Voltage Drop Comparison", fontsize=9, fontweight="bold")
                ax.legend(fontsize=7)
                plt.tight_layout()
                st.pyplot(fig, use_container_width=False)

                diff = abs(pct_a - pct_b)
                winner = "A" if pct_a <= pct_b else "B"
                st.info(
                    f"✅ Lower drop: **Scenario {winner}**  |  "
                    f"A = {pct_a:.2f}%  vs  B = {pct_b:.2f}%  "
                    f"(Δ = {diff:.2f}%)"
                )

        except Exception as e:
            st.error(f"Calculation error: {e}")

    show_history("3. Voltage Drop")

# ═══════════════════════════════════
# MODULE 4 — CABLE CAPACITY
# ═══════════════════════════════════
elif module == "4. Cable Capacity":
    st.markdown("# 📊 Cable Capacity (Iz)")
    st.markdown("---")
    mode = st.radio("Mode", ["Single calculation", "Compare two scenarios"], horizontal=True, label_visibility="collapsed")
    st.markdown("---")

    def capacity_inputs(suffix):
        col1, col2 = st.columns(2)
        with col1:
            sect   = st.selectbox("Cross-Section [mm²]",  SECTIONS, index=5,          key=f"sect_{suffix}")
            mat    = st.radio("Material",           ["Cu","Al"],                        key=f"mat_{suffix}",   help=tip("cu_vs_al"))
            const_ = st.radio("Cable Construction", ["Multicore","Single Wire"],        key=f"cst_{suffix}",   help=tip("construction"))
        with col2:
            ins    = st.radio("Insulation",         ["XLPE","PVC"],                     key=f"ins_{suffix}",   help=tip("xlpe_vs_pvc"))
            cond   = st.radio("Loaded Conductors",  [3, 2],                             key=f"cond_{suffix}")
        return sect, mat, const_, ins, cond

    def capacity_calc(sect, mat, const_, ins, cond):
        """Return (cap_labels, cap_vals) or raises."""
        if mat == "Al" and const_ == "Single Wire" and sect < 16:
            st.warning("Single Wire Al < 16 mm² — not permitted per DS 60364.")
            return [], []
        if mat == "Al" and const_ == "Multicore" and sect < 2.5:
            st.warning("Al < 2.5 mm² — not available.")
            return [], []
        idx     = SECTIONS.index(sect)
        methods = get_ds60364_data(ins, cond, mat, const_)
        labels, vals = [], []
        for m, v in methods.items():
            cap = v[idx]
            if cap > 0:
                labels.append(m); vals.append(cap)
        return labels, vals

    def render_capacity_rows(labels, vals):
        for m, cap in zip(labels, vals):
            st.markdown(f"""<div class="method-row">
                <span class="method-name">{m}</span>
                <span class="method-section">{cap:.1f} A</span>
                </div>""", unsafe_allow_html=True)

    if mode == "Single calculation":
        sect_a, mat_a, const_a, ins_a, cond_a = capacity_inputs("a")
        if st.button("GET CAPACITY", type="primary"):
            try:
                labels_a, vals_a = capacity_calc(sect_a, mat_a, const_a, ins_a, cond_a)
                if vals_a:
                    render_capacity_rows(labels_a, vals_a)
                    add_to_history("4. Cable Capacity",
                        params={"S": f"{sect_a}mm²","Mat": mat_a,"Ins": ins_a,"Cond": cond_a,"Constr": const_a},
                        results={labels_a[0]: f"{vals_a[0]:.1f}A", labels_a[1]: f"{vals_a[1]:.1f}A"})
                    fig, ax = make_fig(5, 2.5)
                    colors_bar = ["#1976d2","#388e3c","#f57c00","#7b1fa2","#c62828","#00838f"]
                    x_pos = np.arange(len(labels_a))
                    bars = ax.bar(x_pos, vals_a, color=colors_bar[:len(labels_a)], alpha=0.8, edgecolor="white")
                    for bar, val in zip(bars, vals_a):
                        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1, f"{val:.0f}A", ha="center", va="bottom", fontsize=7)
                    ax.set_xticks(x_pos)
                    ax.set_xticklabels([short_m(m) for m in labels_a], fontsize=7, rotation=30, ha="right")
                    ax.set_ylabel("Iz [A]", fontsize=8)
                    ax.set_title(f"Capacity — {sect_a} mm² {mat_a} {ins_a} {const_a}", fontsize=9, fontweight="bold")
                    plt.tight_layout(); st.pyplot(fig, use_container_width=False)
            except Exception as e:
                st.error(f"Error: {e}")

    else:  # Compare two scenarios
        sc1, sc2 = st.columns(2)
        with sc1:
            st.caption("Scenario A")
            sect_a, mat_a, const_a, ins_a, cond_a = capacity_inputs("a")
        with sc2:
            st.caption("Scenario B")
            sect_b, mat_b, const_b, ins_b, cond_b = capacity_inputs("b")

        if st.button("GET CAPACITY", type="primary"):
            try:
                labels_a, vals_a = capacity_calc(sect_a, mat_a, const_a, ins_a, cond_a)
                labels_b, vals_b = capacity_calc(sect_b, mat_b, const_b, ins_b, cond_b)

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"### 🅐  {mat_a} / {ins_a} / {const_a} / {sect_a} mm²")
                    render_capacity_rows(labels_a, vals_a)
                with col_b:
                    st.markdown(f"### 🅑  {mat_b} / {ins_b} / {const_b} / {sect_b} mm²")
                    render_capacity_rows(labels_b, vals_b)

                # Comparison chart — first method in common (Cable Tray / Trefoil)
                if vals_a and vals_b:
                    st.markdown("---")
                    # Build side-by-side bar chart for all methods present in both
                    methods_a = dict(zip(labels_a, vals_a))
                    methods_b = dict(zip(labels_b, vals_b))
                    all_methods = list(dict.fromkeys(list(methods_a.keys()) + list(methods_b.keys())))
                    v_a = [methods_a.get(m, 0) for m in all_methods]
                    v_b = [methods_b.get(m, 0) for m in all_methods]

                    # Shorten method labels for display
                    x_labels = [short_m(m) for m in all_methods]
                    x = np.arange(len(all_methods)); w = 0.35
                    fig, ax = make_fig(6, 2.6)
                    bars_a = ax.bar(x-w/2, v_a, w, label=f"A {mat_a}/{ins_a}/{sect_a}mm²", color="#1976d2", alpha=0.85, edgecolor="white")
                    bars_b = ax.bar(x+w/2, v_b, w, label=f"B {mat_b}/{ins_b}/{sect_b}mm²", color="#f57c00", alpha=0.85, edgecolor="white")
                    for bar, val in list(zip(bars_a, v_a)) + list(zip(bars_b, v_b)):
                        if val > 0:
                            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1, f"{val:.0f}", ha="center", fontsize=6)
                    ax.set_xticks(x); ax.set_xticklabels(x_labels, fontsize=7, rotation=30, ha="right")
                    ax.set_ylabel("Iz [A]", fontsize=8)
                    ax.set_title("Capacity Comparison", fontsize=9, fontweight="bold")
                    ax.legend(fontsize=7); plt.tight_layout(); st.pyplot(fig, use_container_width=False)

                    # Summary winner per method
                    tray_key = all_methods[0]
                    va0 = methods_a.get(tray_key, 0); vb0 = methods_b.get(tray_key, 0)
                    if va0 and vb0:
                        winner = "🅐" if va0 >= vb0 else "🅑"
                        diff   = abs(va0 - vb0)
                        st.info(f"**{tray_key}:**  🅐 {va0:.0f} A  vs  🅑 {vb0:.0f} A  —  higher capacity: {winner}  (+{diff:.0f} A)")

                    add_to_history("4. Cable Capacity",
                        params={"A": f"{mat_a}/{ins_a}/{sect_a}mm²", "B": f"{mat_b}/{ins_b}/{sect_b}mm²"},
                        results={"A_tray": f"{vals_a[0]:.0f}A", "B_tray": f"{vals_b[0]:.0f}A"})
            except Exception as e:
                st.error(f"Error: {e}")

    show_history("4. Cable Capacity")


# ═══════════════════════════════════
# MODULE 5 — PARALLEL CABLE LOAD
# ═══════════════════════════════════
elif module == "5. Parallel Cable Load":
    st.markdown("# ⚖️  Parallel Cable Load Distribution")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        i_total    = st.number_input("Total Load Current [A]", value=400.0)
        num_cables = st.number_input("Number of parallel cables", min_value=2, max_value=6, value=2)
    with col2:
        v_mat   = st.radio("Material",           ["Cu","Al"],                     help=tip("cu_vs_al"))
        v_const = st.radio("Cable Construction", ["Multicore","Single Wire"],     help=tip("construction"))
        v_ins   = st.radio("Insulation",         ["XLPE","PVC"],                  help=tip("xlpe_vs_pvc"))
        _sample = get_ds60364_data(v_ins, 3, v_mat, v_const)
        v_meth  = st.selectbox("Installation Method", list(_sample.keys()),       help=tip("install_method"))
    st.markdown("#### Cable Specifications")
    cable_inputs = []
    cols = st.columns(int(num_cables))
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"**Cable {i+1}**")
            L = st.number_input("Length [m]",   value=10.0, key=f"L_{i}", help=tip("e_len"))
            S = st.selectbox("Section [mm2]", SECTIONS, index=10, key=f"S_{i}")
            cable_inputs.append({"L": L, "S": S})
    if st.button("CALCULATE", type="primary"):
        try:
            total_G  = sum(c["S"]/c["L"] for c in cable_inputs)
            tab_vals = get_ds60364_data(v_ins, 3, v_mat, v_const)[v_meth]
            currents, max_izs, pcts = [], [], []
            for c in cable_inputs:
                i_c    = i_total * ((c["S"]/c["L"]) / total_G)
                iz_raw = tab_vals[SECTIONS.index(c["S"])]
                max_iz = iz_raw if iz_raw > 0 else float("nan")
                pct    = (i_c/max_iz)*100 if max_iz > 0 else float("nan")
                currents.append(i_c); max_izs.append(max_iz); pcts.append(pct)
            for i, (c, i_c, max_iz, pct) in enumerate(zip(cable_inputs, currents, max_izs, pcts)):
                if np.isnan(pct):
                    st.markdown(f"""<div class="method-row">
                        <span class="method-name">Cable {i+1} · {c["S"]} mm2 · {c["L"]} m</span>
                        <span class="method-section" style="color:#d32f2f">{i_c:.1f} A</span>
                        <span class="method-cap danger">Al &lt; 16 mm2 — N/A</span></div>""", unsafe_allow_html=True)
                else:
                    cls = "danger" if pct>100 else ("warn" if pct>85 else "ok")
                    status = "OVERLOADED" if pct>100 else ("HIGH" if pct>85 else "OK")
                    st.markdown(f"""<div class="method-row">
                        <span class="method-name">Cable {i+1} · {c["S"]} mm2 · {c["L"]} m</span>
                        <span class="method-section">{i_c:.1f} A</span>
                        <span class="method-cap {cls}">Max {max_iz:.0f} A · {pct:.1f}% {status}</span></div>""", unsafe_allow_html=True)
            add_to_history("5. Parallel Cable Load",
                params={"I_total": f"{i_total}A","n": int(num_cables),"Mat": v_mat,"Constr": v_const,"Method": v_meth},
                results={f"C{i+1}": f"{c:.1f}A ({p:.0f}%)" for i,(c,p) in enumerate(zip(currents,pcts)) if not np.isnan(p)})
            valid = [(c,iz,p) for c,iz,p in zip(currents,max_izs,pcts) if not np.isnan(p)]
            if valid:
                v_c, v_iz, v_p = zip(*valid)
                fig, ax = make_fig(5, 2.2); x = np.arange(len(valid)); w = 0.35
                bc = ["#d32f2f" if p>100 else "#e65100" if p>85 else "#388e3c" for p in v_p]
                ax.bar(x-w/2, v_c,  w, label="Load [A]",   color=bc,        alpha=0.85, edgecolor="white")
                ax.bar(x+w/2, v_iz, w, label="Max Iz [A]", color="#1976d2", alpha=0.5,  edgecolor="white")
                ax.set_xticks(x)
                ax.set_xticklabels([f"C{i+1}\n{cable_inputs[i]['S']} mm²" for i in range(len(valid))], fontsize=7)
                ax.set_ylabel("Current [A]", fontsize=8); ax.set_title("Load vs. Capacity", fontsize=9, fontweight="bold")
                ax.legend(fontsize=7); plt.tight_layout(); st.pyplot(fig, use_container_width=False)
        except Exception as e:
            st.error(f"Error: {e}")
    show_history("5. Parallel Cable Load")


# ═══════════════════════════════════
# MODULE 6 — CONVERTER
# ═══════════════════════════════════
elif module == "6. Converter":
    st.markdown("# 🔄 Power & Current Converter")
    st.markdown("---")
    col_s1, col_s2 = st.columns(2)
    with col_s1: v_sys = st.selectbox("System Voltage [V]", [12,24,48,230,400,690], index=4)
    with col_s2: cos_phi = st.number_input("Power Factor (cos p)", value=0.85, step=0.05, min_value=0.1, max_value=1.0, help=tip("cos_phi"))
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
        res_kva = kva_in; res_kw = kva_in*cos_phi; res_amp = (kva_in*1000)/(phase_factor*v_sys)
    elif btn_kw and kw_in > 0:
        res_kva = kw_in/cos_phi if cos_phi > 0 else 0; res_kw = kw_in; res_amp = (res_kva*1000)/(phase_factor*v_sys)
    elif btn_amp and amp_in > 0:
        res_kva = (phase_factor*v_sys*amp_in)/1000; res_kw = res_kva*cos_phi; res_amp = amp_in
    if res_kva is not None:
        st.markdown("---")
        r1, r2, r3 = st.columns(3)
        r1.markdown(f"""<div class="result-card"><div class="label">Apparent Power</div><div class="value">{res_kva:.3f} kVA</div></div>""", unsafe_allow_html=True)
        r2.markdown(f"""<div class="result-card"><div class="label">Active Power</div><div class="value ok">{res_kw:.3f} kW</div></div>""", unsafe_allow_html=True)
        r3.markdown(f"""<div class="result-card"><div class="label">Current</div><div class="value danger">{res_amp:.1f} A</div></div>""", unsafe_allow_html=True)
        add_to_history("6. Converter",
            params={"V": f"{v_sys}V","cosp": cos_phi},
            results={"S": f"{res_kva:.2f}kVA","P": f"{res_kw:.2f}kW","I": f"{res_amp:.1f}A"})
        if res_kva > 0 and res_kw > 0:
            kvar = np.sqrt(max(res_kva**2-res_kw**2, 0))
            fig, ax = make_fig(3.5, 3); ax.set_aspect("equal")
            tx=[0,res_kw,0,0]; ty=[0,0,kvar,0]
            ax.plot(tx,ty,color="#bbb",lw=1); ax.fill(tx[:3],ty[:3],alpha=0.08,color="#1976d2")
            ax.annotate("",xy=(res_kw,0),xytext=(0,0),arrowprops=dict(arrowstyle="->",color="#388e3c",lw=2))
            ax.annotate("",xy=(res_kw,kvar),xytext=(res_kw,0),arrowprops=dict(arrowstyle="->",color="#d32f2f",lw=2))
            ax.annotate("",xy=(0,kvar),xytext=(res_kw,kvar),arrowprops=dict(arrowstyle="->",color="#1976d2",lw=2.5))
            ax.text(res_kw/2,-res_kva*0.07,f"P={res_kw:.2f}kW",ha="center",color="#388e3c",fontsize=8)
            ax.text(res_kw*1.03,kvar/2,f"Q={kvar:.2f}kVAR",color="#d32f2f",fontsize=8)
            ax.text(res_kw/2-res_kva*0.08,kvar/2+res_kva*0.05,f"S={res_kva:.2f}kVA",color="#1976d2",fontsize=8,
                    rotation=np.degrees(np.arctan2(kvar,res_kw)))
            angle = np.linspace(0,np.arctan2(kvar,res_kw),40); r_arc = res_kva*0.18
            ax.plot(r_arc*np.cos(angle),r_arc*np.sin(angle),color="#999",lw=1)
            ax.text(r_arc*1.1,r_arc*0.2,f"p={np.degrees(np.arctan2(kvar,res_kw)):.1f}",color="#555",fontsize=7)
            ax.set_title("Power Triangle",fontsize=9,fontweight="bold"); ax.axis("off")
            plt.tight_layout(); st.pyplot(fig, use_container_width=False)
    show_history("6. Converter")




st.markdown("---")
st.caption("⚠️ Legal Disclaimer: This is an estimation tool and does not replace professional design software or official standards.")
