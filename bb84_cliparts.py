# Professional SVG Cliparts for BB84 Simulator
# Advanced quantum computing and cryptography graphics

def get_quantum_bit_svg():
    """Professional quantum bit (qubit) visualization"""
    return """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100" height="100">
        <!-- Background circle -->
        <circle cx="100" cy="100" r="95" fill="#f0f4ff" stroke="#2563eb" stroke-width="2"/>
        
        <!-- Quantum state visualization -->
        <g opacity="0.3">
            <circle cx="100" cy="100" r="60" fill="none" stroke="#7c3aed" stroke-width="1" stroke-dasharray="5,5"/>
            <circle cx="100" cy="100" r="45" fill="none" stroke="#7c3aed" stroke-width="1" stroke-dasharray="5,5"/>
            <circle cx="100" cy="100" r="30" fill="none" stroke="#7c3aed" stroke-width="1" stroke-dasharray="5,5"/>
        </g>
        
        <!-- Central core -->
        <circle cx="100" cy="100" r="20" fill="#2563eb" stroke="#1e40af" stroke-width="2"/>
        <circle cx="100" cy="100" r="12" fill="#60a5fa" opacity="0.6"/>
        
        <!-- Quantum probability waves -->
        <path d="M 60 100 Q 70 85, 80 100 T 100 100 T 120 100 T 140 100" fill="none" stroke="#7c3aed" stroke-width="2" opacity="0.7"/>
        <path d="M 100 60 Q 115 70, 100 80 T 100 100 T 100 120 T 100 140" fill="none" stroke="#7c3aed" stroke-width="2" opacity="0.7"/>
        
        <!-- Text label -->
        <text x="100" y="170" font-size="12" font-weight="bold" text-anchor="middle" fill="#1e40af">QUBIT</text>
    </svg>
    """

def get_encryption_lock_svg():
    """Professional encryption lock"""
    return """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100" height="100">
        <!-- Background -->
        <rect x="20" y="20" width="160" height="160" rx="20" fill="#f0f4ff" stroke="#059669" stroke-width="2"/>
        
        <!-- Lock body -->
        <rect x="60" y="90" width="80" height="70" rx="5" fill="#059669" stroke="#047857" stroke-width="2"/>
        
        <!-- Lock shackle (top arc) -->
        <path d="M 80 90 Q 80 40, 120 40 Q 160 40, 160 90" fill="none" stroke="#059669" stroke-width="8" stroke-linecap="round"/>
        
        <!-- Lock keyhole -->
        <circle cx="100" cy="115" r="8" fill="#fef3c7" stroke="#f59e0b" stroke-width="2"/>
        <rect x="98" y="125" width="4" height="20" fill="#f59e0b"/>
        
        <!-- Glow effect -->
        <circle cx="100" cy="100" r="75" fill="none" stroke="#059669" stroke-width="1" opacity="0.2"/>
        
        <!-- Text -->
        <text x="100" y="170" font-size="12" font-weight="bold" text-anchor="middle" fill="#047857">SECURE</text>
    </svg>
    """

def get_key_exchange_svg():
    """Professional key exchange visualization"""
    return """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 150" width="300" height="150">
        <!-- Background -->
        <rect width="300" height="150" fill="#f8f9fa" stroke="#2563eb" stroke-width="2" rx="10"/>
        
        <!-- Alice side -->
        <circle cx="50" cy="75" r="25" fill="#2563eb" stroke="#1e40af" stroke-width="2"/>
        <text x="50" y="82" font-size="14" font-weight="bold" text-anchor="middle" fill="white">ALICE</text>
        
        <!-- Key symbol Alice -->
        <g transform="translate(30, 50)">
            <path d="M 0 5 L 15 5 L 15 8 L 0 8 Z" fill="#7c3aed" stroke="#6d28d9" stroke-width="1"/>
            <circle cx="8" cy="6.5" r="3" fill="#7c3aed" stroke="#6d28d9" stroke-width="1"/>
        </g>
        
        <!-- Exchange arrow -->
        <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                <polygon points="0 0, 10 3, 0 6" fill="#2563eb"/>
            </marker>
        </defs>
        <line x1="80" y1="75" x2="220" y2="75" stroke="#2563eb" stroke-width="3" marker-end="url(#arrowhead)"/>
        <line x1="220" y1="80" x2="80" y2="80" stroke="#7c3aed" stroke-width="3" marker-end="url(#arrowhead)" opacity="0.6"/>
        
        <!-- Protocol labels -->
        <text x="150" y="60" font-size="11" font-weight="bold" text-anchor="middle" fill="#2563eb">Quantum Channel</text>
        <text x="150" y="100" font-size="11" font-weight="bold" text-anchor="middle" fill="#7c3aed">Public Channel</text>
        
        <!-- Bob side -->
        <circle cx="250" cy="75" r="25" fill="#2563eb" stroke="#1e40af" stroke-width="2"/>
        <text x="250" y="82" font-size="14" font-weight="bold" text-anchor="middle" fill="white">BOB</text>
        
        <!-- Key symbol Bob -->
        <g transform="translate(270, 50)">
            <path d="M 0 5 L 15 5 L 15 8 L 0 8 Z" fill="#7c3aed" stroke="#6d28d9" stroke-width="1"/>
            <circle cx="8" cy="6.5" r="3" fill="#7c3aed" stroke="#6d28d9" stroke-width="1"/>
        </g>
    </svg>
    """

