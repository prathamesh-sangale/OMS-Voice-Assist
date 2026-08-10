import { useState, useEffect } from 'react';
import { Table, TableHeader, TableRow, TableCell } from '../../../components/ui/Table';
import { Badge } from '../../../components/ui/Badge';
import { customersApi, type CustomerFilters } from '../../../services/api/customers';
import type { CustomerView } from '../../../services/api/types';

const CustomersPage = () => {
  const [customers, setCustomers] = useState<CustomerView[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<CustomerFilters>({});
  const [searchInput, setSearchInput] = useState('');

  useEffect(() => {
    const fetchCustomers = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await customersApi.getCustomers(filters);
        setCustomers(response.items);
      } catch (err: any) {
        setError(err.message || 'Failed to load customers.');
      } finally {
        setLoading(false);
      }
    };
    fetchCustomers();
  }, [filters]);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchInput(e.target.value);
  };

  const handleSearchSubmit = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      setFilters(prev => ({ ...prev, search: searchInput }));
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-text">Customers</h1>
          <p className="text-sm text-muted-text">Derived client directory from active orders.</p>
        </div>
        <div className="flex gap-2 w-full sm:w-auto">
          <input 
            type="text" 
            placeholder="Search customers (Enter)..." 
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
        <div className="p-12 text-center text-muted-text">Loading customers...</div>
      ) : customers.length === 0 ? (
        <div className="p-12 text-center text-muted-text">No customers match your filters.</div>
      ) : (
        <div className="overflow-x-auto bg-surface rounded-lg border border-border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableCell isHeader>Customer</TableCell>
                <TableCell isHeader>Type</TableCell>
                <TableCell isHeader>Active / Total Orders</TableCell>
                <TableCell isHeader>Sales Execs</TableCell>
                <TableCell isHeader>Loading Cities</TableCell>
                <TableCell isHeader>Delivery Cities</TableCell>
                <TableCell isHeader>Status</TableCell>
              </TableRow>
            </TableHeader>
            <tbody>
              {customers.map((c, i) => (
                <TableRow key={i}>
                  <TableCell className="font-medium text-text whitespace-nowrap">{c.client_name}</TableCell>
                  <TableCell className="whitespace-nowrap">{c.customer_type || '-'}</TableCell>
                  <TableCell className="whitespace-nowrap">{c.active_orders} / {c.total_orders}</TableCell>
                  <TableCell>
                    <div className="max-w-[150px] truncate" title={c.sales_execs.join(', ')}>
                      {c.sales_execs.join(', ') || '-'}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="max-w-[150px] truncate" title={c.loading_cities.join(', ')}>
                      {c.loading_cities.join(', ') || '-'}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="max-w-[150px] truncate" title={c.delivery_cities.join(', ')}>
                      {c.delivery_cities.join(', ') || '-'}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge status={c.active_orders > 0 ? 'success' : 'neutral'}>
                      {c.active_orders > 0 ? 'Active' : 'Inactive'}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </tbody>
          </Table>
        </div>
      )}
    </div>
  );
};

export default CustomersPage;
