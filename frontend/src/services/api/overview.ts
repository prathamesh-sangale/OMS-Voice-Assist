import { fetchClient } from './client';
import type { OverviewResponse } from './types';

export const overviewApi = {
  async getOverview(): Promise<OverviewResponse> {
    return fetchClient<OverviewResponse>('/api/overview');
  }
};
