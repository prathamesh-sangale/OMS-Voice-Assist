import { useState, useEffect } from 'react';
import { Table, TableHeader, TableRow, TableCell } from '../../../components/ui/Table';
import { Badge } from '../../../components/ui/Badge';
import { Button } from '../../../components/ui/Button';
import { Drawer } from '../../../components/ui/Drawer';
import { useNavigate } from 'react-router-dom';
import { Search, X } from 'lucide-react';
import { ordersApi, type OrderFilters } from '../../../services/api/orders';
import type { Order } from '../../../services/api/types';

const OrdersPage = () => {
  const navigate = useNavigate();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const [filters, setFilters] = useState<OrderFilters>({});
  const [searchInput, setSearchInput] = useState('');

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await ordersApi.getOrders(filters);
        setOrders(response.items);
      } catch (err: any) {
        setError(err.message || 'Failed to load orders.');
      } finally {
        setLoading(false);
      }
    };
    fetchOrders();
  }, [filters]);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setFilters(prev => ({ ...prev, search: searchInput }));
    }, 300);
    return () => clearTimeout(timeoutId);
  }, [searchInput]);

  const getStatusColor = (status?: string) => {
    if (!status) return 'neutral';
    const s = status.toLowerCase();
    if (s.includes('active') || s.includes('done')) return 'success';
    if (s.includes('pending')) return 'warning';
    if (s.includes('revision') || s.includes('error')) return 'critical';
    return 'neutral';
  };

  const handleRowClick = (order: Order) => {
    setSelectedOrder(order);
    setIsDrawerOpen(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-text">Orders Management</h1>
          <p className="text-sm text-muted-text">View and manage OMS orders.</p>
        </div>
        <div className="flex gap-2 w-full sm:w-auto">
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-text" />
            <input 
              type="text" 
              placeholder="Search orders..." 
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="w-full pl-9 pr-8 py-2 border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-accent bg-background text-text"
            />
            {searchInput && (
              <button 
                type="button"
                onClick={() => setSearchInput('')}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-muted-text hover:text-text rounded-full hover:bg-surface-hover"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>
      </div>

      {error ? (
        <div className="p-4 bg-surface rounded-md border border-red-500 text-red-500">
          {error}
        </div>
      ) : loading ? (
        <div className="p-12 text-center text-muted-text">Loading orders...</div>
      ) : orders.length === 0 ? (
        <div className="p-12 text-center text-muted-text">No orders match your filters.</div>
      ) : (
        <div className="overflow-x-auto bg-surface rounded-lg border border-border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableCell isHeader>Order</TableCell>
                <TableCell isHeader>Customer</TableCell>
                <TableCell isHeader>Product Type</TableCell>
                <TableCell isHeader>Qty</TableCell>
                <TableCell isHeader>Business Model</TableCell>
                <TableCell isHeader>Status</TableCell>
                <TableCell isHeader>Commitment</TableCell>
                <TableCell isHeader>Sales Exec</TableCell>
              </TableRow>
            </TableHeader>
            <tbody>
              {orders.map((order) => (
                <TableRow key={order.id} onClick={() => handleRowClick(order)}>
                  <TableCell className="font-medium whitespace-nowrap">{order.order_number || '-'}</TableCell>
                  <TableCell className="whitespace-nowrap">{order.client_name || '-'}</TableCell>
                  <TableCell>{order.product_type || order.product_types?.join(', ') || '-'}</TableCell>
                  <TableCell>{order.quantity || '-'}</TableCell>
                  <TableCell>{order.business_model || '-'}</TableCell>
                  <TableCell>
                    <Badge status={getStatusColor(order.status)}>{order.status || '-'}</Badge>
                  </TableCell>
                  <TableCell className="whitespace-nowrap">{order.commitment_date || '-'}</TableCell>
                  <TableCell className="whitespace-nowrap">{order.sales_exec || '-'}</TableCell>
                </TableRow>
              ))}
            </tbody>
          </Table>
        </div>
      )}

      <Drawer 
        isOpen={isDrawerOpen} 
        onClose={() => setIsDrawerOpen(false)}
        title={`Order Inspection: ${selectedOrder?.order_number || selectedOrder?.id}`}
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setIsDrawerOpen(false)}>Close</Button>
            <Button onClick={() => navigate(`/orders/${selectedOrder?.id}`)}>View Full Order</Button>
          </div>
        }
      >
        {selectedOrder && (
          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-semibold text-muted-text uppercase tracking-wider mb-2">Details</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-text">Customer</span>
                  <span className="font-medium text-text">{selectedOrder.client_name || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-text">Product</span>
                  <span className="font-medium text-text">{selectedOrder.product_type || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-text">Quantity</span>
                  <span className="font-medium text-text">{selectedOrder.quantity || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-text">Sales Executive</span>
                  <span className="font-medium text-text">{selectedOrder.sales_exec || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-text">Commitment</span>
                  <span className="font-medium text-text">{selectedOrder.commitment_date || '-'}</span>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="text-sm font-semibold text-muted-text uppercase tracking-wider mb-2">Status</h3>
              <Badge status={getStatusColor(selectedOrder.status)}>{selectedOrder.status || '-'}</Badge>
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default OrdersPage;
