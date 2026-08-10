import { useState, useEffect } from 'react';
import { Table, TableHeader, TableRow, TableCell } from '../../../components/ui/Table';
import { Badge } from '../../../components/ui/Badge';
import { tasksApi, type TaskFilters } from '../../../services/api/tasks';
import type { OrderTask } from '../../../services/api/types';
import { useNavigate } from 'react-router-dom';

const TasksPage = () => {
  const navigate = useNavigate();
  const [tasks, setTasks] = useState<OrderTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<TaskFilters>({});
  const [searchInput, setSearchInput] = useState('');

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await tasksApi.getTasks(filters);
        setTasks(response.items);
      } catch (err: any) {
        setError(err.message || 'Failed to load tasks.');
      } finally {
        setLoading(false);
      }
    };
    fetchTasks();
  }, [filters]);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchInput(e.target.value);
  };

  const handleSearchSubmit = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      setFilters(prev => ({ ...prev, search: searchInput }));
    }
  };

  const getStatusColor = (status?: string) => {
    if (!status) return 'neutral';
    const s = status.toLowerCase();
    if (s.includes('done') || s.includes('completed')) return 'success';
    if (s.includes('in_progress') || s.includes('active')) return 'warning';
    if (s.includes('pending')) return 'critical';
    return 'neutral';
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-text">Tasks</h1>
          <p className="text-sm text-muted-text">Cross-departmental workflow tasks.</p>
        </div>
        <div className="flex gap-2 w-full sm:w-auto">
          <input 
            type="text" 
            placeholder="Search tasks (Enter)..." 
            value={searchInput}
            onChange={handleSearch}
            onKeyDown={handleSearchSubmit}
            className="w-full sm:w-64 px-3 py-2 border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-accent"
          />
        </div>
      </div>

      {error ? (
        <div className="p-4 bg-surface rounded-md border border-red-500 text-red-500">
          {error}
        </div>
      ) : loading ? (
        <div className="p-12 text-center text-muted-text">Loading tasks...</div>
      ) : tasks.length === 0 ? (
        <div className="p-12 text-center text-muted-text">No tasks match your filters.</div>
      ) : (
        <div className="overflow-x-auto bg-surface rounded-lg border border-border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableCell isHeader>Task ID</TableCell>
                <TableCell isHeader>Order</TableCell>
                <TableCell isHeader>Department</TableCell>
                <TableCell isHeader>Stage</TableCell>
                <TableCell isHeader>Status</TableCell>
                <TableCell isHeader>Planned</TableCell>
                <TableCell isHeader>Actual</TableCell>
                <TableCell isHeader>Assigned To</TableCell>
              </TableRow>
            </TableHeader>
            <tbody>
              {tasks.map((task) => (
                <TableRow key={task.id}>
                  <TableCell className="font-medium whitespace-nowrap">{task.id}</TableCell>
                  <TableCell className="whitespace-nowrap">
                    <span 
                      className="text-primary cursor-pointer hover:underline"
                      onClick={() => navigate(`/orders/${task.order_id}`)}
                    >
                      {task.order_id}
                    </span>
                  </TableCell>
                  <TableCell className="whitespace-nowrap">{task.department || '-'}</TableCell>
                  <TableCell className="whitespace-nowrap">{task.stage_label || task.stage_key || '-'}</TableCell>
                  <TableCell>
                    <Badge status={getStatusColor(task.status)}>
                      {task.status || '-'}
                    </Badge>
                  </TableCell>
                  <TableCell className="whitespace-nowrap">{task.planned_date || '-'}</TableCell>
                  <TableCell className="whitespace-nowrap">{task.actual_date || task.done_at || '-'}</TableCell>
                  <TableCell className="whitespace-nowrap">{task.assigned_to || task.done_by || '-'}</TableCell>
                </TableRow>
              ))}
            </tbody>
          </Table>
        </div>
      )}
    </div>
  );
};

export default TasksPage;