def get_protocol_steps_svg():
    """Professional protocol steps visualization"""
    return """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 500" width="100%" height="500">
        <!-- Title -->
        <text x="200" y="30" font-size="18" font-weight="bold" text-anchor="middle" fill="#1e40af">BB84 Protocol Steps</text>
        
        <!-- Step 1 -->
        <g>
            <circle cx="60" cy="80" r="25" fill="#2563eb" stroke="#1e40af" stroke-width="2"/>
            <text x="60" y="87" font-size="16" font-weight="bold" text-anchor="middle" fill="white">1</text>
            <rect x="100" y="60" width="280" height="40" fill="#dbeafe" stroke="#2563eb" stroke-width="1" rx="5"/>
            <text x="240" y="85" font-size="13" font-weight="600" fill="#1e40af">Generate Random Bits & Bases (Alice)</text>
        </g>
        
        <!-- Step 2 -->
        <g>
            <circle cx="60" cy="160" r="25" fill="#2563eb" stroke="#1e40af" stroke-width="2"/>
            <text x="60" y="167" font-size="16" font-weight="bold" text-anchor="middle" fill="white">2</text>
            <rect x="100" y="140" width="280" height="40" fill="#dbeafe" stroke="#2563eb" stroke-width="1" rx="5"/>
            <text x="240" y="165" font-size="13" font-weight="600" fill="#1e40af">Encode & Transmit Qubits (Quantum Channel)</text>
        </g>
        
        <!-- Step 3 -->
        <g>
            <circle cx="60" cy="240" r="25" fill="#7c3aed" stroke="#6d28d9" stroke-width="2"/>
            <text x="60" y="247" font-size="16" font-weight="bold" text-anchor="middle" fill="white">3</text>
            <rect x="100" y="220" width="280" height="40" fill="#ede9fe" stroke="#7c3aed" stroke-width="1" rx="5"/>
            <text x="240" y="245" font-size="13" font-weight="600" fill="#6d28d9">Measure Qubits with Random Bases (Bob)</text>
        </g>
        
        <!-- Step 4 -->
        <g>
            <circle cx="60" cy="320" r="25" fill="#7c3aed" stroke="#6d28d9" stroke-width="2"/>
            <text x="60" y="327" font-size="16" font-weight="bold" text-anchor="middle" fill="white">4</text>
            <rect x="100" y="300" width="280" height="40" fill="#ede9fe" stroke="#7c3aed" stroke-width="1" rx="5"/>
            <text x="240" y="325" font-size="13" font-weight="600" fill="#6d28d9">Public Base Announcement (No Bits Revealed)</text>
        </g>
        
        <!-- Step 5 -->
        <g>
            <circle cx="60" cy="400" r="25" fill="#059669" stroke="#047857" stroke-width="2"/>
            <text x="60" y="407" font-size="16" font-weight="bold" text-anchor="middle" fill="white">5</text>
            <rect x="100" y="380" width="280" height="40" fill="#d1fae5" stroke="#059669" stroke-width="1" rx="5"/>
            <text x="240" y="405" font-size="13" font-weight="600" fill="#047857">Sift, Check QBER & Generate Final Key</text>
        </g>
    </svg>
    """

