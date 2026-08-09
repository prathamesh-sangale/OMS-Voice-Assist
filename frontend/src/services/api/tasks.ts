import { fetchClient } from './client';
import type { OrderTask, PaginatedResponse } from './types';

export interface TaskFilters {
  search?: string;
  status?: string;
  department?: string;
  stage?: string;
  order_id?: string;
}

export const tasksApi = {
  async getTasks(filters: TaskFilters = {}, page: number = 1, pageSize: number = 20): Promise<PaginatedResponse<OrderTask>> {
    const params = new URLSearchParams();
    
    params.append('page', page.toString());
    params.append('page_size', pageSize.toString());
    
    if (filters.search) params.append('search', filters.search);
    if (filters.status) params.append('status', filters.status);
    if (filters.department) params.append('department', filters.department);
    if (filters.stage) params.append('stage', filters.stage);
    if (filters.order_id) params.append('order_id', filters.order_id);
    
    return fetchClient<PaginatedResponse<OrderTask>>(`/api/tasks?${params.toString()}`);
  }
};
