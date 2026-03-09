import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { Card, CardContent, CardHeader, CardTitle, Button, Badge } from '../components/ui';
import { Building2, TrendingUp, TrendingDown, AlertTriangle, Plus, Settings } from 'lucide-react';
import { LineChart, Line, ResponsiveContainer } from 'recharts';
import type { Broker } from '../types';

const mockBrokers: Broker[] = [
  {
    id: 'B1',
    name: 'CEVA Logistics',
    code: 'CEVA',
    status: 'active',
    accuracy_score: 96.5,
    entry_count: 2450,
    exception_rate: 3.5,
    last_file_date: '2026-03-09T08:30:00Z',
    schema_mapping: { ITEM_NUM: 'part_number', TARIFF_NUM: 'hts_code', ORIGIN_CTRY: 'country_of_origin' },
    performance_trend: [95, 96, 94, 97, 96, 97, 96.5],
  },
  {
    id: 'B2',
    name: 'Expeditors International',
    code: 'EXPEDITOR',
    status: 'active',
    accuracy_score: 93.2,
    entry_count: 1820,
    exception_rate: 6.8,
    last_file_date: '2026-03-09T07:15:00Z',
    schema_mapping: { PART_NO: 'part_number', HTS: 'hts_code', COUNTRY_OF_ORIGIN: 'country_of_origin' },
    performance_trend: [91, 92, 93, 92, 94, 93, 93.2],
  },
  {
    id: 'B3',
    name: 'FedEx Trade Networks',
    code: 'FedEx',
    status: 'active',
    accuracy_score: 91.8,
    entry_count: 980,
    exception_rate: 8.2,
    last_file_date: '2026-03-08T16:45:00Z',
    schema_mapping: { PRODUCT_ID: 'part_number', TARIFF_CODE: 'hts_code', ORIGIN: 'country_of_origin' },
    performance_trend: [89, 90, 91, 90, 92, 91, 91.8],
  },
  {
    id: 'B4',
    name: 'UPS Supply Chain',
    code: 'UPS',
    status: 'active',
    accuracy_score: 89.4,
    entry_count: 650,
    exception_rate: 10.6,
    last_file_date: '2026-03-08T14:20:00Z',
    schema_mapping: { PART_NUMBER: 'part_number', HS_CODE: 'hts_code', COO: 'country_of_origin' },
    performance_trend: [88, 87, 89, 88, 90, 89, 89.4],
  },
  {
    id: 'B5',
    name: 'Kuehne+Nagel',
    code: 'KUEHNE',
    status: 'pending',
    accuracy_score: 0,
    entry_count: 0,
    exception_rate: 0,
    last_file_date: '',
    schema_mapping: { TEILENUMMER: 'part_number', ZOLLTARIFNUMMER: 'hts_code', URSPRUNGSLAND: 'country_of_origin' },
    performance_trend: [],
  },
];

function Sparkline({ data, color }: { data: number[]; color: string }) {
  if (data.length === 0) return <span className="text-slate-400 text-sm">No data</span>;
  const chartData = data.map((v, i) => ({ value: v }));
  return (
    <ResponsiveContainer width={100} height={30}>
      <LineChart data={chartData}>
        <Line type="monotone" dataKey="value" stroke={color} strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}

function BrokerCard({ broker }: { broker: Broker }) {
  const trend = broker.performance_trend.length >= 2
    ? broker.performance_trend[broker.performance_trend.length - 1] - broker.performance_trend[0]
    : 0;
  const isImproving = trend >= 0;

  const getScoreColor = (score: number) => {
    if (score >= 95) return 'text-green-600';
    if (score >= 90) return 'text-amber-600';
    return 'text-red-600';
  };

  return (
    <Card className={broker.status === 'pending' ? 'border-amber-200 bg-amber-50/30' : ''}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-lg bg-slate-100 flex items-center justify-center">
              <Building2 className="h-6 w-6 text-slate-600" />
            </div>
            <div>
              <h3 className="font-semibold text-lg text-slate-900">{broker.name}</h3>
              <span className="text-sm text-slate-500 font-mono">{broker.code}</span>
            </div>
          </div>
          <Badge variant={broker.status === 'active' ? 'success' : 'warning'}>
            {broker.status}
          </Badge>
        </div>

        {broker.status === 'active' ? (
          <>
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div>
                <p className="text-sm text-slate-500 mb-1">Accuracy</p>
                <p className={`text-2xl font-bold ${getScoreColor(broker.accuracy_score)}`}>
                  {broker.accuracy_score.toFixed(1)}%
                </p>
              </div>
              <div>
                <p className="text-sm text-slate-500 mb-1">Entries (MTD)</p>
                <p className="text-2xl font-bold text-slate-900">{broker.entry_count.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-slate-500 mb-1">Exception Rate</p>
                <p className="text-2xl font-bold text-slate-900">{broker.exception_rate.toFixed(1)}%</p>
              </div>
            </div>

            <div className="flex items-center justify-between pt-4 border-t">
              <div className="flex items-center gap-2">
                <span className="text-sm text-slate-500">7-Day Trend:</span>
                <Sparkline
                  data={broker.performance_trend}
                  color={isImproving ? '#16a34a' : '#dc2626'}
                />
                {isImproving ? (
                  <TrendingUp className="h-4 w-4 text-green-600" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-600" />
                )}
              </div>
              <Button variant="ghost" size="sm">
                <Settings className="h-4 w-4 mr-1" />
                Configure
              </Button>
            </div>

            <div className="mt-4 text-xs text-slate-400">
              Last file: {new Date(broker.last_file_date).toLocaleString()}
            </div>
          </>
        ) : (
          <div className="py-4 text-center">
            <AlertTriangle className="h-8 w-8 text-amber-500 mx-auto mb-2" />
            <p className="text-sm text-slate-600 mb-4">Pending onboarding - schema mapping configured</p>
            <Button variant="default" size="sm">
              Complete Onboarding
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function Brokers() {
  const [showOnboarding, setShowOnboarding] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['brokers'],
    queryFn: api.brokers.list,
    placeholderData: { data: mockBrokers, status: 'success' },
  });

  const brokers = data?.data || [];
  const activeBrokers = brokers.filter((b) => b.status === 'active');
  const pendingBrokers = brokers.filter((b) => b.status === 'pending');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-slate-900">Broker Management</h2>
        <Button onClick={() => setShowOnboarding(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Onboard New Broker
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-slate-500">Total Brokers</p>
            <p className="text-3xl font-bold text-slate-900">{brokers.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-slate-500">Active</p>
            <p className="text-3xl font-bold text-green-600">{activeBrokers.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-slate-500">Pending Setup</p>
            <p className="text-3xl font-bold text-amber-600">{pendingBrokers.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-slate-500">Avg Accuracy</p>
            <p className="text-3xl font-bold text-slate-900">
              {(activeBrokers.reduce((sum, b) => sum + b.accuracy_score, 0) / activeBrokers.length).toFixed(1)}%
            </p>
          </CardContent>
        </Card>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900" />
        </div>
      ) : (
        <>
          {pendingBrokers.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-slate-700 mb-4">Pending Onboarding</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {pendingBrokers.map((broker) => (
                  <BrokerCard key={broker.id} broker={broker} />
                ))}
              </div>
            </div>
          )}

          <div>
            <h3 className="text-lg font-semibold text-slate-700 mb-4">Active Brokers</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {activeBrokers.map((broker) => (
                <BrokerCard key={broker.id} broker={broker} />
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
