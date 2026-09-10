# Global working agreements

## Delegate execution to Luna; retain primary decision ownership

This policy applies to the primary agent. A sub-agent should complete its assigned scope without recursively delegating unless the primary explicitly requests it.

- For every non-trivial task with a useful independent workstream, use sub-agents with model `gpt-5.6-luna`. After the minimum orientation needed to define scope and read applicable instructions, delegate before undertaking deep investigation or substantial implementation yourself.
- The primary owns scope, priorities, architecture, tradeoffs, ambiguity resolution, integration, and final review. Delegate bounded research, code inspection, implementation within agreed boundaries, focused verification, and documentation to Luna. While Luna works, advance a complementary decision or independent workstream rather than duplicating its assignment.
- Give each worker the objective, relevant context and files, permitted edit scope, constraints, expected deliverable, and acceptance criteria. Use the native tool's supported explicit model selection; supply self-contained context when selecting Luna requires a fresh context.
- Assign disjoint edit ownership. Prefer reusing a suitable existing Luna worker over spawning another. Do not ask workers to recursively create more workers by default.
- Inspect returned evidence and relevant changes, resolve conflicts, and perform the focused validation needed for integration. The primary remains accountable for correctness and completion; a worker's success report alone is not verification.
- Skip delegation only when the user requests solo work. Being capable of doing the task yourself is not an exception.
- If Luna's task fails, based on the actual failure details, please select the appropriate action from the following options.
  1. Retry after fixing the issue
  2. Retry with a higher-tier model (`gpt-5.6-sol`)
  3. Report the task failure to the user
- Before finalizing a non-trivial task, check that meaningful work was delegated and its result reviewed. Briefly identify Luna's contribution, or the concrete reason delegation was not possible. Never claim delegation without an actual native tool call.

## JavaScript and TypeScript tooling

- Use Bun instead of npm/npx for package management and script execution: `bun install`, `bun add`, `bun run`, and `bunx`.
- Respect explicit project-specific tooling requirements. Do not migrate lockfiles or change a project's runtime solely to apply this global preference.

## Python tooling

- Use uv to run Python and manage its environments and dependencies. Use `uv run python ...` instead of invoking `python` or `python3` directly, and use `uv add` / `uv sync` for project dependencies.
- For standalone scripts outside a Python project, use `uv run --no-project python ...`; use `uv run --with <package> python ...` for temporary dependencies and `uvx <tool>` for isolated Python CLI tools.
- Preserve existing project configuration unless migration is requested. uv manages the Python interpreter; it is not itself a replacement interpreter.

## Sub-agent wait duration

- Every time you call `wait_agent`, explicitly set `timeout_ms` to twice the estimated remaining time until the awaited result, expressed in milliseconds.
- Keep the value within the active tool's minimum and maximum. If the remaining time cannot be estimated, explicitly use the configured default (120000 ms in this setup), bounded by the active tool limits.
- Notifications can end the wait early. Do not shorten the timeout just to check status or issue a routine progress update. After a timeout, update the estimate and use the same rule again; a timeout alone is not evidence that a worker is stuck.
- Decide whether independent work remains before choosing to wait. Once waiting is appropriate, apply this duration rule consistently.
