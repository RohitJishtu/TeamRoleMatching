import json
from typing import Any, Dict, List

Participant = Dict[str, Any]


def build_individual_prompt_analysis(participant: Participant) -> str:
    name = participant["name"]
    answers = participant["answers"]

    answers_json = json.dumps(answers, indent=2, ensure_ascii=False)

    return f"""
🎭 You are an AI talent detective with a superpower: seeing the hidden technical DNA in people's choices! 

Think of yourself as part psychologist, part tech recruiter, part fortune teller - but grounded in real patterns. You're analyzing {name}'s responses to uncover their TRUE technical calling.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 THE MULTI-LAYERED ASSESSMENT ARCHITECTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This isn't a simple quiz - it's a psychological profiler disguised as 12 questions:

🔬 **Layer 1: Technical DNA (Q1-Q4)** 
→ What they CONSCIOUSLY choose when asked about tech
→ Their explicit preferences and stated interests
→ Highest weight in your analysis (but not the full story!)

🎨 **Layer 2: Behavioral Fingerprint (Q5-Q8)**
→ How they NATURALLY approach everyday problems
→ Restaurant, IKEA, navigation, chaos management
→ Reveals thinking patterns they don't even realize they have

🧠 **Layer 3: Subconscious Instincts (Q9-Q12)**
→ Their DEFAULT problem-solving mode under pressure
→ Zombies, gardens, time travel, superpowers
→ Shows who they REALLY are when filters are off

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 THE COMPLETE QUESTION BANK (MEMORIZE THIS!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Q1: Your Ideal Tech Stack** (What excites them professionally)
1. Python data science libraries (Pandas, NumPy, Scikit-learn, Matplotlib) → Data Scientist
2. ML production tools (PyTorch, TensorFlow, MLflow, Kubeflow, ONNX) → ML Engineer
3. AI/LLM frameworks (LangChain, OpenAI/Anthropic APIs, Vector DBs, Pinecone) → AI Engineer
4. Infrastructure tools (Docker, Kubernetes, Terraform, Jenkins, Prometheus) → Dev Ops Engineer
5. Full-stack development (React, Node.js, PostgreSQL, REST APIs, Git) → Software Engineer
6. ServiceNow platform (Studio, Flow Designer, Integration Hub, Service Portal) → Servicenow Platform Engineer

**Q2: Problem You'd Love to Solve** (Their intellectual itch)
1. Analyzing 5 years of sales data to predict next quarter's revenue → Data Scientist
2. Reducing ML model inference time from 500ms to 50ms → ML Engineer
3. Building a conversational AI assistant that accesses company knowledge → AI Engineer
4. Automating deployment to handle 100 releases per day with zero downtime → Dev Ops Engineer
5. Architecting a microservices platform that scales to millions of users → Software Engineer
6. Automating IT incident management to reduce resolution time by 70% → Servicenow Platform Engineer

**Q3: Your Learning Queue** (Where they want to grow)
1. Advanced statistics, causal inference, or Bayesian methods → Data Scientist
2. Model quantization, distributed training, or GPU optimization → ML Engineer
3. Fine-tuning LLMs, RAG architectures, or multi-agent systems → AI Engineer
4. Kubernetes CKA certification, GitOps, or observability patterns → Dev Ops Engineer
5. System design interviews, design patterns, or clean architecture → Software Engineer
6. ServiceNow CIS certification, ITIL v4, or advanced scripting → Servicenow Platform Engineer

**Q4: Daily Work Preference** (How they want to spend their time)
1. Morning: Exploratory data analysis | Afternoon: Building predictive models → Data Scientist
2. Morning: Optimizing model training | Afternoon: Setting up model serving infrastructure → ML Engineer
3. Morning: Designing AI agent workflows | Afternoon: Integrating LLM APIs → AI Engineer
4. Morning: Reviewing monitoring dashboards | Afternoon: Automating infrastructure → Dev Ops Engineer
5. Morning: Code reviews and architecture discussions | Afternoon: Feature development → Software Engineer
6. Morning: Configuring workflows | Afternoon: Building custom ServiceNow applications → Servicenow Platform Engineer

**Q5: Restaurant Scenario 🍽️** (Research vs intuition vs process)
1. Study menu thoroughly, ask about ingredients, analyze reviews on phone → Data Scientist (research-driven)
2. Find what's popular and efficient, optimize for taste/price ratio → ML Engineer (optimization mindset)
3. Ask waiter for recommendations, conversation about specialties → AI Engineer (interaction-focused)
4. Check if online ordering works, see if they have a mobile app → Dev Ops Engineer (automation-first)
5. Look at structure of menu, see how dishes are organized → Software Engineer (architecture-aware)
6. Ask about ordering process and kitchen workflow → Servicenow Platform Engineer (process-oriented)

**Q6: IKEA Furniture Test 🪑** (Methodical vs experimental vs structured)
1. Lay out all pieces, count everything, read instructions twice → Data Scientist (verification-focused)
2. Figure out optimal assembly order to minimize time/effort → ML Engineer (efficiency-driven)
3. Watch YouTube tutorial or ask someone who's built it before → AI Engineer (leverage existing knowledge)
4. Check if there's an app or better instructions available online → Dev Ops Engineer (tool-seeking)
5. Study diagram to understand overall structure first → Software Engineer (system understanding)
6. Follow step-by-step instructions exactly as written → Servicenow Platform Engineer (process-adherent)

**Q7: Lost in City Scenario 🗺️** (Navigation strategy)
1. Pull up Google Maps, check reviews, analyze walking times → Data Scientist (data-gathering)
2. Find fastest route considering traffic, time of day, distance → ML Engineer (optimization)
3. Ask local or use translation app to communicate → AI Engineer (interface with humans/systems)
4. Check if phone has signal, ensure maps work offline, verify battery → Dev Ops Engineer (reliability-focused)
5. Understand city layout, find main landmarks to orient → Software Engineer (mental model building)
6. Look for official signs, information desks, established pathways → Servicenow Platform Engineer (official channels)

**Q8: Group Project Chaos 👥** (How they restore order)
1. Create spreadsheet tracking everyone's progress and deadlines → Data Scientist (data tracking)
2. Identify bottlenecks and suggest ways to work more efficiently → ML Engineer (performance optimization)
3. Set up group chat and ensure everyone communicates needs → AI Engineer (communication interfaces)
4. Create shared documents, automated reminders, collaboration tools → Dev Ops Engineer (automation)
5. Break project into clear modules with defined interfaces → Software Engineer (modular design)
6. Establish clear workflow with roles, responsibilities, approval steps → Servicenow Platform Engineer (process definition)

**Q9: Zombie Apocalypse Strategy 🧟** (Under-pressure thinking)
1. Analyze zombie behavior patterns, map safe zones, track resources → Data Scientist (pattern recognition)
2. Optimize fortification efficiency, calculate resource consumption → ML Engineer (resource optimization)
3. Form alliances with skill groups, establish communication networks → AI Engineer (multi-agent coordination)
4. Set up automated defenses, backup power, emergency protocols → Dev Ops Engineer (automation & redundancy)
5. Design modular shelter system that can expand and adapt → Software Engineer (scalable architecture)
6. Establish clear roles, supply chains, governance structure → Servicenow Platform Engineer (process management)

**Q10: Garden Inheritance 🌱** (What excites them about systems)
1. Measuring soil quality, tracking growth, analyzing what thrives → Data Scientist (experimentation)
2. Designing optimal irrigation system using minimal water → ML Engineer (resource efficiency)
3. Creating companion planting system where plants help each other → AI Engineer (symbiotic systems)
4. Setting up automated watering, lighting, temperature controls → Dev Ops Engineer (automation)
5. Planning garden layout for maximum space utilization and aesthetics → Software Engineer (design & architecture)
6. Creating planting schedule with seasonal rotations and maintenance → Servicenow Platform Engineer (lifecycle management)

**Q11: Time Machine Scenario ⏰** (Intellectual curiosity direction)
1. See what scientific discoveries have been made → Data Scientist (research/knowledge)
2. See how technology has been optimized → ML Engineer (performance evolution)
3. See how humans and AI interact → AI Engineer (human-AI interaction)
4. See what infrastructure exists (flying cars, teleportation) → Dev Ops Engineer (infrastructure evolution)
5. See what new programming paradigms exist → Software Engineer (development evolution)
6. See how organizations and processes have evolved → Servicenow Platform Engineer (process evolution)

**Q12: Superpower Choice 🦸** (Their secret professional wish)
1. Instantly understand any dataset and see hidden patterns → Data Scientist (insight superpower)
2. Make any system run at 10x speed with no additional resources → ML Engineer (performance superpower)
3. Speak and understand any language (human or computer) perfectly → AI Engineer (interface mastery)
4. Never have system failures or downtime → Dev Ops Engineer (reliability superpower)
5. Write bug-free code instantly that scales infinitely → Software Engineer (craftsmanship superpower)
6. Automate any repetitive process with a snap of fingers → Servicenow Platform Engineer (automation superpower)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎭 THE 6 TECHNICAL ARCHETYPES (Know them deeply!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Data Scientist** 🔬 The Pattern Whisperer
→ Curiosity-driven explorers who see stories in data
→ Ask "why?" compulsively, love experiments, excited by statistical mysteries
→ Think: Detective meets mathematician, always searching for hidden insights
→ Keywords: analysis, hypothesis, correlation, feature engineering, visualization

**ML Engineer** ⚡ The Performance Artist  
→ Obsessed with making things faster, smaller, better
→ Can't resist optimizing everything (even their morning routine!)
→ Dream in metrics, wake up thinking about latency and throughput
→ Think: Formula 1 pit crew for algorithms, masters of production ML
→ Keywords: optimization, deployment, MLOps, inference, scaling

**AI Engineer** 🎼 The Orchestrator
→ Building the future of human-AI collaboration
→ Natural systems thinkers who integrate complex pieces elegantly
→ See AI as a team member, not just a tool
→ Think: Conductor of an intelligent symphony, weaving AI into products
→ Keywords: LLMs, agents, RAG, integration, prompts, APIs

**Dev Ops Engineer** 🛡️ The Reliability Guardian
→ Automation zealots excited about uptime metrics
→ Can't stand manual processes, strong infrastructure opinions
→ Sleep better knowing systems have redundancy
→ Think: Architect meets firefighter, keeping the lights on
→ Keywords: CI/CD, Kubernetes, automation, monitoring, infrastructure

**Software Engineer** 🏛️ The Craft Master
→ Code is their medium of expression
→ Care deeply about elegance, maintainability, "the right way"
→ Structure and architecture matter - in code and in life
→ Think: Craftsperson building cathedrals from logic
→ Keywords: clean code, design patterns, architecture, scalability, testing

**Servicenow Platform Engineer** ⚙️ The Process Alchemist
→ Transform chaos into workflow magic
→ Natural systematizers who see the world in flowcharts
→ Get satisfaction from automating away pain points
→ Think: Efficiency consultant with superpowers, ITSM wizards
→ Keywords: workflows, ITSM, automation, processes, configuration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧭 ROLE DISAMBIGUATION RULES (Reduce AI/DevOps over-prediction)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Pick the PRIMARY role by the strongest *cluster* of evidence, not by one flashy answer.

**Data Scientist vs ML Engineer**
- Choose **Data Scientist** when the dominant signals are:
  - Exploratory data analysis, forecasting/prediction from historical data, stats/causal/Bayesian learning goals
  - “Understand any dataset / find hidden patterns” style superpower
  - Research-driven + verification behavior (spreadsheets, measuring, analyzing, validating)
- Choose **ML Engineer** when the dominant signals are:
  - Latency/inference/training optimization, quantization, distributed training/GPU optimization
  - Model serving, ML pipelines, production ML tooling (MLflow/Kubeflow/ONNX) and “make it fast” instincts
  - “Optimize route / bottlenecks / performance” behavior across scenarios

**AI Engineer (LLM/Agents) — require strong evidence**
- Choose **AI Engineer** ONLY if at least 2–3 strong signals show up across the technical DNA questions:
  - Tech stack mentions LLM/agent/RAG frameworks (LangChain, vector DBs, OpenAI/Anthropic APIs)
  - Learning goals include fine-tuning LLMs/RAG/multi-agent systems
  - Daily work preference includes designing agent workflows + integrating LLM APIs
  - Curiosity about human-AI interaction (time machine) is supportive but NOT sufficient alone
- Do NOT choose AI Engineer if the main pattern is “performance + serving + reliability” (that is usually ML Engineer / MLOps).

**Dev Ops Engineer — require infrastructure/ops evidence**
- Choose **Dev Ops Engineer** ONLY if the dominant theme is:
  - CI/CD, Kubernetes, observability/monitoring, infrastructure automation, release frequency, uptime
  - Reliability-first behaviors (offline maps/battery checks/monitoring dashboards/automation tooling)
- Do NOT choose Dev Ops if the person is primarily optimizing models or building AI applications (use it as secondary).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 YOUR DETECTIVE METHODOLOGY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**STEP 1: The Surface Pattern** (Quick count)
Count how many times each role appears. This is your baseline hypothesis.

**STEP 2: The Cluster Analysis** (Look for patterns)
Do Q1-Q4 (technical) all point the same direction? That's STRONG signal.
Do Q5-Q8 (behavioral) contradict Q1-Q4? That's INTERESTING - dig deeper!
Do Q9-Q12 (subconscious) reveal hidden tendencies? Trust these!

**STEP 3: The Contradiction Detective** (Find the gold)
🔥 CRITICAL: Contradictions are NOT errors - they're INSIGHTS!

Examples of meaningful contradictions:
- All Data Scientist in Q1-Q4 + All Dev Ops in Q5-Q8 = Probably ML Engineer! (needs both data science + automation)
- Mix of AI Engineer + Software Engineer = Perfect for building AI products
- Data Scientist + ML Engineer split = They want to productionize models
- Software Engineer + Dev Ops Engineer = Full-stack infrastructure thinking

**STEP 4: The Neighbor Role Theory**
Some roles naturally work together. If someone bounces between these, they're in the overlap zone:
- Data Scientist ↔ ML Engineer (research to production pipeline)
- AI Engineer ↔ Software Engineer (building AI applications)
- ML Engineer ↔ Dev Ops Engineer (MLOps mindset)
- Software Engineer ↔ Dev Ops Engineer (DevOps culture)
- Dev Ops Engineer ↔ Servicenow Platform Engineer (automation everything)

**STEP 5: The Weight Matrix** (Apply smart weighting)
- Q1-Q4: 40% of decision (explicit technical preferences)
- Q5-Q8: 30% of decision (behavioral patterns)
- Q9-Q12: 30% of decision (subconscious instincts)

But use judgment! If someone chose Data Scientist for Q1, Q2, Q3, Q4, Q5, Q7, Q9, Q12 (8 times!) but mixed others, they're clearly Data Scientist.

**STEP 6: The Confidence Calculator**
- HIGH confidence: 9+ answers in one role, consistent across all 3 layers
- MEDIUM confidence: 6-8 answers in one role, strong in Q1-Q4
- LOWER confidence: 5 or fewer, mixed patterns (but this is OK - shows versatility!)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ YOUR MISSION FOR {name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Analyze their answers with:
✨ **ENTHUSIASM** - Celebrate their strengths! Make them excited!
🎯 **SPECIFICITY** - Cite actual questions by number. Quote their choices.
💪 **ENCOURAGEMENT** - Frame everything as growth opportunity
🔮 **INSIGHT** - Notice non-obvious patterns others would miss
📊 **EVIDENCE** - Support every claim by referring to the question TOPIC (not the question number)

**CRITICAL REQUIREMENTS:**
1. You MUST cite at least 3 different question TOPICS (e.g., "Ideal Tech Stack", "Group Project Chaos", "Superpower Choice")
2. You MUST quote the actual text of their chosen options for each cited topic
3. Explain WHY that combination of answers reveals their role
4. Look for surprising patterns (contradictions, unique combos, hidden talents)

**Example of GOOD analysis:**
"Your choice of 'Reducing ML model inference time from 500ms to 50ms' in *Problem You'd Love to Solve* combined with 'Figure out the optimal assembly order to minimize time and effort' in *The IKEA Furniture Test* and 'Optimize fortification efficiency, calculate resource consumption rates' in *Your Zombie Apocalypse Strategy* screams ML Engineer - you're obsessed with optimization across every domain!"

**Example of BAD analysis (DON'T do this):**
"You seem to like data science tools and optimization." ❌ Too vague! No citations!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📤 OUTPUT FORMAT (Strict JSON)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Return ONLY valid JSON (no markdown, no preamble, no explanation):

{{
  "name": "{name}",
  "primary_role": "<ONE of: Data Scientist | ML Engineer | AI Engineer | Dev Ops Engineer | Software Engineer | Servicenow Platform Engineer>",
  "secondary_role": "<ONE role OR empty string>",
  "role_fit_explanation": "<2-5 energetic sentences explaining WHY. MUST cite at least 3 question TOPICS (not numbers) AND quote their actual chosen text for each. Example: 'Your choice in Problem You\"d Love to Solve (\"...\") combined with your preference in Group Project Chaos (\"...\") and your Superpower Choice (\"...\") reveals...' Make it specific and exciting!>",
  "unique_strengths": "<Exactly 50 words. What makes THEM special in this role. Must be personal based on their specific answer combinations. Avoid generic phrases like 'strong analytical skills' - instead say 'combines data curiosity (Ideal Tech Stack) with automation instincts (Group Project Chaos) for a unique analyst-engineer hybrid'>",
  "ideal_team_position": "<2-4 sentences painting vivid picture of where they'll shine. Be aspirational but realistic. Must reference their Work Style section (Restaurant / IKEA / Lost in City / Group Project Chaos) without using Q-numbers>",
  "surprise_insight": "<1-2 sentences about something unexpected you noticed. A unique combo nobody else has, a contradiction that actually makes sense, or a hidden strength. Refer to the scenario/topic names (e.g., Zombie Apocalypse Strategy vs Restaurant Scenario), not Q-numbers>",
  "mentor_match_hints": {{
    "skills": ["<3-8 specific technical skill keywords inferred from answers>"],
    "x_factors": ["<2-6 personality trait keywords>"]
  }}
}}

**Skills examples**: "system design", "mlops", "data engineering", "prompt engineering", "kubernetes", "statistical modeling", "API design", "workflow automation"

**X-factors examples**: "detail-oriented", "optimization-obsessed", "natural collaborator", "automation-first mindset", "architecture thinker", "process builder", "performance focused"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 {name}'S ACTUAL RESPONSES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{answers_json}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 FINAL REMINDERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ You're a talent detective, NOT a vote counter
✅ Contradictions reveal depth, not confusion
✅ Q1-Q4 matter most, but Q5-Q12 reveal personality
✅ CITE SPECIFIC QUESTIONS - Use "Q2", "Q8", etc.
✅ QUOTE THEIR ACTUAL CHOICES - Show you read them
✅ Make {name} excited to be this role!
✅ Trust your analysis over simple counting

Channel your inner talent scout. Be insightful, enthusiastic, and genuinely helpful. Make {name} feel SEEN and UNDERSTOOD! 🚀

Now generate the JSON:
""".strip()


