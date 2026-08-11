from typing import List, Dict, Any, Optional
from collections import defaultdict

from ..repositories.base import BaseOMSRepository
from ..schemas.oms import OrderSchema, OrderTaskSchema
from ..schemas.api import PaginatedResponse, CustomerView, OverviewMetrics, OverviewResponse, AnalyticsData, AnalyticsDistribution
from ..contracts.queries import OrderQuery, TaskQuery, CustomerQuery

class OMSService:
    """
    Service layer providing a domain-centric interface to the OMS data.
    Decoupled from the specific storage mechanism through BaseOMSRepository.
    """
    
    def __init__(self, repository: BaseOMSRepository):
        self._repository = repository
        
    def list_orders(self, query: OrderQuery) -> PaginatedResponse[OrderSchema]:
        """Fetch all available orders matching the structured OrderQuery."""
        all_orders = self._repository.list_orders(
            search=query.search,
            status=query.status,
            business_model=query.business_model,
            product=query.product,
            sales_exec=query.sales_exec,
            quantity=query.quantity,
            sort_by=query.sort_by,
            sort_order=query.sort_order
        )
        return self._paginate(all_orders, query.page, query.page_size)
        
    def retrieve_order_details(self, order_id: str) -> OrderSchema:
        """Fetch a specific order by ID."""
        return self._repository.get_order(order_id)
        
    def get_order_tasks(self, order_id: str) -> List[OrderTaskSchema]:
        """Fetch workflow tasks for a specific order."""
        order = self._repository.get_order(order_id)
        return self._repository.get_tasks_for_order(order.id)

    def list_tasks(self, query: TaskQuery) -> PaginatedResponse[OrderTaskSchema]:
        """Fetch all tasks matching the structured TaskQuery."""
        all_tasks = self._repository.list_tasks(
            search=query.search,
            status=query.status,
            department=query.department,
            stage=query.stage,
            order_id=query.order_id
        )
        return self._paginate(all_tasks, query.page, query.page_size)

    def get_customer_summary(self, query: CustomerQuery) -> PaginatedResponse[CustomerView]:
        """Aggregate customer data from raw orders based on the CustomerQuery."""
        all_orders = self._repository.list_orders()
        
        customers_map: Dict[str, CustomerView] = {}
        
        for o in all_orders:
            cname = o.client_name
            if not cname:
                continue
                
            if cname not in customers_map:
                customers_map[cname] = CustomerView(
                    client_name=cname,
                    customer_type=o.customer_type,
                    sales_execs=[],
                    loading_cities=[],
                    delivery_cities=[],
                    active_orders=0,
                    total_orders=0
                )
                
            c = customers_map[cname]
            c.total_orders += 1
            
            # Active definition: not completed and not cancelled
            status = (o.status or "").lower()
            if status and status not in ["completed", "done", "cancelled", "closed"]:
                c.active_orders += 1
                
            if o.sales_exec and o.sales_exec not in c.sales_execs:
                c.sales_execs.append(o.sales_exec)
                
            if o.loading_city and o.loading_city not in c.loading_cities:
                c.loading_cities.append(o.loading_city)
                
            if o.delivery_city and o.delivery_city not in c.delivery_cities:
                c.delivery_cities.append(o.delivery_city)
                
        customer_list = list(customers_map.values())
        
        if query.search:
            s = query.search.lower()
            customer_list = [c for c in customer_list if s in c.client_name.lower()]
        if query.customer_type:
            customer_list = [c for c in customer_list if (c.customer_type or "").lower() == query.customer_type.lower()]
        if query.sales_exec:
            se = query.sales_exec.lower()
            customer_list = [c for c in customer_list if any(se == x.lower() for x in c.sales_execs)]
            
        customer_list.sort(key=lambda x: x.total_orders, reverse=True)
        
        return self._paginate(customer_list, query.page, query.page_size)

    def get_overview_metrics(self) -> OverviewResponse:
        """Calculate executive metrics and return recent activity."""
        all_orders = self._repository.list_orders()
        all_tasks = self._repository.list_tasks()
        
        metrics = OverviewMetrics(
            active_orders=0,
            pending_orders=0,
            completed_orders=0,
            needs_revision=0,
            total_order_value=None
        )
        
        for o in all_orders:
            st = (o.status or "").lower()
            if st in ["completed", "done"]:
                metrics.completed_orders += 1
            elif "pending" in st:
                metrics.pending_orders += 1
            elif "revision" in st or "error" in st:
                metrics.needs_revision += 1
            else:
                metrics.active_orders += 1
                
        recent_orders = list(reversed(all_orders))[:5]
        recent_tasks = list(reversed(all_tasks))[:5]
        
        return OverviewResponse(
            metrics=metrics,
            recent_orders=recent_orders,
            recent_tasks=recent_tasks
        )

    def get_order_analytics(self) -> AnalyticsData:
        """Calculate distribution metrics across various order dimensions."""
        all_orders = self._repository.list_orders()
        
        bm_counts = defaultdict(int)
        prod_counts = defaultdict(int)
        status_counts = defaultdict(int)
        sales_counts = defaultdict(int)
        ctype_counts = defaultdict(int)
        
        for o in all_orders:
            if o.business_model:
                bm_counts[o.business_model] += 1
            if o.status:
                status_counts[o.status] += 1
            if o.sales_exec:
                sales_counts[o.sales_exec] += 1
            if o.customer_type:
                ctype_counts[o.customer_type] += 1
                
            prod_handled = False
            if o.product_types:
                for pt in o.product_types:
                    prod_counts[pt] += 1
                    prod_handled = True
            if not prod_handled and o.product_configs:
                for pc in o.product_configs:
                    if pc.product:
                        prod_counts[pc.product] += 1
                        
        def _to_dist(d: dict) -> List[AnalyticsDistribution]:
            return [AnalyticsDistribution(label=k, value=v) for k, v in sorted(d.items(), key=lambda x: x[1], reverse=True)]
            
        return AnalyticsData(
            business_model=_to_dist(bm_counts),
            product=_to_dist(prod_counts),
            order_status=_to_dist(status_counts),
            sales_executive=_to_dist(sales_counts),
            customer_type=_to_dist(ctype_counts)
        )

    def _paginate(self, items: List[Any], page: int, page_size: int) -> PaginatedResponse:
        total = len(items)
        start_idx = (page - 1) * page_size
        paginated_items = items[start_idx:start_idx + page_size]
        pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        
        return PaginatedResponse(
            items=paginated_items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages
        )
