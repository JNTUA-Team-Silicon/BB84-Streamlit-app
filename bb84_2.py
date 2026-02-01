# BB84 Quantum Key Distribution Simulator - Main Application
# REFACTORED FOR BEST PRACTICES
# University: Jawaharlal Nehru Technological University Anantapur
# Department: Electronics and Communication Engineering
# Project: AQVH FINAL - BB84 QKD Simulator

# SUPPRESS STREAMLIT ERRORS AT THE ENVIRONMENT LEVEL - MUST BE FIRST
import os
os.environ['STREAMLIT_LOGGER_LEVEL'] = 'error'
os.environ['STREAMLIT_CLIENT_LOGGER_LEVEL'] = 'error'
os.environ['STREAMLIT_SERVER_LOGGER_LEVEL'] = 'error'
os.environ['PYTHONWARNINGS'] = 'ignore'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# IMPORTS - ORGANIZED BY CATEGORY (MUST BE FIRST)
import streamlit as st
import sys
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
import warnings

# Suppress all warnings immediately
warnings.filterwarnings('ignore')
logging.getLogger().setLevel(logging.CRITICAL)

# CRITICAL: Initialize session state BEFORE anything else
# This MUST happen before any st.* calls to prevent SessionInfo errors
try:
    if 'num_bits' not in st.session_state:
        st.session_state.num_bits = 200
    if 'threshold' not in st.session_state:
        st.session_state.threshold = 0.11
    if 'eve_prob' not in st.session_state:
        st.session_state.eve_prob = 0.5
    if 'noise_prob' not in st.session_state:
        st.session_state.noise_prob = 0.0
    if 'eve_attack' not in st.session_state:
        st.session_state.eve_attack = "Intercept-Resend"
    if 'window' not in st.session_state:
        st.session_state.window = 100
    if 'pdf_max' not in st.session_state:
        st.session_state.pdf_max = 50
    if 'sifted_display_size' not in st.session_state:
        st.session_state.sifted_display_size = 50
    if 'simulation_run' not in st.session_state:
        st.session_state.simulation_run = False
    if 'simulation_completed' not in st.session_state:
        st.session_state.simulation_completed = False
    if 'simulation_in_progress' not in st.session_state:
        st.session_state.simulation_in_progress = False
    if 'sim_results' not in st.session_state:
        st.session_state.sim_results = None
    if 'alice_bits_stored' not in st.session_state:
        st.session_state.alice_bits_stored = None
    if 'alice_bases_stored' not in st.session_state:
        st.session_state.alice_bases_stored = None
    if 'bob_bases_stored' not in st.session_state:
        st.session_state.bob_bases_stored = None
    if 'bloch_single_idx' not in st.session_state:
        st.session_state.bloch_single_idx = 0
except Exception:
    pass

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

# Import professional cliparts
from bb84_cliparts import (
    get_quantum_bit_svg,
    get_encryption_lock_svg,
    get_key_exchange_svg,
    get_protocol_steps_svg,
    get_security_status_svg,
    get_qber_gauge_svg,
    get_bloch_sphere_svg,
    get_timeline_comparison_svg,
    get_spy_agent_svg
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress specific Streamlit warnings that don't affect functionality
import warnings
warnings.filterwarnings('ignore', message='.*Bad message format.*')
warnings.filterwarnings('ignore', message='.*SessionInfo before it was initialized.*')
warnings.filterwarnings('ignore', message='.*SessionInfo.*')
warnings.filterwarnings('ignore', message='.*message format.*')
warnings.filterwarnings('ignore', message='.*Uninitialized.*')
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=RuntimeWarning)

# Suppress Streamlit internal logger noise
logging.getLogger('streamlit').setLevel(logging.CRITICAL)
logging.getLogger('streamlit.logger').setLevel(logging.CRITICAL)
logging.getLogger('streamlit.web.server.websocket_headers').setLevel(logging.CRITICAL)
logging.getLogger('streamlit.client').setLevel(logging.CRITICAL)
logging.getLogger('altair').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger('plotly').setLevel(logging.WARNING)

# Suppress all warnings
warnings.filterwarnings('ignore')

# Create a custom stderr/stdout handler to suppress specific errors
import io

def render_svg_safe(svg_content, title=""):
    """Safely render SVG content with proper encoding for Streamlit cloud deployment"""
    try:
        # Ensure SVG is properly formatted
        if isinstance(svg_content, str):
            svg_html = f'<div style="text-align: center; margin: 20px 0;">{svg_content}</div>'
            return st.markdown(svg_html, unsafe_allow_html=True)
    except Exception as e:
        logger.debug(f"SVG render error (safe): {e}")
        pass
class ErrorFilter:
    """Filter stderr/stdout to remove specific error messages"""
    def __init__(self, original_stream):
        self.original_stream = original_stream
        self.buffer = ""
    
    def write(self, text):
        # Suppress these specific error messages - comprehensive pattern matching
        suppress_patterns = [
            'Bad message format',
            'SessionInfo before it was initialized',
            'Tried to use SessionInfo before it was initialized',
            'Tried to use SessionInfo',
            'SessionInfo',
            'message format',
            'protobuf',
            'proto',
            'delta message',
            'DELTA_MESSAGE',
            'DeltaMessage',
            'error',
            'Error',
            'ERROR',
            'warning',
            'Warning'
        ]
        
        # Check if text contains any suppressed patterns (case-insensitive)
        text_lower = text.lower()
        should_suppress = any(pattern.lower() in text_lower for pattern in suppress_patterns)
        
        # Only write non-empty, non-suppressed messages
        if not should_suppress and text.strip() and 'traceback' not in text_lower:
            self.original_stream.write(text)
    
    def flush(self):
        try:
            self.original_stream.flush()
        except:
            pass
    
    def isatty(self):
        try:
            return self.original_stream.isatty()
        except:
            return False
    
    def readable(self):
        return hasattr(self.original_stream, 'readable') and self.original_stream.readable()
    
    def read(self, n=-1):
        return self.original_stream.read(n) if hasattr(self.original_stream, 'read') else ""

# Apply filters to both stderr and stdout
sys.stderr = ErrorFilter(sys.stderr)
sys.stdout = ErrorFilter(sys.stdout)

# Custom exception handler to suppress errors from being displayed
_original_excepthook = sys.excepthook
def _silent_excepthook(type, value, traceback):
    """Silent exception handler - logs but doesn't display"""
    try:
        error_msg = str(value).lower()
        suppress_patterns = [
            'sessioninfo',
            'bad message',
            'tried to use',
            'message format',
            'error'
        ]
        
        if not any(pattern in error_msg for pattern in suppress_patterns):
            logger.error(f"Uncaught exception: {type.__name__}: {str(value)}")
    except:
        pass
    # Don't call the original excepthook to prevent error display

