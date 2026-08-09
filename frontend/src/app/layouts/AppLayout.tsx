
import { Outlet } from 'react-router-dom';
import Sidebar from '../../components/navigation/Sidebar';
import Header from '../../components/navigation/Header';

const AppLayout = () => {
  return (
    <div className="flex h-screen w-full bg-background overflow-hidden text-text font-sans">
      <Sidebar />
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AppLayout;
