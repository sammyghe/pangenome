"""WILDSET — the second study domain: the real corpus, hand-labelled.

Domain 1 (`experiment.py`) is a hand-written shop. It tests the mechanism
cleanly and it proves nothing about the world, because I wrote the world.
This is the other half: a frozen snapshot of loci the organism actually
sensed from the live GitHub skills stream, with ground truth labelled by
hand and stated in full below so it can be argued with.

Snapshot taken 2026-08-16 from the live
`observations` table: the 150 highest-starred github_skills loci.
The cut is 150 rather than 30 or 60 on purpose, and the reason is stated
rather than hidden: the interesting items for this owner live in the tail.
A short page would contain neither target and the domain would test
nothing. A long page is also the realistic case — the organism senses
roughly 330 loci every morning, forever.

The owner is STEWARD: someone building agent infrastructure whose problem
is the capability supply chain — what a third-party skill does, what it
can reach, and whether anyone checked. The interests below are the live
organism's own primed interests, not invented for this file.

The discriminating cases (TARGET) are in-trade capabilities sitting far
BELOW the page's adoption distribution — the analogue of domain 1's
underpriced sunglasses. A literal reader ranking by stars never reaches
them; a novelty filter discards them because to this owner "agent skills
security" is the least novel phrase on the page. Only surprise against an
owner-specific reference class finds them.
"""

from __future__ import annotations

