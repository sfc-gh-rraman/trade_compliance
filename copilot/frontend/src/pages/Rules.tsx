import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import { Card, CardContent, CardHeader, CardTitle, Button, Badge, Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '../components/ui';
import { Sparkles, CheckCircle, XCircle, ToggleLeft, ToggleRight, AlertTriangle } from 'lucide-react';
import type { Rule } from '../types';

const mockRules: Rule[] = [
  {
    id: 'R1',
    name: 'China E-Prefix ADD Validation',
    description: 'Parts with E-prefix from China require Anti-Dumping Duty verification',
    rule_type: 'ai_discovered',
    category: 'ADD/CVD',
    status: 'pending',
    confidence: 0.92,
    created_at: '2026-03-08T10:00:00Z',
    conditions: [{ field: 'part_number', operator: 'starts_with', value: 'E-' }, { field: 'country_of_origin', operator: 'equals', value: 'CN' }],
    estimated_impact: { entries_affected: 234, duty_at_risk: 125000 },
  },
  {
    id: 'R2',
    name: 'HTS 8453905090 Misclassification',
    description: 'Common misclassification pattern detected - broker often uses 8453905090 instead of 8453905000',
    rule_type: 'ai_discovered',
    category: 'HTS Validation',
    status: 'pending',
    confidence: 0.87,
    created_at: '2026-03-07T14:30:00Z',
    conditions: [{ field: 'hts_code', operator: 'equals', value: '8453905090' }],
    estimated_impact: { entries_affected: 156, duty_at_risk: 78000 },
  },
  {
    id: 'R3',
    name: 'High Value FTA Threshold',
    description: 'Entries over $50K with FTA claims require additional documentation',
    rule_type: 'validation',
    category: 'FTA',
    status: 'active',
    confidence: 1.0,
    created_at: '2026-02-15T09:00:00Z',
    approved_by: 'admin',
    conditions: [{ field: 'declared_value', operator: 'greater_than', value: 50000 }, { field: 'preferential_program', operator: 'in', value: ['USMCA', 'CAFTA'] }],
    estimated_impact: { entries_affected: 89, duty_at_risk: 45000 },
  },
  {
    id: 'R4',
    name: 'Indian Steel CVD Check',
    description: 'Steel products from India subject to CVD - validate case numbers',
    rule_type: 'compliance',
    category: 'ADD/CVD',
    status: 'active',
    confidence: 1.0,
    created_at: '2026-01-20T11:00:00Z',
    approved_by: 'admin',
    conditions: [{ field: 'hts_code', operator: 'starts_with', value: '72' }, { field: 'country_of_origin', operator: 'equals', value: 'IN' }],
    estimated_impact: { entries_affected: 67, duty_at_risk: 89000 },
  },
  {
    id: 'R5',
    name: 'Taiwan vs China COO Alert',
    description: 'AI detected inconsistent COO declarations between Taiwan and China for similar parts',
    rule_type: 'ai_discovered',
    category: 'Origin',
    status: 'pending',
    confidence: 0.78,
    created_at: '2026-03-06T16:45:00Z',
    conditions: [{ field: 'country_of_origin', operator: 'in', value: ['TW', 'CN'] }],
    estimated_impact: { entries_affected: 45, duty_at_risk: 23000 },
  },
];

function ConfidenceBar({ confidence }: { confidence: number }) {
  const pct = confidence * 100;
  const color = pct >= 90 ? 'bg-green-500' : pct >= 80 ? 'bg-amber-500' : 'bg-red-500';
  return (
    <div className="flex items-center gap-2">
      <div className="w-24 h-2 bg-slate-200 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-slate-500">{pct.toFixed(0)}%</span>
    </div>
  );
}

export function Rules() {
  const queryClient = useQueryClient();
  const [filter, setFilter] = useState<string>('');

  const { data, isLoading } = useQuery({
    queryKey: ['rules', filter],
    queryFn: () => api.rules.list({ status: filter }),
    placeholderData: { data: mockRules, status: 'success' },
  });

  const approveMutation = useMutation({
    mutationFn: (id: string) => api.rules.approve(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['rules'] }),
  });

  const rejectMutation = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) => api.rules.reject(id, reason),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['rules'] }),
  });

  const toggleMutation = useMutation({
    mutationFn: ({ id, active }: { id: string; active: boolean }) => api.rules.toggle(id, active),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['rules'] }),
  });

  const rules = data?.data || [];
  const filteredRules = filter ? rules.filter((r) => r.status === filter) : rules;
  const pendingCount = rules.filter((r) => r.status === 'pending').length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-slate-900">Validation Rules</h2>
        <Select value={filter} onValueChange={setFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="All Rules" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Rules</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="pending">Pending Review ({pendingCount})</SelectItem>
            <SelectItem value="disabled">Disabled</SelectItem>
            <SelectItem value="rejected">Rejected</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {pendingCount > 0 && !filter && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-center gap-3">
          <Sparkles className="h-5 w-5 text-blue-600" />
          <span className="text-sm font-medium text-blue-800">
            {pendingCount} AI-discovered rule{pendingCount !== 1 ? 's' : ''} awaiting your review
          </span>
        </div>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900" />
        </div>
      ) : (
        <div className="grid gap-4">
          {filteredRules.map((rule) => (
            <Card key={rule.id} className={rule.status === 'pending' ? 'border-blue-200 bg-blue-50/30' : ''}>
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-lg text-slate-900">{rule.name}</h3>
                      {rule.rule_type === 'ai_discovered' && (
                        <Badge variant="secondary" className="gap-1">
                          <Sparkles className="h-3 w-3" />
                          AI Discovered
                        </Badge>
                      )}
                      <Badge variant={
                        rule.status === 'active' ? 'success' :
                        rule.status === 'pending' ? 'warning' :
                        rule.status === 'rejected' ? 'destructive' : 'secondary'
                      }>
                        {rule.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-slate-600 mb-4">{rule.description}</p>

                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-slate-500">Category:</span>
                        <span className="ml-2 font-medium">{rule.category}</span>
                      </div>
                      <div>
                        <span className="text-slate-500">Confidence:</span>
                        <span className="ml-2">
                          <ConfidenceBar confidence={rule.confidence} />
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-500">Created:</span>
                        <span className="ml-2">{new Date(rule.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>

                    <div className="mt-4 p-3 bg-slate-100 rounded-lg">
                      <h4 className="text-xs font-medium text-slate-500 uppercase mb-2">Estimated Impact</h4>
                      <div className="flex gap-6 text-sm">
                        <div>
                          <span className="text-slate-600">Entries Affected:</span>
                          <span className="ml-2 font-semibold">{rule.estimated_impact.entries_affected.toLocaleString()}</span>
                        </div>
                        <div>
                          <span className="text-slate-600">Duty at Risk:</span>
                          <span className="ml-2 font-semibold text-amber-600">${rule.estimated_impact.duty_at_risk.toLocaleString()}</span>
                        </div>
                      </div>
                    </div>

                    <div className="mt-4">
                      <h4 className="text-xs font-medium text-slate-500 uppercase mb-2">Conditions</h4>
                      <div className="flex flex-wrap gap-2">
                        {rule.conditions.map((cond, i) => (
                          <Badge key={i} variant="outline" className="font-mono text-xs">
                            {cond.field} {cond.operator} {Array.isArray(cond.value) ? cond.value.join(', ') : cond.value}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col gap-2 ml-4">
                    {rule.status === 'pending' && (
                      <>
                        <Button
                          variant="success"
                          size="sm"
                          onClick={() => approveMutation.mutate(rule.id)}
                          disabled={approveMutation.isPending}
                        >
                          <CheckCircle className="h-4 w-4 mr-1" />
                          Approve
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => rejectMutation.mutate({ id: rule.id, reason: 'Rejected by user' })}
                          disabled={rejectMutation.isPending}
                        >
                          <XCircle className="h-4 w-4 mr-1" />
                          Reject
                        </Button>
                      </>
                    )}
                    {(rule.status === 'active' || rule.status === 'disabled') && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => toggleMutation.mutate({ id: rule.id, active: rule.status !== 'active' })}
                        disabled={toggleMutation.isPending}
                      >
                        {rule.status === 'active' ? (
                          <><ToggleRight className="h-4 w-4 mr-1" />Disable</>
                        ) : (
                          <><ToggleLeft className="h-4 w-4 mr-1" />Enable</>
                        )}
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
