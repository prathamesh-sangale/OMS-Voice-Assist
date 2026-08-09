
import { Bell, User } from 'lucide-react';

const Header = () => {
  return (
    <header className="h-16 bg-surface border-b border-border flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        <h2 className="text-sm font-medium text-text">CEO Command Center</h2>
      </div>
      
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-success"></div>
          <span className="text-xs text-muted-text">OMS Connected</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-accent"></div>
          <span className="text-xs text-muted-text">Voice Ready</span>
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        <button className="text-muted-text hover:text-text">
          <Bell size={18} />
        </button>
        <div className="flex items-center gap-2 pl-4 border-l border-border">
          <div className="w-8 h-8 rounded-full bg-background flex items-center justify-center text-primary">
            <User size={16} />
          </div>
          <span className="text-sm font-medium">Chief Executive</span>
        </div>
      </div>
    </header>
  );
};

export default Header;
