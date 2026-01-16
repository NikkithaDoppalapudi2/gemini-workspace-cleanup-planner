"""
Risk Score Calculator Module
Calculates risk scores based on LastLoginDays, AccessLevel, and Role
"""

import pandas as pd


def get_login_score(days: int) -> int:
    """Calculate risk score based on last login days."""
    if days <= 30:
        return 0
    elif days <= 90:
        return 25
    elif days <= 180:
        return 50
    elif days <= 365:
        return 75
    else:
        return 100


def get_access_score(access_level: str) -> int:
    """Calculate risk score based on access level."""
    access_scores = {
        "Viewer": 10,
        "Commenter": 20,
        "Editor": 40,
        "Owner": 60
    }
    return access_scores.get(access_level, 20)  # Default to 20 if unknown


def get_role_bonus(role: str) -> int:
    """Add bonus points for high-risk roles."""
    high_risk_roles = ["Former Employee", "Contractor", "Intern", "Temporary"]
    for hr_role in high_risk_roles:
        if hr_role.lower() in role.lower():
            return 20
    return 0


def get_risk_category(score: int) -> str:
    """Categorize risk score into levels."""
    if score <= 30:
        return "🟢 Low"
    elif score <= 60:
        return "🟡 Medium"
    elif score <= 80:
        return "🟠 High"
    else:
        return "🔴 Critical"


def calculate_risk_score(row: pd.Series) -> int:
    """Calculate total risk score for a user row."""
    login_days = row.get('LastLoginDays', 0)
    access_level = row.get('AccessLevel', 'Viewer')
    role = row.get('Role', '')
    
    # Handle potential non-numeric values
    try:
        login_days = int(login_days)
    except (ValueError, TypeError):
        login_days = 0
    
    login_score = get_login_score(login_days)
    access_score = get_access_score(access_level)
    role_bonus = get_role_bonus(role)
    
    return login_score + access_score + role_bonus


def add_risk_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Add risk score and category columns to dataframe."""
    df = df.copy()
    df['RiskScore'] = df.apply(calculate_risk_score, axis=1)
    df['RiskCategory'] = df['RiskScore'].apply(get_risk_category)
    return df


def get_risk_summary(df: pd.DataFrame) -> dict:
    """Get summary statistics for risk scores."""
    if 'RiskScore' not in df.columns:
        df = add_risk_scores(df)
    
    total_users = len(df)
    avg_score = df['RiskScore'].mean()
    
    # Count by category
    low_count = len(df[df['RiskScore'] <= 30])
    medium_count = len(df[(df['RiskScore'] > 30) & (df['RiskScore'] <= 60)])
    high_count = len(df[(df['RiskScore'] > 60) & (df['RiskScore'] <= 80)])
    critical_count = len(df[df['RiskScore'] > 80])
    
    return {
        'total_users': total_users,
        'avg_score': round(avg_score, 1),
        'low_count': low_count,
        'medium_count': medium_count,
        'high_count': high_count,
        'critical_count': critical_count,
        'high_risk_total': high_count + critical_count
    }