# (locus, text, stars) — real loci, real star counts, frozen.
WILD = [
    ('sindresorhus/awesome', 'awesome   Awesome lists about all kinds of interesting topics', 496219),
    ('jwasham/coding-interview-university', 'coding-interview-university  A complete computer science study plan to become a software engineer.', 358839),
    ('vinta/awesome-python', 'awesome-python  An opinionated list of Python frameworks, libraries, tools, and resources', 314197),
    ('awesome-selfhosted/awesome-selfhosted', 'awesome-selfhosted  A list of Free Software network services and web applications which can be hosted on your own servers', 312951),
    ('obra/superpowers', 'superpowers  An agentic skills framework & software development methodology that works.', 272555),
    ('affaan-m/ECC', 'ECC  The agent harness performance optimization system. Skills, instincts, memory, security, and research-first development for Claude Code, Codex, Op', 240329),
    ('mattpocock/skills', 'skills  Skills for Real Engineers. Straight from my .agents directory.', 218560),
    ('multica-ai/andrej-karpathy-skills', "andrej-karpathy-skills  A single CLAUDE.md file to improve Claude Code behavior, derived from Andrej Karpathy's observations on LLM coding pitfalls.", 202822),
    ('n8n-io/n8n', 'n8n  Fair-code workflow automation platform with native AI capabilities. Combine visual building with custom code, self-host or cloud, 400+ integratio', 200807),
    ('ultraworkers/claw-code', 'claw-code  An agent-managed museum exhibit, built in Rust with Gajae-Code / LazyCodex  developed and maintained with no human intervention.', 195054),
    ('avelino/awesome-go', 'awesome-go  A curated list of awesome Go frameworks, libraries and software', 181172),
    ('anthropics/skills', 'skills  Public repository for Agent Skills', 169588),
    ('firecrawl/firecrawl', 'firecrawl  The context API to search, scrape, and interact with the web at scale. ', 167870),
    ('msitarzewski/agency-agents', 'agency-agents  A complete AI agency at your fingertips - From frontend wizards to Reddit community ninjas, from whimsy injectors to reality checkers. ', 145646),
    ('Shubhamsaboo/awesome-llm-apps', 'awesome-llm-apps  100+ AI Agents, Agent Skills and RAG Apps - Free and Open Source.', 132784),
    ('ripienaar/free-for-dev', 'free-for-dev  A list of SaaS, PaaS and IaaS offerings that have free tiers of interest to devops and infradev', 131924),
    ('github/spec-kit', 'spec-kit   Toolkit to help you get started with Spec-Driven Development', 129283),
    ('garrytan/gstack', "gstack  Use Garry Tan's exact Claude Code setup: 23 opinionated tools that serve as CEO, Designer, Eng Manager, Release Manager, Doc Engineer, and QA", 128171),
    ('farion1231/cc-switch', 'cc-switch  A cross-platform desktop All-in-One assistant for Claude Code, Codex, OpenCode, OpenClaw, Grok Build & Hermes Agent. Only official website:', 127460),
    ('nextlevelbuilder/ui-ux-pro-max-skill', 'ui-ux-pro-max-skill  An AI skill that provides design intelligence for building professional UI/UX across multiple platforms.', 117096),
    ('jaywcjlove/awesome-mac', 'awesome-mac   This project is dedicated to collecting high-quality macOS software and organizing them systematically by different categories for easy ', 111152),
    ('browser-use/browser-use', 'browser-use   Make websites accessible for AI agents. Automate tasks online with ease.', 109364),
    ('Graphify-Labs/graphify', 'graphify  Turn any codebase, with its docs, SQL schemas, configs, and PDFs, into a queryable knowledge graph. A /graphify skill for Claude Code, Curso', 106790),
    ('google-gemini/gemini-cli', 'gemini-cli  An open-source AI agent that brings the power of Gemini directly into your terminal.', 106531),
    ('harry0703/MoneyPrinterTurbo', 'MoneyPrinterTurbo   AI Generate HD short videos from a topic or keyword with an automated AI workflow.', 104012),
    ('DietrichGebert/ponytail', 'ponytail  Makes your AI agent think like the laziest senior dev in the room. The best code is the code you never wrote.', 103485),
    ('JuliusBrussee/caveman', 'caveman   why use many token when few token do trick  Claude Code skill that cuts 65% of tokens by talking like caveman', 98420),
    ('microsoft/playwright', 'playwright  Playwright is a framework for Web Testing and Automation. It allows testing Chromium, Firefox and WebKit with a single API.', 94562),
    ('karpathy/autoresearch', 'autoresearch  AI agents running research on single-GPU nanochat training automatically', 93916),
    ('punkpeye/awesome-mcp-servers', 'awesome-mcp-servers  A collection of MCP servers.', 92403),
    ('thedotmack/claude-mem', 'claude-mem  Persistent Context Across Sessions for Every Agent  Captures everything your agent does during sessions, compresses it with AI, and inject', 90849),
    ('ruvnet/RuView', 'RuView   RuView turns commodity WiFi signals into real-time spatial intelligence, vital sign monitoring, and presence detection  all without a single ', 90302),
    ('addyosmani/agent-skills', 'agent-skills  Production-grade engineering skills for AI coding agents.', 87547),
    ('nexu-io/open-design', 'open-design   Best DeepSeek Harness Design Plugin. The open-source Claude Design alternative.  Local-first desktop app.  Your coding agent becomes the', 87063),
    ('laravel/laravel', 'laravel  Laravel is a web application framework with expressive, elegant syntax. Weve already laid the foundation for your next big idea  freeing you ', 84812),
    ('koala73/worldmonitor', 'worldmonitor  Real-time global intelligence dashboard. AI-powered news aggregation, geopolitical monitoring, and infrastructure tracking in a unified ', 82197),
    ('lobehub/lobehub', 'lobehub   LobeHub is your Chief Agent Operator, organizing your agents into 724 operations by hiring, scheduling, and reporting on your entire AI team', 81720),
    ('bytedance/deer-flow', 'deer-flow  An open-source long-horizon SuperAgent harness that researches, codes, and creates. With the help of sandboxes, memories, tools, skill, sub', 80064),
    ('Egonex-AI/Understand-Anything', 'Understand-Anything  Graphs that teach > graphs that impress. Turn any code into an interactive knowledge graph you can explore, search, and ask quest', 79431),
    ('paperclipai/paperclip', 'paperclip  The open-source app everyone uses to manage agents at work', 78343),
    ('Leonxlnx/taste-skill', 'taste-skill  Taste-Skill - gives your AI good taste. stops the AI from generating boring, generic slop', 76897),
    ('shareAI-lab/learn-claude-code', 'learn-claude-code  Bash is all you need - A nano claude codelike agent harness, built from 0 to 1', 74326),
    ('D4Vinci/Scrapling', 'Scrapling   An adaptive Web Scraping framework that handles everything from a single request to a full-scale crawl!', 74248),
    ('josephmisiti/awesome-machine-learning', 'awesome-machine-learning  A curated list of awesome Machine Learning frameworks, libraries and software.', 74046),
    ('vuejs/awesome-vue', 'awesome-vue   A curated list of awesome things related to Vue.js', 73544),
    ('ComposioHQ/awesome-claude-skills', 'awesome-claude-skills  A curated list of awesome Claude Skills, resources, and tools for customizing Claude AI workflows', 72571),
    ('Panniantong/Agent-Reach', 'Agent-Reach  Give your AI agent eyes to see the entire internet. Read & search Twitter, Reddit, YouTube, GitHub, Bilibili, XiaoHongShu  one CLI, zero ', 72083),
    ('openinterpreter/openinterpreter', 'openinterpreter  A coding agent for open models like Kimi K3', 68025),
    ('ruvnet/ruflo', 'ruflo   The original agent meta-harness. Deploy intelligent multi-player swarms, coordinate autonomous workflows, and build conversational AI systems.', 67944),
    ('code-yeongyu/oh-my-openagent', 'oh-my-openagent  omo/lazycodex: The coding agent for tokenmaxxers;the one and only agent harness for complex codebases. For your Codex, for your OpenC', 67926),
    ('bradtraversy/design-resources-for-developers', 'design-resources-for-developers  Curated list of design and UI resources from stock photos, web templates, CSS frameworks, UI libraries, tools and muc', 66660),
    ('cline/cline', 'cline  Autonomous coding agent as an SDK, IDE extension, or CLI assistant.', 66248),
    ('Fission-AI/OpenSpec', 'OpenSpec  Spec-driven development (SDD) for AI coding assistants.', 65020),
    ('sansan0/TrendRadar', 'TrendRadar  AI-driven public opinion & trend monitor with multi-platform aggregation, RSS, and smart alerts.  AI  + RSS AI  + AI  + AI  MCP  AI  Docke', 61488),
    ('upstash/context7', 'context7  Context7 Platform -- Up-to-date code documentation for LLMs and AI code editors', 60810),
    ('hesreallyhim/awesome-claude-code', 'awesome-claude-code  A hand-picked collection of the finest of resources for the most awesome of agents, Claude Code, the undisputed champion of codin', 52393),
    ('VoltAgent/awesome-openclaw-skills', 'awesome-openclaw-skills  The awesome collection of OpenClaw skills. 5,400+ skills filtered and categorized from the official OpenClaw Skills Registry.', 51979),
    ('CherryHQ/cherry-studio', 'cherry-studio  AI productivity studio with smart chat, autonomous agents, and 300+ assistants. Unified access to frontier LLMs', 50527),
    ('ChromeDevTools/chrome-devtools-mcp', 'chrome-devtools-mcp  Chrome DevTools for coding agents', 49233),
    ('sickn33/agentic-awesome-skills', 'agentic-awesome-skills  AAS Core is the local, agent-first control plane for complete catalog discovery, agent-owned selection, stack validation, and ', 45002),
    ('DeusData/codebase-memory-mcp', 'codebase-memory-mcp  High-performance code intelligence MCP server. Indexes codebases into a persistent knowledge graph  average repo in milliseconds.', 39053),
    ('wshobson/agents', 'agents  Multi-harness agentic plugin marketplace for Claude Code, Codex CLI, Cursor, OpenCode, GitHub Copilot, and Gemini CLI', 38843),
    ('bytedance/UI-TARS-desktop', 'UI-TARS-desktop  The Open-Source Multimodal AI Agent Stack: Connecting Cutting-Edge AI Models and Agent Infra', 38601),
    ('github/awesome-copilot', 'awesome-copilot  Community-contributed instructions, agents, skills, and configurations to help you make the most of GitHub Copilot.', 37896),
    ('blader/humanizer', 'humanizer  Agent skill that removes signs of AI-generated writing from text', 35849),
    ('K-Dense-AI/scientific-agent-skills', 'scientific-agent-skills  Turn any AI agent into an AI Scientist. The #1 Agent Skills library for science, used by 170,000+ scientists worldwide. 161 r', 33611),
    ('anthropics/claude-plugins-official', 'claude-plugins-official  Official, Anthropic-managed directory of high quality Claude Code Plugins.', 33555),
    ('github/github-mcp-server', "github-mcp-server  GitHub's official MCP Server", 32281),
    ('openai/codex-plugin-cc', 'codex-plugin-cc  Use Codex from Claude Code to review code or delegate tasks.', 31921),
    ('googleworkspace/cli', 'cli  Google Workspace CLI  one command-line tool for Drive, Gmail, Calendar, Sheets, Docs, Chat, Admin, and more. Dynamically built from Google Discov', 30405),
    ('VoltAgent/awesome-agent-skills', 'awesome-agent-skills  A curated collection of 1000+ agent skills from official dev teams and the community, compatible with Claude Code, Codex, Gemini', 30358),
    ('topoteretes/cognee', 'cognee  Cognee is the open-source AI memory platform for agents. Give your AI agents persistent long-term memory across sessions with a self-hosted kn', 30058),
    ('assafelovic/gpt-researcher', 'gpt-researcher  An autonomous agent that conducts deep research on any data using any LLM providers', 29001),
    ('oraios/serena', 'serena  A powerful MCP toolkit for coding, providing semantic retrieval and editing capabilities - the IDE for your agent', 28078),
    ('jarrodwatts/claude-hud', "claude-hud  A Claude Code plugin that shows what's happening - context usage, active tools, running agents, and todo progress", 27413),
    ('OthmanAdi/planning-with-files', 'planning-with-files  Persistent file-based planning for AI coding agents and long-running tasks. Crash-proof markdown plans, session recovery after /c', 26187),
    ('phuryn/pm-skills', 'pm-skills  PM Skills Marketplace: 100+ agentic skills, commands, and plugins  from discovery to strategy, execution, launch, and growth.', 25292),
    ('JimLiu/baoyu-skills', 'baoyu-skills ', 25031),
    ('alirezarezvani/claude-skills', 'claude-skills  345 Claude Code skills & agent skills & plugins (30+ Agents, 70+ custom commands, 330+ skills, customizable references, scripts)for Cla', 24482),
    ('agentskills/agentskills', 'agentskills  Specification and documentation for Agent Skills', 24321),
    ('EveryInc/compound-engineering-plugin', 'compound-engineering-plugin  Official Compound Engineering plugin for Claude Code, Codex, Cursor, and more', 24300),
    ('modelcontextprotocol/python-sdk', 'python-sdk  The official Python SDK for Model Context Protocol servers and clients', 24016),
    ('activepieces/activepieces', 'activepieces  AI Agents & MCPs & AI Workflow Automation  (~400 MCP servers for AI agents)  AI Automation / AI Agent with MCPs  AI Workflows & AI Agent', 23812),
    ('czlonkowski/n8n-mcp', 'n8n-mcp  A MCP for Claude Desktop / Claude Code / Windsurf / Cursor to build n8n workflows for you', 22700),
    ('titanwings/colleague-skill', "colleague-skill   Skill1.0Transforming cold farewells into warm skills? It's giving rebirth era. Welcome to Digital Life 1.0. ", 22558),
    ('1Panel-dev/MaxKB', 'MaxKB   MaxKB is an open-source platform for building enterprise-grade agents. ', 22514),
    ('alibaba/open-code-review', "open-code-review  Fast, efficient, battle-tested at Alibaba's scale. Hybrid architecture code review tool: deterministic pipelines + LLM Agent, precis", 20553),
    ('mksglu/context-mode', 'context-mode  Context window optimization for AI coding agents. Sandboxes tool output (98% reduction), persists session memory, and enforces routing a', 19891),
    ('modelscope/FunASR', 'FunASR  Open-source speech recognition toolkit for training, inference, streaming ASR, VAD, punctuation, speaker diarization pipelines, and OpenAI-com', 19857),
    ('KKKKhazix/khazix-skills', 'khazix-skills   AI Skills  | Agent Skills: leader, neat-freak , hv-analysis, khazix-writer & more  Claude Code, Codex & 40+ agents', 19708),
    ('nukeop/nuclear', 'nuclear  Streaming music player that finds free music for you', 18287),
    ('kubesphere/kubesphere', 'kubesphere  The container platform tailored for Kubernetes multi-cloud, datacenter, and edge management   ', 17032),
    ('microsoft/mcp-for-beginners', 'mcp-for-beginners  This open-source curriculum introduces the fundamentals of Model Context Protocol (MCP) through real-world, cross-language examples', 16995),
    ('microsoft/SkillOpt', 'SkillOpt  SkillOpt is a text-space optimizer that trains reusable natural-language skills for frozen LLM agents through trajectory-driven edits, valid', 16051),
    ('triggerdotdev/trigger.dev', 'trigger.dev  Trigger.dev  build and deploy fullymanaged AI agents and workflows', 16038),
    ('alibaba/zvec', 'zvec  A lightweight, lightning-fast, in-process vector database', 15446),
    ('wasp-lang/open-saas', 'open-saas  A 100% free modern JS SaaS boilerplate (React, NodeJS, Prisma). Full-featured: Auth (email, google, github, slack, MS), Email sending, Back', 15384),
    ('xpzouying/xiaohongshu-mcp', 'xiaohongshu-mcp  MCP for xiaohongshu.com', 15270),
    ('eigent-ai/eigent', 'eigent  Eigent: The Open Source Cowork Desktop - Local and Free Alternative to Claude Cowork and Codex', 15013),
    ('open-metadata/OpenMetadata', 'OpenMetadata  The Open Context Layer for Data and AI , OpenMetadata is the open platform for building trusted data context and business semantics for ', 14885),
    ('YishenTu/claudian', 'claudian  An Obsidian plugin that embeds Claude Code/Codex as an AI collaborator in your vault', 14798),
    ('yusufkaraaslan/Skill_Seekers', 'Skill_Seekers  Convert documentation websites, GitHub repositories, and PDFs into Claude AI skills with automatic conflict detection', 14768),
    ('wanshuiyin/Auto-claude-code-research-in-sleep', 'Auto-claude-code-research-in-sleep  ARIS  (Auto-Research-In-Sleep)  Lightweight Markdown-only skills for autonomous ML research: cross-model review lo', 14733),
    ('NVIDIA/SkillSpector', 'SkillSpector  Security scanner for AI agent skills. Detect vulnerabilities, malicious patterns, security risks, prompt injection, data exfiltration, a', 14667),
    ('modelcontextprotocol/typescript-sdk', 'typescript-sdk  The official TypeScript SDK for Model Context Protocol servers and clients', 13178),
    ('tt-a1i/archify', 'archify  Agent skill for beautiful, verifiable architecture, workflow, sequence, data-flow, and lifecycle diagramsself-contained HTML with motion and ', 13034),
    ('JoeanAmier/XHS-Downloader', 'XHS-Downloader  XiaoHongShuRedNote/', 12362),
    ('tadata-org/fastapi_mcp', 'fastapi_mcp  Expose your FastAPI endpoints as Model Context Protocol (MCP) tools, with Auth!', 11985),
    ('0xJacky/nginx-ui', 'nginx-ui  Yet another WebUI for Nginx', 11412),
    ('mrexodia/ida-pro-mcp', 'ida-pro-mcp  AI-powered reverse engineering assistant that bridges IDA Pro with language models through MCP.', 11368),
    ('citrolabs/ego-lite', 'ego-lite  The fastest browser for AI agents to run browser automation, built for sharing your logged-in browser state with your AI agents, like Codex ', 11118),
    ('0x4m4/hexstrike-ai', 'hexstrike-ai  HexStrike AI MCP Agents is an advanced MCP server that lets AI agents (Claude, GPT, Copilot, etc.) autonomously run 150+ cybersecurity t', 11046),
    ('AgriciDaniel/claude-obsidian', 'claude-obsidian  Self-organizing AI second brain for Obsidian + Claude Code. Drop any source and Claude reads, links, and files it into one connected ', 10929),
    ('aden-hive/hive', 'hive  Multi-Agent Harness for Production AI', 10914),
    ('OpenByteInc/QuantDinger', 'QuantDinger  AI quantitative trading platform for crypto, stocks, and forex with backtesting, live trading, market data, and multi-agent research.vibe', 10706),
    ('mcp-use/mcp-use', 'mcp-use  The fullstack MCP framework to develop MCP Apps for ChatGPT / Claude & MCP Servers for AI Agents.', 10493),
    ('xinnan-tech/xiaozhi-esp32-server', 'xiaozhi-esp32-server  xiaozhi-esp32ESP32Backend service for xiaozhi-esp32, helps you quickly build an ESP32 device control server.', 10326),
    ('ykdojo/claude-code-tips', 'claude-code-tips  40+ tips for getting the most out of Claude Code, from basics to advanced - includes a custom status line script and Claude Code run', 9669),
    ('awslabs/mcp', 'mcp  Open source MCP Servers for AWS', 9604),
    ('openstatusHQ/openstatus', 'openstatus   Status page with uptime monitoring & API monitoring as code ', 8979),
    ('nexu-io/html-anything', 'html-anything   The agentic HTML editor  your local AI agent writes the HTML, you ship it.  75 Skills  9 Surfaces (magazine  deck  poster  XHS / tweet', 8308),
    ('xixu-me/xget', 'xget  Ultra-high-performance, secure, all-in-one acceleration engine for developer resources', 8200),
    ('firerpa/lamda', 'lamda  Android Full-Stack Device Control Platform: WebRTC/H.264 remote desktop, UI/OCR/image-matching automation, one-click MITM, built-in Frida, prox', 8181),
    ('AgriciDaniel/claude-ads', 'claude-ads  Claude-first paid-media operations skill for Claude Code across 12 ad platforms (Google, Meta, YouTube, LinkedIn, TikTok, Microsoft, Apple', 8091),
    ('jnMetaCode/superpowers-zh', 'superpowers-zh   AI     superpowers116k+  + 6  skills Claude Code / Copilot CLI / Hermes Agent / Cursor / Windsurf / Kiro / Gemini CLI  16  AI ', 7682),
    ('Agents365-ai/drawio-skill', 'drawio-skill  Generate draw.io diagrams from natural language  11 presets (UML, SysML/MBSE, BPMN, network, C4), 36 tools: codebase/CI/infra-to-diagram', 7673),
    ('osaurus-ai/osaurus', 'osaurus  Own your AI. The native macOS harness for AI agents -- any model, persistent memory, autonomous execution, cryptographic identity. Built in S', 7626),
    ('yzfly/Awesome-MCP-ZH', 'Awesome-MCP-ZH  MCP  MCPClaude MCPMCP Servers, MCP Clients', 7561),
    ('refly-ai/refly', 'refly  The first open-source agent skills builder. Define skills by vibe workflow, run on Claude Code, Cursor, Codex & more. Build Clawdbot  APIs for ', 7486),
    ('maximhq/bifrost', 'bifrost  Fastest enterprise AI gateway (50x faster than LiteLLM) with adaptive load balancer, cluster mode, guardrails, 1000+ models support & <100 s ', 7335),
    ('AgentDeskAI/browser-tools-mcp', 'browser-tools-mcp  Monitor browser logs directly from Cursor and other MCP compatible IDEs.', 7292),
    ('firecrawl/firecrawl-mcp-server', 'firecrawl-mcp-server   Official Firecrawl MCP Server - Adds powerful web scraping and search to Cursor, Claude and any other LLM clients.', 7241),
    ('Zipstack/unstract', 'unstract  LLM-Driven Extraction of Unstructured Data  Built for API Deployments & ETL Pipeline Workflows', 7141),
    ('BrowserMCP/mcp', 'mcp  Browser MCP is a Model Context Provider (MCP) server that allows AI applications to control your browser', 6972),
    ('trailofbits/skills', 'skills  Trail of Bits Claude Code skills for security research, vulnerability detection, and audit workflows', 6606),
    ('htmlstreamofficial/preline', 'preline  Preline UI is an open-source set of prebuilt UI components based on the utility-first Tailwind CSS framework.', 6385),
    ('getsentry/XcodeBuildMCP', 'XcodeBuildMCP  A Model Context Protocol (MCP) server and CLI that provides tools for agent use when working on iOS and macOS projects.', 6242),
    ('ThinkInAIXYZ/deepchat', 'deepchat  DeepChat - A smart assistant that connects powerful AI to your personal world', 6223),
    ('ikaijua/Awesome-AITools', 'Awesome-AITools  Collection of AI-related utilities. Welcome to submit pull requests /AIpull requests', 6137),
    ('heilcheng/awesome-agent-skills', 'awesome-agent-skills  Tutorials, Guides and Agent Skills Directories', 6100),
    ('MinishLab/semble', 'semble  Fast and Accurate Code Search for Agents. Uses 99% fewer tokens than grep+read', 5889),
    ('Klavis-AI/klavis', 'klavis  Klavis AI: MCP integration platforms that let AI agents use tools reliably at any scale', 5791),
    ('antfu/skills', "skills  Anthony Fu's curated collection of agent skills.", 5765),
    ('gosom/google-maps-scraper', 'google-maps-scraper  scrape data from Google Maps. Extracts data such as the name, address, phone number, website URL, rating, reviews number, latitud', 5525),
    ('Q00/ouroboros', 'ouroboros  Agent OS: the agent gets smarter on its own. We just hold the line: the grading command and expected result never make it into the success ', 5415),
    ('zhukunpenglinyutong/jetbrains-cc-gui', 'jetbrains-cc-gui  Jetbrains Claude Code and Codex GUI Plugin', 5394),
    ('lemonade-sdk/lemonade', 'lemonade  Lemonade helps users discover and run local AI apps by serving optimized LLMs right from their own GPUs and NPUs. Join our discord: https://', 5374),
    ('breaking-brake/cc-wf-studio', 'cc-wf-studio  CC Workflow Studio', 5353),
    ('0xNyk/awesome-hermes-agent', "awesome-hermes-agent  Independent directory of useful skills, plugins, memory providers, tools, surfaces, and guides for Nous Research's open-source H", 5341),
    ('metalbear-co/mirrord', "mirrord  Run any process, on your machine or in an AI agent's environment, as if it were a pod in your Kubernetes cluster: real env vars, DNS, network", 5263),
]

