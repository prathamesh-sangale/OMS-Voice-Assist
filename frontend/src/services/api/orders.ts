import { fetchClient } from './client';
import type { Order, OrderTask, PaginatedResponse } from './types';

export interface OrderFilters {
  search?: string;
  status?: string;
  business_model?: string;
  product?: string;
  sales_exec?: string;
}

export const ordersApi = {
  /**
   * Fetch a paginated list of orders, optionally applying filters.
   */
  async getOrders(filters: OrderFilters = {}, page: number = 1, pageSize: number = 20): Promise<PaginatedResponse<Order>> {
    const params = new URLSearchParams();
    
    params.append('page', page.toString());
    params.append('page_size', pageSize.toString());
    
    if (filters.search) params.append('search', filters.search);
    if (filters.status) params.append('status', filters.status);
    if (filters.business_model) params.append('business_model', filters.business_model);
    if (filters.product) params.append('product', filters.product);
    if (filters.sales_exec) params.append('sales_exec', filters.sales_exec);
    
    return fetchClient<PaginatedResponse<Order>>(`/api/orders?${params.toString()}`);
  },

  /**
   * Fetch a single order by its ID.
   */
  async getOrderById(orderId: string): Promise<Order> {
    return fetchClient<Order>(`/api/orders/${orderId}`);
  },

  /**
   * Fetch the workflow tasks associated with a specific order.
   */
  async getOrderTasks(orderId: string): Promise<OrderTask[]> {
    return fetchClient<OrderTask[]>(`/api/orders/${orderId}/tasks`);
  }
};
