import { Card } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { Calendar, User, MoreHorizontal } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface OrderCardProps {
  order: any;
}

export const OrderCard = ({ order }: OrderCardProps) => {
  const navigate = useNavigate();

  // Helper to determine semantic badge color
  const getStatusColor = (status: string) => {
    const s = (status || '').replace(/_/g, ' ').toLowerCase();
    if (s.includes('completed') || s.includes('done') || s.includes('progress') || s.includes('approved')) return 'success';
    if (s.includes('error') || s.includes('revision') || s.includes('cancelled')) return 'critical';
    if (s.includes('pending approval') || s.includes('review')) return 'warning';
    if (s.includes('pending document') || s.includes('pending')) return 'info';
    if (s.includes('hold')) return 'draft';
    return 'neutral';
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return 'N/A';
    try {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return dateStr;
      return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  const displayId = order.order_number || (order.id ? (order.id.length > 15 ? `#${order.id.slice(0, 8).toUpperCase()}` : order.id) : 'N/A');
  const productType = order.product_type || (order.product_types?.length ? order.product_types.join(', ') : null) || (order.product_configs?.[0]?.product) || 'N/A';
  const statusDisplay = (order.status || 'Unknown').replace(/_/g, ' ').toUpperCase();

  return (
    <div onClick={() => navigate(`/orders/${order.id}`)} className="cursor-pointer h-full transition-transform hover:-translate-y-1 hover:shadow-md">
      <Card className="p-4 flex flex-col h-full bg-white hover:border-primary/50 transition-colors">
        {/* Header */}
        <div className="flex justify-between items-start mb-4 gap-2">
          <span className="text-lg font-bold text-primary truncate" title={order.id}>{displayId}</span>
          <div className="shrink-0">
            <Badge status={getStatusColor(order.status)}>{statusDisplay}</Badge>
          </div>
        </div>

        {/* Body */}
        <div className="flex-1 space-y-4">
          <div>
            <span className="text-[10px] text-muted-text block mb-0.5 whitespace-nowrap">Client</span>
            <span className="text-sm font-bold text-text truncate block" title={order.client_name}>{order.client_name || 'N/A'}</span>
          </div>
          
          <div className="grid grid-cols-2 gap-2">
            <div>
              <span className="text-[10px] text-muted-text block mb-0.5 whitespace-nowrap">Product Type</span>
              <span className="text-xs font-medium text-text truncate block" title={productType}>{productType}</span>
            </div>
            <div>
              <span className="text-[10px] text-muted-text block mb-0.5 whitespace-nowrap">Quantity</span>
              <span className="text-xs font-medium text-text block">{order.quantity || 'N/A'}</span>
            </div>
          </div>
          
          <div>
            <span className="text-[10px] text-muted-text block mb-0.5 whitespace-nowrap">Commitment Date</span>
            <span className="text-xs font-medium text-text block">{formatDate(order.commitment_date)}</span>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-3 mt-4 border-t border-border flex items-center justify-between text-muted-text">
          <div className="flex items-center gap-1.5 shrink-0 min-w-0">
            <Calendar size={14} className="shrink-0" />
            <span className="text-[11px] font-medium whitespace-nowrap truncate">{formatDate(order.commitment_date)}</span>
          </div>
          <div className="flex items-center gap-1.5 shrink-0 min-w-0 ml-2">
            <User size={14} className="shrink-0" />
            <span className="text-[11px] font-medium truncate max-w-[80px]" title={order.sales_exec}>{order.sales_exec?.split(' ')[0] || 'N/A'}</span>
          </div>
          <MoreHorizontal size={16} className="cursor-pointer hover:text-text shrink-0 ml-auto" />
        </div>
      </Card>
    </div>
  );
};
