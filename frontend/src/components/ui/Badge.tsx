

interface BadgeProps {
  children: React.ReactNode;
  status?: 'success' | 'warning' | 'critical' | 'neutral';
}

export const Badge: React.FC<BadgeProps> = ({ children, status = 'neutral' }) => {
  const statusStyles = {
    success: 'bg-success/10 text-success border-success/20',
    warning: 'bg-warning/10 text-warning border-warning/20',
    critical: 'bg-critical/10 text-critical border-critical/20',
    neutral: 'bg-surface text-muted-text border-border',
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${statusStyles[status]}`}>
      {children}
    </span>
  );
};
