import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os

# --- CONFIGURARE PAGINA ---
st.set_page_config(page_title="DS/HD 60364 Calculator", layout="wide")

# --- BAZA DE DATE TABELE (EXACT PDF TABLES) ---
def get_ds60364_data(insulation, loaded_cond):
    if insulation == "PVC":
        if loaded_cond == 2:
            return {
                "Cable Tray (E)":        [22, 30, 40, 51, 70, 94, 119, 148, 180, 232, 282, 328, 379, 434, 514, 593],
                "In Conduit (B2)":       [16.5, 23, 30, 38, 52, 69, 90, 111, 133, 168, 201, 232, 258, 294, 344, 394],
                "Pipe in Ground (D1)":   [22, 29, 37, 46, 60, 78, 99, 119, 140, 173, 204, 231, 261, 292, 336, 379],
                "Direct in Ground (D2)": [22, 28, 38, 48, 64, 83, 110, 132, 156, 192, 230, 261, 293, 331, 382, 427]
            }
        else: 
            return {
                "Cable Tray (E)":        [18.5, 25, 34, 43, 60, 80, 101, 126, 153, 196, 238, 276, 319, 364, 430, 497],
                "In Conduit (B2)":       [15, 20, 27, 34, 46, 62, 80, 99, 118, 149, 179, 206, 225, 255, 297, 339],
                "Pipe in Ground (D1)":   [18, 24, 30, 38, 50, 64, 82, 98, 116, 143, 169, 192, 217, 243, 280, 316],
                "Direct in Ground (D2)": [19, 24, 33, 41, 54, 70, 92, 110, 130, 162, 193, 220, 246, 278, 320, 359]
            }
    else: # XLPE
        if loaded_cond == 2:
            return {
                "Cable Tray (E)":        [26, 36, 49, 63, 86, 115, 149, 185, 225, 289, 352, 410, 473, 542, 641, 741],
                "In Conduit (B2)":       [22, 30, 40, 51, 69, 91, 119, 146, 175, 221, 265, 305, 334, 384, 459, 532],
                "Pipe in Ground (D1)":   [25, 33, 43, 53, 71, 91, 116, 139, 164, 203, 239, 271, 306, 343, 395, 446],
                "Direct in Ground (D2)": [27, 35, 46, 58, 77, 100, 129, 155, 183, 225, 270, 306, 343, 387, 448, 502]
            }
        else: 
            return {
                "Cable Tray (E)":        [23, 32, 42, 54, 75, 100, 127, 158, 192, 246, 298, 346, 399, 456, 538, 621],
                "In Conduit (B2)":       [19.5, 26, 35, 44, 60, 80, 105, 128, 154, 194, 233, 268, 300, 340, 398, 455],
                "Pipe in Ground (D1)":   [21, 28, 36, 44, 58, 75, 96, 115, 135, 167, 197, 223, 251, 281, 324, 365],
                "Direct in Ground (D2)": [23, 30, 39, 49, 65, 84, 107, 129, 153, 188, 226, 257, 287, 324, 375, 419]
            }

# --- MENIU LATERAL (SIDEBAR) ---
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)

st.sidebar.title("Engineering Suite")
module = st.sidebar.radio("Navigare", [
    "1. Short Circuit", 
    "2. Cable Sizing", 
    "3. Voltage Drop & Dimensioning", 
    "4. Cable Capacity Lookup"
])

st.sidebar.markdown("---")
st.sidebar.caption("*Built and Maintained by Ionut Vieru*")

