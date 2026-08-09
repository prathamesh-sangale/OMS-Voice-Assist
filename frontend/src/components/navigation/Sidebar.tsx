
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Mic, ShoppingCart, CheckSquare, Users, LineChart, FileText, Activity, Settings } from 'lucide-react';

const Sidebar = () => {
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
    <aside className="w-[260px] h-screen bg-surface border-r border-border flex flex-col">
      <div className="p-4 border-b border-border">
        <h1 className="text-lg font-semibold text-text tracking-tight">OMS Executive</h1>
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
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                        isActive
                          ? 'bg-primary text-background font-medium'
                          : 'text-text hover:bg-background'
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
  );
};

export default Sidebar;
