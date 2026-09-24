/** Codex SDK bridge: cached ChatGPT login only, one independent thread per call. */
import { Codex } from '@openai/codex-sdk';
import { readFile, writeFile, appendFile } from 'node:fs/promises';
let input = '';
for await (const chunk of process.stdin) input += chunk;
const req = JSON.parse(input);
const env = Object.fromEntries(Object.entries(process.env).filter(([key]) =>
  !/^(OPENAI_API_KEY|CODEX_API_KEY|OPENAI_BASE_URL)$/.test(key)));
const codex = new Codex({ env, config: {
  service_tier: 'fast', forced_login_method: 'chatgpt',
  features: { hooks: false },
} });
const thread = codex.startThread({
  model: 'gpt-6-astra', modelReasoningEffort: req.effort ?? 'high',
  sandboxMode: req.sandbox ?? 'read-only', approvalPolicy: 'never',
  workingDirectory: req.cwd, skipGitRepoCheck: true,
  webSearchMode: req.search ? 'live' : 'disabled', networkAccessEnabled: false,
});
try {
  const { events } = await thread.runStreamed([
    {type: 'text', text: req.prompt},
    ...(req.images ?? []).map(path => ({type: 'local_image', path})),
  ], {outputSchema: req.schema, signal: AbortSignal.timeout(req.timeoutMs ?? 1800000)});
  let final = '', completed = false;
  for await (const event of events) {
    await appendFile(req.trace, JSON.stringify(event) + '\n');
    if (event.type === 'item.completed' && event.item.type === 'agent_message') final = event.item.text;
    if (event.type === 'item.completed' && ['command_execution','web_search','mcp_tool_call'].includes(event.item.type))
      process.stderr.write(`tool: ${event.item.type}\n`);
    if (event.type === 'turn.completed') completed = true;
    if (event.type === 'turn.failed') throw new Error(event.error.message);
    if (event.type === 'error') throw new Error(event.message);
  }
  if (!completed || !final) throw new Error('Codex did not complete with a final result');
  JSON.parse(final);
  await writeFile(req.output, final, 'utf8');
  process.stdout.write(JSON.stringify({thread_id:thread.id, output:req.output}));
} catch (error) {
  process.stderr.write(String(error.message) + '\n');
  process.exitCode = 1;
}
