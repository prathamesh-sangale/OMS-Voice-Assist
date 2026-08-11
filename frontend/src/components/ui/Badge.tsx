

interface BadgeProps {
  children: React.ReactNode;
  status?: 'success' | 'warning' | 'critical' | 'neutral' | 'info' | 'draft';
}

export const Badge: React.FC<BadgeProps> = ({ children, status = 'neutral' }) => {
  const statusStyles = {
    success: 'bg-success/10 text-success border-success/20',
    warning: 'bg-[#FFF3CD] text-[#856404] border-[#FFEEBA]', // Custom yellow for warnings
    critical: 'bg-critical/10 text-critical border-critical/20',
    info: 'bg-[#CCE5FF] text-[#004085] border-[#B8DAFF]', // Blue
    draft: 'bg-[#E2E3E5] text-[#383D41] border-[#D6D8DB]', // Grey
    neutral: 'bg-surface text-muted-text border-border',
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${statusStyles[status]}`}>
      {children}
    </span>
  );
};
