import { OrderCard } from './OrderCard';
import { CheckCircle2, Filter, ChevronRight } from 'lucide-react';

interface OrderResultRendererProps {
  data: any;
}

export const OrderResultRenderer = ({ data }: OrderResultRendererProps) => {
  const items = data?.items || [];
  const total = data?.total || 0;
  const pageSize = data?.page_size || 10;
  
  if (items.length === 0) {
    return (
      <div className="mt-6 text-center py-10 bg-surface rounded-lg border border-border">
        <h4 className="text-lg font-medium text-text mb-1">No orders found</h4>
        <p className="text-sm text-muted-text">Try another command or filter.</p>
      </div>
    );
  }



  return (
    <div className="mt-3 w-full">
      <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-2 pb-3 mb-3 border-b border-border">
        <div className="flex items-center gap-2 text-success">
          <CheckCircle2 size={16} />
          <h3 className="text-sm font-medium">I found {total} orders matching your criteria.</h3>
        </div>
        <div className="flex items-center gap-4 text-xs text-muted-text font-medium">
          <div className="flex items-center gap-1.5 cursor-pointer hover:text-text">
            <Filter size={14} />
            <span>Showing {items.length} of {total} orders</span>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-full">
        {items.map((order: any, idx: number) => (
          <OrderCard key={order.id || idx} order={order} />
        ))}
      </div>

      {total > pageSize && (
        <div className="mt-8 flex justify-center items-center gap-2 text-sm font-medium text-muted-text">
          <button className="w-8 h-8 rounded bg-primary text-white flex items-center justify-center">1</button>
          <button className="w-8 h-8 rounded hover:bg-surface-hover flex items-center justify-center">2</button>
          <button className="w-8 h-8 rounded hover:bg-surface-hover flex items-center justify-center">3</button>
          <button className="flex items-center gap-1 px-3 py-1.5 ml-2 border border-border rounded hover:bg-surface-hover">
            Next <ChevronRight size={14} />
          </button>
        </div>
      )}
    </div>
  );
};
