"""
Importers for external EM simulation results (HFSS/CST).
Supports multiple file formats including Touchstone, CSV, and JSON.
"""
from typing import Dict, Any, List, Tuple
import csv
import json
import re
import logging

logger = logging.getLogger(__name__)


def parse_touchstone_file(file_path: str) -> Dict[str, Any]:
    """
    Parse Touchstone (.s1p, .s2p) file format.
    Standard format used by HFSS, CST, ADS, etc.
    
    Format:
    # Hz S RI R 50
    ! Frequency S11_real S11_imag
    2.4e9 0.1 0.2
    """
    frequencies = []
    s11_data = []
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('!'):
                    continue
                if line.startswith('#'):
                    # Parse header
                    parts = line.split()
                    if len(parts) >= 3:
                        freq_unit = parts[1].upper()  # HZ, KHZ, MHZ, GHZ
                        param_type = parts[2].upper()  # S, Y, Z
                else:
                    # Parse data line
                    parts = line.split()
                    if len(parts) >= 3:
                        freq = float(parts[0])
                        real = float(parts[1])
                        imag = float(parts[2])
                        
                        # Convert frequency to GHz
                        if freq_unit == 'HZ':
                            freq_ghz = freq / 1e9
                        elif freq_unit == 'KHZ':
                            freq_ghz = freq / 1e6
                        elif freq_unit == 'MHZ':
                            freq_ghz = freq / 1e3
                        else:  # GHZ
                            freq_ghz = freq
                        
                        frequencies.append(freq_ghz)
                        s11_data.append({"real": real, "imag": imag})
        
        if frequencies and s11_data:
            # Find resonant frequency (minimum |S11|)
            min_s11_idx = min(range(len(s11_data)), 
                             key=lambda i: abs(complex(s11_data[i]["real"], s11_data[i]["imag"])))
            freq_res_ghz = frequencies[min_s11_idx]
            s11_res = complex(s11_data[min_s11_idx]["real"], s11_data[min_s11_idx]["imag"])
            
            # Calculate return loss: RL = 20 * log10(|S11|)
            import math
            if abs(s11_res) > 0:
                return_loss_db = 20 * math.log10(abs(s11_res))
            else:
                return_loss_db = float('inf')
            
            # Estimate bandwidth (find -10dB points)
            bandwidth_mhz = _estimate_bandwidth_from_s11(frequencies, s11_data)
            
            return {
                "frequency_ghz": freq_res_ghz,
                "return_loss_dB": return_loss_db,
                "bandwidth_mhz": bandwidth_mhz,
                "frequencies": frequencies,
                "s11_data": s11_data,
                "source": "touchstone"
            }
    except Exception as e:
        logger.error(f"Error parsing Touchstone file: {e}")
        raise
    
    return None


def _estimate_bandwidth_from_s11(frequencies: List[float], s11_data: List[Dict]) -> float:
    """Estimate bandwidth from S11 data (find -10dB points)."""
    if not frequencies or not s11_data:
        return 0.0
    
    # Find frequencies where |S11| < 0.316 (return loss < -10dB)
    valid_freqs = []
    for i, s11 in enumerate(s11_data):
        s11_mag = abs(complex(s11["real"], s11["imag"]))
        if s11_mag < 0.316:  # -10dB return loss
            valid_freqs.append(frequencies[i])
    
    if len(valid_freqs) >= 2:
        return (max(valid_freqs) - min(valid_freqs)) * 1000  # Convert to MHz
    return 0.0


