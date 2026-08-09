import { fetchClient } from './client';
import type { AnalyticsData } from './types';

export const analyticsApi = {
  async getOrderAnalytics(): Promise<AnalyticsData> {
    return fetchClient<AnalyticsData>('/api/analytics/orders');
  }
};