# ==========================================
# MODULE 1: SHORT CIRCUIT
# ==========================================
if module == "1. Short Circuit":
    st.header("Short Circuit at Transformer")
    
    col1, col2 = st.columns(2)
    with col1:
        u_pri = st.number_input("U_pri [kV]", value=10.0)
        i_k_pri = st.text_input("I_k_pri [kA]", value="inf")
        s_r = st.number_input("S_r [kVA]", value=1600.0)
    with col2:
        u_n = st.number_input("U_n [V]", value=400.0)
        u_k = st.number_input("u_k [%]", value=6.0)
        
    if st.button("Calculate & Show Graph"):
        try:
            IrT = (s_r * 1000) / (np.sqrt(3) * u_n)
            Ikp_s = i_k_pri.lower()
            
            ZQ = 0 if Ikp_s in ['inf', 'infinity'] else (1.05 * u_n**2) / (np.sqrt(3) * u_pri * 1000 * float(Ikp_s) * 1000)
            ZT = (u_k / 100) * (u_n**2 / (s_r * 1000))
            RT = 0.1 * ZT
            XT = np.sqrt(ZT**2 - RT**2)
            Ikmax = (1.05 * u_n) / (np.sqrt(3) * (ZQ + ZT))
            
            st.success(f"**Nominal current (IrT):** {IrT:.1f} A  \n**I_k_max'':** {Ikmax/1000:.2f} kA")
            
            # Preluare Plot
            t = np.linspace(0, 0.06, 1000)
            omega = 2 * np.pi * 50
            phi = np.arctan(XT/RT) if RT != 0 else np.pi/2
            tau = (XT/omega)/RT if RT != 0 else 0.045
            i_tot = np.sqrt(2) * Ikmax * (np.sin(omega*t - phi) + np.sin(phi) * np.exp(-t/tau))
            
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(t*1000, i_tot/1000, 'r')
            ax.axhline(0, color='black', lw=0.5)
            ax.set_title("Instantaneous Short Circuit Current [kA]")
            ax.set_xlabel("Time [ms]")
            ax.grid(True)
            
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Please check your inputs. Error: {e}")

# ==========================================
# MODULE 2: CABLE SIZING
# ==========================================
elif module == "2. Cable Sizing":
    st.header("Cable Sizing (DS/HD 60364-5-52)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        ib = st.number_input("Load Current Ib [A]:", value=160.0)
        temp = st.number_input("Ambient Temp [°C]:", value=30.0)
        k2 = st.number_input("Grouping Factor (K2):", value=1.0)
        n = st.number_input("Parallel Cables (n):", value=1, min_value=1)
    
    with col2:
        v_mat = st.radio("Material", ["Cu", "Al"])
        v_ins = st.radio("Insulation", ["XLPE", "PVC"])
        
    with col3:
        v_cond = st.radio("Loaded Conductors", [3, 2])
        v_neu = st.checkbox("Loaded Neutral (K3 = 0.86)", value=False)
        
    if st.button("Calculate Sections", type="primary"):
        try:
            k1 = 1.0
            if v_ins == "XLPE":
                if temp > 30: k1 = 0.96 if temp <= 35 else (0.91 if temp <= 40 else (0.87 if temp <= 45 else 0.82))
            else: 
                if temp > 30: k1 = 0.94 if temp <= 35 else (0.87 if temp <= 40 else (0.79 if temp <= 45 else 0.71))
            
            k3 = 0.86 if v_neu else 1.0
            k_total = k1 * k2 * k3
            
            target = ib / (k_total * n)
            mat_faktor = 1.0 if v_mat == "Cu" else 0.78
            load_per_cable = ib / n
            
            sect = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300]
            metoder = get_ds60364_data(v_ins, v_cond)
            
            out = f"**Required Iz per cable:** > {target:.1f} A | **Total Factor (K):** {k_total:.3f}\n\n"
            out += "--- \n"
            
            for m, vals in metoder.items():
                idx = next((i for i, v in enumerate(vals) if v * mat_faktor >= target), -1)
                
                if idx != -1 and idx < len(sect):
                    chosen_sect = sect[idx]
                    base_iz = vals[idx] * mat_faktor
                    actual_capacity = base_iz * k_total
                    
                    out += f"**{m:<22}:** `{chosen_sect:>4} mm²` [Cap: {actual_capacity:>5.1f} A | Load: {load_per_cable:.1f} A]\n\n"
                else:
                    out += f"**{m:<22}:** `N/A (>300 mm²)`\n\n"
            
            st.info(out)
        except Exception as e:
            st.error(f"Please check your inputs. Error: {e}")

