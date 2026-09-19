# Documentación de HappyRobot (docs.happyrobot.ai)

Copia completa en Markdown de **381 páginas** de [docs.happyrobot.ai](https://docs.happyrobot.ai), descargada el 18/09/2026 desde la fuente oficial (sitio protegido con código de acceso).

**Las carpetas reproducen el menú de la web**: una carpeta por pestaña (Developer Guide, Developer Tools, API Reference, Changelog) y, dentro, una carpeta por cada apartado del sidebar. Los prefijos numéricos mantienen el mismo orden que el sitio.

- Cada carpeta tiene un `README.md` con su índice.
- Cada página conserva su frontmatter (`title`, `description`) y el enlace a la URL original.
- Los enlaces entre páginas están reescritos a rutas locales: se navega sin conexión.
- `recursos/openapi-platform-v2.json`: especificación OpenAPI completa de la API v2.
- `recursos/llms.txt`: índice oficial de páginas publicado por el sitio.
- `assets-img/`: imágenes de la documentación.

## Estructura

- [Developer Guide](01-Developer-Guide/README.md) (`01-Developer-Guide/`, 133 páginas)
  - [Get Started](01-Developer-Guide/01-Get-Started/README.md) (`01-Get-Started/`, 5 páginas)
  - [Workflows](01-Developer-Guide/02-Workflows/README.md) (`02-Workflows/`, 10 páginas)
  - [Core Nodes](01-Developer-Guide/03-Core-Nodes/README.md) (`03-Core-Nodes/`, 12 páginas)
  - [Tools](01-Developer-Guide/04-Tools/README.md) (`04-Tools/`, 6 páginas)
  - [Voice Agents](01-Developer-Guide/05-Voice-Agents/README.md) (`05-Voice-Agents/`, 8 páginas)
  - [Text Agents](01-Developer-Guide/06-Text-Agents/README.md) (`06-Text-Agents/`, 7 páginas)
  - [Apps](01-Developer-Guide/07-Apps/README.md) (`07-Apps/`, 7 páginas)
  - [Twin](01-Developer-Guide/08-Twin/README.md) (`08-Twin/`, 6 páginas)
  - [Runs and Monitoring](01-Developer-Guide/09-Runs-and-Monitoring/README.md) (`09-Runs-and-Monitoring/`, 5 páginas)
  - [Experiments](01-Developer-Guide/10-Experiments/README.md) (`10-Experiments/`, 5 páginas)
  - [Quality and Evaluation](01-Developer-Guide/11-Quality-and-Evaluation/README.md) (`11-Quality-and-Evaluation/`, 8 páginas)
  - [Analytics](01-Developer-Guide/12-Analytics/README.md) (`12-Analytics/`, 3 páginas)
  - [Contacts](01-Developer-Guide/13-Contacts/README.md) (`13-Contacts/`, 4 páginas)
  - [Assets](01-Developer-Guide/14-Assets/README.md) (`14-Assets/`, 5 páginas)
  - [Integrations](01-Developer-Guide/15-Integrations/README.md) (`15-Integrations/`, 30 páginas)
    - [Communication](01-Developer-Guide/15-Integrations/04-Communication/README.md) (`04-Communication/`, 10 páginas)
    - [Business Systems](01-Developer-Guide/15-Integrations/05-Business-Systems/README.md) (`05-Business-Systems/`, 9 páginas)
    - [Data and Storage](01-Developer-Guide/15-Integrations/06-Data-and-Storage/README.md) (`06-Data-and-Storage/`, 8 páginas)
  - [Account and Settings](01-Developer-Guide/16-Account-and-Settings/README.md) (`16-Account-and-Settings/`, 11 páginas)
  - [Compliance](01-Developer-Guide/17-Compliance/README.md) (`17-Compliance/`, 1 páginas)
- [Developer Tools](02-Developer-Tools/README.md) (`02-Developer-Tools/`, 17 páginas)
  - [MCP](02-Developer-Tools/01-MCP/README.md) (`01-MCP/`, 4 páginas)
  - [TypeScript SDK](02-Developer-Tools/02-TypeScript-SDK/README.md) (`02-TypeScript-SDK/`, 13 páginas)
- [API Reference](03-API-Reference/README.md) (`03-API-Reference/`, 230 páginas)
  - [Platform V2 API](03-API-Reference/01-Platform-V2-API/README.md) (`01-Platform-V2-API/`, 224 páginas)
    - [API Keys](03-API-Reference/01-Platform-V2-API/01-API-Keys/README.md) (`01-API-Keys/`, 1 páginas)
    - [Runs](03-API-Reference/01-Platform-V2-API/02-Runs/README.md) (`02-Runs/`, 10 páginas)
    - [Billing](03-API-Reference/01-Platform-V2-API/03-Billing/README.md) (`03-Billing/`, 4 páginas)
    - [Use Cases](03-API-Reference/01-Platform-V2-API/04-Use-Cases/README.md) (`04-Use-Cases/`, 1 páginas)
    - [Contacts](03-API-Reference/01-Platform-V2-API/05-Contacts/README.md) (`05-Contacts/`, 5 páginas)
    - [Knowledge Bases](03-API-Reference/01-Platform-V2-API/06-Knowledge-Bases/README.md) (`06-Knowledge-Bases/`, 7 páginas)
    - [Workflows](03-API-Reference/01-Platform-V2-API/07-Workflows/README.md) (`07-Workflows/`, 14 páginas)
    - [Workflow Variables](03-API-Reference/01-Platform-V2-API/08-Workflow-Variables/README.md) (`08-Workflow-Variables/`, 4 páginas)
    - [Audits](03-API-Reference/01-Platform-V2-API/09-Audits/README.md) (`09-Audits/`, 10 páginas)
    - [Issues](03-API-Reference/01-Platform-V2-API/10-Issues/README.md) (`10-Issues/`, 2 páginas)
    - [Apps](03-API-Reference/01-Platform-V2-API/11-Apps/README.md) (`11-Apps/`, 1 páginas)
    - [Versions](03-API-Reference/01-Platform-V2-API/12-Versions/README.md) (`12-Versions/`, 22 páginas)
    - [Workflow Folders](03-API-Reference/01-Platform-V2-API/13-Workflow-Folders/README.md) (`13-Workflow-Folders/`, 5 páginas)
    - [Phone Numbers](03-API-Reference/01-Platform-V2-API/14-Phone-Numbers/README.md) (`14-Phone-Numbers/`, 12 páginas)
    - [SIP Trunks](03-API-Reference/01-Platform-V2-API/15-SIP-Trunks/README.md) (`15-SIP-Trunks/`, 7 páginas)
    - [Integrations](03-API-Reference/01-Platform-V2-API/16-Integrations/README.md) (`16-Integrations/`, 5 páginas)
    - [Integration Resources](03-API-Reference/01-Platform-V2-API/17-Integration-Resources/README.md) (`17-Integration-Resources/`, 15 páginas)
    - [Sessions](03-API-Reference/01-Platform-V2-API/18-Sessions/README.md) (`18-Sessions/`, 4 páginas)
    - [Messages](03-API-Reference/01-Platform-V2-API/19-Messages/README.md) (`19-Messages/`, 2 páginas)
    - [Organization](03-API-Reference/01-Platform-V2-API/20-Organization/README.md) (`20-Organization/`, 4 páginas)
    - [MCP Servers](03-API-Reference/01-Platform-V2-API/21-MCP-Servers/README.md) (`21-MCP-Servers/`, 4 páginas)
    - [Northstars](03-API-Reference/01-Platform-V2-API/22-Northstars/README.md) (`22-Northstars/`, 13 páginas)
    - [Custom Evals](03-API-Reference/01-Platform-V2-API/23-Custom-Evals/README.md) (`23-Custom-Evals/`, 11 páginas)
    - [Adversarial Tests](03-API-Reference/01-Platform-V2-API/24-Adversarial-Tests/README.md) (`24-Adversarial-Tests/`, 6 páginas)
    - [Adversarial Suites](03-API-Reference/01-Platform-V2-API/25-Adversarial-Suites/README.md) (`25-Adversarial-Suites/`, 5 páginas)
    - [E2E Scenarios](03-API-Reference/01-Platform-V2-API/26-E2E-Scenarios/README.md) (`26-E2E-Scenarios/`, 7 páginas)
    - [Test Suites](03-API-Reference/01-Platform-V2-API/27-Test-Suites/README.md) (`27-Test-Suites/`, 13 páginas)
    - [Events](03-API-Reference/01-Platform-V2-API/28-Events/README.md) (`28-Events/`, 1 páginas)
    - [Twin](03-API-Reference/01-Platform-V2-API/29-Twin/README.md) (`29-Twin/`, 10 páginas)
    - [Chat](03-API-Reference/01-Platform-V2-API/30-Chat/README.md) (`30-Chat/`, 7 páginas)
    - [Realtime](03-API-Reference/01-Platform-V2-API/31-Realtime/README.md) (`31-Realtime/`, 1 páginas)
    - [Artifacts](03-API-Reference/01-Platform-V2-API/32-Artifacts/README.md) (`32-Artifacts/`, 2 páginas)
    - [Voice](03-API-Reference/01-Platform-V2-API/33-Voice/README.md) (`33-Voice/`, 2 páginas)
    - [Signals](03-API-Reference/01-Platform-V2-API/34-Signals/README.md) (`34-Signals/`, 7 páginas)
  - [Bridge API](03-API-Reference/02-Bridge-API/README.md) (`02-Bridge-API/`, 6 páginas)
    - [Call HappyRobot API](03-API-Reference/02-Bridge-API/01-Call-HappyRobot-API/README.md) (`01-Call-HappyRobot-API/`, 2 páginas)
    - [HappyRobot calls your API](03-API-Reference/02-Bridge-API/02-HappyRobot-calls-your-API/README.md) (`02-HappyRobot-calls-your-API/`, 4 páginas)
- [Changelog](04-Changelog/README.md) (`04-Changelog/`, 1 páginas)
  - [Changelog](04-Changelog/01-Changelog/README.md) (`01-Changelog/`, 1 páginas)

## Índice completo

**Developer Guide**


  **Get Started**

  - [Introduction](01-Developer-Guide/01-Get-Started/01-Introduction.md)
  - [Platform overview](01-Developer-Guide/01-Get-Started/02-Platform-overview.md) — Architecture and key concepts of the HappyRobot platform
  - [Quickstart](01-Developer-Guide/01-Get-Started/03-Quickstart.md) — Build an outbound voice agent workflow and trigger it via API in 15 minutes
  - [Navigating the platform](01-Developer-Guide/01-Get-Started/04-Navigating-the-platform.md) — Find your way around the sidebar, tabs, and command menu
  - [Claude Desktop](01-Developer-Guide/01-Get-Started/05-Claude-Desktop.md) — Use Claude Desktop to build and manage HappyRobot workflows conversationally

  **Workflows**

  - [Workflows Overview](01-Developer-Guide/02-Workflows/01-Workflows-Overview.md) — Introduction to HappyRobot workflows
  - [Creating a Workflow](01-Developer-Guide/02-Workflows/02-Creating-a-Workflow.md) — Step-by-step guide to building your first workflow
  - [Frontal AI assistant](01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md) — Use the AI assistant to build and edit workflows through conversation
  - [Node Types](01-Developer-Guide/02-Workflows/04-Node-Types.md) — Understanding the different node types available in workflows
  - [Triggers](01-Developer-Guide/02-Workflows/05-Triggers.md) — How to configure workflow triggers
  - [Signals](01-Developer-Guide/02-Workflows/06-Signals.md) — Wake running agents with real-time, event-driven messages from your systems
  - [Variables](01-Developer-Guide/02-Workflows/07-Variables.md) — Using variables and dynamic data in workflows
  - [Versions and Publishing](01-Developer-Guide/02-Workflows/08-Versions-and-Publishing.md) — Managing workflow versions and publishing changes
  - [Environments](01-Developer-Guide/02-Workflows/09-Environments.md) — Configuring development, staging, and production environments
  - [Discussions](01-Developer-Guide/02-Workflows/10-Discussions.md) — Leave comments on workflow nodes and collaborate with your team on the canvas

  **Core Nodes**

  - [Core Nodes Overview](01-Developer-Guide/03-Core-Nodes/01-Core-Nodes-Overview.md) — Built-in workflow nodes that don't require a third-party integration
  - [AI Extract](01-Developer-Guide/03-Core-Nodes/02-AI-Extract.md) — Extract structured data from unstructured text using AI
  - [AI Classify](01-Developer-Guide/03-Core-Nodes/03-AI-Classify.md) — Classify text into predefined categories using AI
  - [AI Generate](01-Developer-Guide/03-Core-Nodes/04-AI-Generate.md) — Generate text content using AI
  - [Custom Code](01-Developer-Guide/03-Core-Nodes/05-Custom-Code.md) — Run Python code within your workflow
  - [Webhook](01-Developer-Guide/03-Core-Nodes/06-Webhook.md) — Send and receive HTTP requests in workflows
  - [Schedule](01-Developer-Guide/03-Core-Nodes/07-Schedule.md) — Add delays and timing control to workflows
  - [File Operations](01-Developer-Guide/03-Core-Nodes/08-File-Operations.md) — Upload, parse, search, and extract text from files in workflows
  - [Conditionals](01-Developer-Guide/03-Core-Nodes/09-Conditionals.md) — Add branching logic to your workflows
  - [Loops](01-Developer-Guide/03-Core-Nodes/10-Loops.md) — Iterate over collections or repeat actions a fixed number of times
  - [Module Change](01-Developer-Guide/03-Core-Nodes/11-Module-Change.md) — Jump to a different module within a workflow
  - [Call Workflow](01-Developer-Guide/03-Core-Nodes/12-Call-Workflow.md) — Invoke another workflow and wait for its response, or start it and continue

  **Tools**

  - [Tools Overview](01-Developer-Guide/04-Tools/01-Tools-Overview.md) — Introduction to tools in HappyRobot
  - [Creating Tools](01-Developer-Guide/04-Tools/02-Creating-Tools.md) — How to create and configure tools for your agents
  - [Tool Call Result](01-Developer-Guide/04-Tools/03-Tool-Call-Result.md) — Preview and choose the payload a tool returns to the agent
  - [Built-in Tools](01-Developer-Guide/04-Tools/04-Built-in-Tools.md) — Default tools that come with voice and text agents
  - [MCP Tools](01-Developer-Guide/04-Tools/05-MCP-Tools.md) — Import tools from external Model Context Protocol servers into your workflows
  - [MCP Server Setup](01-Developer-Guide/04-Tools/06-MCP-Server-Setup.md) — Connect external MCP servers to discover and use their tools in your workflows

  **Voice Agents**

  - [Voice Agents Overview](01-Developer-Guide/05-Voice-Agents/01-Voice-Agents-Overview.md) — Introduction to voice AI agents
  - [Inbound Calls](01-Developer-Guide/05-Voice-Agents/02-Inbound-Calls.md) — Configure agents to handle incoming phone calls
  - [Outbound Calls](01-Developer-Guide/05-Voice-Agents/03-Outbound-Calls.md) — Set up automated outbound calling campaigns
  - [Outbound with Callback](01-Developer-Guide/05-Voice-Agents/04-Outbound-with-Callback.md) — Handle callbacks from missed outbound calls
  - [STT, TTS, and LLM Configuration](01-Developer-Guide/05-Voice-Agents/05-STT-TTS-and-LLM-Configuration.md) — Configure speech-to-text, text-to-speech, and language model settings
  - [Prompts and Tools](01-Developer-Guide/05-Voice-Agents/06-Prompts-and-Tools.md) — Write prompts and attach tools to voice agents
  - [Forward call](01-Developer-Guide/05-Voice-Agents/07-Forward-call.md) — Send an incoming call straight to a phone number with no agent on the line
  - [Transfer popup](01-Developer-Guide/05-Voice-Agents/08-Transfer-popup.md) — Send a context popup to human agents when transferring a call

  **Text Agents**

  - [Text Agents Overview](01-Developer-Guide/06-Text-Agents/01-Text-Agents-Overview.md) — Introduction to text-based AI agents
  - [SMS](01-Developer-Guide/06-Text-Agents/02-SMS.md) — Deploy text agents over SMS
  - [WhatsApp](01-Developer-Guide/06-Text-Agents/03-WhatsApp.md) — Deploy text agents on WhatsApp
  - [Email](01-Developer-Guide/06-Text-Agents/04-Email.md) — Deploy text agents for email conversations
  - [Chatbot](01-Developer-Guide/06-Text-Agents/05-Chatbot.md) — Embed a chatbot widget on your website
  - [Microsoft Teams](01-Developer-Guide/06-Text-Agents/06-Microsoft-Teams.md) — Deploy text agents in Microsoft Teams chats and channels
  - [Slack](01-Developer-Guide/06-Text-Agents/07-Slack.md) — Deploy text agents in Slack channels and direct messages

  **Apps**

  - [Apps Overview](01-Developer-Guide/07-Apps/01-Apps-Overview.md) — Build, edit, and deploy custom web applications inside HappyRobot
  - [Creating an App](01-Developer-Guide/07-Apps/02-Creating-an-App.md) — Start a new app from a template or import an existing GitHub repository
  - [Sandbox Editor](01-Developer-Guide/07-Apps/03-Sandbox-Editor.md) — Edit your app with a live preview and an AI coding agent
  - [Local development](01-Developer-Guide/07-Apps/04-Local-development.md) — Clone an app and run it against your HappyRobot workspace
  - [Deploying](01-Developer-Guide/07-Apps/05-Deploying.md) — Push your app live and watch the build run
  - [Build History and Versioning](01-Developer-Guide/07-Apps/06-Build-History-and-Versioning.md) — Browse past deployments, inspect logs, and roll back via Git
  - [Environment Variables](01-Developer-Guide/07-Apps/07-Environment-Variables.md) — Configure secrets and runtime values for your app

  **Twin**

  - [Twin Overview](01-Developer-Guide/08-Twin/01-Twin-Overview.md) — A managed PostgreSQL database for your organization, built into the platform
  - [Managing Tables](01-Developer-Guide/08-Twin/02-Managing-Tables.md) — Create tables, columns, foreign keys, and views in your Twin database
  - [Polling Tables](01-Developer-Guide/08-Twin/03-Polling-Tables.md) — Keep a Twin table automatically synced from an external HTTP endpoint
  - [Workflow Run Dumps](01-Developer-Guide/08-Twin/04-Workflow-Run-Dumps.md) — Automatically persist workflow run outputs into a Twin table
  - [SQL Console and Capacity](01-Developer-Guide/08-Twin/05-SQL-Console-and-Capacity.md) — Run SQL directly and configure your Twin database's instance class, storage, and gateway
  - [Using Twin in Apps](01-Developer-Guide/08-Twin/06-Using-Twin-in-Apps.md) — Consume Twin data from a HappyRobot App, and version your schema safely alongside App deploys

  **Runs and Monitoring**

  - [Runs Overview](01-Developer-Guide/09-Runs-and-Monitoring/01-Runs-Overview.md) — Monitor and manage workflow executions
  - [Run Statuses](01-Developer-Guide/09-Runs-and-Monitoring/02-Run-Statuses.md) — Understanding run lifecycle and status codes
  - [Transcripts and Messages](01-Developer-Guide/09-Runs-and-Monitoring/03-Transcripts-and-Messages.md) — View conversation transcripts and message history
  - [Recordings](01-Developer-Guide/09-Runs-and-Monitoring/04-Recordings.md) — Access and manage call recordings
  - [Annotations](01-Developer-Guide/09-Runs-and-Monitoring/05-Annotations.md) — Add annotations and notes to runs

  **Experiments**

  - [Experiments](01-Developer-Guide/10-Experiments/01-Experiments.md) — Run controlled A/B tests to compare workflow versions and configuration changes with statistical rigor
  - [Creating experiments](01-Developer-Guide/10-Experiments/02-Creating-experiments.md) — Set up an A/B test with variants, traffic split, and metrics
  - [Experiment metrics](01-Developer-Guide/10-Experiments/03-Experiment-metrics.md) — Default and custom metrics available for measuring experiment outcomes
  - [Analyzing results](01-Developer-Guide/10-Experiments/04-Analyzing-results.md) — Read your experiment dashboard and make data-driven decisions
  - [A/B testing guide](01-Developer-Guide/10-Experiments/05-A-B-testing-guide.md) — A practical guide to running reliable experiments, from core statistics to decision-making patterns

  **Quality and Evaluation**

  - [Quality and evaluation overview](01-Developer-Guide/11-Quality-and-Evaluation/01-Quality-and-evaluation-overview.md) — Define quality standards, automatically audit runs, and continuously improve agent behavior
  - [Northstars](01-Developer-Guide/11-Quality-and-Evaluation/02-Northstars.md) — Define behavioral quality criteria for your agents
  - [Automated audits](01-Developer-Guide/11-Quality-and-Evaluation/03-Automated-audits.md) — Every run is automatically evaluated against your northstars
  - [Audio audits](01-Developer-Guide/11-Quality-and-Evaluation/04-Audio-audits.md) — Analyze transcription accuracy, conversation quality, and acoustic metrics for voice agent calls
  - [Issues](01-Developer-Guide/11-Quality-and-Evaluation/05-Issues.md) — Track and resolve quality problems surfaced by audits and flags
  - [Custom tests](01-Developer-Guide/11-Quality-and-Evaluation/06-Custom-tests.md) — Create test cases with expected conversation flows and tool calls
  - [Adversarial tests](01-Developer-Guide/11-Quality-and-Evaluation/07-Adversarial-tests.md) — Simulate a user challenging an agent across a full conversation and grade the result against northstars
  - [Test suites](01-Developer-Guide/11-Quality-and-Evaluation/08-Test-suites.md) — Group prompt and adversarial tests into suites and run them together against a workflow version

  **Analytics**

  - [Analytics Overview](01-Developer-Guide/12-Analytics/01-Analytics-Overview.md) — Track performance and gain insights
  - [KPI Dashboard](01-Developer-Guide/12-Analytics/02-KPI-Dashboard.md) — Monitor key performance indicators
  - [Workflow Metrics](01-Developer-Guide/12-Analytics/03-Workflow-Metrics.md) — Analyze workflow-level performance data

  **Contacts**

  - [Contacts Overview](01-Developer-Guide/13-Contacts/01-Contacts-Overview.md) — Manage your contact database
  - [Managing Contacts](01-Developer-Guide/13-Contacts/02-Managing-Contacts.md) — Create, update, and organize contacts
  - [Interaction History](01-Developer-Guide/13-Contacts/03-Interaction-History.md) — View past interactions with contacts
  - [Memories](01-Developer-Guide/13-Contacts/04-Memories.md) — How agents remember context across conversations

  **Assets**

  - [Knowledge Bases](01-Developer-Guide/14-Assets/01-Knowledge-Bases.md) — Upload and manage documents for agent reference
  - [Components](01-Developer-Guide/14-Assets/02-Components.md) — Reusable prompt components and templates
  - [Telephony](01-Developer-Guide/14-Assets/03-Telephony.md) — Manage phone numbers, SIP trunks, and audio assets
  - [Voices](01-Developer-Guide/14-Assets/04-Voices.md) — Browse and preview text-to-speech voices for your agents
  - [Models](01-Developer-Guide/14-Assets/05-Models.md) — Reference for every language model available in HappyRobot workflows, voice agents, and text agents

  **Integrations**

  - [Integrations Overview](01-Developer-Guide/15-Integrations/01-Integrations-Overview.md) — Connect HappyRobot to your existing tools and services
  - [Credentials](01-Developer-Guide/15-Integrations/02-Credentials.md) — Manage authentication for your integrations
  - [Integrations marketplace](01-Developer-Guide/15-Integrations/03-Integrations-marketplace.md) — Browse and connect hundreds of integrations through a single connection flow

    **Communication**

    - [Gmail](01-Developer-Guide/15-Integrations/04-Communication/01-Gmail.md) — Send and receive emails with Gmail
    - [Outlook](01-Developer-Guide/15-Integrations/04-Communication/02-Outlook.md) — Send and receive emails with Microsoft Outlook
    - [Slack](01-Developer-Guide/15-Integrations/04-Communication/03-Slack.md) — Send messages and receive events from Slack
    - [Microsoft Teams](01-Developer-Guide/15-Integrations/04-Communication/04-Microsoft-Teams.md) — Send messages and monitor channels in Microsoft Teams
    - [Genesys Audio Connector](01-Developer-Guide/15-Integrations/04-Communication/05-Genesys-Audio-Connector.md) — Stream Genesys Cloud calls to a HappyRobot voice agent over WebSocket
    - [Twilio SMS](01-Developer-Guide/15-Integrations/04-Communication/06-Twilio-SMS.md) — Send and receive SMS messages via Twilio
    - [Telnyx SMS](01-Developer-Guide/15-Integrations/04-Communication/07-Telnyx-SMS.md) — Send and receive SMS messages via Telnyx
    - [WhatsApp](01-Developer-Guide/15-Integrations/04-Communication/08-WhatsApp.md) — Connect to WhatsApp Business API
    - [SendGrid](01-Developer-Guide/15-Integrations/04-Communication/09-SendGrid.md) — Send transactional emails and run direct email agents via SendGrid
    - [HappyRobot Email](01-Developer-Guide/15-Integrations/04-Communication/10-HappyRobot-Email.md) — Use HappyRobot's built-in email service

    **Business Systems**

    - [McLeod TMS](01-Developer-Guide/15-Integrations/05-Business-Systems/01-McLeod-TMS.md) — Integrate with McLeod LoadMaster TMS
    - [Turvo TMS](01-Developer-Guide/15-Integrations/05-Business-Systems/02-Turvo-TMS.md) — Integrate with Turvo TMS
    - [Mastery TMS](01-Developer-Guide/15-Integrations/05-Business-Systems/03-Mastery-TMS.md) — Retrieve loads and carriers, submit offers, book carriers, and post tracking updates in Mastery
    - [TPro](01-Developer-Guide/15-Integrations/05-Business-Systems/04-TPro.md) — Integrate with TPro TMS
    - [3PL](01-Developer-Guide/15-Integrations/05-Business-Systems/05-3PL.md) — Integrate with 3PL Warehouse Manager
    - [Custom TMS](01-Developer-Guide/15-Integrations/05-Business-Systems/06-Custom-TMS.md) — Connect to any TMS with a custom integration
    - [Broker App](01-Developer-Guide/15-Integrations/05-Business-Systems/07-Broker-App.md) — Use the HappyRobot Broker App integration
    - [CXone](01-Developer-Guide/15-Integrations/05-Business-Systems/08-CXone.md) — Integrate with NICE CXone contact center platform
    - [Richpanel](01-Developer-Guide/15-Integrations/05-Business-Systems/09-Richpanel.md) — Escalate text agent conversations to human agents in Richpanel

    **Data and Storage**

    - [Google Sheets](01-Developer-Guide/15-Integrations/06-Data-and-Storage/01-Google-Sheets.md) — Read and write data to Google Sheets
    - [Snowflake](01-Developer-Guide/15-Integrations/06-Data-and-Storage/02-Snowflake.md) — Query data from your Snowflake data warehouse
    - [Redis](01-Developer-Guide/15-Integrations/06-Data-and-Storage/03-Redis.md) — Use Redis for caching and key-value storage
    - [Kafka](01-Developer-Guide/15-Integrations/06-Data-and-Storage/04-Kafka.md) — Publish messages to Apache Kafka topics from a workflow
    - [Google Maps](01-Developer-Guide/15-Integrations/06-Data-and-Storage/05-Google-Maps.md) — Geographic utilities for your workflows
    - [Salesforce](01-Developer-Guide/15-Integrations/06-Data-and-Storage/06-Salesforce.md) — Query, create, update, and delete Salesforce CRM records from workflows
    - [Twin database](01-Developer-Guide/15-Integrations/06-Data-and-Storage/07-Twin-database.md) — Read from and write to your organization's managed database
    - [AWS](01-Developer-Guide/15-Integrations/06-Data-and-Storage/08-AWS.md) — Generate presigned S3 URLs for secure, time-limited object access

  **Account and Settings**

  - [Organization](01-Developer-Guide/16-Account-and-Settings/01-Organization.md) — Manage your organization settings
  - [Members and Access](01-Developer-Guide/16-Account-and-Settings/02-Members-and-Access.md) — Manage members, invitations, roles, and access grants
  - [Custom Roles](01-Developer-Guide/16-Account-and-Settings/03-Custom-Roles.md) — Create reusable roles from HappyRobot access actions
  - [Scope Tags](01-Developer-Guide/16-Account-and-Settings/04-Scope-Tags.md) — Organize resources and limit roles to matching tagged resources
  - [SSO Access](01-Developer-Guide/16-Account-and-Settings/05-SSO-Access.md) — Configure SSO login and resolve identity-provider groups into access grants
  - [API Keys](01-Developer-Guide/16-Account-and-Settings/06-API-Keys.md) — Generate and manage API keys for the HappyRobot API
  - [Bring your own keys](01-Developer-Guide/16-Account-and-Settings/07-Bring-your-own-keys.md) — Run HappyRobot AI features on your organization's own OpenAI, Anthropic, or Gemini credentials
  - [Environment Variables](01-Developer-Guide/16-Account-and-Settings/08-Environment-Variables.md) — Configure environment variables for your workflows
  - [Usage and Billing](01-Developer-Guide/16-Account-and-Settings/09-Usage-and-Billing.md) — Monitor your organization's usage and credit consumption
  - [Workflow Settings](01-Developer-Guide/16-Account-and-Settings/10-Workflow-Settings.md) — Configure settings for individual workflows
  - [SLA and service status](01-Developer-Guide/16-Account-and-Settings/11-SLA-and-service-status.md) — Review measured platform availability, live incidents, and how uptime is calculated

  **Compliance**

  - [EU AI Act and GDPR requirements](01-Developer-Guide/17-Compliance/01-EU-AI-Act-and-GDPR-requirements.md) — Disclosure and recording requirements for agents that interact with people in the EU

**Developer Tools**


  **MCP**

  - [MCP servers](02-Developer-Tools/01-MCP/01-MCP-servers.md) — Connect to HappyRobot from AI coding assistants, Claude Desktop, or your own services
  - [Frontal MCP](02-Developer-Tools/01-MCP/02-Frontal-MCP.md) — Build and edit workflows through conversation from your own MCP client
  - [Workflows MCP](02-Developer-Tools/01-MCP/03-Workflows-MCP.md) — Available tools and prompts for the Workflows MCP server
  - [Twin MCP](02-Developer-Tools/01-MCP/04-Twin-MCP.md) — Available tools for the Twin database MCP server

  **TypeScript SDK**

  - [TypeScript SDK](02-Developer-Tools/02-TypeScript-SDK/01-TypeScript-SDK.md) — Install and configure the HappyRobot TypeScript SDK to manage workflows, voice agents, and integrations programmatically
  - [Quickstart](02-Developer-Tools/02-TypeScript-SDK/02-Quickstart.md) — Trigger a workflow run and read the results in under five minutes
  - [Voice agent tutorial](02-Developer-Tools/02-TypeScript-SDK/03-Voice-agent-tutorial.md) — Create a voice agent, trigger an outbound call, and stream live messages with the TypeScript SDK
  - [Voice call tutorial](02-Developer-Tools/02-TypeScript-SDK/04-Voice-call-tutorial.md) — Build a browser voice call UI with the TypeScript SDK using React, LiveKit, and Express
  - [Chatbot tutorial](02-Developer-Tools/02-TypeScript-SDK/05-Chatbot-tutorial.md) — Build a custom chat UI with the TypeScript SDK using React and Express
  - [Workflows](02-Developer-Tools/02-TypeScript-SDK/06-Workflows.md) — Manage workflows, versions, nodes, runs, and folders with the TypeScript SDK
  - [Sessions and messages](02-Developer-Tools/02-TypeScript-SDK/07-Sessions-and-messages.md) — Read session details, fetch messages, and stream live conversation events with the TypeScript SDK
  - [Telephony](02-Developer-Tools/02-TypeScript-SDK/08-Telephony.md) — Manage phone numbers and SIP trunks with the TypeScript SDK
  - [Integrations](02-Developer-Tools/02-TypeScript-SDK/09-Integrations.md) — Discover integrations and access Google Sheets, Slack, Teams, Twilio SMS, and WhatsApp sub-resources
  - [Resources](02-Developer-Tools/02-TypeScript-SDK/10-Resources.md) — Manage contacts, knowledge bases, variables, MCP servers, apps, billing, voices, and API keys
  - [Quality and testing](02-Developer-Tools/02-TypeScript-SDK/11-Quality-and-testing.md) — Run test suites and adversarial tests, manage northstar criteria, custom evals, issues, and audit remarks
  - [Helpers](02-Developer-Tools/02-TypeScript-SDK/12-Helpers.md) — Use pagination patterns and high-level helper utilities in the TypeScript SDK
  - [Error handling](02-Developer-Tools/02-TypeScript-SDK/13-Error-handling.md) — Handle errors and configure retry behavior in the TypeScript SDK

**API Reference**


  **Platform V2 API**


    **API Keys**

    - [Describe the current API key](03-API-Reference/01-Platform-V2-API/01-API-Keys/01-Describe-the-current-API-key.md) — Returns metadata for the API key used in the Authorization header.

    **Runs**

    - [\[Legacy\] List runs](03-API-Reference/01-Platform-V2-API/02-Runs/01-Legacy-List-runs.md) — Lists runs for a use case. **Deprecated**: prefer GET /workflows/:workflow_id/runs instead.
    - [Cancel a run](03-API-Reference/01-Platform-V2-API/02-Runs/02-Cancel-a-run.md) — Cancels a running or scheduled run for the caller's org by proxying to the workflows service.
    - [Get recordings for a run](03-API-Reference/01-Platform-V2-API/02-Runs/03-Get-recordings-for-a-run.md) — Returns signed URLs for call recordings associated with a run. Optionally filter by session_id.
    - [List run sessions](03-API-Reference/01-Platform-V2-API/02-Runs/04-List-run-sessions.md) — Returns paginated sessions for a run, ordered by timestamp.
    - [Get run](03-API-Reference/01-Platform-V2-API/02-Runs/05-Get-run.md) — Returns metadata for a single run. Use /runs/:run_id/nodes for node summaries, /runs/:run_id/outputs/:output_id for a full node output payload, /runs/:run_id/sessions for session data, and /runs/:run_id/flags for issues.
    - [List run nodes](03-API-Reference/01-Platform-V2-API/02-Runs/06-List-run-nodes.md) — Returns lightweight run node execution records in timestamp order.
    - [Get run output](03-API-Reference/01-Platform-V2-API/02-Runs/07-Get-run-output.md) — Returns the full payload for a single output execution in a run.
    - [Mark run annotation](03-API-Reference/01-Platform-V2-API/02-Runs/08-Mark-run-annotation.md) — Marks a run as correct, incorrect, or critical. When marked as incorrect or critical with a correction message, an issue is automatically created.
    - [List run flags](03-API-Reference/01-Platform-V2-API/02-Runs/09-List-run-flags.md) — Returns paginated flags (issues) for a run, ordered by creation date.
    - [List audit remarks for a run](03-API-Reference/01-Platform-V2-API/02-Runs/10-List-audit-remarks-for-a-run.md) — Returns all northstar audit remarks for a specific run, showing per-criterion pass/fail grades.

    **Billing**

    - [Get usage totals](03-API-Reference/01-Platform-V2-API/03-Billing/01-Get-usage-totals.md) — Returns the authenticated organization's total voice minutes, emails, and text messages between the inclusive start and end datetimes. Use Get usage details for the same usage grouped by workflow.
    - [Get usage details](03-API-Reference/01-Platform-V2-API/03-Billing/02-Get-usage-details.md) — Returns the authenticated organization's voice minutes, emails, and text messages grouped by workflow between the inclusive start and end datetimes. Filter by one or more workflow IDs using repeated use_case_id parameters or a comma-separated list; omit the filter to include all workflows.
    - [Get credits](03-API-Reference/01-Platform-V2-API/03-Billing/03-Get-credits.md) — Returns the authenticated organization's billable credit consumption by workflow for an inclusive date range, grouped daily, weekly, or monthly. Each row includes the period, full folder path, workflow identity, total credits, and the same L1 → L2 → L3 component breakdown shown in Settings → Usage,…
    - [Get run credits](03-API-Reference/01-Platform-V2-API/03-Billing/04-Get-run-credits.md) — Returns credit consumption for a single run, broken down with the same L1 -> L2 -> L3 component taxonomy as Get credits (category -> subcomponents). Scoped to the authenticated organization via API key.

    **Use Cases**

    - [\[Legacy\] List use cases](03-API-Reference/01-Platform-V2-API/04-Use-Cases/01-Legacy-List-use-cases.md) — Returns use cases for the authenticated org along with the live production version if available (or the most recent version as fallback). **Deprecated**: prefer GET /workflows instead.

    **Contacts**

    - [Lookup contact by identifier](03-API-Reference/01-Platform-V2-API/05-Contacts/01-Lookup-contact-by-identifier.md) — Returns contact if found by type and value. Returns 404 if not found. Does not create new contacts.
    - [List contacts](03-API-Reference/01-Platform-V2-API/05-Contacts/02-List-contacts.md) — Returns paginated contacts for the organization. Uses cursor-based pagination.
    - [Get contact](03-API-Reference/01-Platform-V2-API/05-Contacts/03-Get-contact.md) — Returns a single contact with interaction and memory counts
    - [List contact interactions](03-API-Reference/01-Platform-V2-API/05-Contacts/04-List-contact-interactions.md) — Returns paginated communication events for a contact
    - [List contact memories](03-API-Reference/01-Platform-V2-API/05-Contacts/05-List-contact-memories.md) — Returns paginated memories for a contact

    **Knowledge Bases**

    - [Get knowledge bases](03-API-Reference/01-Platform-V2-API/06-Knowledge-Bases/01-Get-knowledge-bases.md) — List all knowledge bases for the organization.
    - [Post knowledge bases](03-API-Reference/01-Platform-V2-API/06-Knowledge-Bases/02-Post-knowledge-bases.md) — Create a new knowledge base for the organization.
    - [Get knowledge bases files](03-API-Reference/01-Platform-V2-API/06-Knowledge-Bases/03-Get-knowledge-bases-files.md) — List all files in a knowledge base. Use this endpoint to check file processing status after triggering chunking via POST /:kbId/trigger-chunking.
    - [Post knowledge bases upload urls](03-API-Reference/01-Platform-V2-API/06-Knowledge-Bases/04-Post-knowledge-bases-upload-urls.md) — Step 1 of the file upload flow. Creates file records in the database and returns presigned object-storage URLs (valid for 3 minutes). Upload each file using uploadUrl and send uploadHeaders when present, then call POST /:kbId/trigger-chunking with the returned fileIds to start processing.
    - [Post knowledge bases trigger chunking](03-API-Reference/01-Platform-V2-API/06-Knowledge-Bases/05-Post-knowledge-bases-trigger-chunking.md) — Step 2 of the file upload flow. Call this endpoint after uploading files to object storage using the presigned URLs and any uploadHeaders from POST /:kbId/upload-urls. Triggers embedding generation for the specified files. Files will be available in the knowledge base within 10-15 minutes. Use GET /…
    - [Delete knowledge bases](03-API-Reference/01-Platform-V2-API/06-Knowledge-Bases/06-Delete-knowledge-bases.md) — Delete a knowledge base and all associated files and chunks. This action is irreversible.
    - [Delete knowledge bases files](03-API-Reference/01-Platform-V2-API/06-Knowledge-Bases/07-Delete-knowledge-bases-files.md) — Delete a file from a knowledge base. This removes the file from storage and deletes all associated chunks. This action is irreversible.

    **Workflows**

    - [List workflows](03-API-Reference/01-Platform-V2-API/07-Workflows/01-List-workflows.md) — Returns paginated workflows for the authenticated organization. Each workflow includes its latest version info (live production version preferred, otherwise most recent). Supports searching by name and filtering by folder.
    - [Create a workflow](03-API-Reference/01-Platform-V2-API/07-Workflows/02-Create-a-workflow.md) — Creates a new workflow in the authenticated organization. Supports three creation modes:
    - [Get a workflow](03-API-Reference/01-Platform-V2-API/07-Workflows/03-Get-a-workflow.md) — Returns a single workflow by UUID or slug, including its latest version info (live production version preferred, otherwise most recent).
    - [Delete a workflow](03-API-Reference/01-Platform-V2-API/07-Workflows/04-Delete-a-workflow.md) — Soft-deletes a workflow by UUID or slug. The workflow must not have any live versions — unpublish all versions before deleting.
    - [Update a workflow](03-API-Reference/01-Platform-V2-API/07-Workflows/05-Update-a-workflow.md) — Updates workflow metadata and settings. Accepts a workflow UUID or slug as the path parameter. Set `folder_id` to `null` to move the workflow to the root level. Use `settings` to update configuration such as webhooks, out-of-office hours, approval process, data retention, and audits. This endpoint d…
    - [List workflow versions](03-API-Reference/01-Platform-V2-API/07-Workflows/06-List-workflow-versions.md) — Returns paginated versions for a workflow. Supports searching by version number or version name.
    - [List workflow templates](03-API-Reference/01-Platform-V2-API/07-Workflows/07-List-workflow-templates.md) — Returns a paginated list of available workflow templates. Each template includes a description and the inputs it accepts (marked as required or optional). Use a template's name in the `from_template.template` field when creating a workflow.
    - [Duplicate a workflow](03-API-Reference/01-Platform-V2-API/07-Workflows/08-Duplicate-a-workflow.md) — Creates a copy of a workflow including all its nodes and configurations. The duplicated workflow is created as a new unpublished workflow with version number 1. If the source uses workflow engine v2, the duplicate remains an editable v2 draft and cannot be published through the public API until upgr…
    - [Publish a workflow](03-API-Reference/01-Platform-V2-API/07-Workflows/09-Publish-a-workflow.md) — Publishes the latest version of the specified workflow to make it live. Before publishing, all action nodes are checked for test errors and untested status. If untested nodes exist (with no errors), a synchronous test-all is triggered first. If any node has test errors, the publish is blocked and er…
    - [Unpublish a workflow](03-API-Reference/01-Platform-V2-API/07-Workflows/10-Unpublish-a-workflow.md) — Finds the currently live version for the workflow and unpublishes it. The version is taken offline and unlocked for editing. Returns 400 if no version is currently live. Accepts a workflow UUID or slug as the path parameter.
    - [List workflow runs](03-API-Reference/01-Platform-V2-API/07-Workflows/11-List-workflow-runs.md) — Returns paginated runs for a workflow. Supports filtering by status, date ranges, and annotation.
    - [Trigger a workflow run](03-API-Reference/01-Platform-V2-API/07-Workflows/12-Trigger-a-workflow-run.md) — Starts a new run for a workflow by proxying to the hooks service. Accepts either a JSON body with payload/environment fields, or a multipart/form-data request with a file and optional form fields (pass environment as a query param for multipart). Supports targeting different environments (production…
    - [List workflow sessions](03-API-Reference/01-Platform-V2-API/07-Workflows/13-List-workflow-sessions.md) — Returns paginated sessions for a workflow across all runs, ordered by timestamp.
    - [Cancel active workflow runs](03-API-Reference/01-Platform-V2-API/07-Workflows/14-Cancel-active-workflow-runs.md) — Cancels all current and queued runs for the workflow. By default, the currently live workflow version is also unpublished. Set unpublish_workflow to false to keep the workflow published after cancellation. Accepts a workflow UUID or slug as the path parameter.

    **Workflow Variables**

    - [List workflow variables](03-API-Reference/01-Platform-V2-API/08-Workflow-Variables/01-List-workflow-variables.md) — Returns paginated variables scoped to a specific workflow. Accepts a workflow UUID or slug as the path parameter.
    - [Create a workflow variable](03-API-Reference/01-Platform-V2-API/08-Workflow-Variables/02-Create-a-workflow-variable.md) — Creates a new variable scoped to the specified workflow. Accepts a workflow UUID or slug as the path parameter.
    - [Delete a workflow variable](03-API-Reference/01-Platform-V2-API/08-Workflow-Variables/03-Delete-a-workflow-variable.md) — Permanently deletes a variable from a workflow. This action cannot be undone.
    - [Update a workflow variable](03-API-Reference/01-Platform-V2-API/08-Workflow-Variables/04-Update-a-workflow-variable.md) — Updates one or more fields on a variable. Only the fields provided in the request body are updated.

    **Audits**

    - [List northstar audits for a workflow](03-API-Reference/01-Platform-V2-API/09-Audits/01-List-northstar-audits-for-a-workflow.md) — Returns paginated northstar audit results for a workflow, showing pass/fail rates per behavioral criterion.
    - [List audit remarks for a northstar](03-API-Reference/01-Platform-V2-API/09-Audits/02-List-audit-remarks-for-a-northstar.md) — Returns cursor-paginated audit remarks for a specific northstar criterion, optionally filtered by grade.
    - [List audit remarks for a workflow](03-API-Reference/01-Platform-V2-API/09-Audits/03-List-audit-remarks-for-a-workflow.md) — Returns cursor-paginated behavioral audit remarks across all northstar criteria for a workflow. Optionally filter by northstar, grade, or status.
    - [List node errors for a workflow](03-API-Reference/01-Platform-V2-API/09-Audits/04-List-node-errors-for-a-workflow.md) — Returns paginated node execution errors for a workflow, grouped by node and error type.
    - [Get audit stats for the live workflow version](03-API-Reference/01-Platform-V2-API/09-Audits/05-Get-audit-stats-for-the-live-workflow-version.md) — Returns aggregate audit statistics for the live (or most recently audited) version of a workflow.
    - [List audited versions for a workflow](03-API-Reference/01-Platform-V2-API/09-Audits/06-List-audited-versions-for-a-workflow.md) — Returns all versions of a workflow that have audit data, indicating which is the live version.
    - [Get an audit remark by ID](03-API-Reference/01-Platform-V2-API/09-Audits/07-Get-an-audit-remark-by-ID.md) — Returns a single behavioral audit remark, including its northstar criterion, grade, correction, evaluated messages, and status.
    - [Get feedback for an audit remark](03-API-Reference/01-Platform-V2-API/09-Audits/08-Get-feedback-for-an-audit-remark.md) — Returns the current caller's feedback for an audit remark, or null if none exists. Supports user-level and org-level API keys.
    - [Submit feedback for an audit remark](03-API-Reference/01-Platform-V2-API/09-Audits/09-Submit-feedback-for-an-audit-remark.md) — Submit a thumbs up/down for an audit remark. Supports user-level and org-level API keys. A thumbs-up automatically adds the remark as a northstar example.
    - [Delete feedback for an audit remark](03-API-Reference/01-Platform-V2-API/09-Audits/10-Delete-feedback-for-an-audit-remark.md) — Removes the current caller's feedback for an audit remark. Supports user-level and org-level API keys.

    **Issues**

    - [List issues for a workflow](03-API-Reference/01-Platform-V2-API/10-Issues/01-List-issues-for-a-workflow.md) — Returns paginated quality issues (flags) for a workflow, optionally filtered by status or source.
    - [Update issue status](03-API-Reference/01-Platform-V2-API/10-Issues/02-Update-issue-status.md) — Updates the status of a quality issue (flag).

    **Apps**

    - [Duplicate an app](03-API-Reference/01-Platform-V2-API/11-Apps/01-Duplicate-an-app.md) — Creates a copy of a managed custom app, including source code and custom environment variables.

    **Versions**

    - [Get a version with nodes summary](03-API-Reference/01-Platform-V2-API/12-Versions/01-Get-a-version-with-nodes-summary.md) — Returns a single version by UUID or slug with metadata, node count, node counts by type, and the list of events (action node types) used.
    - [Update a version](03-API-Reference/01-Platform-V2-API/12-Versions/02-Update-a-version.md) — Updates version metadata (name and/or description). Accepts a version UUID or slug as the path parameter.
    - [Fork a version](03-API-Reference/01-Platform-V2-API/12-Versions/03-Fork-a-version.md) — Creates a new version by copying all nodes from the specified version. The new version gets the next available version number and is unlocked/unpublished. If the source uses workflow engine v2, the fork remains an editable v2 draft and cannot be published through the public API until upgraded to v3.…
    - [Publish a version](03-API-Reference/01-Platform-V2-API/12-Versions/04-Publish-a-version.md) — Publishes the specified version to make it live. Before publishing, node configuration completeness is validated. If untested nodes exist, a synchronous test-all is triggered automatically. Test errors do not block publishing (matching UI behavior) but are returned as informational warnings in the `…
    - [Lock a version](03-API-Reference/01-Platform-V2-API/12-Versions/05-Lock-a-version.md) — Locks the specified version, preventing further edits to its nodes. Accepts a version UUID or slug as the path parameter.
    - [Unlock a version](03-API-Reference/01-Platform-V2-API/12-Versions/06-Unlock-a-version.md) — Unlocks the specified version, allowing edits to its nodes. A version that is currently live cannot be unlocked — use unpublish instead. Accepts a version UUID or slug as the path parameter.
    - [Unpublish a version](03-API-Reference/01-Platform-V2-API/12-Versions/07-Unpublish-a-version.md) — Unpublishes the version (takes it offline) and unlocks it for editing. The version will no longer be live and its published lock is removed, allowing further modifications. The version must currently be live. Accepts a version UUID or slug as the path parameter.
    - [List version nodes](03-API-Reference/01-Platform-V2-API/12-Versions/08-List-version-nodes.md) — Returns all workflow nodes belonging to the specified version. The version can be identified by its UUID or slug.
    - [Add nodes to a version](03-API-Reference/01-Platform-V2-API/12-Versions/09-Add-nodes-to-a-version.md) — Adds one or more nodes to the specified version. Nodes are processed sequentially in array order, so later nodes can reference earlier ones via `parent_node_index` (0-based index into this array) or existing DB nodes via `parent_node_id`. Each node must include a `type` discriminator: `"trigger"`, `…
    - [Get a single node](03-API-Reference/01-Platform-V2-API/12-Versions/10-Get-a-single-node.md) — Returns the full details of a single node including its configuration. For webhook trigger nodes (INCOMING_HOOK or PREDEFINED_REQUEST), the response also includes production, staging, development, and test webhook URLs.
    - [Update a node](03-API-Reference/01-Platform-V2-API/12-Versions/11-Update-a-node.md) — Updates the specified node. The request body must include a `type` discriminator matching the node type. Updatable fields depend on the type: - **trigger**: `name`, `configuration`, `webhook_payload` - **action**: `name`, `configuration`, `webhook_payload` - **agent**: `name`, `configuration`, `prom…
    - [Delete a node](03-API-Reference/01-Platform-V2-API/12-Versions/12-Delete-a-node.md) — Deletes the specified node. For tool, condition, and paths-root nodes, owned child nodes are also cascade-deleted. For action, prompt, and module-change nodes, children are reparented to the deleted node's parent so the workflow chain is preserved. Agent nodes delete their internal children (prompt…
    - [List available variables for a node](03-API-Reference/01-Platform-V2-API/12-Versions/13-List-available-variables-for-a-node.md) — Returns all variable groups available to the specified node, including system variables, environment variables, and upstream node outputs.
    - [Get config schema for a node](03-API-Reference/01-Platform-V2-API/12-Versions/14-Get-config-schema-for-a-node.md) — Returns the configuration schema for the node's event, including field types, required fields, current values, defaults, and validation status. Only works for action nodes (nodes with an event_id).
    - [Set custom node output](03-API-Reference/01-Platform-V2-API/12-Versions/15-Set-custom-node-output.md) — Sets a custom JSON object as the node's output for testing purposes. This upserts the node's generated output schema, marking the node as complete. Useful for defining output schemas on trigger nodes, webhooks, or any node where you want to manually specify the output shape without running the actua…
    - [Test a single node](03-API-Reference/01-Platform-V2-API/12-Versions/16-Test-a-single-node.md) — Triggers a test run for a single node in the specified version. The node must have a complete configuration and the version must not be published. Returns the generated node output (schema) on success.
    - [Test all nodes in a version](03-API-Reference/01-Platform-V2-API/12-Versions/17-Test-all-nodes-in-a-version.md) — Triggers a synchronous test-all run for every testable node in the specified version. Nodes are executed in dependency waves — independent nodes run in parallel. If a node fails, dependent nodes are skipped. The endpoint blocks until all nodes have been tested and returns per-node results.
    - [Inspect a tool's Tool Call Result](03-API-Reference/01-Platform-V2-API/12-Versions/18-Inspect-a-tools-Tool-Call-Result.md) — Returns the current Tool Call Result and acks the tool.
    - [Sync a tool's Tool Call Result](03-API-Reference/01-Platform-V2-API/12-Versions/19-Sync-a-tools-Tool-Call-Result.md) — Generates only untested or out-of-date testable nodes.
    - [Generate a tool's Tool Call Result](03-API-Reference/01-Platform-V2-API/12-Versions/20-Generate-a-tools-Tool-Call-Result.md) — Generates every testable node.
    - [Set Tool Call Result visibility](03-API-Reference/01-Platform-V2-API/12-Versions/21-Set-Tool-Call-Result-visibility.md) — Replaces the complete list of generated leaf fields one branch node exposes to the agent.
    - [List prompt issues](03-API-Reference/01-Platform-V2-API/12-Versions/22-List-prompt-issues.md) — Returns prompt quality issues for all prompt nodes in the specified version. Issues are generated asynchronously by the platform's prompt analysis system. Each prompt node includes its current prompt text, issue generation status, and any open (non-rejected) issues with recommendations.

    **Workflow Folders**

    - [List workflow folders](03-API-Reference/01-Platform-V2-API/13-Workflow-Folders/01-List-workflow-folders.md) — Returns paginated workflow folders for the authenticated organization. Supports searching by name.
    - [Create a workflow folder](03-API-Reference/01-Platform-V2-API/13-Workflow-Folders/02-Create-a-workflow-folder.md) — Creates a new workflow folder in the authenticated organization. Optionally nest it under a parent folder.
    - [Get a workflow folder](03-API-Reference/01-Platform-V2-API/13-Workflow-Folders/03-Get-a-workflow-folder.md) — Returns a single workflow folder by UUID or slug.
    - [Update a workflow folder](03-API-Reference/01-Platform-V2-API/13-Workflow-Folders/04-Update-a-workflow-folder.md) — Updates the name of a workflow folder identified by UUID or slug.
    - [Delete a workflow folder](03-API-Reference/01-Platform-V2-API/13-Workflow-Folders/05-Delete-a-workflow-folder.md) — Deletes a workflow folder by UUID or slug. Workflows inside the folder are moved to the folder specified by `move_to`, or to the parent folder if `move_to` is omitted. Sub-folders are also moved to the same destination.

    **Phone Numbers**

    - [List phone numbers](03-API-Reference/01-Platform-V2-API/14-Phone-Numbers/01-List-phone-numbers.md) — Returns all phone numbers for the authenticated organization, including Twilio, Telnyx, and SIP trunk numbers with caller ID information.
    - [Purchase a phone number](03-API-Reference/01-Platform-V2-API/14-Phone-Numbers/02-Purchase-a-phone-number.md) — Purchases a new phone number from Twilio or Telnyx. For toll-free numbers (US/CA only), also submits toll-free verification. Rate limited to one purchase every 10 minutes per organization. Send force=true in the body to bypass this limit (use with caution — each number has a recurring monthly cost).
    - [Validate toll-free numbers for TextAgent](03-API-Reference/01-Platform-V2-API/14-Phone-Numbers/03-Validate-toll-free-numbers-for-TextAgent.md) — Validates toll-free phone numbers for use with TextAgent SMS. Outbound numbers are always valid. Inbound numbers are blocked if a live inbound TextAgent already uses them.
    - [Delete a toll-free verification](03-API-Reference/01-Platform-V2-API/14-Phone-Numbers/04-Delete-a-toll-free-verification.md) — Deletes a toll-free verification request by its SID.
    - [Free up a phone number](03-API-Reference/01-Platform-V2-API/14-Phone-Numbers/05-Free-up-a-phone-number.md) — Removes a phone number from all workflows it is assigned to. The phone number must not be used in any live version.
    - [Delete a phone number](03-API-Reference/01-Platform-V2-API/14-Phone-Numbers/06-Delete-a-phone-number.md) — Permanently deletes a phone number. The phone number must not be in use by any workflow.
    - [Get phone number usage](03-API-Reference/01-Platform-V2-API/14-Phone-Numbers/07-Get-phone-number-usage.md) — Returns usage information for a phone number across all workflows and versions.
    - [Remove phone number from a workflow](03-API-Reference/01-Platform-V2-API/14-Phone-Numbers/08-Remove-phone-number-from-a-workflow.md) — Removes a phone number from a specific workflow and version. The version must not be live.
    - [Get toll-free verification status](03-API-Reference/01-Platform-V2-API/14-Phone-Numbers/09-Get-toll-free-verification-status.md) — Returns toll-free verification status and submitted data for a phone number. Returns 204 when no verification exists.
    - [Submit toll-free verification](03-API-Reference/01-Platform-V2-API/14-Phone-Numbers/10-Submit-toll-free-verification.md) — Submits a toll-free verification request for a phone number. Requires business_name, notification_email, and sms_url.
    - [Create and attach SIP trunk](03-API-Reference/01-Platform-V2-API/14-Phone-Numbers/11-Create-and-attach-SIP-trunk.md) — Creates a SIP trunk and attaches it to a Twilio phone number. Sets up both inbound and outbound trunks in LiveKit.
    - [Update a phone number](03-API-Reference/01-Platform-V2-API/14-Phone-Numbers/12-Update-a-phone-number.md) — Updates the display name and caller ID setting for a phone number.

    **SIP Trunks**

    - [List SIP trunks](03-API-Reference/01-Platform-V2-API/15-SIP-Trunks/01-List-SIP-trunks.md) — Returns all SIP trunks for the organization.
    - [Create a SIP trunk](03-API-Reference/01-Platform-V2-API/15-SIP-Trunks/02-Create-a-SIP-trunk.md) — Creates a new SIP trunk with inbound and outbound LiveKit trunks. Rate limited to one creation every 10 minutes per organization. Send force=true in the body to bypass this limit (use with caution — each trunk has a recurring monthly cost).
    - [Get SIP trunk options](03-API-Reference/01-Platform-V2-API/15-SIP-Trunks/03-Get-SIP-trunk-options.md) — Returns trunk options for UI (id, name, number).
    - [Create multiple SIP trunks](03-API-Reference/01-Platform-V2-API/15-SIP-Trunks/04-Create-multiple-SIP-trunks.md) — Creates multiple SIP trunks from a shared configuration. Returns the successfully created trunks. Rate limited to one creation every 10 minutes per organization. Send force=true in the body to bypass this limit (use with caution — each trunk has a recurring monthly cost).
    - [Get a SIP trunk](03-API-Reference/01-Platform-V2-API/15-SIP-Trunks/05-Get-a-SIP-trunk.md) — Returns a single SIP trunk by ID.
    - [Update a SIP trunk](03-API-Reference/01-Platform-V2-API/15-SIP-Trunks/06-Update-a-SIP-trunk.md) — Updates a SIP trunk by ID.
    - [Delete a SIP trunk](03-API-Reference/01-Platform-V2-API/15-SIP-Trunks/07-Delete-a-SIP-trunk.md) — Deletes a SIP trunk by ID. Fails if the trunk is still in use by a workflow.

    **Integrations**

    - [List integrations](03-API-Reference/01-Platform-V2-API/16-Integrations/01-List-integrations.md) — Returns available integrations with optional events and credentials. Delegated providers (CRM, HRIS, ATS, etc.) are expanded into individual entries. Supports filtering by category, provider, and search. Paginated (default: 20 per page).
    - [List integration categories with providers](03-API-Reference/01-Platform-V2-API/16-Integrations/02-List-integration-categories-with-providers.md) — Returns a unified map of categories to their available providers. Includes both internal integration groups (Communications, Data, etc.) and delegated provider categories (CRM, HRIS, ATS, etc.).
    - [Get an integration](03-API-Reference/01-Platform-V2-API/16-Integrations/03-Get-an-integration.md) — Returns a single integration by ID, including its events and the organization's connected credentials. Supports both native integration UUIDs and delegated provider composite IDs (e.g. {uuid}--{provider_slug}).
    - [Create a credential for an integration](03-API-Reference/01-Platform-V2-API/16-Integrations/04-Create-a-credential-for-an-integration.md) — Creates a new credential for a form-based integration. OAuth integrations are not supported via API — use the HappyRobot platform UI instead.
    - [Update a credential for an integration](03-API-Reference/01-Platform-V2-API/16-Integrations/05-Update-a-credential-for-an-integration.md) — Replaces an existing form-based credential's title and data while preserving its ID and workflow references. Send the same complete payload as credential creation, including all required data fields. If credential_type is omitted, the integration's default type is used; send it explicitly for a non-…

    **Integration Resources**

    - [List WhatsApp message templates](03-API-Reference/01-Platform-V2-API/17-Integration-Resources/01-List-WhatsApp-message-templates.md) — Returns all approved WhatsApp message templates for the given credential and business account.
    - [List WhatsApp businesses](03-API-Reference/01-Platform-V2-API/17-Integration-Resources/02-List-WhatsApp-businesses.md) — Returns all WhatsApp businesses associated with the organization's credentials.
    - [List WhatsApp business accounts](03-API-Reference/01-Platform-V2-API/17-Integration-Resources/03-List-WhatsApp-business-accounts.md) — Returns all WhatsApp business accounts for a given business ID.
    - [List WhatsApp phone numbers](03-API-Reference/01-Platform-V2-API/17-Integration-Resources/04-List-WhatsApp-phone-numbers.md) — Returns all WhatsApp phone numbers for a given business account ID.
    - [List Slack channels](03-API-Reference/01-Platform-V2-API/17-Integration-Resources/05-List-Slack-channels.md) — Returns all Slack channels accessible with the organization's credentials.
    - [List Slack users](03-API-Reference/01-Platform-V2-API/17-Integration-Resources/06-List-Slack-users.md) — Returns all Slack users accessible with the organization's credentials.
    - [List Google Sheets spreadsheets](03-API-Reference/01-Platform-V2-API/17-Integration-Resources/07-List-Google-Sheets-spreadsheets.md) — Returns Google Sheets spreadsheets accessible with the organization's credentials. Supports search and cursor-based pagination.
    - [List Google Sheets worksheets](03-API-Reference/01-Platform-V2-API/17-Integration-Resources/08-List-Google-Sheets-worksheets.md) — Returns all worksheets (tabs) within a Google Sheets spreadsheet.
    - [List Google Sheets columns](03-API-Reference/01-Platform-V2-API/17-Integration-Resources/09-List-Google-Sheets-columns.md) — Returns all column headers from a specific worksheet within a Google Sheets spreadsheet.
    - [List Google Sheets rows](03-API-Reference/01-Platform-V2-API/17-Integration-Resources/10-List-Google-Sheets-rows.md) — Returns all rows from a specific worksheet within a Google Sheets spreadsheet.
    - [List Microsoft Teams teams](03-API-Reference/01-Platform-V2-API/17-Integration-Resources/11-List-Microsoft-Teams-teams.md) — Returns all Microsoft Teams teams accessible with the organization's credentials.
    - [List Microsoft Teams channels](03-API-Reference/01-Platform-V2-API/17-Integration-Resources/12-List-Microsoft-Teams-channels.md) — Returns all Microsoft Teams channels. Optionally filter by team ID.
    - [List Microsoft Teams users](03-API-Reference/01-Platform-V2-API/17-Integration-Resources/13-List-Microsoft-Teams-users.md) — Returns all Microsoft Teams users accessible with the organization's credentials.
    - [List Twilio SMS phone numbers](03-API-Reference/01-Platform-V2-API/17-Integration-Resources/14-List-Twilio-SMS-phone-numbers.md) — Returns all Twilio SMS phone numbers available for the organization.
    - [List Telnyx SMS phone numbers](03-API-Reference/01-Platform-V2-API/17-Integration-Resources/15-List-Telnyx-SMS-phone-numbers.md) — Returns all Telnyx SMS phone numbers available for the organization.

    **Sessions**

    - [List sessions by caller ID](03-API-Reference/01-Platform-V2-API/18-Sessions/01-List-sessions-by-caller-ID.md) — Returns paginated sessions whose caller phone number matches caller_id, ordered by timestamp. Optionally filter by session timestamp with start_date and/or end_date (ISO 8601). Resolves the phone number to a contact, so a session is only returned if it produced a communication event. Use the session…
    - [Stream session messages (SSE)](03-API-Reference/01-Platform-V2-API/18-Sessions/02-Stream-session-messages-SSE.md) — Opens a Server-Sent Events stream for a single session. Optionally backfills the most recent messages. The stream emits `message` events in real-time and closes when the session ends.
    - [Get session](03-API-Reference/01-Platform-V2-API/18-Sessions/03-Get-session.md) — Returns metadata for a single session.
    - [List session messages](03-API-Reference/01-Platform-V2-API/18-Sessions/04-List-session-messages.md) — Returns paginated messages for a session, ordered by timestamp.

    **Messages**

    - [List message flags](03-API-Reference/01-Platform-V2-API/19-Messages/01-List-message-flags.md) — Returns paginated flags (issues) for a specific message, ordered by creation date.
    - [Create message flag](03-API-Reference/01-Platform-V2-API/19-Messages/02-Create-message-flag.md) — Creates a new flag (issue) on a specific message. The flag is linked to the message and its parent run.

    **Organization**

    - [Get current organization](03-API-Reference/01-Platform-V2-API/20-Organization/01-Get-current-organization.md) — Returns basic information about the authenticated organization.
    - [List members of the current organization](03-API-Reference/01-Platform-V2-API/20-Organization/02-List-members-of-the-current-organization.md) — Returns members of the authenticated organization, including public profile information and each member's workspace-wide role. The role is null when a member only has scoped access.
    - [Add a member to the current organization](03-API-Reference/01-Platform-V2-API/20-Organization/03-Add-a-member-to-the-current-organization.md) — Adds a member to the authenticated organization by email. Internal users are added immediately; everyone else receives an email invitation to accept. Role must be editor or viewer (owners cannot be assigned via the API); defaults to viewer.
    - [Remove a member from the current organization](03-API-Reference/01-Platform-V2-API/20-Organization/04-Remove-a-member-from-the-current-organization.md) — Removes a member from the authenticated organization, identified by email or user_id. Owners cannot be removed via the API.

    **MCP Servers**

    - [List MCP servers](03-API-Reference/01-Platform-V2-API/21-MCP-Servers/01-List-MCP-servers.md) — Returns paginated MCP servers for the authenticated organization.
    - [Create MCP server](03-API-Reference/01-Platform-V2-API/21-MCP-Servers/02-Create-MCP-server.md) — Creates a new MCP server connection. Tests connectivity and discovers available tools before saving.
    - [Refresh MCP server tools](03-API-Reference/01-Platform-V2-API/21-MCP-Servers/03-Refresh-MCP-server-tools.md) — Re-connects to an existing MCP server and refreshes the list of discovered tools.
    - [List authorized organizations](03-API-Reference/01-Platform-V2-API/21-MCP-Servers/04-List-authorized-organizations.md) — Returns the organizations this MCP token is authorized to act on.

    **Northstars**

    - [List northstars for a prompt node](03-API-Reference/01-Platform-V2-API/22-Northstars/01-List-northstars-for-a-prompt-node.md) — Returns all northstars for a prompt node along with AI generation and coverage assessment statuses.
    - [Create a northstar for a prompt node](03-API-Reference/01-Platform-V2-API/22-Northstars/02-Create-a-northstar-for-a-prompt-node.md) — Create a new northstar evaluation criterion for this prompt node.
    - [Generate northstars for a prompt node](03-API-Reference/01-Platform-V2-API/22-Northstars/03-Generate-northstars-for-a-prompt-node.md) — Generate northstars for this node using AI. If northstars already exist they are force-regenerated.
    - [Batch toggle northstars](03-API-Reference/01-Platform-V2-API/22-Northstars/04-Batch-toggle-northstars.md) — Enable or disable all northstars for this prompt node at once.
    - [Iterate northstars for a prompt node](03-API-Reference/01-Platform-V2-API/22-Northstars/05-Iterate-northstars-for-a-prompt-node.md) — Rewrite existing northstars to reflect recent changes made to the prompt node.
    - [Assess northstar coverage for a prompt node](03-API-Reference/01-Platform-V2-API/22-Northstars/06-Assess-northstar-coverage-for-a-prompt-node.md) — Trigger an AI assessment of how well current northstars cover the prompt's expected behaviors.
    - [Create a northstar folder for a prompt node](03-API-Reference/01-Platform-V2-API/22-Northstars/07-Create-a-northstar-folder-for-a-prompt-node.md) — Create a folder for organizing this prompt node's northstars. File northstars into it via folder_id on create or update.
    - [Get a northstar by ID](03-API-Reference/01-Platform-V2-API/22-Northstars/08-Get-a-northstar-by-ID.md)
    - [Delete a northstar](03-API-Reference/01-Platform-V2-API/22-Northstars/09-Delete-a-northstar.md)
    - [Update a northstar](03-API-Reference/01-Platform-V2-API/22-Northstars/10-Update-a-northstar.md) — Update any subset of: name, description, category, examples, enabled state, priority, or folder_id.
    - [Get northstar history](03-API-Reference/01-Platform-V2-API/22-Northstars/11-Get-northstar-history.md) — Fetch the full regeneration chain — every version this northstar was derived from, oldest first.
    - [Submit northstar feedback](03-API-Reference/01-Platform-V2-API/22-Northstars/12-Submit-northstar-feedback.md) — Submit a correctness rating (-2 = strongly wrong, +2 = strongly correct). One entry per API key/user.
    - [Delete northstar feedback](03-API-Reference/01-Platform-V2-API/22-Northstars/13-Delete-northstar-feedback.md) — Remove your feedback on a northstar.

    **Custom Evals**

    - [List custom evals for a prompt node](03-API-Reference/01-Platform-V2-API/23-Custom-Evals/01-List-custom-evals-for-a-prompt-node.md)
    - [Create a custom eval for a prompt node](03-API-Reference/01-Platform-V2-API/23-Custom-Evals/02-Create-a-custom-eval-for-a-prompt-node.md)
    - [Get available tools for custom evals](03-API-Reference/01-Platform-V2-API/23-Custom-Evals/03-Get-available-tools-for-custom-evals.md) — Available tool/function definitions for this node — for building expected_tool_calls.
    - [Get default variables for custom evals](03-API-Reference/01-Platform-V2-API/23-Custom-Evals/04-Get-default-variables-for-custom-evals.md) — Merged default variable values available at runtime (org + use-case + workflow levels).
    - [Extract custom eval from a run](03-API-Reference/01-Platform-V2-API/23-Custom-Evals/05-Extract-custom-eval-from-a-run.md) — Build a custom eval from an existing run. Auto-extracts messages, variables, and suggests a name.
    - [Create a shared Tests folder in a prompt node’s workflow](03-API-Reference/01-Platform-V2-API/23-Custom-Evals/06-Create-a-shared-Tests-folder-in-a-prompt-nodes-workflow.md) — Create a workflow-wide Tests folder. The node resolves the workflow; folder placement is independent of prompt or agent ownership. File top-level tests and suites via folder_id on update.
    - [Get a custom eval by ID](03-API-Reference/01-Platform-V2-API/23-Custom-Evals/07-Get-a-custom-eval-by-ID.md)
    - [Delete a custom eval](03-API-Reference/01-Platform-V2-API/23-Custom-Evals/08-Delete-a-custom-eval.md)
    - [Update a custom eval](03-API-Reference/01-Platform-V2-API/23-Custom-Evals/09-Update-a-custom-eval.md)
    - [Run a custom eval](03-API-Reference/01-Platform-V2-API/23-Custom-Evals/10-Run-a-custom-eval.md) — Execute the eval asynchronously. Poll /custom-evals/:eval_id/runs for results.
    - [List custom eval runs](03-API-Reference/01-Platform-V2-API/23-Custom-Evals/11-List-custom-eval-runs.md)

    **Adversarial Tests**

    - [List adversarial tests for a node](03-API-Reference/01-Platform-V2-API/24-Adversarial-Tests/01-List-adversarial-tests-for-a-node.md)
    - [Get an adversarial test by ID](03-API-Reference/01-Platform-V2-API/24-Adversarial-Tests/02-Get-an-adversarial-test-by-ID.md)
    - [List adversarial test runs](03-API-Reference/01-Platform-V2-API/24-Adversarial-Tests/03-List-adversarial-test-runs.md)
    - [Get adversarial test run by ID](03-API-Reference/01-Platform-V2-API/24-Adversarial-Tests/04-Get-adversarial-test-run-by-ID.md) — Full status and audit remarks for a single test run.
    - [Get adversarial test run messages](03-API-Reference/01-Platform-V2-API/24-Adversarial-Tests/05-Get-adversarial-test-run-messages.md) — The full conversation that took place during this adversarial test run.
    - [Get the resolved audit scope for an adversarial test](03-API-Reference/01-Platform-V2-API/24-Adversarial-Tests/06-Get-the-resolved-audit-scope-for-an-adversarial-test.md) — Returns the northstar categories that BEA will grade against when this test runs. Generated tests inherit the suite's scope; standalone tests carry their own. Use this to display 'currently grading against tags: [...]' without re-implementing the resolution.

    **Adversarial Suites**

    - [List adversarial suites for a node](03-API-Reference/01-Platform-V2-API/25-Adversarial-Suites/01-List-adversarial-suites-for-a-node.md)
    - [Get an adversarial suite by ID](03-API-Reference/01-Platform-V2-API/25-Adversarial-Suites/02-Get-an-adversarial-suite-by-ID.md) — Returns the suite and the mermaid workflow graph if already generated.
    - [List adversarial suite runs](03-API-Reference/01-Platform-V2-API/25-Adversarial-Suites/03-List-adversarial-suite-runs.md)
    - [Get adversarial suite run by ID](03-API-Reference/01-Platform-V2-API/25-Adversarial-Suites/04-Get-adversarial-suite-run-by-ID.md) — Full status and aggregate counts for a suite run.
    - [List test runs in a suite run](03-API-Reference/01-Platform-V2-API/25-Adversarial-Suites/05-List-test-runs-in-a-suite-run.md) — All individual adversarial test results within this suite run.

    **E2E Scenarios**

    - [Get e2e scenarios](03-API-Reference/01-Platform-V2-API/26-E2E-Scenarios/01-Get-e2e-scenarios.md)
    - [Post e2e scenarios](03-API-Reference/01-Platform-V2-API/26-E2E-Scenarios/02-Post-e2e-scenarios.md)
    - [Get e2e scenarios 1](03-API-Reference/01-Platform-V2-API/26-E2E-Scenarios/03-Get-e2e-scenarios-1.md)
    - [Delete e2e scenarios](03-API-Reference/01-Platform-V2-API/26-E2E-Scenarios/04-Delete-e2e-scenarios.md)
    - [Patch e2e scenarios](03-API-Reference/01-Platform-V2-API/26-E2E-Scenarios/05-Patch-e2e-scenarios.md)
    - [Post e2e scenarios run](03-API-Reference/01-Platform-V2-API/26-E2E-Scenarios/06-Post-e2e-scenarios-run.md)
    - [Get e2e scenarios runs](03-API-Reference/01-Platform-V2-API/26-E2E-Scenarios/07-Get-e2e-scenarios-runs.md)

    **Test Suites**

    - [Get test suites](03-API-Reference/01-Platform-V2-API/27-Test-Suites/01-Get-test-suites.md)
    - [Post test suites](03-API-Reference/01-Platform-V2-API/27-Test-Suites/02-Post-test-suites.md)
    - [Get test suitescandidates](03-API-Reference/01-Platform-V2-API/27-Test-Suites/03-Get-test-suitescandidates.md)
    - [Get test suites 1](03-API-Reference/01-Platform-V2-API/27-Test-Suites/04-Get-test-suites-1.md)
    - [Delete test suites](03-API-Reference/01-Platform-V2-API/27-Test-Suites/05-Delete-test-suites.md)
    - [Patch test suites](03-API-Reference/01-Platform-V2-API/27-Test-Suites/06-Patch-test-suites.md)
    - [Get test suites members](03-API-Reference/01-Platform-V2-API/27-Test-Suites/07-Get-test-suites-members.md)
    - [Patch test suites members](03-API-Reference/01-Platform-V2-API/27-Test-Suites/08-Patch-test-suites-members.md)
    - [Post test suites generate](03-API-Reference/01-Platform-V2-API/27-Test-Suites/09-Post-test-suites-generate.md)
    - [Post test suites run](03-API-Reference/01-Platform-V2-API/27-Test-Suites/10-Post-test-suites-run.md)
    - [Get test suites runs](03-API-Reference/01-Platform-V2-API/27-Test-Suites/11-Get-test-suites-runs.md)
    - [Get test suitesruns](03-API-Reference/01-Platform-V2-API/27-Test-Suites/12-Get-test-suitesruns.md)
    - [Post test suitesruns cancel](03-API-Reference/01-Platform-V2-API/27-Test-Suites/13-Post-test-suitesruns-cancel.md)

    **Events**

    - [Get config schema for an event](03-API-Reference/01-Platform-V2-API/28-Events/01-Get-config-schema-for-an-event.md) — Returns the configuration schema for an event, including field types, required fields, defaults, and available options. Use this to inspect what an event expects before creating a node.

    **Twin**

    - [Get Twin database schema](03-API-Reference/01-Platform-V2-API/29-Twin/01-Get-Twin-database-schema.md)
    - [Create a Twin table](03-API-Reference/01-Platform-V2-API/29-Twin/02-Create-a-Twin-table.md)
    - [Get Twin table data](03-API-Reference/01-Platform-V2-API/29-Twin/03-Get-Twin-table-data.md)
    - [Drop a Twin table](03-API-Reference/01-Platform-V2-API/29-Twin/04-Drop-a-Twin-table.md)
    - [Insert a row into a Twin table](03-API-Reference/01-Platform-V2-API/29-Twin/05-Insert-a-row-into-a-Twin-table.md)
    - [Delete rows from a Twin table](03-API-Reference/01-Platform-V2-API/29-Twin/06-Delete-rows-from-a-Twin-table.md)
    - [Update a row in a Twin table](03-API-Reference/01-Platform-V2-API/29-Twin/07-Update-a-row-in-a-Twin-table.md)
    - [Execute SQL on Twin database](03-API-Reference/01-Platform-V2-API/29-Twin/08-Execute-SQL-on-Twin-database.md)
    - [Create a Twin workflow dump table](03-API-Reference/01-Platform-V2-API/29-Twin/09-Create-a-Twin-workflow-dump-table.md) — Creates a Twin table plus a dump config that maps workflow run values into its columns. Unlike POST /twin/tables (a bare table), the server resolves the workflow's variable catalog and binds each column to a variable, so completed runs populate the table automatically. Captures every variable by def…
    - [Delete a Twin workflow dump](03-API-Reference/01-Platform-V2-API/29-Twin/10-Delete-a-Twin-workflow-dump.md) — Deletes the workflow dump run-capture config for a table. Set dropTable=true to also drop the physical table and all its data.

    **Chat**

    - [Create a chat client token](03-API-Reference/01-Platform-V2-API/30-Chat/01-Create-a-chat-client-token.md) — Generates a scoped JWT for browser-side chat operations. Call this from your backend with your API key, then pass the token to the frontend.
    - [Create a chat session](03-API-Reference/01-Platform-V2-API/30-Chat/02-Create-a-chat-session.md) — Creates a new chat session for the workflow scoped in the client token.
    - [Send a chat message](03-API-Reference/01-Platform-V2-API/30-Chat/03-Send-a-chat-message.md) — Sends a user message to the chat session. The AI response will arrive via WebSocket.
    - [Close a chat session](03-API-Reference/01-Platform-V2-API/30-Chat/04-Close-a-chat-session.md) — Ends the chat session, stopping the AI agent. The session cannot be resumed after this call.
    - [Get chat session history](03-API-Reference/01-Platform-V2-API/30-Chat/05-Get-chat-session-history.md) — Retrieves message history for a chat session. Useful for page reloads or reconnects.
    - [Get presigned upload URL](03-API-Reference/01-Platform-V2-API/30-Chat/06-Get-presigned-upload-URL.md) — Returns a presigned S3 URL for direct file upload from the browser. After uploading, call POST /chat/upload/complete to register the artifact.
    - [Complete file upload](03-API-Reference/01-Platform-V2-API/30-Chat/07-Complete-file-upload.md) — Registers an uploaded artifact after direct S3 upload. Call this after uploading the file to the presigned URL.

    **Realtime**

    - [Create a realtime client token](03-API-Reference/01-Platform-V2-API/31-Realtime/01-Create-a-realtime-client-token.md) — Generates a scoped JWT for browser-side realtime connections.

    **Artifacts**

    - [Create artifact download URLs](03-API-Reference/01-Platform-V2-API/32-Artifacts/01-Create-artifact-download-URLs.md) — Returns fresh presigned URLs after verifying each artifact against its server-authored message and the caller's workflow permissions.
    - [\[Deprecated\] Resolve artifact download URLs](03-API-Reference/01-Platform-V2-API/32-Artifacts/02-Deprecated-Resolve-artifact-download-URLs.md) — This endpoint is deprecated and is scheduled to stop working on October 15, 2026 at 12:00 UTC. Migrate to POST /artifacts/download-urls and provide each artifact's message_id.

    **Voice**

    - [List available voices](03-API-Reference/01-Platform-V2-API/33-Voice/01-List-available-voices.md) — Returns the voice catalog available to the authenticated workspace in this HappyRobot cluster. Use the returned id in workflow agent.voices configuration.
    - [Create a voice call token](03-API-Reference/01-Platform-V2-API/33-Voice/02-Create-a-voice-call-token.md) — Generates a LiveKit token for browser-side voice calls with AI agents. Call this from your backend with your API key, then pass the token to the frontend. Use workflow_id to start a new call, or session_id to silently listen to an in-progress call. Set should_takeover to true to take over the call i…

    **Signals**

    - [List signal keys for the org](03-API-Reference/01-Platform-V2-API/34-Signals/01-List-signal-keys-for-the-org.md) — Returns all configured custom signal keys for nodes in the API key org.
    - [Add a custom signal key to node](03-API-Reference/01-Platform-V2-API/34-Signals/02-Add-a-custom-signal-key-to-node.md) — Appends a custom signal key to the target node configuration in all environments.
    - [Delete a custom signal key from node](03-API-Reference/01-Platform-V2-API/34-Signals/03-Delete-a-custom-signal-key-from-node.md) — Removes a custom signal key from the target node configuration in all environments.
    - [Publish an immediate signal](03-API-Reference/01-Platform-V2-API/34-Signals/04-Publish-an-immediate-signal.md) — Publishes a signal to internal signal service. payload.org_id is always derived from API key org. Built-in keys (org., usecase., session.) are allowed for targeting active sessions.
    - [Schedule a delayed signal](03-API-Reference/01-Platform-V2-API/34-Signals/05-Schedule-a-delayed-signal.md) — Schedules a delayed signal in internal signal service. payload.org_id is always derived from API key org.
    - [Delete a scheduled signal](03-API-Reference/01-Platform-V2-API/34-Signals/06-Delete-a-scheduled-signal.md) — Cancels a scheduled signal.
    - [Patch a scheduled signal](03-API-Reference/01-Platform-V2-API/34-Signals/07-Patch-a-scheduled-signal.md) — Updates a scheduled signal. When payload is provided, payload.org_id is always derived from API key org.

  **Bridge API**


    **Call HappyRobot API**

    - [Carrier Event](03-API-Reference/02-Bridge-API/01-Call-HappyRobot-API/01-Carrier-Event.md) — Create or update a carrier in the system
    - [Load Event](03-API-Reference/02-Bridge-API/01-Call-HappyRobot-API/02-Load-Event.md) — Create one or more loads in the system. This endpoint accepts either a single load object or an array of load objects. The response will match the input format - if you send a single object, you'll receive a single object; if you send an array, you'll receive an array.

    **HappyRobot calls your API**

    - [Get Carrier](03-API-Reference/02-Bridge-API/02-HappyRobot-calls-your-API/01-Get-Carrier.md) — Get details for a specific carrier
    - [Get Load](03-API-Reference/02-Bridge-API/02-HappyRobot-calls-your-API/02-Get-Load.md) — Get details for a specific load
    - [Get Loads](03-API-Reference/02-Bridge-API/02-HappyRobot-calls-your-API/03-Get-Loads.md) — Search for loads matching the given criteria
    - [Log Offer](03-API-Reference/02-Bridge-API/02-HappyRobot-calls-your-API/04-Log-Offer.md) — Record a carrier's offer for a specific load

**Changelog**


  **Changelog**

  - [Release notes](04-Changelog/01-Changelog/01-Overview.md)

---

Fuente: https://docs.happyrobot.ai · Contenido © HappyRobot. Copia para uso interno.
