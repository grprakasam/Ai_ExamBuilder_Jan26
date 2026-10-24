import { useState } from 'react';
import api from '../services/api';

export default function Learning() {
  const [testId, setTestId] = useState('');
  const [code, setCode] = useState('');
  const [summary, setSummary] = useState<Record<string, number> | null>(null);
  const [due, setDue] = useState<Array<{concept_id: string; next_review_due: string}>>([]);
  const [error, setError] = useState('');
  const load = async () => {
    try {
      setError('');
      sessionStorage.setItem('exam-access:' + testId, code);
      const [s, d] = await Promise.all([
        api.get('/learning/mastery/summary/' + testId),
        api.get('/learning/mastery/due-for-review/' + testId)
      ]);
      setSummary(s.data); setDue(d.data.concepts_due);
    } catch { setError('Check the test ID and access code.'); }
  };
  return <section className="max-w-2xl mx-auto space-y-4">
    <h1 className="text-2xl font-bold">Learning progress</h1>
    <p>Review mastery and scheduled practice from your recorded answers in this browser session.</p>
    <label className="block">Test ID<input className="block border p-2 w-full" value={testId} onChange={e => setTestId(e.target.value.trim())}/></label>
    <label className="block">Access code<input className="block border p-2 w-full" value={code} onChange={e => setCode(e.target.value)}/></label>
    <button className="bg-indigo-600 text-white p-3 rounded" onClick={load}>Load progress</button>
    {error && <p role="alert">{error}</p>}
    {summary && <p>Mastered: {summary.mastered} of {summary.total_concepts} concepts. Overall mastery: {Math.round(summary.overall_mastery * 100)}%.</p>}
    <h2 className="font-bold">Due for review</h2>
    {due.length ? due.map(d => <p key={d.concept_id}>{d.concept_id} — {new Date(d.next_review_due).toLocaleDateString()}</p>) : <p>No reviews due yet.</p>}
  </section>;
}