# The live organism's own standing interests, weights included.
PROFILE = {"agent": 1.0, "skill": 1.0, "memory": 0.9, "mcp": 0.9,
           "evolution": 0.8, "security": 0.8, "sandbox": 0.7,
           "provenance": 0.7, "swarm": 0.6, "epidemiology": 0.6}

# What this owner saw BEFORE today, and at what adoption. Drawn from the
# store's earliest beat, not from the page — a page that defines its own
# norm can never surprise anyone. Targets are excluded by construction,
# and the sample walks down the whole adoption distribution rather than
# its head: a prior built only from famous repos makes every ordinary
# repo look surprising, which is a broken reference class, not a finding.
HISTORY = [
    ('agentic development framework methodology skills software superpowers that works', 271935.0),
    ('andrej andrej-karpathy-skills behavior claude code coding derived file from improve karpathy llm observations pitfalls single', 202332.0),
    ('agency agency-agents agent and checkers community complete deliverables each expert fingertips from frontend injectors ninjas personality processes proven reality reddit specialized whimsy with wizards your', 145361.0),
    ('across building design for intelligence multiple platforms professional provides skill that ui-ux-pro-max-skill', 116576.0),
    ('and any ast claude cli code codebase codex configs cursor deterministic docs edge every explained for gemini graph graphify into its knowledge local parsing pdfs queryable schemas skill sql store turn vector with', 106166.0),
    ('agents automatically autoresearch nanochat research running single-gpu training', 93831.0),
    ('agent alternative app becomes byok claude clis code codex coding cursor dashboards design desktop engine export files gemini html images landing local-first mp4 open-design open-source opencode pages pdf pptx prototypes ', 85832.0),
    ('agents app everyone manage open-source paperclip the uses work', 78085.0),
    ('and awesome awesome-claude-skills claude curated customizing for list resources skills tools workflows', 72461.0),
    ('agent and codebases codex coding complex for harness lazycodex oh-my-openagent omo one only opencode the tokenmaxxers your', 67852.0),
    ('agents also ambidextrous and anthropic awesome awesome-claude-code champion claude code coding collection companions delectable developer finest for from hand-picked have lines most notch pbc plugins resources scintillat', 52285.0),
    ('agents chrome chrome-devtools-mcp coding devtools for', 49142.0),
    ('agent and connecting cutting-edge infra models multimodal open-source stack the ui-tars-desktop', 38586.0),
    ('agent and antigravity any biology chemistry claude code codex compatible covering cursor databases discovery drug for into library medicine open plus ready-to-use science scientific scientific-agent-skills scientist scie', 33468.0),
    ('across agents cognee engine for give graph knowledge long-term memory open-source persistent platform self-hosted sessions the with your', 30011.0),
    ('active agents and claude claude-hud code context happening plugin progress running shows that todo tools usage what', 27381.0),
    ('baoyu-skills', 24979.0),
    ('activepieces agent agents automation for mcp mcps servers with workflow workflows', 23778.0),
    ('agent alibaba anthropic architecture battle-tested built-in code comments compatible deterministic efficient fast hybrid injection line-level llm multi-language npe open-code-review openai pipelines precise review rulese', 20449.0),
    ('agents and build deploy dev fullymanaged trigger workflows', 16012.0),
    ('agents and assistants building business context data for humans layer open openmetadata platform semantics the trusted', 14875.0),
    ('agent and archify architecture beautiful crisp data-flow diagramsself-contained export for html lifecycle motion sequence skill verifiable with workflow', 12218.0),
    ('ai-trader ai-trading and backtesting crypto data for forex live market multi-agent platform quantdinger quantitative research stocks trading trading-agents vibe-trading with', 10646.0),
    ('advanced also and basics claude claude-code-tips code container custom dev everyday for from getting includes itself line most out plugin running script skills status the tips workflows', 9614.0),
    ('account across amazon and apple audits capability-gated changes claude claude-ads claude-first code deterministic for google json linkedin meta microsoft operations paid-media pinterest platforms reddit reports scoring s', 8042.0),
    ('agents any autonomous built cryptographic execution for fully harness identity macos memory model native offline open osaurus own persistent source swift the your', 7614.0),
    ('agent and awesome-agent-skills directories guides skills tutorials', 6094.0),
    ('agent anthony collection curated skills', 5760.0),
    ('agent any cluster dns env environment kubernetes machine mirrord network pod process real run traffic vars were your', 5261.0),
    ('agent agents and buildwithclaude claude code collections commands desktop extend find hooks hub marketplace openclaw plugins sdk single skills', 3292.0),
]

# The literal task, deliberately orthogonal to what matters to the owner.
TASK = ("List the three highest-starred repositories on this page and their star counts.")
TASK_GOAL = ["stars", "repository"]

# Ground truth, hand-labelled by the steward.
#   core   — genuinely this owner's trade: agent-capability infrastructure
#            touching safety, memory, provenance or the skill supply chain
#   target — core AND far below the page's adoption distribution
LABELS = {
    "core": {
        'DeusData/codebase-memory-mcp',
        'NVIDIA/SkillSpector',
        'agentskills/agentskills',
        'mksglu/context-mode',
        'osaurus-ai/osaurus',
        'thedotmack/claude-mem',
        'topoteretes/cognee',
        'trailofbits/skills',
    },
    "adjacent": set(),
    "target": {
        'NVIDIA/SkillSpector',
        'trailofbits/skills',
    },
}

PAGE = "\n".join(f"{locus} | {text} | {stars} stars" for locus, text, stars in WILD)
