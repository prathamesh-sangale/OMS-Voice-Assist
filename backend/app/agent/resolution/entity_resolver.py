from typing import Optional, List, Dict, Set
from pydantic import BaseModel
from ...oms.services.oms_service import OMSService
from ...oms.contracts.queries import OrderQuery

class ResolutionResult(BaseModel):
    is_ambiguous: bool = False
    resolved_value: Optional[str] = None
    candidates: List[str] = []

class EntityResolver:
    """
    Resolves extracted candidate entities against a cached index of OMS data.
    Implements Exact Match -> Case-Insensitive Exact -> Fuzzy -> Ambiguous.
    """
    
    def __init__(self, oms_service: OMSService):
        self._oms_service = oms_service
        # Cached indexes
        self._sales_execs: Set[str] = set()
        self._customers: Set[str] = set()
        self._products: Set[str] = set()
        self._is_initialized = False
        
    def _refresh_cache(self):
        """Loads valid entities into cache by reading from OMSService."""
        if self._is_initialized:
            return
        # Use max allowed page size. For production, paginate to fetch all.
        all_orders_response = self._oms_service.list_orders(OrderQuery(page_size=100))
        
        for o in all_orders_response.items:
            if o.sales_exec:
                self._sales_execs.add(o.sales_exec)
            if o.client_name:
                self._customers.add(o.client_name)
            if o.product_types:
                for pt in o.product_types:
                    self._products.add(pt)
            if o.product_configs:
                for pc in o.product_configs:
                    if pc.product:
                        self._products.add(pc.product)
                        
        self._is_initialized = True

    def resolve_sales_exec(self, candidate: str) -> ResolutionResult:
        return self._resolve_entity(candidate, self._sales_execs)

    def resolve_customer(self, candidate: str) -> ResolutionResult:
        return self._resolve_entity(candidate, self._customers)
        
    def _resolve_entity(self, candidate: str, domain_set: Set[str]) -> ResolutionResult:
        self._refresh_cache()
        
        # 1. Exact Match
        if candidate in domain_set:
            return ResolutionResult(resolved_value=candidate)
            
        # 2. Case-Insensitive Exact Match
        candidate_lower = candidate.lower()
        exact_insens = [e for e in domain_set if e.lower() == candidate_lower]
        if len(exact_insens) == 1:
            return ResolutionResult(resolved_value=exact_insens[0])
            
        # 3. Fuzzy Candidate Detection (Substring matching)
        candidates = [e for e in domain_set if candidate_lower in e.lower()]
        
        if len(candidates) == 1:
            # We don't automatically execute a fuzzy match. 
            # In Phase 3.2, we return the candidate so rules can decide, but it is unambiguous.
            return ResolutionResult(resolved_value=candidates[0])
        elif len(candidates) > 1:
            # Ambiguous
            return ResolutionResult(is_ambiguous=True, candidates=candidates)
            
        # No match
        return ResolutionResult(resolved_value=None)
