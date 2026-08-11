import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './app/layouts/AppLayout';
import ExecutiveOverview from './features/overview/Overview';
import VoiceCommandCenter from './features/voice-command/VoiceCommandCenter';
import OrdersPage from './features/orders/pages/OrdersPage';
import OrderDetail from './features/orders/pages/OrderDetail';
import AnalyticsPage from './features/analytics/pages/AnalyticsPage';
import TasksPage from './features/tasks/pages/TasksPage';
import CustomersPage from './features/customers/pages/CustomersPage';
import ReportsPage from './features/reports/pages/ReportsPage';
import ActivityPage from './features/activity/pages/ActivityPage';
import SettingsPage from './features/settings/pages/SettingsPage';

import { AgentProvider } from './app/providers/AgentProvider';

// Fallback 404
const NotFoundPage = () => (
  <div className="p-6">
    <h1 className="text-2xl font-semibold mb-4">404 - Not Found</h1>
    <div className="p-8 border-2 border-dashed border-border rounded-lg flex items-center justify-center text-muted-text">
      The requested page does not exist.
    </div>
  </div>
);

const App = () => {
  return (
    <BrowserRouter>
      <AgentProvider>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            <Route index element={<Navigate to="/overview" replace />} />
            <Route path="overview" element={<ExecutiveOverview />} />
            <Route path="voice-command" element={<VoiceCommandCenter />} />
            <Route path="orders" element={<OrdersPage />} />
            <Route path="orders/:id" element={<OrderDetail />} />
            <Route path="tasks" element={<TasksPage />} />
            <Route path="customers" element={<CustomersPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="activity" element={<ActivityPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </AgentProvider>
    </BrowserRouter>
  );
};

export default App;
