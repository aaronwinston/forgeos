# Arize Observe 2026: Developer-Focused Experience Guide

**Theme:** Feedback Loops for Agents  
**Audience:** AI builders, engineering leads, hands-on developers  
**Tone:** Technical, peer-to-peer, builder-focused (not corporate)

---

## EXPERIENCE PRINCIPLES

### 1. Problem First, Event Second
- Lead with pain developers face (agents break in production)
- Position Observe as the place to learn solutions
- Never say "come to our conference"; say "hear how teams solve this"

### 2. Hands-On > Lecture
- 4 hero sessions (40-50 min talks)
- 4 half-day workshops (people code + learn)
- Live demos showing feedback loops in action
- Interactive Q&A (time for real questions)

### 3. Technical Depth
- Assume the audience knows agents
- Dig into architecture, not features
- Code examples, not slide decks
- Real metrics from production systems

### 4. Peer Authority
- Speakers are engineers, not executives
- Named companies (Cursor, Uber, DeepMind, OpenAI) validate legitimacy
- Story time: "Here's what we learned the hard way"
- Networking prioritized (people came to meet each other)

### 5. 7 Keywords Woven In
Thread these throughout talks, materials, discussions:
- Agent harness
- Harness engineering
- AI agent architecture patterns
- Orchestration layer
- Multi-agent system design
- Agent memory architecture
- Tool calling architecture

---

## AGENDA (June 4, 9am-5pm)

### Morning Block (9am-12:30pm)

```
9:00-9:30    REGISTRATION + COFFEE
             Network before sessions begin
             Grab stickers, name badges, schedule

9:30-10:30   KEYNOTE: "Closing the Feedback Loop"
             Speaker: Aayush Garg (Cursor)
             Room: Main stage
             
             The problem: Code-gen agents work in testing, fail in production
             The loop: Observability → Eval → Retrain → Deploy → Measure
             The proof: Real metrics from Cursor's production agents
             
             Audience takeaway: You don't need perfect agents; you need feedback loops

10:30-11:00  BREAK + NETWORKING
             Sponsor booths
             Coffee, food
             Hallway conversations

11:00-12:00  SESSION TRACK A: Agent Memory Architecture
             Speaker: Chi Zhang
             Room: Theater
             
             Deep dive: How agents learn in production
             Stateless agents vs agents with memory + feedback loops
             Workshop: Build agent memory + evaluate it
             
11:00-12:00  SESSION TRACK B: Enterprise Case Study
             Speaker: [Uber/Enterprise AI Lead]
             Room: Classroom B
             
             Real story: How we deployed agents at [Company]
             What broke: Multi-agent orchestration failures
             How we fixed it: Feedback loops at the orchestration layer
             Metrics: Time-to-fix went from 3 hours to 15 minutes

11:00-12:00  WORKSHOP A (First group): Building Evals That Predict Failures
             Facilitator: [Arize Engineer]
             Room: Lab
             
             Hands-on: Write evals, deploy agent, watch it fail, improve
             Goal: You leave with code for continuous evals
             
12:00-12:30  LUNCH (provided)
             Networking tables organized by topic
             "Agent Architecture" table, "Observability" table, etc.
```

---

### Afternoon Block (12:30pm-5:00pm)

```
12:30-1:30   SIMULTANEOUS SESSIONS

12:30-1:30   SESSION TRACK C: Tool Calling Architecture
             Speaker: [Engineer from CrewAI/Mastra/similar]
             Room: Theater
             
             Problem: Tool chains break in production (boundary failures)
             Architecture: Observability + Eval + Retrain for tool sequences
             Real example: Multi-tool agent that learns which sequences work
             Walkthrough: How to instrument tool calling for feedback loops

12:30-1:30   SESSION TRACK D: Evals at Scale
             Speaker: Eno Oziel
             Room: Classroom B
             
             Problem: Static evals don't scale to production
             Solution: Continuous evals that feed retraining loops
             Infrastructure: What does this look like at scale?
             Metrics: Measuring eval quality in production

12:30-1:30   WORKSHOP B (Second group): Building Evals That Predict Failures
             Facilitator: [Arize Engineer]
             Room: Lab
             
             Same content as Workshop A (parallel group)

1:30-2:00    BREAK + NETWORKING
             Office hours (go ask speakers questions)
             Sponsor booths

2:00-3:00    SPEAKER PANEL: Multi-Agent Systems at Scale
             Moderator: [Arize Engineer]
             Panelists: Aayush, Chi, [Enterprise lead], Eno
             Room: Main stage
             
             Structured questions:
             - Why do multi-agent systems fail?
             - How does observability change with multiple agents?
             - What does the orchestration layer look like?
             - How do you retrain when failures cross agent boundaries?
             - What metrics matter?
             
             Audience Q&A (bring your real problems)

3:00-3:30    BREAK + NETWORKING
             Sponsor booths
             Hallway conversations

3:30-4:30    SIMULTANEOUS SESSIONS

3:30-4:30    SESSION TRACK E: Agent Feedback Loops in Action
             Speaker: Stuart Larson
             Room: Theater
             
             Live demo: Deploy an agent, introduce a failure, fix via feedback loop
             Real codebase walkthrough
             Repository: [Public repo with example]
             Audience: Clone it, use it at your org

3:30-4:30    SESSION TRACK F: Memory Architecture for Learning
             Speaker: [Arize engineer or Chi continued]
             Room: Classroom B
             
             Deep technical: Session state, vector stores, retrieval architectures
             Code walkthrough: How to add memory to existing agent
             Performance trade-offs: Memory vs latency vs cost

3:30-4:30    WORKSHOP C (Third group): Setting Up Observability
             Facilitator: [Arize Engineer]
             Room: Lab
             
             Hands-on: Instrument an agent with sessions + traces
             Real tool: Use Arize SDK
             Goal: You leave with code you can deploy Monday

4:30-5:00    CLOSING KEYNOTE: The Future of Agent Harness Engineering
             Speaker: Aparna Dhinakaran (Founder & CEO)
             Room: Main stage
             
             What we're seeing across thousands of agents
             Patterns that work (feedback loops)
             Patterns that fail (static approaches)
             The next 12 months: What's changing in this space
             Call to action: Build with feedback loops in mind

5:00-5:30    NETWORKING + THANKS
             Informal wrap-up
             Speaker availability
             Prizes, giveaways

5:30         VENUE CLOSES
```

