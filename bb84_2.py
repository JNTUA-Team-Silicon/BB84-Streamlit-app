# BB84 Quantum Key Distribution Simulator - Main Application
# REFACTORED FOR BEST PRACTICES
# University: Jawaharlal Nehru Technological University Anantapur
# Department: Electronics and Communication Engineering
# Project: AQVH FINAL - BB84 QKD Simulator

# IMPORTS - ORGANIZED BY CATEGORY (MUST BE FIRST)

import streamlit as st
import io
import base64
import hashlib
import time
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from matplotlib.patches import Patch
import logging

# Optional: ReportLab for PDF generation (graceful fallback)
REPORTLAB_AVAILABLE = False
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_bloch_multivector
from qiskit_aer import AerSimulator
from qiskit import transpile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PAGE CONFIG - MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="JNTUA BB84 Quantum Key Distribution Simulator - QKD Protocol",
    page_icon="jntua_logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# GPU BACKEND DETECTION (MUST BE BEFORE SESSION INIT)
@st.cache_resource
def get_quantum_backend():
    """Auto-detect GPU, fallback to CPU"""
    try:
        from qiskit_aer_gpu_simulator import AerSimulator as GPUSimulator
        logger.info("🟢 GPU Backend Available")
        return GPUSimulator(device='GPU'), True
    except ImportError:
        logger.info("🟡 GPU Backend Not Available - Using CPU")
        return AerSimulator(), False

# CUSTOM STYLING - PROFESSIONAL THEME WITH VIBRANT COLORS
def inject_custom_css():
    """Inject custom CSS for professional styling"""
    try:
        st.write("""
        <style>
        h1 { color: #2563eb !important; font-weight: 800 !important; }
        h2 { color: #1e40af !important; margin-top: 30px !important; font-weight: 700 !important; }
        h3 { color: #2563eb !important; font-weight: 600 !important; }
        .stButton > button { background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important; color: white !important; font-weight: 700; text-transform: uppercase; }
        </style>
        """, unsafe_allow_html=True)
    except Exception:
        pass

# Local Modules - Configuration & Utilities
import bb84_config as config
from bb84_simulator import BB84Simulator
from bb84_utils import (
    create_transmission_timeline,
    compute_metrics,
    analyze_error_patterns,
    calculate_key_rate,
    get_basis_distribution,
    get_bit_distribution,
    calculate_eve_impact
)
from bb84_visualizations import (
    plot_pdf_style_timeline,
    plotly_bit_timeline,
    plotly_error_timeline,
    qber_gauge,
    decision_line,
    plotly_bloch_sphere,
    create_pdf_report_with_graphs,
)

# SESSION STATE INITIALIZATION - MODULE LEVEL (BEFORE ANY FUNCTIONS)
# This initializes all session state ONCE when the app starts
# Prevents "SessionInfo before it was initialized" errors

def _initialize_session_state():
    """Initialize ALL session state variables - IDEMPOTENT"""
    # Simulation parameters
    st.session_state.setdefault("num_bits", config.DEFAULT_QUBITS)
    st.session_state.setdefault("threshold", config.DEFAULT_QBER_THRESHOLD)
    st.session_state.setdefault("eve_prob", config.DEFAULT_EVE_PROB)
    st.session_state.setdefault("eve_attack", "Intercept-Resend")
    st.session_state.setdefault("noise_prob", config.DEFAULT_NOISE_PROB)
    st.session_state.setdefault("window", config.DEFAULT_WINDOW_SIZE)
    st.session_state.setdefault("pdf_max", config.DEFAULT_PDF_MAX_BITS)
    st.session_state.setdefault("sifted_display_size", config.DEFAULT_SIFTED_DISPLAY_SIZE)

    # Simulation control flags
    st.session_state.setdefault("simulation_run", False)
    st.session_state.setdefault("simulation_completed", False)
    st.session_state.setdefault("simulation_in_progress", False)

    # Simulation results (CACHED - reused across reruns)
    st.session_state.setdefault("sim_results", None)
    st.session_state.setdefault("alice_bits_stored", None)
    st.session_state.setdefault("alice_bases_stored", None)
    st.session_state.setdefault("bob_bases_stored", None)

    # UI state for fragments
    st.session_state.setdefault("bloch_single_idx", 0)
    st.session_state.setdefault("bloch_range_start", 0)
    st.session_state.setdefault("bloch_range_end", 10)
    st.session_state.setdefault("timeline_range_no_start", 0)
    st.session_state.setdefault("timeline_range_no_end", 0)
    st.session_state.setdefault("timeline_range_eve_start", 0)
    st.session_state.setdefault("timeline_range_eve_end", 0)

    # Cached visualization objects
    st.session_state.setdefault("cached_figures", {})
    st.session_state.setdefault("cached_pdf_bytes", None)

# SIMULATION ENGINE - RUN ONLY ON BUTTON PRESS

