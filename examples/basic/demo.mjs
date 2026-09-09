import { makeCommand, evaluate, rceProtection, ssrfProtection } from '../../packages/agentproof_sdk_node/src/index.js';

const cases = [
  makeCommand({ agent_id: 'demo-agent', tool: 'search_web', params: { query: 'weather in Tokyo' } }),
  makeCommand({ agent_id: 'demo-agent', tool: 'shell_exec', params: { command: 'rm -rf /' } }),
];

for (const command of cases) {
  console.log(JSON.stringify({ command, ...evaluate(command, [rceProtection, ssrfProtection]) }, null, 2));
}
