import { Card } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { Calendar, User, ExternalLink, MapPin } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface OrderDetailsCardProps {
  order: any;
}

export const OrderDetailsCard = ({ order }: OrderDetailsCardProps) => {
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
    <Card className="p-5 flex flex-col bg-white border border-border shadow-sm mt-4 w-full max-w-sm">
      {/* Header */}
      <div className="flex justify-between items-start mb-4 gap-2">
        <div>
          <span className="text-xl font-bold text-primary block" title={order.id}>{displayId}</span>
          <span className="text-sm font-medium text-text mt-1 block" title={order.client_name}>{order.client_name || 'Unknown Client'}</span>
        </div>
        <Badge status={getStatusColor(order.status)}>{statusDisplay}</Badge>
      </div>

      {/* Body */}
      <div className="space-y-4 py-2 border-y border-border">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <span className="text-xs text-muted-text block mb-1">Product</span>
            <span className="text-sm font-medium text-text block">{productType}</span>
          </div>
          <div>
            <span className="text-xs text-muted-text block mb-1">Quantity</span>
            <span className="text-sm font-medium text-text block">{order.quantity || 'N/A'}</span>
          </div>
          <div>
            <span className="text-xs text-muted-text block mb-1">Destination</span>
            <span className="text-sm font-medium text-text flex items-center gap-1">
              <MapPin size={12} className="text-muted-text"/>
              {order.destination || 'N/A'}
            </span>
          </div>
          <div>
            <span className="text-xs text-muted-text block mb-1">Commitment</span>
            <span className="text-sm font-medium text-text flex items-center gap-1">
               <Calendar size={12} className="text-muted-text"/>
               {formatDate(order.commitment_date)}
            </span>
          </div>
        </div>
      </div>

      {/* Footer Actions */}
      <div className="pt-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
           <User size={14} className="text-muted-text" />
           <span className="text-xs text-muted-text">{order.sales_exec || 'Unassigned'}</span>
        </div>
        <button 
          onClick={() => navigate(`/orders/${order.id}`)}
          className="flex items-center gap-1.5 text-xs font-medium text-primary hover:text-primary-hover bg-primary/10 hover:bg-primary/20 px-3 py-1.5 rounded transition-colors"
        >
          View Full Details
          <ExternalLink size={12} />
        </button>
      </div>
    </Card>
  );
};