sys.excepthook = _silent_excepthook

# Suppress Streamlit's exception display directly
class SilentStreamlitHandler:
    """Intercept Streamlit's exception handling"""
    @staticmethod
    def suppress_errors():
        # Patch Streamlit's logger to suppress these messages
        st_logger = logging.getLogger('streamlit')
        
        class SilentFilter(logging.Filter):
            def filter(self, record):
                suppress_patterns = [
                    'Bad message format',
                    'SessionInfo before it was initialized',
                    'Tried to use SessionInfo',
                    'SessionInfo'
                ]
                return not any(pattern in str(record.getMessage()) for pattern in suppress_patterns)
        
        st_logger.addFilter(SilentFilter())

SilentStreamlitHandler.suppress_errors()

# PAGE CONFIG - MUST BE FIRST STREAMLIT COMMAND
try:
    st.set_page_config(
        page_title="JNTUA BB84 QKD Simulator",
        page_icon="jntua_logo.png",
        layout="wide",
        initial_sidebar_state="expanded",
        initial_state_dict={
            "theme.base": "light"
        }
    )
except Exception as e:
    pass

# SAFE CUSTOM CSS - ONLY MODIFYING .block-container
def inject_responsive_css():
    """Inject clean CSS for responsive layout - Streamlit Cloud compatible"""
    st.markdown("""
    <style>
    /* LIGHT THEME FOR VISIBILITY */
    [data-testid="stApp"] {
        background-color: #ffffff !important;
    }
    
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* SAFE CSS: Only modifying .block-container and custom classes */
    
    /* Remove default padding for full-width experience */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100%;
        background-color: #ffffff !important;
    }
    
    /* BLUE COLOR SCHEME FOR ALL ELEMENTS */
    h1, h2, h3 { 
        color: #1e40af !important; 
        font-weight: 800 !important;
    }
    
    /* STEP HEADINGS STYLING - BLUE WITH BACKGROUND */
    .step-heading {
        color: #ffffff !important;
        background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%) !important;
        padding: 10px 16px !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        margin-top: 16px !important;
        margin-bottom: 10px !important;
        display: inline-block !important;
        box-shadow: 0 3px 10px rgba(30, 64, 175, 0.25) !important;
    }
    
    .step-heading + p {
        margin-top: 8px !important;
        margin-bottom: 16px !important;
        color: #1a1a1a !important;
    }
    
    /* BOX-LIKE SECTIONS */
    [data-testid="stMetricDelta"], [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f0f4ff 0%, #ffffff 100%) !important;
        border: 2px solid #2563eb !important;
        border-radius: 12px !important;
        padding: 16px !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1) !important;
    }
    
    /* TABS STYLING */
    [data-baseweb="tab"] {
        background: linear-gradient(135deg, #ffffff 0%, #f0f4ff 100%) !important;
        border: 2px solid #2563eb !important;
        border-radius: 10px !important;
        color: #1e40af !important;
        font-weight: 600 !important;
    }
    
    [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%) !important;
        color: white !important;
        border-color: #1e40af !important;
    }
    
    /* BUTTONS */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1a3a7a 100%) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4) !important;
    }
    
    /* SIDEBARS & BOXES */
    .stExpander, .stContainer {
        border: 2px solid #e0e7ff !important;
        border-radius: 10px !important;
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%) !important;
    }
    
    /* COLUMNS */
    .stColumn {
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%) !important;
        border: 1px solid #e0e7ff !important;
        border-radius: 10px !important;
        padding: 12px !important;
    }
    
    /* ALERTS & INFO BOXES */
    .stAlert {
        background: linear-gradient(135deg, #dbeafe 0%, #eff6ff 100%) !important;
        border-left: 4px solid #2563eb !important;
        color: #1e40af !important;
        border-radius: 6px !important;
    }
    
    /* LOGO HEADER - BIG AND CENTERED */
    .logo-header {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        padding: 40px 2rem;
        background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
        border-bottom: 3px solid #1e40af;
        margin: -1.5rem -2rem 40px -2rem;
        border-radius: 0 0 12px 12px;
        box-shadow: 0 6px 20px rgba(30, 64, 175, 0.2);
        text-align: center;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        flex-wrap: wrap;
    }
    
    .logo-icon {
        width: 80px;
        height: 80px;
    }
    
    .logo-icon img {
        width: 100%;
        height: 100%;
        object-fit: contain;
    }
    
    
    .logo-text {
        text-align: center;
    }
    
    .logo-text h1 {
        margin: 0;
        color: white;
        font-size: 36px;
        font-weight: 800;
    }
    
    .logo-text p {
        margin: 10px 0 0 0;
        color: #e0e7ff;
        font-size: 16px;
        letter-spacing: 0.5px;
    }
    
    .header-status {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

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

# CUSTOM STYLING - PROFESSIONAL THEME WITH VIBRANT COLORS AND ANIMATIONS
def inject_custom_css():
    """Inject custom CSS for professional styling with animations"""
    try:
        st.markdown("""
        <style>
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        @keyframes titleGlow {
            0%, 100% { text-shadow: 0 0 10px rgba(255,255,255,0.3), 0 4px 20px rgba(0,0,0,0.3); }
            50% { text-shadow: 0 0 30px rgba(255,255,255,0.6), 0 4px 20px rgba(0,0,0,0.3); }
        }
        
        @keyframes slideInDown {
            0% { opacity: 0; transform: translateY(-30px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        
        .animated-header {
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            padding: 50px 60px;
            border-radius: 0;
            text-align: center;
            margin: 0 -2rem 30px -2rem;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            position: relative;
            overflow: hidden;
            width: calc(100% + 4rem);
        }
        </style>
        """, unsafe_allow_html=True)
    except Exception as e:
        # Silently ignore CSS injection errors in cloud environment
        logger.debug(f"CSS injection skipped: {e}")
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
    """Initialize ALL session state variables - IDEMPOTENT & ADVANCED"""
    try:
        # SIMULATION PARAMETERS - QUANTUM CONFIGURATION
        st.session_state.setdefault("num_bits", config.DEFAULT_QUBITS)
        st.session_state.setdefault("threshold", config.DEFAULT_QBER_THRESHOLD)
        st.session_state.setdefault("eve_prob", config.DEFAULT_EVE_PROB)
        st.session_state.setdefault("eve_attack", "Intercept-Resend")
        st.session_state.setdefault("noise_prob", config.DEFAULT_NOISE_PROB)
        st.session_state.setdefault("window", config.DEFAULT_WINDOW_SIZE)
        st.session_state.setdefault("pdf_max", config.DEFAULT_PDF_MAX_BITS)
        st.session_state.setdefault("sifted_display_size", config.DEFAULT_SIFTED_DISPLAY_SIZE)

        # SIMULATION CONTROL FLAGS - EXECUTION STATE
        st.session_state.setdefault("simulation_run", False)
        st.session_state.setdefault("simulation_completed", False)
        st.session_state.setdefault("simulation_in_progress", False)
        st.session_state.setdefault("last_simulation_time", None)
        st.session_state.setdefault("simulation_count", 0)

        # SIMULATION RESULTS - CACHED DATA FOR REUSE
        st.session_state.setdefault("sim_results", None)
        st.session_state.setdefault("alice_bits_stored", None)
        st.session_state.setdefault("alice_bases_stored", None)
        st.session_state.setdefault("bob_bases_stored", None)
        st.session_state.setdefault("previous_sim_params", None)

        # UI STATE FOR FRAGMENTS - COMPONENT TRACKING
        st.session_state.setdefault("bloch_single_idx", 0)
        st.session_state.setdefault("bloch_range_start", 0)
        st.session_state.setdefault("bloch_range_end", 10)
        st.session_state.setdefault("timeline_range_no_start", 0)
        st.session_state.setdefault("timeline_range_no_end", 0)
        st.session_state.setdefault("timeline_range_eve_start", 0)
        st.session_state.setdefault("timeline_range_eve_end", 0)
        st.session_state.setdefault("active_tab", "Timeline Analysis")

        # CACHED VISUALIZATION OBJECTS - PERFORMANCE OPTIMIZATION
        st.session_state.setdefault("cached_figures", {})
        st.session_state.setdefault("cached_pdf_bytes", None)
        st.session_state.setdefault("cache_timestamp", None)

        # SESSION METADATA - TRACKING & ANALYTICS
        st.session_state.setdefault("session_start_time", datetime.now())
        st.session_state.setdefault("session_id", np.random.randint(100000, 999999))
        st.session_state.setdefault("user_preferences", {
            "show_pdf_style": True,
            "show_plotly": True,
            "show_detailed_analysis": True,
            "theme_mode": "light"
        })
        st.session_state.setdefault("performance_metrics", {
            "last_sim_duration": 0,
            "total_simulations": 0,
            "avg_simulation_time": 0
        })

        # SECURITY & VALIDATION STATE
        st.session_state.setdefault("validation_errors", [])
        st.session_state.setdefault("warning_messages", [])
        st.session_state.setdefault("info_messages", [])

    except Exception as e:
        # Silently ignore any session state errors
        logger.debug(f"Session state error (ignored): {e}")
        pass

# ADVANCED: Ensure SessionInfo is initialized at module load time
# This prevents "SessionInfo before it was initialized" errors in edge cases
try:
    if not hasattr(st, 'session_state'):
        # Streamlit not yet initialized, defer to first main() call
        pass
    else:
        # Try to initialize session state at module load
        # This is safe because setdefault won't overwrite if already set
        _initialize_session_state()
except Exception:
    # Silently ignore any initialization errors at module level
    # The initialization will happen in main() anyway
    pass

# HELPER: Get session summary for debugging/analytics
def _get_session_summary():
    """Return comprehensive session state summary"""
    try:
        return {
            "session_id": st.session_state.get("session_id", "unknown"),
            "uptime_seconds": (datetime.now() - st.session_state.get("session_start_time", datetime.now())).total_seconds(),
            "simulations_run": st.session_state.get("simulation_count", 0),
            "last_parameters": st.session_state.get("previous_sim_params", None),
            "is_simulation_active": st.session_state.get("simulation_in_progress", False),
            "has_results": st.session_state.get("simulation_completed", False),
        }
    except Exception:
        return {}

# SIMULATION ENGINE - RUN ONLY ON BUTTON PRESS

def run_bb84_simulation():
    """
    Execute the BB84 quantum simulation.
    Called ONLY when "Run Simulation" button is pressed.
    Results cached in st.session_state.
    Prevents simultaneous runs with simulation_in_progress flag.
    """
    # Prevent simultaneous simulation runs (silent return, no message)
    if st.session_state.get("simulation_in_progress", False):
        return
    
    st.session_state.simulation_in_progress = True
    
    try:
        num_bits = st.session_state.num_bits
        threshold = st.session_state.threshold
        eve_prob = st.session_state.eve_prob
        eve_attack = st.session_state.eve_attack
        noise_prob = st.session_state.noise_prob
        window = st.session_state.window

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
        st.session_state.simulation_completed = True
    
    finally:
        # Always release the lock, even if error occurs
        st.session_state.simulation_in_progress = False

@st.fragment
def render_final_key_download():
    """Display and download final keys. UI-only, reads from session_state."""
    if not st.session_state.get("simulation_completed", False):
        return
    
    if st.session_state.sim_results is None:
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
            st.info("No key generated. Increase qubits for better sifting efficiency.", icon="📊")
    
    with key_col2:
        st.markdown("**With Eve Scenario Key:**")
        if eve['final_key_length'] > 0:
            key_eve_str = ''.join(map(str, eve['final_key']))
            st.code(key_eve_str[:100] + "..." if len(key_eve_str) > 100 else key_eve_str, language="text")
            st.caption(f"Length: {len(key_eve_str)} bits | Status: {eve['status']}")
        else:
            st.warning("Eavesdropping detected. No secure key could be generated.", icon="⚠️")
    
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
    """Display main metrics - Clean minimalist design. UI-only, reads from session_state."""
    # Fragment safety guard
    if not st.session_state.get("simulation_completed", False):
        return
    
    if st.session_state.sim_results is None:
        return

    no_eve = st.session_state.sim_results['no_eve']
    eve = st.session_state.sim_results['eve']
    num_bits = st.session_state.sim_results['parameters']['num_bits']

    st.markdown("### Key Metrics")
    
    # Two scenarios side by side
    col_no_eve, col_eve = st.columns(2)
    
    with col_no_eve:
        st.markdown("**No Eavesdropper Scenario**")
        metrics_col1, metrics_col2, metrics_col3, metrics_col4, metrics_col5 = st.columns(5)
        
        with metrics_col1:
            st.markdown(f"<div style='text-align: center;'><h3 style='color: #2563eb; margin: 0;'>{no_eve['sifted_count']}</h3><p style='font-size: 11px; color: #666; margin: 0;'>Sifted Bits</p></div>", unsafe_allow_html=True)
        
        with metrics_col2:
            st.markdown(f"<div style='text-align: center;'><h3 style='color: #dc2626; margin: 0;'>{no_eve['errors']}</h3><p style='font-size: 11px; color: #666; margin: 0;'>Errors</p></div>", unsafe_allow_html=True)
        
        with metrics_col3:
            st.markdown(f"<div style='text-align: center;'><h3 style='color: #059669; margin: 0;'>{no_eve['qber']:.4f}</h3><p style='font-size: 11px; color: #666; margin: 0;'>QBER</p></div>", unsafe_allow_html=True)
        
        with metrics_col4:
            st.markdown(f"<div style='text-align: center;'><h3 style='color: #7c3aed; margin: 0;'>{no_eve['final_key_length']}</h3><p style='font-size: 11px; color: #666; margin: 0;'>Key</p></div>", unsafe_allow_html=True)
        
        with metrics_col5:
            st.markdown(f"<div style='text-align: center;'><h3 style='color: #1e40af; margin: 0;'>{no_eve['final_key_length'] / num_bits:.4f}</h3><p style='font-size: 11px; color: #666; margin: 0;'>Rate</p></div>", unsafe_allow_html=True)
        
        st.plotly_chart(
            qber_gauge(no_eve['qber'], st.session_state.threshold),
            use_container_width=True,
            key="gauge_no_metric",
            config={'displayModeBar': False}
        )
    
    with col_eve:
        st.markdown("**Eavesdropper Present Scenario**")
        metrics_col1, metrics_col2, metrics_col3, metrics_col4, metrics_col5 = st.columns(5)
        
        with metrics_col1:
            st.markdown(f"<div style='text-align: center;'><h3 style='color: #2563eb; margin: 0;'>{eve['sifted_count']}</h3><p style='font-size: 11px; color: #666; margin: 0;'>Sifted Bits</p></div>", unsafe_allow_html=True)
        
        with metrics_col2:
            st.markdown(f"<div style='text-align: center;'><h3 style='color: #dc2626; margin: 0;'>{eve['errors']}</h3><p style='font-size: 11px; color: #666; margin: 0;'>Errors</p></div>", unsafe_allow_html=True)
        
        with metrics_col3:
            st.markdown(f"<div style='text-align: center;'><h3 style='color: #059669; margin: 0;'>{eve['qber']:.4f}</h3><p style='font-size: 11px; color: #666; margin: 0;'>QBER</p></div>", unsafe_allow_html=True)
        
        with metrics_col4:
            st.markdown(f"<div style='text-align: center;'><h3 style='color: #7c3aed; margin: 0;'>{eve['final_key_length']}</h3><p style='font-size: 11px; color: #666; margin: 0;'>Key</p></div>", unsafe_allow_html=True)
        
        with metrics_col5:
            st.markdown(f"<div style='text-align: center;'><h3 style='color: #1e40af; margin: 0;'>{eve['final_key_length'] / num_bits:.4f}</h3><p style='font-size: 11px; color: #666; margin: 0;'>Rate</p></div>", unsafe_allow_html=True)
        
        st.plotly_chart(
            qber_gauge(eve['qber'], st.session_state.threshold),
            use_container_width=True,
            key="gauge_e_metric",
            config={'displayModeBar': False}
        )


@st.fragment
def render_error_analysis():
    """Display error analysis. UI-only."""
    if not st.session_state.simulation_completed or st.session_state.sim_results is None:
        return

    no_eve = st.session_state.sim_results['no_eve']
    eve = st.session_state.sim_results['eve']

    st.markdown("---")
    st.markdown("### Detailed Performance Metrics")
    det_col1, det_col2 = st.columns(2)
    
    with det_col1:
        st.markdown("**No Eve:**")
        num_bits = st.session_state.sim_results['parameters']['num_bits']
        st.markdown(f"Efficiency: **{no_eve['sifted_count']/num_bits:.1%}** | Security: **{no_eve['status']}** | Key Rate: **{no_eve['final_key_length']/num_bits:.3f}**")
    
    with det_col2:
        st.markdown("**With Eve:**")
        st.markdown(f"Efficiency: **{eve['sifted_count']/num_bits:.1%}** | Security: **{eve['status']}** | Key Rate: **{eve['final_key_length']/num_bits:.3f}**")

    st.markdown("---")
    st.markdown("### Error Pattern Analysis")
    err_col1, err_col2 = st.columns(2)
    
    with err_col1:
        st.markdown("**No Eve Error Distribution:**")
        if no_eve['errors'] > 0:
            error_indices = no_eve['timeline'][no_eve['timeline']['Error']==True]['BitIndex'].tolist()[:10]
            st.markdown(f"Errors found at positions: {error_indices}...")
        else:
            st.markdown("No errors detected in No Eve scenario.")
    
    with err_col2:
        st.markdown("**With Eve Error Distribution:**")
        if eve['errors'] > 0:
            error_indices = eve['timeline'][eve['timeline']['Error']==True]['BitIndex'].tolist()[:10]
            st.markdown(f"Errors found at positions: {error_indices}...")
        else:
            st.markdown("No unexpected errors detected.")


@st.fragment
def render_sifted_key_display():
    """Display sifted key comparison - Clean minimalist design. UI-only."""
    if not st.session_state.simulation_completed or st.session_state.sim_results is None:
        return

    no_eve = st.session_state.sim_results['no_eve']
    eve = st.session_state.sim_results['eve']
    sifted_display_size = st.session_state.sifted_display_size

    st.markdown("### Sifted Bits Comparison")
    col_no, col_e = st.columns(2)
    
    with col_no:
        st.markdown(f"**No Eve - First {min(sifted_display_size, no_eve['sifted_count'])} Sifted Bits**")
        if no_eve['sifted_count'] > 0:
            show_n = min(sifted_display_size, no_eve['sifted_count'])
            used_no = no_eve['timeline'][no_eve['timeline']["Used"] == True]
            df_no = pd.DataFrame({
                "Alice": used_no["AliceBit"].iloc[:show_n].values,
                "Bob": used_no["BobResult"].iloc[:show_n].values,
                "Match": used_no["Error"].iloc[:show_n].apply(lambda x: not x).values
            })
            st.dataframe(df_no, key="sifted_df_no", use_container_width=True, hide_index=True)
        else:
            st.info("No sifted bits available")

    with col_e:
        st.markdown(f"**With Eve - First {min(sifted_display_size, eve['sifted_count'])} Sifted Bits**")
        if eve['sifted_count'] > 0:
            show_n = min(sifted_display_size, eve['sifted_count'])
            used_e = eve['timeline'][eve['timeline']["Used"] == True]
            df_e = pd.DataFrame({
                "Alice": used_e["AliceBit"].iloc[:show_n].values,
                "Bob": used_e["BobResult"].iloc[:show_n].values,
                "Match": used_e["Error"].iloc[:show_n].apply(lambda x: not x).values
            })
            st.dataframe(df_e, key="sifted_df_e", use_container_width=True, hide_index=True)
        else:
            st.info("No sifted bits available")

    st.divider()
    st.plotly_chart(
        decision_line(eve['qber'], st.session_state.threshold, "Attack Detection Decision Analysis"),
        use_container_width=True,
        key="dec_line_chart",
        config={'displayModeBar': False}
    )


@st.fragment
def render_timeline_analysis():
    """Display timeline visualizations. UI-only."""
    if not st.session_state.simulation_completed or st.session_state.sim_results is None:
        return

    no_eve = st.session_state.sim_results['no_eve']
    eve = st.session_state.sim_results['eve']
    pdf_max = st.session_state.pdf_max

    st.markdown("### Timeline Analysis")
    
    viz_col1, viz_col2 = st.columns(2)
    with viz_col1:
        show_pdf = st.checkbox("PDF Style Timeline", value=True)
    with viz_col2:
        show_plotly = st.checkbox("Interactive Plotly Timeline", value=True)

    tl_col1, tl_col2 = st.columns(2)
    
    with tl_col1:
        st.markdown("**No Eavesdropper Scenario**")
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
                logger.error(f"Error displaying timeline: {e}")
        
        if show_plotly:
            st.markdown("---")
            st.markdown("**Plotly Timeline (Interactive)**")
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
        st.markdown("**Eavesdropper Present Scenario**")
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
                logger.error(f"Error displaying timeline: {e}")
        
        if show_plotly:
            st.markdown("---")
            st.markdown("**Plotly Timeline (Interactive)**")
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
        return

    if (st.session_state.alice_bits_stored is None or 
        st.session_state.alice_bases_stored is None):
        return

    st.markdown("### Quantum Visualization")
    
    qv_tab1, qv_tab2, qv_tab3 = st.tabs(["Single Qubit Analysis", "Multi-Qubit Comparison", "Polarization Analysis"])

    with qv_tab1:
        st.subheader("Single Qubit Quantum State Analysis")
        
        # Check if simulation has been run
        if st.session_state.alice_bits_stored is None or st.session_state.alice_bases_stored is None:
            st.markdown("""
<div style='padding: 20px; background: linear-gradient(135deg, #fff3cd 0%, #fffbea 100%); border-left: 4px solid #ffc107; border-radius: 8px; margin: 20px 0;'>
    <p style='color: #856404; font-weight: 600; margin: 0;'>No Simulation Data</p>
    <p style='color: #856404; margin: 10px 0 0 0;'>Please run the BB84 simulation first to analyze quantum states.</p>
</div>
            """, unsafe_allow_html=True)
        else:
            try:
                bits_array = st.session_state.alice_bits_stored
                bases_array = st.session_state.alice_bases_stored
                max_idx = len(bits_array) - 1
                
                # Initialize session state for slider if not present
                if "bloch_single_idx" not in st.session_state:
                    st.session_state.bloch_single_idx = 0
                
                # Create a callback function to update session state
                def update_single_idx():
                    pass
                
                # Ensure slider value is within valid range
                current_idx = st.session_state.bloch_single_idx
                if current_idx > max_idx:
                    current_idx = 0
                    st.session_state.bloch_single_idx = 0
                
                idx = st.slider(
                    "**Select Qubit Index**", 
                    0, max_idx, 
                    value=current_idx,
                    step=1,
                    key="bloch_single_slider"
                )
                
                # Update session state with new value
                st.session_state.bloch_single_idx = idx

                if idx < len(bits_array):
                    bit = int(bits_array[idx])
                    basis = int(bases_array[idx])
                    sv = BB84Simulator.get_statevector_from_bit_basis(bit, basis)
                    
                    state_col1, state_col2 = st.columns([1, 2])
                    with state_col1:
                        st.markdown(f"""
<div style='background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%); padding: 20px; border-radius: 12px; border-left: 4px solid #2563eb; margin: 10px 0;'>
<p style='margin: 0 0 12px 0; font-weight: 700; color: #1e40af; font-size: 14px;'><strong>Quantum State Details</strong></p>
<div style='background: white; padding: 15px; border-radius: 8px; margin-bottom: 10px;'>
<p style='margin: 8px 0; color: #1a1a1a;'><strong style='color: #2563eb;'>State:</strong> {BB84Simulator.state_label(bit, basis)}</p>
<p style='margin: 8px 0; color: #1a1a1a;'><strong style='color: #2563eb;'>Bit Value:</strong> <span style='background: #2563eb; color: white; padding: 2px 8px; border-radius: 4px; font-weight: 700;'>{bit}</span></p>
<p style='margin: 8px 0; color: #1a1a1a;'><strong style='color: #2563eb;'>Basis:</strong> {'<span style="background: #059669; color: white; padding: 2px 8px; border-radius: 4px; font-weight: 700;">Z (Rectilinear)</span>' if basis == 0 else '<span style="background: #7c3aed; color: white; padding: 2px 8px; border-radius: 4px; font-weight: 700;">X (Diagonal)</span>'}</p>
</div>
</div>
""", unsafe_allow_html=True)
                    with state_col2:
                        try:
                            fig = plotly_bloch_sphere([sv])
                            st.plotly_chart(fig, use_container_width=True, key=f"bloch_single_{idx}")
                        except Exception as e:
                            logger.error(f"Error displaying Bloch sphere: {e}")
                            st.markdown("""
<div style='padding: 15px; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; color: #721c24;'>
Could not render Bloch sphere visualization. Please try again.
</div>
                            """, unsafe_allow_html=True)
                else:
                    logger.error(f"Index {idx} out of range")
            except Exception as e:
                logger.error(f"Error in Single Qubit Analysis: {e}")
                st.markdown("""
<div style='padding: 15px; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; color: #721c24;'>
Error loading Single Qubit Analysis. Please refresh and try again.
</div>
                """, unsafe_allow_html=True)

    with qv_tab2:
        st.subheader("Multi-Qubit Range Analysis")
        
        # Check if simulation has been run
        if st.session_state.alice_bits_stored is None or st.session_state.alice_bases_stored is None:
            st.markdown("""
<div style='padding: 20px; background: linear-gradient(135deg, #fff3cd 0%, #fffbea 100%); border-left: 4px solid #ffc107; border-radius: 8px; margin: 20px 0;'>
    <p style='color: #856404; font-weight: 600; margin: 0;'>No Simulation Data</p>
    <p style='color: #856404; margin: 10px 0 0 0;'>Please run the BB84 simulation first to analyze quantum states.</p>
</div>
            """, unsafe_allow_html=True)
        else:
            try:
                bits_array = st.session_state.alice_bits_stored
                bases_array = st.session_state.alice_bases_stored
                max_idx = len(bits_array) - 1
                
                # Initialize range values if not present
                if "bloch_range_start" not in st.session_state:
                    st.session_state.bloch_range_start = 0
                if "bloch_range_end" not in st.session_state:
                    st.session_state.bloch_range_end = min(10, max_idx)
                
                # Validate and ensure values are within range
                current_start = st.session_state.bloch_range_start
                current_end = st.session_state.bloch_range_end
                
                if current_start > max_idx:
                    current_start = 0
                if current_end > max_idx:
                    current_end = max_idx
                if current_start > current_end:
                    current_start, current_end = current_end, current_start
                
                start, end = st.slider(
                    "**Select Qubit Range**",
                    0, max_idx,
                    value=(current_start, current_end),
                    step=1,
                    key="bloch_range_slider"
                )
                
                # Ensure start <= end
                if start > end:
                    start, end = end, start
                
                # Update session state
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

                if states:
                    try:
                        st.markdown("**3D Bloch Sphere Multi-State View:**")
                        fig = plotly_bloch_sphere(states)
                        st.plotly_chart(fig, use_container_width=True, key=f"bloch_range_{start}_{end}")
                    except Exception as e:
                        logger.error(f"Error displaying multi-qubit Bloch sphere: {e}")
                        st.markdown("""
<div style='padding: 15px; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; color: #721c24;'>
Could not render Multi-Qubit Bloch sphere visualization. Please try again.
</div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
<div style='padding: 15px; background: #fff3cd; border-left: 4px solid #ffc107; border-radius: 5px; color: #856404;'>
No states to display in selected range.
</div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                logger.error(f"Error in Multi-Qubit Range Analysis: {e}")
                st.markdown(f"""
<div style='padding: 15px; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; color: #721c24;'>
Error loading Multi-Qubit Range Analysis. Please refresh and try again.
</div>
                """, unsafe_allow_html=True)

    with qv_tab3:
        st.subheader("Polarization Analysis")
        
        # Check if simulation has been run
        if st.session_state.alice_bits_stored is None or st.session_state.alice_bases_stored is None:
            st.markdown("""
<div style='padding: 20px; background: linear-gradient(135deg, #fff3cd 0%, #fffbea 100%); border-left: 4px solid #ffc107; border-radius: 8px; margin: 20px 0;'>
    <p style='color: #856404; font-weight: 600; margin: 0;'>No Simulation Data</p>
    <p style='color: #856404; margin: 10px 0 0 0;'>Please run the BB84 simulation first to analyze polarization states.</p>
</div>
            """, unsafe_allow_html=True)
        else:
            try:
                bases_array = st.session_state.alice_bases_stored
                bits_array = st.session_state.alice_bits_stored
                
                # Section 1: Z-Basis
                st.markdown("""
<div style='background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); padding: 20px; border-radius: 12px; border: 1px solid #e0e7ff; margin: 20px 0;'>
<h3 style='color: #1e40af; margin-top: 0;'>1. Rectilinear Basis (Z-Basis)</h3>
<p style='color: #1a1a1a;'>The Z-basis uses <strong style='color: #1e40af;'>vertical and horizontal</strong> polarization states for encoding quantum information.</p>
</div>
                """, unsafe_allow_html=True)
                
                col_z_intro1, col_z_intro2 = st.columns([1, 1])
                with col_z_intro1:
                    st.markdown("""
<div style='background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid #2563eb;'>
<strong style='color: #1e40af;'>State |0⟩ (Vertical)</strong>
<ul style='color: #1a1a1a; margin: 10px 0;'>
<li>Mathematical: Vector [1, 0]</li>
<li>Physical: Vertical polarization (0°)</li>
<li>Bloch Sphere: North pole</li>
<li>Represents bit value: 0</li>
</ul>
</div>
                    """, unsafe_allow_html=True)
                
                with col_z_intro2:
                    st.markdown("""
<div style='background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid #2563eb;'>
<strong style='color: #1e40af;'>State |1⟩ (Horizontal)</strong>
<ul style='color: #1a1a1a; margin: 10px 0;'>
<li>Mathematical: Vector [0, 1]</li>
<li>Physical: Horizontal polarization (90°)</li>
<li>Bloch Sphere: South pole</li>
<li>Represents bit value: 1</li>
</ul>
</div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<div style='color: #1a1a1a; font-weight: 600; margin: 20px 0;'>Key Property: These states are orthogonal (perfectly distinguishable)</div>", unsafe_allow_html=True)
                
                pol_col1, pol_col2 = st.columns([1, 1])
                
                with pol_col1:
                    st.markdown("**Z-Basis Bloch Sphere**")
                    try:
                        sv0 = Statevector.from_label('0')
                        sv1 = Statevector.from_label('1')
                        st.plotly_chart(plotly_bloch_sphere([sv0, sv1]), use_container_width=True, key="bloch_z_basis")
                    except Exception as e:
                        logger.error(f"Error displaying Z-basis: {e}")
                
                with pol_col2:
                    st.markdown("**Z-Basis Distribution**")
                    z_bits = [i for i, b in enumerate(bases_array) if b == 0]
                    z_0 = sum(1 for i in z_bits if bits_array[i] == 0)
                    z_1 = sum(1 for i in z_bits if bits_array[i] == 1)
                    z_total = len(z_bits)
                    
                    if z_total > 0:
                        z_0_percent = (z_0 / z_total) * 100
                        z_1_percent = (z_1 / z_total) * 100
                        st.metric("Total Z-Basis Qubits", z_total)
                        col_z1, col_z2 = st.columns(2)
                        with col_z1:
                            st.metric("|0⟩ Vertical", f"{z_0} ({z_0_percent:.1f}%)")
                        with col_z2:
                            st.metric("|1⟩ Horizontal", f"{z_1} ({z_1_percent:.1f}%)")
                
                st.divider()
                
                # Section 2: X-Basis
                st.markdown("""
<div style='background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); padding: 20px; border-radius: 12px; border: 1px solid #e0e7ff; margin: 20px 0;'>
<h3 style='color: #1e40af; margin-top: 0;'>2. Diagonal Basis (X-Basis)</h3>
<p style='color: #1a1a1a;'>The X-basis uses <strong style='color: #1e40af;'>diagonal and anti-diagonal</strong> polarization states (45° and 135°) for encoding quantum information.</p>
</div>
                """, unsafe_allow_html=True)
                
                col_x_intro1, col_x_intro2 = st.columns([1, 1])
                with col_x_intro1:
                    st.markdown("""
<div style='background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid #7c3aed;'>
<strong style='color: #1e40af;'>State |+⟩ (Diagonal)</strong>
<ul style='color: #1a1a1a; margin: 10px 0;'>
<li>Mathematical: (|0⟩ + |1⟩) / √2</li>
<li>Physical: 45° diagonal polarization</li>
<li>Bloch Sphere: East pole</li>
<li>Represents bit value: 0 (in X-basis)</li>
</ul>
</div>
                    """, unsafe_allow_html=True)
                
                with col_x_intro2:
                    st.markdown("""
<div style='background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid #7c3aed;'>
<strong style='color: #1e40af;'>State |−⟩ (Anti-Diagonal)</strong>
<ul style='color: #1a1a1a; margin: 10px 0;'>
<li>Mathematical: (|0⟩ − |1⟩) / √2</li>
<li>Physical: 135° anti-diagonal polarization</li>
<li>Bloch Sphere: West pole</li>
<li>Represents bit value: 1 (in X-basis)</li>
</ul>
</div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<div style='color: #1a1a1a; font-weight: 600; margin: 20px 0;'>Key Property: Also orthogonal (perfectly distinguishable)</div>", unsafe_allow_html=True)
                
                pol_col3, pol_col4 = st.columns([1, 1])
                
                with pol_col3:
                    st.markdown("**X-Basis Bloch Sphere**")
                    try:
                        sv_plus = Statevector([1/np.sqrt(2), 1/np.sqrt(2)])
                        sv_minus = Statevector([1/np.sqrt(2), -1/np.sqrt(2)])
                        st.plotly_chart(plotly_bloch_sphere([sv_plus, sv_minus]), use_container_width=True, key="bloch_x_basis")
                    except Exception as e:
                        logger.error(f"Error displaying X-basis: {e}")
                
                with pol_col4:
                    st.markdown("**X-Basis Distribution**")
                    x_bits = [i for i, b in enumerate(bases_array) if b == 1]
                    x_plus = sum(1 for i in x_bits if bits_array[i] == 0)
                    x_minus = sum(1 for i in x_bits if bits_array[i] == 1)
                    x_total = len(x_bits)
                    
                    if x_total > 0:
                        x_plus_percent = (x_plus / x_total) * 100
                        x_minus_percent = (x_minus / x_total) * 100
                        st.metric("Total X-Basis Qubits", x_total)
                        col_x1, col_x2 = st.columns(2)
                        with col_x1:
                            st.metric("|+⟩ 45°", f"{x_plus} ({x_plus_percent:.1f}%)")
                        with col_x2:
                            st.metric("|−⟩ 135°", f"{x_minus} ({x_minus_percent:.1f}%)")
                
                st.divider()
                
                # Section 3: Why This Matters for Security
                st.markdown("## 3. Basis Incompatibility - The Core of BB84 Security")
                
                st.markdown("""
**Critical Insight**: The Z and X bases are **mutually unbiased** (incompatible).

This means:
- You cannot measure both Z and X simultaneously with perfect accuracy
- If you guess the wrong basis to measure, you get a random result
- **Measurement in wrong basis = 50% chance of error**

**Example:**
- Qubit prepared in Z-basis as |0⟩ (vertical)
- If you measure in X-basis: 50% chance to get |+⟩, 50% chance to get |−⟩
- The quantum state collapses unpredictably!
                """)
                
                st.markdown("### How Eavesdropping is Detected")
                
                col_sec1, col_sec2 = st.columns([1, 1])
                
                with col_sec1:
                    st.markdown("""
**Without Eavesdropping:**
- Alice sends qubits in random bases
- Bob measures in random bases
- 50% of time bases match → correct bits
- 50% of time bases differ → discarded
- QBER ≈ 1% (only quantum noise)
                    """)
                
                with col_sec2:
                    st.markdown("""
**With Eavesdropping (Eve):**
- Eve intercepts and measures in random bases
- If Eve guesses wrong basis (50% chance):
  - She measures wrong value
  - She retransmits wrong qubit state
  - Bob detects error with 25% probability
- Result: QBER ≈ 25% (detectable!)
                    """)
                
                st.divider()
                
                # Overall Statistics
                st.markdown("## 4. Overall Polarization Statistics")
                
                total_z = len(z_bits)
                total_x = len(x_bits)
                total_qubits = total_z + total_x
                
                if total_qubits > 0:
                    z_percent = (total_z / total_qubits) * 100
                    x_percent = (total_x / total_qubits) * 100
                    
                    col_stat1, col_stat2, col_stat3 = st.columns(3)
                    with col_stat1:
                        st.metric("Total Qubits Sent", total_qubits)
                    with col_stat2:
                        st.metric("Z-Basis Qubits", f"{total_z} ({z_percent:.1f}%)")
                    with col_stat3:
                        st.metric("X-Basis Qubits", f"{total_x} ({x_percent:.1f}%)")
                    
                    st.markdown("### Expected vs Actual Distribution")
                    st.markdown(f"""
In a proper BB84 protocol with **truly random basis selection**:

**Expected:**
- Each basis should be chosen ~50% of the time
- Expected Z-basis: {total_qubits * 0.5:.0f} qubits
- Expected X-basis: {total_qubits * 0.5:.0f} qubits

**Actual:**
- Actual Z-basis: {total_z} qubits ({z_percent:.1f}%)
- Actual X-basis: {total_x} qubits ({x_percent:.1f}%)

**Analysis**: The distribution {'confirms' if abs(z_percent - 50) < 5 else 'shows'} {'proper' if abs(z_percent - 50) < 5 else 'non-uniform'} random basis selection in the simulation.
                    """)
                
            except Exception as e:
                logger.error(f"Error in Polarization Analysis: {e}")


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
            © 2026 BB84 Quantum Key Distribution Simulator | AQVH Final Project | All Rights Reserved<br>
            <strong style='color: #1e40af;'>Team Silicon</strong> | JNTUA ECE Department
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
    try:
        _initialize_session_state()
    except Exception as e:
        logger.error(f"Session initialization error: {e}")
        pass
    
    # INJECT RESPONSIVE CSS FOR STREAMLIT CLOUD COMPATIBILITY
    try:
        inject_responsive_css()
    except Exception as e:
        logger.debug(f"CSS injection: {e}")
        pass
    
    # ADVANCED HEADER WITH SESSION TRACKING
    try:
        session_info = _get_session_summary()
        uptime = int(session_info.get("uptime_seconds", 0))
        sims = session_info.get("simulations_run", 0)
        
        col_logo, col_text, col_session = st.columns([1, 3, 1.5])
        
        with col_logo:
            st.image("spy.png", width=100, use_column_width=False)
        
        with col_text:
            st.markdown("""
            <div style='padding: 10px 0;'>
                <h1 style='margin: 0; color: #1e40af; font-size: 28px; font-weight: 900;'>JNTUA BB84 QKD Simulator</h1>
                <p style='margin: 5px 0 0 0; color: #2563eb; font-size: 14px; font-weight: 600;'>Quantum Key Distribution | Cryptography & Security</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_session:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%); padding: 12px; border-radius: 8px; border-left: 3px solid #1e40af; text-align: right;'>
                <p style='margin: 0; color: #1e40af; font-size: 12px; font-weight: 600;'>SESSION INFO</p>
                <p style='margin: 3px 0 0 0; color: #2563eb; font-size: 11px;'>ID: #{session_info.get("session_id", "N/A")}</p>
                <p style='margin: 2px 0 0 0; color: #2563eb; font-size: 11px;'>Simulations: {sims}</p>
                <p style='margin: 2px 0 0 0; color: #2563eb; font-size: 11px;'>Uptime: {uptime}s</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
    except Exception as e:
        logger.debug(f"Header rendering: {e}")
    
    # ADVANCED PLATFORM CAPABILITIES WITH ICONS
    st.markdown("### Platform Capabilities")
    cap_col1, cap_col2, cap_col3 = st.columns(3)
    
    with cap_col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%); padding: 15px; border-radius: 10px; border-left: 4px solid #1e40af;'>
        <strong style='color: #1e40af;'>Quantum Simulation</strong>
        <p style='color: #1a1a1a; font-size: 13px; margin: 5px 0 0 0;'>Complete BB84 protocol execution with quantum mechanics</p>
        </div>
        """, unsafe_allow_html=True)
    
    with cap_col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%); padding: 15px; border-radius: 10px; border-left: 4px solid #1e40af;'>
        <strong style='color: #1e40af;'>Threat Detection</strong>
        <p style='color: #1a1a1a; font-size: 13px; margin: 5px 0 0 0;'>Eavesdropper detection via QBER analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with cap_col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%); padding: 15px; border-radius: 10px; border-left: 4px solid #1e40af;'>
        <strong style='color: #1e40af;'>Intelligence Analytics</strong>
        <p style='color: #1a1a1a; font-size: 13px; margin: 5px 0 0 0;'>Timeline & metrics with visualizations</p>
        </div>
        """, unsafe_allow_html=True)
    
    # ADVANCED SYSTEM STATUS CARDS
    st.markdown("### System Status")
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        try:
            backend, gpu_available = get_quantum_backend()
            backend_name = "GPU (CUDA)" if gpu_available else "CPU"
            st.metric("Quantum Backend", backend_name, "Operational")
        except Exception:
            st.metric("Quantum Backend", "CPU", "Operational")
    
    with status_col2:
        st.metric("Security Mode", "Enabled", "QBER Monitoring Active")
    
    with status_col3:
        session_info = _get_session_summary()
        sim_count = session_info.get("simulations_run", 0)
        st.metric("Session Stats", f"{sim_count} simulations", f"ID: {session_info.get('session_id', 'N/A')}")
    
    st.divider()
    
    # ADVANCED SESSION INFORMATION DISPLAY
    with st.expander("Session & Environment Details", expanded=False):
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.markdown("**Session Information:**")
            session_info = _get_session_summary()
            st.markdown(f"""
            - **Session ID:** `{session_info.get('session_id', 'N/A')}`
            - **Uptime:** {int(session_info.get('uptime_seconds', 0))} seconds
            - **Simulations:** {session_info.get('simulations_run', 0)}
            - **Active Simulation:** {'Yes' if session_info.get('is_simulation_active') else 'No'}
            """)
        
        with col_info2:
            st.markdown("**Current Configuration:**")
            try:
                st.markdown(f"""
                - **Qubits:** {st.session_state.num_bits}
                - **QBER Threshold:** {st.session_state.threshold:.2f}%
                - **Eve Probability:** {st.session_state.eve_prob:.0%}
                - **Noise Level:** {st.session_state.noise_prob:.2%}
                """)
            except:
                st.markdown("Configuration loading...")
    
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

    ### Security: 
    Any eavesdropping introduces detectable errors due to quantum no-cloning theorem.
    
    ### Detailed Protocol Flow:
    ```
    BB84 PROTOCOL PSEUDOCODE:
    
    1. Alice generates N random bits and N random bases
       - bits = [random 0/1 for _ in range(N)]
       - bases = [random Rectilinear/Diagonal for _ in range(N)]
    
    2. Alice encodes and transmits qubits to Bob
       - FOR i in range(N):
           - Encode bits[i] using bases[i]
           - Send qubit through quantum channel
    
    3. Bob measures received qubits
       - FOR i in range(N):
           - Choose random basis (Rectilinear/Diagonal)
           - Measure qubit in chosen basis
           - Record measurement result
    
    4. Alice publicly announces her bases
       - Announce: bases = [b1, b2, ..., bN]
    
    5. Bob publicly announces his bases
       - Announce: bob_bases = [b1, b2, ..., bN]
    
    6. Keep matching basis positions
       - sifted_key = [bits[i] where bases[i] == bob_bases[i]]
    
    7. Estimate Quantum Bit Error Rate (QBER)
       - Test subset of sifted key against Bob's measurements
       - QBER = (errors / sample_size) * 100
    
    8. Check for eavesdropping
       - IF QBER > threshold:
           - Abort protocol (eavesdropping detected)
       - ELSE:
           - Continue to step 9
    
    9. Privacy amplification
       - Apply hash function to remaining sifted key
       - Final secure cryptographic key ready for use
    ```
    """)

    # SIMULATION PARAMETERS SECTION
    st.header("Simulation Configuration")
    
    st.markdown("**Configuration Instructions:** Adjust the parameters below to customize your BB84 simulation.")

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
        pass  # Configuration loaded silently

    # SIMULATION EXECUTION
    st.markdown("---")
    if st.button("**Run BB84 Simulation**", type="primary", use_container_width=True):
        # ONLY RUN SIMULATION ON BUTTON PRESS
        st.session_state.simulation_run = True
        run_bb84_simulation()

    # RESULTS DISPLAY - Only show if simulation completed
    if st.session_state.simulation_completed:
        st.markdown("---")
        st.markdown("### Simulation Results")

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
        st.markdown("Configure parameters above and click **Run BB84 Simulation** to see results.")

    # FOOTER SECTION
    render_footer()


# APP ENTRY POINT
if __name__ == "__main__":
    try:
        # Force initialization before anything else
        _initialize_session_state()
        # Run the app
        main()
    except Exception as e:
        # Silently catch any uncaught exceptions
        error_msg = str(e)
        if 'SessionInfo' not in error_msg and 'Bad message format' not in error_msg:
            logger.error(f"Application error: {error_msg}")
        # Don't raise or display the error to user