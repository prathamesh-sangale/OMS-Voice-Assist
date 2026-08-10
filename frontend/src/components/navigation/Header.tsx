import { Bell, User, Menu } from 'lucide-react';

interface HeaderProps {
  onMenuClick: () => void;
}

const Header = ({ onMenuClick }: HeaderProps) => {
  return (
    <header className="h-16 bg-surface border-b border-border flex items-center justify-between px-4 md:px-6 shrink-0 z-10 sticky top-0">
      <div className="flex items-center gap-3 md:gap-4">
        <button 
          className="md:hidden text-muted-text hover:text-text p-1 -ml-1 rounded-md hover:bg-background" 
          onClick={onMenuClick}
          aria-label="Open menu"
        >
          <Menu size={24} />
        </button>
        <h2 className="text-sm md:text-base font-medium text-text truncate">CEO Command Center</h2>
      </div>
      
      <div className="hidden md:flex items-center gap-6">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-success shadow-[0_0_8px_rgba(0,255,0,0.5)]"></div>
          <span className="text-xs text-muted-text">OMS Connected</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-accent shadow-[0_0_8px_rgba(0,255,255,0.5)]"></div>
          <span className="text-xs text-muted-text">Voice Ready</span>
        </div>
      </div>
      
      <div className="flex items-center gap-3 md:gap-4">
        <button className="text-muted-text hover:text-text p-1 md:p-0 rounded-md hover:bg-background md:hover:bg-transparent">
          <Bell size={20} className="md:w-[18px] md:h-[18px]" />
        </button>
        <div className="flex items-center gap-2 pl-3 md:pl-4 border-l border-border">
          <div className="w-8 h-8 rounded-full bg-background flex items-center justify-center text-primary shrink-0">
            <User size={16} />
          </div>
          <span className="text-sm font-medium hidden sm:block">Chief Executive</span>
        </div>
      </div>
    </header>
  );
};

export default Header;
