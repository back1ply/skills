# Detailed Prompting Techniques

Extended examples and tips for each of the 11 foundational techniques.

---

## Contents

- 1\. Zero-Shot Prompting
- 2\. Few-Shot Prompting
- 3\. System Prompting
- 4\. Role Prompting
- 5\. Contextual Prompting
- 6\. Step-Back Prompting
- 7\. Chain-of-Thought (CoT)
- 8\. Self-Consistency
- 9\. Tree of Thoughts (ToT)
- 10\. ReAct (Reason + Act)
- 11\. Automatic Prompt Engineering (APE)

## 1. Zero-Shot Prompting

Single instruction, no examples.

### Zero-Shot Examples

- "Summarize the following transcript into a one-paragraph executive briefing suitable for a board meeting."
- "Generate 3 headline options for a homepage that emphasizes speed, simplicity, and trust."
- "Extract and rank the top 3 objections raised in this sales call transcript."

### Zero-Shot Tips by Level

- **Beginner:** Use action verbs: Summarize, List, Write. Avoid vague words like "help" or "explain"
- **Intermediate:** Add format instruction: "in 3 bullet points" or "as a table"
- **Advanced:** Combine directives: "Summarize in 3 bullets, each under 10 words, focusing on customer pain points"

---

## 2. Few-Shot Prompting

Provide examples to guide the model.

### Few-Shot Examples

- "Example: I want a large pizza with mushrooms. JSON: {\"size\": \"large\", \"toppings\": [\"mushrooms\"]}. Now convert: I'd like a small pizza with olives."
- "Here's an ideal changelog entry: [example]. Write one for the feature update below."
- "Here are two support responses that defuse frustration with empathy. Write a third using the same tone."

### Few-Shot Tips by Level

- **Beginner:** Copy structure of one example, change inputs
- **Intermediate:** Provide range of examples (short/long, formal/casual)
- **Advanced:** Use contrasting examples to teach distinctions and edge cases

---

## 3. System Prompting

Set rules for model behavior.

### System Prompt Examples

- "Always answer using the STAR method. Respond only in bullet points."
- "Only use language a 10th-grade reader can understand. Avoid acronyms."
- "Provide answers in Markdown with headings, subheadings, and bolded key terms."
- "Every response: short summary first, then full explanation."

### System Prompt Tips by Level

- **Beginner:** Simple rules: "Respond in a friendly tone" or "Answer in bullet points"
- **Intermediate:** Layer constraints: tone + format + audience in one system prompt
- **Advanced:** Enforce behavior across multiple turns (always speak as mentor, always return Markdown)

---

## 4. Role Prompting

Assign a persona or expertise.

### Role Prompt Examples

- "You are a financial advisor. Recommend three strategies for someone with $10,000 to invest over 5 years."
- "You are a senior PMM at a B2B SaaS company. Write a 3-sentence value proposition."
- "You are a customer success manager. Draft a proactive check-in email for a client showing churn signals."

### Role Prompt Tips by Level

- **Beginner:** Start with "You are a..." + familiar job title
- **Intermediate:** Use domain-specific roles to shape tone and accuracy
- **Advanced:** Combine role + context + format for nuanced control

---

## 5. Contextual Prompting

Provide background, data, or scenario.

### Contextual Examples

- "Using the customer persona and product description below, write a 2-sentence ad hook."
- "Here's our brand tone guidelines. Rewrite this help center article to match."
- "Given our revenue goals and Q3 priorities, generate 3 OKR options for sales enablement."

### Contextual Tips by Level

- **Beginner:** Copy/paste relevant doc before the prompt
- **Intermediate:** Use summaries instead of raw data when input is long
- **Advanced:** Chain multiple inputs and explicitly state how they relate

---

## 6. Step-Back Prompting

Solve general question first, then apply to specific task.

### Step-Back Examples

- "Before writing the email, list 3 things the recipient likely values. Then write the email using that context."
- "First, outline characteristics of high-performing onboarding flows. Then critique this one."
- "Start by identifying the key emotion this campaign should trigger. Then write a subject line."

### Step-Back Tips by Level

- **Beginner:** Ask warm-up question before real task
- **Intermediate:** Use to deconstruct complex decisions (goals → actions → message)
- **Advanced:** Generate principles first, then apply them to the task

---

## 7. Chain-of-Thought (CoT)

Show reasoning step by step.

### CoT Examples

- "Walk through the steps to calculate CAC using this data. Then provide the result."
- "Given this list of product issues, identify which could cause the highest NPS drop. Explain your reasoning."
- "Break down the decision process for renewing vs sunsetting this feature. Include cost, usage, feedback."

### CoT Tips by Level

- **Beginner:** Add "Explain your reasoning" or "Think step by step"
- **Intermediate:** Ask for pros/cons, compare options, walk through logic
- **Advanced:** Combine with structured outputs (tables, multi-step formulas)

---

## 8. Self-Consistency

Run same prompt multiple times, choose most consistent result.

### Self-Consistency Examples

- "Classify this review as positive/neutral/negative five times. Return most frequent label with reasoning."
- "Generate three explanations for this churn event. Summarize the most consistent one."
- "Answer this question three times. Decide which version best aligns with user intent."

### Self-Consistency Tips by Level

- **Beginner:** Run prompt a few times, compare results manually
- **Intermediate:** Ask model to repeat 3-5 times, select most common answer
- **Advanced:** Generate multiple answers, evaluate for consistency, select best

**Note:** Requires temperature > 0 for variability.

---

## 9. Tree of Thoughts (ToT)

Explore multiple reasoning paths.

### ToT Examples

- "Explore three GTM strategies for Q4 launch. Evaluate tradeoffs and recommend one."
- "Generate 3 frameworks for organizing this knowledge base. Justify each, select most scalable."
- "Imagine three customer objections during onboarding. Propose mitigation for each."

### ToT Tips by Level

- **Beginner:** Ask for "3 different ideas" before choosing one
- **Intermediate:** Prompt for options, then evaluate for clarity/impact/feasibility
- **Advanced:** Use ToT as decision engine: branch paths, evaluate tradeoffs, synthesize

---

## 10. ReAct (Reason + Act)

Model reasons then performs actions (search, tools).

### ReAct Examples

- "Search how many children each Metallica member has. Sum total. Output only the final number."
- "Search for this company's latest funding round. Write a congratulatory email referencing it."
- "Use code interpreter to calculate monthly burn rate from this spreadsheet. Write plain-English summary."

### ReAct Tips by Level

- **Beginner:** Use "Search" or "Calculate" tools, manually combine with AI output
- **Intermediate:** Prompts like "Search for X, then summarize in 2 lines"
- **Advanced:** Combine tool use + reasoning + generation in one loop

---

## 11. Automatic Prompt Engineering (APE)

Use AI to generate and test prompt variations.

### APE Examples

- "Write 10 alternate prompts for summarizing technical articles. Pick the clearest one."
- "Generate 5 prompt variations for reframing negative self-talk. Rank most to least supportive."
- "Create 7 prompts asking users to describe product feedback. Tag each by tone."

### APE Tips by Level

- **Beginner:** Ask model to rewrite your prompt in 3 clearer variations
- **Intermediate:** Generate 5-10 versions with different tones/formats, test across tasks
- **Advanced:** Use frameworks like PromptLayer, DSPy, or PromptFoo for scale testing
