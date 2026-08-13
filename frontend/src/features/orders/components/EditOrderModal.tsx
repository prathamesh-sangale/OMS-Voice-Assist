import React, { useState } from 'react';
import type { Order } from '../../../services/api/types';
import { Button } from '../../../components/ui/Button';

interface EditOrderModalProps {
  order: Order;
  isOpen: boolean;
  onClose: () => void;
  onSave: (orderId: string, updates: Partial<Order>) => Promise<void>;
}

export const EditOrderModal: React.FC<EditOrderModalProps> = ({ order, isOpen, onClose, onSave }) => {
  const [formData, setFormData] = useState<Partial<Order>>({
    client_name: order.client_name || '',
    status: order.status || '',
    commitment_date: order.commitment_date || '',
    quantity: order.quantity || undefined,
    business_model: order.business_model || '',
    loading_city: order.loading_city || '',
    delivery_city: order.delivery_city || ''
  });
  const [isSaving, setIsSaving] = useState(false);

  if (!isOpen) return null;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'quantity' ? (value ? parseInt(value, 10) : undefined) : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSaving(true);
      await onSave(order.order_number || order.id, formData);
      onClose();
    } catch (error) {
      console.error("Failed to save order", error);
      alert("Failed to save order updates.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-surface rounded-xl border border-border shadow-2xl w-full max-w-lg overflow-hidden flex flex-col">
        <div className="p-5 border-b border-border flex justify-between items-center bg-background/50">
          <h2 className="text-xl font-semibold text-text">Edit Order {order.order_number}</h2>
          <button onClick={onClose} className="text-muted-text hover:text-text">&times;</button>
        </div>
        
        <div className="p-6 overflow-y-auto">
          <form id="edit-order-form" onSubmit={handleSubmit} className="space-y-4">
            
            <div className="space-y-1">
              <label className="text-sm font-medium text-muted-text">Client Name</label>
              <input 
                type="text" 
                name="client_name" 
                value={formData.client_name} 
                onChange={handleChange}
                className="w-full px-3 py-2 bg-background border border-border rounded-md text-text focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-sm font-medium text-muted-text">Status / Stage</label>
                <select 
                  name="status" 
                  value={formData.status} 
                  onChange={handleChange}
                  className="w-full px-3 py-2 bg-background border border-border rounded-md text-text focus:outline-none focus:ring-2 focus:ring-primary/50"
                >
                  <option value="Pending">Pending</option>
                  <option value="Pending Approval">Pending Approval</option>
                  <option value="Approved">Approved</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Done">Done</option>
                  <option value="Cancelled">Cancelled</option>
                  <option value="Needs Revision">Needs Revision</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-sm font-medium text-muted-text">Commitment Date</label>
                <input 
                  type="text" 
                  name="commitment_date" 
                  value={formData.commitment_date} 
                  onChange={handleChange}
                  placeholder="DD-MM-YYYY"
                  className="w-full px-3 py-2 bg-background border border-border rounded-md text-text focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-sm font-medium text-muted-text">Quantity</label>
                <input 
                  type="number" 
                  name="quantity" 
                  value={formData.quantity || ''} 
                  onChange={handleChange}
                  className="w-full px-3 py-2 bg-background border border-border rounded-md text-text focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>

              <div className="space-y-1">
                <label className="text-sm font-medium text-muted-text">Business Model</label>
                <input 
                  type="text" 
                  name="business_model" 
                  value={formData.business_model} 
                  onChange={handleChange}
                  className="w-full px-3 py-2 bg-background border border-border rounded-md text-text focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-sm font-medium text-muted-text">Loading City</label>
                <input 
                  type="text" 
                  name="loading_city" 
                  value={formData.loading_city} 
                  onChange={handleChange}
                  className="w-full px-3 py-2 bg-background border border-border rounded-md text-text focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>

              <div className="space-y-1">
                <label className="text-sm font-medium text-muted-text">Delivery City</label>
                <input 
                  type="text" 
                  name="delivery_city" 
                  value={formData.delivery_city} 
                  onChange={handleChange}
                  className="w-full px-3 py-2 bg-background border border-border rounded-md text-text focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>
            </div>

          </form>
        </div>
        
        <div className="p-4 border-t border-border flex justify-end gap-3 bg-background/50">
          <Button variant="ghost" onClick={onClose} disabled={isSaving}>Cancel</Button>
          <Button variant="primary" type="submit" form="edit-order-form" disabled={isSaving}>
            {isSaving ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </div>
    </div>
  );
};
