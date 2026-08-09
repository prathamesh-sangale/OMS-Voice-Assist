

export const Table = ({ children, className = '' }: { children: React.ReactNode, className?: string }) => (
  <div className={`w-full overflow-x-auto border border-border rounded-lg bg-white ${className}`}>
    <table className="w-full text-sm text-left">
      {children}
    </table>
  </div>
);

export const TableHeader = ({ children }: { children: React.ReactNode }) => (
  <thead className="text-xs text-muted-text uppercase bg-surface border-b border-border">
    {children}
  </thead>
);

export const TableRow = ({ children, onClick, className = '' }: { children: React.ReactNode, onClick?: () => void, className?: string }) => (
  <tr 
    onClick={onClick}
    className={`border-b border-border last:border-0 hover:bg-surface transition-colors ${onClick ? 'cursor-pointer' : ''} ${className}`}
  >
    {children}
  </tr>
);

export const TableCell = ({ children, isHeader = false, className = '' }: { children: React.ReactNode, isHeader?: boolean, className?: string }) => {
  const Component = isHeader ? 'th' : 'td';
  return (
    <Component className={`px-4 py-3 font-medium ${isHeader ? 'font-semibold tracking-wider' : 'text-text'} ${className}`}>
      {children}
    </Component>
  );
};
