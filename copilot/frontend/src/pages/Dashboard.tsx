import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { Card, CardContent, CardHeader, CardTitle, Badge } from '../components/ui';
import { ArrowUpRight, ArrowDownRight, AlertTriangle, CheckCircle, TrendingUp, DollarSign } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { Link } from 'react-router-dom';
import type { DashboardData } from '../types';

const mockData: DashboardData = {
  kpis: {
    pass_rate: 94.2,
    total_exceptions: 147,
    anomalies_detected: 23,
    duty_at_risk: 1245000,
  },
  recent_exceptions: [
    { id: '1', broker_id: 'B1', broker_name: 'CEVA', entry_number: '00416681212', entry_date: '2026-03-08', line_number: 5, part_number: 'P12345', hts_code: '8453905090', gtm_hts_code: '8453905000', country_of_origin: 'CN', declared_value: 25000, duty_amount: 1250, validation_type: 'hts_code', status: 'open', audit_comments: '', created_at: '2026-03-08T10:00:00Z' },
    { id: '2', broker_id: 'B2', broker_name: 'EXPEDITOR', entry_number: '231-4067539-5', entry_date: '2026-03-07', line_number: 2, part_number: 'P67890', hts_code: '8501101000', gtm_hts_code: '8501109000', country_of_origin: 'MX', declared_value: 15000, duty_amount: 0, validation_type: 'add_cvd', status: 'open', audit_comments: '', created_at: '2026-03-07T14:30:00Z' },
    { id: '3', broker_id: 'B1', broker_name: 'CEVA', entry_number: '00416681213', entry_date: '2026-03-07', line_number: 1, part_number: 'P11111', hts_code: '7326908688', gtm_hts_code: '7326908688', country_of_origin: 'IN', declared_value: 8500, duty_amount: 425, validation_type: 'anomaly', status: 'escalated', audit_comments: 'Unusual value pattern', created_at: '2026-03-07T09:15:00Z' },
  ],
  broker_scores: [
    { broker: 'CEVA', accuracy: 96.5, volume: 2450 },
    { broker: 'EXPEDITOR', accuracy: 93.2, volume: 1820 },
    { broker: 'FedEx', accuracy: 91.8, volume: 980 },
    { broker: 'UPS', accuracy: 89.4, volume: 650 },
    { broker: 'Kuehne+Nagel', accuracy: 88.1, volume: 340 },
  ],
  pending_rules: 5,
  trends: [
    { date: 'Mar 3', exceptions: 18, entries: 450 },
    { date: 'Mar 4', exceptions: 22, entries: 480 },
    { date: 'Mar 5', exceptions: 15, entries: 520 },
    { date: 'Mar 6', exceptions: 28, entries: 510 },
    { date: 'Mar 7', exceptions: 32, entries: 490 },
    { date: 'Mar 8', exceptions: 24, entries: 540 },
    { date: 'Mar 9', exceptions: 8, entries: 280 },
  ],
};

function KPICard({ label, value, change, trend, format, icon: Icon }: {
  label: string;
  value: number;
  change?: number;
  trend?: 'up' | 'down' | 'neutral';
  format?: 'percent' | 'currency' | 'number';
  icon?: React.ElementType;
}) {
  const formatValue = (v: number) => {
    if (format === 'percent') return `${v.toFixed(1)}%`;
    if (format === 'currency') return `$${(v / 1000).toFixed(0)}K`;
    return v.toLocaleString();
  };

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-slate-500">{label}</p>
          {Icon && <Icon className="h-5 w-5 text-slate-400" />}
        </div>
        <div className="mt-2 flex items-baseline gap-2">
          <p className="text-3xl font-bold text-slate-900">{formatValue(value)}</p>
          {change !== undefined && (
            <span className={`flex items-center text-sm font-medium ${
              trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-slate-500'
            }`}>
              {trend === 'up' ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
              {Math.abs(change)}%
            </span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: api.dashboard.get,
    placeholderData: { data: mockData, status: 'success' },
  });

  const dashboard = data?.data || mockData;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="h-12 w-12 text-amber-500 mx-auto mb-4" />
        <p className="text-slate-600">Failed to load dashboard data</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {dashboard.pending_rules > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-5 w-5 text-amber-600" />
            <span className="text-sm font-medium text-amber-800">
              {dashboard.pending_rules} AI-discovered rules pending review
            </span>
          </div>
          <Link to="/rules?status=pending" className="text-sm font-medium text-amber-700 hover:text-amber-900">
            Review now &rarr;
          </Link>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          label="Pass Rate"
          value={dashboard.kpis.pass_rate}
          change={2.3}
          trend="up"
          format="percent"
          icon={CheckCircle}
        />
        <KPICard
          label="Total Exceptions"
          value={dashboard.kpis.total_exceptions}
          change={-5.1}
          trend="down"
          format="number"
          icon={AlertTriangle}
        />
        <KPICard
          label="Anomalies Detected"
          value={dashboard.kpis.anomalies_detected}
          format="number"
          icon={TrendingUp}
        />
        <KPICard
          label="Duty at Risk"
          value={dashboard.kpis.duty_at_risk}
          change={12.4}
          trend="up"
          format="currency"
          icon={DollarSign}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Exception Trend (7 Days)</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={dashboard.trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="#64748b" />
                <YAxis tick={{ fontSize: 12 }} stroke="#64748b" />
                <Tooltip />
                <Line type="monotone" dataKey="exceptions" stroke="#ef4444" strokeWidth={2} dot={{ fill: '#ef4444' }} name="Exceptions" />
                <Line type="monotone" dataKey="entries" stroke="#3b82f6" strokeWidth={2} dot={{ fill: '#3b82f6' }} name="Entries" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Broker Scorecard</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dashboard.broker_scores} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis type="number" domain={[80, 100]} tick={{ fontSize: 12 }} stroke="#64748b" />
                <YAxis dataKey="broker" type="category" tick={{ fontSize: 12 }} stroke="#64748b" width={100} />
                <Tooltip />
                <Bar dataKey="accuracy" fill="#3b82f6" radius={[0, 4, 4, 0]} name="Accuracy %" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Recent Exceptions</CardTitle>
          <Link to="/exceptions" className="text-sm font-medium text-blue-600 hover:text-blue-800">
            View all &rarr;
          </Link>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-2 font-medium text-slate-500">Broker</th>
                  <th className="text-left py-3 px-2 font-medium text-slate-500">Entry #</th>
                  <th className="text-left py-3 px-2 font-medium text-slate-500">Part</th>
                  <th className="text-left py-3 px-2 font-medium text-slate-500">Type</th>
                  <th className="text-left py-3 px-2 font-medium text-slate-500">Status</th>
                  <th className="text-right py-3 px-2 font-medium text-slate-500">Duty</th>
                </tr>
              </thead>
              <tbody>
                {dashboard.recent_exceptions.map((exc) => (
                  <tr key={exc.id} className="border-b last:border-0 hover:bg-slate-50">
                    <td className="py-3 px-2">{exc.broker_name}</td>
                    <td className="py-3 px-2 font-mono text-xs">{exc.entry_number}</td>
                    <td className="py-3 px-2">{exc.part_number}</td>
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
                    <td className="py-3 px-2 text-right font-mono">${exc.duty_amount.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
