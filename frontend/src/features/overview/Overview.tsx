import { useState, useEffect } from 'react';
import { MetricCard, Card } from '../../components/ui/Card';
import { Table, TableHeader, TableRow, TableCell } from '../../components/ui/Table';
import { Badge } from '../../components/ui/Badge';
import { overviewApi } from '../../services/api/overview';
import type { OverviewResponse } from '../../services/api/types';
import { useNavigate } from 'react-router-dom';

const ExecutiveOverview = () => {
  const navigate = useNavigate();
  const [data, setData] = useState<OverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchOverview = async () => {
      try {
        setLoading(true);
        const res = await overviewApi.getOverview();
        setData(res);
      } catch (err: any) {
        setError(err.message || 'Failed to load overview data.');
      } finally {
        setLoading(false);
      }
    };
    fetchOverview();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-text mb-1">Executive Overview</h1>
          <p className="text-sm text-muted-text">Real-time performance and insights across the OMS.</p>
        </div>
        <div className="p-12 text-center text-muted-text">Loading overview...</div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-text mb-1">Executive Overview</h1>
          <p className="text-sm text-muted-text">Real-time performance and insights across the OMS.</p>
        </div>
        <div className="p-4 bg-surface rounded-md border border-red-500 text-red-500">{error || 'Failed to load.'}</div>
      </div>
    );
  }

  const { metrics, recent_orders, recent_tasks } = data;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-text mb-1">Executive Overview</h1>
        <p className="text-sm text-muted-text">Real-time performance and insights across the OMS.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Null representation safely rendered */}
        <MetricCard 
          title="Total Order Value" 
          value={metrics.total_order_value !== null && metrics.total_order_value !== undefined ? `$${metrics.total_order_value}` : '—'} 
          trend="Pending proper calculation" 
          isPositive={true} 
        />
        <MetricCard 
          title="Active Orders" 
          value={metrics.active_orders.toString()} 
          trend="Currently processing" 
          isPositive={true} 
        />
        <MetricCard 
          title="Pending/Needs Revision" 
          value={(metrics.pending_orders + metrics.needs_revision).toString()} 
          trend="Requires attention" 
          isPositive={false} 
        />
        <MetricCard 
          title="Completed" 
          value={metrics.completed_orders.toString()} 
          trend="All time" 
          isPositive={true} 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 p-6 min-h-[300px]">
          <h2 className="text-lg font-medium mb-4">Recent Orders</h2>
          {recent_orders.length === 0 ? (
            <div className="flex items-center justify-center h-32 text-muted-text border-2 border-dashed border-border rounded">
              No recent orders found
            </div>
          ) : (
            <div className="overflow-x-auto rounded-lg border border-border mt-2">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableCell isHeader>Order</TableCell>
                    <TableCell isHeader>Client</TableCell>
                    <TableCell isHeader>Status</TableCell>
                  </TableRow>
                </TableHeader>
                <tbody>
                  {recent_orders.map(o => (
                    <TableRow key={o.id} onClick={() => navigate(`/orders/${o.id}`)}>
                      <TableCell className="font-medium text-text cursor-pointer hover:underline whitespace-nowrap">{o.order_number || o.id}</TableCell>
                      <TableCell className="whitespace-nowrap">{o.client_name || '-'}</TableCell>
                      <TableCell>
                        <Badge status={(o.status || '').toLowerCase() === 'completed' ? 'success' : 'neutral'}>
                          {o.status || '-'}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </tbody>
              </Table>
            </div>
          )}
        </Card>
        
        <Card className="p-6 min-h-[300px]">
          <h2 className="text-lg font-medium mb-4">Recent Tasks</h2>
          {recent_tasks.length === 0 ? (
            <div className="flex items-center justify-center h-32 text-muted-text border-2 border-dashed border-border rounded">
              No recent tasks found
            </div>
          ) : (
            <div className="space-y-4 text-sm">
              {recent_tasks.map(t => (
                <div key={t.id} className="flex items-start gap-3 border-b border-border pb-3 last:border-0">
                  <div className={`w-3 h-3 mt-1 rounded-full ${(t.status || '').toLowerCase() === 'done' ? 'bg-success' : 'bg-warning'}`}></div>
                  <div>
                    <span className="font-medium text-text cursor-pointer hover:underline" onClick={() => navigate(`/orders/${t.order_id}`)}>
                      {t.order_id} - {t.stage_label || t.stage_key}
                    </span>
                    <div className="text-xs text-muted-text mt-0.5">
                      Status: {t.status || '-'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default ExecutiveOverview;