def get_security_status_svg(secure=True):
    """Professional security status indicator"""
    status_color = "#059669" if secure else "#dc2626"
    status_label = "SECURE" if secure else "COMPROMISED"
    status_text = "No eavesdropping detected" if secure else "Eavesdropping detected"
    
    return f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 150" width="300" height="150">
        <!-- Background -->
        <rect width="300" height="150" fill="#f8f9fa" stroke="{status_color}" stroke-width="3" rx="10"/>
        
        <!-- Status indicator circle -->
        <circle cx="60" cy="75" r="35" fill="{status_color}" opacity="0.2" stroke="{status_color}" stroke-width="2"/>
        <circle cx="60" cy="75" r="25" fill="{status_color}"/>
        
        <!-- Checkmark or X -->
        {"<path d='M 45 75 L 55 85 L 75 65' fill='none' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/>" if secure else "<path d='M 45 60 L 75 90 M 75 60 L 45 90' fill='none' stroke='white' stroke-width='4' stroke-linecap='round'/>"}
        
        <!-- Status text -->
        <text x="150" y="70" font-size="20" font-weight="bold" fill="{status_color}">{status_label}</text>
        <text x="150" y="100" font-size="13" fill="#666">{status_text}</text>
    </svg>
    """

def get_qber_gauge_svg(qber_percent, threshold):
    """Professional QBER gauge visualization"""
    qber_decimal = qber_percent / 100
    gauge_color = "#059669" if qber_percent < threshold else "#dc2626"
    
    return f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="300" height="200">
        <!-- Background -->
        <rect width="300" height="200" fill="#f8f9fa" stroke="#2563eb" stroke-width="2" rx="10"/>
        
        <!-- Gauge background arc -->
        <path d="M 50 150 A 100 100 0 0 1 250 150" fill="none" stroke="#e5e7eb" stroke-width="20" stroke-linecap="round"/>
        
        <!-- Safe zone (green) -->
        <path d="M 50 150 A 100 100 0 0 1 180 60" fill="none" stroke="#059669" stroke-width="20" stroke-linecap="round"/>
        
        <!-- Danger zone (red) -->
        <path d="M 180 60 A 100 100 0 0 1 250 150" fill="none" stroke="#dc2626" stroke-width="20" stroke-linecap="round"/>
        
        <!-- Threshold line -->
        <line x1="150" y1="50" x2="150" y2="80" stroke="#2563eb" stroke-width="3"/>
        <text x="150" y="100" font-size="11" font-weight="bold" text-anchor="middle" fill="#2563eb">Threshold: {threshold:.1f}%</text>
        
        <!-- Gauge needle -->
        <g transform="translate(150, 150)">
            <line x1="0" y1="0" x2="0" y2="-80" stroke="{gauge_color}" stroke-width="4" stroke-linecap="round" transform="rotate({qber_decimal * 180 - 90})"/>
            <circle cx="0" cy="0" r="8" fill="{gauge_color}"/>
        </g>
        
        <!-- QBER value display -->
        <text x="150" y="175" font-size="24" font-weight="bold" text-anchor="middle" fill="{gauge_color}">{qber_percent:.2f}%</text>
        <text x="150" y="195" font-size="12" text-anchor="middle" fill="#666">QBER</text>
    </svg>
    """

def get_bloch_sphere_svg():
    """Professional Bloch sphere representation"""
    return """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 250 250" width="250" height="250">
        <!-- Outer sphere -->
        <circle cx="125" cy="125" r="100" fill="#f0f4ff" stroke="#2563eb" stroke-width="2"/>
        <ellipse cx="125" cy="125" rx="100" ry="30" fill="none" stroke="#2563eb" stroke-width="1" opacity="0.3"/>
        
        <!-- Axes -->
        <line x1="25" y1="125" x2="225" y2="125" stroke="#2563eb" stroke-width="2" opacity="0.5"/>
        <line x1="125" y1="25" x2="125" y2="225" stroke="#2563eb" stroke-width="2" opacity="0.5"/>
        
        <!-- Axis labels -->
        <text x="230" y="130" font-size="12" font-weight="bold" fill="#2563eb">X</text>
        <text x="120" y="20" font-size="12" font-weight="bold" fill="#2563eb">Z</text>
        
        <!-- Quantum state point -->
        <circle cx="170" cy="90" r="6" fill="#7c3aed" stroke="#6d28d9" stroke-width="2"/>
        
        <!-- State vector line -->
        <line x1="125" y1="125" x2="170" y2="90" stroke="#7c3aed" stroke-width="2" stroke-dasharray="5,5"/>
        
        <!-- Rotation arcs -->
        <path d="M 140 125 A 15 15 0 0 0 155 110" fill="none" stroke="#059669" stroke-width="1" opacity="0.5" stroke-dasharray="3,3"/>
        
        <!-- Label -->
        <text x="125" y="230" font-size="13" font-weight="bold" text-anchor="middle" fill="#1e40af">Bloch Sphere</text>
    </svg>
    """