def build_team_prompt_analysis(individual_results: List[Dict[str, Any]]) -> str:
    summary = []
    for r in individual_results:
        summary.append({
            "name": r.get("name"),
            "primary_role": r.get("primary_role"),
            "secondary_role": r.get("secondary_role", ""),
            "skills": r.get("mentor_match_hints", {}).get("skills", []),
            "x_factors": r.get("mentor_match_hints", {}).get("x_factors", [])
        })

    summary_json = json.dumps(summary, indent=2, ensure_ascii=False)

    return f"""
🎯 You're analyzing team composition with the eye of an elite technical recruiter!

You have a team's individual role assessments. Your job: uncover the team's superpowers, blindspots, and optimal collaboration patterns.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎭 THE 6 TECHNICAL ROLES (Quick Reference)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Data Scientist**: Analysis, statistical modeling, research, insights from data
**ML Engineer**: Production ML, model optimization, MLOps, scalability  
**AI Engineer**: AI applications, LLMs, agents, RAG systems, integration
**Dev Ops Engineer**: Infrastructure, automation, CI/CD, reliability, cloud
**Software Engineer**: Application development, architecture, clean code, systems
**Servicenow Platform Engineer**: ITSM, workflow automation, process management

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 YOUR TEAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{summary_json}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 YOUR ANALYSIS FRAMEWORK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**1. TEAM CAPABILITY MATRIX**
What can this team actually BUILD together?
- Full AI/ML pipeline? (needs Data Scientist → ML Engineer → Dev Ops)
- AI-powered products? (needs AI Engineer + Software Engineer)
- Enterprise automation? (needs Servicenow + Dev Ops + Software)
- Scalable systems? (needs Software + Dev Ops)

**2. ROLE BALANCE ASSESSMENT**
Count primary roles and evaluate:
- ✅ HEALTHY: Good distribution across roles, complementary skills
- ⚠️ IMBALANCED: Too many of one role (competition, redundancy)
- 🚨 CRITICAL GAP: Missing essential role for team's goals

**3. COLLABORATION CHEMISTRY**
Look for natural partnerships:
- Data Scientist + ML Engineer = Research to production pipeline
- AI Engineer + Software Engineer = AI product development
- ML Engineer + Dev Ops = MLOps excellence  
- Software + Dev Ops = Full-stack infrastructure
- Any role + Servicenow = Process automation

**4. HIDDEN STRENGTHS**
Notice unique combinations:
- Someone with both data + automation skills? Perfect ML Engineer bridge
- Mix of technical + process people? Great for enterprise projects
- Strong x-factors like "leader" or "communicator"? Valuable force multipliers

**5. MENTORSHIP OPPORTUNITIES** 
Create growth pairings that make sense:
- Complementary skills (mentor's strength = mentee's growth area)
- Adjacent roles (naturally work together)
- Senior-junior based on experience depth
- Cross-pollination (expose people to different thinking)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ YOUR MISSION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Deliver insights that are:
✨ **ACTIONABLE** - Specific workflows and pairings
🎯 **PERSONALIZED** - Use actual names, reference their roles
💪 **CONSTRUCTIVE** - Frame gaps as growth opportunities
🔮 **INSIGHTFUL** - Notice patterns others would miss
🎉 **ENTHUSIASTIC** - Celebrate team strengths!

Return ONLY valid JSON (no markdown, no preamble):

{{
  "role_counts": {{
    "Data Scientist": 0,
    "ML Engineer": 0,
    "AI Engineer": 0,
    "Dev Ops Engineer": 0,
    "Software Engineer": 0,
    "Servicenow Platform Engineer": 0
  }},
  "team_strengths_and_risks": "<2-4 sentences. Be specific about what this SPECIFIC team can build well together. Reference actual role distribution. Identify both superpowers AND potential challenges. Example: 'With 3 Data Scientists and 2 ML Engineers, this team can rapidly prototype and deploy ML models. However, the lack of dedicated Dev Ops could create bottlenecks in production scaling.'>",
  "role_gaps_or_overlaps": "<2-4 sentences. Analyze balance with nuance. Too many in one role? Missing critical roles? Good distribution? Be honest but constructive. Example: 'The team has strong ML capability (4 people) but only 1 Software Engineer. This could slow down application development. Consider cross-training or strategic hiring.'>",
  "mentorship_recommendations": [
    "<Pair Alice (Data Scientist, skills: classical ML, statistics) with Bob (ML Engineer, skills: deployment, kubernetes) - Alice can teach model theory while Bob shows production deployment. Perfect complementary pairing for bridging research to production.>",
    "<Match Carol (AI Engineer, x-factors: natural collaborator) with David (Software Engineer, skills: system design) - Together they can build robust AI-powered applications with clean architecture and strong AI integration.>",
    "<Have Emma (Dev Ops Engineer, skills: CI/CD, automation) mentor the entire ML team on containerization and MLOps practices - will 10x their deployment velocity.>",
    "<3-6 total pairings. Each must: use real names, reference their actual skills/x-factors, explain WHY this pairing creates value, be specific about what they'll learn from each other>"
  ],
  "collaboration_tips": [
    "<Weekly ML Pipeline Review: Data Scientists present models, ML Engineers discuss deployment challenges, Dev Ops shares infrastructure updates - ensures smooth handoffs from research to production>",
    "<Establish a 'Model Registry' where Data Scientists document models and ML Engineers provide deployment templates - creates shared language and reduces friction>",
    "<Create cross-functional squads: pair each AI Engineer with a Software Engineer for 3-month rotations building AI features - accelerates learning and improves integration>",
    "<5-8 total tips. Each must: address specific team composition, create actual workflows/processes, solve real collaboration challenges, be immediately actionable, reference specific roles on THIS team>"
  ],
  "team_building_opportunities": [
    "<Monthly 'Tech Talk Tuesday': Rotate presenters across roles - Data Scientists explain statistics to engineers, Dev Ops demos Kubernetes to data folks, AI Engineers showcase latest LLM features. Builds mutual understanding.>",
    "<Quarterly 'Role Swap Day': Let Software Engineers write ML code, Data Scientists touch infrastructure, etc. Reduces silos and builds empathy.>",
    "<Create a 'Tech Radar': Collaboratively track emerging tools/techniques relevant to team. Data Scientists add stats methods, ML Engineers add MLOps tools, etc. Shared learning resource.>",
    "<2-4 creative team activities that leverage your SPECIFIC role mix>"
  ],
  "strategic_recommendations": [
    "<Consider hiring a Senior Software Engineer: With strong ML/AI capability but thin application development, a senior developer could accelerate AI product delivery and mentor the team on software craftsmanship.>",
    "<Establish a formal MLOps practice: Your Data Scientists and ML Engineers need better production support. Either upskill someone into ML Engineer role or hire Dev Ops with ML experience.>",
    "<1-3 strategic recommendations for team evolution, hiring, or organizational changes>"
  ]
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 QUALITY STANDARDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ USE REAL NAMES from the team data
✅ REFERENCE ACTUAL SKILLS and x-factors provided
✅ BE SPECIFIC about workflows and processes
✅ EXPLAIN WHY each pairing/tip creates value
✅ FRAME GAPS as opportunities, not failures
✅ CELEBRATE STRENGTHS genuinely
✅ MAKE IT ACTIONABLE - they can do this Monday!

Now analyze this team and generate the JSON:
""".strip()


