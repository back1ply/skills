# Go-Live & Operations

## Contents

- Getting Buy-In
- Common Data Problems and Solutions
- SMED — Cycle Time Reduction
- FMEA — Risk Management
- Data Collection Methods
- Process Mapping KPI Production
- Preflight Checks Before Launch
- Handover to BAU Team
- Sustaining KPIs

## Getting Buy-In

### Five Stages of Buy-In

**Stage 1 — Create Engagement**

- [ ] Involve a wide selection of stakeholders in the KPI Tree session (most effective technique)
- [ ] Go through reasons behind new measures clearly and simply with those providing data or being measured
- [ ] Hold an event or series of one-to-ones for frank discussion of concerns
- [ ] Deal with potential issues openly and honestly
- [ ] Create a "frequently asked questions" document

**Stage 2 — Build a Case**

- [ ] Show a real-world benefit from collecting the data (or a significant problem if you don't)
- [ ] Give relevant and compelling real-life examples
- [ ] Explain how you'll manage the extra workload from data collection

Rational argument alone won't build engagement. Engagement is essentially an emotional process. A frequent mistake: reacting to lack of engagement by strengthening the rational argument — this can be counter-productive.

**Stage 3 — Remove Obstructions**

Make it easy to comply:
- [ ] Create a user guide for each type of user
- [ ] Clearly define the process to follow
- [ ] Test the process with all individuals who will follow it
- [ ] Step-by-step instructions, decision branches, screen grabs
- [ ] Identify additional required skills and where to acquire them
- [ ] Contact details for additional help (phone number ideal)
- [ ] Make user guides readily available and easy to use
- [ ] Laminated, colour, A3 user guides work brilliantly
- [ ] Version-control guides and keep fully up to date
- [ ] Action feedback as quickly as possible

**Critical**: Make sure line managers of key data gatherers are fully engaged. Any dissent, however subtle, will destroy data collection efforts. Never bypass middle managers.

**Stage 4 — Public Displays of Importance**

- [ ] Have full and frank discussions with senior managers at the start
- [ ] Document what you're trying to achieve and get physical sign-off
- [ ] Get senior stakeholders to write a briefing document (or write one for them to sign)
- [ ] Senior stakeholders should kick off any roadshows or briefings explaining: why important, what happens if it fails, their interest, when follow-up is, what they expect, their confidence
- [ ] Let people know there's an open door for practical problems
- [ ] Ensure everything said in public and private is aligned
- [ ] Address off-the-record whispers that aren't aligned — seriously and early
- [ ] Schedule regular review/steering sessions

**Stage 5 — Develop Good Habits**

- [ ] Minimise process variation between repetitions
- [ ] Ensure a predictable "heartbeat" frequency
- [ ] Tackle falling out of habit quickly
- [ ] Fix problems that stop people fast
- [ ] Reinforce good work with positive feedback
- [ ] Track errors and omissions on a visual management chart

Things to avoid:
- [ ] Changing the process frequently or unnecessarily
- [ ] Changing layout/position of user interfaces and forms
- [ ] Making the process complex or cumbersome
- [ ] Allowing "grey" exceptions without clear guidance

---

## Common Data Problems and Solutions

### Problem 1 — Data Living in Islands

Small islands in spreadsheets, Word documents, and ad hoc databases.

**Solution**:
- Develop a clear definition of which unique KPIs you need
- Create a production process map for each measure
- Create a data location table:

| Data | Use | Storage Method | Location | Source or Duplicate? | Owner | Contact |
|------|-----|----------------|----------|----------------------|-------|---------|
| ... | ... | ... | ... | ... | ... | ... |

For each item answer:
- Is this the right place to store this information?
- Is the collection method clearly defined and effective?
- Is there a better method for moving information from storage to point of use?

### Problem 2 — Contradictory Datasets

Same-sounding measures giving different numbers. Shakes faith in the system and lets people reject data they don't like.

- [ ] Create a KPI definition sheet for each measure
- [ ] Track, record, and investigate incidents of contradictory values
- [ ] If structural issues exist, be open and develop a plan for underlying fixes

### Problem 3 — Data in Different Forms

Different time spans, geographic areas, or business units making consolidation impossible.

Solutions (in order of cost/complexity):
1. **Excel "fudge"** — Most common. Requires real discipline and good manual systems.
2. **Data marts** — Databases that aggregate with more structure than Excel.
3. **Third-party connection tools** — Connect directly to source data across multiple sources.
4. **Fundamental IT solution** — Expensive, risky, time-consuming.

For Excel solutions, ensure:
- [ ] Central document showing definitive data sources
- [ ] Change log for all business-critical spreadsheets
- [ ] Locked-down spreadsheets with controlled write permissions
- [ ] Detailed process maps kept up to date by named individuals
- [ ] Sign-off process for critical calculations

### Problem 4 — Lack of Trust

Start with "Why are you collecting it?" If the need melts away, stop. If it's important, repair trust:

- [ ] Understand precisely what data is used and for what purpose
- [ ] Survey key stakeholders to identify specific concerns
- [ ] Shortlist high-priority data
- [ ] Investigate specific elements of high-priority data in detail
- [ ] If no issues, broaden the analysis
- [ ] If issues found, develop remediation plan
- [ ] Implement remediation action plan
- [ ] Put controls in place to stay on track

### Problem 5 — Collection Delays

The slowest data delivery determines final production date.

- [ ] Develop a publication timetable with clear deadlines (realistic, with contingency)
- [ ] Process map the reporting "supply chain"
- [ ] Apply SMED to reduce cycle time (requires process mapping first)

---

## SMED — Cycle Time Reduction

### What Is SMED?

Single Minute Exchange of Dies — the technique enabling F1 teams to change tyres in 2.31 seconds. Developed by Shigeo Shingo for Toyota. Applied to KPI production, it reduces report cycle time.

### Observe the Process

- [ ] Observe (or video) the process
- [ ] Note duration of major activities and their sequence/dependencies
- [ ] Identify whether activities are **internal** (must stop the process) or **external** (can be done without holding up production)
- [ ] Draw a Gantt chart showing internal and external operations

### Identify Internal Activities

- [ ] What data can you check/validate offline before report production?
- [ ] What data/extracts must be delivered before the process can run?
- [ ] How could production and supply be streamlined?
- [ ] What condition does the process need to be in? Can people/IT be prepared in advance?
- [ ] What adjustments happen during production?
- [ ] Which would benefit from standardisation (pre-written queries, macros, batch jobs)?
- [ ] What makes the operator hunt for data or commentary? How to make it easily to hand?
- [ ] When do you perform complex/fiddly tasks relying on memory?
- [ ] Can you use code/macros/scripts to automate manipulation? Could manipulation be avoided with redesign?
- [ ] Can testing/checking be improved?
- [ ] Can you learn from previous mistakes?
- [ ] What's the most rational testing regime: 100% inspection or statistical sampling?

### Remove or Reduce Internal Operations

- [ ] Group internal activities together to minimise pause time
- [ ] Convert internal to external (e.g., run a query on a spare PC in advance)
- [ ] Reduce complexity of compulsory internal operations

### External Activities

- [ ] Verify external operations are truly external
- [ ] Reduce time on external activities to reduce total effort

---

## FMEA — Risk Management

### Failure Mode and Effects Analysis

Score each risk:

```
FMEA Score = Probability (1-10) × Severity (1-10)
```

With optional detectability: `Score = Probability × Severity × Detectability`

### FMEA Checklist

- [ ] Go through your system asking "What happens if this fails?"
- [ ] Document consequential events
- [ ] Assign probability score (1-10)
- [ ] Assign severity score (1-10)
- [ ] Calculate FMEA score
- [ ] Identify high-scoring risks for mitigating actions
- [ ] Calibrate your scales with specific examples at 1, 5, and 10

### FMEA Matrix Template

| Failure | Mode | Effect | Probability | Severity | Score | Mitigation |
|---------|------|--------|-------------|----------|-------|------------|
| Missing data | Sheets not completed | Incomplete data | 9 | 7 | 63 | Implement tracking log |
| Missing data | Sheets not returned | Incomplete data | 6 | 7 | 42 | Document process, backup collectors |
| Missing data | Run out of capture sheets | Incomplete data | 8 | 9 | 72 | Sheet kanban — restock on low levels |
| Missing data | Staff not aware | Incomplete data | 8 | 5 | 40 | Add to induction training |

After mitigations, rescore to show improvement.

---

## Data Collection Methods

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Excel** | Quick setup, familiar, flexible, easy import/export | Mixes source with analysis, unstable with links, complexity piles up | Short-medium term, most common |
| **SharePoint** | Proper database, handles multi-user edits, easy surveys | Needs technical setup, limited form customisation (pre-2010) | Team data sharing, survey collection |
| **Paper** | Instant deploy, everyone can use it, shows human interest | Requires re-keying, physical collection, forms run out | Very short-term prototypes only |
| **Customised existing system** | Consistent UI, can capture system data automatically | Budget/scope creep, slow, requires IT vendor support | Last mile replacement of clunky systems |
| **ERP/CRM extraction** | Invisible to end-user, can be fully automated | Problematic if supplemental data needed, restricted DB access | When all data already collected |
| **Third-party capture** | Tuned to specific needs, robust DB back-end | Requires configuration, vendor support, budget | Well-defined PC-based processes |

### Data Collection Checklist

- [ ] Is the data source defined by role (not just a person's name)?
- [ ] Is data collection a reasonable task? How long does it take? Does the person agree?
- [ ] Is there a check for timely submission and follow-up for missing/incorrect data?
- [ ] Do you have a KPI definition for the data being collected?
- [ ] Does the person understand precisely what is required and when?
- [ ] Is there a contingency plan for sickness/holiday?
- [ ] Is there a backup plan for historic KPI data?
- [ ] Does data collection have a very senior sponsor?

---

## Process Mapping KPI Production

### Why Map?

- Complete end-to-end overview (often for the first time)
- Engages process owners in dialogue
- Enables improvement and simplification
- Foundation for lead-time reduction, skills management, and audits

### Process Mapping Checklist

- [ ] Decide which tool to use (Visio, PowerPoint, Aris, etc.)
- [ ] Train or requisition process mapping resource
- [ ] Find online or physical repository for maps that users can access
- [ ] Agree conventions for process mapping
- [ ] Create version control and revision numbering
- [ ] Agree footer content
- [ ] Decide on contact details (phone best, then email)
- [ ] Identify stakeholders using RACI (Operations, Risk, Regulatory, Data Security, Privacy, Quality)

### Process Mapping Levels

Separate into levels to keep things manageable:
- **High level**: "Use the bathroom"
- **Medium detail**: "Have a shower", "Clean teeth", "Wash face"
- **Detailed**: "Squeeze toothpaste onto toothbrush", "Clean specific mouth areas", "Rinse"

Create specific examples for your organisation to illustrate each level. Appoint one final arbiter for consistency.

---

## Preflight Checks Before Launch

- [ ] Introduce "source sign-off" process for externally sourced data
- [ ] Publish KPI definitions with the report
- [ ] Publish known issues and remediation actions
- [ ] Test data on a small friendly audience first
- [ ] Add caveats explaining expected first-pass issues
- [ ] Walk key stakeholders through the report privately before any public forum
- [ ] Get explicit confirmation of comfort from key stakeholders

---

## Handover to BAU Team

- [ ] Full definition of each KPI (documented on paper and/or database)
- [ ] Process map(s) for each measure's production process
- [ ] User guides for each individual producing a measure
- [ ] SLA document written for humans, with rationale (plus summary if complex)
- [ ] Templates, spreadsheets for producing output
- [ ] Action log showing what happened and outstanding items
- [ ] Every action has "who", "when", "how", and "what"
- [ ] Contact list for each key person in production
- [ ] Book a follow-up session to confirm smooth handover

---

## Sustaining KPIs

### What Kills Established Systems

| Issue | Prevention |
|-------|------------|
| Rapid strategy change | Every strategy review includes a formal KPI review |
| Unexpected disasters | Set a "wake up" date for dormant measures and meetings |
| Loss of senior sponsor | Spread senior ownership across multiple sponsors |
| "Flat earthers" | Make "gut instinct only" culturally unacceptable, like ignoring H&S |
| Loss of key specialists | Use Skills Matrix to identify single-person dependencies early |
| Mistrust of output | SLA and process for dealing with accuracy issues |
| Entropy | Allocate dedicated resource to maintenance (may not be full time, but must have accountability) |

### Reverse Brainstorming

Run a session with key stakeholders:
1. Get them to identify likely issues (people are more comfortable thinking about what goes wrong)
2. "Flip" each negative into positive preventive actions
3. Automatic buy-in — they came up with it themselves

### The Right Mindset

- Persistent constructive scepticism
- A bias towards simplicity
- Desire for structure and order
- Constant mindfulness of organisational objectives
- Always remembering your end customer is a human being
