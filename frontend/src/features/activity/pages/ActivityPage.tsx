
import { Table, TableHeader, TableRow, TableCell } from '../../../components/ui/Table';
import { Badge } from '../../../components/ui/Badge';

const MOCK_ACTIVITY = [
  { id: '1', time: '12:42', action: 'Order viewed', object: 'OR603', user: 'CEO', result: 'Success' },
  { id: '2', time: '12:35', action: 'Status changed', object: 'OR598', user: 'System', result: 'Success' },
  { id: '3', time: '11:15', action: 'Login attempt', object: '-', user: 'Unknown', result: 'Failed' },
  { id: '4', time: '09:20', action: 'Report Exported', object: 'Sales Report', user: 'CEO', result: 'Success' },
];

const ActivityPage = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-text">System Activity</h1>
          <p className="text-sm text-muted-text">Audit trail of system and user interactions.</p>
        </div>
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableCell isHeader>Time</TableCell>
            <TableCell isHeader>Action</TableCell>
            <TableCell isHeader>Object</TableCell>
            <TableCell isHeader>User</TableCell>
            <TableCell isHeader>Result</TableCell>
          </TableRow>
        </TableHeader>
        <tbody>
          {MOCK_ACTIVITY.map((log) => (
            <TableRow key={log.id}>
              <TableCell className="text-muted-text">{log.time}</TableCell>
              <TableCell className="font-medium text-text">{log.action}</TableCell>
              <TableCell>{log.object}</TableCell>
              <TableCell>{log.user}</TableCell>
              <TableCell>
                <Badge status={log.result === 'Success' ? 'success' : 'critical'}>{log.result}</Badge>
              </TableCell>
            </TableRow>
          ))}
        </tbody>
      </Table>
    </div>
  );
};

export default ActivityPage;
