import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Mic, ShoppingCart, CheckSquare, Users, LineChart, FileText, Activity, Settings, X } from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
}

const Sidebar = ({ isOpen, setIsOpen }: SidebarProps) => {
  const navGroups = [
    {
      title: 'Executive',
      items: [
        { name: 'Overview', path: '/overview', icon: <LayoutDashboard size={18} /> },
        { name: 'Voice Command', path: '/voice-command', icon: <Mic size={18} /> },
      ],
    },
    {
      title: 'OMS',
      items: [
        { name: 'Orders', path: '/orders', icon: <ShoppingCart size={18} /> },
        { name: 'Tasks', path: '/tasks', icon: <CheckSquare size={18} /> },
        { name: 'Customers', path: '/customers', icon: <Users size={18} /> },
      ],
    },
    {
      title: 'Insights',
      items: [
        { name: 'Analytics', path: '/analytics', icon: <LineChart size={18} /> },
        { name: 'Reports', path: '/reports', icon: <FileText size={18} /> },
      ],
    },
    {
      title: 'System',
      items: [
        { name: 'Activity', path: '/activity', icon: <Activity size={18} /> },
        { name: 'Settings', path: '/settings', icon: <Settings size={18} /> },
      ],
    },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/60 z-40 md:hidden backdrop-blur-sm transition-opacity" 
          onClick={() => setIsOpen(false)}
        />
      )}
      
      {/* Sidebar Content */}
      <aside 
        className={`fixed inset-y-0 left-0 z-50 w-[260px] bg-surface border-r border-border flex flex-col transform transition-transform duration-200 ease-in-out md:relative md:translate-x-0 shadow-xl md:shadow-none ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="h-16 px-4 border-b border-border flex justify-between items-center shrink-0">
          <h1 className="text-lg font-semibold text-text tracking-tight">OMS Executive</h1>
          <button 
            className="md:hidden text-muted-text hover:text-text p-1 -mr-1 rounded-md hover:bg-background" 
            onClick={() => setIsOpen(false)}
            aria-label="Close menu"
          >
            <X size={20} />
          </button>
        </div>
        
        <nav className="flex-1 overflow-y-auto p-4 space-y-6">
          {navGroups.map((group) => (
            <div key={group.title}>
              <h2 className="text-xs font-semibold text-muted-text uppercase tracking-wider mb-2 px-3">
                {group.title}
              </h2>
              <ul className="space-y-1">
                {group.items.map((item) => (
                  <li key={item.name}>
                    <NavLink
                      to={item.path}
                      onClick={() => setIsOpen(false)}
                      className={({ isActive }) =>
                        `flex items-center gap-3 px-3 py-2.5 md:py-2 rounded-md text-sm transition-colors ${
                          isActive
                            ? 'bg-primary text-background font-medium shadow-sm'
                            : 'text-text hover:bg-background active:bg-border'
                        }`
                      }
                    >
                      {item.icon}
                      {item.name}
                    </NavLink>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </nav>
      </aside>
    </>
  );
};

export default Sidebar;