def run_bb84_simulation():
    """
    Execute the BB84 quantum simulation.
    Called ONLY when "Run Simulation" button is pressed.
    Results cached in st.session_state.
    Prevents simultaneous runs with simulation_in_progress flag.
    """
    # Prevent simultaneous simulation runs
    if st.session_state.get("simulation_in_progress", False):
        st.warning("Simulation already running. Please wait for it to complete.")
        return
    
    # Set lock
    st.session_state.simulation_in_progress = True
    
    try:
        num_bits = st.session_state.num_bits
        threshold = st.session_state.threshold
        eve_prob = st.session_state.eve_prob
        eve_attack = st.session_state.eve_attack
        noise_prob = st.session_state.noise_prob
        window = st.session_state.window

        with st.spinner("Running BB84 Quantum Simulation..."):
            progress_bar = st.progress(0)
            progress_bar.progress(25, text="Initializing quantum simulator...")

            sim = BB84Simulator()
            
            # Generate random bits and bases for Alice and Bob
            alice_bits = np.random.randint(0, 2, num_bits)
            alice_bases = np.random.randint(0, 2, num_bits)
            bob_bases = np.random.randint(0, 2, num_bits)
            
            # Store in session state for use in visualizations
            st.session_state.alice_bits_stored = alice_bits
            st.session_state.alice_bases_stored = alice_bases
            st.session_state.bob_bases_stored = bob_bases

            progress_bar.progress(50, text="Simulating quantum transmission...")
            
            # Simulate both scenarios
            bob_no_eve, eve_results_no = sim.simulate_transmission(
                alice_bits, alice_bases, bob_bases, 
                eve_present=False, noise_prob=noise_prob
            )
            bob_eve, eve_results_eve = sim.simulate_transmission(
                alice_bits, alice_bases, bob_bases, 
                eve_present=True, eve_intercept_prob=eve_prob, noise_prob=noise_prob
            )
            
            progress_bar.progress(75, text="Analyzing results...")

            # Compute timelines and metrics
            def compute_scenario(bob_results):
                """Compute metrics for a scenario"""
                timeline = create_transmission_timeline(alice_bits, alice_bases, bob_bases, bob_results)
                used = timeline[timeline["Used"] == True]
                
                errors = int(np.sum(used["Error"].values))
                qber = errors / len(used) if len(used) > 0 else 0.0
                sec = sim.assess_security(float(qber), float(threshold))
                
                sifted_key = used["AliceBit"].astype(int).tolist()
                final_key = sim.privacy_amplification(sifted_key, qber) if sec['status'] == "SECURE" else []

                return {
                    'timeline': timeline,
                    'errors': errors,
                'qber': qber,
                'status': sec['status'],
                'sifted_count': len(used),
                'final_key_length': len(final_key),
                'final_key': final_key
            }

        no_eve_results = compute_scenario(bob_no_eve)
        eve_results = compute_scenario(bob_eve)

        # Store all results in session state for reuse
        st.session_state.sim_results = {
            'no_eve': no_eve_results,
            'eve': eve_results,
            'bob_no_eve': bob_no_eve,
            'bob_eve': bob_eve,
            'eve_eavesdropper_results_no': eve_results_no,
            'eve_eavesdropper_results_eve': eve_results_eve,
            'parameters': {
                'num_bits': num_bits,
                'threshold': threshold,
                'eve_prob': eve_prob,
                'eve_attack': eve_attack,
                'noise_prob': noise_prob,
                'window': window
            }
        }

        progress_bar.empty()
        st.success("Simulation completed successfully!")
        st.session_state.simulation_completed = True
    
    finally:
        # Always release the lock, even if error occurs
        st.session_state.simulation_in_progress = False

@st.fragment
def render_final_key_download():
    """Display and download final keys. UI-only, reads from session_state."""
    if not st.session_state.get("simulation_completed", False):
        st.info("Run simulation to see final keys.")
        return
    
    if st.session_state.sim_results is None:
        st.info("Run simulation to see final keys.")
        return

    no_eve = st.session_state.sim_results['no_eve']
    eve = st.session_state.sim_results['eve']

    st.markdown("### Final Secure Keys")
    
    key_col1, key_col2 = st.columns(2)
    
    with key_col1:
        st.markdown("**No Eve Scenario Key:**")
        if no_eve['final_key_length'] > 0:
            key_no_str = ''.join(map(str, no_eve['final_key']))
            st.code(key_no_str[:100] + "..." if len(key_no_str) > 100 else key_no_str, language="text")
            st.caption(f"Length: {len(key_no_str)} bits | Status: {no_eve['status']}")
        else:
            st.warning("No secure key generated.")
    
    with key_col2:
        st.markdown("**With Eve Scenario Key:**")
        if eve['final_key_length'] > 0:
            key_eve_str = ''.join(map(str, eve['final_key']))
            st.code(key_eve_str[:100] + "..." if len(key_eve_str) > 100 else key_eve_str, language="text")
            st.caption(f"Length: {len(key_eve_str)} bits | Status: {eve['status']}")
        else:
            st.error("No secure key generated due to eavesdropping.")
    
    # Download buttons
    st.markdown("---")
    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        if no_eve['final_key_length'] > 0:
            key_no_bytes = ''.join(map(str, no_eve['final_key'])).encode('utf-8')
            st.download_button(
                label=" **Download No Eve Key**",
                data=key_no_bytes,
                file_name="bb84_no_eve_key.txt",
                mime="text/plain",
                help="Download the secure key for No Eve scenario"
            )
    with dl_col2:
        if eve['final_key_length'] > 0:
            key_eve_bytes = ''.join(map(str, eve['final_key'])).encode('utf-8')
            st.download_button(
                label=" **Download With Eve Key**",
                data=key_eve_bytes,
                file_name="bb84_with_eve_key.txt",
                mime="text/plain",
                help="Download the secure key for With Eve scenario"
            )

# FRAGMENT FUNCTIONS - UI ONLY, READ FROM SESSION STATE