def get_timeline_comparison_svg():
    """Professional timeline comparison visualization"""
    return """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="300">
        <!-- Title -->
        <text x="200" y="25" font-size="16" font-weight="bold" text-anchor="middle" fill="#1e40af">Alice vs Bob - Basis Comparison</text>
        
        <!-- Alice row -->
        <text x="20" y="70" font-size="13" font-weight="bold" fill="#1e40af">Alice:</text>
        
        <!-- Alice qubits -->
        <g id="alice-bits">
            <rect x="80" y="55" width="20" height="20" fill="#2563eb" stroke="#1e40af" stroke-width="1" rx="2"/>
            <text x="90" y="68" font-size="10" text-anchor="middle" fill="white" font-weight="bold">Z</text>
            
            <rect x="110" y="55" width="20" height="20" fill="#2563eb" stroke="#1e40af" stroke-width="1" rx="2"/>
            <text x="120" y="68" font-size="10" text-anchor="middle" fill="white" font-weight="bold">X</text>
            
            <rect x="140" y="55" width="20" height="20" fill="#2563eb" stroke="#1e40af" stroke-width="1" rx="2"/>
            <text x="150" y="68" font-size="10" text-anchor="middle" fill="white" font-weight="bold">Z</text>
            
            <rect x="170" y="55" width="20" height="20" fill="#2563eb" stroke="#1e40af" stroke-width="1" rx="2"/>
            <text x="180" y="68" font-size="10" text-anchor="middle" fill="white" font-weight="bold">X</text>
            
            <text x="210" y="68" font-size="11" font-weight="bold" fill="#1e40af">...</text>
        </g>
        
        <!-- Bob row -->
        <text x="20" y="150" font-size="13" font-weight="bold" fill="#7c3aed">Bob:</text>
        
        <!-- Bob measurements -->
        <g id="bob-bits">
            <rect x="80" y="135" width="20" height="20" fill="#7c3aed" stroke="#6d28d9" stroke-width="1" rx="2"/>
            <text x="90" y="148" font-size="10" text-anchor="middle" fill="white" font-weight="bold">Z</text>
            
            <rect x="110" y="135" width="20" height="20" fill="#f97316" stroke="#ea580c" stroke-width="1" rx="2"/>
            <text x="120" y="148" font-size="10" text-anchor="middle" fill="white" font-weight="bold">Z</text>
            
            <rect x="140" y="135" width="20" height="20" fill="#7c3aed" stroke="#6d28d9" stroke-width="1" rx="2"/>
            <text x="150" y="148" font-size="10" text-anchor="middle" fill="white" font-weight="bold">Z</text>
            
            <rect x="170" y="135" width="20" height="20" fill="#7c3aed" stroke="#6d28d9" stroke-width="1" rx="2"/>
            <text x="180" y="148" font-size="10" text-anchor="middle" fill="white" font-weight="bold">X</text>
            
            <text x="210" y="148" font-size="11" font-weight="bold" fill="#7c3aed">...</text>
        </g>
        
        <!-- Match indicators -->
        <g id="matches">
            <circle cx="90" cy="105" r="5" fill="#059669"/>
            <text x="120" y="108" font-size="10" fill="#dc2626">✗</text>
            <circle cx="150" cy="105" r="5" fill="#059669"/>
            <circle cx="180" cy="105" r="5" fill="#059669"/>
        </g>
        
        <!-- Legend -->
        <text x="30" y="220" font-size="11" font-weight="600" fill="#059669">● Match (Keep)</text>
        <text x="30" y="245" font-size="11" font-weight="600" fill="#dc2626">✗ No Match (Discard)</text>
        <text x="30" y="270" font-size="11" font-weight="600" fill="#2563eb">Z = Rectilinear, X = Diagonal</text>
    </svg>
    """
