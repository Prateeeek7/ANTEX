# Test Case: Antenna Design Optimization Validation

## Test Case ID: TC-001
## Test Name: 2.4 GHz Microstrip Patch Antenna Optimization
## Date: 2025-12-13

---

## Test Objective
Validate that the optimization system correctly generates antenna designs with accurate calculations for:
- Resonant frequency
- Return loss (RL)
- VSWR
- Bandwidth
- Gain
- Impedance matching

---

## Input Parameters

### Project Information
```json
{
  "name": "Test 2.4GHz Patch Antenna",
  "description": "Standard WiFi 2.4GHz patch antenna design test",
  "target_frequency_ghz": 2.4,
  "bandwidth_mhz": 100,
  "max_size_mm": 50.0,
  "substrate": "FR4",
  "substrate_thickness_mm": 1.6,
  "feed_type": "microstrip",
  "polarization": "linear",
  "target_gain_dbi": 6.5,
  "target_impedance_ohm": 50.0,
  "conductor_thickness_um": 35.0
}
```

### Optimization Configuration
```json
{
  "algorithm": "ga",
  "population_size": 20,
  "generations": 30,
  "design_type": "patch"
}
```

### Expected Material Properties (FR4)
```json
{
  "substrate_name": "FR4",
  "permittivity": 4.4,
  "loss_tangent": 0.02,
  "substrate_height_mm": 1.6
}
```

---

## Expected Outcomes

### Resonant Frequency
- **Target**: 2.38 - 2.42 GHz
- **Frequency Error**: < 3%
- **Calculation Formula**: `f_res = c / (2 * L_eff * sqrt(eps_eff))`
  - Where `L_eff = L + 2*ΔL` (accounts for fringing fields)
  - Where `eps_eff = (eps_r + 1)/2 + (eps_r - 1)/2 * (1 + 12*h/W)^(-0.5)`

### Return Loss (RL)
- **Target**: < -10 dB at resonant frequency
- **Minimum**: -15 dB to -20 dB (excellent match)
- **Calculation Formula**: `RL = -20 * log10(|S11|)`
  - Where `S11 = (Z - Z0) / (Z + Z0)`

### VSWR
- **Target**: 1.2 - 1.8 at resonant frequency
- **Excellent**: < 1.5
- **Calculation Formula**: `VSWR = (1 + |S11|) / (1 - |S11|)`

### Bandwidth
- **Target**: 30 - 70 MHz (for 1.6mm FR4 substrate)
- **Calculation**: Bandwidth depends on:
  - Substrate height (h)
  - Dielectric constant (ε_r)
  - Patch dimensions (W × L)

### Gain
- **Target**: 6.0 - 7.0 dBi for FR4
- **Calculation Formula**: `Gain = Efficiency × Directivity`
  - Directivity from aperture: `D = 4π * A_eff / λ²`
  - Efficiency accounts for conductor and dielectric losses

### Impedance
- **Target**: 50 Ω ± 5% (real part)
- **Feed Offset Range**: Typically 0-10 mm from edge

---

## Expected Geometry Parameters (Approximate)

Based on standard microstrip patch antenna design for 2.4 GHz on FR4:

```json
{
  "length_mm": 28.0 - 32.0,
  "width_mm": 35.0 - 40.0,
  "substrate_height_mm": 1.6,
  "feed_offset_mm": 5.0 - 10.0,
  "eps_r": 4.4
}
```

**Note**: These are approximate ranges. The optimizer should find the optimal values.

---

## Validation Criteria

### Must Pass (Critical)
1. ✅ Resonant frequency within 2.38-2.42 GHz range
2. ✅ Frequency error < 3%
3. ✅ Return loss < -10 dB at resonant frequency
4. ✅ VSWR < 2.0 at resonant frequency
5. ✅ Bandwidth > 30 MHz

### Should Pass (Important)
6. ✅ Gain ≥ 6.0 dBi
7. ✅ VSWR < 1.5 (excellent match)
8. ✅ Impedance real part within 45-55 Ω range
9. ✅ Geometry respects max_size_mm constraint (50mm)

### Nice to Have (Optimization Quality)
10. ✅ Gain ≥ 6.5 dBi
11. ✅ Bandwidth ≥ 50 MHz
12. ✅ Frequency error < 2%

---

## Test Execution Steps

### Step 1: Create Project
```bash
POST /api/projects
Content-Type: application/json

{
  "name": "Test 2.4GHz Patch Antenna",
  "description": "Standard WiFi 2.4GHz patch antenna design test",
  "target_frequency_ghz": 2.4,
  "bandwidth_mhz": 100,
  "max_size_mm": 50.0,
  "substrate": "FR4",
  "substrate_thickness_mm": 1.6,
  "feed_type": "microstrip",
  "polarization": "linear",
  "target_gain_dbi": 6.5,
  "target_impedance_ohm": 50.0,
  "conductor_thickness_um": 35.0
}
```

### Step 2: Start Optimization
```bash
POST /api/optimize/start
Content-Type: application/json

{
  "project_id": <project_id_from_step_1>,
  "algorithm": "ga",
  "population_size": 20,
  "generations": 30,
  "design_type": "patch"
}
```

### Step 3: Wait for Completion
- Poll optimization status: `GET /api/optimize/runs/<run_id>`
- Wait for status: "completed" or "failed"

### Step 4: Retrieve Results
```bash
GET /api/optimize/runs/<run_id>/best-candidate
```

### Step 5: Validate Results
Compare actual results against expected outcomes above.

---

## Sample Expected Output (Best Candidate)

