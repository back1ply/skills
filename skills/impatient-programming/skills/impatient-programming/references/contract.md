# The Contract: how to write and keep one

These are this skill's own notes, drawn from several IMP pages (rules 13, 17, 20, 26, 28 and 29, the intro, the FAQ, the "Born at ZAR" case study, and Muhannad Salkini's essay). For the authors' words, follow the links at the bottom.

## What it is

The Contract is the team's written description of what the software must do. It lives in the repository next to the code, it is versioned, and the goal is that a machine can run it. It replaces XP's "system metaphor": the shared mental model that used to live in people's heads now lives in source control, where agents can read it and checks can enforce it.

It is **not** a backlog of user stories and **not** a long planning document. It is a set of **obligations**, meaning invariants the finished code must keep.

## What goes in

- **Functional obligations:** what the component promises its callers. Example: "a Stop from an operator during a reboot wins."
- **Non-functional obligations:** latency, ordering, idempotency, limits, retry behaviour and so on. These are the ones teams usually forget. The intro's example is a component that averages 100 ms with a caller that times out at 150 ms. A "cleaner" refactor that drifts to 140 ms breaks production even though no test fails.
- **The reason for each obligation**, so that a future reader or agent can tell whether it still applies.
- **Declared exceptions.** When something that would normally fail a guardrail is kept on purpose (for example, deliberate duplication that `exhale` would flag), the Contract records it and says why.

## The ZAR shape (one way to lay it out)

The Agora experiments used three artifacts per component:

1. **Intent document:** what the component is for, the invariants it keeps, and why each one exists. Include the *derivation* behind numeric decisions, not just the value, or a regenerating agent will treat the value as arbitrary.
2. **Decision records:** the reasoning behind each design choice, which commit history alone doesn't capture.
3. **Contract spec:** the executable part. Keep only language-neutral promises here. If an assertion would stop holding once someone rewrote the component in a different language or design, it's an implementation detail. Move it to the ordinary test suite.

Salkini's essay adds a fourth artifact worth keeping beside the Contract:

4. **Rejected-approaches log:** short entries for things the team tried and ruled out, which tests can't catch (for example "caching this lookup served stale prices"). Each entry has three parts: what not to do, why, and which paths it covers. A regenerating agent reads the entries for its scope before writing code.

## The lifecycle inside one PR

1. **Before touching existing code**, pin its current behaviour and find out why each guard is there. This is the one step that comes first (rule 20).
2. **Inhale:** while you and your human work out the feature, write each obligation into the Contract as you go.
3. **Exhale:** check the Contract against what was *agreed*, not against what got built. An agent that writes the code and the Contract together tends to describe whatever it built. Look for missing obligations (especially non-functional ones).
4. **Mutation-test** the Contract's tests (rule 26). A test that kills no mutant on its own is removed. Credit each kill to an obligation where tooling allows.
5. **Merge** only when the Contract is met. It is met or not met; it is never a score (rule 29).
6. **Publish contract coverage:** the share of the system the Contract describes. Expect it to be below 100%. The number shows how much is still unwritten.

## When a production bug appears (rule 28)

A bug means a defect in code that is live in production; anything else is a refinement (`refine:`). For a real bug:

1. Roll back or hotfix if users are hurting.
2. Add the missing obligation to the Contract.
3. Make it executable and watch it go **red** against the unchanged code. That red result is the bug report written as a test.
4. Show the new test kills the mutant that matches the bug.
5. Fix the code until it's green. Label the PR `fix:`.

## Regeneration drills (rule 17)

Keeping a component regenerable means that if you deleted it, an agent could rebuild it from the Contract alone. Treat this as a fire drill, not a habit of rewriting:

- Give fresh agents the intent, decision records and Contract spec in an isolated worktree. Keep the old code, its tests and the git history out of reach.
- Have each regenerator log every ambiguity it hit and what it decided. Every judgment call it had to make shows something the intent left unsaid. Write those into the next revision.
- Score each rebuild against the original on behaviour, not on code shape.
- A statement in the intent with no executable example behind it isn't enforced yet. Add the example.
- An old test suite that fails mostly on stubbed private methods or exact wording is testing the old implementation, not its behaviour.

Stephen Margheim's essay pushes back on regenerating often. A working codebase holds fixes no spec captures, and every agent session learns from it. The usual move is to make a better pattern true everywhere at once, not to regenerate.

For a step-by-step deletion test you can run on a real component, see Obie Fernandez's `deletion-test` skill: <https://github.com/obie/skills/tree/main/skills/deletion-test>.

## Tooling

- `covenant` (Elixir) ties contract tests to numbered obligations, fails on any obligation without a passing test, and publishes contract coverage.
- `flinch` (Go) runs mutation testing on Contract-covered code and credits each kill to an obligation.
- For other stacks, see `tools.md` and the live directories at <https://impatientprogramming.org/tools/contract/> and <https://impatientprogramming.org/tools/tests-that-bite/>.

## Sources

- Rule 13, 17, 20, 26, 28, 29: <https://impatientprogramming.org/rules/>
- The Contract, in the intro: <https://impatientprogramming.org/xp-revisited/#the-metaphor-finally-has-a-home>
- Born at ZAR: <https://impatientprogramming.org/case-studies/born-at-zar/>
- Muhannad Salkini, "Rule 17: What the Contract can't hold": <https://impatientprogramming.org/essays/muhannad-salkini-rule-17-what-the-contract-can-t-hold/>
- Stephen Margheim, "Code Is Cheap Now. That's Why It Matters.": <https://impatientprogramming.org/essays/stephen-margheim-code-is-cheap-now/>
- Chad Fowler, "The Deletion Test": <https://chadfowler.com/regenerative-software/3md5ftetaes2e/>
