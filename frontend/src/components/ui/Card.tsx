

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export const Card: React.FC<CardProps> = ({ children, className = '' }) => {
  return (
    <div className={`bg-white border border-border rounded-lg shadow-sm ${className}`}>
      {children}
    </div>
  );
};

export const MetricCard: React.FC<{ title: string; value: string; trend?: string; isPositive?: boolean }> = ({ title, value, trend, isPositive }) => (
  <Card className="p-4 flex flex-col justify-between h-32">
    <h3 className="text-sm font-medium text-muted-text">{title}</h3>
    <div>
      <div className="text-2xl font-semibold text-text">{value}</div>
      {trend && (
        <div className={`text-xs mt-1 font-medium ${isPositive ? 'text-success' : 'text-critical'}`}>
          {trend}
        </div>
      )}
    </div>
  </Card>
);
