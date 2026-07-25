"""
src/data.py
-----------
Data definitions, parameters, and ingestion pipeline for Problem 1 (Drawdown)
and Problem 2 (Buildup) well test analysis.
"""

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class DrawdownParameters:
    """
    Parameters for Problem 1: Constant-rate Drawdown Test.
    
    Units:
        q   : Oil flow rate (STB/day)
        p_i : Initial reservoir pressure (psia)
        h   : Formation thickness (ft)
        phi : Porosity (fraction)
        r_w : Wellbore radius (ft)
        B   : Oil formation volume factor (RB/STB)
        c_t : Total compressibility (psi^-1)
        mu  : Viscosity (cP)
    """
    q: float = 50.0
    p_i: float = 1326.6
    h: float = 25.0
    phi: float = 0.276
    r_w: float = 0.36
    B: float = 1.099
    c_t: float = 9.4e-6
    mu: float = 5.28


@dataclass(frozen=True)
class BuildupParameters:
    """
    Parameters for Problem 2: Shut-in Pressure Buildup Test.
    
    Units:
        q   : Oil flow rate prior to shut-in (STB/day)
        p_i : Initial flowing bottomhole pressure / initial pressure reference (psia)
        h   : Formation thickness (ft)
        phi : Porosity (fraction)
        r_w : Wellbore radius (ft)
        B   : Oil formation volume factor (RB/STB)
        c_t : Total compressibility (psi^-1)
        mu  : Viscosity (cP)
        t_p : Effective production time prior to shut-in (hrs)
        A   : Reservoir drainage area (acres)
    """
    q: float = 10.0
    p_i: float = 1192.45
    h: float = 10.0
    phi: float = 0.319
    r_w: float = 0.34
    B: float = 1.098
    c_t: float = 10.9e-6
    mu: float = 5.11
    t_p: float = 960.0
    A: float = 80.0


# Raw observation data for Problem 1 (time_hr, p_wf_psi)
P1_RAW_DATA = [
    (0.100, 1109.0), (0.220, 937.0), (0.364, 805.1), (0.537, 707.8), (0.744, 638.4),
    (0.993, 589.9), (1.290, 555.5), (1.650, 530.2), (2.080, 510.3), (2.600, 493.7),
    (3.220, 478.9), (3.960, 465.4), (4.850, 452.8), (5.920, 440.8), (7.200, 429.3),
    (8.740, 418.1), (10.590, 407.2), (12.810, 396.6), (15.470, 386.1), (18.670, 375.8),
    (22.500, 365.6), (27.100, 355.5), (32.620, 345.5), (39.250, 335.5), (47.200, 325.6),
    (48.000, 324.7)
]

# Raw observation data for Problem 2 (delta_t_hr, p_ws_psi)
P2_RAW_DATA = [
    (0.000, 1192.45), (0.050, 1206.92), (0.110, 1217.90), (0.182, 1226.92), (0.268, 1234.52),
    (0.372, 1241.02), (0.496, 1246.66), (0.646, 1251.62), (0.825, 1256.04), (1.040, 1260.05),
    (1.298, 1263.73), (1.608, 1267.15), (1.979, 1270.37), (2.420, 1273.43), (2.960, 1276.36),
    (3.600, 1279.19), (4.370, 1281.93), (5.300, 1284.61), (6.410, 1287.22), (7.740, 1289.79),
    (9.330, 1292.31), (11.250, 1294.80), (13.550, 1297.24), (16.310, 1299.66), (19.620, 1302.04),
    (23.600, 1304.39), (28.400, 1306.71), (34.100, 1308.99), (41.000, 1311.23), (49.200, 1313.42),
    (59.100, 1315.56), (71.000, 1317.65), (72.000, 1317.81)
]


def get_drawdown_params() -> DrawdownParameters:
    """Return default DrawdownParameters instance with exact course units and values."""
    return DrawdownParameters()


def get_buildup_params() -> BuildupParameters:
    """Return default BuildupParameters instance with exact course units and values."""
    return BuildupParameters()


def get_drawdown_dataframe(params: DrawdownParameters = None) -> pd.DataFrame:
    """
    Constructs and returns the DataFrame for Problem 1 (Drawdown Test).

    Columns:
        - 'time_hr'    : Elapsed test time (hours)
        - 'p_wf_psi'   : Wellbore flowing pressure (psi)
        - 'delta_p_psi': Pressure drawdown drop p_i - p_wf (psi)
    """
    if params is None:
        params = get_drawdown_params()

    df = pd.DataFrame(P1_RAW_DATA, columns=['time_hr', 'p_wf_psi'])
    df['delta_p_psi'] = params.p_i - df['p_wf_psi']
    return df[['time_hr', 'p_wf_psi', 'delta_p_psi']]