@st.fragment
def render_metrics_display():
    """Display main metrics. UI-only, reads from session_state."""
    # Fragment safety guard
    if not st.session_state.get("simulation_completed", False):
        st.info("Run simulation to see metrics.")
        return
    
    if st.session_state.sim_results is None:
        st.info("Run simulation to see metrics.")
        return

    no_eve = st.session_state.sim_results['no_eve']
    eve = st.session_state.sim_results['eve']
    num_bits = st.session_state.sim_results['parameters']['num_bits']

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(" **No Eavesdropper Scenario**")
        st.metric(" Transmitted Qubits", num_bits)
        st.metric(" Sifted Bits", no_eve['sifted_count'])
        st.metric(" Errors Detected", no_eve['errors'])
        st.metric(" QBER", f"{no_eve['qber']:.4f}")
        st.metric(" Final Secure Key", no_eve['final_key_length'])
        st.metric("⟱ Key Rate", f"{no_eve['final_key_length'] / num_bits:.4f}")
        st.plotly_chart(
            qber_gauge(no_eve['qber'], st.session_state.threshold),
            use_container_width=True,
            key="gauge_no_metric"
        )

    with col2:
        st.subheader(" **Eavesdropper Present Scenario**")
        st.metric(" Transmitted Qubits", num_bits)
        st.metric(" Sifted Bits", eve['sifted_count'])
        st.metric(" Errors Detected", eve['errors'])
        st.metric(" QBER", f"{eve['qber']:.4f}")
        st.metric(" Final Secure Key", eve['final_key_length'])
        st.metric("⟱ Key Rate", f"{eve['final_key_length'] / num_bits:.4f}")
        st.plotly_chart(
            qber_gauge(eve['qber'], st.session_state.threshold),
            use_container_width=True,
            key="gauge_e_metric"
        )


@st.fragment
def render_error_analysis():
    """Display error analysis. UI-only."""
    if not st.session_state.simulation_completed or st.session_state.sim_results is None:
        st.info("⏳ Run simulation to see error analysis.")
        return

    no_eve = st.session_state.sim_results['no_eve']
    eve = st.session_state.sim_results['eve']

    st.markdown("---")
    st.markdown("### Detailed Performance Metrics")
    det_col1, det_col2 = st.columns(2)
    
    with det_col1:
        st.markdown("**No Eve:**")
        num_bits = st.session_state.sim_results['parameters']['num_bits']
        st.info(f"• Efficiency: {no_eve['sifted_count']/num_bits:.1%}\n• Security: {no_eve['status']}\n• Key Rate: {no_eve['final_key_length']/num_bits:.3f}")
    
    with det_col2:
        st.markdown("**With Eve:**")
        st.info(f"• Efficiency: {eve['sifted_count']/num_bits:.1%}\n• Security: {eve['status']}\n• Key Rate: {eve['final_key_length']/num_bits:.3f}")

    st.markdown("---")
    st.markdown("### Error Pattern Analysis")
    err_col1, err_col2 = st.columns(2)
    
    with err_col1:
        st.markdown("**No Eve Error Distribution:**")
        if no_eve['errors'] > 0:
            error_indices = no_eve['timeline'][no_eve['timeline']['Error']==True]['BitIndex'].tolist()[:10]
            st.warning(f"Errors found at positions: {error_indices}...")
        else:
            st.success("No errors detected!")
    
    with err_col2:
        st.markdown("**With Eve Error Distribution:**")
        if eve['errors'] > 0:
            error_indices = eve['timeline'][eve['timeline']['Error']==True]['BitIndex'].tolist()[:10]
            st.error(f"Errors found at positions: {error_indices}...")
        else:
            st.info("Unexpected: No errors with Eve present")


@st.fragment
def render_sifted_key_display():
    """Display sifted key comparison. UI-only."""
    if not st.session_state.simulation_completed or st.session_state.sim_results is None:
        st.info("Run simulation to see sifted keys.")
        return

    no_eve = st.session_state.sim_results['no_eve']
    eve = st.session_state.sim_results['eve']
    sifted_display_size = st.session_state.sifted_display_size

    st.markdown("### Sifted Bits Comparison")
    col_no, col_e = st.columns(2)
    
    with col_no:
        st.markdown(f"**No Eve (First {min(sifted_display_size, no_eve['sifted_count'])} Sifted Bits):**")
        if no_eve['sifted_count'] > 0:
            show_n = min(sifted_display_size, no_eve['sifted_count'])
            used_no = no_eve['timeline'][no_eve['timeline']["Used"] == True]
            df_no = pd.DataFrame({
                "Alice": used_no["AliceBit"].iloc[:show_n].values,
                "Bob": used_no["BobResult"].iloc[:show_n].values,
                "Match": used_no["Error"].iloc[:show_n].apply(lambda x: not x).values
            })
            st.dataframe(df_no, key="sifted_df_no", use_container_width=True)
        else:
            st.info("No sifted bits.")

    with col_e:
        st.markdown(f"**With Eve (First {min(sifted_display_size, eve['sifted_count'])} Sifted Bits):**")
        if eve['sifted_count'] > 0:
            show_n = min(sifted_display_size, eve['sifted_count'])
            used_e = eve['timeline'][eve['timeline']["Used"] == True]
            df_e = pd.DataFrame({
                "Alice": used_e["AliceBit"].iloc[:show_n].values,
                "Bob": used_e["BobResult"].iloc[:show_n].values,
                "Match": used_e["Error"].iloc[:show_n].apply(lambda x: not x).values
            })
            st.dataframe(df_e, key="sifted_df_e", use_container_width=True)
        else:
            st.info("No sifted bits.")

    st.plotly_chart(
        decision_line(eve['qber'], st.session_state.threshold, "**Attack Detection Decision Analysis**"),
        use_container_width=True,
        key="dec_line_chart"
    )


