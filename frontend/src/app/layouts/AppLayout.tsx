import { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import Sidebar from '../../components/navigation/Sidebar';
import Header from '../../components/navigation/Header';
import { Mic } from 'lucide-react';

const AppLayout = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const navigate = useNavigate();
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

      {!isVoiceCommandPage && (
        <button
          onClick={() => navigate('/voice-command')}
          className="fixed bottom-6 right-6 z-50 w-14 h-14 flex items-center justify-center rounded-full bg-primary text-white shadow-lg shadow-primary/20 hover:bg-opacity-90 transition-all hover:scale-105 active:scale-95"
          title="Open Voice Command"
          aria-label="Voice Command"
        >
          <Mic size={24} />
        </button>
      )}
    </div>
  );
};

export default AppLayout;
