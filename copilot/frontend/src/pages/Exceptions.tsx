import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import { Card, CardContent, CardHeader, CardTitle, Button, Badge, Input, Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '../components/ui';
import { Download, ChevronDown, ChevronUp, Search, Filter, X } from 'lucide-react';
import type { Exception } from '../types';

const mockExceptions: Exception[] = [
  { id: '1', broker_id: 'B1', broker_name: 'CEVA', entry_number: '00416681212', entry_date: '2026-03-08', line_number: 5, part_number: 'P12345', hts_code: '8453905090', gtm_hts_code: '8453905000', country_of_origin: 'CN', declared_value: 25000, duty_amount: 1250, validation_type: 'hts_code', status: 'open', audit_comments: 'Tariff mismatch - broker declared 8453905090, GTM shows 8453905000', created_at: '2026-03-08T10:00:00Z' },
  { id: '2', broker_id: 'B2', broker_name: 'EXPEDITOR', entry_number: '231-4067539-5', entry_date: '2026-03-07', line_number: 2, part_number: 'P67890', hts_code: '8501101000', gtm_hts_code: '8501109000', country_of_origin: 'MX', declared_value: 15000, duty_amount: 0, validation_type: 'add_cvd', status: 'open', audit_comments: 'ADD case number missing', created_at: '2026-03-07T14:30:00Z' },
  { id: '3', broker_id: 'B1', broker_name: 'CEVA', entry_number: '00416681213', entry_date: '2026-03-07', line_number: 1, part_number: 'P11111', hts_code: '7326908688', gtm_hts_code: '7326908688', country_of_origin: 'IN', declared_value: 8500, duty_amount: 425, validation_type: 'anomaly', status: 'escalated', audit_comments: 'AI detected: Value 3x higher than historical average for this part', created_at: '2026-03-07T09:15:00Z' },
  { id: '4', broker_id: 'B3', broker_name: 'FedEx', entry_number: 'FX-2026-00892', entry_date: '2026-03-06', line_number: 3, part_number: 'P22222', hts_code: '8544429090', gtm_hts_code: '8544421000', country_of_origin: 'TW', declared_value: 12000, duty_amount: 600, validation_type: 'hts_code', status: 'resolved', audit_comments: 'Corrected HTS code - cable voltage classification', created_at: '2026-03-06T16:45:00Z', resolved_at: '2026-03-07T11:00:00Z', resolved_by: 'jsmith' },
  { id: '5', broker_id: 'B1', broker_name: 'CEVA', entry_number: '00416681214', entry_date: '2026-03-06', line_number: 8, part_number: 'E-54321', hts_code: '8481803090', gtm_hts_code: '8481803090', country_of_origin: 'CN', declared_value: 45000, duty_amount: 11250, validation_type: 'add_cvd', status: 'open', audit_comments: 'China E-prefix requires ADD verification', created_at: '2026-03-06T08:20:00Z' },
];

export function Exceptions() {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState({ broker: '', status: '', country: '', search: '' });
  const [expandedRow, setExpandedRow] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['exceptions', filters],
    queryFn: () => api.exceptions.list(filters),
    placeholderData: { data: mockExceptions, status: 'success' },
  });

  const resolveMutation = useMutation({
    mutationFn: ({ id, comments }: { id: string; comments: string }) => api.exceptions.resolve(id, comments),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['exceptions'] }),
  });

  const exceptions = data?.data || [];
  const filteredExceptions = exceptions.filter((exc) => {
    if (filters.search && !exc.entry_number.toLowerCase().includes(filters.search.toLowerCase()) && !exc.part_number.toLowerCase().includes(filters.search.toLowerCase())) return false;
    if (filters.broker && exc.broker_name !== filters.broker) return false;
    if (filters.status && exc.status !== filters.status) return false;
    if (filters.country && exc.country_of_origin !== filters.country) return false;
    return true;
  });

  const uniqueBrokers = [...new Set(exceptions.map((e) => e.broker_name))];
  const uniqueCountries = [...new Set(exceptions.map((e) => e.country_of_origin))];

  const handleExport = () => {
    window.open(api.exceptions.export(filters), '_blank');
  };

  const clearFilters = () => {
    setFilters({ broker: '', status: '', country: '', search: '' });
  };

  const hasActiveFilters = filters.broker || filters.status || filters.country;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-slate-900">Exceptions</h2>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => setShowFilters(!showFilters)}>
            <Filter className="h-4 w-4 mr-2" />
            Filters
            {hasActiveFilters && <Badge variant="secondary" className="ml-2">{[filters.broker, filters.status, filters.country].filter(Boolean).length}</Badge>}
          </Button>
          <Button variant="outline" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {showFilters && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-4 flex-wrap">
              <div className="flex-1 min-w-[200px]">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                  <Input
                    placeholder="Search entry # or part #..."
                    value={filters.search}
                    onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                    className="pl-9"
                  />
                </div>
              </div>
              <Select value={filters.broker} onValueChange={(v) => setFilters({ ...filters, broker: v })}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder="Broker" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Brokers</SelectItem>
                  {uniqueBrokers.map((b) => <SelectItem key={b} value={b}>{b}</SelectItem>)}
                </SelectContent>
              </Select>
              <Select value={filters.status} onValueChange={(v) => setFilters({ ...filters, status: v })}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Status</SelectItem>
                  <SelectItem value="open">Open</SelectItem>
                  <SelectItem value="escalated">Escalated</SelectItem>
                  <SelectItem value="resolved">Resolved</SelectItem>
                </SelectContent>
              </Select>
              <Select value={filters.country} onValueChange={(v) => setFilters({ ...filters, country: v })}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder="Country" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Countries</SelectItem>
                  {uniqueCountries.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                </SelectContent>
              </Select>
              {hasActiveFilters && (
                <Button variant="ghost" size="sm" onClick={clearFilters}>
                  <X className="h-4 w-4 mr-1" />
                  Clear
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>
            {filteredExceptions.length} Exception{filteredExceptions.length !== 1 ? 's' : ''}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-slate-50">
                    <th className="w-8"></th>
                    <th className="text-left py-3 px-2 font-medium text-slate-500">Broker</th>
                    <th className="text-left py-3 px-2 font-medium text-slate-500">Entry #</th>
                    <th className="text-left py-3 px-2 font-medium text-slate-500">Date</th>
                    <th className="text-left py-3 px-2 font-medium text-slate-500">Part</th>
                    <th className="text-left py-3 px-2 font-medium text-slate-500">HTS Code</th>
                    <th className="text-left py-3 px-2 font-medium text-slate-500">COO</th>
                    <th className="text-left py-3 px-2 font-medium text-slate-500">Type</th>
                    <th className="text-left py-3 px-2 font-medium text-slate-500">Status</th>
                    <th className="text-right py-3 px-2 font-medium text-slate-500">Value</th>
                    <th className="text-right py-3 px-2 font-medium text-slate-500">Duty</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredExceptions.map((exc) => (
                    <>
                      <tr key={exc.id} className="border-b hover:bg-slate-50 cursor-pointer" onClick={() => setExpandedRow(expandedRow === exc.id ? null : exc.id)}>
                        <td className="py-3 px-2">
                          {expandedRow === exc.id ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                        </td>
                        <td className="py-3 px-2 font-medium">{exc.broker_name}</td>
                        <td className="py-3 px-2 font-mono text-xs">{exc.entry_number}</td>
                        <td className="py-3 px-2 text-slate-500">{exc.entry_date}</td>
                        <td className="py-3 px-2">{exc.part_number}</td>
                        <td className="py-3 px-2 font-mono text-xs">{exc.hts_code}</td>
                        <td className="py-3 px-2">{exc.country_of_origin}</td>
                        <td className="py-3 px-2">
                          <Badge variant={exc.validation_type === 'anomaly' ? 'warning' : 'secondary'}>
                            {exc.validation_type.replace('_', ' ')}
                          </Badge>
                        </td>
                        <td className="py-3 px-2">
                          <Badge variant={exc.status === 'open' ? 'destructive' : exc.status === 'escalated' ? 'warning' : 'success'}>
                            {exc.status}
                          </Badge>
                        </td>
                        <td className="py-3 px-2 text-right font-mono">${exc.declared_value.toLocaleString()}</td>
                        <td className="py-3 px-2 text-right font-mono">${exc.duty_amount.toLocaleString()}</td>
                      </tr>
                      {expandedRow === exc.id && (
                        <tr className="bg-slate-50">
                          <td colSpan={11} className="p-4">
                            <div className="grid grid-cols-2 gap-4">
                              <div>
                                <h4 className="font-medium text-slate-700 mb-2">HTS Comparison</h4>
                                <div className="grid grid-cols-2 gap-2 text-sm">
                                  <div>
                                    <span className="text-slate-500">Broker HTS:</span>
                                    <span className="ml-2 font-mono">{exc.hts_code}</span>
                                  </div>
                                  <div>
                                    <span className="text-slate-500">GTM HTS:</span>
                                    <span className="ml-2 font-mono">{exc.gtm_hts_code}</span>
                                  </div>
                                </div>
                              </div>
                              <div>
                                <h4 className="font-medium text-slate-700 mb-2">Audit Comments</h4>
                                <p className="text-sm text-slate-600">{exc.audit_comments || 'No comments'}</p>
                              </div>
                            </div>
                            {exc.status !== 'resolved' && (
                              <div className="mt-4 flex justify-end gap-2">
                                <Button variant="outline" size="sm">Escalate</Button>
                                <Button
                                  variant="success"
                                  size="sm"
                                  onClick={() => resolveMutation.mutate({ id: exc.id, comments: 'Resolved' })}
                                  disabled={resolveMutation.isPending}
                                >
                                  Resolve
                                </Button>
                              </div>
                            )}
                          </td>
                        </tr>
                      )}
                    </>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