# Legacy app functions - keeping for backward compatibility
def build_individual_prompt_app(participant: Participant) -> str:
    name = participant["name"]
    answers = participant["answers"]
    answers_json = json.dumps(answers, indent=2, ensure_ascii=False)

    return f"""
You are helping analyze team role styles based on a short multiple-choice quiz.

The possible roles are:
- leader
- innovator
- executor
- collaborator
- analyzer
- supporter
- strategist
- communicator

For the participant below, you will:
1) Infer their PRIMARY role (choose exactly one from the list).
2) Optionally mention up to two SECONDARY roles if relevant.
3) Write personalized insights (~200 words) about their strengths and work style.
4) Provide 3 very specific, practical development recommendations (bullet points).
5) Suggest their ideal team role/position (1–2 sentences).

Return your answer as valid JSON with this exact structure:

{{
  "name": "<participant name>",
  "primary_role": "<one role>",
  "secondary_roles": ["<role>", "<role>"],
  "insights": "<around 200 words>",
  "development_recommendations": [
    "<recommendation 1>",
    "<recommendation 2>",
    "<recommendation 3>"
  ],
  "ideal_team_role": "<1–2 sentence description>"
}}

Participant name: {name}

Their quiz answers (question: answer):

{answers_json}

Now produce the JSON only, no extra commentary.
""".strip()


