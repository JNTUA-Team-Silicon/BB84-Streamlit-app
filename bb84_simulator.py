# BB84 Simulator Core Module
import numpy as np
import hashlib
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector
import bb84_config as config

class BB84Simulator:
    """Optimized BB84 Quantum Key Distribution Simulator using Qiskit"""
    
    def __init__(self):
        """Initialize the simulator with optimal settings"""
        try:
            self.simulator = AerSimulator(
                method=config.SIMULATOR_METHOD,
                device=config.SIMULATOR_DEVICE
            )
        except:
            self.simulator = AerSimulator(
                method=config.SIMULATOR_METHOD,
                device="CPU"
            )
    
    @staticmethod
    def encode_qubit(bit, basis):
        """Encode a classical bit into a quantum state
        
        Args:
            bit: Classical bit (0 or 1)
            basis: Basis choice (0=Z, 1=X)
        
        Returns:
            QuantumCircuit: Encoded quantum circuit
        """
        qc = QuantumCircuit(1, 1)
        if int(bit) == 1:
            qc.x(0)
        if int(basis) == 1:
            qc.h(0)
        return qc
    
    def simulate_transmission(self, alice_bits, alice_bases, bob_bases, 
                            eve_present=False, eve_intercept_prob=0.5, 
                            noise_prob=0.0):
        """Simulate quantum transmission of qubits (HIGHLY OPTIMIZED)
        
        This function implements the complete BB84 quantum key distribution protocol
        including optional Eve interception, measurement, and resending.
        
        HOW EVE INTERCEPTION WORKS:
        1. eve_intercept_prob is the probability (0-1) that Eve intercepts each qubit
           - This comes from the EVE slider in the UI (ranges 0% to 100%)
           - Each qubit independently has eve_intercept_prob chance of being intercepted
        
        2. For each intercepted qubit:
           - Eve chooses a random basis (Z or X) - she doesn't know Alice's basis
           - Eve measures the qubit in that basis
           - Result: 50% chance Eve chose correct basis (no error), 50% wrong (introduces error)
           - Eve records her measurement result in eve_results[i]
           - Eve resends a new qubit prepared with her measurement result
        
        3. For non-intercepted qubits:
           - Alice's original qubit travels to Bob unmodified
           - No Eve-introduced errors
        
        IMPACT ON ERROR RATE:
        - If eve_intercept_prob = 0.5 (50%): Eve intercepts ~50% of qubits
          → Expected QBER ≈ 0.5 × 0.25 = 12.5% (0.25 = 25% error when wrong basis)
        - If eve_intercept_prob = 1.0 (100%): Eve intercepts all qubits
          → Expected QBER ≈ 0.25 (25% from Eve's wrong measurements)
        - If eve_intercept_prob = 0.0 (0%): Eve doesn't intercept
          → QBER ≈ noise_prob only (natural quantum noise)
        
        Args:
            alice_bits: Alice's random bits (0 or 1)
            alice_bases: Alice's basis choices (0=Z-basis, 1=X-basis)
            bob_bases: Bob's basis choices (0=Z-basis, 1=X-basis)
            eve_present: Whether Eve is eavesdropping (True/False)
            eve_intercept_prob: Probability Eve intercepts each qubit (0.0 to 1.0)
                               - This parameter is controlled by EVE slider
                               - 0.0 = Eve never intercepts (0%)
                               - 0.5 = Eve intercepts ~50% of qubits
                               - 1.0 = Eve intercepts all qubits (100%)
            noise_prob: Natural quantum channel noise probability
        
        Returns:
            tuple: (bob_results, eve_results)
                   bob_results: List of Bob's measurement outcomes
                   eve_results: List of Eve's measurement outcomes (None if no Eve)
        """
        # Vectorize input conversion with efficient data types
        alice_bits = np.asarray([int(b) for b in list(alice_bits)], dtype=np.int8)
        alice_bases = np.asarray([int(b) for b in list(alice_bases)], dtype=np.int8)
        bob_bases = np.asarray([int(b) for b in list(bob_bases)], dtype=np.int8)
        
        n = len(alice_bits)
        bob_results = np.zeros(n, dtype=np.int8)
        eve_results = np.zeros(n, dtype=np.int8) if eve_present else None
        eve_bases = None
        eve_intercepts = None
        
        if eve_present:
            eve_bases = np.random.randint(0, 2, n, dtype=np.int8)
            # Pre-generate all intercept decisions for vectorization
            # eve_intercepts[i] = True if Eve intercepts qubit i, False otherwise
            # Probability of True is eve_intercept_prob
            # This means: for n qubits, approximately n*eve_intercept_prob will be True
            eve_intercepts = np.random.random(n) < eve_intercept_prob
        
        # Optimized batch processing for maximum speed
        batch_size = config.BATCH_SIZE
        
        for batch_start in range(0, n, batch_size):
            batch_end = min(batch_start + batch_size, n)
            batch_indices = np.arange(batch_start, batch_end)
            
            circuits = []
            
            for i in batch_indices:
                qc = QuantumCircuit(1, 1)
                
                # Encode Alice's bit into circuit
                if alice_bits[i] == 1:
                    qc.x(0)
                
                # CRITICAL SECTION: EVE INTERCEPTION LOGIC
                # Handle Eve interception if present and if she intercepts THIS qubit
                if eve_present and eve_intercepts[i]:
                    # ===== EVE MEASURES THE QUBIT =====
                    # Eve doesn't know which basis Alice used (it's secret!)
                    # So Eve chooses a random basis (Z or X)
                    if eve_bases[i] == 1:  # If Eve chose X-basis
                        qc.h(0)  # Apply Hadamard gate to measure in X-basis
                    
                    qc.measure(0, 0)  # Measure the qubit
                    # Run the measurement quantum circuit
                    job_eve = self.simulator.run(transpile(qc, self.simulator), shots=1)
                    res_eve = job_eve.result().get_counts()
                    eve_results[i] = int(list(res_eve.keys())[0])  # Record Eve's measurement
                    
                    # ERROR INTRODUCTION HAPPENS HERE:
                    # If eve_bases[i] == alice_bases[i] (50% chance): Eve gets CORRECT bit
                    # If eve_bases[i] != alice_bases[i] (50% chance): Eve gets RANDOM bit
                    # When Eve got wrong bit and resends it, Bob will measure it wrong
                    # This introduces ~25% error in final sifted key
                    
                    # ===== EVE RESENDS THE QUBIT =====
                    # Create a NEW qubit based on Eve's measurement result
                    # This qubit will be sent to Bob (not Alice's original qubit)
                    qc = QuantumCircuit(1, 1)
                    if eve_results[i] == 1:  # If Eve measured 1
                        qc.x(0)  # Prepare bit 1
                    if eve_bases[i] == 1:  # In Eve's chosen basis
                        qc.h(0)  # Prepare in X-basis if Eve chose X
                    
                    # Important: Bob will now measure this Eve-resent qubit (not Alice's original)
                    
                else:
                    # Eve doesn't intercept this qubit
                    # Alice's original qubit travels unmodified to Bob
                    # Apply Alice's basis so Bob receives the correctly-encoded qubit
                    if alice_bases[i] == 1:
                        qc.h(0)
                
                # Apply Bob's measurement basis
                if bob_bases[i] == 1:
                    qc.h(0)
                qc.measure(0, 0)
                circuits.append(qc)
            
            # Run batch with optimized transpilation (level 3 for maximum optimization)
            if circuits:
                transpiled = transpile(circuits, self.simulator, optimization_level=3)
                job = self.simulator.run(transpiled, shots=1)
                results = job.result()
                
                for idx, i in enumerate(batch_indices):
                    counts = results.get_counts(idx)
                    bob_results[i] = int(list(counts.keys())[0])
                    
                    # Apply channel noise efficiently
                    if noise_prob > 0 and np.random.random() < noise_prob:
                        bob_results[i] = 1 - bob_results[i]
        
        return bob_results.tolist(), eve_results.tolist() if eve_present else None
    
    @staticmethod
    def privacy_amplification(sifted_key, error_rate, 
                            target_security_level=None):
        """Apply privacy amplification via hashing (IMPROVED)
        
        PRIVACY AMPLIFICATION: Final security hardening step
        
        PURPOSE:
        After removing sifted bits with detected errors, the remaining key might still
        have partial information leaked to Eve. Privacy amplification removes this.
        
        HOW IT WORKS:
        1. Uses Shannon entropy to calculate information Eve might have about sifted key
           - If error_rate = 0%: Eve learned nothing (h_eve = 0.0)
           - If error_rate = 25%: Eve learned some bits (h_eve > 0)
           - Formula: h_eve = -e*log2(e) - (1-e)*log2(1-e)
        
        2. Computes secure key length:
           - secure_length = n * (1 - h_eve) - security_margin
           - Example: if n=100, h_eve=0.5: secure_length ≈ 50 - margin ≈ 40 bits
        
        3. Hashes the sifted key using SHA-256:
           - SHA-256 produces 256 bits of cryptographically secure output
           - Even if Eve knows 50% of input, hash output is completely unknown
           - This removes her partial information advantage
        
        4. Extracts final key from hash:
           - Takes first secure_length bits from SHA-256 hash
           - If more bits needed, uses SHA-512 as secondary source
        
        RESULT:
        - Eve's partial information is eliminated
        - Key length is reduced but security is guaranteed
        - Even against quantum computers, security is maintained
        
        Args:
            sifted_key: The sifted key bits (from matched bases)
            error_rate: Quantum bit error rate (QBER)
                       - Used to estimate Eve's information gain
                       - 0% error → Eve learned nothing
                       - 25% error → Eve has some knowledge
            target_security_level: Target security parameter (default 1e-6)
                                 - Probability of successful attack allowed
        
        Returns:
            list: Amplified secure key bits (smaller but unconditionally secure)
        """
        if target_security_level is None:
            target_security_level = config.TARGET_SECURITY_LEVEL
            
        sifted_key = np.array([int(b) for b in list(sifted_key)], dtype=np.int8)
        n = len(sifted_key)
        if n == 0:
            return []

        # Improved Shannon entropy calculation
        e = float(np.clip(error_rate, 0.0, 1.0))
        if e <= 0.0 or e >= 1.0:
            h_eve = 0.0
        else:
            # Use more accurate entropy formula
            h_eve = -e * np.log2(e) - (1 - e) * np.log2(1 - e)

        # Compute secure key length with safety margin
        secure_length = n * (1 - h_eve) - 2 * np.log2(1 / float(target_security_level))
        secure_length = max(0, int(secure_length))

        if secure_length == 0:
            return []

        # Use SHA-256 for better hash properties
        key_str = ''.join(str(int(b)) for b in sifted_key)
        digest = hashlib.sha256(key_str.encode()).hexdigest()
        binary_hash = bin(int(digest, 16))[2:].zfill(256)
        
        # Extract secure bits with additional hashing if needed
        final_bits = [int(b) for b in binary_hash[:secure_length]]
        
        # If need more bits, use SHA-512 as secondary source
        if secure_length > 256:
            digest2 = hashlib.sha512(key_str.encode()).hexdigest()
            binary_hash2 = bin(int(digest2, 16))[2:].zfill(512)
            final_bits.extend([int(b) for b in binary_hash2[:secure_length - 256]])

        return final_bits[:secure_length]
    
    @staticmethod
    def assess_security(qber, threshold=None):
        """Assess security based on QBER (Quantum Bit Error Rate)
        
        ERROR DETECTION AND SECURITY DECISION:
        
        QBER is the KEY SECURITY METRIC:
        - QBER = (Number of Errors in Sifted Key) / (Total Sifted Key Bits)
        - It reveals eavesdropping presence
        
        WHY QBER DETECTS EVE:
        1. Without Eve (eve_intercept_prob = 0%):
           - QBER ≈ 0-1% (only natural quantum noise)
           - Expected QBER formula: 0 × 0.25 + noise ≈ 1%
        
        2. With Eve intercepting (eve_intercept_prob = 50%):
           - Eve introduces ~25% error when she measures wrong basis
           - Expected QBER = 0.5 × 0.25 + noise ≈ 12.5%
           - Formula: eve_prob × 0.25 + channel_noise
        
        3. With Eve intercepting all (eve_intercept_prob = 100%):
           - Expected QBER = 1.0 × 0.25 + noise ≈ 25.1%
        
        SECURITY THRESHOLD (default 11%):
        - Threshold is placed between:
          * No-eavesdropping QBER (1%)
          * With-eavesdropping QBER (25%)
        - Position at 11% catches eavesdropping with high confidence
        
        DECISION LOGIC:
        - If QBER ≤ threshold (11%): SECURE → Proceed with key
        - If QBER > threshold (11%): INSECURE → Abort and retry
        
        This is how eavesdropping is DETECTED:
        Eve CANNOT avoid introducing detectable errors because:
        - She must measure without knowing the basis (50% wrong)
        - Wrong measurement resend causes Bob's measurement errors
        - Errors accumulate in QBER calculation
        - QBER > threshold triggers alarm
        
        Args:
            qber: Quantum bit error rate (0.0 to 1.0)
            threshold: QBER threshold for security decision
                      - Default: 0.11 (11%)
                      - Below this: SECURE (proceed)
                      - Above this: INSECURE (abort)
        
        Returns:
            dict: Security assessment with:
                  - status: 'SECURE' or 'INSECURE'
                  - message: Human-readable explanation
                  - action: 'PROCEED_WITH_KEY' or 'ABORT_AND_RETRY'
                  - color: 'green' or 'red' for UI display
        """
        
        Returns:
            dict: Security assessment
        """
        if threshold is None:
            threshold = config.DEFAULT_QBER_THRESHOLD
            
        if qber <= threshold:
            return {
                'status': 'SECURE',
                'message': f'QBER ({qber:.3f}) below threshold. Key exchange successful.',
                'action': 'PROCEED_WITH_KEY',
                'color': 'green'
            }

        return {
            'status': 'INSECURE',
            'message': f'QBER ({qber:.3f}) exceeds threshold ({threshold}). Eavesdropping suspected.',
            'action': 'ABORT_AND_RETRY',
            'color': 'red'
        }
    
    @staticmethod
    def get_statevector_from_bit_basis(bit, basis):
        """Get Statevector for given bit and basis
        
        Args:
            bit: Classical bit (0 or 1)
            basis: Basis choice (0=Z, 1=X)
        
        Returns:
            Statevector: Quantum state vector
        """
        qc = QuantumCircuit(1)
        if int(bit) == 1:
            qc.x(0)
        if int(basis) == 1:
            qc.h(0)
        return Statevector.from_instruction(qc)
    
    @staticmethod
    def state_label(bit, basis):
        """Get human-readable label for quantum state
        
        Args:
            bit: Classical bit
            basis: Basis choice
        
        Returns:
            str: State label with notation
        """
        if int(basis) == 0:
            return "|0⟩ (Z)" if int(bit) == 0 else "|1⟩ (Z)"
        return "|+⟩ (X)" if int(bit) == 0 else "|−⟩ (X)"
