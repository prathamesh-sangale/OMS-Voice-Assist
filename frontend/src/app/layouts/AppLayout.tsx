import { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from '../../components/navigation/Sidebar';
import Header from '../../components/navigation/Header';
import GlobalCommandOverlay from '../../components/agent/GlobalCommandOverlay';

const AppLayout = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const location = useLocation();

  const isVoiceCommandPage = location.pathname === '/voice-command';

  return (
    <div className="flex h-screen w-full bg-background overflow-hidden text-text font-sans relative">
      <Sidebar isOpen={isSidebarOpen} setIsOpen={setIsSidebarOpen} />
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        <Header onMenuClick={() => setIsSidebarOpen(true)} />
        <main className="flex-1 overflow-auto p-4 md:p-6 relative">
          <Outlet />
        </main>
      </div>

      {!isVoiceCommandPage && <GlobalCommandOverlay />}
    </div>
  );
};

export default AppLayout;