---

## SPEAKER BRIEF: "Make It Developer-Focused"

### When You're Preparing Your Talk

**DO:**
```
✓ Start with a problem the audience has debugged
  ("Your agent passed evals. You shipped it. It broke in prod.")
  
✓ Show code or architecture diagrams
  (People want to see HOW, not just WHAT)
  
✓ Share real metrics from your production system
  ("Time-to-fix went from 3 hours to 15 minutes")
  
✓ Explain the feedback loop specific to your domain
  (Code-gen loops vs orchestration loops vs memory loops)
  
✓ End with: "Here's what you can do Monday"
  (Actionable, concrete next steps)
```

**DON'T:**
```
✗ Spend time on Arize product demo
  (Assume they know what observability is)
  
✗ Use generic "agent reliability" language
  (Use specific architecture: memory, orchestration, tool calling)
  
✗ Avoid hard technical questions
  (These developers came to learn the hard parts)
  
✗ Make it about your company's achievement
  (Frame it as "here's what we learned, try it")
  
✗ Save questions for the end
  (Build in interactivity; let people interrupt with questions)
```

### Message Threading

In your talk, weave in:
- **Agent harness / Harness engineering:** How you think about agents at scale
- **Architecture patterns:** The specific loops you built
- **Orchestration layer:** Multi-agent complexity
- **Memory architecture:** How agents learn
- **Tool calling:** Boundary failures and how to observe them

**Example language:**
> "We learned that harness engineering isn't just observability. It's observability + evaluation + retraining loops. For us, the orchestration layer was where most failures happened, so we built feedback loops specifically for multi-agent coordination."

---

## WORKSHOP DESIGN: Keep It Real

### Workshop 1: Building Evals That Predict Failures (3 hours)

**Problem statement:** Your evals pass. Your agents break in production. Why?

**What we do:**
1. **First hour:** Write static evals (participants write 5 evals for a demo agent)
2. **Live demo:** Deploy the agent with those evals
3. **Chaos:** Introduce failures intentionally
4. **Reality check:** Show that evals didn't catch them
5. **Explanation:** Why static evals fail

Then:
6. **Hour two:** Build continuous eval pipeline
7. **Hook it up:** Production failures → auto-eval → signal for retrain
8. **Code:** Participants implement a basic version
9. **Test it:** Run failures through it; watch it catch them

Finally:
10. **Hour three:** Architecture patterns
11. **Cost/benefit:** When is this worth it? Trade-offs?
12. **Q&A:** Real questions about their production setup

**They leave with:** Code they can use Monday; template for their own agents

---

### Workshop 2: Setting Up Observability (3 hours)

**Problem:** You're blind. You log strings. You can't reproduce failures.

**What we do:**
1. **Design:** What to observe in an agent (inputs, decisions, outputs, reasoning, errors)
2. **Build it:** Implement observability in a sample agent using Arize SDK
3. **Test it:** Deliberately break the agent; show the rich context in traces
4. **Queries:** How to find the failure in your observability system
5. **Alerts:** Auto-detect when something's wrong
6. **Integration:** Connect to your feedback loop (failures → evals)

**They leave with:** Working observability for their agent; code to deploy

---

### Workshop 3: Multi-Agent Orchestration & Feedback Loops (3 hours)

**Problem:** One agent fails 5%. Three agents coordinating fail 15%. Why?

**What we do:**
1. **Architecture:** How failures cascade across agent boundaries
2. **Observability:** Tracing failures at the orchestration level (not just individual agents)
3. **Build it:** Implement orchestration observability (spans that cross agents)
4. **Evals:** Test workflows, not individual agents
5. **Failure injection:** Break the orchestration intentionally
6. **Feedback loops:** How do you retrain when failures cross agent boundaries?
7. **Real complexity:** Multi-agent memory, shared state, coordination patterns

**They leave with:** Understanding of multi-agent system design; patterns to avoid