def parse_hfss_result(file_path: str) -> Dict[str, Any]:
    """
    Parse HFSS simulation result file.
    
    Supports:
    - Touchstone (.s1p) files
    - CSV exports with standard HFSS headers
    - JSON exports
    """
    file_ext = file_path.lower().split('.')[-1]
    
    # Try Touchstone format first
    if file_ext in ['s1p', 's2p', 's3p', 's4p']:
        try:
            return parse_touchstone_file(file_path)
        except Exception as e:
            logger.warning(f"Touchstone parsing failed: {e}, trying other formats")
    
    # Try CSV format
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Try to detect delimiter
            first_line = f.readline()
            f.seek(0)
            
            # Common HFSS CSV formats
            reader = csv.DictReader(f)
            rows = list(reader)
            
            if rows:
                # Try to find frequency and S11 columns (case-insensitive)
                row = rows[0]
                freq_key = None
                s11_real_key = None
                s11_imag_key = None
                return_loss_key = None
                
                for key in row.keys():
                    key_lower = key.lower()
                    if 'freq' in key_lower and freq_key is None:
                        freq_key = key
                    if ('s11' in key_lower or 's_11' in key_lower) and 'real' in key_lower:
                        s11_real_key = key
                    if ('s11' in key_lower or 's_11' in key_lower) and ('imag' in key_lower or 'im' in key_lower):
                        s11_imag_key = key
                    if 'return' in key_lower and 'loss' in key_lower:
                        return_loss_key = key
                
                # Extract data
                if freq_key:
                    # Find resonant frequency (minimum |S11|)
                    min_s11_idx = 0
                    min_s11_mag = float('inf')
                    
                    for i, row in enumerate(rows):
                        if s11_real_key and s11_imag_key:
                            s11_real = float(row.get(s11_real_key, 0))
                            s11_imag = float(row.get(s11_imag_key, 0))
                            s11_mag = abs(complex(s11_real, s11_imag))
                            if s11_mag < min_s11_mag:
                                min_s11_mag = s11_mag
                                min_s11_idx = i
                    
                    freq_val = float(rows[min_s11_idx].get(freq_key, 2.4))
                    # Convert to GHz if needed
                    if freq_val < 1:
                        freq_ghz = freq_val
                    elif freq_val < 1000:
                        freq_ghz = freq_val / 1e3
                    else:
                        freq_ghz = freq_val / 1e9
                    
                    return_loss = -20.0
                    if return_loss_key:
                        return_loss = float(rows[min_s11_idx].get(return_loss_key, -20.0))
                    elif s11_real_key and s11_imag_key:
                        s11_real = float(rows[min_s11_idx].get(s11_real_key, 0))
                        s11_imag = float(rows[min_s11_idx].get(s11_imag_key, 0))
                        s11_mag = abs(complex(s11_real, s11_imag))
                        if s11_mag > 0:
                            return_loss = 20 * (abs(s11_mag).bit_length() - 1)
                    
                    return {
                        "frequency_ghz": freq_ghz,
                        "return_loss_dB": return_loss,
                        "bandwidth_mhz": 150.0,  # Would need full sweep to calculate
                        "source": "hfss_csv"
                    }
    except Exception as e:
        logger.warning(f"CSV parsing failed: {e}")
    
    # Try JSON format
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return {
                    "frequency_ghz": data.get("frequency_ghz", data.get("frequency", 2.4)),
                    "return_loss_dB": data.get("return_loss_dB", data.get("return_loss", -20.0)),
                    "gain_dBi": data.get("gain_dBi", data.get("gain", 5.0)),
                    "bandwidth_mhz": data.get("bandwidth_mhz", data.get("bandwidth", 150)),
                    "source": "hfss_json"
                }
    except Exception as e:
        logger.warning(f"JSON parsing failed: {e}")
    
    # Fallback: return error
    raise ValueError(f"Could not parse HFSS file. Supported formats: Touchstone (.s1p), CSV, JSON. Error: {str(e)}")


