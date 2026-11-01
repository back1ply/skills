# The 29 rules of Impatient Programming

Source: [The rules that govern how we work](https://impatientprogramming.org/rules/) by Obie Fernandez,
impatientprogramming.org, licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Changes: reformatted from HTML to markdown, one section per rule; "Revisit this rule"
links and images removed. Text otherwise unchanged. Snapshot: 2026-10-27.

Each rule shows the 2026 IMP rule, then Don Wells's 1999 XP rule it revisits.
Anchor links (`https://impatientprogramming.org/rules/#rule-N`) point to the live page.

## Planning

### Rule 1: Get your story straight.

1999: *User stories are written.*  
Link: https://impatientprogramming.org/rules/#rule-1

Before you commit to a project, write down your success criteria for it and post that somewhere that the rest of your team can refer to it. A lot of teams use Linear these days, and it has a native first-class Projects feature that we use at ZAR for this purpose. The point is to understand and document what you're going to build before you commit to delivering it.

That's the only kind of “story” IMP cares about: the account you can give of what you're building and how you'll know it worked.

### Rule 2: Call your shot every week.

1999: *Release planning creates the release schedule.*  
Link: https://impatientprogramming.org/rules/#rule-2

One big project, one demoable vertical slice by Friday.

Long projects climb a hill. Until you reach the top, you're still turning unknowns into knowns, and nobody should pretend to know the date. At the top, whoever committed gives a forecast they believe. That's good management, and it's no deadline.

Ryan Singer's Shape Up gave us the hill.

### Rule 3: Every green merge is a release, ideally.

1999: *Make frequent small releases.*  
Link: https://impatientprogramming.org/rules/#rule-3

Shoot for fully automated and continuous release. Projects with high blast radius components may not fully achieve that goal. Given how the clankers can fix or roll back almost anything almost instantly, the risk of a bad release causing production incidents has never been lower.

Essays [Sebastian Scholl, “Stop Apologizing for Being the Bottleneck”](https://impatientprogramming.org/essays/sebastian-scholl-stop-apologizing-for-being-the-bottleneck/) extends

Tools [Review and merge](https://impatientprogramming.org/tools/review-and-merge/)

### Rule 4: No timeboxes. A weekly showcase is the heartbeat.

1999: *The project is divided into iterations.*  
Link: https://impatientprogramming.org/rules/#rule-4

For eXtreme Programming (XP) purists, the only purpose of an iteration was to track velocity.

Then Scrum came along with its sprints. They let teams expand the work to fit the deadline. We think that's exactly the wrong kind of way to enforce commitments in the age of AI.

IMP has no timeboxed iterations. Work flows pull request by pull request, and every green merge is an increment ([rule 3](https://impatientprogramming.org/rules/#rule-3)). Rework still happens, inside every pull request ([rule 12](https://impatientprogramming.org/rules/#rule-12)). Once a week the whole company holds a showcase, and the rule is presenters can only show something that they've actually finished. Nothing in progress counts, and if it's product, you demo it in production. Each person or team picks one or two bigger things, and small tweaks don't count.

Waterfall worked in phases of months. XP cut that to iterations of weeks. IMP drops the timebox entirely, but keeps a weekly heartbeat in place. Mostly because it's a nice ritual that gives people a chance to show off their best work and receive appreciation for it.

Under no circumstances are bosses allowed to criticize or question decisions made by the team during the showcase.

C. Northcote Parkinson explained why deadlines expand.

### Rule 5: The One Question starts each feature.

1999: *Iteration planning starts each iteration.*  
Link: https://impatientprogramming.org/rules/#rule-5

What do we still need to learn before we can build this?

## Managing

### Rule 6: Work in the open, with your agents.

1999: *Give the team a dedicated open work space.*  
Link: https://impatientprogramming.org/rules/#rule-6

XP gave the team an open workspace. Most teams are remote now, so the open workspace is a shared chat space where people and agents work side by side in public channels.

Ideally, everyone's local Claude Code sessions feed a shared knowledge graph. What's learned by one should be learned by all.

Essays [Matthew Canham, “The Playbook and the Contract”](https://impatientprogramming.org/essays/matthew-canham-the-playbook-and-the-contract/) agrees

Tools [The agent itself](https://impatientprogramming.org/tools/the-agent/)

### Rule 7: Set a sustainable attention budget.

1999: *Set a sustainable pace.*  
Link: https://impatientprogramming.org/rules/#rule-7

Human understanding goes to the new stuff.

### Rule 8: Agents brief the team every day.

1999: *A stand up meeting starts each day.*  
Link: https://impatientprogramming.org/rules/#rule-8

Each morning the team's agents post a brief on what the whole team did, people and agents alike, so the brief covers more than the agents' own work. That's what autonomous agents are for.

### Rule 9: Throughput is measured, and labeled honestly.

1999: *The Project Velocity is measured.*  
Link: https://impatientprogramming.org/rules/#rule-9

When you work with agents you ship in far smaller increments than you used to. That breaks how most teams measure. A dozen small PRs polishing a feature no user has seen yet get counted as a dozen bug fixes, and suddenly the dashboard says quality is collapsing.

In IMP a fix means a defect in code that's live in production. Everything else is refinement, and it gets labeled that way: `refine:`.

On flat-rate plans the bill is fixed, so dollars aren't worth tracking. Plan limits are. Watch how close you run to them, because hitting one stops your agents mid-work.

Essays [Matthew Canham, “The Playbook and the Contract”](https://impatientprogramming.org/essays/matthew-canham-the-playbook-and-the-contract/) pushes back

Tools [Measurement](https://impatientprogramming.org/tools/measurement/)

### Rule 10: Move attention around.

1999: *Move people around.*  
Link: https://impatientprogramming.org/rules/#rule-10

People rotate to the new work, and agents take over the maintenance.

### Rule 11: Fix IMP when it breaks.

1999: *Fix XP when it breaks.*  
Link: https://impatientprogramming.org/rules/#rule-11



## Designing

### Rule 12: Simplicity: breathe in, breathe out.

1999: *Simplicity.*  
Link: https://impatientprogramming.org/rules/#rule-12

Simplicity is where breathing lives. Every pull request breathes. On the inhale, you let the agent sprawl until the universe reveals exactly what your new feature wants to be. On the exhale, you fold what you learned back into *what already exists in the system*, in the same PR.

Agents add complexity by default, and the exhale is where simplicity happens. Technical debt is not tolerated.

**Breathe in.** The agent sprawls until the feature shows what it wants to be.
**Breathe out.** You fold what you learned back into what already exists.
**Merge.** Same pull request, with the Contract underneath the whole time.

Essays [Stephen Margheim, “Code Is Cheap Now. That's Why It Matters.”](https://impatientprogramming.org/essays/stephen-margheim-code-is-cheap-now/) extends

Tools [Breathing out](https://impatientprogramming.org/tools/breathing-out/)

### Rule 13: Write the Contract.

1999: *Choose a system metaphor.*  
Link: https://impatientprogramming.org/rules/#rule-13

System metaphor was the XP practice teams found hardest to apply. The problem is that the metaphor lived in people's heads. Peter Naur saw the same problem in 1985, when he argued that a program's real value is the theory in its programmers' heads.

In IMP the metaphor/mental model gets written down in the source code. We call it the Contract. It's the team's comprehensive description of what the software must do, in a form a team can collaborate on and maintain. More on [the Contract](https://impatientprogramming.org/xp-revisited/#the-metaphor-finally-has-a-home).

Ancestor: Peter Naur, “Programming as Theory Building” (1985).

Tools [The Contract](https://impatientprogramming.org/tools/contract/), [Proof](https://impatientprogramming.org/tools/proof/)

### Rule 14: Use artifacts for design sessions.

1999: *Use CRC cards for design sessions.*  
Link: https://impatientprogramming.org/rules/#rule-14

Now when we start a feature we open an editable artifact and talk through the design and architecture decisions with Claude until we both understand what we're building. We ask for a comp and reject it. We ask for three options. When the picture is clear, then we unleash the agent to do its thing.

The artifact that helped you think becomes the design record.

### Rule 15: Spikes are cheap, so run several in parallel.

1999: *Create spike solutions to reduce risk.*  
Link: https://impatientprogramming.org/rules/#rule-15

A spike was a quick throwaway program written to answer one question, then deleted. We rationed them, because a spike could cost a pair a day or two. Now a spike costs minutes, so imps run several in parallel and let the results argue it out.

Tools [The agent itself](https://impatientprogramming.org/tools/the-agent/)

### Rule 16: Experiment on what to build. Boil the lake on how you build it.

1999: *No functionality is added early.*  
Link: https://impatientprogramming.org/rules/#rule-16

YAGNI still holds for scope. Don't overbuild. Use that nearly unlimited intelligence at your fingertips to learn how to advance your project via the scientific method. Name your hypotheses and your assumptions, run bakeoffs, and experiment like crazy until you figure out exactly the feature that you need.

And once you figure it out? Go all the way. Goldplate it as much as you want! Garry Tan calls it boiling the lake: completeness is so cheap now that taking shortcuts stops making sense. Build it complete and please your customer, but never forget to “breathe out” before you ship that PR so that none of the new stuff turns into technical debt.

Garry Tan boils lakes and oceans. Eric Ries taught a generation to experiment.

Tools [Proof](https://impatientprogramming.org/tools/proof/)

### Rule 17: Keep it regenerable. Regenerate when it's worth it.

1999: *Refactor whenever and wherever possible.*  
Link: https://impatientprogramming.org/rules/#rule-17

Regeneration works like a fire drill. You don't burn the building down to move offices, but you run the drill, because the drill is how you find out everyone can get out.

If you couldn't delete a component and rebuild it from the Contract, the Contract is missing something. Run the drill now and then, and regenerate for real when a better design makes it pay. Entire systems can get regenerated in an afternoon now, so the drill is cheap.

Essays [Muhannad Salkini, “Rule 17: What the Contract can't hold”](https://impatientprogramming.org/essays/muhannad-salkini-rule-17-what-the-contract-can-t-hold/) extends [Stephen Margheim, “Code Is Cheap Now. That's Why It Matters.”](https://impatientprogramming.org/essays/stephen-margheim-code-is-cheap-now/) pushes back

## Coding

### Rule 18: Put the solution in front of the customer, and stop guessing what they want.

1999: *The customer is always available.*  
Link: https://impatientprogramming.org/rules/#rule-18

XP put the customer in the room. Now a spike is one of the first things you do, and it goes straight in front of the customer. Throwaway prototypes, trial balloons, five versions of a screen before lunch. Experiments cost almost nothing, so nobody has to guess what the customer wants anymore.

Sometimes the customer builds the prototype. At ZAR the whole company is expected to code, not just the engineers. Our CEO isn't a programmer, and some of our best systems started as prototypes he built himself.

Tools [What users see](https://impatientprogramming.org/tools/what-users-see/)

### Rule 19: Standards are enforced by machines.

1999: *Code must be written to agreed standards.*  
Link: https://impatientprogramming.org/rules/#rule-19

Convention over configuration. The rules run in machines: mutation gates, executable contracts, merge checks, guardrails on every change.

Essays [Stephen Margheim, “Code Is Cheap Now. That's Why It Matters.”](https://impatientprogramming.org/essays/stephen-margheim-code-is-cheap-now/) extends

Tools [Structure](https://impatientprogramming.org/tools/structure/), [Standards](https://impatientprogramming.org/tools/standards/)

### Rule 20: Agree on the Contract, and make it executable.

1999: *Code the unit test first.*  
Link: https://impatientprogramming.org/rules/#rule-20

Throughout the inhale you and the agent work out what the feature must do, and the agent writes each obligation into the Contract as it goes. Those are the *invariants* the result must adhere to when it is finished, functional and non-functional. Making sure the Contract is complete is part of the exhale ([rule 12](https://impatientprogramming.org/rules/#rule-12)).

An agent that writes the Contract while it writes the code can end up describing whatever it built. So on the exhale you check the Contract against what you agreed, and the kill matrix ([rule 26](https://impatientprogramming.org/rules/#rule-26)) catches tests that pass no matter what the code does.

One thing does come first. When you're changing existing code, pin the behavior it already has before the agent touches it, and find out why each fence is there before you move it.

The most impish thing you can do is to make the Contract executable, and that's one of the greenest green fields that exists in October 2026.

Essays [Matthew Canham, “The Playbook and the Contract”](https://impatientprogramming.org/essays/matthew-canham-the-playbook-and-the-contract/) extends

Tools [The Contract](https://impatientprogramming.org/tools/contract/), [Generated inputs](https://impatientprogramming.org/tools/generated-inputs/), [Tests that bite](https://impatientprogramming.org/tools/tests-that-bite/)

### Rule 21: All production code is pair programmed, with an Agent.

1999: *All production code is pair programmed.*  
Link: https://impatientprogramming.org/rules/#rule-21

XP asked people to pair on all production code. Thoughtworks, Pivotal Labs, Hashrocket. We did it with a vengeance, and it was exhausting. But it never took off hardly anywhere else because it cost two salaries for one keyboard, which is something that the people controlling the purse strings just could not get through their fat skulls as an improvement.

Today everyone pairs with Claude Code (or a similar coding agent) all day, every day.

Essays [Mark Ryall, “Keep pairing with humans”](https://impatientprogramming.org/essays/mark-ryall-keep-pairing-with-humans/) pushes back

Tools [The agent itself](https://impatientprogramming.org/tools/the-agent/)

### Rule 22: Retired.

1999: *Only one pair integrates code at a time.*  
Link: https://impatientprogramming.org/rules/#rule-22

Machines took this one over. Merge queues and CI serialize integration, so nobody takes turns anymore. IMP says so out loud and doesn't keep the rule out of nostalgia.

### Rule 23: Integrate continuously.

1999: *Integrate often.*  
Link: https://impatientprogramming.org/rules/#rule-23

Long-lived branches hurt your teammates, and when agents are writing code all day, a branch goes stale in hours.

Tools [Review and merge](https://impatientprogramming.org/tools/review-and-merge/)

### Rule 24: Guardrails fire on every change.

1999: *Set up a dedicated integration computer.*  
Link: https://impatientprogramming.org/rules/#rule-24

A guardrail is software, and building one is programming. Think of bowling with kids, when you put the bumpers up so the ball reaches the pins. The pins are business value. The ball is whatever your coding agent does when you give it a prompt.

Bumpers up. They keep the ball out of the gutter on its way to the pins.

Tools [Safety](https://impatientprogramming.org/tools/safety/), [What users see](https://impatientprogramming.org/tools/what-users-see/)

### Rule 25: Collective ownership, agents included.

1999: *Use collective ownership.*  
Link: https://impatientprogramming.org/rules/#rule-25

In the most extreme implementations of IMP, we completely hand over ownership of maintenance work to autonomous agents.

## Testing

### Rule 26: Every test must prove it's worth keeping.

1999: *All code must have unit tests.*  
Link: https://impatientprogramming.org/rules/#rule-26

Not all code needs unit tests, because every test (unit or otherwise) has to prove that it's worth keeping and burning CPU cycles on. Agents will happily write thousands of automated tests along with your code.

Imps run all automated tests through a *kill matrix* using mutation testing, and keep a test only if it catches something no other test catches.

A kill matrix. Each column is the code broken on purpose in one small way, and a dot means that test catches it. Take away tests 3 and 5 and every mutant shown is still caught.

Tools [Tests that bite](https://impatientprogramming.org/tools/tests-that-bite/)

### Rule 27: Green merges itself.

1999: *All code must pass all unit tests before it can be released.*  
Link: https://impatientprogramming.org/rules/#rule-27

Our long-term goal is to get rid of human code review altogether. The blast radius of your PR is how you decide how aggressive to get with that goal today. As much as possible should ship, land and deploy based on automated checks and adversarial model review. Save human eyes for reviews guarding against catastrophic risks.

Claude can set up canary deployments for you without breaking a sweat. It can also hotfix or rollback almost any bad release almost instantly. IMP embraces the fact that the risks of continual deployment have never been lower.

Essays [Muhannad Salkini, “Rule 17: What the Contract can't hold”](https://impatientprogramming.org/essays/muhannad-salkini-rule-17-what-the-contract-can-t-hold/) extends [Sebastian Scholl, “Stop Apologizing for Being the Bottleneck”](https://impatientprogramming.org/essays/sebastian-scholl-stop-apologizing-for-being-the-bottleneck/) extends [Matthew Canham, “The Playbook and the Contract”](https://impatientprogramming.org/essays/matthew-canham-the-playbook-and-the-contract/) pushes back

Tools [Review and merge](https://impatientprogramming.org/tools/review-and-merge/)

### Rule 28: When a bug is found, the Contract was missing something.

1999: *When a bug is found tests are created.*  
Link: https://impatientprogramming.org/rules/#rule-28

A bug is a defect in code that's live in production ([rule 9](https://impatientprogramming.org/rules/#rule-9)). Everything else is refinement.

Add the missing obligation to the Contract first, make it executable ([rule 20](https://impatientprogramming.org/rules/#rule-20)), and prove the new test kills the mutant that matches the bug ([rule 26](https://impatientprogramming.org/rules/#rule-26)). Then fix the code. Every bug leaves the Contract stronger.

Tools [Generated inputs](https://impatientprogramming.org/tools/generated-inputs/)

### Rule 29: The Contract must be met, and contract coverage is published.

1999: *Acceptance tests are run often and the score is published.*  
Link: https://impatientprogramming.org/rules/#rule-29

Acceptance tests are the Contract, and the Contract isn't scored: it's either met or it isn't. What gets published is how much of the system the Contract covers.

Reaching 100% contract coverage is very hard, so the number tells everyone how much of the system is still unwritten.

Tools [The Contract](https://impatientprogramming.org/tools/contract/)