---

## DEVELOPER EXPERIENCE (Day-Of)

### Registration / Arrival (8:30am)
```
- Quick check-in (name, company, interests)
- Badge
- Lanyard with schedule
- Sticker pack (agent-themed: "Closed the loop", "Stateless ≠ Happy", etc.)
- Notebook + pen
- Water bottle
```

### Name Badge Design
```
[Name]
[Company]
[What you build]
  ☐ Agents
  ☐ Agent infrastructure
  ☐ Observability
  ☐ Other

[What you want to learn]
  ☐ Memory architecture
  ☐ Multi-agent systems
  ☐ Evals at scale
  ☐ Tool calling
  ☐ General feedback loops

(Helps people network based on shared interests)
```

### Signage
```
Main stage area: "Feedback Loops: Architecture Doesn't Lie"
Workshop area: "Hands-On: Code with Us"
Networking area: "Hallway Track: Where Ideas Happen"
Speaker office hours: "Office Hours: Ask the Team"
Sponsor area: "Sponsor booths — but they know you're technical"
```

### Snacks / Food Strategy
```
9:00am   Coffee, pastries (fuel developers early)
12:00pm  Lunch — tables organized by topic
2:00pm   Snack break
4:00pm   Afternoon coffee

Foods that don't make hands/slides dirty:
- Fruit
- Sandwiches
- Chips in bowls
- Cookies
- Coffee, tea, water
```

### Wifi / Setup
```
- Network: OBSERVE_2026
- Password: [Simple password]
- No "accept terms" pages (frustrates developers)
- QR code on schedule with wifi info
- Backup: Mobile hotspot in main room for when wifi fails
```

### Code / Materials
```
GitHub repo: github.com/arize-ai/observe-2026
- All workshop code
- Session slides
- Example agents
- Setup instructions

Attendees can:
- Clone before the conference
- Pull during the conference
- Take it home and use it
```

---

## MEASUREMENT & FOLLOW-UP

### During Event
```
- Attendance (who showed up)
- Workshop attendance (which hands-on sessions were full)
- Q&A engagement (which speakers got the most questions)
- Hallway feedback (what are people saying?)
- Sponsor interactions (which booths were busy)
```

### Post-Event (Day 1)
```
Email to all attendees:
- Thank you
- Video links (when available)
- GitHub repo link
- Feedback survey (2 min, 5 questions)
- Next steps (webinar series on feedback loops coming soon)
```

### Post-Event (Week 1)
```
Analyze feedback:
- Which sessions were most valuable?
- Which topics resonated?
- What's missing from the current story?

Segment attendees:
- Registered interest (memory, orchestration, evals, tool calling)
- Company type (startup, enterprise)
- Use case (code-gen, automation, multi-agent)

Use this for content strategy next quarter
```

### Post-Event (Month 1)
```
Content repurposing:
- Session videos on YouTube
- Audio transcripts → blog posts
- Code → tutorials
- Feedback themes → next year's sessions

Contact attendees who:
- Registered interest in partnerships
- Showed strong engagement
- Work at target accounts
```

---

## TONE & LANGUAGE THROUGHOUT

### Descriptions (Website, Emails, Materials)

**Session Description Style:**

OLD (marketing-y):
> "Join us for an exciting session on agent reliability! Learn cutting-edge techniques for building production-grade agents. Industry leaders will share insights on best practices and lessons learned."

NEW (developer-focused):
> "Your agent works in testing. It breaks in production. Here's why—and the feedback loop pattern that prevents it. Hear how Cursor catches failures automatically and deploys improvements without manual intervention."

---

**Workshop Description Style:**

OLD (vague):
> "Hands-on workshop on agent observability. Learn the fundamentals and build systems that matter."

NEW (specific):
> "Three hours. You'll instrument an agent with sessions + traces. You'll deploy it. You'll break it intentionally. You'll see exactly why bad observability leaves you blind. You'll leave with code you can deploy Monday."

---

### Signage & Materials

**Hero visuals:**
- Code screenshots (not cartoons)
- Real dashboards (not mock-ups)
- Actual failure traces
- Metrics from production systems

**Copy on slides:**
- Problem first ("agents fail in production")
- Specific ("multi-agent orchestration failures")
- Not "revolutionary AI infrastructure"

**Stickers / Swag:**
- Funny ones: "Stateless ≠ Happy", "Closed the Loop", "Feedback Loop Achieved"
- Technical ones: "Agent Harness Engineer", "Memory Architecture", "Orchestration Layer"
- Not generic "Arize" branding

---

## PARTNERSHIP / SPONSOR GUIDELINES

If sponsors are involved:
```
✓ Sponsors demonstrate real integrations (not just logo placements)
✓ Sponsor talks are technical (how tool X enables feedback loops)
✓ Sponsor demos show code, not slide decks
✓ Sponsor booths have engineers (not salespeople)
✗ No "come see how we can help you" pitches
✗ No banner ads in the main room
✗ No generic product demos
```

---

**Last Updated:** April 28, 2026  
**Experience:** Technical, hands-on, developer-focused  
**Measurement:** Engagement, feedback, content opportunity
