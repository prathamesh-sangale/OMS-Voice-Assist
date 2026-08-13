import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { Button } from '../../../components/ui/Button';
import { ordersApi } from '../../../services/api/orders';
import type { Order, OrderTask } from '../../../services/api/types';
import { useAgent } from '../../../app/providers/AgentProvider';
import { EditOrderModal } from '../components/EditOrderModal';

const OrderDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [order, setOrder] = useState<Order | null>(null);
  const [tasks, setTasks] = useState<OrderTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  
  const { dispatchCommand } = useAgent();

  useEffect(() => {
    const fetchOrderDetails = async () => {
      if (!id) return;
      try {
        setLoading(true);
        setError(null);
        const [orderData, tasksData] = await Promise.all([
          ordersApi.getOrderById(id),
          ordersApi.getOrderTasks(id)
        ]);
        setOrder(orderData);
        setTasks(tasksData);
      } catch (err: any) {
        setError(err.message || 'Order could not be found.');
      } finally {
        setLoading(false);
      }
    };
    fetchOrderDetails();
  }, [id]);

  const handleSaveOrder = async (orderId: string, updates: Partial<Order>) => {
    try {
      const updatedOrder = await ordersApi.updateOrder(orderId, updates);
      setOrder(updatedOrder);
    } catch (err) {
      throw err;
    }
  };

  const getStatusColor = (status?: string) => {
    if (!status) return 'neutral';
    const s = status.toLowerCase();
    if (s.includes('active') || s.includes('done')) return 'success';
    if (s.includes('pending')) return 'warning';
    if (s.includes('revision') || s.includes('error')) return 'critical';
    return 'neutral';
  };

  if (loading) {
    return (
      <div className="space-y-6 max-w-6xl mx-auto p-12 text-center text-muted-text">
        Loading order details...
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="space-y-6 max-w-6xl mx-auto">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/orders')}>&larr; Back</Button>
        </div>
        <div className="p-12 text-center text-red-500 bg-surface border border-red-500 rounded-md">
          {error || 'Order could not be found.'}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/orders')}>&larr; Back</Button>
          <div>
            <h1 className="text-2xl font-semibold text-text">Order {order.order_number || id}</h1>
            <p className="text-sm text-muted-text">{order.client_name || 'Unknown Client'}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">Print</Button>
          <Button variant="primary" onClick={() => setIsEditModalOpen(true)}>Edit Order</Button>
        </div>
      </div>

      {isEditModalOpen && order && (
        <EditOrderModal
          order={order}
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          onSave={handleSaveOrder}
        />
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Order Information */}
        <Card className="p-6 md:col-span-2 space-y-6">
          <div>
            <h2 className="text-lg font-medium text-text mb-4 border-b border-border pb-2">Order Information</h2>
            <div className="grid grid-cols-2 gap-y-4 text-sm">
              <div>
                <span className="block text-muted-text">Business Model</span>
                <span className="font-medium">{order.business_model || '-'}</span>
              </div>
              <div>
                <span className="block text-muted-text">Product</span>
                <span className="font-medium">{order.product_type || order.product_types?.join(', ') || '-'}</span>
              </div>
              <div>
                <span className="block text-muted-text">Quantity</span>
                <span className="font-medium">{order.quantity || '-'}</span>
              </div>
              <div>
                <span className="block text-muted-text">Status / Stage</span>
                <Badge status={getStatusColor(order.status)}>{order.status || '-'}</Badge>
              </div>
              <div>
                <span className="block text-muted-text">Commitment Date</span>
                <span className="font-medium">{order.commitment_date || '-'}</span>
              </div>
              <div>
                <span className="block text-muted-text">Sales Executive</span>
                <span className="font-medium">{order.sales_exec || '-'}</span>
              </div>
            </div>
          </div>

          <div>
            <h2 className="text-lg font-medium text-text mb-4 border-b border-border pb-2">Commercial Details</h2>
            <div className="grid grid-cols-2 gap-y-4 text-sm">
              <div>
                <span className="block text-muted-text">Billing Name</span>
                <span className="font-medium">{order.billing_name || '-'}</span>
              </div>
              <div>
                <span className="block text-muted-text">Billing Email</span>
                <span className="font-medium">{order.billing_email || '-'}</span>
              </div>
              <div>
                <span className="block text-muted-text">Finance Email</span>
                <span className="font-medium">{order.finance_email || '-'}</span>
              </div>
              <div>
                <span className="block text-muted-text">Is SEZ?</span>
                <span className="font-medium">{order.is_sez || '-'}</span>
              </div>
            </div>
          </div>
          
          {order.containers && order.containers.length > 0 && (
            <div>
              <h2 className="text-lg font-medium text-text mb-4 border-b border-border pb-2">Containers ({order.containers.length})</h2>
              <div className="space-y-2">
                {order.containers.map((container) => (
                  <div key={container.id} className="p-3 bg-background rounded-md border border-border text-sm flex justify-between">
                    <span><span className="text-muted-text">No:</span> {container.container_no || '-'}</span>
                    <span><span className="text-muted-text">App:</span> {container.application || '-'}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Card>

        {/* Logistics & Workflow sidebar */}
        <div className="space-y-6">
          <Card className="p-6">
            <h2 className="text-lg font-medium text-text mb-4 border-b border-border pb-2">Logistics</h2>
            <div className="space-y-4 text-sm">
              <div>
                <span className="block text-muted-text">Loading City</span>
                <span className="font-medium">{order.loading_city || '-'}</span>
              </div>
              <div>
                <span className="block text-muted-text">Delivery City</span>
                <span className="font-medium">{order.delivery_city || '-'}</span>
              </div>
              <div>
                <span className="block text-muted-text">Delivery State</span>
                <span className="font-medium">{order.delivery_state || '-'}</span>
              </div>
              <div>
                <span className="block text-muted-text">Transport Mode</span>
                <span className="font-medium">{order.transport_mode || '-'}</span>
              </div>
              <div>
                <span className="block text-muted-text">PO Received Date</span>
                <span className="font-medium">{order.po_received_date || '-'}</span>
              </div>
            </div>
          </Card>
          
          <Card className="p-6">
            <h2 className="text-lg font-medium text-text mb-4 border-b border-border pb-2">Workflow Stages</h2>
            <div className="space-y-4 text-sm">
              {tasks.length === 0 ? (
                <div className="text-muted-text italic">No workflow tasks available.</div>
              ) : (
                tasks.map((task) => (
                  <div key={task.id} className="flex items-start gap-3">
                    <div className={`w-3 h-3 mt-1 rounded-full ${task.status === 'done' ? 'bg-success' : 'bg-warning'}`}></div>
                    <div>
                      <span className={task.status === 'done' ? 'text-muted-text' : 'font-medium'}>
                        {task.stage_label || task.department || '-'}
                      </span>
                      <div className="text-xs text-muted-text mt-0.5">
                        {task.status === 'done' ? `Completed: ${task.actual_date || task.done_at}` : `Planned: ${task.planned_date}`}
                        {task.done_by ? ` • By ${task.done_by}` : ''}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default OrderDetail;
