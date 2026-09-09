import crypto from 'node:crypto';

export function canonicalJson(value) {
  const sort = (v) => {
    if (Array.isArray(v)) return v.map(sort);
    if (v && typeof v === 'object') return Object.fromEntries(Object.keys(v).sort().map(k => [k, sort(v[k])]));
    return v;
  };
  return JSON.stringify(sort(value));
}

export function sha256(value, truncate = null) {
  const hex = crypto.createHash('sha256').update(canonicalJson(value)).digest('hex');
  return truncate ? hex.slice(0, truncate) : hex;
}

export function makeCommand({ agent_id, tool, params = {}, timestamp = Date.now() / 1000, trace_id = crypto.createHash('sha256').update(`${process.hrtime.bigint()}`).digest('hex').slice(0, 16) }) {
  if (!agent_id || !tool) throw new Error('agent_id and tool are required');
  return { agent_id, tool, params, timestamp, trace_id };
}

export function evaluate(command, rules = []) {
  const results = rules.map(rule => rule(command));
  const verdict = results.some(r => r.verdict === 'deny') ? 'deny' : results.some(r => r.verdict === 'escalate') ? 'escalate' : 'allow';
  return { verdict, rule_results: results };
}

export function rceProtection(command) {
  const text = JSON.stringify(command.params);
  const hit = /\brm\s+-rf\b|\bcurl\b.+\|\s*(bash|sh)|\beval\s*\(/i.test(text);
  return { rule_name: 'rce_protection', verdict: hit ? 'deny' : 'allow', reason: hit ? 'rce_pattern_detected' : '' };
}

export function ssrfProtection(command) {
  const text = JSON.stringify(command.params).toLowerCase();
  const hit = ['127.0.0.1', 'localhost', '169.254.169.254', '0.0.0.0'].some(x => text.includes(x));
  return { rule_name: 'ssrf_protection', verdict: hit ? 'deny' : 'allow', reason: hit ? 'ssrf_private_target_detected' : '' };
}