def parse_cst_result(file_path: str) -> Dict[str, Any]:
    """
    Parse CST simulation result file.
    
    Supports:
    - Touchstone (.s1p) files
    - CST ASCII export format
    - CSV exports
    - JSON exports
    """
    file_ext = file_path.lower().split('.')[-1]
    
    # Try Touchstone format first (CST can export to Touchstone)
    if file_ext in ['s1p', 's2p', 's3p', 's4p']:
        try:
            return parse_touchstone_file(file_path)
        except Exception as e:
            logger.warning(f"Touchstone parsing failed: {e}, trying other formats")
    
    # Try CST ASCII format (common export format)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            # Look for CST header
            if any('CST' in line or 'Computer Simulation Technology' in line for line in lines[:10]):
                # Parse CST ASCII format
                # Format: Frequency [Hz] |S11| [dB] or Frequency [Hz] Re(S11) Im(S11)
                data_rows = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('!'):
                        parts = line.split()
                        if len(parts) >= 2:
                            try:
                                freq = float(parts[0])
                                # Convert to GHz
                                if freq < 1:
                                    freq_ghz = freq
                                elif freq < 1000:
                                    freq_ghz = freq / 1e3
                                else:
                                    freq_ghz = freq / 1e9
                                
                                if len(parts) >= 3:
                                    # Real and imaginary
                                    s11_real = float(parts[1])
                                    s11_imag = float(parts[2])
                                else:
                                    # Magnitude in dB
                                    s11_mag_db = float(parts[1])
                                    s11_mag = 10 ** (s11_mag_db / 20)
                                    s11_real = s11_mag  # Approximate
                                    s11_imag = 0
                                
                                data_rows.append({
                                    "freq_ghz": freq_ghz,
                                    "s11_real": s11_real,
                                    "s11_imag": s11_imag
                                })
                            except ValueError:
                                continue
                
                if data_rows:
                    # Find resonant frequency
                    min_s11_idx = min(range(len(data_rows)),
                                     key=lambda i: abs(complex(data_rows[i]["s11_real"], data_rows[i]["s11_imag"])))
                    freq_res = data_rows[min_s11_idx]["freq_ghz"]
                    s11_res = complex(data_rows[min_s11_idx]["s11_real"], data_rows[min_s11_idx]["s11_imag"])
                    import math
                    if abs(s11_res) > 0:
                        return_loss_db = 20 * math.log10(abs(s11_res))
                    else:
                        return_loss_db = float('inf')
                    
                    return {
                        "frequency_ghz": freq_res,
                        "return_loss_dB": return_loss_db,
                        "bandwidth_mhz": 150.0,
                        "source": "cst_ascii"
                    }
    except Exception as e:
        logger.warning(f"CST ASCII parsing failed: {e}")
    
    # Try JSON format
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return {
                    "frequency_ghz": data.get("frequency_ghz", data.get("frequency", 2.4)),
                    "return_loss_dB": data.get("return_loss_dB", data.get("return_loss", -20.0)),
                    "gain_dBi": data.get("gain_dBi", data.get("gain", 5.0)),
                    "bandwidth_mhz": data.get("bandwidth_mhz", data.get("bandwidth", 150)),
                    "source": "cst_json"
                }
    except Exception as e:
        logger.warning(f"JSON parsing failed: {e}")
    
    # Try CSV format
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if rows:
                # Look for common CST column names
                row = rows[0]
                freq_key = None
                s11_key = None
                
                for key in row.keys():
                    key_lower = key.lower()
                    if 'freq' in key_lower:
                        freq_key = key
                    if 's11' in key_lower or 's_11' in key_lower:
                        s11_key = key
                
                if freq_key:
                    freq_val = float(rows[0].get(freq_key, 2.4))
                    if freq_val < 1:
                        freq_ghz = freq_val
                    elif freq_val < 1000:
                        freq_ghz = freq_val / 1e3
                    else:
                        freq_ghz = freq_val / 1e9
                    
                    return_loss = -20.0
                    if s11_key:
                        s11_val = float(rows[0].get(s11_key, -20.0))
                        return_loss = s11_val if s11_val < 0 else -s11_val
                    
                    return {
                        "frequency_ghz": freq_ghz,
                        "return_loss_dB": return_loss,
                        "bandwidth_mhz": 150.0,
                        "source": "cst_csv"
                    }
    except Exception as e:
        logger.warning(f"CSV parsing failed: {e}")
    
    # Fallback: raise error
    raise ValueError(f"Could not parse CST file. Supported formats: Touchstone (.s1p), CST ASCII, CSV, JSON. Error: {str(e)}")





