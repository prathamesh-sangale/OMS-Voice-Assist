import { useState, useEffect } from 'react';
import { Card } from '../../../components/ui/Card';
import { analyticsApi } from '../../../services/api/analytics';
import type { AnalyticsData, AnalyticsDistribution } from '../../../services/api/types';

const AnalyticsPage = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        const res = await analyticsApi.getOrderAnalytics();
        setData(res);
      } catch (err: any) {
        setError(err.message || 'Failed to load analytics data.');
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  const renderDistributionBars = (title: string, dist: AnalyticsDistribution[], maxColors: string[] = ['bg-primary', 'bg-accent', 'bg-border', 'bg-success', 'bg-warning']) => {
    const total = dist.reduce((acc, curr) => acc + curr.value, 0);
    return (
      <Card className="p-6 min-h-[250px]">
        <h2 className="text-lg font-medium text-text mb-4 border-b border-border pb-2">{title}</h2>
        {dist.length === 0 ? (
          <div className="flex items-center justify-center h-20 text-muted-text italic">No data</div>
        ) : (
          <div className="space-y-4 text-sm mt-4">
            {dist.map((item, idx) => {
              const percent = total > 0 ? Math.round((item.value / total) * 100) : 0;
              const colorClass = maxColors[idx % maxColors.length];
              return (
                <div key={item.label}>
                  <div className="flex justify-between mb-1">
                    <span className="truncate pr-2">{item.label}</span>
                    <span className="font-medium">{item.value} ({percent}%)</span>
                  </div>
                  <div className="w-full bg-surface rounded-full h-2">
                    <div className={`${colorClass} h-2 rounded-full`} style={{ width: `${percent}%` }}></div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-text">Executive Analytics</h1>
          <p className="text-sm text-muted-text">High-level distribution and business model insights.</p>
        </div>
      </div>

      {error ? (
        <div className="p-4 bg-surface rounded-md border border-red-500 text-red-500">
          {error}
        </div>
      ) : loading ? (
        <div className="p-12 text-center text-muted-text">Loading analytics...</div>
      ) : data ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {renderDistributionBars('Order Status', data.order_status, ['bg-success', 'bg-warning', 'bg-primary', 'bg-border'])}
          {renderDistributionBars('Business Model', data.business_model, ['bg-primary', 'bg-accent', 'bg-border'])}
          {renderDistributionBars('Product Types', data.product)}
          {renderDistributionBars('Customer Types', data.customer_type, ['bg-accent', 'bg-primary'])}
          {renderDistributionBars('Sales Executives', data.sales_executive)}
        </div>
      ) : null}
    </div>
  );
};

export default AnalyticsPage;
