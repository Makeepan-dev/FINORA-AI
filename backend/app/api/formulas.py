from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, List, Optional
from ..formulas.models import FormulaDomain, FormulaStatus, FormulaEntry, CalculationResult
from ..formulas.registry import global_formula_registry

router = APIRouter(prefix="/formulas", tags=["Financial Formula Registry & Engine"])

@router.get("", response_model=List[FormulaEntry])
def list_formulas(
    domain: Optional[FormulaDomain] = None,
    status: Optional[FormulaStatus] = None,
    search: Optional[str] = Query(None, description="Search keyword in formula name or description")
) -> List[FormulaEntry]:
    """Lists all registered financial formulas, algorithms and models with filtering."""
    return global_formula_registry.list_all(domain=domain, status=status, search=search)

@router.get("/catalog/summary")
def get_catalog_summary() -> Dict[str, Any]:
    """Returns registry summary statistics, domain breakdown, and execution readiness."""
    return global_formula_registry.get_summary()

@router.get("/{formula_id}", response_model=FormulaEntry)
def get_formula(formula_id: str) -> FormulaEntry:
    """Returns full metadata, requirements, assumptions, and validation rules for a formula."""
    entry = global_formula_registry.get(formula_id)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Formula '{formula_id}' not found.")
    return entry

@router.post("/{formula_id}/calculate", response_model=CalculationResult)
def execute_formula(
    formula_id: str,
    inputs: Dict[str, Any] = Body(..., description="Key-value mapping of required and optional inputs")
) -> CalculationResult:
    """
    Executes a registered formula using authoritative Decimal arithmetic.
    Returns structured result, explanation, assumptions, and precision metadata.
    """
    try:
        return global_formula_registry.execute(formula_id, inputs)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except NotImplementedError as nie:
        raise HTTPException(status_code=501, detail=str(nie))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")
