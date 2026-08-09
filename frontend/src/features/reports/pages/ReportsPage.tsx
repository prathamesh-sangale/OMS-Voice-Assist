
import { Card } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';

const REPORTS = [
  'Executive Order Summary',
  'Order Status Report',
  'Pending Approval Report',
  'Commitment Risk Report',
  'Sales Executive Report'
];

const ReportsPage = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-text">Reports</h1>
          <p className="text-sm text-muted-text">Executive reports and data exports.</p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {REPORTS.map((report) => (
          <Card key={report} className="p-6 flex flex-col justify-between min-h-[160px]">
            <h3 className="font-medium text-text mb-4">{report}</h3>
            <div className="flex items-center gap-3 mt-auto">
              <Button variant="outline" size="sm" className="w-full">View Report</Button>
              <Button variant="ghost" size="sm" className="w-full text-muted-text" disabled>Export</Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default ReportsPage;