@st.fragment
def render_timeline_analysis():
    """Display timeline visualizations. UI-only."""
    if not st.session_state.simulation_completed or st.session_state.sim_results is None:
        st.info("Run simulation to see timelines.")
        return

    no_eve = st.session_state.sim_results['no_eve']
    eve = st.session_state.sim_results['eve']
    pdf_max = st.session_state.pdf_max

    st.markdown("### Timeline Analysis")
    
    viz_col1, viz_col2 = st.columns(2)
    with viz_col1:
        show_pdf = st.checkbox(" **PDF Style Timeline**", value=True)
    with viz_col2:
        show_plotly = st.checkbox(" **Interactive Plotly Timeline**", value=True)

    tl_col1, tl_col2 = st.columns(2)
    
    with tl_col1:
        st.subheader(" **No Eavesdropper Scenario**")
        if show_pdf:
            try:
                fig_pdf_no = plot_pdf_style_timeline(
                    no_eve['timeline'], 
                    title="No Eve Scenario", 
                    max_bits=pdf_max, 
                    color_scheme='blue'
                )
                st.pyplot(fig_pdf_no, use_container_width=True)
            except Exception as e:
                st.error(f"Error displaying timeline: {e}")
        
        if show_plotly:
            st.markdown("---")
            st.subheader("Plotly Timeline (Interactive)")
            max_no = len(no_eve['timeline']) - 1
            if st.session_state.timeline_range_no_end == 0:
                st.session_state.timeline_range_no_end = min(max_no, 100)
            
            saved_start_no = min(st.session_state.timeline_range_no_start, max_no)
            saved_end_no = min(st.session_state.timeline_range_no_end, max_no)
            start_no, end_no = st.slider(
                "Select range", 0, max_no, 
                value=(saved_start_no, saved_end_no), 
                key="range_no_slider_key"
            )

            st.plotly_chart(
                plotly_bit_timeline(no_eve['timeline'], start_no, end_no, title="No Eve - Plotly Timeline"),
                use_container_width=True,
                key="plotly_timeline_no"
            )
            st.plotly_chart(
                plotly_error_timeline(no_eve['timeline'], start_no, end_no, title="No Eve - Error Timeline"),
                use_container_width=True,
                key="plotly_err_no"
            )

    with tl_col2:
        st.subheader(" **Eavesdropper Present Scenario**")
        if show_pdf:
            try:
                fig_pdf_e = plot_pdf_style_timeline(
                    eve['timeline'], 
                    title="With Eve Scenario", 
                    max_bits=pdf_max, 
                    color_scheme='red'
                )
                st.pyplot(fig_pdf_e, use_container_width=True)
            except Exception as e:
                st.error(f"Error displaying timeline: {e}")
        
        if show_plotly:
            st.markdown("---")
            st.subheader("Plotly Timeline (Interactive)")
            max_e = len(eve['timeline']) - 1
            if st.session_state.timeline_range_eve_end == 0:
                st.session_state.timeline_range_eve_end = min(max_e, 100)
            
            saved_start_e = min(st.session_state.timeline_range_eve_start, max_e)
            saved_end_e = min(st.session_state.timeline_range_eve_end, max_e)
            start_e, end_e = st.slider(
                "Select range", 0, max_e, 
                value=(saved_start_e, saved_end_e), 
                key="range_e_slider_key"
            )

            st.plotly_chart(
                plotly_bit_timeline(eve['timeline'], start_e, end_e, title="With Eve - Plotly Timeline"),
                use_container_width=True,
                key="plotly_timeline_e"
            )
            st.plotly_chart(
                plotly_error_timeline(eve['timeline'], start_e, end_e, title="With Eve - Error Timeline"),
                use_container_width=True,
                key="plotly_err_e"
            )