# ==========================================
# MODULE 3: VOLTAGE DROP & DIMENSIONING
# ==========================================
elif module == "3. Voltage Drop & Dimensioning":
    st.header("Voltage Drop Calculator")
    
    col1, col2 = st.columns(2)
    with col1:
        e_len = st.number_input("Length [m]:", value=50.0)
        e_curr = st.number_input("Current Ib [A]:", value=16.0)
        e_sect = st.number_input("Test Section [mm²]:", value=2.5)
    
    with col2:
        v_mat = st.radio("Material", ["Cu", "Al"])
        v_sys = st.selectbox("System Voltage", [12, 24, 230, 400], index=2)
        
    if st.button("Calculate Voltage Drop", type="primary"):
        try:
            rho = 0.0225 if v_mat == "Cu" else 0.036
            
            if v_sys in [12, 24]:
                factor = 2
                cos_phi = 1.0
            elif v_sys == 230:
                factor = 2
                cos_phi = 0.85
            else: 
                factor = np.sqrt(3)
                cos_phi = 0.85

            dV_volts = (factor * e_len * e_curr * rho * cos_phi) / e_sect
            du_percent = (dV_volts / v_sys) * 100

            def get_required_section(target_percent):
                target_volts = (target_percent / 100.0) * v_sys
                return (factor * e_len * e_curr * rho * cos_phi) / target_volts

            s_req_3 = get_required_section(3)
            s_req_5 = get_required_section(5)
            s_req_8 = get_required_section(8)

            std_cables = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300]
            
            def match_standard(req_val):
                for cab in std_cables:
                    if cab >= req_val:
                        return f"{cab} mm²"
                return ">300 mm²"

            out =  f"### ANALYSIS FOR {e_sect} mm² ({v_mat}) AT {v_sys}V\n"
            out += f"**Voltage Drop (dU):** `{du_percent:.2f} %`  ({dV_volts:.2f} V)\n\n"
            
            out += f"### RECOMMENDED SECTIONS FOR MAX LIMITS\n"
            out += f"- **Limit 3% :** Req. {s_req_3:>6.2f} mm² -> Use: **{match_standard(s_req_3)}**\n"
            out += f"- **Limit 5% :** Req. {s_req_5:>6.2f} mm² -> Use: **{match_standard(s_req_5)}**\n"
            out += f"- **Limit 8% :** Req. {s_req_8:>6.2f} mm² -> Use: **{match_standard(s_req_8)}**\n"
            
            st.success(out)

        except Exception as e:
            st.error(f"Please check your inputs. Error: {e}")

# ==========================================
# MODULE 4: CABLE CAPACITY LOOKUP
# ==========================================
elif module == "4. Cable Capacity Lookup":
    st.header("Cable Capacity Lookup (DS 60364)")
    
    sections_list = [1.5, 2.5, 4.0, 6.0, 10.0, 16.0, 25.0, 35.0, 50.0, 70.0, 95.0, 120.0, 150.0, 185.0, 240.0, 300.0]
    
    col1, col2 = st.columns(2)
    with col1:
        selected_section = st.selectbox("Cross-Section [mm²]:", sections_list, index=5)
        v_mat = st.radio("Material", ["Cu", "Al"])
        
    with col2:
        v_ins = st.radio("Insulation", ["XLPE", "PVC"])
        v_cond = st.radio("Loaded Conductors", [3, 2])
        
    if st.button("Get Max Capacity", type="primary"):
        try:
            idx = sections_list.index(selected_section)

            metoder = get_ds60364_data(v_ins, v_cond)
            mat_faktor = 1.0 if v_mat == "Cu" else 0.78
            
            warning = ""
            if v_mat == "Al" and selected_section < 16:
                warning = "\n*(Note: Al conductors < 16mm² are rarely allowed)*\n"

            out = f"### Max Capacity (Iz) | {selected_section} mm² {v_mat} | {v_ins} | {v_cond}-Cond\n"
            out += warning + "\n"
            out += "--- \n"
            for m, vals in metoder.items():
                out += f"**{m:<24}:** `{vals[idx] * mat_faktor:.1f} A`\n\n"

            st.info(out)

        except Exception as e:
            st.error(f"Could not fetch capacity. Error: {e}")