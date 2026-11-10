from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from .decimal_math import to_decimal, round_currency, safe_divide

def detect_duplicate_transactions(
    transactions: List[Dict[str, Any]],
    time_window_hours: int = 48
) -> List[Dict[str, Any]]:
    """
    Identifies potential duplicate debits based on matching merchant, amount,
    and proximity in timestamp. Distinguishes verified legitimate multiple purchases
    (such as separate developer seat licenses) using invoice or seat metadata.
    """
    duplicates = []
    # Sort transactions by timestamp
    sorted_txs = sorted(
        [t for t in transactions if t.get("type", "").lower() in ["expense", "debit"]],
        key=lambda x: x.get("timestamp", "")
    )

    checked_pairs = set()

    for i in range(len(sorted_txs)):
        t1 = sorted_txs[i]
        t1_id = t1.get("transaction_id", "")
        t1_amt = to_decimal(t1.get("amount", 0))
        t1_merchant = t1.get("merchant_id", "")
        t1_time_str = t1.get("timestamp", "")

        try:
            t1_dt = datetime.fromisoformat(t1_time_str.replace("Z", "+00:00"))
        except Exception:
            continue

        for j in range(i + 1, len(sorted_txs)):
            t2 = sorted_txs[j]
            t2_id = t2.get("transaction_id", "")
            if (t1_id, t2_id) in checked_pairs or (t2_id, t1_id) in checked_pairs:
                continue

            t2_amt = to_decimal(t2.get("amount", 0))
            t2_merchant = t2.get("merchant_id", "")
            t2_time_str = t2.get("timestamp", "")

            try:
                t2_dt = datetime.fromisoformat(t2_time_str.replace("Z", "+00:00"))
            except Exception:
                continue

            delta_hours = abs((t2_dt - t1_dt).total_seconds()) / 3600.0
            if delta_hours > time_window_hours:
                break  # Sorted list, no further match in window

            if t1_merchant == t2_merchant and t1_amt == t2_amt:
                checked_pairs.add((t1_id, t2_id))

                # Check if legitimately distinct purchases (e.g. GitForge seats)
                desc1 = t1.get("description", "").lower()
                desc2 = t2.get("description", "").lower()
                is_legitimate_distinct = False

                if "seat" in desc1 and "seat" in desc2 and desc1 != desc2:
                    is_legitimate_distinct = True
                elif t1.get("anomaly_flag") == "verified_legitimate_repeated":
                    is_legitimate_distinct = True

                duplicates.append({
                    "primary_transaction_id": t1_id,
                    "duplicate_transaction_id": t2_id,
                    "merchant_id": t1_merchant,
                    "amount": float(t1_amt),
                    "hours_apart": round(delta_hours, 2),
                    "is_legitimate_distinct": is_legitimate_distinct,
                    "investigation_verdict": "LEGITIMATE_MULTIPLE_PURCHASE" if is_legitimate_distinct else "POTENTIAL_DUPLICATE_ERROR",
                    "requires_dispute": not is_legitimate_distinct
                })

    return duplicates

def detect_recurring_commitments(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Identifies recurring subscriptions by evaluating interval regularity (28-31 days).
    """
    merchant_txs: Dict[str, List[Dict[str, Any]]] = {}
    for t in transactions:
        m = t.get("merchant_id", "unknown")
        if t.get("type", "").lower() in ["expense", "debit"]:
            merchant_txs.setdefault(m, []).append(t)

    recurring = []
    for m, tx_list in merchant_txs.items():
        if len(tx_list) < 2:
            continue
        sorted_m_txs = sorted(tx_list, key=lambda x: x.get("timestamp", ""))
        intervals = []
        for k in range(len(sorted_m_txs) - 1):
            try:
                d1 = datetime.fromisoformat(sorted_m_txs[k]["timestamp"].replace("Z", "+00:00"))
                d2 = datetime.fromisoformat(sorted_m_txs[k+1]["timestamp"].replace("Z", "+00:00"))
                intervals.append((d2 - d1).days)
            except Exception:
                pass

        if intervals:
            avg_interval = sum(intervals) / len(intervals)
            # Monthly recurring interval between 27 and 33 days
            if 27 <= avg_interval <= 33:
                last_tx = sorted_m_txs[-1]
                amt = to_decimal(last_tx.get("amount", 0))
                recurring.append({
                    "merchant_id": m,
                    "cadence": "monthly",
                    "average_amount": float(amt),
                    "annual_run_rate": float(amt * Decimal("12")),
                    "last_billed_date": last_tx.get("timestamp", "")[:10],
                    "transaction_count": len(sorted_m_txs)
                })

    return recurring

def detect_spending_anomalies(
    transactions: List[Dict[str, Any]],
    baseline_threshold: Decimal = Decimal("300.00")
) -> List[Dict[str, Any]]:
    """
    Detects unusual transaction spikes and anomalies exceeding spending thresholds.
    """
    anomalies = []
    for t in transactions:
        amt = to_decimal(t.get("amount", 0))
        flag = t.get("anomaly_flag")
        if amt >= baseline_threshold or flag is not None:
            anomalies.append({
                "transaction_id": t.get("transaction_id"),
                "merchant_id": t.get("merchant_id"),
                "category": t.get("category"),
                "amount": float(amt),
                "timestamp": t.get("timestamp"),
                "anomaly_flag": flag or "high_single_ticket_expense",
                "severity": "HIGH" if amt >= Decimal("500.00") else "MEDIUM"
            })
    return anomalies

def calculate_cash_flow_runway(
    current_liquid_balance: Decimal,
    monthly_income: Decimal,
    monthly_expenses: Decimal
) -> Dict[str, Any]:
    """
    Computes net burn rate and liquid cash runway in months.
    """
    bal = to_decimal(current_liquid_balance)
    inc = to_decimal(monthly_income)
    exp = to_decimal(monthly_expenses)

    net_cash_flow = inc - exp

    if net_cash_flow >= Decimal("0.00"):
        runway_months = "INFINITE (Positive Cash Flow)"
        monthly_burn = Decimal("0.00")
        is_sustainable = True
    else:
        monthly_burn = abs(net_cash_flow)
        runway = safe_divide(bal, monthly_burn)
        runway_months = f"{float(runway):.1f} months"
        is_sustainable = False

    return {
        "current_liquid_balance": float(bal),
        "monthly_income": float(inc),
        "monthly_expenses": float(exp),
        "net_cash_flow": float(net_cash_flow),
        "monthly_burn_rate": float(monthly_burn),
        "runway": runway_months,
        "is_cash_flow_positive": is_sustainable
    }