@st.fragment
def render_bloch_visualizations():
    """Display Bloch sphere visualizations. UI-only."""
    if not st.session_state.simulation_completed:
        st.info("Run simulation to see Bloch spheres.")
        return

    if (st.session_state.alice_bits_stored is None or 
        st.session_state.alice_bases_stored is None):
        st.warning("Quantum states not available.")
        return

    st.markdown("### Quantum Visualization")
    
    qv_tab1, qv_tab2, qv_tab3 = st.tabs(["Single Qubit Analysis", "Multi-Qubit Comparison", "Polarization Analysis"])

    with qv_tab1:
        st.subheader("Single Qubit Quantum State Analysis")
        bits_array = st.session_state.alice_bits_stored
        bases_array = st.session_state.alice_bases_stored
        max_idx = len(bits_array) - 1
        
        idx = st.slider(
            "**Select Qubit Index**", 
            0, max_idx, 
            value=min(st.session_state.bloch_single_idx, max_idx),
            key="bloch_single_idx_slider"
        )
        st.session_state.bloch_single_idx = idx

        bit = int(bits_array[idx])
        basis = int(bases_array[idx])
        sv = BB84Simulator.get_statevector_from_bit_basis(bit, basis)
        
        state_col1, state_col2 = st.columns([1, 2])
        with state_col1:
            st.markdown(f"""
```
State: {BB84Simulator.state_label(bit, basis)}
Bit: {bit}
Basis: {'Z (Rectilinear)' if basis == 0 else 'X (Diagonal)'}
```
""")
        with state_col2:
            try:
                st.plotly_chart(plotly_bloch_sphere([sv]), use_container_width=True)
            except Exception as e:
                st.error(f"Error displaying Bloch sphere: {e}")

    with qv_tab2:
        st.subheader("Multi-Qubit Range Analysis")
        bits_array = st.session_state.alice_bits_stored
        bases_array = st.session_state.alice_bases_stored
        max_idx = len(bits_array) - 1
        
        start, end = st.slider(
            "**Select Qubit Range**",
            0, max_idx,
            value=(min(st.session_state.bloch_range_start, max_idx), 
                   min(st.session_state.bloch_range_end, max_idx)),
            key="bloch_range_slider"
        )
        st.session_state.bloch_range_start = start
        st.session_state.bloch_range_end = end

        states = []
        state_info = []
        for i in range(start, end + 1):
            if i < len(bits_array):
                bit = int(bits_array[i])
                basis = int(bases_array[i])
                sv = BB84Simulator.get_statevector_from_bit_basis(bit, basis)
                states.append(sv)
                state_info.append(f"Qubit {i}: {BB84Simulator.state_label(bit, basis)}")

        st.markdown("**Quantum States in Range:**")
        for info in state_info:
            st.markdown(f"• {info}")

        try:
            st.markdown("**3D Bloch Sphere Multi-State View:**")
            st.plotly_chart(plotly_bloch_sphere(states), use_container_width=True)
        except Exception as e:
            st.error(f"Error displaying multi-qubit Bloch sphere: {e}")

    with qv_tab3:
        st.subheader("Polarization Analysis")
        pol_col1, pol_col2 = st.columns(2)
        
        with pol_col1:
            st.markdown("**Rectilinear Polarization (Z-Basis)**")
            st.markdown("• **|0 (North)**: Horizontal\n• **|1 (South)**: Vertical")
            try:
                sv0 = Statevector.from_label('0')
                sv1 = Statevector.from_label('1')
                st.plotly_chart(plotly_bloch_sphere([sv0, sv1]), use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")
            
            bases_array = st.session_state.alice_bases_stored
            bits_array = st.session_state.alice_bits_stored
            z_bits = [i for i, b in enumerate(bases_array) if b == 0]
            z_0 = sum(1 for i in z_bits if bits_array[i] == 0)
            z_1 = sum(1 for i in z_bits if bits_array[i] == 1)
            st.markdown(f"**Bits in Z-Basis:** {len(z_bits)} (|0: {z_0}, |1: {z_1})")

        with pol_col2:
            st.markdown("**Diagonal Polarization (X-Basis)**")
            st.markdown("• **|+ (East)**: Superposition\n• **|- (West)**: Superposition")
            try:
                sv_plus = Statevector([1/np.sqrt(2), 1/np.sqrt(2)])
                sv_minus = Statevector([1/np.sqrt(2), -1/np.sqrt(2)])
                st.plotly_chart(plotly_bloch_sphere([sv_plus, sv_minus]), use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")
            
            x_bits = [i for i, b in enumerate(bases_array) if b == 1]
            x_plus = sum(1 for i in x_bits if bits_array[i] == 0)
            x_minus = sum(1 for i in x_bits if bits_array[i] == 1)
            st.markdown(f"**Bits in X-Basis:** {len(x_bits)} (|+: {x_plus}, |-: {x_minus})")


# PDF REPORT GENERATION - WITH CACHING

@st.cache_data(ttl=3600)
def generate_pdf_report_bytes(
    project_info_tuple,
    summary_tuple,
    timeline_csv_no_eve,
    timeline_csv_eve,
    num_bits,
    sift_no, key_no, qber_no,
    sift_e, key_e, qber_e,
    threshold,
    pdf_max_bits
):
    """Generate PDF bytes. Cached to avoid recomputation."""
    project_info_dict = dict(project_info_tuple)
    summary_dict = dict(summary_tuple)
    
    return create_pdf_report_with_graphs(
        project_info=project_info_tuple,
        summary=summary_tuple,
        timeline_df_no_eve_csv=timeline_csv_no_eve,
        timeline_df_eve_csv=timeline_csv_eve,
        num_bits=num_bits,
        sift_no=sift_no, key_no=key_no, qber_no=qber_no,
        sift_e=sift_e, key_e=key_e, qber_e=qber_e,
        threshold=threshold,
        pdf_max_bits=pdf_max_bits
    )


@st.fragment
def render_report_downloads():
    """Display report generation and downloads. UI-only."""
    if not st.session_state.simulation_completed or st.session_state.sim_results is None:
        st.info("⏳ Run simulation to generate reports.")
        return

    st.markdown("### Professional Report Generation")

    no_eve = st.session_state.sim_results['no_eve']
    eve = st.session_state.sim_results['eve']
    params = st.session_state.sim_results['parameters']

    report_col1, report_col2, report_col3 = st.columns(3)
    with report_col1:
        include_charts = st.checkbox(" **Include Charts**", value=True)
    with report_col2:
        include_timeline = st.checkbox(" **Include Timeline**", value=True)
    with report_col3:
        detailed_analysis = st.checkbox(" **Detailed Analysis**", value=True)

    st.markdown("---")
    st.subheader("Report Downloads")

    project_info = {
        "University": "JNTUA",
        "College": "JNTUACEA",
        "Department": "ECE",
        "Project": "AQVH FINAL: BB84 QKD Simulator",
        "Team": "Team Silicon",
        "Generated On": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "Total Qubits": params['num_bits'],
        "Eve Probability": params['eve_prob'],
        "Eve Attack": params['eve_attack'],
        "Noise Probability": params['noise_prob'],
        "QBER Threshold": params['threshold']
    }

    summary = {
        "No Eve QBER": f"{no_eve['qber']:.4f}",
        "No Eve Errors": no_eve['errors'],
        "No Eve Key": no_eve['final_key_length'],
        "With Eve QBER": f"{eve['qber']:.4f}",
        "With Eve Errors": eve['errors'],
        "With Eve Key": eve['final_key_length']
    }

    # Generate PDF with caching
    project_info_tuple = tuple(sorted(project_info.items()))
    summary_tuple = tuple(sorted(summary.items()))
    timeline_csv_no_eve = no_eve['timeline'].to_csv(index=False)
    timeline_csv_eve = eve['timeline'].to_csv(index=False)

    pdf_bytes = generate_pdf_report_bytes(
        project_info_tuple,
        summary_tuple,
        timeline_csv_no_eve,
        timeline_csv_eve,
        params['num_bits'],
        no_eve['sifted_count'], no_eve['final_key_length'], no_eve['qber'],
        eve['sifted_count'], eve['final_key_length'], eve['qber'],
        params['threshold'],
        st.session_state.pdf_max
    )

    dl_col1, dl_col2, dl_col3 = st.columns(3)
    
    with dl_col1:
        st.download_button(
            " **CSV: No Eve Data**",
            data=timeline_csv_no_eve.encode("utf-8"),
            file_name="AQVH_No_Eve_Timeline.csv",
            mime="text/csv",
            help="Download detailed timeline data for secure channel"
        )
    
    with dl_col2:
        st.download_button(
            " **CSV: With Eve Data**",
            data=timeline_csv_eve.encode("utf-8"),
            file_name="AQVH_With_Eve_Timeline.csv",
            mime="text/csv",
            help="Download detailed timeline data for compromised channel"
        )
    
    with dl_col3:
        st.download_button(
            " **PDF Full Report**",
            data=pdf_bytes,
            file_name="AQVH_FINAL_BB84_Report.pdf",
            mime="application/pdf",
            help="Download comprehensive PDF report with all analysis"
        )


# MAIN APPLICATION

def render_footer():
    """Render professional footer with social media logos and developer links"""
    try:
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); border-radius: 10px; border-top: 3px solid #2563eb;'>
            
            <!-- Developer Info -->
            <p style='font-size: 16px; color: #1e40af; font-weight: 700; margin: 10px 0;'>
            <strong>Developed by Keerthan V S and Team</strong>
            </p>
            <p style='font-size: 13px; color: #666; margin: 5px 0;'>
            Team Silicon | JNTUACEA ECE Department | Anantapur
            </p>
            
            <!-- Social Media Links with Icons -->
            <div style='margin: 20px 0; display: flex; justify-content: center; gap: 25px; align-items: center;'>
            
            <!-- GitHub -->
            <a href='https://github.com/keer999' target='_blank' style='text-decoration: none; display: flex; flex-direction: column; align-items: center; gap: 5px;'>
                <svg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 24 24' fill='#333' style='filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); transition: transform 0.2s;' onmouseover='this.style.transform="scale(1.15)"' onmouseout='this.style.transform="scale(1)"'>
                    <path d='M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v 3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z'/>
                </svg>
                <span style='font-size: 12px; color: #333; font-weight: 600;'>GitHub</span>
            </a>
            
            <!-- LinkedIn -->
            <a href='https://www.linkedin.com/in/keerthan-vs' target='_blank' style='text-decoration: none; display: flex; flex-direction: column; align-items: center; gap: 5px;'>
                <svg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 24 24' fill='#0A66C2' style='filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); transition: transform 0.2s;' onmouseover='this.style.transform="scale(1.15)"' onmouseout='this.style.transform="scale(1)"'>
                    <path d='M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.225 0z'/>
                </svg>
                <span style='font-size: 12px; color: #0A66C2; font-weight: 600;'>LinkedIn</span>
            </a>
            
            <!-- Email -->
            <a href='mailto:keerthanroyal8@gmail.com' style='text-decoration: none; display: flex; flex-direction: column; align-items: center; gap: 5px;'>
                <svg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 24 24' fill='#EA4335' style='filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); transition: transform 0.2s;' onmouseover='this.style.transform="scale(1.15)"' onmouseout='this.style.transform="scale(1)"'>
                    <path d='M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z'/>
                </svg>
                <span style='font-size: 12px; color: #EA4335; font-weight: 600;'>Email</span>
            </a>
            
            </div>
            
            <!-- Footer Text -->
            <p style='font-size: 12px; color: #999; margin-top: 15px; border-top: 1px solid #e0e0e0; padding-top: 15px;'>
            © 2026 BB84 Quantum Key Distribution Simulator | AQVH Final Project | All Rights Reserved
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception:
        # Fallback to simple markdown if HTML rendering fails silently
        st.markdown("---")
        st.markdown("""
        **Developed by Keerthan V S and Team** | Team Silicon | JNTUA ECE Department
        
        [GitHub](https://github.com/keer999) • [LinkedIn](https://www.linkedin.com/in/keerthan-vs) • [Email](mailto:keerthanroyal8@gmail.com)
        """)

# MAIN APPLICATION

def main():
    """Main Streamlit application entry point"""
    
    # CRITICAL: INITIALIZE SESSION STATE FIRST
    # This must be the absolute first operation to prevent SessionInfo errors
    _initialize_session_state()
    
    # HEADER SECTION - PURE STREAMLIT COMPONENTS (NO HTML)
    st.title("BB84 Quantum Key Distribution Simulator")
    st.markdown("Interactive Quantum Cryptography Learning & Research Platform", help=None)
    
    # INJECT CSS AFTER HEADER
    inject_custom_css()
    
    # Platform features card - PURE STREAMLIT
    st.subheader("Platform Capabilities")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Simulation:** Complete BB84 protocol execution")
        st.markdown("**Security:** Eavesdropper detection via QBER")
        st.markdown("**Analysis:** Timeline & comparative metrics")
    with col2:
        st.markdown("**Visualization:** Bloch sphere quantum states")
        st.markdown("**Reports:** PDF export with full analysis")
        st.markdown("**Education:** Interactive learning platform")
    
    # System status badge - PURE STREAMLIT
    st.success("System Ready - Configure parameters and click Run BB84 Simulation to begin")
    
    # Display GPU Backend Status - PURE STREAMLIT
    try:
        backend, gpu_available = get_quantum_backend()
        if gpu_available:
            st.success("GPU Acceleration Enabled - Using CUDA GPU for quantum simulations")
        else:
            st.warning("CPU Mode - GPU not available, using CPU for simulations")
    except Exception:
        pass
    
    # NOTE: DO NOT CALL render_meta_tags_safely() - it causes "Bad message format" errors
    # Minimal meta tag injection is redundant and triggers frontend message format issues

    left, center = st.columns([2, 8])
    with left:
        try:
            st.image("jntua_logo.png", width=200)
        except:
            pass

    with center:
        st.subheader("JNTUA BB84 Quantum Key Distribution Simulator")
        st.markdown("**Department of Electronics and Communication Engineering**")
    st.header("BB84 Quantum Key Distribution Process")
    st.markdown("""
    **BB84** is the first quantum key distribution protocol. It allows two parties to share a secure key over an insecure channel.

    ### Steps of BB84:
    1. **Alice generates qubits** with random bits in random bases (Z or X)
    2. **Bob measures qubits** with random bases (Z or X)
    3. **Basis announcement** - They publicly announce bases (not bits)
    4. **Sifting** - Keep only bits where bases matched
    5. **Error checking** - Estimate QBER from a subset of sifted key
    6. **Privacy amplification** - Distill secure key from sifted key using hashing

    ### Security: Any eavesdropping introduces detectable errors due to quantum no-cloning theorem.
    """)

    # SIMULATION PARAMETERS SECTION
    st.header("Simulation Configuration")
    
    # Enhanced parameter description - PURE STREAMLIT
    st.info("Instructions: Adjust the parameters below to customize your BB84 simulation. Each parameter affects how the quantum key distribution protocol behaves and how secure the shared key is.")

    param_col1, param_col2, param_col3 = st.columns(3)
    
    with param_col1:
        st.slider(
            "Qubits to Transmit",
            config.MIN_QUBITS, config.MAX_QUBITS,
            key="num_bits",
            step=50,
            help="Total number of qubits Alice sends through the quantum channel. More qubits = longer sifted key"
        )
        st.slider(
            "QBER Threshold (%)",
            config.MIN_THRESHOLD, config.MAX_THRESHOLD,
            key="threshold",
            step=0.01,
            help="Max acceptable error rate (%). If exceeded, eavesdropping is assumed. Typical: ~11%"
        )
    
    with param_col2:
        st.slider(
            " Eve Intercept Probability",
            0.0, 1.0,
            key="eve_prob",
            step=0.05,
            help="Chance Eve intercepts each qubit. 0=No eavesdropping, 1=Full interception"
        )
        st.slider(
            " Channel Noise Probability",
            0.0, 0.1,
            key="noise_prob",
            step=0.005,
            help="Environmental noise causing bit flips. Realistic channels have 1-3% noise"
        )
    
    with param_col3:
        st.selectbox(
            " Eve Attack Strategy",
            config.EVE_ATTACK_TYPES,
            index=0,
            key="eve_attack",
            help="Type of quantum attack Eve uses (if present)"
        )
        st.slider(
            " PDF Timeline Bits",
            20, 200,
            key="pdf_max",
            step=10,
            help="Maximum qubits shown in PDF timeline visualization"
        )

    # Enhanced parameters summary
    st.markdown("---")
    st.subheader(" Current Configuration Summary")
    
    try:
        params_summary = f"""
        | Setting | Value | Description |
        |---------|-------|-------------|
        | **Qubits** | {st.session_state.num_bits} | Total quantum bits transmitted |
        | **QBER Threshold** | {st.session_state.threshold:.2f}% | Max acceptable error rate |
        | **Eve Prob** | {st.session_state.eve_prob:.0%} | Likelihood of eavesdropping |
        | **Channel Noise** | {st.session_state.noise_prob:.2%} | Environmental error rate |
        | **Eve Attack** | {st.session_state.eve_attack} | Eavesdropping method |
        | **PDF Max** | {st.session_state.pdf_max} bits | Timeline visualization limit |
        """
        st.markdown(params_summary)
    except Exception:
        st.info("Configuration parameters loaded successfully")

    # SIMULATION EXECUTION
    st.markdown("---")
    if st.button("**Run BB84 Simulation**", type="primary", use_container_width=True):
        # ONLY RUN SIMULATION ON BUTTON PRESS
        st.session_state.simulation_run = True
        run_bb84_simulation()

    # RESULTS DISPLAY - Only show if simulation completed
    if st.session_state.simulation_completed:
        st.markdown("---")
        st.success(" Simulation completed! Results below:")

        # Use fragments for UI rendering (not computation)
        render_metrics_display()
        render_error_analysis()
        render_sifted_key_display()

        # Tabs for detailed analysis
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Timeline Analysis", "Comparative Analysis", "Quantum Visualization", "Report Generation", "Protocol Guide"])

        with tab1:
            render_timeline_analysis()

        with tab2:
            st.subheader("⇄ **Comparative Analysis: No Eve vs With Eve**")
            if st.session_state.sim_results:
                no_eve = st.session_state.sim_results['no_eve']
                eve = st.session_state.sim_results['eve']
                num_bits = st.session_state.sim_results['parameters']['num_bits']

                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
                
                ax1.bar(["Transmitted", "Sifted", "Final Key"],
                    [num_bits, no_eve['sifted_count'], no_eve['final_key_length']],
                    color=['#5DADE2', '#2E86AB', '#1B4965'])
                ax1.set_title(f"No Eve Scenario (QBER: {no_eve['qber']:.3f})", fontsize=12, fontweight='bold')
                ax1.set_ylabel("Number of Bits")
                ax1.grid(axis='y', alpha=0.3)
                
                # Add value labels on bars
                for i, v in enumerate([num_bits, no_eve['sifted_count'], no_eve['final_key_length']]):
                    ax1.text(i, v + 5, str(v), ha='center', va='bottom', fontweight='bold')

                ax2.bar(["Transmitted", "Sifted", "Final Key"],
                        [num_bits, eve['sifted_count'], eve['final_key_length']],
                        color=['#E74C3C', '#C0392B', '#A93226'])
                ax2.set_title(f"With Eve Scenario (QBER: {eve['qber']:.3f})", fontsize=12, fontweight='bold')
                ax2.set_ylabel("Number of Bits")
                ax2.grid(axis='y', alpha=0.3)
                
                # Add value labels on bars
                for i, v in enumerate([num_bits, eve['sifted_count'], eve['final_key_length']]):
                    ax2.text(i, v + 5, str(v), ha='center', va='bottom', fontweight='bold')

                plt.tight_layout()
                st.pyplot(fig)
                
                # Display final key comparison metrics
                st.markdown("---")
                col_no_eve, col_eve = st.columns(2)
                with col_no_eve:
                    st.metric(" **Final Secure Key Length (No Eve)**", f"{no_eve['final_key_length']} bits")
                    st.caption(f"Security Status: {no_eve['status']}")
                with col_eve:
                    st.metric(" **Final Secure Key Length (With Eve)**", f"{eve['final_key_length']} bits")
                    st.caption(f"Security Status: {eve['status']}")
                
                # Display final keys with download option
                render_final_key_download()

        with tab3:
            render_bloch_visualizations()

        with tab4:
            render_report_downloads()

        with tab5:
            st.header(" BB84 Quantum Key Distribution Protocol")
            
            st.markdown("""
            ### Protocol Overview
            **BB84** is the first quantum key distribution protocol, proposed by **Charles Bennett** and **Gilles Brassard** in 1984. 
            It allows two parties, Alice and Bob, to securely share a secret key over an insecure channel, with security guaranteed by quantum mechanics.
            """)
            
            # Protocol steps with detailed explanation
            st.markdown("""
            ### ⟲ The BB84 Protocol Steps
            
            **Step ① Key Generation by Alice:**
            - Generates random bits: 0 or 1
            - Randomly chooses basis for each bit:
              - **Rectilinear (Z basis):** encodes 0→|0, 1→|1
              - **Diagonal (X basis):** encodes 0→|+, 1→|-
            - Sends prepared qubits through quantum channel to Bob
            
            **Step ② Measurement by Bob:**
            - Randomly selects Z or X basis for each qubit
            - Measures qubit in chosen basis
            - Records measurement outcomes
            - Basis choices remain secret
            
            **Step ③ Basis Announcement & Sifting:**
            - Alice and Bob publicly compare basis choices (not bit values)
            - Keep only bits where bases **matched** (sifted key)
            - Statistically ~50% of bits survive sifting
            
            **Step ④ Quantum Bit Error Rate (QBER) Check:**
            - Compare random subset of sifted key publicly
            - Calculate QBER = (errors / total checked bits)
            - If QBER < threshold (~11%): proceed to key
            - If QBER > threshold: abort (eavesdropping detected)
            
            **Step ⑤ Privacy Amplification:**
            - Apply cryptographic hashing to sifted key
            - Produces shorter, unconditionally secure final key
            - Removes residual information about bit values
            """)
            
            st.markdown("""
            ###  Security Guarantees
            
            - **Quantum No-Cloning Theorem:** Eve cannot perfectly copy unknown quantum states
            - **Measurement Collapse:** Eve's measurement disturbs quantum states she cannot know basis for
            - **Error Detection:** Eve's interference creates detectable errors in QBER
            - **Unconditional Security:** Proven secure by quantum mechanics, not computational hardness
            """)
            
            st.markdown("""
            ### Dev This Simulator
            
            This tool simulates:
            -  Complete BB84 protocol execution
            -  Scenarios with/without eavesdropper (Eve)
            -  Channel noise and error modeling
            -  QBER calculation and threat detection
            -  Bloch sphere visualization of quantum states
            -  Timeline analysis of basis choices and measurements
            -  Professional report generation
            """)
            
            # Resources section
            st.markdown("""
            ###  Further Reading & Resources
            
            **Academic Papers:**
            -  [Bennett & Brassard (1984): Quantum Cryptography - Google Scholar](https://scholar.google.com/scholar?q=bennett+brassard+1984+quantum+cryptography)
            -  [BB84 Protocol on IEEE Xplore](https://ieeexplore.ieee.org/)
            
            **Standards & Guidelines:**
            -  [NIST Quantum Key Distribution Overview](https://csrc.nist.gov/projects/quantum-key-distribution)
            -  [ETSI QKD Standards](https://www.etsi.org/technologies/quantum-key-distribution)
            
            **Framework Documentation:**
            -  [Qiskit Quantum Information Guide](https://qiskit.org/documentation/apidoc/qiskit.quantum_info.html)
            -  [Qiskit Circuit Tutorial](https://qiskit.org/documentation/tutorials/circuits/index.html)
            -  [IBM Quantum Learning](https://quantum-computing.ibm.com/)
            
            **Educational Resources:**
            -  [Quantum Cryptography Basics - IBM Quantum](https://quantum-computing.ibm.com/composer/docs/iqx/guide/)
            -  [Quantum Key Distribution - Wikipedia](https://en.wikipedia.org/wiki/Quantum_key_distribution)
            -  [Bloch Sphere Visualization](https://en.wikipedia.org/wiki/Bloch_sphere)
            """)
            
            # Key metrics reference
            st.markdown("""
            ###  Key Metrics Explained
            
            | Metric | Definition | Interpretation |
            |--------|------------|----------------|
            | **QBER** | Quantum Bit Error Rate | Ratio of errors to checked bits; >11% suggests eavesdropping |
            | **Sifted Key** | Bits with matching bases | ~50% of transmitted bits survive sifting |
            | **Final Key** | Privacy-amplified key | Cryptographically secure key from hashing |
            | **Key Rate** | Bits/second of final key | Throughput metric for practical implementation |
            """)

    else:
        st.info("← Configure parameters above and click **Run BB84 Simulation** to see results.")

    # FOOTER SECTION
    render_footer()


# APP ENTRY POINT
if __name__ == "__main__":
    main()