def get_buildup_dataframe(params: BuildupParameters = None) -> pd.DataFrame:
    """
    Constructs and returns the DataFrame for Problem 2 (Buildup Test).

    Columns:
        - 'delta_t_hr'  : Shut-in time delta t (hours)
        - 'p_ws_psi'    : Wellbore shut-in pressure (psi)
        - 't_e_hr'      : Agarwal equivalent time t_e = (t_p * delta_t) / (t_p + delta_t) (hours)
        - 'horner_ratio': Horner ratio (t_p + delta_t) / delta_t
        - 'delta_p_psi' : Pressure buildup change p_ws(delta_t) - p_wf(delta_t=0) (psi)
    """
    if params is None:
        params = get_buildup_params()

    df = pd.DataFrame(P2_RAW_DATA, columns=['delta_t_hr', 'p_ws_psi'])
    p_wf_0 = df['p_ws_psi'].iloc[0]  # pressure at delta_t = 0 (1192.45 psia)
    
    # Calculate Agarwal equivalent time t_e (hours)
    df['t_e_hr'] = np.where(
        df['delta_t_hr'] == 0,
        0.0,
        (params.t_p * df['delta_t_hr']) / (params.t_p + df['delta_t_hr'])
    )

    # Calculate Horner ratio (t_p + delta_t) / delta_t
    df['horner_ratio'] = np.where(
        df['delta_t_hr'] == 0,
        np.inf,
        (params.t_p + df['delta_t_hr']) / df['delta_t_hr']
    )

    # Calculate buildup pressure change delta_p = p_ws(dt) - p_wf(dt=0)
    df['delta_p_psi'] = df['p_ws_psi'] - p_wf_0

    return df[['delta_t_hr', 'p_ws_psi', 't_e_hr', 'horner_ratio', 'delta_p_psi']]


def validate_drawdown_data(df: pd.DataFrame, params: DrawdownParameters = None) -> bool:
    """
    Validates structural and physical integrity of drawdown dataset (Problem 1).

    Ensures:
        - Is a pandas DataFrame
        - Columns: ['time_hr', 'p_wf_psi', 'delta_p_psi']
        - Exactly 26 rows
        - No NaN values
        - Strictly positive time values
        - Strictly increasing time values
        - Strictly decreasing flowing pressure
        - Strictly positive pressure drop delta_p_psi
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input data must be a pandas DataFrame")

    required_cols = {'time_hr', 'p_wf_psi', 'delta_p_psi'}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(f"Missing required drawdown columns: {missing}")

    if len(df) != 26:
        raise ValueError(f"Expected exactly 26 rows for Drawdown data, got {len(df)}")

    if df.isnull().values.any():
        raise ValueError("Drawdown DataFrame contains NaN or null values")

    if not (df['time_hr'] > 0).all():
        raise ValueError("Drawdown time_hr must be strictly positive")

    if not (df['time_hr'].diff().iloc[1:] > 0).all():
        raise ValueError("Drawdown time_hr must be strictly monotonic increasing")

    if not (df['p_wf_psi'].diff().iloc[1:] < 0).all():
        raise ValueError("Drawdown p_wf_psi must be strictly monotonic decreasing")

    if not (df['delta_p_psi'] > 0).all():
        raise ValueError("Drawdown delta_p_psi must be strictly positive")

    return True


def validate_buildup_data(df: pd.DataFrame, params: BuildupParameters = None) -> bool:
    """
    Validates structural and physical integrity of buildup dataset (Problem 2).

    Ensures:
        - Is a pandas DataFrame
        - Columns: ['delta_t_hr', 'p_ws_psi', 't_e_hr', 'horner_ratio', 'delta_p_psi']
        - Exactly 33 rows
        - No NaN values
        - Non-negative shut-in time values (delta_t_hr >= 0)
        - Strictly increasing shut-in time values for delta_t > 0
        - Strictly increasing shut-in pressure p_ws_psi
        - Valid Agarwal equivalent time t_e_hr >= 0
        - Delta P == 0 at delta_t = 0, and delta_p_psi > 0 for delta_t > 0
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input data must be a pandas DataFrame")

    required_cols = {'delta_t_hr', 'p_ws_psi', 't_e_hr', 'horner_ratio', 'delta_p_psi'}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(f"Missing required buildup columns: {missing}")

    if len(df) != 33:
        raise ValueError(f"Expected exactly 33 rows for Buildup data, got {len(df)}")

    if df.isnull().values.any():
        raise ValueError("Buildup DataFrame contains NaN or null values")

    if not (df['delta_t_hr'] >= 0).all():
        raise ValueError("Buildup delta_t_hr must be non-negative")

    if not (df['delta_t_hr'].diff().iloc[1:] > 0).all():
        raise ValueError("Buildup delta_t_hr must be strictly monotonic increasing")

    if not (df['p_ws_psi'].diff().iloc[1:] > 0).all():
        raise ValueError("Buildup p_ws_psi must be strictly monotonic increasing")

    if not (df['t_e_hr'] >= 0).all():
        raise ValueError("Buildup t_e_hr must be non-negative")

    if abs(df['delta_p_psi'].iloc[0]) > 1e-6:
        raise ValueError("Buildup delta_p_psi must start at 0.0 at delta_t = 0")

    if not (df['delta_p_psi'].iloc[1:] > 0).all():
        raise ValueError("Buildup delta_p_psi must be strictly positive for delta_t > 0")

    return True