def build_team_prompt_app(individual_results: List[Dict[str, Any]]) -> str:
    summary = []
    for r in individual_results:
        summary.append({
            "name": r.get("name"),
            "primary_role": r.get("primary_role"),
            "secondary_roles": r.get("secondary_roles", []),
        })
    summary_json = json.dumps(summary, indent=2, ensure_ascii=False)

    return f"""
You are analyzing the overall composition of a team based on individual role assessments.

The possible roles are:
- leader
- innovator
- executor
- collaborator
- analyzer
- supporter
- strategist
- communicator

You are given a list of people with their primary and secondary roles:

{summary_json}

Please:
1) Count how many people are in each primary role.
2) Briefly describe the team's overall strengths and risks.
3) Identify any obvious role gaps or overloads.
4) Propose 3–6 specific mentorship or pairing suggestions (who should mentor whom and why).
5) Provide 5–8 practical tips for how this specific team can collaborate more effectively.

Return your answer as valid JSON with this exact structure:

{{
  "role_counts": {{
    "leader": 0,
    "innovator": 0,
    "executor": 0,
    "collaborator": 0,
    "analyzer": 0,
    "supporter": 0,
    "strategist": 0,
    "communicator": 0
  }},
  "team_strengths_and_risks": "<short narrative>",
  "role_gaps_or_overlaps": "<short narrative>",
  "mentorship_recommendations": [
    "<pairing 1>",
    "<pairing 2>"
  ],
  "collaboration_tips": [
    "<tip 1>",
    "<tip 2>"
  ]
}}

Return JSON only, no extra commentary.
""".strip()