```json
{
  "fitness": 85.5,
  "geometry_params": {
    "length_mm": 29.8,
    "width_mm": 37.2,
    "substrate_height_mm": 1.6,
    "feed_offset_mm": 7.5,
    "eps_r": 4.4
  },
  "metrics": {
    "estimated_freq_ghz": 2.398,
    "freq_error_ghz": 0.002,
    "return_loss_dB": -18.5,
    "vswr": 1.28,
    "estimated_bandwidth_mhz": 52.3,
    "gain_estimate_dBi": 6.7,
    "estimated_impedance_ohm": {
      "real": 48.2,
      "imag": 2.1
    },
    "efficiency_percent": 78.5
  }
}
```

---

## Test Case 2: Rogers 5880 High-Performance Design

### Input Parameters
```json
{
  "name": "Test 2.4GHz Rogers 5880 Patch",
  "description": "High-performance patch antenna on Rogers 5880",
  "target_frequency_ghz": 2.4,
  "bandwidth_mhz": 80,
  "max_size_mm": 50.0,
  "substrate": "Rogers RT/duroid 5880",
  "substrate_thickness_mm": 1.6,
  "feed_type": "microstrip",
  "polarization": "linear",
  "target_gain_dbi": 7.5,
  "target_impedance_ohm": 50.0,
  "conductor_thickness_um": 35.0
}
```

### Expected Material Properties (Rogers 5880)
```json
{
  "substrate_name": "Rogers RT/duroid 5880",
  "permittivity": 2.2,
  "loss_tangent": 0.0009,
  "substrate_height_mm": 1.6
}
```

### Expected Outcomes (Rogers 5880)
- **Resonant Frequency**: 2.38 - 2.42 GHz
- **Gain**: 7.0 - 8.0 dBi (higher than FR4 due to lower losses)
- **Bandwidth**: 40 - 60 MHz (typically narrower than FR4)
- **Return Loss**: < -15 dB
- **VSWR**: < 1.5

### Expected Geometry (Approximate)
- **Length**: ~38-42 mm (longer than FR4 due to lower ε_r)
- **Width**: ~40-45 mm

---

## Test Case 3: Edge Case - Tight Size Constraint

### Input Parameters
```json
{
  "name": "Test Compact 2.4GHz Patch",
  "description": "Compact design with tight size constraint",
  "target_frequency_ghz": 2.4,
  "bandwidth_mhz": 50,
  "max_size_mm": 30.0,
  "substrate": "FR4",
  "substrate_thickness_mm": 0.8,
  "feed_type": "microstrip",
  "polarization": "linear",
  "target_gain_dbi": 5.5,
  "target_impedance_ohm": 50.0,
  "conductor_thickness_um": 18.0
}
```

### Expected Outcomes
- Must respect `max_size_mm = 30.0` constraint
- Frequency accuracy may be slightly reduced due to size constraint
- Gain may be lower (5.0-6.0 dBi) due to smaller aperture

---

## Validation Script

Use this Python script to validate test results:

```python
def validate_test_results(actual, expected):
    """Validate actual results against expected outcomes."""
    errors = []
    
    # Frequency validation
    freq = actual['metrics']['estimated_freq_ghz']
    freq_error_pct = abs(freq - expected['target_frequency_ghz']) / expected['target_frequency_ghz'] * 100
    if freq < 2.38 or freq > 2.42:
        errors.append(f"Frequency {freq:.3f}GHz outside range 2.38-2.42 GHz")
    if freq_error_pct > 3.0:
        errors.append(f"Frequency error {freq_error_pct:.2f}% exceeds 3%")
    
    # Return loss validation
    rl = actual['metrics']['return_loss_dB']
    if rl > -10:
        errors.append(f"Return loss {rl:.2f}dB exceeds -10 dB target")
    
    # VSWR validation
    vswr = actual['metrics']['vswr']
    if vswr > 2.0:
        errors.append(f"VSWR {vswr:.2f} exceeds 2.0 target")
    
    # Bandwidth validation
    bw = actual['metrics']['estimated_bandwidth_mhz']
    if bw < 30:
        errors.append(f"Bandwidth {bw:.2f}MHz below 30 MHz minimum")
    
    # Gain validation
    gain = actual['metrics']['gain_estimate_dBi']
    if gain < 6.0:
        errors.append(f"Gain {gain:.2f}dBi below 6.0 dBi target")
    
    # Size constraint validation
    params = actual['geometry_params']
    max_dim = max(params['length_mm'], params['width_mm'])
    if max_dim > expected['max_size_mm']:
        errors.append(f"Max dimension {max_dim:.2f}mm exceeds constraint {expected['max_size_mm']}mm")
    
    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "summary": {
            "frequency_ghz": freq,
            "frequency_error_pct": freq_error_pct,
            "return_loss_dB": rl,
            "vswr": vswr,
            "bandwidth_mhz": bw,
            "gain_dBi": gain,
            "max_dimension_mm": max_dim
        }
    }
```

---

## Notes

1. **Material Properties**: Ensure backend correctly looks up material properties from the material library
2. **Unit Consistency**: Verify all calculations use consistent units (mm, GHz, MHz, dBi, Ω)
3. **Fringing Fields**: Ensure `ΔL` calculation uses correct formula based on W/h ratio
4. **Frequency Dependence**: Verify RL and VSWR calculations depend on frequency offset (f_operating vs f_res)
5. **Gain Model**: Verify gain = efficiency × directivity, using W × L for aperture area

---

## Success Criteria

✅ **Test Passes** if:
- All "Must Pass" criteria are met
- At least 7 out of 9 "Should Pass" criteria are met
- No calculation errors or exceptions occur

❌ **Test Fails** if:
- Any "Must Pass" criteria fails
- Less than 5 "Should Pass" criteria are met
- Optimization run fails or crashes
- Results violate physical constraints (e.g., size limits)

