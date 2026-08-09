import { fetchClient } from './client';
import type { CustomerView, PaginatedResponse } from './types';

export interface CustomerFilters {
  search?: string;
  customer_type?: string;
  sales_exec?: string;
}

export const customersApi = {
  async getCustomers(filters: CustomerFilters = {}, page: number = 1, pageSize: number = 20): Promise<PaginatedResponse<CustomerView>> {
    const params = new URLSearchParams();
    
    params.append('page', page.toString());
    params.append('page_size', pageSize.toString());
    
    if (filters.search) params.append('search', filters.search);
    if (filters.customer_type) params.append('customer_type', filters.customer_type);
    if (filters.sales_exec) params.append('sales_exec', filters.sales_exec);
    
    return fetchClient<PaginatedResponse<CustomerView>>(`/api/customers?${params.toString()}`);
  }
};
