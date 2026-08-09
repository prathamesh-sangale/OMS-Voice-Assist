
import { X } from 'lucide-react';

interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export const Drawer: React.FC<DrawerProps> = ({ isOpen, onClose, title, children, footer }) => {
  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-text/20 z-40 transition-opacity"
          onClick={onClose}
        />
      )}
      
      {/* Drawer Panel */}
      <div 
        className={`fixed inset-y-0 right-0 w-96 bg-surface shadow-xl z-50 transform transition-transform duration-300 ease-in-out flex flex-col border-l border-border ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="h-16 flex items-center justify-between px-6 border-b border-border">
          <h2 className="text-lg font-semibold text-text">{title}</h2>
          <button onClick={onClose} className="text-muted-text hover:text-text">
            <X size={20} />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-6">
          {children}
        </div>
        
        {footer && (
          <div className="p-4 border-t border-border bg-background">
            {footer}
          </div>
        )}
      </div>
    </>
  );
};
