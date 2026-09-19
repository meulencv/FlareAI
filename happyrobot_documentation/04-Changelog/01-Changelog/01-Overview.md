---
title: "Release notes"
---

# Release notes

<div className="changelog-page">
  <div className="changelog-title">Changelog</div>
  <p style={{opacity: 0.7, marginBottom: "2.5rem"}}>New updates and improvements to HappyRobot.</p>

  <Update label="September 15, 2026">
    ### v3 voices are out of preview

    HappyRobot **v3** voices are now generally available. The voice library shows them with a plain `v3` badge instead of `v3 (preview)`.

    **Who can use this:**\
    Every workspace browsing the voice library. See [Voices](../../01-Developer-Guide/14-Assets/04-Voices.md).
  </Update>

  <Update label="September 14, 2026">
    ### Shared test suites for prompt and adversarial tests

    A workflow's tests now live on one **Tests** page, and a single suite can hold both prompt tests and adversarial tests, run them together, and report one set of results.

    **What's new:**

    * **Evals > Tests** lists every test and suite for the workflow, with **All / Prompt / Adversarial** filters, folders, search, and a toggle to group tests under the prompt or agent they target
    * **Run > All tests** or **Run > Selected tests** starts tests in bulk against the version you have selected
    * Suites are built **Manually** from existing tests, or **AI-assisted** from a generation prompt — up to 10 tests, across the types you pick, scoped to all, selected, or category-filtered northstars, with shared adversary model, environment, timeout, and message guidance for generated adversarial tests
    * A suite's panel adds **Executions** and **Audits** tabs: suite run history with outcome summaries, per-test results, northstar grades, and cancellation for a run in flight
    * Every test has a browsable **Executions** tab with version and failed-only filters, and recent executions appear inline on its row
    * Membership changes preserve definitions and history: a test belongs to one suite at a time, removing a test doesn't delete it, and deleting a suite leaves its tests in place
    * Adversarial test authoring moved to the same place, with an execution scope (**Agent only** or **Full workflow**), additional participant personas, saved seeded node outputs, and northstar grading scope
    * New `Test Suites` and `E2E Scenarios` API resources, exposed in the SDK as `client.testSuites` and `client.e2eScenarios`. `client.adversarialSuites` and `client.adversarialTests` are now read-only history, and the Workflows MCP tools `manage_adversarial_tests` and `manage_adversarial_suites` are retired in favor of the Frontal MCP's `manage_test_suites` and `manage_e2e_scenarios`

    **Who can use this:**\
    Any workflow with tests. See [Test suites](../../01-Developer-Guide/11-Quality-and-Evaluation/08-Test-suites.md) and [Adversarial tests](../../01-Developer-Guide/11-Quality-and-Evaluation/07-Adversarial-tests.md).

    ### A tool that owns a Genesys Transfer always ends the call

    A Genesys Transfer's output variables only reach the Architect flow on the disconnect HappyRobot sends when the agent leaves, so the tool that contains the transfer has to end the call — otherwise the node sends nothing.

    **What's new:**

    * Adding, pasting, or moving a Genesys Transfer under a tool turns on that tool's **End call after execution**, and the toggle can't be turned off while the transfer is there
    * Versions saved before this rule show a warning on the transfer node and are blocked from publishing until the owning tool ends the call, with the block naming the tool

    **Who can use this:**\
    Workflows using the [Genesys Audio Connector](../../01-Developer-Guide/15-Integrations/04-Communication/05-Genesys-Audio-Connector.md#handing-the-call-back-to-architect).

    ### Voice agents default to GPT-5.6 Luna as the secondary model

    The **Secondary model** on a voice agent's prompt node now defaults to **GPT-5.6 Luna** through Azure, replacing GPT-4.1.

    **What's new:**

    * Nodes left on the default follow the new platform default; a node that explicitly selected a model keeps it
    * Pick any other model to override it, or choose **None** to run on the primary model alone

    **Who can use this:**\
    Every voice agent. See [Secondary model](../../01-Developer-Guide/05-Voice-Agents/05-STT-TTS-and-LLM-Configuration.md#secondary-model).

    ### Templatable email sender display name

    The **Display name** recipients see in an email agent's `From` header now accepts variables, so one workflow can send under a different sender identity per run.

    **What's new:**

    * Every sender configuration has the field — both direct strategies, all three transactional sending services, and the Gmail/Outlook direct path
    * SendGrid and Postmark now show the sender identity fields on inbound agents too, and require them only for outbound

    **Who can use this:**\
    Any email agent. See [Sender display name](../../01-Developer-Guide/06-Text-Agents/04-Email.md#sender-display-name).

    ### Update integration credentials through the API

    `PUT /integrations/{integration_id}/credentials/{credential_id}` replaces a form-based credential's title and data while keeping its ID, so workflows that reference it keep working.

    **What's new:**

    * Send the same complete payload as creation; omitted `tag_ids` preserve existing tags and an empty array removes them
    * OAuth credentials still have to be authorized in the platform UI — the endpoint returns `405`
    * Secrets are never returned in a response

    **Who can use this:**\
    Any API key with integration access. See [Managing credentials through the API](../../01-Developer-Guide/15-Integrations/02-Credentials.md#managing-credentials-through-the-api).
  </Update>

  <Update label="September 13, 2026">
    ### Paste a JSON payload into the manual trigger

    The manual trigger dialog now has **Builder** and **JSON** tabs, so you can test a webhook workflow with a real payload instead of retyping it field by field.

    **What's new:**

    * **JSON** gives you the whole payload in a code editor with syntax highlighting and a **Format** button — the practical way to send nested objects and arrays
    * The tabs stay in sync: switching to **JSON** renders what you typed in the builder, and switching back reads your JSON into the builder's fields
    * Invalid JSON is reported inline, and blocks both the tab switch and the trigger until you fix it
    * Available on webhook, predefined request, incoming hook, and workflow function triggers

    **Who can use this:**\
    Any live workflow version you can preview. See [The manual trigger dialog](../../01-Developer-Guide/02-Workflows/05-Triggers.md#the-manual-trigger-dialog).
  </Update>

  <Update label="September 12, 2026">
    ### Call a workflow without waiting for it

    A **Fire and forget** toggle on the Call Workflow node starts the target workflow and lets the parent carry straight on.

    **What's new:**

    * The node returns the child's run ID and continues immediately — no response node required on the target
    * **Timeout** is disabled, and **Gracefully handle errors** and **Test output** are hidden, since there's no response to wait for, type, or branch on
    * The node no longer reports as incomplete when no sample response node is selected

    **Who can use this:**\
    Any V3 workflow with a Call Workflow node. See [Fire and forget](../../01-Developer-Guide/03-Core-Nodes/12-Call-Workflow.md#fire-and-forget).

    ### You can only grant the access you hold

    Member, API key, and role changes are now bounded by the caller's own grants, enforced on the server.

    **What's new:**

    * Inviting or re-scoping a member requires every action in the assigned role across everywhere the proposed scope reaches — and, when editing an existing member, the ability to delegate their current grants too
    * Creating, updating, or revoking an organization API key follows the same rule against the key's grants
    * Creating or updating a role requires each of its actions across the whole scope that owns the role, because a role edit changes every assignment of it; the denial names the role
    * **API key management** is no longer a full-workspace-only action, so it can be held through a Scope Tag grant and stays bounded by that scope
    * The rules apply through the UI, the API, and Frontal alike

    **Who can use this:**\
    Every workspace. See [Delegation limits](../../01-Developer-Guide/16-Account-and-Settings/03-Custom-Roles.md#delegation-limits).

    ### Ask Frontal why a northstar is failing

    Frontal can read the [audit remarks](../../01-Developer-Guide/11-Quality-and-Evaluation/03-Automated-audits.md) behind your quality numbers, so you can investigate a failing northstar in conversation.

    **What's new:**

    * List a workflow's remarks filtered by northstar, grade, or status, and open any single remark in detail
    * Frontal pulls the run's transcript, tool calls, workflow version, and prompt when the remark alone isn't enough to explain the behavior
    * Access is read-only, and Frontal separates what the auditor found from its own interpretation

    **Who can use this:**\
    Any workflow with northstars and audits enabled. See [Investigate northstar audit results](../../01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md#investigate-northstar-audit-results).

    ### Connected integrations come first in node search

    Searching the node menu now ranks events from integrations you've already connected above the rest, so the provider you actually use wins over same-named events from providers you haven't set up. See [Add nodes](../../01-Developer-Guide/02-Workflows/02-Creating-a-Workflow.md#add-nodes).
  </Update>

  <Update label="September 11, 2026">
    ### Frontal asks clarifying questions you can click

    In Plan mode, Frontal now asks the questions that would change its plan through an interactive widget instead of a paragraph of prose.

    **What's new:**

    * A **Questions** card appears above the chat input with up to three questions, each offering two to four options and a short note on what each option implies
    * Unless the choices are exhaustive, an **Other…** field takes an answer in your own words
    * Step through with **Next** and **Previous**, then **Submit** to send every answer at once; **Cancel** or simply typing a message dismisses the card
    * Accepting a plan card now switches the chat to **Build** mode as it starts applying the plan

    **Who can use this:**\
    Everyone with access to Frontal. See [Clarifying questions](../../01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md#clarifying-questions).

    ### Frontal can plan your tag architecture

    Frontal can design a workspace's [Scope Tag](../../01-Developer-Guide/16-Account-and-Settings/04-Scope-Tags.md) vocabulary before anything is created.

    **What's new:**

    * **Tag with Frontal** on **Settings > Tags** opens the assistant in Plan mode with the workspace tags skill attached
    * Frontal reads your existing tags and resource assignments, asks how access should be divided, and publishes a read-only **Tag architecture draft** — a tree of proposed tag types and nesting with a summary
    * Revise the draft as many times as you like; nothing is written until you click **Accept plan**, which switches to Build mode and creates the vocabulary
    * Creating the tags and assigning them to resources stay separate steps, so assignments come afterwards in small reviewable batches
    * The Tags page itself now renders the tag hierarchy inline

    **Who can use this:**\
    Workspaces that own their tag vocabulary. See [Plan a tag structure with Frontal](../../01-Developer-Guide/16-Account-and-Settings/04-Scope-Tags.md#plan-a-tag-structure-with-frontal).

    ### Run details show which version ran

    The run details panel header now names the workflow version between the run ID and the step count, so you can tell which version produced a result without cross-checking the table. See [Run details panel](../../01-Developer-Guide/09-Runs-and-Monitoring/01-Runs-Overview.md#run-details-panel).

    ### See what's tagged in every workspace

    **Show resources** on the Tags page — which expands each tag to list the resources carrying it — is now available in every workspace, not only child workspaces of a parent organization. See [Review tag coverage](../../01-Developer-Guide/16-Account-and-Settings/04-Scope-Tags.md#review-tag-coverage).
  </Update>

  <Update label="September 10, 2026">
    ### API keys can expire, and organizations can require it

    Organization API keys now carry an expiration date, and owners can cap how long any key in the workspace stays valid.

    **What's new:**

    * The create-key dialog asks for an **Expiration**: 30, 60, 90, or 180 days, 1 year, or **Never**
    * The key table has an **Expires** column, showing a date, **Never**, or **Pending revocation** for a key already past its expiry
    * **Enable API Key Retention** under **Settings > General** sets a **Maximum Key Age** that binds both organization and personal keys, and removes **Never** from the picker
    * Tightening the policy shows how many existing keys are affected, with an **Affected API Keys** dialog comparing current and new effective expiry — keys already past the limit are revoked within the hour
    * `GET /api-key/describe` returns `expiresAt`, already reduced to the organization's maximum key age

    **Who can use this:**\
    Every workspace. See [Expiration](../../01-Developer-Guide/16-Account-and-Settings/06-API-Keys.md#expiration) and [API key retention](../../01-Developer-Guide/16-Account-and-Settings/01-Organization.md#api-key-retention).

    ### Webhook nodes can send multipart form data

    A Webhook node can now send `multipart/form-data`, so a workflow can upload files to an API instead of only describing them.

    **What's new:**

    * Selecting `multipart/form-data` replaces the body editor with a list of **fields**, sent in the order you list them
    * Each field is **Text** (the value as a form field) or **File** (uploads the artifact the value points to — an artifact ID or a file variable)
    * A file field whose value resolves to a list of artifacts sends one file part per artifact, and field names can repeat
    * Fields have individual enable toggles; the node won't save until every enabled field has a name and every file field has a file reference

    **Who can use this:**\
    Any workflow with a Webhook node. See [Multipart form data](../../01-Developer-Guide/03-Core-Nodes/06-Webhook.md#multipart-form-data).

    ### Client certificates (mTLS) for webhooks

    Webhook nodes can present a client certificate to endpoints that require mutual TLS.

    **What's new:**

    * A new **Client Certificate (mTLS)** credential type under **Settings > Integrations > OAuth 2.0** takes a client certificate, a private key, and an optional private CA certificate as PEM
    * All three fields are write-only — once saved they can only be replaced, so HappyRobot validates the PEM blocks and checks that the key matches the certificate at save time rather than failing on the first run
    * Select the credential in a Webhook node's request settings, alongside whatever authentication method the endpoint uses, or reference it with a variable

    **Who can use this:**\
    Any workflow with a Webhook node. See [Client certificates (mTLS)](../../01-Developer-Guide/15-Integrations/02-Credentials.md#client-certificates-mtls).

    ### One Tests page per workflow

    **Custom Tests** and **Adversarial** are now a single **Tests** item in the workflow sidebar.

    **What's new:**

    * One page at `/tests` holds both test types, with **All / Prompt / Adversarial** toggles that show a count each
    * A flat list is the default, with a breadcrumb on every row showing which agent and prompt the test belongs to; a view toggle switches back to the tree grouped by workflow structure
    * Folders are shared across test types, so one folder can hold prompt and adversarial tests. Tests outside a folder are listed alongside the folders, and folders with nothing matching the active filter are hidden
    * **New** creates a test (then **Prompt** or **Adversarial**), a suite, or a folder
    * Search covers test, prompt, and agent names

    **Who can use this:**\
    Every workflow. See [The Tests page](../../01-Developer-Guide/11-Quality-and-Evaluation/06-Custom-tests.md#the-tests-page).

    ### Test OAuth 2.0 credentials before saving them

    An **API Client** credential is now verified against the token endpoint before it's stored.

    **What's new:**

    * **Test Connection** on the API Client form requests an access token with the values on screen and discards it — nothing is saved and the token never reaches the browser
    * A failure shows the error the authorization server returned, so the token URL, client ID, secret, or scope can be fixed in place
    * Editing a field after a successful test clears the result, so a saved credential is always one that worked

    **Who can use this:**\
    Anyone who manages integrations. See [Testing an API Client credential before saving](../../01-Developer-Guide/15-Integrations/02-Credentials.md#testing-an-api-client-credential-before-saving).

    ### Agents can stay silent without saying "Mhmm"

    The **Stay silent** built-in tool now has a **Play acknowledgement** sub-setting.

    **What's new:**

    * On by default, matching today's behavior: the agent says a short "Mhmm." before going quiet, so the caller knows the line is live
    * Turn it off for complete silence — useful when the caller is reading out a long list of numbers and shouldn't be interrupted at all

    **Who can use this:**\
    Voice agents with **Stay silent** enabled. See [Stay silent](../../01-Developer-Guide/04-Tools/04-Built-in-Tools.md#voice-agent-built-in-tools).

    ### List organization members through the API

    **What's new:**

    * `GET /org/members` returns the members of the authenticated organization with their public profile and workspace-wide role
    * `role` is `null` for a member who only holds Scope Tag grants
    * Listing requires the view-workspace-members action

    **Who can use this:**\
    Any workspace with an API key. See [List members](../../01-Developer-Guide/16-Account-and-Settings/02-Members-and-Access.md#list-members).

    ### Tool parameters as runs table columns

    Custom columns can now surface tool call **parameters**, including the parameters of tools from a connected [MCP server](../../01-Developer-Guide/04-Tools/05-MCP-Tools.md). Because parameters are inputs rather than outputs, they're read from the node's input when no matching output exists — so a column on an MCP tool's argument populates with the values the agent actually passed. See [Custom columns](../../01-Developer-Guide/09-Runs-and-Monitoring/01-Runs-Overview.md#custom-columns).
  </Update>

  <Update label="September 9, 2026">
    ### Sign in and land where you left off

    Opening HappyRobot now returns you to the workspace you used last instead of always resolving to your default one.

    **What's new:**

    * Your last visited workspace is remembered across devices and browsers, so the root URL redirects there on your next sign-in
    * Switching workspaces updates the destination immediately

    **Who can use this:**\
    Everyone with access to more than one workspace.

    ### Listen to a live call without taking it over

    You can now listen in on a call that's still in progress. The AI agent keeps handling it and nobody on the call is told you're there.

    **What's new:**

    * A **Live call** bar replaces the recording player at the top of a run's **Details** tab while a voice session is live — click **Listen now** to hear the conversation
    * You join hidden and without a microphone, so listening changes nothing about the call; several people can listen to the same call at once
    * The bar reports its own state: **Listening live**, **Audio paused** when the browser blocks playback, **Reconnecting audio**, and **Call ended**
    * Listening only needs permission to view the workflow's runs, a lower bar than taking a call over
    * In the SDK, `client.voice.createToken({ session_id })` without `should_takeover` returns an observer token, and the browser client's new `voice.listen()` joins without publishing audio. `should_takeover: true` keeps the existing takeover behavior

    **Who can use this:**\
    Any voice workflow. See [Listening to a call in progress](../../01-Developer-Guide/09-Runs-and-Monitoring/04-Recordings.md#listening-to-a-call-in-progress) and [Listen to a live call](../../02-Developer-Tools/02-TypeScript-SDK/04-Voice-call-tutorial.md#listen-to-a-live-call).

    ### Toll-free SMS numbers on Telnyx

    US and Canadian toll-free numbers can now be bought on Telnyx, not just Twilio.

    **What's new:**

    * **Toll-Free** is offered for US/CA numbers on Telnyx, and buying one submits the toll-free verification in the same step
    * Telnyx requires business registration number, authority, and country for **every** business type, including sole proprietors, and requires an opt-in image URL
    * The verification form validates against the selected provider's rules, so requirements are enforced before submission rather than rejected by the carrier later

    **Who can use this:**\
    Workspaces buying numbers on Telnyx. See [US and Canadian toll-free numbers](../../01-Developer-Guide/14-Assets/03-Telephony.md#us-and-canadian-toll-free-numbers).
  </Update>

  <Update label="September 8, 2026">
    ### Voice agents can fall back to a second model mid-turn

    A voice agent's prompt node now exposes the **Secondary Model** that keeps a turn from stalling when the primary model runs slow.

    **What's new:**

    * The secondary model only takes over a turn once the primary passes a latency threshold — otherwise the primary answers and the secondary result is discarded
    * Leave it on the default (`gpt-4.1` through Azure, shown as **Default · Azure**), pick any model available to your organization, or choose **None** from the source menu to run on the primary alone
    * The field accepts a variable, so the fallback can be chosen per call
    * Primary and secondary must be different model families; picking the same family for both is rejected
    * Messages the secondary answered carry an **LLM fallback** badge in the run transcript, and the tooltip names the provider and model that produced them

    **Who can use this:**\
    Inbound, outbound, and outbound-with-callback voice agents. See [Secondary model](../../01-Developer-Guide/05-Voice-Agents/05-STT-TTS-and-LLM-Configuration.md#secondary-model).

    ### API keys carry their own roles and scopes

    An organization API key is now its own access principal, so what a key can do no longer depends on who created it.

    **What's new:**

    * The create dialog asks for access grants alongside the name — pair a role with the full workspace or with [Scope Tags](../../01-Developer-Guide/16-Account-and-Settings/04-Scope-Tags.md), and add as many grants as the integration needs
    * New keys start at **Viewer** on the full workspace
    * The key row's **⋯** menu gained an **Edit** action for changing a key's name and access without rotating the key value; **Revoke** moved into the same menu
    * Keys get no HappyRobot-staff bypass and no parent-organization fallback — a key reaches only the workspace it belongs to
    * Keys that rely on tag grants are counted as blockers when disabling **Tags as access scopes**, and appear in the affected-principals list when deleting a tag
    * Keys that existed before this change were granted **Owner** on the full workspace, matching the access they already had

    **Who can use this:**\
    Workspaces on HappyRobot-managed RBAC. See [Access grants for organization keys](../../01-Developer-Guide/16-Account-and-Settings/06-API-Keys.md#access-grants-for-organization-keys).

    ### Twin permissions split into data, schema, and infrastructure

    Twin access is no longer all-or-nothing: editing rows, reshaping the schema, and administering the database instance are separately grantable.

    **What's new:**

    * Three new role actions — **Edit Twin data**, **Manage Twin schema**, and **Manage Twin database instance** — join **View Twin**
    * **Full Twin access** now covers all three plus unrestricted SQL execution in the SQL console, and selects the narrower actions automatically
    * The Twin UI follows the grants: read-only tables explain why editing is unavailable, and schema, polling, dump, and capacity controls appear only for the matching action
    * Roles that already had Twin management keep all three capabilities; the **Editor** system role receives **Edit Twin data**

    **Who can use this:**\
    Any workspace with Twin. See [Permissions](../../01-Developer-Guide/08-Twin/01-Twin-Overview.md#permissions).

    ### Different app environment variable values in Preview and Production

    An app's environment variables now hold a separate value per environment instead of one value shared across both.

    **What's new:**

    * Give a variable a **Production** value, a **Preview** value, or both, and remove either one without deleting the variable
    * Editing shows **Unchanged** as the placeholder — leave a field blank to keep the stored value
    * Preview values become configurable once the app has a Preview deployment
    * The sandbox and the downloaded `.env.local` use Preview values when the app has a Preview deployment, and Production values otherwise; restart the sandbox to pick up a change
    * Adding a key that already exists now says so instead of silently overwriting

    **Who can use this:**\
    Next.js Full-Stack apps. See [Values by environment](../../01-Developer-Guide/07-Apps/07-Environment-Variables.md#values-by-environment).

    ### Duplicate a workflow into any folder

    The duplicate dialog gained a **Destination folder**, so a copy no longer has to land next to the original.

    **What's new:**

    * Pick any folder you can create workflows in, or the workspace root; the field defaults to the source workflow's folder
    * Destinations are filtered by your permissions and by whether the copy's Scope Tags are allowed there — when nothing is available, the dialog says so instead of failing on submit
    * The name conflict message now explains that workflow names are unique across all folders in the organization

    **Who can use this:**\
    Anyone who can create workflows. See [Duplicating a workflow](../../01-Developer-Guide/16-Account-and-Settings/10-Workflow-Settings.md#duplicating-a-workflow).

    ### Organization-level credits in the usage API

    `GET /billing/usage/credits` now returns the consumption that isn't attributable to a workflow, so API totals reconcile with the Usage page.

    **What's new:**

    * Consumption shown as **Platform & Services** in **Settings > Usage** is returned as a row with an empty `workflow_id`, `workflow_name`, and `folder_path`
    * The empty `workflow_id` is the discriminator, since a real workflow may legitimately be named "Platform & Services"
    * The row is returned only to callers with workspace-level usage or billing access, and can't be selected or excluded through the endpoint's filters

    **Who can use this:**\
    Any workspace with an API key. See [Usage and Billing](../../01-Developer-Guide/16-Account-and-Settings/09-Usage-and-Billing.md).

    ### Jump to any page from the tab strip

    The **+** button in the tab strip opens a searchable list of destinations instead of cloning the page you're on.

    **What's new:**

    * Search across the current workspace's pages, its workflows, and your open tabs
    * Choosing an already-open tab switches to it; anything else opens in a new tab
    * Results never cross into another organization

    **Who can use this:**\
    Everyone, inside a workspace.

    ### MCP tools copy together with their server call

    Copying an MCP tool now keeps the tool node and its child MCP Call node together, so the pasted tool still works.

    **What's new:**

    * Selecting an MCP tool without its MCP Call node is no longer a valid copy, and the MCP Call node can't be copied on its own
    * Pasting a prompt is restricted to agent nodes, so a prompt can't land somewhere it would never run

    **Who can use this:**\
    Any workflow using [MCP tools](../../01-Developer-Guide/04-Tools/05-MCP-Tools.md#copying-mcp-tools).
  </Update>

  <Update label="September 6, 2026">
    ### See which resources carry which tags

    **Settings > Tags > All tags** has a **Show resources** toggle that turns the tag tree into a coverage view, so you can find untagged resources without opening each one.

    **What's new:**

    * Every tag expands into the resources tagged with it, grouped by kind — workflows and folders, phone numbers, node and prompt components, integration credentials, knowledge bases, apps, and Twin
    * Solid badges mark tags assigned directly; outlined badges mark tags inherited from a workflow folder
    * An **Untagged resources** section lists everything with no effective tag, grouped by type with a count per group
    * Search covers resource names, resource types, and tag names, not just tags
    * Drag a resource onto a tag and choose **Add**, **Move**, or **Replace all** to change its assignment in place
    * Inherited tags are shown but can't be moved from here, and resource types your role can't view are reported as incomplete rather than silently dropped

    **Who can use this:**\
    Workspaces that belong to a parent organization. See [Review tag coverage](../../01-Developer-Guide/16-Account-and-Settings/04-Scope-Tags.md#review-tag-coverage).

    ### Stage roles, tags, and grants before leaving legacy SSO RBAC

    Organizations still on legacy SSO RBAC can now build their HR SSO Grants model in advance instead of doing it during the cutover.

    **What's new:**

    * The Roles, Tags, and SSO Access pages show a **Legacy SSO RBAC is still active** banner and allow creating and editing tags, custom roles, and HR SSO grants
    * Staged definitions are saved but don't affect access until legacy SSO RBAC is turned off
    * The Grant Builder offers tag scopes while staging, so you can generate the group names your IdP needs
    * The cutover toggles — **Resolve incoming group names as grants** and the parent **Tags as access scopes** setting — stay hidden until legacy mode is off

    **Who can use this:**\
    Organizations on legacy SSO RBAC. See [Stage the new model before the cutover](../../01-Developer-Guide/16-Account-and-Settings/05-SSO-Access.md#stage-the-new-model-before-the-cutover).
  </Update>

  <Update label="September 5, 2026">
    ### Choose the environment an MCP Call node introspects

    The **MCP Call** node has its own **Environment for schema generation** selector, so it no longer has to follow the trigger's testing environment.

    **What's new:**

    * Choose **Default**, **Development**, **Staging**, or **Production** on the node
    * **Default** keeps the previous behavior — the workflow's testing environment, or **Development** when it isn't set
    * Only schema generation is affected; runtime still uses the version's environment

    **Who can use this:**\
    Any workflow with an MCP tool. See [Environment for schema generation](../../01-Developer-Guide/04-Tools/05-MCP-Tools.md#environment-for-schema-generation).
  </Update>

  <Update label="September 4, 2026">
    ### WhatsApp numbers move into Telephony, on one row per number

    **Assets > Telephony > Phone Numbers** now shows one row per phone number, with every provider that carries it on the same row. Everything that used to live on the WhatsApp integration's **Cloud Migration** tab moved here.

    **What's new:**

    * A **Providers** column badges each connection on a number — Twilio, Telnyx, WhatsApp, SIP — so a number you own in more than one place stops appearing twice
    * Separate **Calling Status** and **Messaging Status** columns, each rolling up every provider; hover for the per-provider inbound/outbound breakdown and the reason a capability isn't synced
    * A **Usage** column with a dot per environment the number is published in, replacing the environment you used to set by hand
    * WhatsApp actions live on the row's **…** menu: **Register number**, **Sync messaging** (with Meta's SMS or voice verification inline), and **Sync calling**
    * The **Add New** menu no longer carries WhatsApp entries, and the WhatsApp integration's **Cloud Migration** tab links here instead
    * A **Sync phone numbers** button refreshes the registry from your providers on demand; the page also syncs when you open it
    * Tags now apply to a number as a whole rather than to its SIP trunk, so WhatsApp numbers and numbers without a trunk can be scoped
    * A new **Free number** action detaches a number from every non-live use case at once
    * Workflow number pickers list one option per working provider connection, and only when its calling is **Synced**

    **Who can use this:**\
    Any workspace managing phone numbers. See [Phone numbers](../../01-Developer-Guide/14-Assets/03-Telephony.md#phone-numbers) and [WhatsApp numbers](../../01-Developer-Guide/14-Assets/03-Telephony.md#whatsapp-numbers).

    ### Start a custom role from Owner, Editor, or Viewer

    **Duplicate** is now available on the system roles, not just your own.

    **What's new:**

    * Duplicating **Owner**, **Editor**, or **Viewer** opens the role editor pre-filled with that role's action list
    * The copy is an ordinary custom role — editable, archivable, and independent of the system role it came from
    * **Edit** and **Archive** still apply to custom roles only

    **Who can use this:**\
    Anyone who can edit the role catalog. See [Edit, duplicate, or archive a role](../../01-Developer-Guide/16-Account-and-Settings/03-Custom-Roles.md#edit-duplicate-or-archive-a-role).
  </Update>

  <Update label="September 3, 2026">
    ### New workspace navigation: tabs, a unified sidebar, and Command-K

    The app shell was rebuilt around clearer product areas, a single workspace tree, and browser-style tabs.

    **What's new:**

    * Pages you open stay in a **tab strip** — drag to reorder, right-click to pin, group, rename, re-icon, duplicate, or close. Tabs are saved to your account and survive a reload
    * **Settings > Profile** adds tab preferences: whether tabs are shared globally, per parent org, or per workspace; whether navigating reuses a matching open tab; and whether main destinations auto-pin
    * The sidebar groups pages under the products you can access — **Frontal**, **Workflows**, **Twin**, **Interfaces**, **Integrations** — each with its own sub-navigation
    * One **Workspace** tree now holds workflows, apps, and components together, at the root or in folders. Filter which types it shows, create from the **+** menu, and drag items between folders
    * Resources inherit [Scope Tags](../../01-Developer-Guide/16-Account-and-Settings/04-Scope-Tags.md) from their folder trail, and direct tags stay distinct from inherited ones
    * **Cmd/Ctrl + K** opens a permission-aware command menu over pages, resources, workspaces, open tabs, and actions
    * Saved links and bookmarks are unaffected

    **Who can use this:**\
    Everyone. See [Navigating the platform](../../01-Developer-Guide/01-Get-Started/04-Navigating-the-platform.md).

    ### Arabic voices from Munsit

    **Munsit** joins HappyRobot, ElevenLabs, and Cartesia as a text-to-speech provider, specialized in Arabic.

    **What's new:**

    * Four Emirati Munsit voices — **Majed**, **Abdulaziz**, **Aisha**, and **Noor** — are available to every workspace
    * Munsit voices speak Arabic and handle Arabic–English code-switching, and support per-voice **speed** and **gain**
    * The language filter distinguishes Arabic (Emirati) `ar-AE`, Arabic (Saudi) `ar-SA`, and Arabic (Gulf / Khaleeji) alongside Modern Standard Arabic `ar-001`

    **Who can use this:**\
    Every workspace, from **Assets > Voices**. See [Arabic voices](../../01-Developer-Guide/14-Assets/04-Voices.md#arabic-voices).

    ### Cap how long a text conversation can run

    Text agents get a **Maximum session duration** setting next to the idle timeout.

    **What's new:**

    * Set a whole number of minutes between 1 and 525600 (one year), or leave it empty for no maximum
    * Timing starts when the session opens — after the initial message for outbound agents — and messages, reminders, and tool calls do not reset it
    * When the cap is reached the agent closes the conversation silently and the workflow moves on
    * The field accepts [variables](../../01-Developer-Guide/02-Workflows/07-Variables.md), so the cap can come from trigger data

    **Who can use this:**\
    Any inbound or outbound text agent. See [Maximum session duration](../../01-Developer-Guide/06-Text-Agents/01-Text-Agents-Overview.md#maximum-session-duration).

    ### Map your existing IdP group names to HR SSO Grants

    A configured grant can now carry an **alias**, so you don't have to create HappyRobot's canonical `HR:` groups in your identity provider.

    **What's new:**

    * **Add custom alias** under a generated group name in the Grant Builder attaches one IdP group name to that grant
    * The picker suggests your parent organization's existing policies and your legacy SSO RBAC group names, and accepts anything else you type
    * At login or directory sync, a claimed group matching an alias resolves exactly like the canonical name, so you can migrate gradually
    * Removing an alias leaves the grant in place

    **Who can use this:**\
    Workspaces and parent organizations on HR SSO Grants. See [Reuse an existing IdP group name](../../01-Developer-Guide/16-Account-and-Settings/05-SSO-Access.md#reuse-an-existing-idp-group-name).
  </Update>

  <Update label="September 2, 2026">
    ### Loop iterations are paginated in the run graph

    The **Graph** tab of a run no longer tries to draw every iteration of a large loop at once.

    **What's new:**

    * When a run's graph has more than 100 nodes, loop iterations are paginated — the graph shows one iteration at a time and the loop node carries a pager with the selected iteration and the total
    * Step through iterations with the arrows, or click the chevron and type an iteration number to jump straight to it
    * Nested loops each get their own pager, so you can open one iteration of an outer loop and page through the inner loop inside it
    * Smaller graphs are unchanged and still show every iteration at once

    **Who can use this:**\
    Any run that expands a [Loop](../../01-Developer-Guide/03-Core-Nodes/10-Loops.md) inline. See [Loop iterations in large graphs](../../01-Developer-Guide/09-Runs-and-Monitoring/01-Runs-Overview.md#loop-iterations-in-large-graphs).
  </Update>

  <Update label="September 1, 2026">
    ### Translate a run transcript

    Runs in a language you don't read can now be translated in place, without leaving the platform.

    **What's new:**

    * **Translate this run** in the **⋯** menu on a session header rewrites every message into your browser's language; **Show original** switches back
    * Translation runs on your device using your browser's built-in translation models — no run data is sent to a translation service
    * The source language is detected per message, so runs that mix languages still translate, including transcripts from earlier dial attempts
    * The action is hidden when the transcript is already in your browser's language
    * Turn on **Automatically translate run transcripts** in your profile preferences to translate every run whose language models are already downloaded

    **Who can use this:**\
    Voice and text runs, in browsers that expose on-device translation and language detection. See [Translating a transcript](../../01-Developer-Guide/09-Runs-and-Monitoring/03-Transcripts-and-Messages.md#translating-a-transcript).

    ### API keys enforce workspace permissions

    The API now answers every request with the same permission model as the platform UI.

    **What's new:**

    * An **organization key** has full access to its own workspace and can never reach another workspace or a parent organization
    * A **personal key** is limited to its owner's role, custom-role actions, and [Scope Tags](../../01-Developer-Guide/16-Account-and-Settings/04-Scope-Tags.md) — list endpoints return only the records that member can see, and changing their grants changes the key's reach
    * Coverage now includes contacts, integrations, signals, quality issues, Twin, voices, and organization details, alongside workflows, runs, and sessions
    * The run stream is filtered the same way: a personal key only receives updates for runs it may view
    * Requests outside a key's permissions return `403`; requests for a specific record the key cannot view return `404`

    **Who can use this:**\
    Every API and SDK caller. See [What a key can access](../../01-Developer-Guide/16-Account-and-Settings/06-API-Keys.md#what-a-key-can-access).

    ### Delete a Twin workflow dump from the API or an assistant

    Stopping a [workflow run dump](../../01-Developer-Guide/08-Twin/04-Workflow-Run-Dumps.md) no longer requires dropping its table by hand.

    **What's new:**

    * `DELETE /twin/dump/{tableName}` removes the run-capture configuration and keeps the table and its rows; add `?dropTable=true` to also drop the table and all its data
    * The Twin MCP server exposes the same operation as `delete_workflow_dump`, and asks you to confirm before it runs — use it instead of `drop_table` for dump tables so the capture config goes away with the table
    * A table can hold only one dump configuration, so re-creating a dump for a table updates the existing one instead of adding a second

    **Who can use this:**\
    Any workspace with a Twin database. See [Deleting a dump](../../01-Developer-Guide/08-Twin/04-Workflow-Run-Dumps.md#deleting-a-dump) and [Twin MCP](../../02-Developer-Tools/01-MCP/04-Twin-MCP.md).

    ### Frontal finds the right skill on its own

    You no longer have to remember to attach a [skill](../../01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md#skills) before asking Frontal for something it covers.

    **What's new:**

    * Every chat receives a catalog of the skills available to you — names and descriptions only — and Frontal loads a skill's content itself when your request clearly matches its description
    * Up to 3 skills are loaded per message; skills you attached manually stay active and are never loaded twice
    * Descriptions now decide when a skill applies, so writing "Use when editing voice agent prompts" makes a skill discoverable
    * Skill content is never quoted back to you — Frontal describes the resulting guidance instead

    **Who can use this:**\
    Everyone with access to Frontal. See [Automatic skill discovery](../../01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md#automatic-skill-discovery).

    ### Inline images in email previews

    The **Preview** tab of an inbound email now renders the images the sender embedded in the body — signature logos, pasted screenshots — instead of dropping them.

    **What's new:**

    * Embedded images are resolved when you open the message, so previews keep working for old runs
    * An image HappyRobot could not retrieve shows a placeholder rather than a broken image

    **Who can use this:**\
    Any run with an inbound email. See [Text agent transcripts](../../01-Developer-Guide/09-Runs-and-Monitoring/03-Transcripts-and-Messages.md#text-agent-transcripts).

    ### Saved MCP server secrets survive a re-test

    Testing or refreshing an existing [MCP server credential](../../01-Developer-Guide/04-Tools/06-MCP-Server-Setup.md) no longer requires re-entering its token.

    **What's new:**

    * Stored auth tokens and custom header values are shown as `••••••••`; leave them alone and **Test**, **Refresh**, and **Save** reuse the stored secret
    * A Staging or Development token left empty still falls back to the Production value
    * Changing the server URL to an endpoint that isn't stored on any of the credential's tabs requires re-entering the secrets — a saved token is never sent to a new host

    **Who can use this:**\
    Anyone managing MCP server credentials in **Integrations**. See [Editing a saved credential](../../01-Developer-Guide/04-Tools/06-MCP-Server-Setup.md#editing-a-saved-credential).
  </Update>

  <Update label="August 31, 2026">
    ### Tie message feedback to the Northstar it broke

    The feedback control on an assistant message in a run's transcript now asks what kind of problem it is, so a flagged response is tracked against the rule it violated instead of as a generic message issue.

    **What's new:**

    * **Give feedback** on an assistant or rep message offers three kinds: **General issue**, **Violates an existing Northstar**, and **Missing Northstar**
    * The Northstar picker lists only the Northstars that apply to that message — the prompt node's, its prompt components', the agent's, and those of any workflow that called into it — with disabled ones left out
    * Ticking several Northstars creates one issue per Northstar, sharing the priority, correction, and reason you entered
    * The Northstar's name appears as a badge on the issue in the **Flags** table
    * **Missing Northstar** opens Frontal with the response and the workflow version attached, and asks it to check coverage and propose the smallest non-overlapping addition — it reports back rather than making changes
    * Failed audit remarks in the transcript can now be rated **Accurate** or **Inaccurate** inline, without opening the Audits page
    * Hover a user message and click the **flag** icon to report a transcription, end-of-sentence, or interruption problem
    * Audit remarks from northstar-graded [custom tests](../../01-Developer-Guide/11-Quality-and-Evaluation/06-Custom-tests.md) accept feedback too, which they previously refused

    **Who can use this:**\
    Anyone with permission to create issues on the workflow; the Northstar options additionally require permission to view Northstars. See [Giving feedback on a message](../../01-Developer-Guide/09-Runs-and-Monitoring/03-Transcripts-and-Messages.md#giving-feedback-on-a-message) and [Northstar-linked issues](../../01-Developer-Guide/11-Quality-and-Evaluation/05-Issues.md#northstar-linked-issues).

    ### List available voices from the API

    A new `GET /voices` endpoint returns the voice catalog available to your workspace, so you can resolve a voice ID without opening the platform.

    **What's new:**

    * Each voice includes the `id` to use in a workflow's `agent.voices` configuration, plus provider, model family, gender, and the languages and locales it supports
    * The optional `language` filter takes a prefix like `en` to match every accent, or a locale like `en-GB` to match one
    * Available in the TypeScript SDK as `client.voice.list({ language })`

    **Who can use this:**\
    Any API key whose role can view voices. See [Listing voices with the API](../../01-Developer-Guide/14-Assets/04-Voices.md#listing-voices-with-the-api).

    ### Voice filters focus on gender and language

    The **Provider** facet has been removed from the voice library and the workflow voice picker.

    **What's new:**

    * Filter voices by **Gender** and **Language**, and search by name, in both the voice library and the voice picker on an agent node
    * Choosing a voice is now about how it sounds rather than which vendor generates it

    **Who can use this:**\
    Everyone browsing voices. See [Browsing voices](../../01-Developer-Guide/14-Assets/04-Voices.md#browsing-voices).

    ### Cost metrics for experiments

    Experiments can now measure what a variant costs, not just how well it performs.

    **What's new:**

    * A **billing** category of default metrics sums the credits a run consumed: total, voice, voice LLM, voice orchestration, telephony, run, run orchestration, run LLM, and texting credits
    * All billing metrics are numeric and treat lower as better, and use the same taxonomy as the credits in **Settings > Usage**
    * Small metric values keep their precision in the analysis charts and stat grid instead of rounding to zero

    **Who can use this:**\
    Any experiment. See [Billing metrics](../../01-Developer-Guide/10-Experiments/03-Experiment-metrics.md#billing-metrics).

    ### Grant Builder rows are saved for the whole organization

    The HR SSO **Grant Builder** used to keep its rows in your browser, so the group names your organization had modeled were invisible to teammates.

    **What's new:**

    * Rows are stored on the workspace or parent organization and saved as you edit them, so every administrator sees the same configuration
    * Editing rows requires `workspace.settings.update` or `parent-org.settings.update`; view-only access can still read and copy names
    * A tag used by a builder row can no longer be deleted — the delete dialog reports how many rows still reference it, instead of the deletion silently changing the group name that row encodes
    * **Member Groups** renders rows exactly as the builder does, hides empty sections, and omits members with no grants or a suspended role

    **Who can use this:**\
    Organizations using HR SSO Grants. See [Saved builder rows](../../01-Developer-Guide/16-Account-and-Settings/05-SSO-Access.md#saved-builder-rows).

    ### Smaller changes

    * Runs show a **Max call duration reached** event when a call ends because it hit the max call duration configured on the voice agent node
    * User messages in a transcript show an **Echo** badge when the heuristic echo classifier flags likely acoustic echo, alongside the existing Filler, Out of context, and Redundant badges
    * Buying a number through the `manage_phone_numbers` MCP tool now requires `phone_number_type` (`local`, `toll_free`, `national`, or `mobile`) — the assistant asks which type you want instead of failing validation
    * The app import form spells out its GitHub token requirements, and a failed import names the repository it could not read
  </Update>

  <Update label="August 28, 2026">
    ### Use the transcript before or after a transfer

    A voice agent's transcript can now be read in two halves, split at the point the call was handed off to a human.

    **What's new:**

    * `transcript.pre_transfer` (**Transcript Before Transfer**) and `transcript.post_transfer` (**Transcript After Transfer**) appear under the agent node's `transcript` in the `@` picker
    * Reference either one anywhere a variable resolves at runtime — prompts, conditions, and node configuration — for example to extract only what the representative discussed
    * Pointing an AI Extract or AI Classify node at a segment is treated as passing it the transcript, so the node no longer corrects you back to the whole thing
    * The segments are computed at lookup time rather than stored, so they aren't offered as runs-table columns or experiment metric sources

    **Who can use this:**\
    Any workflow with a voice agent that transfers calls. See [Transcript segments on transferred calls](../../01-Developer-Guide/02-Workflows/07-Variables.md#transcript-segments-on-transferred-calls).

    ### Twin storage alerts go to the recipients you choose

    Twin can email a list of addresses you manage yourself when performance reaches a critical threshold.

    **What's new:**

    * An **Email alerts** section in **Settings → Twin Database**, available once the Twin database status is **Available**
    * Enter up to 20 addresses separated by commas or new lines; duplicates and casing are normalized and a counter shows how many you have
    * Any valid address works, including a shared inbox or on-call alias — clear the box and save to turn alerts off

    **Who can use this:**\
    Organizations with a Twin database, for users who can manage Twin settings. See [Email alerts](../../01-Developer-Guide/08-Twin/05-SQL-Console-and-Capacity.md#email-alerts).

    ### Name your chats with the Apps coding agent

    The agent sidebar's session history now lets you rename a chat instead of hunting for it by its original title.

    **What's new:**

    * Hover a chat in **Session history** for a pencil icon; type a new name and press **Enter** to save or **Escape** to cancel
    * Delete is in the same row, and each row shows when the chat was last updated

    **Who can use this:**\
    Anyone editing an App in the sandbox editor. See [Chat history](../../01-Developer-Guide/07-Apps/03-Sandbox-Editor.md#chat-history).
  </Update>

  <Update label="August 27, 2026">
    ### Frontier tier and per-turn limits for text agent media

    Text agent media processing gains a higher-quality tier and builder-configurable limits on what gets processed each turn.

    **What's new:**

    * A **Frontier** option on both the OCR and transcription dropdowns, alongside Standard and Advanced. Frontier OCR reads the document with a frontier vision model rather than a dedicated OCR engine, which helps most on messy scans and context-dependent content
    * Language hints are available on Frontier transcription as well as Advanced
    * A new **Advanced limits** section sets max files per turn (1–25), max size per file (1–50 MB), max total size per turn (1–100 MB), processing timeout (10–480 s), and max attempts (1–5)
    * Limits cover documents and audio combined, and an attachment over a limit is still captured and visible in the run — it just isn't sent for processing
    * **Reset to Defaults** restores all five. Defaults are the platform maximums for files and sizes, so existing agents behave exactly as before until you change them

    **Who can use this:**\
    Every text agent channel that accepts attachments. See [Media processing](../../01-Developer-Guide/06-Text-Agents/01-Text-Agents-Overview.md#media-processing) and [Advanced limits](../../01-Developer-Guide/06-Text-Agents/01-Text-Agents-Overview.md#advanced-limits).

    ### Preserve rich formatting in included email history

    Gmail and Outlook mailboxes can keep the original formatting of prior messages when a text agent includes conversation history in a reply.

    **What's new:**

    * **Preserve rich formatting in conversation history**, a beta toggle in the subscription's **Advanced** section
    * Earlier emails keep their paragraphs, tables, links, and spacing where that formatting is available; plain-text turns keep their text and line spacing
    * The setting is per **mailbox** — saving it applies to every active subscription on that mailbox, so a thread renders consistently. Existing subscriptions stay opted out until you turn it on
    * It changes only how history is rendered; it does not add history to replies

    **Who can use this:**\
    Gmail and Outlook email agents. See [Gmail](../../01-Developer-Guide/15-Integrations/04-Communication/01-Gmail.md#advanced-subscription-settings) and [Outlook](../../01-Developer-Guide/15-Integrations/04-Communication/02-Outlook.md#advanced-subscription-settings).

    ### LLM token usage by model in the credits API

    `GET /billing/usage/credits` now reports token counts on the LLM subcomponent that spent them.

    **What's new:**

    * Any subcomponent named `LLM` carries a `usage` array with `model`, `input_tokens`, `cache_input_tokens`, `cache_write_tokens`, and `output_tokens`
    * Because usage hangs off the subcomponent, you can tell which part of the workflow consumed the tokens rather than reading one per-workflow total
    * Bring-your-own-key calls are included even when they consume zero HappyRobot credits, so an LLM subcomponent can report usage with `credits` of `0`

    **Who can use this:**\
    Anyone calling the billing API. See [LLM token usage by model](../../01-Developer-Guide/16-Account-and-Settings/09-Usage-and-Billing.md#llm-token-usage-by-model).

    ### Japanese and Chinese v3 voices

    Three HappyRobot **v3** voices join the library: Yukie and Yutaro (Japanese, `ja-JP`) and Haibo (Chinese Mandarin, `zh-CN`).

    **Who can use this:**\
    Any voice agent. See [Voices](../../01-Developer-Guide/14-Assets/04-Voices.md).

    ### Warm handoffs warn on SIP URIs

    The Transfer node's **To number** field now tells you up front that a warm handoff needs a phone number.

    **What's new:**

    * Entering something that looks like a SIP URI on a warm handoff raises a warning, because it would fail at transfer time
    * The field's placeholder and tooltip follow the transfer type, so the SIP URL guidance for User-to-User Information no longer appears on warm handoffs
    * To reach an extension on a warm handoff, use **To extension** under **Advanced Telephony**

    **Who can use this:**\
    Any workflow with a Transfer node. See [Transfer configuration](../../01-Developer-Guide/05-Voice-Agents/06-Prompts-and-Tools.md#transfer-configuration).

    ### Named failure reason when a prompt is too large

    A voice session that fails because its assembled prompt exceeds what the model provider accepts now says so in the run timeline, instead of showing a raw slug.

    **What's new:**

    * `prompt_too_large` is described in plain language, with a pointer to the usual cause — an unfiltered API response or knowledge base result interpolated into the prompt
    * Four startup failure reasons the voice handler already emitted are described too: `agent_config_failed`, `voice_bootstrap_failed`, `room_join_failed`, and `outbound_sip_create_failed`

    **Who can use this:**\
    Any failed voice run. See [Voice session failure reasons](../../01-Developer-Guide/09-Runs-and-Monitoring/02-Run-Statuses.md#voice-session-failure-reasons).
  </Update>

  <Update label="August 26, 2026">
    ### One Genesys Connector ID per environment

    The Genesys Audio Connector trigger now shows a separate **Connector ID** for production, staging, and development, so a staging Architect flow and a production one can both be live against the same workflow.

    **What's new:**

    * **Connector IDs** replaces the single **Node ID** field — copy the ID for the environment that Architect flow should reach and add it as the `node_id` input variable, or as the action's Connector ID
    * Each ID pins the connector's lookup to one environment, the way an Inbound to Number trigger already can with a different phone number per environment
    * Flows configured with the older plain node ID keep working, but they always answer from production whenever production is live

    **Who can use this:**\
    Any workflow with a Genesys Audio Connector trigger. See [One flow per environment](../../01-Developer-Guide/15-Integrations/04-Communication/05-Genesys-Audio-Connector.md#one-flow-per-environment).

    ### European ring tone for hold music

    Tools can now play the European ringback cadence while their child nodes run.

    **What's new:**

    * **Ring tones (EU)** joins the hold-music selector — the ETSI ringback tone, 1 second on and 4 seconds off, which is what callers in Europe expect to hear
    * The existing **Ring tones** option is unchanged and keeps the North American cadence

    **Who can use this:**\
    Any tool attached to a voice agent. See [Hold music](../../01-Developer-Guide/04-Tools/02-Creating-Tools.md#hold-music).

    ### Whisper messages warn at the 1,024-character limit

    The whisper message rides in a SIP header and is truncated at 1,024 characters at transfer time. The editor now tells you before that happens.

    **What's new:**

    * A warning appears on the Direct Transfer node as soon as the typed whisper message passes 1,024 characters, showing the current count
    * Variables count toward the limit once they expand at runtime, so a message that looks short in the editor can still be cut

    **Who can use this:**\
    Whisper transfers on any voice agent. See [Whisper message length limit](../../01-Developer-Guide/05-Voice-Agents/06-Prompts-and-Tools.md#whisper-message-length-limit).

    ### Europe/Madrid time variable

    `time.now_europe_madrid` is now available alongside the other timezone variables, resolving to the current time in Madrid when the workflow runs.

    **Who can use this:**\
    Any workflow. See [Time variables](../../01-Developer-Guide/02-Workflows/07-Variables.md#time-variables).

    ### End conversation toggle on the Reasoning Agent

    The Reasoning Agent node's **Behavior** settings now include the same **End conversation** control text agents have, so an orchestrating reasoning agent can be told not to end on its own and to wait for a [signal](../../01-Developer-Guide/02-Workflows/06-Signals.md) instead.

    **Who can use this:**\
    Any workflow with a Reasoning Agent node. See [End conversation](../../01-Developer-Guide/06-Text-Agents/01-Text-Agents-Overview.md#end-conversation).
  </Update>

  <Update label="August 25, 2026">
    ### Outbound retry attempts grouped in the run timeline

    Every dial attempt of a retried outbound call now lives under one call section in the run's **Details** tab, instead of appearing as separate calls.

    **What's new:**

    * An **Attempt *n*/*total*** pager in the section header steps through attempts, showing each one's transcript, events, and recording in place — it opens on the final attempt
    * Hovering the counter shows that attempt's number, status, and timestamp; on the final attempt it shows the retry outcome (**Completed**, **Max attempts reached**, or **Callback received**)
    * Between attempts the timeline shows *Attempt n failed. Waiting to retry*, with the approximate time of the next dial when one is scheduled

    **Who can use this:**\
    Any outbound call with retries configured. See [Outbound retry attempts](../../01-Developer-Guide/09-Runs-and-Monitoring/03-Transcripts-and-Messages.md#outbound-retry-attempts).

    ### DTMF badge on keypad turns

    Caller turns that arrived from the phone keypad now carry a **DTMF** badge in the transcript, so a pressed `1` reads differently from a spoken "one".

    **What's new:**

    * The badge sits on the caller's message bubble in the run's **Details** tab
    * When consecutive short caller turns are merged into one bubble, the badge stays if any turn in the group was a keypress

    **Who can use this:**\
    Any voice run. See [Message indicators](../../01-Developer-Guide/09-Runs-and-Monitoring/03-Transcripts-and-Messages.md#message-indicators).

    ### Telnyx numbers hidden while a port is in flight

    Telnyx numbers with a **port-pending** status no longer appear in the phone number inventory. Until the port completes the number still belongs to the losing carrier, so listing it showed the same number twice — once under each carrier.

    **Who can use this:**\
    Organizations with a Telnyx integration. See [Telnyx numbers being ported](../../01-Developer-Guide/14-Assets/03-Telephony.md#telnyx-numbers-being-ported).
  </Update>

  <Update label="August 24, 2026">
    ### See and control what a tool returns to the agent

    Every tool now has a **Tool Call Result** panel that shows the exact payload the agent receives and lets you choose, field by field, what it is allowed to see.

    **What's new:**

    * **View Tool Call Result** at the bottom of a tool's configure panel opens a preview built from every output-producing node in the tool's branch, in execution order — one step per node, loops shown once, all paths shown even though only the executed one appears at runtime
    * Fields start **hidden**: the first time a tool-branch node generates a schema, every field is unexposed, and you switch on the ones the agent needs. Regenerating keeps your choices, hides newly discovered fields, and drops fields that no longer exist
    * **Sync Tool Call Result** generates only untested or out-of-date nodes; **Generate Tool Call Result** regenerates the whole branch. Both execute nodes for real, so webhooks fire and integration writes can happen. Incomplete nodes are reported instead of run, and per-node failures are listed
    * Each node shows its state — incomplete (with the reason), untested, or valid — plus a list badge, and a search box filters fields across the whole result
    * A new tool — including one you copy, duplicate, or import — blocks publishing until its result has been opened once; opening the panel itself executes nothing, and tools that predate the feature never block. The tool node shows a red glyph for *not opened yet* and a separate, non-blocking glyph when the branch has drifted since the last generation
    * The same four operations are available on the public API under `/versions/{version_id}/tools/{tool_id}/tool-call-result/` (`inspect`, `sync`, `generate`, and `visibility`), and to Frontal

    **Who can use this:**\
    Any workflow with tools. See [Tool Call Result](../../01-Developer-Guide/04-Tools/03-Tool-Call-Result.md).

    ### App URLs no longer reveal your app's name

    New app slugs are opaque codenames — `slate-harbor-k29xd` rather than `carrier-portal-x8f2q` — because every certificate issued for an app hostname is published permanently to public certificate transparency logs.

    **What's new:**

    * The create and import sheets show the generated **URL slug**, under **Advanced settings**, with a refresh button to draw a different one
    * Typing your own slug is still allowed, and now shows a warning that the name will appear in the app URL and in public certificate transparency records
    * Custom slugs are capped at 30 characters (the exact cap follows your apps domain) so the hostname fits the SSL certificate's 64-character Common Name limit, and slugs already in use are rejected up front
    * The same cap and warning apply in an app's **Custom URL** panel

    **Who can use this:**\
    All new apps. Existing app slugs are unchanged. See [Naming and slugs](../../01-Developer-Guide/07-Apps/02-Creating-an-App.md#naming-and-slugs) and [Custom URLs](../../01-Developer-Guide/07-Apps/05-Deploying.md#custom-urls).

    ### Inbound Text trigger flags a channel change

    The **Inbound Text** trigger's output schema depends on the channel — and, for email, the provider — of the agent connected to it. The editor now says so instead of leaving you with stale variables.

    **What's new:**

    * A warning glyph reading *Connected agent changed to …* appears on the trigger when the connected Inbound Text Agent's channel, or its email provider, no longer matches the schema you generated. Regenerate the schema to refresh the `@` variable picker
    * Before a channel is resolved, the trigger's testing panel notes that it shows common fields only, and that channel-specific fields such as `to_email` and thread data appear once a channel is selected

    **Who can use this:**\
    Any workflow starting from an Inbound Text trigger. See [Inbound trigger output schema](../../01-Developer-Guide/06-Text-Agents/01-Text-Agents-Overview.md#inbound-trigger-output-schema).

    ### Drag knowledge bases into folders

    The knowledge base list is now a tree you can rearrange directly.

    **What's new:**

    * Drag a knowledge base onto a folder to file it, or onto the list root to take it out. Select several rows to move them together
    * Fixed the file-count and storage totals, which could come back wrong on the list and in the organization's storage usage
    * Folder rows total the file count and storage size of everything inside them, and those totals are now correct
    * Searching keeps a folder visible when its name matches or when it holds a matching knowledge base

    **Who can use this:**\
    Everyone with access to **Assets > Knowledge Bases**. See [Organizing the knowledge base list](../../01-Developer-Guide/14-Assets/01-Knowledge-Bases.md#organizing-the-knowledge-base-list).

    ### Run environment in the workflow runs API

    `GET /workflows/{workflow_id}/runs` now returns `execution_environment` on each run, so you can tell development, staging, and production runs apart without fetching each run individually.

    **Who can use this:**\
    Any API or SDK caller listing a workflow's runs. See the [API reference](https://docs.happyrobot.ai/api-reference/overview).
  </Update>

  <Update label="August 22, 2026">
    ### Voice notes pick languages before voices

    WhatsApp voice notes now start from the languages they're spoken in. A new required **Languages** field sits above the voice picker and drives it.

    **What's new:**

    * Pick one or more languages with regional accents — **Spanish (Mexico)**, **Portuguese (Brazil)**, and so on — from the same catalog the voice library uses, each row showing its flag and copyable accent code
    * Selecting a second accent for a language you already picked replaces the first, so a language never appears twice; **All Languages** covers everything the library supports
    * The **Voice** picker reorders itself around your selection: native accents for a selected language first, then cloned accents, then the rest
    * Voice notes can't be published without at least one language and a voice

    **Who can use this:**\
    WhatsApp text agents with voice notes enabled. See [Reply with voice notes](../../01-Developer-Guide/06-Text-Agents/03-WhatsApp.md#reply-with-voice-notes).

    ### Loop Break can be built before a loop goes sequential

    A **Loop Break** node can now be added inside a loop that's still set to run in parallel, so you can build the branch first and switch the loop afterwards.

    **What's new:**

    * Adding a Loop Break to a parallel loop is allowed while editing instead of being blocked outright
    * The loop's configure panel flags the conflict — *"Parallel loops cannot contain Loop Break. Switch this loop to sequential execution to publish."* — and publishing stays blocked until you switch the loop to sequential or remove the break
    * Frontal and the MCP server give the same guidance, so an agent building the workflow doesn't refuse the break outright either

    **Who can use this:**\
    Any workflow with a Loop node. See [Loop Break and parallel loops](../../01-Developer-Guide/03-Core-Nodes/10-Loops.md#loop-break-and-parallel-loops).
  </Update>

  <Update label="August 21, 2026">
    ### Choose the number a transfer or forward dials from

    Transfers and forwards can now pick which of your numbers the outbound leg originates on, with a new **From number** field. This is what makes transfers work on web calls.

    **What's new:**

    * **From number** appears on the **Forward call** node under **Advanced configuration**, and on the **Transfer** node under **Advanced Telephony** for warm handoffs and whisper transfers
    * It selects the SIP trunk, not just the caller ID, so pointing it at an internal trunk keeps the outbound leg off your carrier even when the call arrived on a carrier number
    * The picker only offers numbers your organization owns, including SIP numbers; **Clear** returns to the default of dialing from the number the call arrived on
    * On a [web call](../../01-Developer-Guide/02-Workflows/05-Triggers.md#web-call) workflow — which arrives on no number of its own — the field is required, and the node warns until you set one
    * Web calls also hide the caller-ID pass-through options and rule out a **direct transfer**, which hands over the caller's own phone leg; use a warm handoff or whisper transfer instead

    **Who can use this:**\
    Any workflow with a Transfer or Forward call node. See [Choosing the number to dial out from](../../01-Developer-Guide/05-Voice-Agents/07-Forward-call.md#choosing-the-number-to-dial-out-from).

    ### Limits on transcription context and key terms

    Voice agent transcription inputs now have explicit caps, replacing the old token-based key term limit.

    **What's new:**

    * **Transcription context** holds up to 5,000 characters
    * **Key terms** hold up to 100 entries of 50 characters each
    * Variable references don't count toward either limit — only the literal text does
    * Over-limit fields show how far over they are and mark the node incomplete, which blocks publishing
    * Agents saved before the limits existed keep working and keep loading as-is

    **Who can use this:**\
    All voice agent node types. See [Transcription context](../../01-Developer-Guide/05-Voice-Agents/05-STT-TTS-and-LLM-Configuration.md#transcription-context).

    ### The transcript follows the recording as it plays

    Playing a call recording now moves the transcript with it, instead of leaving you to find your place by hand.

    **What's new:**

    * Messages ahead of the playhead are dimmed, so the line being spoken is the last one at full opacity

    * The transcript auto-scrolls to keep the current line in view

    * Scrolling, swiping, or arrow keys pause the following so you can read ahead; returning to the bottom resumes it

    * Dimming applies only to the session the recording belongs to, so multi-session runs stay readable

    * Dimming clears when you take over the scroll, so the conversation stops reading as a finished wall of text only while you're following along

    **Who can use this:**\
    Any voice run with a recording. See [Following the transcript while it plays](../../01-Developer-Guide/09-Runs-and-Monitoring/04-Recordings.md#following-the-transcript-while-it-plays).

    ### Jump straight to a loop iteration

    Loops in a run's **Details** tab now have a direct jump alongside the existing pager, and the selected iteration lives in the URL.

    **What's new:**

    * Open the **⌄** menu next to the loop's pager and type an iteration number to go straight to it, instead of clicking through hundreds of iterations
    * The selected iteration is stored in the URL as `loop_iteration`, so a shared link opens on the same iteration — nested loops included
    * Selecting a different run clears the iteration

    **Who can use this:**\
    Any run containing a Loop node. See [Navigating loop iterations](../../01-Developer-Guide/09-Runs-and-Monitoring/01-Runs-Overview.md#navigating-loop-iterations).

    ### Custom URLs for apps

    An app can now be given one friendly subdomain instead of living at its generated slug.

    **What's new:**

    * **Custom URL** in the app header's **⋯** menu takes a slug — up to 30 lowercase letters, numbers, and hyphens — and shows the resulting hostname as you type
    * The generated URL keeps working; both resolve to the same deployment, and the app's **Public URL** switches to the custom one
    * One custom slug per app: saving a new one replaces the previous, which stops resolving. Slugs are unique across the platform and can't match the app's own generated slug
    * The app slug, preview URL, repository, environment variables, and access controls are untouched
    * **Remove custom URL** takes it back off after a confirmation

    **Who can use this:**\
    Deployed managed Next.js apps, for members with deploy access. See [Custom URLs](../../01-Developer-Guide/07-Apps/05-Deploying.md#custom-urls).

    ### Audit remark feedback accepts org-level API keys

    The audit remark feedback endpoints no longer require a key tied to a person.

    **What's new:**

    * `GET`, `POST`, and `DELETE /audit-remarks/:id/feedback` accept both user-level and org-level API keys
    * Feedback is scoped to whichever identity created it — a user key acts on that user's feedback, an org key on that key's
    * The feedback object now reports its author as either `created_by` (user key or platform UI) or `created_by_api_key` (org key), with exactly one of the two set. `created_by` is nullable as a result

    **Who can use this:**\
    Anyone submitting audit feedback from the API or SDK. See [Audit remarks](../../02-Developer-Tools/02-TypeScript-SDK/11-Quality-and-testing.md#audit-remarks).
  </Update>

  <Update label="August 20, 2026">
    ### Copy an agent's transcript from the run timeline

    Every agent block in a run's **Details** tab now has an actions menu, and the first thing in it is **Copy transcript**.

    **What's new:**

    * **Copy transcript** puts that session's full transcript on the clipboard as plain text — no selecting and scrolling, and ready to paste into a ticket or a model playground
    * The menu is disabled with a *No transcript available* tooltip when the agent produced none
    * **Open in Chat Playground** moved into the same menu, so both agent actions live in one place instead of as separate buttons

    **Who can use this:**\
    Any run with an agent. See [Agent actions](../../01-Developer-Guide/09-Runs-and-Monitoring/03-Transcripts-and-Messages.md#agent-actions).

    ### Send feedback without leaving the platform

    The workspace menu has a new **Feedback** item for telling the HappyRobot team what's working and what isn't.

    **What's new:**

    * Pick a category — **Feature request**, **Bug report**, **Billing issue**, or **Other** — write what happened, and submit
    * <kbd>Cmd</kbd>/<kbd>Ctrl</kbd> + <kbd>Enter</kbd> submits from the text box

    **Who can use this:**\
    Everyone. See [Sending feedback](../../01-Developer-Guide/01-Get-Started/02-Platform-overview.md#sending-feedback).
  </Update>

  <Update label="August 19, 2026">
    ### Pin a tool parameter to a fixed value

    Every tool parameter now has a **Agent decides** / **Fixed value** selector, so you can send a value the agent never sees or chooses.

    **What's new:**

    * **Fixed value** replaces the parameter's example with a templated editor — literal text, [variables](../../01-Developer-Guide/02-Workflows/07-Variables.md), or a mix — and the value is sent on every call
    * A fixed parameter is hidden from the model, so it can't be guessed, changed, or left out
    * Works on custom tools and on [MCP tools](../../01-Developer-Guide/04-Tools/05-MCP-Tools.md#agent-filled-and-fixed-parameters), whose parameter names and types the server still fixes
    * A required parameter pinned with no value blocks publishing with `Fixed value required for: <parameter>` instead of failing at runtime
    * The `binding` field is accepted on tool parameters through the API

    **Who can use this:**\
    Any voice or text agent with tools. See [Fixed parameter values](../../01-Developer-Guide/04-Tools/02-Creating-Tools.md#fixed-parameter-values).

    ### Genesys Audio Connector reads input variables, not customConfig

    The Audio Connector trigger's variables field was labelled for `customConfig`, which the AudioHook spec does not apply to the Audio Connector at all. It reads Genesys **input variables**, and now says so — and the names you declare are usable while you build.

    **What's new:**

    * The trigger's **node\_id** goes into the Genesys action under **Session Variables – Inputs** as an input variable named `node_id`, or as the action's **Connector ID** — not as a `customConfig` key, which never reached HappyRobot
    * **Input variables** on the trigger declares the names Genesys sends on the session; generate the node's output schema to reference them downstream
    * The caller context the connector always sends — caller's number, called number, language, and the Genesys conversation identifiers — comes through on its own and doesn't need declaring

    **Who can use this:**\
    Workflows triggered by a Genesys Audio Connector. See [Genesys Audio Connector](../../01-Developer-Guide/15-Integrations/04-Communication/05-Genesys-Audio-Connector.md).

    ### Phone number renames stick on Telnyx and SIP trunk numbers

    Renaming a number wrote the new name to Twilio only, so renames on Telnyx numbers and custom SIP trunk numbers disappeared on the next page load.

    **What's new:**

    * A rename is now written to whichever provider owns the number: Twilio numbers in Twilio, Telnyx numbers as the customer reference, and a custom SIP trunk's number on the trunk
    * Names are trimmed and capped at 255 characters — a blank or over-long name is rejected instead of failing mid-write
    * Telnyx lookups are scoped to the owning workspace, so a number can only be resolved by the workspace it belongs to

    **Who can use this:**\
    Any workspace managing phone numbers. See [Phone number settings](../../01-Developer-Guide/14-Assets/03-Telephony.md#phone-number-settings).

    ### Reasoning agents get timeout, reminder, and signal settings

    A reasoning agent used to take a name and nothing else. It now has the same Behavior and Intelligence settings as an inbound text agent, minus the parts that need a channel.

    **What's new:**

    * The node's panel splits into **Behavior** and **Intelligence** tabs below the **Agent name** field
    * **Behavior** adds **Idle session timeout** and **Reminders**, with the same uniform/custom intervals and message options as a text agent
    * **Intelligence** adds **Agent signals** — wake the agent on published signals, subscribe to custom topics, and choose whether a signal starts a response
    * The prompt node's **Built-in** tab offers **End conversation**, **Escalate to human**, and **Read media**, all off by default
    * The idle timeout message, delivery-error handling, and contact memory are not offered — a reasoning agent has no channel and no contact to send to

    **Who can use this:**\
    Any workflow with a reasoning agent. See [Reasoning agent settings](../../01-Developer-Guide/02-Workflows/04-Node-Types.md#reasoning-agent-settings).

    ### Format a Twin SQL query

    The **Query Twin with SQL** node's editor now has a **Format** button.

    **What's new:**

    * Lays out selected fields one per line, and `WHERE`, `GROUP BY`, `HAVING`, `ORDER BY`, `LIMIT`, `OFFSET`, and `RETURNING` each on their own line, with `AND` and `OR` indented under their clause
    * Only whitespace moves: variable pills, string literals, dollar-quoted blocks, commas inside function calls, and SQL comments are left exactly as written

    **Who can use this:**\
    Any workflow with a Query Twin with SQL node. See [Formatting the query](../../01-Developer-Guide/15-Integrations/06-Data-and-Storage/07-Twin-database.md#formatting-the-query).
  </Update>

  <Update label="August 18, 2026">
    ### Model selection splits into model, reasoning effort, and speed

    Model pickers no longer list every reasoning variant as its own model. You pick a family, then how hard it should think and how fast it should run.

    **What's new:**

    * **Model** picks the family, grouped by provider, with recommended and new families flagged
    * **Reasoning effort** — no reasoning, minimal, low, medium, high, extra high, or max — appears for families that offer more than one level
    * **Speed** picks **Standard** or **Fast**, where Fast uses the provider's priority tier. It's shown only for organizations with priority capacity, and never on AI nodes, reasoning agents, custom tests, or adversarial suites
    * Recommendations and defaults are now per surface: voice agents and AI nodes default to `gpt-5.6-luna`, text and reasoning agents to `gpt-5.6-luna-max`, [custom-test judges](../../01-Developer-Guide/11-Quality-and-Evaluation/06-Custom-tests.md#judge-model) to `gpt-5.6-luna`, and adversarial suites to `gemini-3.5-flash-minimal`
    * New in the catalog: **Claude Sonnet 5**, **Grok 4.6**, **Grok 4.5**, **Kimi K3**, and full effort coverage on the GPT-5.6 and GPT-5.2 families
    * Deprecated and no longer selectable: GPT-4o, GPT-5 (and Mini/Reasoning), GPT-5.1 Instant, o4-mini, GPT-OSS 120B, Kimi K2, Gemini 2.5 and Gemini 3 families, Gemini 3.1 Flash Live, Grok 4.3, and Grok 4.20
    * Existing model IDs keep working — `turbo-one` resolves to `gpt-4.1`, `gpt-5.2` to `gpt-5.2-medium` — so saved configurations and API calls are unaffected

    **Who can use this:**\
    Everywhere a model is selected. See [How model selection works](../../01-Developer-Guide/14-Assets/05-Models.md#how-model-selection-works).

    ### Hand a Genesys call back to the Architect flow

    A new **Genesys transfer** action ends an [Audio Connector](../../01-Developer-Guide/15-Integrations/04-Communication/05-Genesys-Audio-Connector.md) session and returns output variables so your Architect flow can route the caller.

    **What's new:**

    * Set the **Queue** the flow should route to — templated, so the agent can pick per call — plus an optional **Reason** for the flow to log
    * The node always sends an escalation flag, and **Advanced configuration** lets you rename the three variables or add extra ones
    * Names must match the Architect action's **Session Variables - Outputs** exactly; the node explains this inline because a mismatch is silent on both sides
    * Adding the node under a tool turns on **End call after execution** on that tool, since the variables ride the session disconnect
    * The node warns when the workflow isn't triggered by a Genesys Audio Connector, where it would fail at runtime
    * The trigger's **Input variables** list now works: declared names come from the Genesys `inputVariables` (not `customConfig`) and are available in the `@` picker before the first call has run

    **Who can use this:**\
    Workflows triggered by a Genesys Audio Connector. See [Handing the call back to Architect](../../01-Developer-Guide/15-Integrations/04-Communication/05-Genesys-Audio-Connector.md#handing-the-call-back-to-architect).

    ### Resolve access from SSO group names

    SSO-enabled workspaces can have identity-provider group names become access-scope grants at login.

    **What's new:**

    * **Resolve incoming group names as grants** under **Settings > General > Access Control** turns it on, and asks whether to remove HappyRobot-assigned access immediately or keep it until each member's next login
    * Group names encode a scope, an optional tag scope, and a role — for example `HR:wsp:acme:viewer`
    * Multi-workspace organizations get an **HR SSO Grants** builder that composes the names for you and reflects the resulting grants on the members page
    * While it's on, invitations and role changes are disabled in HappyRobot — access is managed in your identity provider
    * The older `HR_`-prefixed SSO RBAC tree is deprecated in favor of these grants

    **Who can use this:**\
    Workspaces on SSO. See [Resolve group names as grants](../../01-Developer-Guide/16-Account-and-Settings/05-SSO-Access.md#resolve-group-names-as-grants).

    ### Mastery TMS integration

    Seven new action nodes connect workflows to Mastery Logistics Systems.

    **What's new:**

    * **Find load by reference** and **Find carrier** for lookups
    * **Submit offer** and **Get offer status** for a poll-based offer cycle
    * **Book and assign** to book a carrier and record the driver in one call, plus **Driver assignment** to assign or remove a driver on its own
    * **Update from workflow** to post tracking, stop, driver, bounce, and incident updates to a load
    * Credentials take a base URL, token URL, username, and password

    **Who can use this:**\
    Any workspace with the Mastery integration enabled. See [Mastery TMS](../../01-Developer-Guide/15-Integrations/05-Business-Systems/03-Mastery-TMS.md).

    ### Delay the agent's initial message

    Voice agents can wait before speaking their opening line, so they don't talk over the other party as the call connects.

    **What's new:**

    * **Delay initial message** sits beside the initial message on the prompt node, in seconds, up to 10 — empty means greet immediately, as before

    * If the other party speaks first the wait ends early, and the initial message becomes the agent's first turn

    * Available through the API as `initial_message_delay_ms` wherever a prompt node can be written, including the voice-agent templates and the SDK helper

    * Also available on the API as `initial_message_delay_ms` on a prompt node, and as `initialMessageDelayMs` on the SDK's `createVoiceAgent` helper

    **Who can use this:**\
    Voice agents. See [Prompt fields](../../01-Developer-Guide/05-Voice-Agents/06-Prompts-and-Tools.md#prompt-fields).

    ### Skip turn for text agents

    Not every event needs an answer. **Skip turn** is a built-in that lets a text agent mark an event as handled and say nothing, instead of inventing a message.

    **What's new:**

    * New **Skip turn** row at the bottom of the prompt node's **Built-in** tab, off by default
    * When the agent calls it, no message is sent, no configured tool or workflow action runs, and the event is marked as handled
    * If the agent also produces a message or another action in the same turn, skip turn is ignored and those outputs continue normally
    * Skipping a turn does not put the agent into a waiting mode — the next message, signal, reminder, or tool result follows the agent's normal response settings
    * Skipped turns are rendered in the run history, so it's clear the agent chose to stay quiet rather than failing to respond
    * Reference it from the prompt with `/` like any other built-in

    **Who can use this:**\
    Channel-backed text agents — SMS, WhatsApp, email, chatbot, Teams, and Slack. See [Skip turn](../../01-Developer-Guide/04-Tools/04-Built-in-Tools.md#text-agent-built-in-tools) and [Skip turn settings](../../01-Developer-Guide/06-Text-Agents/01-Text-Agents-Overview.md#skip-turn).

    ### Call Workflow shows the target's expected request fields

    When a Call Workflow node points at a static target whose trigger declares request parameters, the Payload section now says so.

    **What's new:**

    * Declared parameters you haven't configured are listed as missing, with **Add missing** to append them with empty values

    * Keys you already set — and extra keys the target doesn't declare — are left alone

    * Suggestions come from the latest version of the target, so they follow its contract as it changes

    * The banner names the first three missing fields plus a count of the rest, and its **Add missing fields** button appends them all to the builder at once

    **Who can use this:**\
    Call Workflow nodes with a static target. See [Expected request fields](../../01-Developer-Guide/03-Core-Nodes/12-Call-Workflow.md#expected-request-fields).

    ### Rename audio assets

    Audio library assets can be relabeled without re-uploading.

    **What's new:**

    * **Edit** on an asset updates its **name** and **description**; the audio file is untouched, so existing references keep working
    * Descriptions are optional on every creation path — upload, TTS disclaimer, and warm handoff intro — so the library can hold a short label instead of the full spoken script

    **Who can use this:**\
    Everyone with access to **Assets > Telephony**. See [Managing assets](../../01-Developer-Guide/14-Assets/03-Telephony.md#managing-assets).

    ### Audits appear on the workflow that ran them

    A workflow's **Audits** page now covers every run it executed, including runs it handled as the callee of a [Call Workflow](../../01-Developer-Guide/03-Core-Nodes/12-Call-Workflow.md) node.

    **What's new:**

    * A called workflow's remarks show up on its own Audits page instead of only on its caller's
    * The calling workflow still sees those remarks under the run it started, so the same remark can appear on both pages
    * Organization-level metrics and pass rates continue to count each run once

    **Who can use this:**\
    Workflows invoked by other workflows. See [What the page covers](../../01-Developer-Guide/11-Quality-and-Evaluation/03-Automated-audits.md#what-the-page-covers).

    ### Duplicate numbers are no longer flagged in the telephony table

    The warning triangle next to a phone number that appeared more than once has been removed. It counted display numbers within the workspace rather than detecting a routing conflict, so it flagged expected SIP and Telnyx duplicates as problems.

    **What's new:**

    * No warning icon on duplicated numbers; check the **Type** column to see which provider a row belongs to
    * Rows are still sorted so duplicates land next to each other, and the inbound voice trigger's picker still shows a provider badge per option

    **Who can use this:**\
    Any workspace managing phone numbers. See [Numbers shared across providers](../../01-Developer-Guide/14-Assets/03-Telephony.md#numbers-shared-across-providers).
  </Update>

  <Update label="August 17, 2026">
    ### Custom roles and tag-scoped access

    Roles are no longer limited to Owner, Editor, and Viewer. You can compose your own from individual access actions, and grant a role on tagged resources instead of the whole workspace.

    **What's new:**

    * **Settings > Roles** lists the role catalog and lets you create a custom role from the action catalog, or duplicate a built-in role as a starting point
    * **Tags as access scopes** (beta), under **Settings > General > Access Control**, turns a member's access into a list of grants — each one a role plus a scope
    * A tag scope applies its role only to resources carrying *every* tag in the scope; a member can hold several grants at once
    * Workflows, phone numbers, components, credentials, knowledge bases, apps, and Twin tables participate in tag-scoped access
    * When you pick a role for a tag scope, the editor separates the actions that follow tags from the ones that need workspace-wide access, so a scope that can't do what you expect is visible before you save
    * Multi-workspace organizations can own the role catalog and the tag vocabulary centrally, and enable tag scopes for every child workspace

    **Who can use this:**\
    Everyone. Managing these settings requires the workspace settings permission. See [Custom Roles](../../01-Developer-Guide/16-Account-and-Settings/03-Custom-Roles.md) and [Scope Tags](../../01-Developer-Guide/16-Account-and-Settings/04-Scope-Tags.md).

    ### Warn the agent before a call hits its maximum duration

    Voice agents can now receive scheduled instructions as the call approaches **Max call duration**, instead of being cut off mid-sentence.

    **What's new:**

    * **Max duration notices** takes up to five notices, each with a **seconds before end** offset and an **instruction** that supports [variables](../../01-Developer-Guide/02-Workflows/07-Variables.md)
    * Notices are shown on a timeline in firing order and can be edited or deleted individually
    * Offsets must be unique and shorter than the max call duration; shortening the duration past a scheduled notice flags the conflict rather than silently dropping it
    * Available on inbound, outbound, and outbound-with-callback voice agents

    **Who can use this:**\
    Voice agents. See [Call duration limits](../../01-Developer-Guide/05-Voice-Agents/02-Inbound-Calls.md#call-duration-limits).

    ### Transfer recording defaults to Audio + Transcription

    Warm handoff and whisper transfers now record both audio and transcription by default, so agents can learn from the human part of the call.

    **What's new:**

    * Selecting **Warm handoff** or **Whisper transfer** writes the **Audio + Transcription** recording mode explicitly instead of leaving it implied
    * Nodes that predate the recording options continue to behave as **Audio** until the transfer type is re-selected
    * A new **Preserve UUI parameters** toggle under Advanced Telephony keeps `;encoding=...` and other UUI parameters literal in the Refer-To URI, for receiving systems that don't percent-decode them

    **Who can use this:**\
    Transfer nodes. See [Transfer configuration](../../01-Developer-Guide/05-Voice-Agents/06-Prompts-and-Tools.md#transfer-configuration).
  </Update>

  <Update label="August 16, 2026">
    ### Bring your own LLM keys

    Register your organization's own OpenAI, Anthropic, or Gemini credentials so model usage is billed to your provider account instead of HappyRobot's.

    **What's new:**

    * **Settings → API Keys → ⋮ → Bring your own keys** holds one credential per provider: an API key for OpenAI and Anthropic, a Google Cloud project ID plus service account JSON for Gemini
    * Credentials are validated with the provider before they're stored, and a card shows the status, the last validation time, and the provider's own error when validation fails
    * **Validate**, **Disable**/**Enable**, **Replace**, and **Remove** actions per provider; enabling re-validates first, so a revoked key comes back as failed rather than active
    * Credentials are write-only — the platform never returns them, and the card shows only the last four characters
    * A credential the provider rejects during use is marked failed automatically, so a key revoked upstream stops being retried
    * [Frontal](../../01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md) chats on OpenAI and Anthropic models run on an active credential, and model pickers mark those providers with a **BYOK** badge. Requests fall back to HappyRobot's credentials whenever no active credential is available, so nothing breaks if a key is rotated

    **Who can use this:**\
    Anyone who can manage API keys for the workspace. See [Bring your own keys](../../01-Developer-Guide/16-Account-and-Settings/07-Bring-your-own-keys.md).

    ### MCP authentication works from Cursor

    Connecting the HappyRobot [MCP servers](../../02-Developer-Tools/01-MCP/01-MCP-servers.md) from Cursor now completes the OAuth flow instead of stalling on the callback.

    **What's new:**

    * Cursor's native `cursor://` callback is trusted by default, alongside `localhost` and Claude's hosted callback — no need to allow-list it under **Settings → MCP Clients**
    * Both authorizing and denying hand the callback back to the desktop app, so Cursor picks up the result

    **Who can use this:**\
    Anyone connecting an MCP server from Cursor. See [Installation → Cursor](../../02-Developer-Tools/01-MCP/01-MCP-servers.md#installation).
  </Update>

  <Update label="August 14, 2026">
    ### WhatsApp templates must have every required parameter filled

    A WhatsApp text agent node used to count as complete as soon as a template was selected. It now checks the parameters of that template too — so a template that would have been rejected by Meta at send time is caught in the editor instead.

    **What's new:**

    * Header and body placeholders, media URLs on image/video/document headers, dynamic URL button suffixes, and copy-code values must all have a value before the node is complete
    * [Carousel](../../01-Developer-Guide/06-Text-Agents/03-WhatsApp.md#carousel-templates) parameters are checked card by card, including the inbound **Carousel With First Message** greeting
    * The node error names the template slot that's missing values — initial outbound, timeout, reminder, or first-message carousel — instead of a generic "missing template"
    * Quick-reply payloads stay optional, and templates saved before this change keep working
    * **Dynamic mode** slots are unaffected: the template isn't known until runtime, so only the template-name variable is checked

    **Who can use this:**\
    Any WhatsApp text agent. See [Required parameters](../../01-Developer-Guide/06-Text-Agents/03-WhatsApp.md#required-parameters).
  </Update>

  <Update label="August 13, 2026">
    ### SendGrid as a direct email provider

    SendGrid can now power a full two-way [email text agent](../../01-Developer-Guide/06-Text-Agents/04-Email.md) on your own domain — receiving through Inbound Parse and sending through the same API-key credential.

    **What's new:**

    * **SendGrid** appears in an email agent's provider list; like Postmark it's a direct provider, so there's no mailbox to connect and no separate sending strategy to choose
    * Selecting the credential surfaces a generated **Inbound Webhook URL** to paste into a SendGrid Inbound Parse setting for a subdomain MX'd to `mx.sendgrid.net`
    * **Sender Identity** sets the From address and display name, which can stay a branded apex address as long as the domain is authenticated in SendGrid
    * A **Reply-To** on the parsed subdomain is plus-addressed per conversation, so replies route back to the agent while the visible From stays your apex address

    **Who can use this:**\
    Any email text agent, with a SendGrid credential from the [SendGrid integration](../../01-Developer-Guide/15-Integrations/04-Communication/09-SendGrid.md). See [Direct email providers](../../01-Developer-Guide/06-Text-Agents/04-Email.md#direct-email-providers-sendgrid-postmark).

    ### Test an inbound call with mock SIP headers

    Workflows that branch on carrier SIP headers could not be exercised from the play button — a preview is a web call, which carries no headers. Now they can.

    **What's new:**

    * **Test call with SIP headers** in the chevron menu next to the play button collects header name/value pairs and starts a test call that carries them
    * The run reads them from `raw_headers` exactly as it would on a real INVITE, so header-dependent branches take the same path as in production
    * Names arrive lowercased, the way the SIP stack writes them, and only headers a real call could deliver are accepted — up to 20 per call
    * The last set you used is remembered per workflow, so repeat tests are one click
    * The item is hidden for web-call entrypoints, where a real call has no headers to mock

    **Who can use this:**\
    Any live workflow whose root trigger is **Inbound to Number**. See [Testing with mock SIP headers](../../01-Developer-Guide/05-Voice-Agents/02-Inbound-Calls.md#testing-with-mock-sip-headers).

    ### Business hours setting name accepts a variable

    The **Business hours setting name** field on voice agent nodes takes a [variable](../../01-Developer-Guide/02-Workflows/07-Variables.md) instead of only a fixed selection, so the schedule can be chosen per contact at runtime.

    **What's new:**

    * Available on outbound, outbound-with-callback, and inbound voice agent nodes when **Respect business hours** is on
    * Useful for multi-timezone campaigns, where each row of the trigger payload carries the schedule it should be called under — no more switching the dropdown per campaign
    * A value that matches no schedule name on the workflow falls back to **Default**, and the field says so
    * Nodes saved with a fixed selection keep working

    **Who can use this:**\
    Any voice agent node respecting business hours. See [Business hours](../../01-Developer-Guide/05-Voice-Agents/03-Outbound-Calls.md#business-hours).

    ### Per-environment MCP server headers

    MCP server credentials already had a server URL and auth token per environment. The headers now follow the same model.

    **What's new:**

    * **Header Name** (for API Key auth) and **Custom Headers** can differ on the Production, Staging, and Development tabs
    * Leaving them empty on Staging or Development reuses the Production values, the same fallback the URL and token use
    * The same fields are available on the MCP endpoints of the [Platform API](https://docs.happyrobot.ai/api-reference/overview)

    **Who can use this:**\
    Any MCP server credential. See [Per-environment configuration](../../01-Developer-Guide/04-Tools/06-MCP-Server-Setup.md#per-environment-configuration).

    ### Preview audio options from the picker

    Hold music, background noise, and custom audio assets were pickable by name only, so choosing one meant publishing and calling to hear it.

    **What's new:**

    * Every option row in the background noise, hold music, custom audio asset, and custom recording-disclaimer pickers has a play/pause button
    * Starting one preview pauses whichever was already playing, across rows and across pickers
    * Options that aren't a single clip — **Random** and **No background noise** — have no button

    **Who can use this:**\
    Anyone configuring a voice agent or tool node. See [Audio environment](../../01-Developer-Guide/05-Voice-Agents/02-Inbound-Calls.md#audio-environment) and [Hold music](../../01-Developer-Guide/04-Tools/02-Creating-Tools.md#hold-music).

    ### Clearer tool execution guidance

    The **Execution** setting on a tool node now explains itself in place.

    **What's new:**

    * The info popover next to the selector describes **Blocking**, **Background — silent**, and **Background — announce**, and links to the tool-calling docs
    * On a text agent it adds that a blocking tool can hold the conversation for up to 24 hours — much longer than on a call, where a caller is waiting
    * The warning that transfer, end-session, and hold-music tools must stay blocking is unchanged

    **Who can use this:**\
    Any tool node. See [Execution](../../01-Developer-Guide/04-Tools/02-Creating-Tools.md#execution).

    ### Platform SLA and service status page

    Workspaces with platform availability reporting on their agreement get a new **Settings > Service > SLA** page.

    **What's new:**

    * Measured 30-day availability per component (Voice · Inbound, Voice · Outbound) for the region serving the workspace, from continuous synthetic end-to-end checks
    * Live incidents and maintenance, from the same source as the sidebar status banner, plus a link to the full status page and incident history
    * Coverage below 95% of expected checks publishes no percentage at all — the page reports **Insufficient data** rather than a flattering number computed over a monitoring gap
    * Published maintenance windows leave the measurement period entirely, so they read as neither downtime nor a gap

    **Who can use this:**\
    Workspaces with availability reporting enabled; the page is hidden otherwise. See [SLA and service status](../../01-Developer-Guide/16-Account-and-Settings/11-SLA-and-service-status.md).

    ### Dictate messages to the app coding agent

    The [sandbox editor](../../01-Developer-Guide/07-Apps/03-Sandbox-Editor.md)'s agent sidebar has a microphone button, so you can describe a change instead of typing it.

    **What's new:**

    * Recognized speech is appended to whatever is already in the composer, so typing and dictation mix freely
    * Uses your browser's speech recognition; the button is disabled in browsers that don't support it

    **Who can use this:**\
    Anyone editing an app in the sandbox. See [Dictation](../../01-Developer-Guide/07-Apps/03-Sandbox-Editor.md#dictation).

    ### Resolved prompts in run details

    Prompt node rows in a run's **Details** tab now render the exact prompt sent to the model as readable Markdown, with every variable already substituted.

    **What's new:**

    * The resolved prompt is shown inline, with a copy button
    * Expand **Raw output** for the `INPUT`, `PAYLOAD`, and `OUTPUT` JSON that other node types show by default

    **Who can use this:**\
    Every run with a prompt node. See [Prompt node outputs](../../01-Developer-Guide/09-Runs-and-Monitoring/03-Transcripts-and-Messages.md#prompt-node-outputs).
  </Update>

  <Update label="August 12, 2026">
    ### Call Workflow handles child errors gracefully, not just timeouts

    The Call Workflow node's **Gracefully handle timeout** setting is now **Gracefully handle errors** and covers failures in the child workflow as well as timeouts.

    **What's new:**

    * With the toggle on, both timeouts and child-workflow errors are returned as structured node output and the parent workflow continues, so you can branch to a fallback path either way
    * Nodes saved under the old setting keep working
    * The node's response-node picker is now a **Test output** section with a **Sample workflow** and **Sample node**; response nodes always resolve from the latest version of the sample workflow
    * For a static target, the sample workflow follows your target selection automatically

    **Who can use this:**\
    Any workflow with a Call Workflow node. See [Call Workflow](../../01-Developer-Guide/03-Core-Nodes/12-Call-Workflow.md#gracefully-handle-errors).

    ### Twin is discoverable through the integrations API again

    Twin was hidden from the integrations marketplace UI — it's your own database, not a third-party card — and that same hide list was being applied to the [Platform API](https://docs.happyrobot.ai/api-reference/overview). Listing integrations skipped it, so **Read from Twin**, **Write to Twin**, and **SQL** couldn't be discovered programmatically.

    **What's new:**

    * The integrations list endpoint (and the `list_integrations` tool on the [Workflows MCP server](../../02-Developer-Tools/01-MCP/03-Workflows-MCP.md)) now returns Twin and its node events
    * The marketplace UI is unchanged — Twin still isn't listed there

    **Who can use this:**\
    Any workspace with a provisioned [Twin database](../../01-Developer-Guide/08-Twin/01-Twin-Overview.md).
  </Update>

  <Update label="August 11, 2026">
    ### Forward a call without an agent

    A new **Forward call** node connects an incoming caller straight to a phone number with no AI agent on the line.

    **What's new:**

    * The caller hears ringback while the destination rings and is connected as soon as it answers; if nobody answers within the **Ringing timeout** (45 seconds by default), the caller is hung up on
    * Unlike an outside-agent transfer, the call stays on HappyRobot, so the platform plays ringback and knows whether the destination picked up
    * Advanced configuration adds a destination **extension**, custom **SIP headers**, and a toggle to show the destination the original caller's number
    * A failed or unanswered dial is reported in the node's output rather than as a node failure, so you branch on the result
    * The forward's recording appears on the node itself in the run's **Details** tab

    **Who can use this:**\
    Any workflow handling inbound calls. See [Forward call](../../01-Developer-Guide/05-Voice-Agents/07-Forward-call.md).

    ### Show the original caller's number on warm handoffs

    The **Transfer** node can now present the inbound caller's number to the representative on a **warm handoff**, so they see who is actually calling.

    **What's new:**

    * **Show the original caller's number** lives under **Advanced Telephony** on the Transfer node, and appears for warm handoffs
    * Requires carrier support. On a bring-your-own Twilio account it has no effect until Immutable Call Forwarding is enabled on the account; when the carrier can't authorize the number, the call still connects and shows your number
    * With the toggle on, callbacks from the destination reach the caller rather than your business

    **Who can use this:**\
    Warm handoffs and [Forward call](../../01-Developer-Guide/05-Voice-Agents/07-Forward-call.md) nodes. See [Caller ID on warm handoffs and forwards](../../01-Developer-Guide/14-Assets/03-Telephony.md#showing-the-callers-number-on-warm-handoffs-and-forwards).

    ### Frontal chats get tabs, a slash menu, and automatic names

    The Frontal panel now holds several conversations side by side, and everything that used to be scattered across menus is in one place you reach by typing `/`.

    **What's new:**

    * A **tab strip** at the top of the panel — open a new chat with **+**, drag tabs to reorder them, and right-click a tab to rename it, mark it read or unread, close it, or delete it
    * Tabs stay live when they're not in focus: a **spinner** shows while a chat is still streaming, and a **blue dot** marks a chat with a new assistant message you haven't read
    * The **Chats** button opens your full chat history grouped by date, so closing a tab tidies the strip without losing the conversation
    * New chats **name themselves** from your first message — the title streams in next to Frontal's reply instead of sitting as *Untitled chat*
    * Type `/` in an empty input for a searchable menu covering **Lookback Turns**, **Enable subagents**, **Subagent Model**, **Chat Model**, **Popout to Composer View**, **Download chat as JSON**, **Clear chat**, and your skills
    * Settings picked in the slash menu apply to the chat you're in, so different tabs can run on different models with different skills attached
    * The **Chat Model** picker is now available to everyone, not just HappyRobot staff
    * Skills moved out of the **+** menu and into the slash menu

    **Who can use this:**\
    Everyone with access to Frontal. See [Chats](../../01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md#chats) and [The slash menu](../../01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md#the-slash-menu).

    ### Frontal can manage response nodes

    Frontal can now turn a workflow's response nodes on and off, so you can wire up a callable workflow by asking for it.

    **What's new:**

    * Ask Frontal to mark or unmark an action node as a response node and it applies the change as a reviewable operation
    * The **Response node** switch in the editor now explains what it does and notes that when several are enabled, the first to complete wins
    * The switch appears only on action nodes, where it has an effect

    **Who can use this:**\
    Any workflow that's called by another workflow. See [Test output](../../01-Developer-Guide/03-Core-Nodes/12-Call-Workflow.md#test-output).

    ### Get the credits a single run consumed

    A new Billing endpoint returns what one [run](../../01-Developer-Guide/09-Runs-and-Monitoring/01-Runs-Overview.md) cost, so you can attribute spend per conversation instead of per day or per workflow.

    **What's new:**

    * `GET /billing/usage/runs/{run_id}` returns `total_credits` plus a nested category → subcomponent breakdown, using the same taxonomy as `GET /billing/usage/credits`
    * The TypeScript SDK exposes it as `client.billing.getRunCredits(runId)`
    * The Billing endpoints in the API reference have been retitled and rewritten to state exactly what each one returns and which filters it accepts: **Get credits**, **Get usage details**, and **Get usage totals**

    **Who can use this:**\
    Any workspace with an API key. See [Credits for a single run](../../01-Developer-Guide/16-Account-and-Settings/09-Usage-and-Billing.md#credits-for-a-single-run) and [Billing](../../02-Developer-Tools/02-TypeScript-SDK/10-Resources.md#billing).

    ### Legacy Run Python node retired

    The old **Run Python** node can no longer be created, and every existing one has been migrated to the sandboxed Python runtime.

    **What's new:**

    * Run Python is gone from the node picker, the API, and the MCP server
    * Migrated nodes run on the sandbox's **Standard** execution profile; code and inputs carry over unchanged
    * Pick **Standard** or **Advanced** to control which packages are available

    **Who can use this:**\
    Any workflow running Python. See [Custom Code](../../01-Developer-Guide/03-Core-Nodes/05-Custom-Code.md).

    ### Remove a phone number from every version of a workflow

    The phone number usage dialog can now detach a number from all of a workflow's versions in one action instead of one version at a time.

    **What's new:**

    * Hover a workflow's header row in the usage dialog and choose **Remove from all versions**
    * Live versions can't be edited, so they're skipped; the confirmation tells you how many versions will change and how many live ones are left untouched

    **Who can use this:**\
    Any workspace managing phone numbers. See [Where a number is used](../../01-Developer-Guide/14-Assets/03-Telephony.md#where-a-number-is-used).
  </Update>

  <Update label="August 10, 2026">
    ### Copy several workflow nodes at once

    The workflow editor clipboard now handles a whole selection, not just one node and its subtree.

    **What's new:**

    * Turn on **Select nodes on the canvas**, pick the nodes you want, and click **Copy** in the selection toolbar
    * A selection has to form one connected block — the button explains itself when it can't be copied
    * Action nodes gained **Copy Node & Nested**, and agent and loop nodes now offer both a scoped copy (**Copy Agent**, **Copy Loop**) and a **& Nested** variant that takes everything downstream too
    * Copying drops you straight into paste mode, and **Undo** now reverses a paste in one step
    * Pasted nodes keep their branch structure, their node component status, and any date values they carried

    **Who can use this:**\
    Anyone who can edit a workflow. See [Copy and paste nodes](../../01-Developer-Guide/02-Workflows/02-Creating-a-Workflow.md#copy-and-paste-nodes).

    ### Run a Next.js app locally against your workspace

    Apps built from the **Next.js Full-Stack** template have a **Develop locally** panel that sets up a local clone wired to the same workspace as the deployed app.

    **What's new:**

    * **Develop locally** in an app's actions menu hands you the `git clone` command, a **Download .env.local** button, and the Git identity and run commands ready to copy
    * The downloaded `.env.local` carries your custom variables and the platform-managed ones, so the local app sees the same configuration as the deployed one
    * Apps served from `localhost` can sign in through the same HappyRobot flow as the deployed app, with the same workspace and permission checks
    * Pushes from the local clone build and deploy exactly like changes made in the sandbox

    **Who can use this:**\
    Next.js Full-Stack apps with a managed repository, for anyone who can edit the app. See [Local development](../../01-Developer-Guide/07-Apps/04-Local-development.md).

    ### Generate northstars for a whole agent

    [Northstar](../../01-Developer-Guide/11-Quality-and-Evaluation/02-Northstars.md) generation now runs at the agent level instead of one prompt at a time, so an agent and all of its prompts are covered in a single background pass.

    **What's new:**

    * The **⋯** menu on an agent row offers **Force regenerate** (replace the agent's prompt- and agent-level northstars) and **Re-iterate** (re-evaluate the existing ones against the current prompts)
    * Both modes confirm before running, then show a **Generating** badge on the agent row and fill in the results automatically when the run finishes — no reload needed
    * Failed runs surface an **Error** badge on the row so you can retry. Status is tracked server-side, so a run started by a teammate — or before you reloaded the page — still shows as running
    * The empty state's **Auto Generate** button now force-regenerates every agent in the version

    **Who can use this:**\
    Any workflow with northstars. See [Auto-generation and coverage](../../01-Developer-Guide/11-Quality-and-Evaluation/02-Northstars.md#auto-generation-and-coverage).

    ### Clearer northstar grouping and component coverage

    The northstars tree now shows each prompt component once, at the narrowest place it applies, and prompt components carry their own coverage score.

    **What's new:**

    * A component used by one prompt is listed under that prompt; a component shared by several prompts of the same agent is listed once under the agent
    * Called workflows are grouped per workflow rather than once per call site, so a workflow invoked from several places appears a single time
    * Component northstars that no coverage assessment has cited are badged **Unfulfilled**
    * A prompt component's **Northstars** tab shows a coverage percentage badge and an **Assess Coverage** action, matching the workflow table
    * **Generate** creates a component's northstars from its own content; **Regenerate** replaces them, affecting every workflow that uses the component. Both run in the background and the list refreshes as they progress

    **Who can use this:**\
    Any workspace using [components](../../01-Developer-Guide/14-Assets/02-Components.md). See [Northstars on prompt components](../../01-Developer-Guide/11-Quality-and-Evaluation/02-Northstars.md#northstars-on-prompt-components).
  </Update>

  <Update label="August 9, 2026">
    ### Delete a Paths block and keep one branch

    Deleting a [Paths](../../01-Developer-Guide/03-Core-Nodes/09-Conditionals.md#paths) block used to take every branch with it. You can now promote one branch instead of rebuilding it by hand.

    **What's new:**

    * The **Delete paths** dialog has a **Keep a path** dropdown listing every branch, plus **Keep none** for the old behavior
    * The kept branch reconnects to the node above the Paths block; the other branches and all conditions are deleted
    * The canvas previews exactly which nodes go away as you change the selection, and the dialog says whether nodes after a [branch merge](../../01-Developer-Guide/03-Core-Nodes/09-Conditionals.md#branch-merges-v3-only) survive
    * The [Frontal](../../01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md) assistant can do the same — ask it to delete a Paths block and keep a specific path

    **Who can use this:**\
    Any workflow with a Paths block. See [Deleting a Paths block](../../01-Developer-Guide/03-Core-Nodes/09-Conditionals.md#deleting-a-paths-block).
  </Update>

  <Update label="August 8, 2026">
    ### Turn a configured node into a node component

    You can now create a reusable [node component](../../01-Developer-Guide/14-Assets/02-Components.md) straight from a node you've already built, instead of recreating its configuration in the component library.

    **What's new:**

    * **Create Node Component** in the **…** menu of an action node's configuration panel opens the component form prefilled with the node's name, integration event, and configuration
    * Every [variable](../../01-Developer-Guide/02-Workflows/07-Variables.md) the node referenced becomes a component input automatically, so the component is portable across workflows
    * Available on action nodes — not triggers, path roots, or nodes already synced with a component — for anyone who can manage components

    **Who can use this:**\
    Any workspace using the workflow editor. See [Creating a node component from an existing workflow node](../../01-Developer-Guide/14-Assets/02-Components.md#from-an-existing-workflow-node).
  </Update>

  <Update label="August 7, 2026">
    ### Prompt components get drafts and publishing

    Editing a [prompt component](../../01-Developer-Guide/14-Assets/02-Components.md) no longer changes what live workflows run. Saving creates a draft version; workflows keep using the version you published.

    **What's new:**

    * **Save** stores a new draft version, **Save and Publish** stores it and makes it live in one step
    * The components table has a **Live Version** column, and the changelog marks which version is live
    * The changelog diff compares any two versions — pick the earlier side from a selector — and offers **Publish** and **Revert to this Version** on the version you're viewing
    * Reverting copies an old version forward as a new version instead of overwriting history, so you still choose when it goes live
    * Publishing records an entry on every workflow version that depends on the component
    * Creating a component still publishes version 1 immediately

    **Who can use this:**\
    Any workspace using prompt components. See [Versions and publishing](../../01-Developer-Guide/14-Assets/02-Components.md#versions-and-publishing).

    ### Frontal can create and edit prompt components

    [Frontal](../../01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md) can now manage prompt component definitions, not just reference them from prompts.

    **What's new:**

    * Ask Frontal to list components, inspect one component's markdown and inputs, create a new component, or update an existing one
    * Component edits are saved as drafts — Frontal tells you the change isn't live and points you to **Assets > Components** to publish
    * Frontal can't publish or delete components

    **Who can use this:**\
    Frontal in Build mode. See [Manage prompt components](../../01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md#manage-prompt-components).

    ### Register a carrier number on WhatsApp

    A Twilio or Telnyx number you already own in HappyRobot can now be added to your WhatsApp Business Account from the Telephony page — no new number from Meta required.

    **What's new:**

    * **Add New > Register on WhatsApp** in **Assets > Telephony** walks through adding the number to your WABA, Meta's voice verification, and Cloud API registration
    * For the length of the code window, calls to the number are forwarded to a phone you nominate so you can hear the code read aloud; routing is restored afterwards
    * The dialog checks up front whether forwarding is possible and warns you when the code will land on a live workflow's transcript instead — for example, when the number is already answering production traffic
    * WhatsApp Business Calling is enabled automatically once the number registers, if your account is eligible
    * The existing **WhatsApp Number** menu entry is now called **Sync WhatsApp**, for numbers already on a WABA

    **Who can use this:**\
    Any workspace with a WhatsApp credential and a voice-capable carrier number. See [Registering a carrier number on WhatsApp](../../01-Developer-Guide/14-Assets/03-Telephony.md#registering-a-carrier-number-on-whatsapp).

    ### Pick the environment a Gmail or Outlook trigger tests with

    The email trigger's testing environment is now an explicit choice rather than a toggle you could leave unset.

    **What's new:**

    * Each environment tab shows a **Use for testing** button, and the selected one shows a **Selected for testing** badge
    * The trigger reports as incomplete until an environment is selected, so a test run can't fall back to the wrong credentials

    **Who can use this:**\
    Workflows with a Gmail or Outlook [email trigger](../../01-Developer-Guide/02-Workflows/05-Triggers.md#email).
  </Update>

  <Update label="August 6, 2026">
    ### Pre-encoded hex UUI and an optional purpose parameter

    [User-to-User Information](../../01-Developer-Guide/05-Voice-Agents/03-Outbound-Calls.md#user-to-user-information-uui) gained an encoding for values that are already hex, plus a switch for receiving systems that don't want the `;purpose=app` parameter.

    **What's new:**

    * New **Pre-encoded hex** encoding sends your value unchanged as `;encoding=hex` — use it when the value is a UUI header read off an inbound call, which the workflow surfaces as a hex string. Picking plain **Hex** for such a value encodes it twice
    * Each encoding option now spells out whether it encodes the value or passes it through
    * New **Omit purpose parameter** switch sends only `;encoding=` on the header
    * **Pre-encoded hex** is offered only with the **Plain Text** data format, and Genesys compatibility is unavailable with it — the value is sent as-is, so it must already carry the discriminator prefix the far end expects

    **Who can use this:**\
    Outbound voice agent, outbound with callback, and direct transfer nodes. See [Encoding options](../../01-Developer-Guide/05-Voice-Agents/03-Outbound-Calls.md#encoding-options).
  </Update>

  <Update label="August 5, 2026">
    ### AI nodes get the current model lineup

    The model picker on [AI Extract](../../01-Developer-Guide/03-Core-Nodes/02-AI-Extract.md), [AI Classify](../../01-Developer-Guide/03-Core-Nodes/03-AI-Classify.md), and [AI Generate](../../01-Developer-Guide/03-Core-Nodes/04-AI-Generate.md) is back in sync with the models available to voice and text agents.

    **What's new:**

    * The GPT-5.6 family — [Luna](../../01-Developer-Guide/14-Assets/05-Models.md#gpt-5.6-luna), [Luna (High)](../../01-Developer-Guide/14-Assets/05-Models.md#gpt-5.6-luna-high), [Terra](../../01-Developer-Guide/14-Assets/05-Models.md#gpt-5.6-terra), [Sol](../../01-Developer-Guide/14-Assets/05-Models.md#gpt-5.6-sol), and [Sol (Max)](../../01-Developer-Guide/14-Assets/05-Models.md#gpt-5.6-sol-max) — plus [GPT-5.2 (Reasoning)](../../01-Developer-Guide/14-Assets/05-Models.md#gpt-5.2-medium) and [GPT-5.4 Nano (Medium)](../../01-Developer-Guide/14-Assets/05-Models.md#gpt-5.4-nano-medium) are selectable on AI nodes
    * **GPT-5.6 Luna** is the new default for all three nodes and the top **Recommended** entry, followed by **GPT-5.6 Terra**
    * Anthropic Claude models work correctly on AI Generate
    * Legacy ids (`o1`, `o3`, `o3-mini`, `o3-pro`, `gpt-4.1-nano`, `gpt-4o-mini`) are no longer selectable; nodes already saved with them keep running

    **Who can use this:**\
    Every workspace. See [Models](../../01-Developer-Guide/14-Assets/05-Models.md).

    ### Search variables from the inline `@` picker

    The `@` variable picker now filters as you type, using the same inline behavior as the `/` command menu.

    **What's new:**

    * Type after the `@` to filter by variable or group name — the typed text stays inline in the field, so nothing is lost if you don't insert a variable
    * Arrow keys move through the matches; **Enter** or **Tab** inserts the highlighted one
    * The same picker is used everywhere variables are accepted, in prompt editors and templated node fields alike

    **Who can use this:**\
    Every workflow. See [Referencing variables](../../01-Developer-Guide/02-Workflows/07-Variables.md#referencing-variables).
  </Update>

  <Update label="August 4, 2026">
    ### Conditional prompt components

    A prompt can now choose between [prompt components](../../01-Developer-Guide/14-Assets/02-Components.md) at runtime, so one agent can carry different instructions per region, customer tier, or campaign without duplicating the prompt.

    **What's new:**

    * Insert a **Conditional Prompt Component** from the `/` menu or the prompt editor toolbar
    * Each **case** pairs a condition — built with the same AND/OR builder as [conditional nodes](../../01-Developer-Guide/03-Core-Nodes/09-Conditionals.md#condition-builder) — with the prompt component to include, inputs and all
    * Cases are reorderable and evaluated top to bottom; only the first match is included, with an optional **Fallback** component when nothing matches
    * Conditions read the variables available at that prompt node, including trigger data and upstream node outputs
    * Publishing is blocked until every case has both a complete condition and a selected component

    **Who can use this:**\
    Any prompt node. See [Conditional prompt components](../../01-Developer-Guide/14-Assets/02-Components.md#conditional-prompt-components).

    ### Faster access to prompt component usage

    **What's new:**

    * Click a referenced component's name in a prompt to open it directly in the Components editor
    * **View Usages** lists every workflow using a component, grouped by version and marked **Live**, **Locked**, or **Draft**, with a link into each version's editor
    * The components table sorts by name — click the **Name** header to toggle the direction

    **Who can use this:**\
    Every workspace. See [Usage tracking](../../01-Developer-Guide/14-Assets/02-Components.md#usage-tracking).

    ### Reactions and media timeouts in the run timeline

    **What's new:**

    * A WhatsApp contact's emoji reaction is delivered to the agent as a conversation turn, and renders in the timeline as a compact line showing the emoji and the message reacted to
    * Calls that end because audio stopped flowing — a network problem, or a hang-up signal that never arrived — now show an explicit **Media timeout** marker instead of ending without explanation

    **Who can use this:**\
    WhatsApp agents and every voice run. See [Reactions](../../01-Developer-Guide/06-Text-Agents/03-WhatsApp.md#reactions) and [Event markers](../../01-Developer-Guide/09-Runs-and-Monitoring/03-Transcripts-and-Messages.md#event-markers).

    ### Northstars an agent owns

    A [northstar](../../01-Developer-Guide/11-Quality-and-Evaluation/02-Northstars.md) can now belong to an agent instead of a single prompt node, so behavior that must hold everywhere doesn't have to be repeated on every prompt.

    **What's new:**

    * Create an agent-level northstar from the agent's row in the northstars table — it's graded against the agent's whole conversation, across every prompt
    * Agent-owned rows are listed under the agent's header, above its prompt groups
    * Northstars from [called workflows](../../01-Developer-Guide/03-Core-Nodes/12-Call-Workflow.md), including their agent-level ones, are nested under the calling agent, where you can enable or disable them for your call path

    **Who can use this:**\
    Any workflow using behavioral northstars. See [Prompt-level and agent-level northstars](../../01-Developer-Guide/11-Quality-and-Evaluation/02-Northstars.md#prompt-level-and-agent-level-northstars).

    ### Call a workflow on either engine version

    The **Target Workflow** picker on the [Call Workflow](../../01-Developer-Guide/03-Core-Nodes/12-Call-Workflow.md) node no longer hides workflows running on the V2 engine.

    **What's new:**

    * Any workflow with a compatible trigger and calling enabled is selectable, whichever engine version it runs on
    * The calling workflow still has to be on the V3 engine

    **Who can use this:**\
    Any V3 workflow with a Call Workflow node. See [Target workflow](../../01-Developer-Guide/03-Core-Nodes/12-Call-Workflow.md#target-workflow).
  </Update>

  <Update label="August 3, 2026">
    ### AI and recording disclosure for voice agents

    Voice agent nodes have a new **Recording disclaimer** option that plays a single pre-recorded line covering both the AI disclosure and the recording notice — "This is a recorded call with an AI agent."

    **What's new:**

    * **AI and recording disclosure** is available on inbound, outbound, and outbound-with-callback voice agents, and plays before the agent's initial message
    * **Recording language** defaults to **Auto**, which plays the disclosure in the call's conversation language; it can also be pinned to a specific language or templated from a [variable](../../01-Developer-Guide/02-Workflows/07-Variables.md)
    * On EU deployments the option is the default for new voice agent nodes, and selecting anything else raises a warning on the node

    **Who can use this:**\
    Every voice agent. See [EU AI Act and GDPR requirements](../../01-Developer-Guide/17-Compliance/01-EU-AI-Act-and-GDPR-requirements.md#voice-agents) and [Recording and disclaimers](../../01-Developer-Guide/05-Voice-Agents/02-Inbound-Calls.md#recording-and-disclaimers).

    ### Copy node IDs from the run graph

    **What's new:**

    * The node detail panel in a run's **Graph** tab shows the node's execution status as a badge and has **Copy node ID** and **Copy persistent ID** actions, for correlating a run against the API or a support request

    **Who can use this:**\
    Every run. See [Graph tab](../../01-Developer-Guide/09-Runs-and-Monitoring/01-Runs-Overview.md#graph-tab).
  </Update>

  <Update label="July 31, 2026">
    ### Send images and documents from a WhatsApp agent

    A WhatsApp text agent can now share an image or a PDF in the conversation, so a contact can look at a rate confirmation or a BOL without leaving the thread.

    **What's new:**

    * New **Send images and documents** row in the prompt node's **Built-in** tab, off by default and available on the WhatsApp channel only
    * The row's settings describe when the agent should send media and what caption to use — an AI-written caption, a fixed one, or none
    * Enabling it registers the `hr_builtin_tool__send_whatsapp_media` [built-in tool](../../01-Developer-Guide/04-Tools/04-Built-in-Tools.md), which the agent calls when your prompt tells it to
    * Voice notes moved out of the shared **Media** row into their own **Send voice notes** row, and the remaining row is now called **Automatically process media**

    **Who can use this:**\
    WhatsApp text agents. See [Sending images and documents](../../01-Developer-Guide/06-Text-Agents/03-WhatsApp.md#sending-images-and-documents).

    ### Northstars a prompt component owns

    A [northstar](../../01-Developer-Guide/11-Quality-and-Evaluation/02-Northstars.md) can now belong to a [prompt component](../../01-Developer-Guide/14-Assets/02-Components.md), so a rule that travels with reusable prompt content doesn't have to be re-added in every workflow that embeds it.

    **What's new:**

    * Prompt components have a **Northstars** page — open it from the component's row menu with **Manage Northstars** — where you create rules by hand or generate them from the component's own content
    * Northstars defined on a component grade every workflow that embeds it, and appear in each workflow's northstars table under the component's section
    * A workflow can add a northstar to an embedded component or a called workflow's prompt that only that version grades, without changing what the component or the callee owns

    **Who can use this:**\
    Any workspace using prompt components. See [Northstars on prompt components](../../01-Developer-Guide/11-Quality-and-Evaluation/02-Northstars.md#northstars-on-prompt-components).
  </Update>

  <Update label="July 30, 2026">
    ### Send WhatsApp template node

    A new **WhatsApp > Send WhatsApp** action node sends a pre-approved template message from a workflow, without standing up a text agent for it.

    **What's new:**

    * Configure a **To** number, the WhatsApp credential, business account, and sending phone number, then pick an approved template and map its parameters — the same template configurator used by [WhatsApp text agents](../../01-Developer-Guide/06-Text-Agents/03-WhatsApp.md#message-templates)
    * Every field accepts [variables](../../01-Developer-Guide/02-Workflows/07-Variables.md), so the recipient and the parameter values can come from earlier nodes
    * Available under **Communications** in **Settings > Integrations**

    **Who can use this:**\
    Any workspace with a WhatsApp credential. See [Send WhatsApp](../../01-Developer-Guide/15-Integrations/04-Communication/08-WhatsApp.md#send-whatsapp).

    ### Connect a warm transfer without a handoff message

    The [Direct Transfer](../../01-Developer-Guide/05-Voice-Agents/06-Prompts-and-Tools.md#call-transfer) node's warm handoff has a new **Connect immediately (no message)** switch for reps who don't want to be briefed first.

    **What's new:**

    * With the switch on, the caller is connected as soon as the rep answers — no handoff message, no intro audio, and no press-1/press-9 handshake
    * The handoff message, intro audio, voice speed, and spoken-digit fields are hidden while it's on, since none of them apply
    * Use it when you want direct-transfer behavior but still need to dial an extension, which plain direct transfers don't support

    **Who can use this:**\
    Any warm handoff transfer. See [Transfer configuration](../../01-Developer-Guide/05-Voice-Agents/06-Prompts-and-Tools.md#transfer-configuration).
  </Update>

  <Update label="July 29, 2026">
    ### Transcript clicks land on the right audio

    **What's new:**

    * Clicking a line in a [run transcript](../../01-Developer-Guide/09-Runs-and-Monitoring/04-Recordings.md#transcript-linked-playback) now seeks the recording to where that speech actually starts, using the speech offsets the transcription provider reports instead of the timestamp the message was recorded at
    * Previously a click could land past the start of its own line — most often on caller lines, and worst when the caller talked over the agent

    **Who can use this:**\
    Every voice run with a recording.

    ### Imported workflows keep their variable references

    **What's new:**

    * Importing a workflow JSON file now rewrites the node references buried in each node's configuration — variable handles, condition fields, and loop **Iterate over** expressions — to the new node IDs, so an imported copy runs like the original instead of losing every node-to-node reference

    **Who can use this:**\
    Anyone importing a workflow. See [Import a workflow from a file](../../01-Developer-Guide/02-Workflows/02-Creating-a-Workflow.md#import-a-workflow-from-a-file).
  </Update>

  <Update label="July 28, 2026">
    ### Publish Avro to Kafka, and set record headers

    The [Kafka](../../01-Developer-Guide/15-Integrations/06-Data-and-Storage/04-Kafka.md) **Publish** node can now publish in Confluent wire format against a schema registry, and attach record headers to the message.

    **What's new:**

    * New **Value Format** option — **JSON** (the default) sends the payload as-is; **Avro** resolves the subject's registered schema and publishes in Confluent wire format
    * Optional **Schema Subject** overrides the default `<topic>-value` subject
    * New **Headers** list attaches record headers to the message, such as CloudEvents attributes — values accept [variables](../../01-Developer-Guide/02-Workflows/07-Variables.md)
    * Kafka credentials gained **Schema Registry URL**, username, password, and CA certificate fields; the username, password, and certificate default to the broker's

    **Who can use this:**\
    Any workspace with a Kafka credential. See [Value format and Avro](../../01-Developer-Guide/15-Integrations/06-Data-and-Storage/04-Kafka.md#value-format-and-avro).

    ### WhatsApp numbers for voice agents

    WhatsApp Business Calling numbers can now be routed to HappyRobot and used by inbound voice workflows alongside your carrier numbers.

    **What's new:**

    * **Assets > Telephony > Add New > WhatsApp Number** (since renamed **Sync WhatsApp**) opens a dialog listing every number on your WhatsApp credentials with its sync status, and syncs one per row
    * Syncing points Business Calling at HappyRobot; only synced numbers appear in the numbers table and in the inbound voice trigger's number picker
    * When a number fails to sync, the dialog names the checks that are keeping it off the connector path
    * A number that exists as both a carrier number and a WhatsApp number is shown once per provider, with a provider badge in the picker and on the selected number

    **Who can use this:**\
    Workspaces with a WhatsApp credential. See [Syncing a number already on WhatsApp](../../01-Developer-Guide/14-Assets/03-Telephony.md#syncing-a-number-already-on-whatsapp).

    ### Background tool execution for text agents

    The tool **Execution** setting — blocking or background — is no longer voice-only.

    **What's new:**

    * **Execution** is now available on tools attached to text agents and on [MCP tools](../../01-Developer-Guide/04-Tools/05-MCP-Tools.md), where it sits under **Advanced**
    * The info popover next to the setting explains all three modes: **Blocking**, **Background — silent**, and **Background — announce**
    * Tools that transfer, end the session, or play hold music still have to stay blocking, and the warning now says "end the session" rather than naming call-only actions

    **Who can use this:**\
    Every voice and text agent tool. See [Execution](../../01-Developer-Guide/04-Tools/02-Creating-Tools.md#execution).
  </Update>

  <Update label="July 26, 2026">
    ### Compare more than two variants in an experiment

    An [experiment](../../01-Developer-Guide/10-Experiments/01-Experiments.md) is no longer limited to one control and one treatment — you can add several treatments and split traffic across all of them.

    **What's new:**

    * **Add Treatment** adds another variant to a draft; each one carries its own version or config overrides, its own traffic share, and its own name
    * Traffic is entered per variant and has to sum to 100%, with a whole-number minimum of 1% per variant
    * Rename a variant — including **Control** — from its actions menu, and remove a treatment with a dialog that returns its traffic to control
    * Custom metric sources are mapped for every variant, not just two, and the mappings survive adding, removing, or repointing a variant
    * The analysis view reports runs per variant and compares each treatment against control; with more than four variants the header points to the per-variant breakdown

    **Who can use this:**\
    Any workflow on the V3 engine. See [Configure variants](../../01-Developer-Guide/10-Experiments/02-Creating-experiments.md#configure-variants).

    ### Workspace-wide data retention

    Data retention can now be set once for the whole workspace, instead of workflow by workflow.

    **What's new:**

    * **Settings > General > Advanced Settings** has a **Workspace Data Retention** switch and a **Workspace Retention Period** of 7, 14, 30, 60, 90, or 180 days, or 1 year
    * A workflow's own retention can't exceed the workspace policy — longer options are dropped from the workflow picker, and an existing longer value is shown as **exceeds workspace limit**
    * Before saving a shorter workspace period, an **Affected Workflows** dialog lists every workflow whose data would start being deleted sooner, and a confirmation notes that the next cleanup may delete retained data
    * The [API](https://docs.happyrobot.ai/api-reference/overview) rejects a `data_retention_days` on workflow create or update that exceeds the workspace policy

    **Who can use this:**\
    Every workspace. See [Data retention](../../01-Developer-Guide/16-Account-and-Settings/01-Organization.md#data-retention).

    ### Modify email node for Gmail

    **What's new:**

    * New **Gmail > Modify email** action node marks a message as read or unread, or archives it, given a **Message id** — useful for clearing an inbox the **New Email** trigger watches after a workflow has handled a message

    **Who can use this:**\
    Any workspace with a Gmail credential. See [Actions](../../01-Developer-Guide/15-Integrations/04-Communication/01-Gmail.md#actions).

    ### See where an email credential is used

    Gmail and Outlook credentials and subscriptions now show what depends on them, and refuse to be deleted out from under a live agent.

    **What's new:**

    * **View Usage** on a credential's or subscription's row menu lists the workflows and versions using it, grouped by workflow and marked with the environment and whether the agent is inbound or outbound
    * Deleting a credential or subscription that a live email agent uses is blocked, with a message pointing at **View Usage** so you can unpublish the listed versions first

    **Who can use this:**\
    Gmail and Outlook credentials. See [Credential usage](../../01-Developer-Guide/15-Integrations/02-Credentials.md#credential-usage).

    ### Claude Opus 5 in Frontal and Apps

    **What's new:**

    * **Claude Opus 5** is available in the [Frontal](../../01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md) model picker and in Apps, and is Frontal's new default model
    * **Grok 4.5** was added, and the retired Grok 4.1 Fast entries were replaced with **Grok 4.20 (Non-Reasoning)**
    * Grok models are selectable again, but reject PDF attachments — attaching a PDF while a Grok model is selected returns an error

    **Who can use this:**\
    Every workspace. See [Attaching files](../../01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md#attaching-files).
  </Update>

  <Update label="July 24, 2026">
    ### Publish to Kafka from a workflow

    A new **Kafka** integration lets workflows publish messages to topics on your own Apache Kafka broker, so downstream consumers pick up workflow outcomes without polling HappyRobot.

    **What's new:**

    * New **Kafka > Publish** action node with **Topic**, **Payload**, and an optional **Message Key** for partitioning — all of which accept [variables](../../01-Developer-Guide/02-Workflows/07-Variables.md)
    * Credentials take a comma-separated **Bootstrap Servers** list, **SASL/PLAIN** or no authentication, TLS on by default, and an optional PEM **CA Certificate** for private certificate authorities
    * Available under **Data and Storage** in **Settings > Integrations**

    **Who can use this:**\
    Any workspace that can reach its broker from HappyRobot. See [Kafka](../../01-Developer-Guide/15-Integrations/06-Data-and-Storage/04-Kafka.md).

    ### Edit webhook XML bodies as raw text

    Setting a [Webhook](../../01-Developer-Guide/03-Core-Nodes/06-Webhook.md) node's content type to `application/xml` now switches the body editor to raw text with XML syntax highlighting.

    **What's new:**

    * The body is sent exactly as written — no JSON parsing, no JSON validation errors, and no **Format** button
    * Type `@` to insert a variable anywhere in the markup, including inside elements and attribute values

    **Who can use this:**\
    Any workflow with a Webhook node. See [XML bodies](../../01-Developer-Guide/03-Core-Nodes/06-Webhook.md#xml-bodies).
  </Update>

  <Update label="July 23, 2026">
    ### Built-in tools move to the prompt node

    Everything an agent can decide to *call* is now configured next to the prompt that instructs it, in a new **Built-in** tab on the prompt node.

    **What's new:**

    * The prompt node has **Behavior** and **Built-in** tabs — the tab is channel-aware, showing hang up, stay silent, and press digit for voice agents, and the escalation, end conversation, media, interactive-message, and email tools for text agents
    * **Stay silent**, **Press digit**, and the phone-tree instructions field moved off the voice agent node; the text agent's **Advanced** tab is gone and its settings moved too
    * Prompt nodes with active built-ins show a **built-in** badge on the canvas that lists them and links straight into the matching row
    * Type `/` in the prompt editor to reference a **built-in**, **custom**, or **MCP** tool by name — inserted as a chip that follows renames and renders as disabled if the tool is switched off or deleted
    * Email agents can pin **To**, **CC**, **BCC**, **Subject**, **Body**, **Reply to all**, and **Include conversation history** on the send, reply, and forward tools instead of letting the agent choose
    * Generic-webhook escalation is split into **Inbound API** and **Outbound events**, each with a setup status badge, and OCR, transcription, and voice notes are now single **Disabled / Standard / Advanced** dropdowns
    * Switching a voice agent to a custom LLM server is now a command in the **Model** picker rather than a separate segmented control

    **Who can use this:**\
    Every voice and text agent. See [Built-in tools](../../01-Developer-Guide/04-Tools/04-Built-in-Tools.md#the-built-in-tab).

    ### Discussions on the workflow canvas

    You can now leave comment threads on workflow nodes and collaborate with your team without leaving the editor.

    **What's new:**

    * Start a discussion from a single node's menu, or select several nodes and pin one thread across all of them (up to 100 nodes)
    * **@mention** teammates in a comment to pull them into the thread
    * **Resolve** and **reopen** threads to track what's been handled
    * An activity panel lists every open discussion in the current version, flags the ones that mention you, shows an unread count, and has a **Mark all as read** action
    * Discussions are scoped to the workflow version they were written against

    **Who can use this:**\
    Anyone with access to a workflow. See [Discussions](../../01-Developer-Guide/02-Workflows/10-Discussions.md).
  </Update>

  <Update label="July 22, 2026">
    ### New reasoning models and v3 voices

    **What's new:**

    * Three new OpenAI models are selectable anywhere a model is: [GPT-5.6 Sol (Max)](../../01-Developer-Guide/14-Assets/05-Models.md#gpt-5.6-sol-max), [GPT-5.6 Luna (High)](../../01-Developer-Guide/14-Assets/05-Models.md#gpt-5.6-luna-high), and [GPT-5.4 Nano (Medium)](../../01-Developer-Guide/14-Assets/05-Models.md#gpt-5.4-nano-medium)
    * **GPT-5.4 Nano (Medium)** is the new default for high-volume audits and [custom-eval judges](../../01-Developer-Guide/11-Quality-and-Evaluation/06-Custom-tests.md#judge-model) — a reasoning-capable model priced for the volume eval suites generate
    * Ten new HappyRobot **v3** voices, adding Croatian `hr-HR`, Hungarian `hu-HU`, Chinese (Mandarin) `zh-CN`, and Spanish (Argentina) `es-AR` to the v3 language coverage

    **Who can use this:**\
    Every workspace. See [Models](../../01-Developer-Guide/14-Assets/05-Models.md) and [Voices](../../01-Developer-Guide/14-Assets/04-Voices.md).

    ### WhatsApp carousel templates

    WhatsApp text agents can now send approved **carousel** templates — a swipeable row of cards, each with its own media, text, and buttons.

    **What's new:**

    * Use a carousel template as an outbound agent's **initial message**, or as an optional inbound greeting via **Carousel with first message** (sent right after the agent's first reply)
    * The template parameter mapper renders each card separately, so you can map its media URL, body parameters, and an optional quick-reply payload per card
    * Sent carousels are badged in the conversation on the [Runs](../../01-Developer-Guide/09-Runs-and-Monitoring/01-Runs-Overview.md) page
    * Only carousel templates approved by Meta are selectable

    **Who can use this:**\
    WhatsApp text agents. See [Carousel templates](../../01-Developer-Guide/06-Text-Agents/03-WhatsApp.md#carousel-templates).

    ### Inbound voice agents no longer configure a call source

    The **Call** field has been removed from the inbound voice agent node. Agents now automatically use the workflow's root trigger as their call source.

    **What's new:**

    * There's nothing to select — the agent answers the call from the workflow's trigger
    * To publish, the root trigger must be an **Inbound to Number**, **Web Call**, **Workflow Function Request**, or **Genesys Audio Connector** trigger; publishing is blocked otherwise with an explanatory error

    **Who can use this:**\
    Every inbound voice agent. See [Call source](../../01-Developer-Guide/05-Voice-Agents/02-Inbound-Calls.md#call-source).
  </Update>

  <Update label="July 21, 2026">
    ### Insert Paths blocks between existing nodes

    On the V3 workflow engine, you can now add a [Paths](../../01-Developer-Guide/03-Core-Nodes/09-Conditionals.md#paths) branching block in the middle of an existing chain instead of only at the end of a branch.

    **What's new:**

    * When you insert Paths between two connected nodes, the downstream nodes splice into the block's first path so the rest of the workflow keeps running unchanged
    * You can then branch off the block's other paths from that point
    * On V2, Paths can still only be added to leaf nodes with no children

    **Who can use this:**\
    V3 workflows. See [Inserting Paths between existing nodes](../../01-Developer-Guide/03-Core-Nodes/09-Conditionals.md#inserting-paths-between-existing-nodes-v3-only).
  </Update>

  <Update label="July 19, 2026">
    ### Duplicate apps from the API

    You can now duplicate a managed [app](../../01-Developer-Guide/07-Apps/01-Apps-Overview.md) programmatically, not just from the UI. This makes it easy to script staging copies or template new apps from an existing one.

    **What's new:**

    * New `POST /apps/{app_slug}/duplicate` endpoint and a matching `client.apps.duplicate()` method in the [TypeScript SDK](../../02-Developer-Tools/02-TypeScript-SDK/10-Resources.md#apps)
    * Optionally override the copy's **name**, **description**, and **tag\_ids**; omitted fields fall back to the source app's values (name defaults to `"{original name} Copy"`)
    * Source code and custom environment variables are copied; platform-managed values are regenerated and service credentials must be reconfigured
    * Only managed Next.js apps can be duplicated

    **Who can use this:**\
    Any API key with permission to edit the source app and create apps in the organization. See [Apps](../../02-Developer-Tools/02-TypeScript-SDK/10-Resources.md#apps) in the SDK reference.
  </Update>

  <Update label="July 14, 2026">
    ### Call workflows as reusable functions

    Workflow-to-workflow calling is now a first-class product surface. Any workflow can opt in to being called by others, and the [Call Workflow](../../01-Developer-Guide/03-Core-Nodes/12-Call-Workflow.md) node shows the child's execution inline in the parent run.

    **What's new:**

    * Each trigger node has an **Advanced configuration** section with **Allow this workflow to be called by other workflows** (on by default) and **Hide this workflow's execution in parent run views**
    * Workflow Function Request triggers add a **Call compatible** setting, which exposes the call envelope parameters and makes the workflow selectable as an inbound voice agent call source
    * The Call Workflow target picker now lists only eligible workflows — V3 engine, a supported trigger, and calling enabled
    * Parent runs render the called workflow inline with its name, status, and a response-node badge; expand it to inspect the child's execution

    **Who can use this:**\
    Available on V3 workflows that use the Call Workflow node. See [Making a workflow callable](../../01-Developer-Guide/03-Core-Nodes/12-Call-Workflow.md#making-a-workflow-callable).
  </Update>

  <Update label="July 13, 2026">
    ### Capture webhook response headers

    The [Webhook](../../01-Developer-Guide/03-Core-Nodes/06-Webhook.md) node can now expose selected response headers to downstream nodes, not just the response status and body.

    **What's new:**

    * Enable **Response headers to capture** in the node's **Settings** and add the header names you want
    * Capture up to 10 headers per node; captured values are available through the `@` variable picker like any other node output
    * Only the headers you name are captured — a warning reminds you that headers can contain sensitive data and are stored with run output

    **Who can use this:**\
    Available on every Webhook node. See [Capturing response headers](../../01-Developer-Guide/03-Core-Nodes/06-Webhook.md#capturing-response-headers).

    ### Send a body on GET requests

    The [Webhook](../../01-Developer-Guide/03-Core-Nodes/06-Webhook.md) node's GET method now supports an optional request body for APIs that expect one.

    **What's new:**

    * GET requests expose the same **Body** and **Content type** options as POST
    * A compatibility warning notes that gateways, servers, and proxies may drop bodies on GET — prefer POST when a payload is required

    **Who can use this:**\
    Available on Webhook nodes using the GET method. See [GET](../../01-Developer-Guide/03-Core-Nodes/06-Webhook.md#get).

    ### Original GPT-5 models retired

    The original **GPT-5**, **GPT-5 Mini**, and **GPT-5 (Reasoning)** [models](../../01-Developer-Guide/14-Assets/05-Models.md) are deprecated and can no longer be selected for new AI nodes. Workflows that already reference them keep running.

    **What's new:**

    * New AI node selections should use the **GPT-5.6** family — **GPT-5.6 Sol** (frontier), **GPT-5.6 Terra** (balanced), and **GPT-5.6 Luna** (cost-optimized) — or an existing **GPT-5.5**, **GPT-5.4**, or **GPT-5.2** model
    * The **Fast** GPT-5 variants are deprecated too; use `fast-gpt-5.6-sol`, `fast-gpt-5.4`, or `fast-gpt-5.2-instant` instead
    * Existing workflows that reference a retired model continue to run unchanged

    **Who can use this:**\
    The model picker in every AI node. See [Models](../../01-Developer-Guide/14-Assets/05-Models.md#openai).
  </Update>

  <Update label="July 12, 2026">
    ### Escalation milestone in the run timeline

    The run [details timeline](../../01-Developer-Guide/09-Runs-and-Monitoring/03-Transcripts-and-Messages.md) now shows a first-class milestone when an agent hands a conversation to a human.

    **What's new:**

    * When the agent invokes its escalation tool, the timeline shows an **Escalation requested** or **Escalation started** milestone
    * The milestone appears without hiding the underlying tool call, so you can still expand it for the full request and result

    **Who can use this:**\
    Shown automatically on the **Details** tab of any run with an escalation. See [Event markers](../../01-Developer-Guide/09-Runs-and-Monitoring/03-Transcripts-and-Messages.md#event-markers).

    ### Read audit remarks from the API and MCP

    [Automated audit](../../01-Developer-Guide/11-Quality-and-Evaluation/03-Automated-audits.md) remarks — the per-run, per-northstar pass/fail grades with corrections — are now available programmatically.

    **What's new:**

    * New Platform API endpoints fetch a single remark by ID or list a workflow's remarks, filtered by northstar, grade, or status
    * The Workflows MCP server adds a read-only `manage_audits` tool for the same data

    **Who can use this:**\
    Available through the [Platform API](https://docs.happyrobot.ai/api-reference/overview) and the [Workflows MCP server](../../02-Developer-Tools/01-MCP/03-Workflows-MCP.md).
  </Update>

  <Update label="July 11, 2026">
    ### New OpenRouter models

    Five models routed through **OpenRouter** are now available in AI nodes, each with configured provider fallback so requests are retried against a backup provider if the primary one is unavailable.

    **What's new:**

    * **GLM 5.2**, **DeepSeek V4 Flash**, **DeepSeek V4 Pro**, **MiniMax M3**, and **Step 3.7 Flash**
    * Selectable anywhere a model is chosen — AI nodes, voice and text agents, and eval judges

    **Who can use this:**\
    Available on the **US** platform. Not available in the **EU** region, and a workspace can hide them in its settings. See [OpenRouter](../../01-Developer-Guide/14-Assets/05-Models.md#openrouter).

    ### Gracefully handle Teams send errors

    The [Microsoft Teams](../../01-Developer-Guide/15-Integrations/04-Communication/04-Microsoft-Teams.md) **Send Channel Message** and **Send Direct Message** actions can now continue the workflow when a message fails to send.

    **What's new:**

    * Toggle **Gracefully handle send errors** on either send action
    * When enabled, a failed send is returned as structured node output instead of failing the node, and the workflow moves on to the next step
    * Leave it off (the default) to have send failures stop the run so they surface immediately

    **Who can use this:**\
    Available when configuring Teams send actions in the workflow editor. See [Actions](../../01-Developer-Guide/15-Integrations/04-Communication/04-Microsoft-Teams.md#actions).
  </Update>

  <Update label="July 10, 2026">
    ### Workflow engine v2 publishing retired

    Publishing on the legacy **v2** [workflow engine](../../01-Developer-Guide/02-Workflows/08-Versions-and-Publishing.md#workflow-engine-version-v2-and-v3) has been retired across the editor, MCP, SDK, and public API.

    **What's new:**

    * New v2 versions can no longer be published or promoted — upgrade a version to **v3** before publishing it
    * Existing published v2 versions stay live and continue running until you explicitly unpublish them
    * v2 drafts remain editable, and a v3 version can still be downgraded (though it then can't be published until upgraded again)

    **Who can use this:**\
    Applies to every workflow. See [Upgrading a version to v3](../../01-Developer-Guide/02-Workflows/08-Versions-and-Publishing.md#upgrading-a-version-to-v3), or contact HappyRobot if anything blocks the migration.

    ### Duplicate an app

    You can now duplicate a custom [app](../../01-Developer-Guide/07-Apps/01-Apps-Overview.md) into a brand-new copy, code and all.

    **What's new:**

    * Open an app's actions menu (**⋯**) and choose **Duplicate**
    * Give the copy a new name and description; the source app's code and custom environment variables — including secret values — are copied over, while platform-managed values are regenerated for the copy
    * The original app is left untouched

    **Who can use this:**\
    Requires permission to edit the source app and to create apps; available for Next.js apps deployed to Vercel. See [Duplicating an app](../../01-Developer-Guide/07-Apps/02-Creating-an-App.md#duplicating-an-app).

    ### See available libraries in the Advanced Python node

    The **Advanced Python** [custom code](../../01-Developer-Guide/03-Core-Nodes/05-Custom-Code.md) node now lists the exact packages available in each execution profile.

    **What's new:**

    * An **Available Libraries** popover shows every package in the selected profile, grouped by category
    * The **Advanced** profile (Python 3.12) ships curated libraries for documents, spreadsheets, text, images, and geospatial work — well beyond `pandas` and `numpy` — while the **Standard** profile (Python 3.10) covers the standard library plus date/time helpers

    **Who can use this:**\
    Advanced Python nodes in the workflow editor. See [Available libraries](../../01-Developer-Guide/03-Core-Nodes/05-Custom-Code.md#available-libraries).
  </Update>

  <Update label="July 9, 2026">
    ### New GPT-5.6 models

    Three [GPT-5.6 models](../../01-Developer-Guide/14-Assets/05-Models.md#gpt-5.6-luna) from OpenAI are now available across workflows, voice agents, and text agents.

    **What's new:**

    * **GPT-5.6 Luna** (`gpt-5.6-luna`) — optimized for cost-sensitive workloads
    * **GPT-5.6 Terra** (`gpt-5.6-terra`) — balances intelligence and cost
    * **GPT-5.6 Sol** (`gpt-5.6-sol`) — frontier model for complex professional work

    **Who can use this:**\
    Selectable anywhere you choose a model. See [Models](../../01-Developer-Guide/14-Assets/05-Models.md).

    ### Manage organization members via the API

    You can now add and remove [organization members](../../01-Developer-Guide/16-Account-and-Settings/02-Members-and-Access.md#managing-members-via-the-api) programmatically with an organization-scoped [API key](../../01-Developer-Guide/16-Account-and-Settings/06-API-Keys.md).

    **What's new:**

    * `POST /org/members` invites a member by email as an **editor** or **viewer** (defaults to viewer); internal users are added immediately, everyone else receives an email invitation
    * `DELETE /org/members` removes a member by `email` or `user_id`
    * Owners can't be added or removed through the API — owner management stays in the app

    **Who can use this:**\
    Available on the [public API](https://docs.happyrobot.ai/api-reference/overview). See [Managing members via the API](../../01-Developer-Guide/16-Account-and-Settings/02-Members-and-Access.md#managing-members-via-the-api).
  </Update>

  <Update label="July 8, 2026">
    ### Connect an MCP client to multiple workspaces

    The HappyRobot [MCP servers](../../02-Developer-Tools/01-MCP/01-MCP-servers.md) can now authorize a single connection for more than one workspace, so one client can operate across several organizations.

    **What's new:**

    * During the OAuth authorization step, select **one or more workspaces** from a searchable, grouped list — or use **Select all**
    * When a connection is authorized for multiple workspaces, every tool call takes a required **`org`** parameter (the workspace slug) that names which workspace it runs in
    * Call **`get_connection_info`** to list the authorized workspaces and their slugs; single-workspace connections are unchanged

    **Who can use this:**\
    Available in the MCP OAuth flow for coding assistants, Claude Desktop, and external OAuth hosts. See [Authorizing multiple workspaces](../../02-Developer-Tools/01-MCP/01-MCP-servers.md#authorizing-multiple-workspaces).

    ### Per–knowledge base maximum file size

    Each [knowledge base](../../01-Developer-Guide/14-Assets/01-Knowledge-Bases.md) now has a configurable **Maximum file size** so you can control how large the documents added to it can be.

    **What's new:**

    * Set a **Maximum file size** (1–1,024 MB, default 10 MB) from a knowledge base's settings
    * The limit applies to uploaded files, free-text documents, and web-source documents; oversized files are rejected with an error naming which files were too large
    * Enforced on the [public API](https://docs.happyrobot.ai/api-reference) too — set `max_file_size_mb` when creating a knowledge base

    **Who can use this:**\
    Available on every knowledge base under **Assets → Knowledge Bases**. See [Maximum file size](../../01-Developer-Guide/14-Assets/01-Knowledge-Bases.md#maximum-file-size).

    ### Filter runs by run ID

    The [Runs](../../01-Developer-Guide/09-Runs-and-Monitoring/01-Runs-Overview.md) page now includes a **Run ID** filter for jumping straight to specific runs.

    **What's new:**

    * Add a **Run ID** filter and match a single run with **Equals**, or several at once with **In list**
    * Combines with the other filters and persists in the URL, so filtered views stay shareable

    **Who can use this:**\
    Available in the Runs filter bar. See [Filtering](../../01-Developer-Guide/09-Runs-and-Monitoring/01-Runs-Overview.md#filtering).

    ### Capability badges for non-voice Twilio numbers

    The [telephony](../../01-Developer-Guide/14-Assets/03-Telephony.md) inventory now flags Twilio numbers that can't be used for voice, before you try to sync them.

    **What's new:**

    * Numbers that support SMS but not voice show an **SMS Only** badge, and the sync action is hidden
    * Numbers that support neither voice nor SMS show an **Unsupported** badge
    * This prevents failed sync attempts on numbers Twilio rejects as not SIP-trunking capable

    **Who can use this:**\
    Shown automatically in the phone numbers table. See [Twilio number capabilities](../../01-Developer-Guide/14-Assets/03-Telephony.md#twilio-number-capabilities).
  </Update>

  <Update label="July 7, 2026">
    ### Version built-in variables

    Two new [built-in variables](../../01-Developer-Guide/02-Workflows/07-Variables.md#current-variables) expose the workflow version a run is executing on.

    **What's new:**

    * `current.version_id` — the ID of the workflow version the run is executing on
    * `current.version_name` — the name of that version
    * Reference them with the `@` picker in the editor, or with `{{current.version_id}}` in API configurations — useful for tagging outbound notifications, logs, or downstream records with the exact version that produced them

    **Who can use this:**\
    Available in every workflow. See [Current variables](../../01-Developer-Guide/02-Workflows/07-Variables.md#current-variables).

    ### Dynamic saved views on the Runs page

    [Saved views](../../01-Developer-Guide/09-Runs-and-Monitoring/01-Runs-Overview.md#saved-views) can now include filters that prompt you for a value each time you apply them.

    **What's new:**

    * When saving a view, toggle **Ask each time** on any filter pill to turn it into a parameter instead of a fixed value
    * Applying the view prompts you for each parameter's value — handy for reusable views like "Runs for a caller" or "Runs by ID" where the value changes on each use
    * A view can carry multiple parameters

    **Who can use this:**\
    Available when saving views on the Runs page. See [Ask each time (dynamic views)](../../01-Developer-Guide/09-Runs-and-Monitoring/01-Runs-Overview.md#ask-each-time-dynamic-views).
  </Update>

  <Update label="July 6, 2026">
    ### Query Twin with SQL

    Workflows can now run a **read-only SQL query** against your Twin database with the new **Query Twin with SQL** node.

    **What's new:**

    * Write a `SELECT` (or `WITH`) query for cases the Read from Twin node can't express — joins across tables, aggregations, and computed expressions
    * Insert [workflow variables](../../01-Developer-Guide/02-Workflows/07-Variables.md) with the `@` picker; they're passed as parameterized query values, so queries are safe against SQL injection
    * Set a **Max rows** cap (default 100, up to 1000); results report whether they were truncated
    * Only read queries are allowed — writes, multiple statements, and DDL/DML are rejected

    **Who can use this:**\
    Available in the workflow editor once your organization's [Twin database](../../01-Developer-Guide/08-Twin/01-Twin-Overview.md) is provisioned. See [Query Twin with SQL](../../01-Developer-Guide/15-Integrations/06-Data-and-Storage/07-Twin-database.md#query-twin-with-sql).

    ### Interactive messages for WhatsApp agents

    WhatsApp text agents can now send native **interactive messages** — tappable list pickers and quick-reply buttons — when asking a contact to choose from a set of options.

    **What's new:**

    * Toggle **Interactive messages** on an inbound or outbound WhatsApp agent; the agent decides when to send a list or reply buttons instead of plain text
    * Interactive messages are badged on the [Runs](../../01-Developer-Guide/09-Runs-and-Monitoring/01-Runs-Overview.md) page so you can see when the agent used them
    * WhatsApp-only — enabling the setting on any other channel raises a validation error

    **Who can use this:**\
    Available on WhatsApp text agent nodes in the workflow editor. See [Interactive messages](../../01-Developer-Guide/06-Text-Agents/03-WhatsApp.md#interactive-messages).
  </Update>

  <Update label="July 3, 2026">
    ### Require authentication on transfer popups

    The [Transfer Popup](../../01-Developer-Guide/05-Voice-Agents/08-Transfer-popup.md) node can now be protected with a static access key, so the popup URL alone is no longer enough to view call context.

    **What's new:**

    * A **Require authentication** toggle on the Create Popup node generates an **Access key** you can regenerate or copy at any time
    * When enabled, viewers must present the key as an `X-API-Key` header or `Authorization: Bearer` header before any popup data is served
    * Existing popup nodes default to no authentication, so nothing changes until you turn it on

    **Who can use this:**\
    Available on the Transfer Popup node in the workflow editor. See [Require authentication](../../01-Developer-Guide/05-Voice-Agents/08-Transfer-popup.md#require-authentication-optional).
  </Update>

  <Update label="July 2, 2026">
    ### Loop iterations as child runs

    The [Loop](../../01-Developer-Guide/03-Core-Nodes/10-Loops.md) node can now dispatch each iteration as its own run instead of expanding the loop inline in the parent run.

    **What's new:**

    * Turn on **Materialize each item as a child run** in the loop config to give every item its own run, with independent transcript, status, and outputs
    * A new **Parent run** column in the [Runs](../../01-Developer-Guide/09-Runs-and-Monitoring/01-Runs-Overview.md) table links each child run back to the run that created it
    * In this mode the loop is terminal in the parent run — nodes after the Loop End do not run

    **Who can use this:**\
    Available on the Loop node in the workflow editor. See [Child runs](../../01-Developer-Guide/03-Core-Nodes/10-Loops.md#child-runs).

    ### List sessions by caller phone number

    The Public API can now look up sessions by the caller's phone number.

    **What's new:**

    * New `GET /sessions?caller_id=` endpoint returns paginated sessions for a caller (E.164 phone number), with optional `start_date` and `end_date` filters
    * Available in the TypeScript SDK as `client.sessions.list()` — pair it with `getMessages()` to fetch each session's transcript

    **Who can use this:**\
    Available to Public API and SDK consumers. See [List sessions by caller](../../02-Developer-Tools/02-TypeScript-SDK/07-Sessions-and-messages.md#list-sessions-by-caller).
  </Update>

  <Update label="July 1, 2026">
    ### Per-API-key rate limits

    Public API rate limits are now counted **per API key** instead of being shared across an IP address.

    **What's new:**

    * Each bearer token gets its own quota of **300 requests per minute**, so keys no longer compete for a shared limit
    * Unauthenticated requests fall back to per-IP limiting

    **Who can use this:**\
    Applies to all Public API consumers. See [Rate limits](https://docs.happyrobot.ai/api-reference/rate-limits).

    ### Test cron schedules instantly

    Cron-based [schedule triggers](../../01-Developer-Guide/02-Workflows/05-Triggers.md#cron-expression) can now be fired on demand so you don't have to wait for the next scheduled time.

    **What's new:**

    * Open the workflow preview and click **Trigger Now** in the **Manual trigger** dialog to run a cron workflow immediately and verify the schedule and logic
    * The workflow must be live to run a preview execution

    **Who can use this:**\
    Available on cron schedule triggers in the workflow editor. See [Cron expression](../../01-Developer-Guide/02-Workflows/05-Triggers.md#cron-expression).
  </Update>

  <Update label="June 30, 2026">
    ### Genesys Audio Connector

    You can now route calls from **Genesys Cloud** to a HappyRobot voice agent, streamed over a WebSocket — no separate phone number or SIP trunk required.

    **What's new:**

    * New **Genesys** integration with a credential (API key + client secret) used to verify Genesys AudioHook requests
    * New **Genesys Audio Connector** trigger that provides a connection URL and a stable `node_id` to wire into your Genesys Architect flow, plus optional custom variables from the Genesys `customConfig` payload
    * Pairs with an **Inbound Voice Agent** node to handle the conversation

    **Who can use this:**\
    Configure the credential in **Settings > Integrations** and add the trigger in the workflow editor. See [Genesys Audio Connector](../../01-Developer-Guide/15-Integrations/04-Communication/05-Genesys-Audio-Connector.md).

    ### New v3 voices, languages, and accents

    HappyRobot's newest generation of text-to-speech voices — **v3 (preview)** — is now available in the voice library.

    **What's new:**

    * New v3 voices across many languages, labeled **v3 (preview)** in **Assets > Voices** and listed first in the voice selector
    * The model version appears as a badge next to each voice and in the Voice Info tab
    * Additional languages and regional accents, including Spanish (Chile) `es-CL`, Spanish (Puerto Rico) `es-PR`, Modern Standard Arabic `ar-001`, Catalan `ca-ES`, and Galician `gl-ES`
    * Unlike ElevenLabs v3 voices, HappyRobot v3 voices support per-voice **speed** and **gain** adjustment

    **Who can use this:**\
    Browse and select voices in **Assets > Voices** or the voice agent node. See [Voices](../../01-Developer-Guide/14-Assets/04-Voices.md).

    ### Named variables and media in WhatsApp templates

    WhatsApp [message templates](../../01-Developer-Guide/06-Text-Agents/03-WhatsApp.md#message-templates) now support named placeholders and dedicated media and coupon parameters.

    **What's new:**

    * Map template parameters by **named** placeholders (`{{customer_name}}`) in addition to numeric ones (`{{1}}`)
    * Supply image, video, or document header media through a dedicated `{{media_url}}` parameter
    * Set copy-code button values through a `{{coupon_code}}` parameter

    **Who can use this:**\
    Available on WhatsApp text agent nodes in the workflow editor. See [Message templates](../../01-Developer-Guide/06-Text-Agents/03-WhatsApp.md#message-templates).

    ### Attach knowledge bases to Frontal

    The [Frontal AI assistant](../../01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md) can now use more of your workspace as context.

    **What's new:**

    * Attach a **Knowledge Base** from the **Add Artifacts** menu so Frontal can search it when answering questions
    * Attach **Twin** databases/tables and **Editor Nodes** as context, and navigate the menu with the keyboard

    **Who can use this:**\
    Available in the Frontal chat input in the workflow editor. See [Attaching context](../../01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md#attaching-context).
  </Update>

  <Update label="June 29, 2026">
    ### End session on delivery error for all text agents

    The **End session on delivery error** setting is now available across text agent channels, not just WhatsApp.

    **What's new:**

    * Enable **End session on delivery error** on SMS, WhatsApp, chatbot, Microsoft Teams, and Slack agents to end the session and expose error metadata when a message fails to deliver
    * Downstream nodes can inspect the error to log it, notify a human, or retry through a different channel

    **Who can use this:**\
    Available on outbound text agent nodes in the workflow editor. See [Delivery error handling](../../01-Developer-Guide/06-Text-Agents/01-Text-Agents-Overview.md#delivery-error-handling).

    ### More run filter operators

    [Custom column filters](../../01-Developer-Guide/09-Runs-and-Monitoring/01-Runs-Overview.md#filtering) in the Runs tab now support text-pattern and presence operators.

    **What's new:**

    * New **Is empty** and **Is not empty** operators to filter on whether a node output has a value
    * **Like (case-sensitive)** and **iLike (any case)** operators with `%` wildcard matching
    * Clearer operator labels alongside the existing numeric comparisons

    **Who can use this:**\
    Available on the Runs tab for any workflow. See [Filtering](../../01-Developer-Guide/09-Runs-and-Monitoring/01-Runs-Overview.md#filtering).

    ### Sync inbound prompt for outbound callbacks

    Outbound-with-callback voice agents can now keep the callback prompt in sync with the outbound prompt.

    **What's new:**

    * Turn on **Sync inbound** to have the callback prompt mirror the outbound prompt automatically; leave it off to edit the callback prompt separately

    **Who can use this:**\
    Available on the outbound-with-callback voice agent node. See [Sync inbound](../../01-Developer-Guide/05-Voice-Agents/04-Outbound-with-Callback.md#sync-inbound).

    ### Basic auth for MCP client credentials

    The MCP `client_credentials` token endpoint now accepts credentials via HTTP Basic auth.

    **What's new:**

    * Pass your API key using an `Authorization: Basic` header (`client_secret_basic`) in addition to the request body — useful for platforms like Workato that expect it

    **Who can use this:**\
    Developers using the MCP service-to-service flow. See [Service-to-service authentication](../../02-Developer-Tools/01-MCP/01-MCP-servers.md#service-to-service-authentication).
  </Update>

  <Update label="June 28, 2026">
    ### Export Twin SQL console results

    The [Twin SQL console](../../01-Developer-Guide/08-Twin/05-SQL-Console-and-Capacity.md#sql-console) can now get query results out of the browser.

    **What's new:**

    * **Export CSV** — download the rows a query returns as a CSV file, with values escaped per RFC 4180 so commas, quotes, and line breaks stay intact
    * **Copy TSV** — copy results to your clipboard as tab-separated values, ready to paste straight into a spreadsheet

    **Who can use this:**\
    Available in the Twin SQL console result console whenever a query returns rows. See [Exporting results](../../01-Developer-Guide/08-Twin/05-SQL-Console-and-Capacity.md#exporting-results).
  </Update>

  <Update label="June 26, 2026">
    ### List workflow sessions over the API

    A new endpoint returns sessions across **all runs** of a workflow in one paginated call, instead of fetching them run by run.

    **What's new:**

    * `GET /workflows/{workflow_id}/sessions` lists sessions for a workflow, ordered by timestamp, with `page`, `page_size`, and `sort` query parameters
    * Each session includes its `id`, `run_id`, `version_id`, `status`, `type`, `duration`, `timestamp`, and `failure_reason`
    * Available in the TypeScript SDK as `client.workflows.listSessions(workflowId, query?)`

    **Who can use this:**\
    Available to anyone with an API key. See [Workflows SDK](../../02-Developer-Tools/02-TypeScript-SDK/06-Workflows.md#workflows) and the [API reference](https://docs.happyrobot.ai/api-reference).

    ### Create Twin dumps from the API and MCP

    [Workflow run dumps](../../01-Developer-Guide/08-Twin/04-Workflow-Run-Dumps.md) can now be created programmatically, not just from the Twin workspace.

    **What's new:**

    * `POST /twin/dump` creates a dump table and binds its columns to a workflow's variables — pass a `workflowId` and `tableName`, and the server resolves the workflow's variable catalog for you. Use `include` to capture a subset of variables and `pk` to choose the primary key
    * The Twin MCP server exposes the same capability through the new `create_workflow_dump` tool, so an AI assistant can stand up a dump table that completed runs populate automatically

    **Who can use this:**\
    Available to anyone with an API key or the [Twin MCP server](../../02-Developer-Tools/01-MCP/04-Twin-MCP.md). See [Creating a dump programmatically](../../01-Developer-Guide/08-Twin/04-Workflow-Run-Dumps.md#creating-a-dump-programmatically).
  </Update>

  <Update label="June 25, 2026">
    ### Phone tree navigation for inbound voice agents

    Inbound voice agents can now press digits to navigate automated phone menus (IVR).

    **What's new:**

    * Turn on **Enable press digit** in the inbound voice agent settings to give the agent the `press_digit` tool, so it can send DTMF tones (`0`–`9`, `*`, `#`) during the call
    * Add navigation instructions directly to the agent's main prompt — inbound agents don't use a separate phone tree prompt

    **Who can use this:**\
    Available on the inbound voice agent node in the workflow editor. See [Conversation built-ins](../../01-Developer-Guide/05-Voice-Agents/02-Inbound-Calls.md#conversation-built-ins).

    ### Reference whole objects and arrays in the variable picker

    The `@` variable picker now exposes container variables, not just leaf fields.

    **What's new:**

    * When a node output is an object or an array, the picker lists both individual fields (e.g. `extract.address.city`) and their parent container (e.g. `extract.address`), so you can pass an entire structure to a downstream node or API call
    * Each entry shows its type — string, number, boolean, object, or array

    **Who can use this:**\
    Available anywhere the `@` picker appears in the workflow editor. See [Referencing variables](../../01-Developer-Guide/02-Workflows/07-Variables.md#referencing-variables).
  </Update>

  <Update label="June 24, 2026">
    ### Email signatures for text agents

    Email text agents can now append a **signature** to every outbound email.

    **What's new:**

    * Set an **Email signature** on inbound or outbound email agents — HTML content that's added to the end of every email the agent sends, including the initial email and all replies
    * Supports [variables](../../01-Developer-Guide/02-Workflows/07-Variables.md) via the `@` picker, so you can personalize the signature with values like the agent name

    **Who can use this:**\
    Available on email text agent nodes in the workflow editor. See [Email signature](../../01-Developer-Guide/06-Text-Agents/04-Email.md#email-signature).

    ### Gracefully handle timeout on Call Workflow

    The [Call Workflow](../../01-Developer-Guide/03-Core-Nodes/12-Call-Workflow.md) node has a new **Gracefully handle timeout** control.

    **What's new:**

    * When enabled, a timeout is returned as structured node output instead of an empty result, and the parent workflow continues — so you can branch on whether the child workflow responded in time and route to a fallback path
    * The target workflow keeps running independently either way

    **Who can use this:**\
    Available on the Call Workflow node in the workflow editor. See [Timeout](../../01-Developer-Guide/03-Core-Nodes/12-Call-Workflow.md#gracefully-handle-timeout).

    ### Wallets scoped to all environments

    Wallets can now be scoped to **All Environments** instead of a single environment.

    **What's new:**

    * When creating or editing a wallet, choose **All Environments** (the new default) to cover usage across every environment, or pin the wallet to a specific environment

    **Who can use this:**\
    Available to organization owners in **Settings > Billing**. See [Wallet environment scope](../../01-Developer-Guide/16-Account-and-Settings/09-Usage-and-Billing.md#wallet-environment-scope).
  </Update>

  <Update label="June 23, 2026">
    ### Higher organization API key limit

    Organizations can now have up to **10 active API keys** at a time, increased from 5.

    **What's new:**

    * Create and keep up to 10 active organization-level API keys, giving you more room to scope keys per integration or environment
    * The personal API key limit is unchanged at one key per member

    **Who can use this:**\
    Available in **Settings > API Keys**. See [API keys](../../01-Developer-Guide/16-Account-and-Settings/06-API-Keys.md#organization-api-keys).

    ### Static web call URLs per environment

    Web call triggers now have a **static, shareable URL for each environment**, so the link you distribute keeps working as you publish new versions.

    **What's new:**

    * Each web call deployment has a fixed URL per environment — `…/deployments/{workflow_slug}` for production, `…/deployments/staging/{workflow_slug}` for staging, and `…/deployments/development/{workflow_slug}` for development
    * Each URL always resolves to the currently published version in that environment
    * The **Enhanced security** setting (require sign-in to open the link) is now configured independently per environment, so you can protect production while leaving development open for testing

    **Who can use this:**\
    Available on the web call trigger in the workflow editor. See [Web call](../../01-Developer-Guide/02-Workflows/05-Triggers.md#web-call).
  </Update>

  <Update label="June 22, 2026">
    ### ISO 8601 time variable

    A new built-in time variable, `time.now_iso`, resolves to the current UTC time in **ISO 8601** format (e.g. `2026-06-23T14:32:10.000Z`).

    **What's new:**

    * Use `time.now_iso` when passing the current time to an API, webhook, or other system that expects a standard machine-readable timestamp, instead of the human-readable timezone variables

    **Who can use this:**\
    Available in the `@` variable picker in any workflow. See [Time variables](../../01-Developer-Guide/02-Workflows/07-Variables.md#time-variables).

    ### Signals on email text agents

    Email text agents now support [signals](../../01-Developer-Guide/02-Workflows/06-Signals.md), bringing them in line with the other voice and text agent channels.

    **What's new:**

    * The **Agent Signals** section is now available on inbound email text agent nodes, so you can subscribe an email agent to topics and react to real-time events mid-conversation

    **Who can use this:**\
    Available on email text agent nodes in the workflow editor. See [Signals](../../01-Developer-Guide/02-Workflows/06-Signals.md).
  </Update>

  <Update label="June 19, 2026">
    ### "Is not empty" conditional operator

    Condition nodes have a new **Is not empty** operator that matches any field that has a value.

    **What's new:**

    * Select **Is not empty** in the operator dropdown of a [Conditional](../../01-Developer-Guide/03-Core-Nodes/09-Conditionals.md) (Paths or Conditional Output) to branch when a field is present
    * Like **Is empty**, it requires no comparison value — it's the inverse, matching fields that are not empty, null, or undefined

    **Who can use this:**\
    Available in the workflow editor and the MCP/API condition builder. See [Available operators](../../01-Developer-Guide/03-Core-Nodes/09-Conditionals.md#available-operators).
  </Update>

  <Update label="June 18, 2026">
    ### Convert to File node

    A new **Convert to File** node turns content produced earlier in a workflow into an uploaded file.

    **What's new:**

    * Build a **CSV**, **JSON**, or **Plain Text** file from any node output — extracted data, generated text, or a Custom Code block's result
    * Set the **file name** (with extension) and reference variables in both the content and name
    * The node returns the file **URL**, so downstream nodes like Webhook or email actions can attach or link to it

    **Who can use this:**\
    Available as a File Operations node in the workflow editor and the public API. See [Convert to File](../../01-Developer-Guide/03-Core-Nodes/08-File-Operations.md#convert-to-file).
  </Update>

  <Update label="June 17, 2026">
    ### Transfer outcome variables

    A new built-in `transfer` variable group surfaces the outcome of call transfers at the agent level, so you can react to a transfer without knowing which node fired it.

    **What's new:**

    * Reference `transfer.succeeded`, `transfer.completed_at`, and `transfer.error` to check the overall transfer result for a run
    * Inspect warm-handoff details with `transfer.warm_handoff_rep_picked_up`, `transfer.warm_handoff_rep_call_connected`, `transfer.warm_handoff_rep_left_before_transferring`, `transfer.warm_handoff_pressed_one`, and `transfer.warm_handoff_pressed_nine`
    * Values aggregate across every transfer node in the workflow — resolving to the successful transfer if one occurred, otherwise the latest attempt

    **Who can use this:**\
    Available in the workflow editor variable picker. See [Transfer variables](../../01-Developer-Guide/02-Workflows/07-Variables.md#transfer-variables).
  </Update>

  <Update label="June 16, 2026">
    ### DELETE webhook node

    The [Webhook node](../../01-Developer-Guide/03-Core-Nodes/06-Webhook.md) now supports the **DELETE** HTTP method, alongside GET, POST, PUT, and PATCH.

    **What's new:**

    * Add a **DELETE** webhook to remove a resource on an external API
    * Supports a request body, custom headers, query parameters, and all authentication methods — the same configuration as POST

    **Who can use this:**\
    Available on the Webhook node in the workflow editor. See [Webhook — DELETE](../../01-Developer-Guide/03-Core-Nodes/06-Webhook.md#delete).

    ### Custom SIP headers (UUI) on outbound voice agents

    Outbound voice agent nodes can now attach **User-to-User Information (UUI)** to the outbound call as SIP headers, carrying custom context to the receiving system.

    **What's new:**

    * A **User To User Information** block in the **Advanced** settings of the **Outbound Voice Agent** and **Outbound Voice Agent with Callback** nodes
    * Send data as a **JSON Object** (key-value pairs) or **Plain Text**, with variable support on keys and values
    * Choose the **encoding** (**Hex**, **ASCII**, or **Base64**) and enable **Genesys compatibility** when integrating with Genesys contact centers
    * Mirrors the UUI configuration already available on the Direct Transfer action

    **Who can use this:**\
    Available on outbound voice agent nodes in the workflow editor. See [User-to-User Information (UUI)](../../01-Developer-Guide/05-Voice-Agents/03-Outbound-Calls.md#user-to-user-information-uui).

    ### Protect the initial message from interruptions

    Voice agent prompt nodes have a new setting that prevents the caller from interrupting the agent's opening message.

    **What's new:**

    * A **Protect initial message from interruptions** toggle on the prompt node (voice agents only), disabled by default
    * When enabled, the agent finishes its initial message before it begins listening — useful when the greeting contains a disclaimer or required identification

    **Who can use this:**\
    Available on the prompt node of any voice agent. See [Prompt fields](../../01-Developer-Guide/05-Voice-Agents/06-Prompts-and-Tools.md#prompt-node).

    ### Dynamic timeout and reminder values for text agents

    Text agent timeout and reminder settings now accept [variables](../../01-Developer-Guide/02-Workflows/07-Variables.md) in addition to static numbers.

    **What's new:**

    * The **idle timeout**, **reminder count**, and **reminder interval** fields can be set with variables, so they can be driven by trigger data or upstream node output
    * Static values still enforce their limits (idle timeout ≥ 1 minute, reminder count 1–12, intervals ≥ 10 seconds); the previous maximum on reminder intervals has been removed

    **Who can use this:**\
    Available on all text agent channels. See [Timeout behavior](../../01-Developer-Guide/06-Text-Agents/01-Text-Agents-Overview.md#timeout-behavior) and [Reminders](../../01-Developer-Guide/06-Text-Agents/01-Text-Agents-Overview.md#reminders).

    ### Workspace owners can configure audits

    Audit and audio-audit configuration is no longer limited to internal users — **workspace owners** can now enable audits and set sampling for their organization.

    **Who can use this:**\
    Available to workspace owners on the audits configuration. See [Configuring audits](../../01-Developer-Guide/11-Quality-and-Evaluation/03-Automated-audits.md#configuring-audits).
  </Update>

  <Update label="June 15, 2026">
    ### Break out of loops early

    Loops support a new **Loop Break** node that exits the loop as soon as it's reached, like a `break` statement.

    **What's new:**

    * Add a **Loop Break** node inside a loop body — typically under a [Condition](../../01-Developer-Guide/03-Core-Nodes/09-Conditionals.md) — to stop iterating once a condition is met
    * A Loop Break cannot be placed under a Paths node that evaluates all matching paths

    **Who can use this:**\
    Available in the workflow editor. See [Loop Break](../../01-Developer-Guide/03-Core-Nodes/10-Loops.md#loop-break).

    ### Reference loop results as lists

    Outputs produced inside a loop now resolve as **lists** when referenced after the loop — for both sequential and parallel loops.

    **What's new:**

    * A node inside the loop that produces a variable resolves to a list (one value per iteration) when referenced from a node after the Loop End
    * This now applies to **sequential** loops as well as parallel loops; single-iteration loops return a one-item list, and sequential loops preserve iteration order
    * The [public API and SDK](https://docs.happyrobot.ai/api-reference) flag these variable groups with `is_list: true`

    **Who can use this:**\
    Available in the workflow editor and API. See [Referencing loop results outside the loop](../../01-Developer-Guide/03-Core-Nodes/10-Loops.md#referencing-loop-results-outside-the-loop).
  </Update>

  <Update label="June 13, 2026">
    ### Telnyx as an SMS provider

    SMS text agents can now run on **Telnyx** in addition to Twilio. Bring your own Telnyx account and numbers for inbound and outbound SMS.

    **What's new:**

    * A **Bring your own Telnyx** option in the SMS provider selector for inbound agents, outbound agents, and the **Send SMS** node
    * A new **Telnyx SMS** integration for storing your Telnyx API key, webhook public key, and messaging profile ID
    * To receive SMS, both the webhook public key and messaging profile ID are required — they can be left blank only for send-only (outbound) use

    **Who can use this:**\
    Available for SMS text agents. See [SMS text agents](../../01-Developer-Guide/06-Text-Agents/02-SMS.md#sms-provider) and the [Telnyx SMS integration](../../01-Developer-Guide/15-Integrations/04-Communication/07-Telnyx-SMS.md).
  </Update>

  <Update label="June 12, 2026">
    ### Experiments are now generally available

    Workflow experiments have graduated from beta. Running A/B tests on workflows no longer requires internal access — Experiments are available to all users with workflow access.

    **What's new:**

    * Split traffic between a control and treatment variant to validate changes before rollout
    * Compare targeted overrides — change prompts, models, or node settings without publishing a separate workflow version
    * Track platform and custom metrics so rollout decisions come from production data
    * Existing experiments are unaffected — only the beta label has been removed

    **Who can use this:**\
    Available to all users with workflow access, on the V3 workflow engine. See [Experiments](../../01-Developer-Guide/10-Experiments/01-Experiments.md).

    ### Reply with voice notes on WhatsApp

    WhatsApp text agents can now reply with voice notes instead of plain text.

    **What's new:**

    * A **Reply with voice notes** toggle in the agent's **Media processing** settings (WhatsApp channel only)
    * Pick the text-to-speech **Voice** used to synthesize replies from the searchable voice library
    * Regular text replies are delivered as WhatsApp voice notes; template messages still send as approved templates

    **Who can use this:**\
    Available for WhatsApp text agents. See [Reply with voice notes](../../01-Developer-Guide/06-Text-Agents/03-WhatsApp.md#reply-with-voice-notes).
  </Update>

  <Update label="June 11, 2026">
    ### Credit usage API endpoint

    A new public API endpoint reports credit consumption so you can build your own usage dashboards and billing reconciliation.

    **What's new:**

    * `GET /billing/usage/credits` returns credit consumption broken down by component (event type) per workflow
    * Bucket results by `daily`, `weekly`, or `monthly` granularity over a date range
    * Filter by folder or workflow name; results are scoped to the organization tied to your API key

    **Who can use this:**\
    Available to API users with a valid API key. See the **Billing** section of the [API reference](https://docs.happyrobot.ai/api-reference/overview).
  </Update>

  <Update label="June 10, 2026">
    ### Attach files to Frontal

    You can now attach files to a [Frontal](../../01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md) message to give the assistant visual or document context.

    **What's new:**

    * Drag files onto the chat input, or use the attach control, to include them with your next message
    * Supports images (JPEG, PNG, GIF, WebP), PDF, and text files — up to 5 files per message, 3.5 MB each (500 KB for text files)
    * Attachments appear as removable badges above the input

    **Who can use this:**\
    Available in the Frontal AI assistant inside the workflow editor. See [Attaching files](../../01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md#attaching-files).
  </Update>

  <Update label="June 9, 2026">
    ### Web sources for knowledge bases

    Knowledge bases can now stay in sync with a website. A **web source** is a managed connection that crawls a site on demand or on a schedule, replacing one-off URL scraping when you need content to stay current.

    **What's new:**

    * Add a web source with one of three **Source types**: **This page** (single URL), **Selected pages** (discover and pick pages), or **Entire website**
    * **Auto-refresh** on a **Daily**, **Weekly**, or **Monthly** schedule, plus **Auto-remove missing pages** to prune content that disappears from the site
    * A **sync runs** table per source shows each crawl's status and the number of discovered, processed, and updated pages — refresh or cancel crawls from here
    * Crawled pages appear as files in the knowledge base, so agents search them the same way as uploads

    **Who can use this:**\
    Available in **Assets → Knowledge Bases**. See [Web sources](../../01-Developer-Guide/14-Assets/01-Knowledge-Bases.md#web-sources).

    ### Inline attachment processing for Gmail and Outlook

    The email **Get Message** / **Get Email** and **Get Thread Messages** actions can now extract text from attachments inline — no separate **Parse Attachment** node required.

    **What's new:**

    * New **Process attachments** toggle on the Gmail **Get Message** / **Get Thread Messages** and Outlook **Get Email** / **Get Thread Messages** actions
    * Choose an **Attachment processor** — **Standard**, **Advanced**, or **Frontier** — to trade speed for accuracy on complex or scanned documents
    * Contact intelligence (memory, interaction limit, auto context injection) is now available on **outbound text agents** as well

    **Who can use this:**\
    Available for the Gmail and Outlook integrations. See [Gmail attachment processing](../../01-Developer-Guide/15-Integrations/04-Communication/01-Gmail.md#attachment-processing) and [Outlook attachment processing](../../01-Developer-Guide/15-Integrations/04-Communication/02-Outlook.md#attachment-processing).
  </Update>

  <Update label="June 8, 2026">
    ### Salesforce custom domains

    The Salesforce integration now supports connecting to sandbox orgs and orgs that use a custom **My Domain**.

    **What's new:**

    * An **Advanced** section when adding a Salesforce credential lets you set a custom **Salesforce Domain**
    * Use `login.salesforce.com` for production, `test.salesforce.com` for sandboxes, or your org's My Domain (e.g. `mycompany.my.salesforce.com`)

    **Who can use this:**\
    Available for the Salesforce integration. See [Custom Salesforce domain](../../01-Developer-Guide/15-Integrations/06-Data-and-Storage/06-Salesforce.md#custom-salesforce-domain).

    ### SIP trunk attribute-to-header mappings

    Inbound and bidirectional SIP trunks can now forward call attributes to your carrier as SIP headers.

    **What's new:**

    * A new **Attribute → Header mappings** option on inbound and bidirectional trunks maps room attributes set by workflow tools (for example, on hangup) to outbound SIP header names

    **Who can use this:**\
    Available when creating a SIP trunk in **Assets → Telephony**. See [SIP trunks](../../01-Developer-Guide/14-Assets/03-Telephony.md#sip-trunks).
  </Update>

  <Update label="June 5, 2026">
    ### Advanced Python: Standard and Advanced execution profiles

    The **Advanced Python** custom-code node now lets you pick an **execution profile** that controls which packages the sandbox loads.

    **What's new:**

    * A **Standard / Advanced** segmented control at the top of the node
    * **Standard** runs sandboxed Python with the standard library only — no third-party packages
    * **Advanced** routes to the larger sandbox profile that adds `pandas` and `numpy`
    * New nodes default to **Standard**; network access and arbitrary package installs remain disabled in both profiles
    * The `execution_profile` field is also exposed through the [API](https://docs.happyrobot.ai/api-reference) and SDK

    **Who can use this:**\
    Available on the **Advanced Python** node in the workflow editor. See [Custom Code — Execution profile](../../01-Developer-Guide/03-Core-Nodes/05-Custom-Code.md#execution-profile).
  </Update>

  <Update label="June 4, 2026">
    ### Twilio Business Profiles

    You can now create and manage Twilio **Business Profiles** for US calling compliance directly from the Telephony page, then attach an approved profile to regular US Twilio numbers.

    **What's new:**

    * New **Add New > Business Profile** action on the **Compliance** tab, with a guided dialog for business, address, and authorized-representative details
    * **Sync Business Profiles from Twilio** button to import profiles created in the Twilio Console and refresh their statuses
    * Approved business profiles can be selected when buying a regular US Twilio number — selecting one is optional, with a warning shown when none is set
    * New optional `business_profile_application_id` parameter on the [buy phone number](https://docs.happyrobot.ai/api-reference) API

    **Who can use this:**\
    Available in **Assets → Telephony → Compliance** for orgs using Twilio. See [Compliance — Business profiles](../../01-Developer-Guide/14-Assets/03-Telephony.md#business-profiles).
  </Update>

  <Update label="June 2, 2026">
    ### Outbound calls: dynamic verified caller ID

    The workflow outbound-call **Verified caller ID** field now has two modes, so you can pick a verified number from a dropdown or supply one at runtime.

    **What's new:**

    * **Verified** mode (default) — a dropdown of your completed verified caller IDs, with a warning when a saved static value no longer matches a verified number
    * **Dynamic** mode — click **Use a dynamic value** to enter a templated value with variables (e.g. `@trigger.caller_id` or a literal `{{...}}`), useful when you pick the caller ID at runtime, have many verified numbers, or verify on a carrier whose numbers aren't listed
    * Dynamic values are not checked against your verified caller IDs — calls fail if the resolved number isn't actually verified

    **Who can use this:**\
    Available on the outbound voice agent node. See [Destination and caller ID](../../01-Developer-Guide/05-Voice-Agents/03-Outbound-Calls.md#destination-and-caller-id).
  </Update>

  <Update label="June 1, 2026">
    ### Recording disclaimer flow simplified

    The voice agent recording disclaimer configuration has been streamlined into a single dropdown. The standalone **Play recording message** toggle is gone — choose **No disclaimer** to skip the disclaimer entirely, or pick a style that fits your call.

    **What's new:**

    * One **Recording disclaimer** dropdown with options: **No disclaimer**, **Robotic voice (legacy)**, **Natural voice**, and **Custom recording**
    * Custom recordings now support a **Dynamic** mode — provide a templated string (with [variables](../../01-Developer-Guide/02-Workflows/07-Variables.md)) that the TTS engine reads at call time, useful when the disclaimer needs to vary per call (region, campaign, recipient)
    * Existing custom recordings continue to work as **Static** audio assets from **Assets → Audio**
    * New **Copy Asset ID** action on each audio asset's menu in the Audio Library

    **Who can use this:**\
    Applies to all voice agent nodes (inbound, outbound, outbound with callback). See [Recording and disclaimers](../../01-Developer-Guide/05-Voice-Agents/02-Inbound-Calls.md#recording-and-disclaimers).

    ### AI Extract: parameter descriptions are now required

    In **Parameters** mode, the AI Extract node now requires a non-empty **Description** on every parameter (in addition to a name). A parameter with a missing description marks the node as incomplete, preventing extraction errors at runtime.

    **Who can use this:**\
    Applies to all AI Extract nodes configured in Parameters mode. See [AI Extract](../../01-Developer-Guide/03-Core-Nodes/02-AI-Extract.md).
  </Update>

  <Update label="May 31, 2026">
    ### Deliver Text Session Message node

    A new **Deliver Text Session Message** action node (Text category) pushes a templated message directly into a running text agent session — such as the chatbot widget — without invoking the LLM.

    **What's new:**

    * Delivers the **Message** verbatim into the session referenced by **Session ID** (typically `@Agent.session_id`)
    * Both fields support [variables](../../01-Developer-Guide/02-Workflows/07-Variables.md) and are required
    * Useful for deterministic, scripted output (status updates, payload cards, handoff notices) where you don't want an AI-generated reply

    **Who can use this:**\
    Available in the workflow editor for any text agent session. See [Delivering a message into a session](../../01-Developer-Guide/06-Text-Agents/05-Chatbot.md#delivering-a-message-into-a-session).

    ### Escalation Control API for Generic Webhook text agents

    The Generic Webhook escalation mode now exposes a second inbound endpoint your operator system can call to end an active escalation without having to send a reply message.

    **What's new:**

    * **Escalation Control** endpoint: `POST /generic-escalation/control`
    * Body accepts `session_id`, `action` (`back_to_agent` or `close_session`), and an optional `reason`
    * `back_to_agent` returns control to the AI agent; `close_session` ends the underlying text session
    * Reuses the existing **Inbound Secret** — no new credential to provision
    * The agent settings panel now shows an **Inbound APIs** section with **Inbound Reply** and **Escalation Control** tabs, each with a copyable URL and JSON payload schema

    **Who can use this:**\
    Available on every text agent escalation set to **Generic Webhook** mode. See [Escalation](../../01-Developer-Guide/06-Text-Agents/01-Text-Agents-Overview.md#escalation).

    ### HappyRobot V1 voices deprecation notice

    Workflow versions that still use a HappyRobot V1 voice now show a **V1 voices deprecation** badge in the editor. Hover the badge for migration guidance.

    **What's new:**

    * The deprecation badge appears whenever any node in the workflow version selects a static HappyRobot V1 voice
    * Migrate any agent on a V1 voice to a V2 voice before **June 12, 2026**
    * After the deprecation date, V1 voices on any remaining workflow versions are automatically reassigned to the equivalent V2 voice with no service disruption

    **Who can use this:**\
    The badge is visible to every user on workflow versions that reference a V1 voice. See [Voices](../../01-Developer-Guide/14-Assets/04-Voices.md).

    ### Frontal skills: global skills curated by HappyRobot

    The wording and ownership of global Frontal skills has been clarified. Global skills are now described as authored and curated by HappyRobot, rather than by your organization's administrators.

    **What's new:**

    * Global skills explicitly reflect HappyRobot-authored guidance applied to every chat in every organization
    * You can still **Request global availability** on a personal skill — the request goes to the HappyRobot team for review

    **Who can use this:**\
    Applies to every Frontal user. See [Global skills](../../01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md#global-skills).

    ### MCP server credential edits

    The MCP server integration form now properly loads existing credential values when you open one for editing. Switching between credentials in the same session also resets the form to the correct values instead of preserving stale state.

    **Who can use this:**\
    Applies to anyone configuring an MCP server credential. See [MCP Server Setup](../../01-Developer-Guide/04-Tools/06-MCP-Server-Setup.md).
  </Update>

  <Update label="May 29, 2026">
    ### Inbound email address uniqueness

    Inbound email text agents now register their monitored email address in the platform's channel routing table, the same way inbound SMS and WhatsApp numbers do. A given inbound mailbox can only be assigned to one published agent at a time — publishing a second workflow on the same address fails with a conflict error.

    **Who can use this:**\
    Applies to every inbound email text agent. See [Email subscription](../../01-Developer-Guide/06-Text-Agents/04-Email.md#email-subscription).

    ### Email initial-message attachments

    Outbound email text agents can now attach one or more files to the **first** email they send. The new **Attachments** field lives in the Initial Email Message section and accepts public URLs.

    **What's new:**

    * New **Attachments** field above the body in the outbound email agent configuration
    * Multiple URLs are supported — separate them with commas or place one per line
    * Each URL supports [variables](../../01-Developer-Guide/02-Workflows/07-Variables.md), so you can attach per-recipient documents like contracts, invoices, or rate confirmations
    * Each attachment is fetched server-side; 25 MB cap per file

    **Who can use this:**\
    Available for outbound text agents on the email channel. See [Initial email content](../../01-Developer-Guide/06-Text-Agents/04-Email.md#initial-email-content-outbound-only).

    ### WhatsApp per-phone callback overrides

    The WhatsApp integration's **Migrate to Cloud API** tab is now a single unified table across every WhatsApp credential — no more credential picker — and exposes a new per-phone callback release action.

    **What's new:**

    * Single table view that lists every phone number across all WhatsApp credentials, with filters for sync status, verification status, and migration status
    * New **Release callback override** action on each row — clears a per-phone webhook override so Meta falls back to the WhatsApp Business Account or app-level callback
    * Phone numbers claimed by another HappyRobot cluster are flagged in the table, and now also appear dimmed in agent phone-number selectors with a link to **Cloud settings** for fixing the claim

    **Who can use this:**\
    Available in **Integrations → WhatsApp → Migrate to Cloud API** for any org with the WhatsApp integration enabled. See [WhatsApp number management](../../01-Developer-Guide/15-Integrations/04-Communication/08-WhatsApp.md#whatsapp-number-management).
  </Update>

  <Update label="May 28, 2026">
    ### Recording player: playback rate and download

    The recording player in the run details panel has been rebuilt around a new audio component. It still sticks to the top of the panel as you scroll, but now exposes additional controls.

    **What's new:**

    * **Playback rate** button — speed up or slow down review (e.g., 1.25×, 1.5×, 2×)
    * **Download** button — save the recording audio file locally without needing the API
    * Existing controls — play/pause, scrubber, time and duration display, volume — work the same as before, and the transcript-linked seek behaviour is preserved

    **Who can use this:**\
    Available for every voice run with recording enabled. See [Recordings](../../01-Developer-Guide/09-Runs-and-Monitoring/04-Recordings.md#playing-recordings-in-the-platform).

    ### Voice agents: extension field is warm-handoff only

    In the **Direct Transfer** node, the **To extension** field now only appears when the transfer type is **Warm handoff**. It is hidden for **Direct transfer** and **Whisper transfer** modes, where it was never carried into the outgoing SIP signaling.

    **Who can use this:**\
    Applies to all Direct Transfer nodes. See [Call transfer](../../01-Developer-Guide/05-Voice-Agents/06-Prompts-and-Tools.md#call-transfer).

    ### Voice agents: inline signal subscriptions

    The **Agent signals** configuration section — previously available only on text agents — now appears inside the configuration panel of every voice agent (inbound, outbound, outbound-with-callback). You can enable signals, add custom topics, and toggle response-on-signal directly while editing the agent. Workflow-level signal settings still work and stay in sync. See [Inbound signal subscriptions](../../01-Developer-Guide/16-Account-and-Settings/10-Workflow-Settings.md#inbound-signal-subscriptions).
  </Update>

  <Update label="May 27, 2026">
    ### ElevenLabs v3 voices

    Voices from ElevenLabs' new **v3** model family are now selectable in the voice library and inside voice agents.

    **What's new:**

    * New `eleven_v3` model family available in the voice picker, including the `eleven_v3_conversational` voice
    * v3 voices use a tuned expressive stability (`0.75`) by default
    * **Gain** and **speed** controls are hidden when a v3 voice is selected — these settings are not supported by the v3 family and would be ignored

    **Who can use this:**\
    Available wherever voices are configured — voice agent nodes and **Assets → Voices**. See [Per-voice settings](../../01-Developer-Guide/05-Voice-Agents/05-STT-TTS-and-LLM-Configuration.md#per-voice-settings-v3).
  </Update>

  <Update label="May 25, 2026">
    ### Gemini 3.5 Flash voice models

    Three new Gemini 3.5 Flash variants are now available in the model picker — frontier-class flash models with better performance than Gemini 3 Flash, configurable across reasoning depths.

    **What's new:**

    * **`gemini-3.5-flash-minimal`** (\~600ms, Light tier) — no reasoning, fastest variant
    * **`gemini-3.5-flash-low`** (\~800ms, Light tier) — light reasoning
    * **`gemini-3.5-flash-medium`** (\~1200ms, Standard tier) — medium reasoning

    **Who can use this:**\
    Available everywhere a model is selected in HappyRobot. See [Models](../../01-Developer-Guide/14-Assets/05-Models.md#gemini-3.5-flash-minimal) for descriptions, latencies, and IDs.

    ### Custom title and description for apps

    When you create or edit an app, the app's name and description are now exposed to the deployed Next.js project so your app code can drive page titles, meta tags, and any user-visible copy that should match the app's identity in HappyRobot.

    **What's new:**

    * The app's display name is available to your app code, updating automatically when you rename the app
    * The app's description is available too, falling back to a default when none is set
    * Both values are managed by HappyRobot and injected on every preview and production deployment

    **Who can use this:**\
    Available for all organizations using the Apps feature. See [Environment variables](../../01-Developer-Guide/07-Apps/07-Environment-Variables.md) for the full list of values your app receives.
  </Update>

  <Update label="May 22, 2026">
    ### Advanced Python node (beta)

    A second Python variant — **Advanced Python** — is now available in the workflow node picker alongside the existing **Run Python** node. It runs your code in an isolated sandbox with the `data-science-v1` package profile, exposing `pandas` and `numpy` for data-frame and numerical work.

    **What's new:**

    * New **Advanced Python** action under the Code category, marked **beta** in the sidebar header
    * Available libraries: `pandas`, `numpy`, `datetime`, `json`, `re` — network access and arbitrary package installs are disabled inside the sandbox
    * Same input/output contract as Run Python: inputs are exposed as the `input_data` dict and you return results by assigning to `output`

    **Who can use this:**\
    Available in the workflow editor for all organizations. See [Custom Code](../../01-Developer-Guide/03-Core-Nodes/05-Custom-Code.md#advanced-python-beta) for details.

    ### Language hints for advanced audio transcription

    Text agents with the **advanced** transcription tier can now bias the transcriber toward one or more expected languages. This improves accuracy for contacts who send audio in multiple languages or in a language the engine doesn't pick up reliably on its own.

    **What's new:**

    * New **Language hints** field in the agent's media processing settings, visible only when transcription is set to the advanced tier
    * Searchable multi-select of supported languages — leave empty for automatic detection
    * Applies to all text agent channels (SMS, WhatsApp, email, chatbot, Slack, Teams) with media processing enabled

    **Who can use this:**\
    Available for text agents using the advanced transcription tier. See [Media processing](../../01-Developer-Guide/06-Text-Agents/01-Text-Agents-Overview.md#media-processing).

    ### Inline transcripts for audio attachments in runs

    The run details panel now shows a **Transcription** toggle beneath every audio attachment that was processed by the text agent media pipeline. Expand it to read the transcript the LLM saw, without re-listening to the audio.

    **Who can use this:**\
    Visible automatically on any run whose audio attachments were transcribed via [media processing](../../01-Developer-Guide/06-Text-Agents/01-Text-Agents-Overview.md#media-processing). See [Artifacts](../../01-Developer-Guide/09-Runs-and-Monitoring/03-Transcripts-and-Messages.md#artifacts).

    ### Cartesia voices migrated to sonic-3

    All Cartesia voices in the platform now use the `sonic-3` model. Existing voices were migrated automatically in place, and the **Add new voice** dialog defaults new Cartesia voices to `sonic-3`. No action is required.
  </Update>

  <Update label="May 21, 2026">
    ### Public API: trigger a workflow run with a file upload

    The `POST /workflows/{workflow_id}/runs` endpoint and the TypeScript SDK's `workflows.triggerRun` now accept `multipart/form-data` in addition to JSON. Send a `file` form field along with any extra fields and the request is forwarded to the workflow's trigger node the same way an [API file upload](../../01-Developer-Guide/02-Workflows/05-Triggers.md#api-file-upload) trigger would receive it.

    **What's new:**

    * `POST /workflows/{workflow_id}/runs` accepts `multipart/form-data` requests with a `file` field, optional extra form fields, and `environment` as a query parameter
    * The TypeScript SDK auto-detects multipart payloads — pass `{ file, payload, environment }` to `workflows.triggerRun` and the SDK switches transports
    * JSON payloads continue to work unchanged

    **Who can use this:**\
    Available for any API client with a valid HappyRobot API key. See [API Reference — Triggering with a file upload](https://docs.happyrobot.ai/api-reference/overview#triggering-with-a-file-upload).

    ### Genesys SIP trunks: skip the per-trunk IP allowlist

    The **Create SIP Trunk** dialog now has a **Genesys carrier** toggle. When enabled, the per-trunk allowed-addresses field is hidden and the trunk is created without an IP allowlist entry — Genesys source IPs are pre-trusted at HappyRobot's SBC.

    **What's new:**

    * New **Genesys carrier** switch under the allowed-addresses section of the trunk creation dialog
    * Inbound or bidirectional trunks no longer require at least one allowed address when the toggle is on
    * Outbound-only trunks are unaffected (they never required an allowlist)

    **Who can use this:**\
    Available in the SIP trunk creation dialog for all organizations. See [SIP trunks > Optional settings](../../01-Developer-Guide/14-Assets/03-Telephony.md#optional-settings).

    ### Frontal: marketplace integrations

    The Frontal AI workflow assistant now knows about every provider in the [integrations marketplace](../../01-Developer-Guide/15-Integrations/03-Integrations-marketplace.md) (CRM, HRIS, ATS, accounting, ticketing, file storage). You can ask Frontal to add actions for connected providers — for example, "Add a HubSpot create-contact action after the AI Extract node" — and it will propose the matching marketplace action.

    **Who can use this:**\
    Available wherever Frontal is. See [Frontal AI assistant](../../01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md).
  </Update>

  <Update label="May 19, 2026">
    ### Transcribe keypresses toggle on voice agents

    Voice agent nodes have a new **Transcribe keypresses** toggle in the **Advanced** section. When enabled (the default), caller DTMF keypresses are transcribed and treated as user turns, interrupting the agent. Disable it to ignore accidental keypresses that would otherwise derail the conversation.

    **Who can use this:**\
    Available on inbound, outbound, and outbound-with-callback voice agent nodes. See [Transcribe keypresses](../../01-Developer-Guide/05-Voice-Agents/05-STT-TTS-and-LLM-Configuration.md#transcribe-keypresses).

    ### Send SMS node

    A new **Send SMS** action node sends a one-off SMS message from a workflow without starting a conversation session. The older Send Text node is now deprecated.

    **What's new:**

    * New **Send SMS** node under the Text category in the node picker, with fields for recipient (`To`), `Message` body, and SMS provider selection
    * Provider options match the SMS agent: **Use existing toll-free** or **Bring your own Twilio**, including regional Twilio credentials
    * The deprecated **Send Text** node still works but is no longer maintained — a banner in the configuration panel points to Send SMS

    **Who can use this:**\
    Available in the workflow editor for all organizations. See [SMS text agents](../../01-Developer-Guide/06-Text-Agents/02-SMS.md#sending-a-one-off-sms) for details.

    ### Yearly billing for manual SIP trunks

    Custom SIP trunks (created in **Assets > Telephony**) now create a yearly recurring billing item automatically when provisioned and end the recurring item when the trunk is deleted. No action is required on existing trunks.
  </Update>

  <Update label="May 18, 2026">
    ### Generic Webhook escalation for text agents

    Text agents can now escalate to any HTTP endpoint via a configurable **Generic Webhook** mode, in addition to the existing HappyRobot Platform, CXone, Richpanel, and Email-in-thread modes.

    **What's new:**

    * Configure an **Inbound Secret** and copyable **Inbound URL** so your endpoint can post agent replies back to HappyRobot
    * Three independently configurable outbound hooks — **Escalation Start**, **User Message**, and **Escalation End** — each with URL, headers, body (via schema builder), content type, and authentication (None, API Key, Bearer, Basic)
    * Body templates can reference escalation context variables: `session_id`, `event_type`, `reason`, `message_id`, `message_body`, `identity`, `channel`, and `history`

    **Who can use this:**\
    Available for all text agent channels (SMS, WhatsApp, email, chatbot, Slack, Microsoft Teams). See [Escalation](../../01-Developer-Guide/06-Text-Agents/01-Text-Agents-Overview.md#escalation).

    ### Custom SIP BYE headers on tool end-call

    Tool nodes that end a voice call after execution can now send custom SIP headers on the BYE message — useful for passing routing reasons or metadata back to your SBC or downstream systems.

    **What's new:**

    * Enable **End call after this tool** in a tool node, then add **BYE headers** as key/value pairs
    * Header values support workflow variables, so headers can carry per-call routing data
    * Common examples: `X-RouteReason`, `X-RouteType`, `X-RouteValue`, `X-MetaData`

    **Who can use this:**\
    Available on tool nodes attached to voice agent prompt nodes. See [Creating tools](../../01-Developer-Guide/04-Tools/02-Creating-Tools.md#end-call-after-tool).

    ### Wallet alert thresholds

    Wallets now support configurable warning and critical alert thresholds. Owners of the target organization receive email notifications when consumption crosses each threshold.

    **What's new:**

    * New **Warning** (default 70%) and **Critical** (default 90%) percentage fields on wallet create and edit
    * Warning must be lower than Critical; values are validated on save
    * Thresholds apply per wallet, so different wallets can have different alerting policies

    **Who can use this:**\
    Available in **Settings > Wallets** for all organizations. See [Wallet alert thresholds](../../01-Developer-Guide/16-Account-and-Settings/09-Usage-and-Billing.md#wallet-alert-thresholds).
  </Update>

  <Update label="May 17, 2026">
    ### SIP trunk direction selector

    When creating a custom SIP trunk in **Assets > Telephony**, you can now pick a direction — **Inbound and outbound**, **Inbound only**, or **Outbound only** — and the form only requires the fields that apply.

    **What's new:**

    * **Inbound only** trunks skip the SIP server address requirement (HappyRobot has nothing to dial outbound)
    * **Outbound only** trunks skip the source-IP allowlist (no inbound side to gate)
    * **Inbound and outbound** continues to require both, matching the previous behavior
    * Existing trunks are read back as "Inbound and outbound" with no migration needed

    **Who can use this:**\
    Available in the SIP trunk creation dialog for all organizations. See [SIP trunks](../../01-Developer-Guide/14-Assets/03-Telephony.md#sip-trunks).

    ### Run URL variable

    A new `current.run_url` built-in variable resolves to a deep link to the current run in the HappyRobot platform. Useful for outbound notifications, escalations, and any message where you want to point recipients at the run record.

    **Who can use this:**\
    Available in every workflow alongside the existing `current.run_id` and related built-ins. See [Current variables](../../01-Developer-Guide/02-Workflows/07-Variables.md#current-variables).
  </Update>

  <Update label="May 15, 2026">
    ### Frontal skills

    Frontal, the AI workflow assistant, now accepts reusable instructions called **skills** — short Markdown addendums you can attach to a conversation to capture conventions Frontal should follow.

    **What's new:**

    * Click the **+** button next to the Frontal input and open the **Skills** submenu to tick skills on or off for the current conversation; selected skills appear as chips above the input
    * Create personal skills from **Manage skills** with a name, optional description, and Markdown content — skills you create are scoped to your user
    * Organization admins can publish **global skills** that apply to everyone in the org; they appear alongside personal skills in the same submenu
    * Authors can **request global availability** for a personal skill from the skill's menu; admins review pending requests and either approve (the skill becomes global) or reject (it stays personal)
    * Skill content is rejected at save time if it contains phrases that look like prompt-injection attempts ("ignore previous instructions", "reveal system prompt", and similar)
    * Skills are appended to Frontal's system prompt as labeled sections — they can shape tone, formatting, and working style but cannot grant new tools or override safety guardrails

    **Who can use this:**\
    Available wherever Frontal is — open Frontal in any workflow editor. See [Frontal AI assistant — Skills](../../01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md#skills) for details.

    ### Workflow signals settings

    The workflow settings page's **Webhooks** section has been replaced with a broader **Signals** tab covering both outbound delivery and inbound subscriptions.

    **What's new:**

    * **Outbound** sub-tab — the existing webhook configuration, used to deliver signals to external systems
    * **Inbound** sub-tab — subscribe each agent in the workflow to specific signal topics. Default topics (`session.<current>`, `usecase.<current>`, `org.<current>`) are enabled when signals are on, and you can add custom topics with binding patterns from the **Subscribe to custom signals** dialog
    * **Start agent response on signal** toggle controls whether incoming signals wake the agent to generate a reply, or are only delivered for the agent to read while it's already speaking

    **Who can use this:**\
    Available on the **Signals** tab of any workflow's settings page. See [Workflow Settings — Signals](../../01-Developer-Guide/16-Account-and-Settings/10-Workflow-Settings.md#signals) for details.

    ### Per-environment inbound signals

    Inbound signal subscriptions on voice and text agents can now be configured independently per environment. Previously the same subscriptions applied to production, staging, and development; now each environment has its own.

    **What's new:**

    * The Inbound sub-tab on the **Signals** settings page shows an environment switcher (Production, Staging, Development) for every inbound-signal-capable agent
    * Adding, removing, or editing a custom subscription applies only to the selected environment
    * Default topics (`org.<id>`, `usecase.<id>`, `session.<current>`) now show the actual org and use case IDs so you can copy them without manual substitution
    * The **copy** button next to a topic now copies a full JSON signal payload (key + sample payload) instead of just the topic key — paste it directly into a `POST /signals` request body

    **Who can use this:**\
    Available on the **Signals** tab for any V3 workflow that includes a voice or text agent.

    ### Apps RBAC: viewer and editor roles

    The role-based access control (RBAC) tree now exposes app-scoped role groups alongside the existing workflow groups, so IDP-managed access to the Apps feature can be granted independently of workflow access.

    **What's new:**

    * New **all apps** group at the workspace level grants Viewer or Editor access to every app in that workspace
    * Each individual app exposes its own **Viewer** and **Editor** group, so access can be scoped to a single app
    * Apps support **Viewer** and **Editor** roles only — there is no Owner role at the app level
    * The **Create App** button and the per-row **Edit** and **Delete** actions in the Apps table are now hidden for users without Editor permission on that scope

    **Who can use this:**\
    Available for organizations using RBAC with the Apps feature.

    ### Billing: detailed text channel breakdown

    The communication usage breakdown in **Settings > Billing** now preserves channel detail for texting instead of collapsing everything into "Email" or "Other".

    **What's new:**

    * Texting credits and message counts are now broken out per channel: **WhatsApp**, **SMS**, **Emails**, **Chatbot Messages**, **Teams Messages**, **Slack Messages**, and **Other**
    * Each row links to a tooltip explaining the channel
    * Channel labels are now title-cased for consistency with the rest of the dashboard

    **Who can use this:**\
    Available in **Settings > Billing** for all organizations on credit-based plans.
  </Update>

  <Update label="May 14, 2026">
    ### Public API: get current organization

    A new `GET /org` endpoint on the public REST API returns basic information about the authenticated organization.

    **What's new:**

    * Returns `id`, `name`, `slug`, and `tier` for the organization that owns the API key making the request
    * Use it to display the active organization in custom dashboards or to verify which org a key belongs to before making other API calls

    **Who can use this:**\
    Available to any API client with a valid HappyRobot API key. See the [API Reference](https://docs.happyrobot.ai/api-reference) for full endpoint details.
  </Update>

  <Update label="May 12, 2026">
    ### Self-serve verified caller IDs

    You can now verify external phone numbers directly from the HappyRobot UI and assign them as the **Verified caller ID** on outbound voice agents — no need to verify in the Twilio Console and paste the number manually.

    **What's new:**

    * New **Verified Numbers** tab on **Assets > Telephony** lists every verified number with its status (pending, completed, failed, expired, or removed)
    * Start a verification with **Add New > Verified Number** — HappyRobot calls the number and prompts the user to enter a 6-digit code on the keypad
    * The list live-syncs with Twilio on every visit, so numbers you verified directly in the Twilio Console show up automatically and numbers removed there are flagged as `removed`
    * The outbound voice agent **Verified caller ID** field now renders as a dropdown of completed verified numbers, with a **Use a custom value** escape hatch for templated values with variables

    **Who can use this:**\
    Available for all organizations on the **Assets > Telephony** page. See [Verified numbers](../../01-Developer-Guide/14-Assets/03-Telephony.md#verified-numbers) for the verification flow.

    ### MCP tools: typed argument editor

    The **MCP Call** node's tool argument editor now adapts to the parameter type declared on the MCP server.

    **What's new:**

    * `array` parameters get a list editor so you can add or remove items
    * `object` parameters get a JSON input with an example placeholder
    * `string`, `number`, and `boolean` parameters keep the single templated text input

    **Who can use this:**\
    Available for all MCP tools added to a workflow. See [MCP Tools — Tool argument types](../../01-Developer-Guide/04-Tools/05-MCP-Tools.md#tool-argument-types).

    ### Experiment indicator on runs

    The **Version** column on the Runs page now shows a small flask icon next to runs that are part of an active experiment. Hover the icon to see the experiment name and variant.

    **Who can use this:**\
    Available in the Runs page for any organization with active experiments.

    ### OCR Playground: insert result as node output

    The OCR Playground now has a **Use as node output** action that pushes the playground's extracted result back into the OCR node's output. Downstream nodes can then reference the real extracted values during configuration without needing a workflow run to populate the schema.

    **Who can use this:**\
    Available in the OCR Playground for any **OCR Extract** node. See [File Operations — OCR Extract](../../01-Developer-Guide/03-Core-Nodes/08-File-Operations.md#ocr-extract).
  </Update>

  <Update label="May 10, 2026">
    ### Redesigned model picker

    The LLM model picker used across voice agents, text agents, AI nodes, and evaluation has been rebuilt around a searchable, provider-grouped panel.

    **What's new:**

    * Brand icons and provider grouping with a pinned **Recommended** section, plus an icon-only provider filter for narrowing quickly
    * Latency badges and a tooltip on every row showing the model's latency tier and time-to-first-token estimate, sourced from [Artificial Analysis](https://artificialanalysis.ai/models)
    * "New" and "Most used" badges to surface fresh and proven options
    * Search works across model name, ID, and provider — keyboard navigation with full ARIA support
    * The picker preserves deprecated or restricted selections so existing workflows continue to render their saved model

    **Who can use this:**\
    Available everywhere a model is selected in HappyRobot. See [Models](../../01-Developer-Guide/14-Assets/05-Models.md) for the full catalog.

    ### New models across vendors

    Several frontier and specialist models are now available in the catalog.

    **What's new:**

    * **OpenAI gpt-5.5** — OpenAI's newest flagship; a step up in coding, agentic work, and professional reasoning
    * **Anthropic Claude Opus 4.7** — Anthropic's newest flagship; step-change improvement in agentic coding and complex reasoning
    * **Google Gemini 3.1 Flash Live** — Real-time dialogue model optimized for low-latency conversational use cases like voice agents
    * **Mistral Codestral, Devstral 2, Nemo 12B, Leanstral** — Four new Mistral specialists for coding and high-volume tasks
    * **xAI Grok 4.20 Multi-agent** — Grok 4.20 variant built for orchestrated multi-step agentic workflows
    * Premium-capacity variants are now marked **Priority** in the picker — same underlying model with dedicated throughput so replies stay fast under load, at a slightly higher per-call cost

    The older `gemini-3-flash-*` family is now marked deprecated and superseded by `gemini-3.1-flash-lite` / `gemini-3.1-pro-high`.

    **Who can use this:**\
    Available to all organizations. See [Models](../../01-Developer-Guide/14-Assets/05-Models.md) for descriptions, latencies, and IDs.
  </Update>

  <Update label="May 8, 2026">
    ### Custom test outputs for nodes

    Action, event, and loop nodes now keep a versioned history of their test outputs and let you author a custom one by hand.

    **What's new:**

    * **Output Schema Version selector** — every test run is saved and listed by timestamp in the node's testing panel. Switch between past outputs to compare runs or restore an earlier shape that downstream nodes were wired against
    * **Custom Output dialog** — click the `{ }` icon next to the version selector to paste or edit a JSON object directly in a Monaco editor. The custom output becomes the active schema for the `@` variable picker, so you can scaffold downstream nodes before the upstream integration is ready
    * **Empty-state placeholder** — nodes with no saved outputs now show a "No saved outputs yet" message instead of an empty selector

    **Who can use this:**\
    Available for all workflows. The braces button is disabled on published (immutable) versions. See [Creating a workflow](../../01-Developer-Guide/02-Workflows/02-Creating-a-Workflow.md#node-output-schemas) for details.

    ### Multiple inbound phone numbers for SMS and WhatsApp text agents

    Inbound SMS and WhatsApp agents can now answer messages on multiple phone numbers — a single agent listens across any number of numbers configured in a list.

    **What's new:**

    * New **Phone numbers** list in the inbound SMS and inbound WhatsApp configurations. Each row registers one number with the agent.
    * SMS rows let you mix **Use existing toll-free** and **Bring your own Twilio** providers in the same agent.
    * WhatsApp rows can use different credentials, businesses, and business accounts per phone.
    * Timeout and reminder message **templates are configured per phone number** in WhatsApp, so each number can use templates from its own WhatsApp Business Account.
    * Numbers already assigned to a published inbound agent are hidden from the picker to prevent conflicts.

    **Who can use this:**\
    Available for all organizations. See [SMS](../../01-Developer-Guide/06-Text-Agents/02-SMS.md#multiple-inbound-phone-numbers) and [WhatsApp](../../01-Developer-Guide/06-Text-Agents/03-WhatsApp.md#multiple-inbound-phone-numbers) for setup.

    ### Voice agent LLM: Model Catalog or BYO LLM

    The voice agent prompt node's **Use Custom LLM** Yes/No toggle has been replaced with a clearer **Model Catalog | BYO LLM** segmented control.

    **What's new:**

    * **Model Catalog** selects from HappyRobot's curated set of integrated providers (OpenAI, Anthropic, Google, Mistral, xAI)
    * **BYO LLM** routes traffic to your own Chat Completions-compatible endpoint — vLLM, Ollama, Groq, Together, Azure, OpenRouter, Cerebras, or any compatible server
    * HappyRobot still owns voice orchestration and built-in tools (hangup, transfer) under either choice

    **Who can use this:**\
    Available in voice agent prompt nodes. See [Custom LLM server](../../01-Developer-Guide/05-Voice-Agents/05-STT-TTS-and-LLM-Configuration.md#llm-source-model-catalog-or-custom-llm-server) for setup.

    ### Twin: foreign keys

    Twin tables now support foreign-key constraints, both when creating a new table and on existing tables.

    **What's new:**

    * A **Foreign keys** section in the Create Table sheet, Edit Columns sheet, and table preview panel
    * Configure source column, referenced table and column, and ON UPDATE / ON DELETE actions (`NO ACTION`, `RESTRICT`, `CASCADE`, `SET NULL`, `SET DEFAULT`)
    * Live tables preview orphan rows before adding the constraint — if any rows would violate it, the operation is blocked and a sample is shown so you can clean them up first
    * The Twin canvas draws an edge between related tables once a foreign key exists

    **Who can use this:**\
    Available for all organizations with a provisioned [Twin database](../../01-Developer-Guide/15-Integrations/06-Data-and-Storage/07-Twin-database.md#foreign-keys).

    ### Telephony: Panama numbers

    Panama (PA) is now selectable in the country picker when buying a phone number in **Assets > Telephony**.
  </Update>

  <Update label="May 7, 2026">
    ### Backfill historical runs into Twin Dump tables

    Twin Dump tables can now be populated with completed workflow runs from before the dump existed. Backfills run in the background while live runs continue to write rows normally.

    **What's new:**

    * **Backfill at table creation** — when creating a new dump, check **Also start a backfill** and choose a window of completed runs to replay
    * **Backfill an existing table** — click **Backfill** in the dump table toolbar to view past jobs and start a new one
    * **Run estimate** — the create-dump sheet shows how many completed runs fall in your selected window before you submit
    * **Job history** — every backfill records its window, status (queued, running, succeeded, failed), and processed/succeeded/failed counts in the Backfill sheet

    **Limits in beta:** windows are capped at 90 days, jobs at 20,000 runs each, and only one backfill can be queued or running per table at a time.

    **Who can use this:**\
    Available for all organizations with a provisioned Twin database. See [Twin Dump → Backfill historical runs](../../01-Developer-Guide/15-Integrations/06-Data-and-Storage/07-Twin-database.md#backfill-historical-runs) for the full guide.

    ### Voice sample download

    The voice library's Text to Speech tab has a new download button next to the play control. Click it to save the generated sample as a `.wav` file named after the voice (e.g., `Aria.wav`) — useful for sharing clips with stakeholders, keeping a reference clip, or comparing voices outside the platform.

    **Who can use this:**\
    Available in **Assets → Voices** for all organizations. See [Voices](../../01-Developer-Guide/14-Assets/04-Voices.md#text-to-speech) for details.
  </Update>

  <Update label="May 4, 2026">
    ### Marketplace webhook triggers: data-change events

    Webhook triggers on marketplace integrations now fire on specific data-change events instead of a single generic event type. Configure a Common Model and choose which changes start the workflow.

    **What's new:**

    * **Common Model selector** — pick the standard record type to listen for (for example, `Contact`, `Employee`, or `Ticket`). Available models depend on the provider's category
    * **Event types** — choose any combination of **Data Added**, **Data Changed**, and **Data Removed** to filter which changes trigger the workflow
    * Records pushed by the provider are normalized to the marketplace's common model schema, so the same trigger configuration works across providers in the same category

    **Who can use this:**\
    Available for any marketplace integration that supports webhooks. See [Marketplace → Webhook trigger](../../01-Developer-Guide/15-Integrations/03-Integrations-marketplace.md#webhook-trigger).

    ### Chatbot agents: per-environment configuration

    Chatbot text agents now support environment-specific configuration like other text agent channels. You can configure separate prompts, tools, and registered domains for production, staging, and development.

    **Who can use this:**\
    Available in the **Inbound Text Agent** node when **Channel** is set to **Chatbot**. See [Chatbot → Environments](../../01-Developer-Guide/06-Text-Agents/05-Chatbot.md#environments).
  </Update>

  <Update label="May 1, 2026">
    ### Runs page redesign

    The Runs page has been rebuilt with a new table, richer filtering, and saved views.

    **What's new:**

    * **Infinite scrolling** — older runs load automatically as you scroll; there is no longer a fixed page size or pagination control
    * **Column visibility and reordering** — click the column menu to show or hide any column, and drag column headers to rearrange them. Changes persist between sessions.
    * **Saved views** — save a combination of active filters and visible columns as a named view. Switch between views using the tab bar above the table. Right-click a view tab to rename, update, or delete it. Views are shared across your team.
    * **Advanced filtering** — filter conditions now support additional operators including `between` and `not between` for date and numeric columns, in addition to the existing equality, comparison, and pattern-matching operators
    * **New run details panel** — the right-side panel for inspecting a run has been redesigned with improved layouts for voice, text, email, and loop runs

    **Who can use this:**\
    Available for all workflows. See [Runs overview](../../01-Developer-Guide/09-Runs-and-Monitoring/01-Runs-Overview.md) for details.

    ### Call Workflow: marking response nodes

    A workflow node can now be explicitly marked as a **response node**, making it available for selection in the Call Workflow node's response selector.

    **What's new:**

    * Any action node in a workflow has a new **Response Node** section in its configuration panel
    * Enable **Mark this node as a response node** to expose it as a selectable response point in parent workflows that call this workflow
    * When the Call Workflow node's target is set dynamically (via a variable), use the **Workflow for Testing** picker to select a static workflow for schema and response node lookup during configuration

    **Who can use this:**\
    Available in the workflow editor for all V3 workflows using the [Call Workflow](../../01-Developer-Guide/03-Core-Nodes/12-Call-Workflow.md) node.
  </Update>

  <Update label="April 30, 2026">
    ### Twin MCP server

    A new `@happyrobot-ai/mcp-twin` package brings your organization's [Twin database](../../01-Developer-Guide/15-Integrations/06-Data-and-Storage/07-Twin-database.md) into AI coding assistants like Claude Code, Claude Desktop, Cursor, and VS Code Copilot.

    **What's new:**

    * Install the server with `npx @happyrobot-ai/mcp-twin` and authenticate with your HappyRobot API key
    * Explore your database with `get_schema` and `get_table_data`, and mutate rows with `insert_row`, `update_row`, and `delete_rows`
    * Manage schema with `create_table` and `drop_table`, or run arbitrary SQL (joins, aggregations, `ALTER TABLE`, migrations) via `execute_sql`
    * Configure the server interactively with the `setup` tool when no API key is set as an environment variable
    * SQL queries enforce a 5-second timeout; `SELECT` results are capped at 500 rows / 1 MB

    **Who can use this:**\
    Available for all organizations with a provisioned Twin database. See the [Twin MCP server](../../02-Developer-Tools/01-MCP/04-Twin-MCP.md) page for installation and configuration details.

    ### File attachments in the agent sandbox

    The OpenCode agent sidebar now accepts files via drag-and-drop, clipboard paste, or the file picker. You can attach screenshots, PDFs, CSVs, logs, or any other file — each upload lands in the sandbox workspace at `/workspace/app/.attachments/` so the agent can read it directly.

    **What's new:**

    * Drag any file onto the sidebar or paste from your clipboard to attach it
    * Attach up to 10 files per message, up to 25 MB each
    * Chip previews show upload progress and let you remove attachments before sending
    * Images are inlined as vision content so the agent can interpret them visually

    **Who can use this:**\
    Available for all organizations using the app sandbox (Apps feature).
  </Update>

  <Update label="April 29, 2026">
    ### Slack and Microsoft Teams text agents

    Dedicated conversational text agents for Slack and Microsoft Teams are now generally available. Both channels support inbound and outbound configurations and use the same prompt, tool, timeout, reminder, and escalation system as other text agent channels.

    **Slack agent:**

    * Install the HappyRobot Slack app once per workspace via OAuth — no per-channel setup
    * Inbound supports **Group Direct Messages** and **Channel Messages** (with optional channel scoping); the bot automatically replies in threads inside channels
    * Outbound supports **Direct Message**, **Group Direct Message**, and **Channel** destinations, with all fields templatable from variables
    * Backseat context tracking — the bot silently records messages sent without an @mention so it has full thread context the next time it's brought in
    * Thread history is fetched automatically when the bot is @mentioned mid-thread

    **Microsoft Teams agent:**

    * New bot-based architecture replaces the older Microsoft Graph subscription model — no 3-day renewals, no per-channel subscriptions, no encryption certificates
    * Inbound supports **Group Chats** and **Channel Messages** (with required team and channel selection for channel scoping)
    * Outbound supports **Personal Chat**, **Group Chat**, and **Channel** destinations; HappyRobot installs the bot for the recipient automatically when needed
    * Quote replies, reply-to-bot detection, and silent context tracking work the same way they do in Slack

    **Who can use this:**\
    Available for all organizations. See the [Slack text agent](../../01-Developer-Guide/06-Text-Agents/07-Slack.md) and [Microsoft Teams text agent](../../01-Developer-Guide/06-Text-Agents/06-Microsoft-Teams.md) pages for setup, configuration, and limitations. The Teams bot app package is provided by your account team for IT admin upload to the Teams Admin Center.

    ### AWS S3 integration

    A new AWS integration lets workflows generate presigned URLs for private S3 objects. Use it to give callers or downstream systems temporary access to recordings, documents, or any file stored in S3 — without exposing AWS credentials.

    **What's new:**

    * Connect with an IAM user access key (Access Key ID, Secret Access Key, Region)
    * Use the **S3 Get Presigned URL** action to generate a time-limited download link for any S3 object
    * Configure the bucket, object key, and expiration (default 1 hour, max 7 days) — all fields support variable templating
    * Outputs `presigned_url`, `expires_at`, `bucket`, and `key` for use in downstream nodes

    **Who can use this:**\
    Available for all organizations. See the [AWS integration](../../01-Developer-Guide/15-Integrations/06-Data-and-Storage/08-AWS.md) page for setup and configuration.

    ### MCP inspector

    The MCP Server integration now includes a built-in inspector for testing and debugging your connected MCP servers directly from the platform.

    **What's new:**

    * Click the **Inspect** button (search icon) on any server in the **Tools** tab to open the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) in a new browser tab
    * The inspector connects through a secure platform proxy, pre-authenticated — no additional credentials or local setup required
    * Send test requests to tools and inspect their inputs and outputs interactively

    **Who can use this:**\
    Available for all organizations with at least one connected MCP server. See [MCP Server Setup](../../01-Developer-Guide/04-Tools/06-MCP-Server-Setup.md#managing-servers) for details.
  </Update>

  <Update label="April 28, 2026">
    ### Voice descriptions

    All HappyRobot voices now have a short description visible in the **Voice Info** tab when you select a voice.

    **What's new:**

    * Each HappyRobot voice shows a description summarizing its character and tone (e.g., "Confident young male voice with a modern Spanish accent")
    * Descriptions help you quickly evaluate voices without listening to every preview

    **Who can use this:**\
    Available in **Assets → Voices** for all HappyRobot voices. The `description` field is also returned in the Voices API.
  </Update>

  <Update label="April 27, 2026">
    ### Audio audits: semantic phrase insights

    The audio audits analytics dashboard now includes a **Top Semantic Mismatches** panel when you select the **Semantic WER** metric in the Transcription section.

    **What's new:**

    * Ranked list of key phrases in your agent's vocabulary that are most frequently transcribed incorrectly
    * Each row shows the reference phrase, the most common incorrect transcription ("heard as"), error type classification, total error count, and share of overall key phrase errors
    * Summary stats highlight the most-impacted phrase and total error volume
    * Conversational filler words are automatically filtered out so only domain-relevant vocabulary appears

    **Who can use this:**\
    Available in the Audio Audits page for any workflow. Select the **Semantic WER** metric in the Transcription section to reveal the insights panel. See [Semantic phrase insights](../../01-Developer-Guide/11-Quality-and-Evaluation/04-Audio-audits.md#semantic-phrase-insights) for details.

    ### Email: drop quoted history from inbound emails

    Gmail and Outlook subscriptions now include an **Advanced** settings section with a new toggle to strip quoted reply history from inbound emails before they reach your workflow.

    **What's new:**

    * New **Drop quoted history from inbound emails** toggle in the **Advanced** accordion when creating or editing a Gmail or Outlook subscription
    * When enabled, only the sender's new content is kept — quoted prior messages from the thread are removed before processing
    * Reduces noise in email thread workflows where only the latest message matters

    **Who can use this:**\
    Available for all Gmail and Outlook subscriptions. See [Gmail](../../01-Developer-Guide/15-Integrations/04-Communication/01-Gmail.md#advanced-subscription-settings) and [Outlook](../../01-Developer-Guide/15-Integrations/04-Communication/02-Outlook.md#advanced-subscription-settings) for details.

    ### HappyRobot TTS v2 now generally available

    The **v2** model for HappyRobot text-to-speech voices is no longer in preview — it is now generally available.

    **What's new:**

    * The "preview" label has been removed from HappyRobot v2 TTS voices
    * v2 voices continue to show a **v2** model badge in the voice library; older v0 voices are labeled **v0 (deprecated)**
    * v2 voices now appear first in the voice selection dropdown for easier discovery
    * Hungarian (`hu-HU`) is now available as a TTS accent for HappyRobot voices, joining the existing set of supported languages

    **Who can use this:**\
    Available to all organizations. Browse v2 voices in **Assets → Voices**.
  </Update>

  <Update label="April 24, 2026">
    ### Signals API: key management endpoints

    The Signals public API now includes endpoints to manage signal keys — the named identifiers that link an external signal to a specific signal trigger node in your workflow.

    **What's new:**

    * **Add a signal key** — `POST /signals/keys` registers a key name for a signal trigger node. The key must match the pattern `a-z`, `0-9`, `-`, `_`, `.`, `*`, `#` (dot-separated segments), up to 256 characters. Keys starting with `usecase.` or `session.` are reserved.
    * **Delete a signal key** — `DELETE /signals/keys` removes a registered key from a node.
    * **List signal keys** — `GET /signals/keys` returns all keys registered for your organization.

    All signal key endpoints are authenticated with your API key and scoped to your organization. See the [API Reference](https://docs.happyrobot.ai/api-reference) for full endpoint documentation.

    **Who can use this:**\
    Available to all organizations using the Signals API.
  </Update>

  <Update label="April 22, 2026">
    ### Integrations marketplace

    HappyRobot now includes an integrations marketplace giving you access to hundreds of external services across CRM, HRIS, ATS, Accounting, Ticketing, and File Storage — all through a single connection flow.

    **What's new:**

    * Browse and search integrations from a new marketplace view in **Settings > Integrations**, with curated collections (Featured, New Arrivals, Most Popular, Enterprise) and category filters
    * Connect any provider using a guided OAuth flow — no raw API keys or credentials required on your side
    * Use connected integrations as action nodes in the workflow editor with standard events: **Get**, **List**, **Create**, **Update**, **Passthrough**, **Download**, and **Trigger**
    * Featured providers include HubSpot, Workday, ServiceNow, NetSuite, Greenhouse, BambooHR, Jira, and many more

    **Who can use this:**\
    Available for all organizations. See [Integrations marketplace](../../01-Developer-Guide/15-Integrations/03-Integrations-marketplace.md) for setup and usage details.

    ### Frontal AI assistant (beta)

    Frontal, the AI assistant for the workflow editor, is now available to all organizations.

    **What's new:**

    * Open Frontal from within any workflow to ask questions, get recommendations, and apply edits through conversation
    * **Plan mode** — propose and review a full plan before any changes are applied; bigger changes surface as a reviewable plan card you can accept or reject
    * **Build mode** — apply edits directly, one operation at a time
    * Ask Frontal to rewrite prompts, swap models, add or remove nodes, merge branches, and more — every edit is reviewable in the editor
    * Frontal reads your workflow structure and can answer questions about node configuration without making changes
    * Close the panel and come back later — long-running tasks continue in the background and resume when you return

    **Who can use this:**\
    Available for all organizations in the workflow editor. See [Frontal AI assistant](../../01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md) for details.

    ### Per-version workflow engine

    Each workflow version now independently tracks which engine (v2 or v3) it runs on. You can upgrade individual versions to v3 without touching other versions in the same workflow — no big-bang migration required.

    **What's new:**

    * **Per-version control** — each version carries its own engine setting; mix v2 and v3 versions within the same workflow freely
    * **Fork inheritance** — forking a v3 version creates a v3 draft; forking a v2 version creates a v2 draft
    * **Auto-loop conversion** — when upgrading a version to v3, parallel and sequential action groups are automatically converted to explicit loop nodes
    * **Downgrade support** — unpublish a v3 version and click **Downgrade** to revert it to v2 without affecting other versions

    The workflow editor shows a banner when you open a draft that can be upgraded, and walks you through the process step by step.

    **Who can use this:**\
    Available for all workflows. See [Versions and Publishing](../../01-Developer-Guide/02-Workflows/08-Versions-and-Publishing.md#workflow-engine-version-v2-and-v3) for details.

    ### Per-voice gain and speed for static voices

    In V3 voice agents, each statically selected voice can now carry its own **gain** and **speed** settings, in addition to the existing per-voice agent name.

    **What's new:**

    * Set per-voice gain (0.5–1.5) and speed (0.7–1.2) from the voice settings panel — click the settings icon next to any voice after adding it
    * When all selected voices have explicit per-voice settings, the top-level gain and speed controls are hidden automatically
    * Speed is available for ElevenLabs and Cartesia voices; gain is available for all providers

    **Who can use this:**\
    Available for V3 voice agents. See [STT, TTS, and LLM configuration](../../01-Developer-Guide/05-Voice-Agents/05-STT-TTS-and-LLM-Configuration.md#per-voice-settings-v3) for details.
  </Update>

  <Update label="April 20, 2026">
    ### OAuth 2.0 authentication for MCP servers

    MCP servers can now authenticate using an OAuth 2.0 client credentials flow instead of a static token.

    **What's new:**

    * Select **OAuth 2.0** as the auth type when configuring an MCP server connection
    * Link any **OAuth 2.0 → API Client** credential from your organization — HappyRobot fetches a short-lived access token at connection time and sends it as a `Bearer` token
    * Configure separate OAuth 2.0 credentials for Staging and Development environments, just like static tokens
    * The `auth_type: "oauth2"` option and `oauth2_credential_id` field are available in the public API and the `manage_mcp_servers` tool in the HappyRobot MCP developer server

    **Who can use this:**\
    Available for all MCP server integrations. Requires an existing OAuth 2.0 → API Client credential. See [MCP Server Setup](../../01-Developer-Guide/04-Tools/06-MCP-Server-Setup.md) for configuration details.

    ### EU cluster support in the TypeScript SDK

    The `@happyrobot-ai/sdk` package now accepts a `cluster` option to route API requests to the EU region.

    **What's new:**

    * Pass `cluster: "eu"` when initializing `HappyRobotClient` or `HappyRobotChatClient` to connect to `https://platform.eu.happyrobot.ai/api/v2`
    * Defaults to `"us"` — no change required for existing US-region users
    * The `CLUSTER_URLS` map is exported from the SDK for use in custom configurations

    **Who can use this:**\
    Available in `@happyrobot-ai/sdk`. See [TypeScript SDK](../../02-Developer-Tools/02-TypeScript-SDK/01-TypeScript-SDK.md) for configuration details.
  </Update>

  <Update label="April 17, 2026">
    ### Call Workflow node

    You can now invoke another workflow directly from within a workflow and capture its response as a node output.

    **What's new:**

    * Add a **Call Workflow** node from the node picker in the workflow editor
    * Select any workflow in your organization as the target, and choose which of its response nodes to capture
    * Optionally pin the child to a specific version and environment, or inherit the calling workflow's environment
    * Pass a data payload to the child workflow at invocation time using the builder or raw JSON mode
    * Set a timeout so the parent can continue if the child does not respond in time
    * The child workflow's response is available as node output for downstream references in the parent

    **Who can use this:**\
    Available for all workflows in the workflow editor. See [Call Workflow](../../01-Developer-Guide/03-Core-Nodes/12-Call-Workflow.md) for configuration details.

    ### Per-voice agent name

    Each voice selected for a V3 voice agent can now carry its own agent name.

    **What's new:**

    * Set a **per-voice agent name** in the voice settings panel — when a voice is randomly assigned to a call, the agent introduces itself using the name tied to that voice
    * When using a dynamic voice (variable-driven), configure optional **name**, **gain**, and **speed** overrides in the inline fields below the variable input
    * When every selected voice has a per-voice name set, the legacy top-level agent name field is hidden automatically

    **Who can use this:**\
    Available for V3 voice agents. See [STT, TTS, and LLM configuration](../../01-Developer-Guide/05-Voice-Agents/05-STT-TTS-and-LLM-Configuration.md#per-voice-settings-v3) for details.
  </Update>

  <Update label="April 15, 2026">
    ### New models: GPT-5.4 family, o4-mini, Gemini 3.1, and Claude 4.6

    Several new language models are now available across all agent types.

    **New models:**

    * **gpt-5.4** (\~1100ms) — Most capable GPT model. Best for agentic, coding, and professional workflows.
    * **gpt-5.4-mini** (\~600ms) — Near gpt-5.4 quality at lower cost and latency.
    * **gpt-5.4-nano** (\~400ms) — Cheapest GPT-5.4-class model for simple high-volume tasks.
    * **o4-mini** (\~900ms) — Best reasoning model per dollar. Ideal for complex multi-step tool calling.
    * **gemini-3.1-pro-low / gemini-3.1-pro-high** — Google's most intelligent model with advanced reasoning (low and high thinking). Replaces the deprecated gemini-3-pro variants.
    * **gemini-3.1-flash-lite** (\~300ms) — Ultra-fast and cheap Gemini model, 45% faster than Gemini 2.5 Flash.
    * **claude-sonnet-4.6** (\~500ms) — Best combination of Claude speed and intelligence.
    * **claude-opus-4.6** (\~1200ms) — Most intelligent Claude model, for complex reasoning and agent tasks.

    **Also:**

    * **Claude models are now available for all agent types** (voice and text). Previously, Claude models were restricted to text agents.
    * **Kimi K2 is deprecated.** Existing workflows using kimi-k2 will continue to work but the model is no longer recommended.

    **Who can use this:**\
    All models are available in the model selector of any prompt node. See [STT, TTS, and LLM configuration](../../01-Developer-Guide/05-Voice-Agents/05-STT-TTS-and-LLM-Configuration.md#choosing-a-model) for the full model reference.

    ### Bulk invite team members

    You can now invite multiple team members at once from **Settings > Members**.

    **What's new:**

    * Paste a comma- or newline-separated list of email addresses into the invite panel
    * The panel validates each address in real time — flagging invalid formats, existing members, and already-invited addresses
    * All valid addresses receive invitations in a single action; addresses with issues are skipped and displayed in the review list
    * A summary shows how many invitations will be sent before you confirm

    **Who can use this:**\
    Available to all organization Owners. See [Team Members and Roles](../../01-Developer-Guide/16-Account-and-Settings/02-Members-and-Access.md#inviting-members) for details.

    ### Signals API

    The signals API is now available in the public REST API, allowing you to trigger and schedule signals programmatically from external systems.

    **What's new:**

    * **Publish a signal** — send an immediate signal to a workflow with a key and payload
    * **Schedule a signal** — deliver a signal after a configurable delay (in seconds)
    * **Update a scheduled signal** — change the key, payload, or delay of a pending signal before it fires
    * **Cancel a scheduled signal** — remove a scheduled signal before it is delivered
    * **List signal keys** — retrieve available signal key patterns for a workflow

    All endpoints are authenticated with your API key and scoped to your organization. See the [API Reference](https://docs.happyrobot.ai/api-reference) for full endpoint documentation.
  </Update>

  <Update label="April 14, 2026">
    ### Experiments now in beta for all users

    The Experiments feature is now available to all organizations as a public beta. It was previously restricted to internal users.

    **What's new:**

    * All users can now access **Experiments** in the workflow editor under the **Experiments** tab (marked **Beta**)
    * Redesigned empty state with feature cards explaining key capabilities and a link to the docs
    * A/B test workflow versions and configuration changes — split traffic between a control and treatment variant, define custom metrics, and monitor results with daily estimates and confidence indicators

    **Who can use this:**\
    Available to all users on V3 workflows. Find it in the workflow editor under the **Experiments** tab. See [Experiments](../../01-Developer-Guide/10-Experiments/01-Experiments.md) to get started.
  </Update>

  <Update label="April 13, 2026">
    ### Twin: filters with operators and order by

    The **Read from Twin** node now supports richer query configuration — filter rows using comparison operators and sort results by any column.

    **What's new:**

    * **Filter operators** — Each filter condition now includes an operator field. Available operators depend on the column type:
      * Text columns: Equals, Not equal, Contains
      * Numeric and timestamp columns: Equals, Not equal, Greater than, Less than, Greater or equal, Less or equal
      * UUID and boolean columns: Equals, Not equal
    * **Order by** — Sort query results by any column, ascending or descending. A single sort column is supported per query.
    * Filters and ordering support dynamic values (workflow variables)

    **Who can use this:**\
    Available for all Twin Read nodes in the workflow editor. See [Twin database](../../01-Developer-Guide/15-Integrations/06-Data-and-Storage/07-Twin-database.md#read-from-twin) for configuration details.

    ### Twin: edit dump column mappings

    The Twin Dump configuration (which automatically persists workflow run data to a Twin table) can now be edited after creation.

    **What's new:**

    * Open any existing dump configuration in the Twin workspace and click **Edit mappings**
    * Update which workflow variable maps to each table column without recreating the dump from scratch
    * Workflow runtime variables (`__run_id__`, `__completed_at__`) are available alongside all node outputs

    **Who can use this:**\
    Available in the Twin workspace for all organizations with a provisioned Twin database. See [Twin database](../../01-Developer-Guide/15-Integrations/06-Data-and-Storage/07-Twin-database.md#twin-dump) for details.
  </Update>

  <Update label="April 12, 2026">
    ### Custom LLM server for voice agents

    Voice agents can now route LLM traffic to your own OpenAI-compatible endpoint instead of the built-in models.

    **What's new:**

    * New **Use Custom LLM** toggle in the prompt node configuration for voice agents
    * Add a **Custom LLM Server** credential under **Integrations** with your endpoint URL and API key
    * HappyRobot still manages voice orchestration and built-in tools (hangup, transfer) — only LLM calls are forwarded
    * The model, system prompt, and tool definitions from your workflow are passed through to your endpoint

    **Who can use this:**\
    Available for all voice agents (inbound and outbound). See [STT, TTS, and LLM configuration](../../01-Developer-Guide/05-Voice-Agents/05-STT-TTS-and-LLM-Configuration.md#custom-llm-server) for setup instructions.

    ### OCR Deep Extract

    The OCR Extract node (Advanced mode) now includes a **Deep Extract** option for near-perfect accuracy on complex documents.

    **What's new:**

    * **Deep Extract** toggle in the advanced options of the OCR Extract node (Reducto provider)
    * Uses agentic extraction with iterative verification — best for complex or multi-column documents
    * Higher credit usage than standard Advanced mode

    **Who can use this:**\
    Available in any workflow using the OCR Extract node with Advanced mode (Reducto). See [File Operations](../../01-Developer-Guide/03-Core-Nodes/08-File-Operations.md#ocr-extract) for details.

    ### Run node outputs API and `triggerAndWaitForNodeOutput` SDK helper

    New API endpoints and an SDK helper let you fetch node-level output data from a run and synchronously wait for a specific node to complete.

    **What's new:**

    * **`GET /runs/:run_id/nodes`** — List node executions for a run, optionally filtered by `node_persistent_id`
    * **`GET /runs/:run_id/outputs/:output_id`** — Fetch the full output payload for a specific node execution
    * **`triggerAndWaitForNodeOutput()`** SDK helper triggers a workflow and polls until a named node produces output, then returns the payload — without waiting for the entire run to finish
    * **MCP**: `monitor_runs` tool now supports an `outputs` action to inspect node execution records and fetch output payloads from your AI coding assistant

    **Who can use this:**\
    Available in SDK v0.1.10 and later via `@happyrobot-ai/sdk/helpers`. Requires V3 workflows. See [SDK helpers](../../02-Developer-Tools/02-TypeScript-SDK/12-Helpers.md#triggerAndWaitForNodeOutput) and [SDK workflows](../../02-Developer-Tools/02-TypeScript-SDK/06-Workflows.md#runs) for full reference.
  </Update>

  <Update label="April 10, 2026">
    ### MCP: manage knowledge bases

    The HappyRobot MCP server now includes a `manage_knowledge_bases` tool for full knowledge base lifecycle management directly from AI coding assistants like Claude Code, Cursor, and VS Code Copilot.

    **What's new:**

    * **`manage_knowledge_bases`** replaces the previous `list_knowledge_bases` tool with seven actions: `list`, `create`, `delete`, `list_files`, `upload_files`, `trigger_chunking`, and `delete_file`
    * Upload documents to a knowledge base by getting presigned S3 URLs, uploading file content, then triggering processing — all without leaving your editor
    * Files are ready for RAG search in voice and text agents approximately 10–15 minutes after chunking is triggered
    * The `create` action also maps to a new `POST /knowledge-bases` endpoint in the public API

    **Who can use this:**\
    Available in `@happyrobot-ai/mcp` v0.1.10 and later. See the [MCP server docs](../../02-Developer-Tools/01-MCP/01-MCP-servers.md#available-tools) for the full action reference.

    ### Transfer Caller ID setting

    The phone number settings dialog now clearly labels the caller ID option as **Transfer Caller ID** and explains exactly what it controls.

    **What's new:**

    * The setting is renamed from **Caller ID** to **Transfer Caller ID** for clarity
    * Description now specifies: controls what number a human agent sees on their phone when a call is **directly transferred** to them
    * Includes an explicit note that warm and whisper transfers are not affected by this setting

    **Who can use this:**\
    Available for all Twilio phone numbers under **Assets → Telephony**. See the [telephony docs](../../01-Developer-Guide/14-Assets/03-Telephony.md#phone-number-settings) for details.

    ### Experiments: duplicate and filter

    Two improvements make experiments easier to manage in the workflow editor.

    **What's new:**

    * **Duplicate experiment** — Open any active or completed experiment, click the actions menu (**…**), and select **Duplicate** to create a new draft experiment pre-populated with the same variants, metrics, and configuration overrides. Useful for iterating on past experiments without reconfiguring from scratch.
    * **Experiment filter on runs page** — The Runs tab now includes an experiment filter so you can narrow results to runs associated with a specific experiment.

    **Who can use this:**\
    Available for all workflows with experiments. Find experiments in the workflow editor under the **Experiments** tab.
  </Update>

  <Update label="April 9, 2026">
    ### Branch merges in workflows (V3)

    Path branches can now be merged back into a shared continuation node in V3 workflows. Previously, parallel branches created by a Paths node had to remain independent — now they can converge after completing their individual steps.

    **What's new:**

    * Connect the terminal node of one branch to any node in another branch to create a merge anchor
    * The workflow continues from the merge anchor once both branches reach it
    * The Frontal AI assistant can create and remove branch merges on your behalf

    **Who can use this:**\
    Available on workflows using the V3 engine. Upgrade from V2 by hovering the engine badge in the top-left corner of the workflow editor. See [branch merges](../../01-Developer-Guide/03-Core-Nodes/09-Conditionals.md#branch-merges-v3-only).

    ### Text agent media processing available on all channels

    Media processing (OCR and audio transcription) is now available for all text agent channels, not just chatbot. Configure document and audio attachment handling for SMS, WhatsApp, email, Teams, and chatbot agents.

    **What's new:**

    * **Document processing (OCR)** — standard tier (Gemini) or advanced tier (Reducto)
    * **Audio transcription** — standard tier (Whisper) or advanced tier (Soniox)
    * Available for both inbound and outbound text agents

    **Who can use this:**\
    Available in the agent node configuration for all text agent channels. See [media processing](../../01-Developer-Guide/06-Text-Agents/01-Text-Agents-Overview.md#media-processing).

    ### New language support: Urdu, Bengali, Slovenian

    Three additional languages are now available for voice agent speech recognition and TTS:

    * Urdu (`ur-PK`)
    * Bengali (`bn-BD`)
    * Slovenian (`sl-SI`)

    **Who can use this:**\
    Available in the STT language selector and when browsing ElevenLabs voices in **Assets → Voices**. See [supported languages](../../01-Developer-Guide/05-Voice-Agents/05-STT-TTS-and-LLM-Configuration.md#languages).

    ### Webhooks: dynamic OAuth2 credentials

    The OAuth2 authentication option in webhook nodes now supports dynamic credentials. You can reference a variable to select the OAuth2 credential at runtime instead of hardcoding a static selection.

    **Who can use this:**\
    Available in the Webhook node's authentication settings. Type `@` in the OAuth2 credential field to reference a variable.
  </Update>

  <Update label="April 7, 2026">
    ### MCP server: per-environment configuration

    MCP server connections now support separate credentials for Production, Staging, and Development environments.

    **What's new:**

    * The MCP server credential form now has three tabs: **Production**, **Staging**, and **Development**
    * Each environment has its own server URL and auth token fields
    * Staging and Development fields are optional — if left blank, they fall back to the Production values
    * When testing a Staging or Development connection, the platform compares the discovered tools against Production and highlights any mismatches (missing or extra tools)
    * The API `CreateMCPServer` and response schemas now include `staging_server_url`, `staging_auth_token`, `development_server_url`, and `development_auth_token` fields

    **Why this matters:**\
    Previously, a single MCP server credential used the same URL and token across all environments. With per-environment configuration, you can point staging workflows at a staging MCP server and development workflows at a local server, while keeping Production isolated.

    **Who can use this:**\
    Available for all MCP server integrations. Update credentials under **Integrations → MCP Server**. See [MCP Server Setup](../../01-Developer-Guide/04-Tools/06-MCP-Server-Setup.md#per-environment-configuration) for details.
  </Update>

  <Update label="April 4, 2026">
    ### Twin database: CSV import

    You can now import data into a Twin table directly from a CSV file using a new import panel in the Twin workspace.

    **What's new:**

    * Drag-and-drop CSV upload with a header validation step and row preview
    * Real-time progress bar during import with a completion summary showing row counts and any errors
    * New API endpoint: `POST /twin/tables/{tableName}/rows/bulk` for programmatic bulk inserts (up to 500 rows per request)

    **Who can use this:**\
    Available in the Twin workspace for all organizations with a provisioned Twin database. See [Twin database](../../01-Developer-Guide/15-Integrations/06-Data-and-Storage/07-Twin-database.md#import-data-via-csv).

    ### Northstars: copy from another version

    Northstars can now be copied from one workflow version to another, so you don't have to recreate evaluation criteria by hand when working across versions.

    **What's new:**

    * A **Copy from version** option appears in the row action menu for each northstar
    * Select a source version, click **Copy & Replace**, and all northstars for that prompt node in the current version are replaced with the source version's northstars

    **Who can use this:**\
    Available in the **Evaluate** tab for any workflow with multiple versions. See [Northstars](../../01-Developer-Guide/11-Quality-and-Evaluation/02-Northstars.md#copying-northstars-from-another-version).

    ### Custom tests: auto-generated test suites

    When you create a new test suite, HappyRobot now automatically generates an initial set of test cases based on your prompt node's instructions.

    **What's new:**

    * Tests are generated immediately after suite creation — no manual setup required to get started
    * A "Generating tests..." notification confirms the generation is in progress
    * Generated tests can be edited, deleted, or supplemented with additional cases

    **Who can use this:**\
    Available when creating a new test suite in the **Custom Evals** subtab of the workflow editor. See [Custom tests](../../01-Developer-Guide/11-Quality-and-Evaluation/06-Custom-tests.md).
  </Update>

  <Update label="April 2, 2026">
    ### Teams inbound: team and channel selection for channel messages

    Inbound Teams text agents now let you scope which channels the agent monitors when **Channel Messages** is selected as a message type.

    **What's new:**

    * After selecting **Channel Messages**, two new required pickers appear: **Teams** and **Channels**
    * Select one or more Teams workspaces to monitor, then select specific channels within each workspace
    * Channels are grouped by workspace in the picker. Leaving channels empty for a workspace monitors all accessible channels in that workspace
    * Existing channel selections are preserved if you toggle message types

    **Who can use this:**\
    Available for all inbound Teams text agents. See [Microsoft Teams](../../01-Developer-Guide/06-Text-Agents/06-Microsoft-Teams.md#select-teams-and-channels-channel-messages-only).

    ### Failure handling for integration nodes

    External integration action nodes now include a **Failure Handling** section in the node sidebar.

    **What's new:**

    * Toggle **Continue on failure** to let the workflow proceed even if a node fails
    * When enabled, the run is not marked as failed and execution continues to the next node
    * Node output variables are empty when the node fails in continue mode
    * Applies to all integration action nodes (Salesforce, Google Sheets, Slack, TMS integrations, etc.)
    * Not available for AI agents, webhooks, code nodes, conditionals, or built-in nodes
    * Useful for non-critical steps like logging or notifications that should not block the main workflow

    **Who can use this:**\
    Available on all integration action nodes in the workflow editor. See [Node types — Failure handling](../../01-Developer-Guide/02-Workflows/04-Node-Types.md#failure-handling).

    ### Custom eval: judge model selection

    Custom tests now let you choose which LLM model acts as the judge when evaluating agent responses.

    **What's new:**

    * A **Judge Model** dropdown appears in the evaluation criteria panel when **Custom** mode is selected
    * The selected model evaluates the agent's response against your criteria and returns a pass/fail result with reasoning

    **Who can use this:**\
    Available in the **Evaluate > Custom Evals** tab of any workflow. See [Custom tests — Judge model](../../01-Developer-Guide/11-Quality-and-Evaluation/06-Custom-tests.md#judge-model).
  </Update>

  <Update label="March 30, 2026">
    ### API file upload trigger

    A new **API File Upload** trigger lets external systems start a workflow by posting a file via `multipart/form-data`.

    **What's new:**

    * New trigger type in the workflow editor: **API File Upload**
    * Posts to an auto-generated endpoint URL (available per environment: production, staging, development)
    * Send the file as a `file` form field; any additional form fields are passed as workflow variables
    * Supports API key authentication and enhanced security (OAuth2/HMAC), consistent with the Webhook trigger

    **Who can use this:**\
    Available to all workflows. See [API file upload](../../01-Developer-Guide/02-Workflows/05-Triggers.md#api-file-upload) for the request format.

    ### MCP tool calls: custom headers

    The MCP Call action node now supports configuring custom HTTP headers sent with every tool call.

    **What's new:**

    * New **Custom Headers** section in the MCP Call node configuration
    * Define key-value pairs; both keys and values support variable templating (type `@` to insert workflow variables)
    * Useful for forwarding authentication tokens, tenant IDs, or other per-request metadata to your MCP server

    **Who can use this:**\
    Available for all MCP tool nodes in the workflow editor. See [MCP tools](../../01-Developer-Guide/04-Tools/05-MCP-Tools.md#custom-headers) for details.

    ### Workflow navigation: sidebar replaced by breadcrumb switcher

    The left-hand workflow sidebar has been removed. Switch between workflows using the **breadcrumb** at the top of the workflow editor.

    **What's new:**

    * Click the workflow name in the breadcrumb to open a searchable folder/tree view of all your workflows
    * Keyboard shortcut: **Ctrl+U** (Windows/Linux) or **⌃U** (Mac)
    * A one-time dialog explains the change the first time you open a workflow after the update

    **Why this matters:**\
    The breadcrumb switcher supports folder navigation, making it easier to find workflows in large organizations without the sidebar taking up permanent screen space.

    **Who can use this:**\
    Available to all users.

    ### Loops: list indicator for parallel loop variables

    When referencing outputs from a parallel loop in a downstream node, the variable picker now indicates that the variable resolves to a list.

    **What's new:**

    * A blue `[]` suffix appears next to variable names that come from a parallel loop
    * Hovering shows a tooltip: "Resolves to a list (parallel loop)"
    * Variable group headers from parallel loops show a blue **List** badge

    **Who can use this:**\
    Available in the workflow editor variable picker for all workflows using loop nodes with parallel execution enabled. See [loop nodes](../../01-Developer-Guide/03-Core-Nodes/10-Loops.md#variables-from-parallel-loops) for details.
  </Update>

  <Update label="March 29, 2026">
    ### Richpanel escalation for text agents

    Text agents can now escalate conversations to [Richpanel](https://richpanel.com), a helpdesk platform for customer support teams.

    **What's new:**

    * New **Richpanel** option in the escalation mode selector on inbound and outbound text agent nodes
    * Configure a Richpanel credential (API key + optional webhook secret) under **Settings → Integrations**
    * When the agent escalates, HappyRobot hands off the conversation to your Richpanel support queue

    **Who can use this:**\
    Available for all text agent channels (SMS, WhatsApp, email, chatbot). Enable the Richpanel integration under **Settings → Integrations** and configure a credential before use. See [Richpanel](../../01-Developer-Guide/15-Integrations/05-Business-Systems/09-Richpanel.md) for setup instructions.

    ### Eval runs: credit usage display

    Credit usage is now shown directly on eval run history pages. A tooltip on each run entry shows the credits consumed by that run.

    **Who can use this:**\
    Available on the adversarial suite run history and custom eval run history pages under the Quality section.
  </Update>

  <Update label="March 25, 2026">
    ### Warm handoff: custom intro audio

    The Direct Transfer node now supports custom audio for the warm handoff intro — the clip played to the receiving agent before they are connected to the caller.

    **What's new:**

    * Set **Intro mode** to **Custom** in the warm handoff settings of a Direct Transfer node
    * Select any audio asset from your library as the intro clip
    * The default behavior (built-in intro audio) is unchanged unless you opt into custom mode

    **Who can use this:**\
    Available for all workflows using the Direct Transfer node with warm handoff enabled. Upload audio assets in **Assets → Telephony → Audio Library**. See [warm handoff intro audio](../../01-Developer-Guide/14-Assets/03-Telephony.md#warm-handoff-intro-audio).

    ### Time variables in workflows

    A new built-in `time` variable group is available in all workflows. Variables like `time.now_utc` and `time.now_america_new_york` resolve to the current timestamp in 15 common timezones at the moment the workflow runs.

    **What's new:**

    * 15 timezone-specific time variables available without any configuration
    * Reference them with `@time.now_<timezone>` in the workflow editor
    * Useful for giving AI agents awareness of the current time, or for time-based conditional logic

    **Who can use this:**\
    Available to all workflows. See [time variables](../../01-Developer-Guide/02-Workflows/07-Variables.md#time-variables).

    ### Runs: comparison operators for numeric and duration filters

    Custom column filters on the Runs page now support comparison operators for numeric and duration values.

    **What's new:**

    * Filter numeric and duration columns with `=`, `≠`, `>`, `≥`, `<`, and `≤` operators
    * Numeric filter input values are preserved when switching between operators

    **Who can use this:**\
    Available on the Runs page for any workflow with custom columns. Open the filter popover for a numeric or duration column to see the new operators.

    ### Chat token: pass trigger variables

    The `POST /chat/tokens` endpoint (and `client.chat.createToken()` in the SDK) now accepts an optional `data` field for forwarding trigger variables when a chat session starts.

    **What's new:**

    * Pass `data: Record<string, unknown>` to `createToken()` to inject variables into the session at startup
    * The `data` is embedded in the token and forwarded to the workflow as trigger variables when the first message arrives

    **Who can use this:**\
    Available via the REST API and the `@happyrobot-ai/sdk` package. See the [chatbot tutorial](../../02-Developer-Tools/02-TypeScript-SDK/05-Chatbot-tutorial.md#pass-data-to-the-agent).
  </Update>

  <Update label="March 22, 2026">
    ### Chatbot trigger: custom payload params

    Chatbot workflows can now declare named **params** on the trigger node, allowing your website to pass structured data into the workflow when a visitor starts a conversation.

    **What's new:**

    * Define param names (for example, `user_id`, `page_url`) on the **Inbound Text** trigger node
    * Set `window.HappyRobotConfig = { payload: { ... } }` in your embed code to pass values at session start
    * Params are available as workflow variables in downstream nodes
    * The workflow editor preview shows a pre-filled payload textarea for testing declared params
    * A copyable JSON schema is shown in the trigger panel for integration reference

    **Why this matters:**\
    Previously, chatbot sessions had no way to receive context from the embedding page. With params, you can pass account IDs, product context, or any other page-level data into the workflow without requiring the visitor to type it.

    **Who can use this:**\
    Available for all chatbot workflows. See the [Chatbot docs](../../01-Developer-Guide/06-Text-Agents/05-Chatbot.md#passing-custom-data-to-the-chatbot-params) for the embed code pattern.

    ### Loop node: output schema generation

    Loop nodes now support output schema generation via the Testing Drawer.

    **What's new:**

    * **Generate Output Schema** button in the Loop node configure panel footer
    * Clicking it opens the Testing Drawer (the same tool used by action nodes), where you can run the loop with sample data to capture its output structure
    * Once generated, downstream nodes can reference loop output variables using the `@` picker

    **Who can use this:**\
    Available in the workflow editor for all loop nodes. The button is enabled once the loop node is fully configured.

    ### Compliance bundle rename

    Compliance bundles can now be renamed directly from the compliance table.

    **What's new:**

    * New **Rename** option in the row action menu (ellipsis **…**) on the Compliance tab of the Telephony page
    * No need to navigate to the bundle's settings page to update its name

    **Who can use this:**\
    Available to all organizations with compliance bundles configured. Find it under **Assets → Telephony → Compliance**.
  </Update>

  <Update label="March 20, 2026">
    ### Time variables

    Variables now come in two types: **custom** (static key-value pairs) and **time** (dynamic date/time values resolved at runtime).

    **What's new:**

    * New **Time Variables** tab on the **Settings > Variables** page (and **Workflow Settings > Variables**)
    * Time variables are configured with a key name, an IANA timezone, and a format string (e.g., `yyyy-MM-dd`, `h:mm a`)
    * At runtime, a time variable resolves to the current date/time formatted according to your settings — always fresh, always timezone-correct
    * Time variables appear in the `@` variable picker under **Workflow Time Variables** or **Organization Time Variables** depending on their scope

    **Why this matters:**\
    Previously, injecting the current date or time into a workflow required custom code or external tooling. Time variables let you reference dynamic date/time values anywhere in a workflow — prompts, conditions, webhook bodies — without writing code.

    **Who can use this:**\
    Available to all users. Manage time variables under **Settings > Variables > Time Variables** or **Workflow Settings > Variables > Time Variables**. See [environment variables](../../01-Developer-Guide/16-Account-and-Settings/08-Environment-Variables.md#time-variables) for details.

    ### Loop node output schemas

    Loop nodes can now generate a typed output schema, making loop outputs available in the `@` variable picker for downstream nodes.

    **What's new:**

    * New **Generate Output Schema** button in the loop node configuration panel
    * Click it to open the testing drawer, run a test, and derive a schema from the output
    * Once generated, loop output variables appear in the variable picker with full type information — the same as any other node
    * The button changes to **View Output Schema** once a schema exists; regenerate it any time by running another test

    **Why this matters:**\
    Previously, loop nodes couldn't expose their outputs to downstream nodes. With a generated schema, any node after the loop can reference loop output variables directly using `@`.

    **Who can use this:**\
    Available for all loop nodes. Click the loop node in the workflow editor and use the **Generate Output Schema** button. See [loop node docs](../../01-Developer-Guide/03-Core-Nodes/10-Loops.md#output-schema) for details.
  </Update>

  <Update label="March 18, 2026">
    ### Artifacts: on-demand presigned URL resolution

    Session message artifacts no longer embed presigned download URLs directly. Instead, a new `POST /artifacts/resolve` endpoint resolves presigned URLs on demand.

    **What's new:**

    * New **`POST /artifacts/resolve`** endpoint accepts up to 500 `s3_keys` and an optional `expires_in` duration (60–604800 seconds) and returns a fresh presigned download URL for each key
    * `GET /sessions/:session_id/messages` now returns only `s3_key` and `status` on artifact objects — no embedded URLs

    **Why this matters:**\
    Presigned URLs embedded in message responses expired after a fixed window, causing broken downloads when responses were cached or replayed. Fetching URLs on demand means they're always fresh and you control the expiry window.

    **Migration required:**\
    If your integration reads artifact URLs from `getMessages()`, update it to call `artifacts.resolve()` with the `s3_key` values instead. See the [sessions and messages SDK reference](../../02-Developer-Tools/02-TypeScript-SDK/07-Sessions-and-messages.md#artifacts) for details.

    ### Twin: SQL editor and capacity configuration

    The **Twin Database** settings page now includes a built-in SQL editor and capacity management controls.

    **What's new:**

    * **SQL editor** — Run SQL queries directly against your Twin database from the settings page. Useful for schema inspection, ad-hoc queries, and debugging without an external database client
    * **Capacity configuration** — Adjust the RDS instance class and allocated storage from the settings UI
    * **RDS status** — The database status card now shows instance class, storage allocation, current database size, storage usage percentage, and any pending modifications
    * **Row update API** — New `PATCH /twin/tables/:tableName/rows` endpoint updates a single row by primary key map

    **Why this matters:**\
    The SQL editor reduces the friction of exploring and validating your data schema without leaving the platform. Capacity controls let you right-size the database as your data volume grows.

    **Who can use this:**\
    Available to all organizations with a Twin database provisioned. Find the new panels in **Settings → Twin Database**. See the [Twin integration docs](../../01-Developer-Guide/15-Integrations/06-Data-and-Storage/07-Twin-database.md) for details.
  </Update>

  <Update label="March 17, 2026">
    ### WhatsApp: end session on delivery error

    WhatsApp inbound and outbound text agents now have an **End session on delivery error** toggle.

    **What's new:**

    * When enabled, the session ends immediately if WhatsApp reports a message delivery failure
    * Error details are surfaced as node output variables so downstream nodes can inspect and respond — for example, to log the error, notify a human, or retry via a different channel
    * When disabled (default), delivery errors are ignored and the conversation continues

    **Why this matters:**\
    Delivery failures are now actionable within the workflow. Rather than silently continuing after a failed message, you can branch on the error and handle it explicitly.

    **Who can use this:**\
    Available for all WhatsApp inbound and outbound text agent nodes. Find the toggle in the recipient configuration section of the WhatsApp agent setup. See [WhatsApp docs](../../01-Developer-Guide/06-Text-Agents/03-WhatsApp.md#delivery-error-handling).

    ### SMS agent workflow template (API)

    The `POST /workflows` API endpoint now supports `"sms-agent"` as a `from_template` value, joining the existing `voice-agent`, `inbound-voice-agent`, `whatsapp-agent`, `email-agent`, and `chatbot-agent` templates.

    **What's new:**

    * `POST /workflows` with `from_template: "sms-agent"` creates a pre-configured outbound SMS agent workflow with a webhook trigger, Twilio SMS credentials, and webhook routing already wired up
    * Accepts optional `agent_name` and `prompt` inputs to customize the generated workflow

    **Why this matters:**\
    Programmatically bootstrapping SMS agent workflows is now as simple as the other agent types — no manual node configuration required.

    **Who can use this:**\
    Available via the API. Requires Twilio SMS credentials and an SMS from-number configured in your organization.
  </Update>

  <Update label="March 16, 2026">
    ### Outbound voice agent: graceful invalid number handling

    Outbound and outbound-with-callback voice agents now have a **Gracefully handle invalid number** toggle.

    **What's new:**

    * When enabled, an invalid destination phone number surfaces as an error in the node output and the workflow continues after retries are exhausted
    * When disabled (default), an invalid number causes the node to fail and halts the workflow

    **Why this matters:**\
    Previously, a bad phone number in a batch would stop an entire workflow run. With graceful handling, you can catch invalid numbers in downstream nodes — flag them in your CRM, send an alert, or skip to the next contact — without aborting the whole run.

    **Who can use this:**\
    Available for all outbound and outbound-with-callback voice agent nodes. Find the toggle in the voice agent configuration panel.

    ### HappyRobot TTS v2 voices

    HappyRobot's text-to-speech engine now offers a v2 model tier for supported voices.

    **What's new:**

    * Voices with model version **v2** are now available in the voice library
    * v2 voices use the latest synthesis engine, offering improved naturalness and quality
    * The model version is shown in the **Voice Info** tab when previewing a voice in **Assets > Voices**

    **Why this matters:**\
    v2 voices provide higher quality audio output, especially for longer or more complex speech patterns.

    **Who can use this:**\
    Available to all organizations. Browse and preview v2 voices in **Assets > Voices**.

    ### Run graph: horizontal layout

    The run details graph now supports a horizontal layout orientation.

    **What's new:**

    * New **Vertical / Horizontal** toggle in the graph toolbar
    * Horizontal mode reorients the graph so nodes flow left-to-right instead of top-to-bottom

    **Why this matters:**\
    Wide workflows with many parallel branches or long sequential paths can be easier to read in a horizontal layout.

    **Who can use this:**\
    Available for all runs. Open any run, go to the **Graph** tab, and use the toggle in the toolbar.

    ### HappyRobot MCP server: `get_node_details` and Plate JSON access

    The HappyRobot MCP server adds a `get_node_details` tool and a new parameter for accessing raw prompt structure.

    **What's new:**

    * New **`get_node_details`** tool retrieves the full configuration of a specific workflow node, including its settings and prompt content in compact markdown form
    * New optional **`include_plate_json`** parameter (default `false`) — set to `true` to also receive the raw Plate JSON document for prompt nodes. Useful when you need to inspect or modify the low-level document structure

    **Why this matters:**\
    AI coding assistants using the MCP server can now read node configuration before modifying it, enabling more precise edits. The `include_plate_json` flag avoids sending large JSON payloads by default while still making them accessible when needed.

    **Who can use this:**\
    Available in the `@happyrobot-ai/mcp` package. See the [MCP server docs](../../02-Developer-Tools/01-MCP/01-MCP-servers.md#available-tools) for the full tool reference.
  </Update>

  <Update label="March 11, 2026">
    ### Twin database integration

    Workflows can now read from and write to your organization's managed database using the new **Twin** integration.

    **What's new:**

    * **Read from Twin** — query rows from a Twin table with optional column filters and a row limit
    * **Write to Twin** — insert or upsert a row into a Twin table; primary key columns drive upsert behavior
    * Both nodes support dynamic values (workflow variables) in all fields
    * The Twin database is provisioned per organization; an optional API gateway can expose it as a REST API for external access

    **Why this matters:**\
    Twin gives workflows a persistent, structured store for data that outlives a single run — lookup tables, per-contact state, cached results, or any other tabular data your workflows need to share across runs.

    **Who can use this:**\
    Available to all organizations with a Twin database provisioned. Find the **Twin** integration in the workflow editor under the **Data** category. See the [Twin integration docs](../../01-Developer-Guide/15-Integrations/06-Data-and-Storage/07-Twin-database.md) for configuration details.

    ### Contact Intelligence workflow nodes

    Three new workflow nodes let you read and update contact data directly inside workflows without relying on automatic post-call extraction.

    **What's new:**

    * **Read Contact** — fetch a contact's profile, extracted attributes, and recent interaction history. Look up contacts by contact ID, phone number, or email.
    * **Update Contact** — write or merge attribute values onto a contact record. Useful for persisting data collected during a conversation.
    * **Search Contact Memories** — run a semantic search over a contact's memory store to retrieve the most relevant past facts given a natural-language query.

    **Why this matters:**\
    Previously, contact data was read automatically at the start of agent conversations. These nodes let you read contact context at any point in a workflow, update attributes mid-run as information is collected, and search memories for targeted retrieval rather than loading all recent interactions.

    **Who can use this:**\
    Available to all organizations with contact intelligence configured. Find the **Contact Intelligence** integration in the workflow editor under the **Data** category. See [using contact intelligence in workflows](../../01-Developer-Guide/13-Contacts/04-Memories.md#using-contact-intelligence-in-workflows).

    ### Latency and conversation flow quality flags

    Three new automated quality flags now fire on voice runs that exceed conversation health thresholds.

    **What's new:**

    * **High average latency** — flags runs where the average combined assistant response latency exceeds 3,000 ms
    * **High interruptions** — flags runs where the assistant interrupts the user in more than 40% of turns
    * **High natural cuts** — flags runs where the user cuts off the assistant in more than 40% of turns

    **Why this matters:**\
    These flags surface latency problems and awkward conversation dynamics that aren't visible in transcripts alone. They appear in the **Flags** subtab of the Audits page alongside existing audio quality flags and generate issues for tracking and follow-up.

    **Who can use this:**\
    Applied automatically to all voice runs. No configuration required. Find flagged runs in the **Audits → Flags** tab for any workflow.
  </Update>

  <Update label="March 8, 2026">
    ### Run graph: node variables inspection

    The node detail panel in the run graph now shows the workflow variable values that were in scope when each node executed.

    **What's new:**

    * Click **View Variables** in any node's detail panel to see all workflow variables at the point that node ran
    * Search by variable name to quickly find specific values in large variable sets
    * Variables display as formatted JSON with a copy button alongside the existing Input and Output sections
    * Node configuration is also shown when non-empty

    **Why this matters:**\
    Variable inspection makes it much easier to debug unexpected behavior — you can see exactly what data was available at each step without needing to trace through the full event timeline.

    **Who can use this:**\
    Available for all runs. Open any run, go to the **Graph** tab, and click any node to open the detail panel.
  </Update>

  <Update label="March 5, 2026">
    ### Workflow Import from File

    You can now import a previously exported workflow directly from the new workflow dialog.

    **What's new:**

    * New **Upload File** tab in the **New Workflow** dialog
    * Drag and drop or browse for a `.json` workflow export file
    * The workflow engine version (Version 2 or Version 3) is detected automatically from the file
    * Workflow name defaults to the filename and can be edited before importing

    **Why this matters:**\
    This makes it easy to duplicate workflows across organizations, restore workflows from exports, or migrate workflows without manual rebuilding.

    **Who can use this:**\
    Available to all users. Click **New Workflow** and select the **Upload File** tab. Requires a valid HappyRobot workflow JSON export.

    ### Evaluate page: Northstars and Custom Evals consolidated

    The **Behavioral Northstars** and **Custom Evals** views are now unified under a single **Evaluate** tab when editing a workflow version.

    **What's new:**

    * Northstars and Custom Evals are now tabs within a single **Evaluate** page rather than separate pages
    * The **Behavioral Northstars** tab now includes a **View All Prompts** table that shows every prompt node's northstars at a glance alongside its prompt content — switch to **View Detail** to focus on a single prompt
    * Navigating to the old `/northstars` URL redirects automatically to the Evaluate page

    **Why this matters:**\
    Having northstars and custom evals side-by-side reduces context switching when reviewing agent behavioral rules and test coverage together.

    **Who can use this:**\
    Available to all users. Access via the **Evaluate** tab when editing a workflow version.

    ### Pause and resume realtime updates on the Runs page

    The runs table now has a **Pause / Resume Realtime Updates** toggle in the page header.

    **What's new:**

    * Click **Pause Realtime Updates** to freeze the table while reviewing runs — no new rows or status changes will appear
    * Click **Resume Realtime Updates** to re-enable live updates and refresh the table immediately

    **Why this matters:**\
    When a workflow is actively processing many runs, the table can update frequently and make it hard to focus on a specific row. Pausing live updates lets you inspect a snapshot without the table shifting.

    **Who can use this:**\
    Available to all users. Find the toggle in the header of the Runs page for any workflow.
  </Update>

  <Update label="March 3, 2026">
    ### Salesforce CRM Integration

    Salesforce is now available as a native integration, letting workflows query, create, update, and delete records in your Salesforce org.

    **What's new:**

    * **SOQL Query** — run any SOQL query to retrieve records from Salesforce objects
    * **Create Record** — create new records in any Salesforce object (Account, Contact, Lead, Opportunity, or custom objects)
    * **Get Record** — retrieve a record by ID and select which fields to return
    * **Update Record** — update one or more fields on an existing record
    * **Delete Record** — permanently delete a record by ID
    * Dynamic credentials are supported, so workflows can authenticate with different Salesforce orgs at runtime

    **Why this matters:**\
    This enables direct CRM automation without requiring external middleware. Voice and text agents can look up contacts before a call, log outcomes after a call ends, and update deal or lead status based on conversation results.

    **Who can use this:**\
    Available to all customers. Enable the integration under **Settings > Integrations** and add a Salesforce OAuth credential. Find the actions in the workflow editor under the **Data** category. See the [Salesforce integration docs](../../01-Developer-Guide/15-Integrations/06-Data-and-Storage/06-Salesforce.md) for setup details.

    ### New Spanish regional accent variants

    Three additional Spanish regional accent variants are now available for HappyRobot voices:

    * **Spanish (Colombia)** — `es-CO`
    * **Spanish (Venezuela)** — `es-VE`
    * **Spanish (Peru)** — `es-PE`

    These join the existing Spanish regional accents (Mexico, Argentina, Spain, and others) available in the voice accent selector. Preview any variant from **Assets > Voices** before assigning it to an agent.
  </Update>

  <Update label="February 27, 2026">
    ### Voice Accent Selection

    HappyRobot voices now support regional accent selection, giving you control over how an agent sounds beyond a single language.

    **What's new:**

    * Select a specific regional accent when previewing a voice in the **Assets > Voices** panel
    * Accents are grouped as **Native** (the voice's original training locale) or **Cloned** (synthesized accent variants)
    * Supported accents include regional variants for English, Spanish, Portuguese, German, Dutch, French, Italian, and more (for example, English (US), English (UK), English (Australia), Spanish (Mexico), Spanish (Argentina))
    * Preview any accent combination before selecting a voice for your agent

    **Why this matters:**\
    Matching the voice accent to your callers' expectations improves call experience and reduces friction. A Spanish-speaking agent serving customers in Mexico now sounds distinctly different from one serving customers in Spain.

    **Who can use this:**\
    Available for all HappyRobot voices. Find accent selection in the Text to Speech preview panel on any HappyRobot voice in **Assets > Voices**.

    ### Run Graph View

    The run details panel now includes a **Graph** tab that visualizes workflow execution as a node graph.

    **What's new:**

    * New **Graph** tab alongside the existing Details and Analytics tabs in the run details panel
    * Nodes are color-coded by execution status: green (succeeded), red (failed), gray (skipped), blue (running), yellow (pending)
    * Click any node to see its input and output previews
    * Zoom in and out to navigate larger graphs

    **Why this matters:**\
    The graph view makes it easier to understand execution flow at a glance, especially for complex workflows with conditional paths, loops, or many nodes. You can quickly spot where a run failed or which path was taken without reading through the full event timeline.

    **Who can use this:**\
    Available for all runs. Open any run and click the **Graph** tab in the details panel.

    ### LLM Cost Breakdown in Run Analytics

    The Analytics tab in run details now shows a per-node, per-model breakdown of LLM credit costs.

    **What's new:**

    * The **LLM** row in the credit usage table is now expandable
    * Expand it to see credit consumption per node
    * Expand each node further to see costs by individual model

    **Why this matters:**\
    When a run uses multiple prompt nodes or different models across nodes, it was previously difficult to understand which specific calls drove credit usage. This breakdown makes cost attribution clear and helps you optimize model choices per node.

    **Who can use this:**\
    Available for all runs. Open any run, go to the **Analytics** tab, and expand the LLM row in the Usage section.

    ### Microsoft Teams Text Agent (Beta)

    Microsoft Teams is now a supported channel for text agents, allowing you to deploy AI agents in Teams chats and channels.

    **What's new:**

    * Deploy inbound text agents that respond to messages in personal chats, group chats, and Teams channels
    * Deploy outbound text agents that initiate conversations with Teams users
    * Supports all standard text agent capabilities: system prompts, tools, idle timeouts, reminders, and escalation
    * Uses existing Microsoft Teams OAuth credentials

    **Why this matters:**\
    Teams is a primary communication channel for many enterprise teams. This enables internal automation use cases — routing requests, answering questions from internal knowledge bases, and managing workflows — without leaving Teams.

    **Who can use this:**\
    Currently in beta. Select **Teams** as the channel when configuring an inbound or outbound text agent. Requires a [Microsoft Teams credential](../../01-Developer-Guide/15-Integrations/04-Communication/04-Microsoft-Teams.md).
  </Update>

  <Update label="February 2, 2026">
    ### Custom Evals & Regression Tests (GA)

    Custom Evals and Regression Tests are now generally available, enabling you to systematically test, validate, and safeguard agent behavior as workflows evolve.

    **What's new:**

    **Custom Evals**

    * Create custom tests for prompt nodes that validate agent behavior using full conversation history, workflow variables, and expected outcomes
    * One-click test extraction from runs, create a test directly from any assistant message in a run transcript
    * LLM judge evaluation using plain-language expectations (for example, "The agent should politely decline and offer alternatives")
    * Validation of expected tool calls, including argument structure and content

    **Regression Tests**

    * Version-aware test tracking tied to persistent prompt node IDs
    * Run history with workflow version context, pass/fail status, and LLM judge reasoning
    * Regression detection by re-running test suites before publishing changes to production

    **Why this matters:**\
    Custom Evals act as living documentation for expected agent behavior, while Regression Tests provide confidence that prompt or workflow changes won't break existing scenarios. Together, they enable faster iteration, safer deployments, and clearer auditability of agent behavior over time.

    **Who can use this:**\
    Available to all customers. Access via the **Custom Tests** tab when editing a workflow with prompt nodes. Regression tests are available when runs exist for the workflow.

    ### Compliance Bundles for International Phone Numbers

    Compliance Bundles are now available to simplify regulatory requirements when purchasing international phone numbers.

    **What's new:**

    * New Compliance tab on the Telephony page for centralized bundle management
    * Support for both Twilio and Telnyx providers
    * Guided, three-step bundle configuration:
      * Business information
      * Address verification (when required)
      * Document uploads
    * Support for 35+ countries across Europe, APAC, and the Americas
    * Bundle reuse for unlimited purchases within the same country and number type
    * Real-time status tracking synced with provider APIs
    * Integrated selection during the phone number purchase flow

    **Why this matters:**\
    Many countries require regulatory approval before phone numbers can be purchased. Compliance Bundles remove manual processes, unblock international expansion, and provide clear visibility into approval status, all within the platform.

    **Who can use this:**\
    Available to all customers purchasing phone numbers outside the US and Canada. Find it under **Telephony → Compliance**, or during international phone number purchase.
  </Update>

  <Update label="January 30, 2026">
    ### Post-Transfer Recordings

    Transfers now support optional post-handoff recording and transcription for deeper visibility into human handoffs.

    **What's new:**

    * New Record Transfer Conversation option for Whisper Transfer and Warm Handoff
    * Observer mode continues transcription after the transfer connects
    * Automatic audio silencing once the human representative joins
    * Clear speaker attribution between caller and representative in transcripts

    **Why this matters:**\
    You can now capture and review what happens after an AI hands off to a human, supporting QA, compliance, training, and performance analysis without additional recording infrastructure.
  </Update>

  <Update label="January 29, 2026">
    ### Agents Stay Silent When Appropriate

    Voice agents can now intentionally remain silent instead of always responding.

    **What's new:**

    * New built-in capability allowing agents to stay silent on their turn

    **Why this matters:**\
    This improves conversation flow in scenarios like call holds or IVR navigation, preventing interruptions and making agents feel more natural.
  </Update>

  <Update label="January 25, 2026">
    ### Bridge Chrome Extension

    Bridge now has a Chrome extension that lets customers trigger calls directly from supported load boards.

    **What's new:**

    * Trigger calls from DAT, Highway, Truckstop, and TransportPro
    * No need to switch to the Bridge UI to initiate calls

    **Why this matters:**\
    This reduces friction by keeping actions closer to where users already work.
  </Update>

  <Update label="January 23, 2026">
    ### Custom MCP Connections and Tools

    HappyRobot now supports connecting external Model Context Protocol (MCP) servers directly into workflows.

    **What's new:**

    * Connect external MCP servers using bearer tokens, API keys, or no authentication
    * Automatic discovery of available MCP tools
    * Use MCP tools directly in agent prompts like native workflow tools
    * Built-in execution, authentication, timeout handling, and error management

    **Why this matters:**\
    This enables near-unlimited extensibility by allowing agents to interact with external systems without waiting for native integrations.

    ### Native OCR and Extraction Node

    Document processing has been consolidated into a single, more powerful OCR and extraction node.

    **What's new:**

    * Standard mode for simple field extraction
    * Advanced mode using JSON Schema for complex documents
    * Node Playground for isolated testing
    * Direct file URL support

    **Why this matters:**\
    Teams can extract structured data faster and more reliably while shortening the development and testing loop.

    ### Text Agents Over Email (General Availability)

    Email is now a first-class channel for text-based AI agents.

    **What's new:**

    * Stateful, multi-turn email conversations
    * Environment-specific credential isolation
    * Automated inbound subscription handling
    * Smart reminders, idle timeouts, and escalation tools

    **Why this matters:**\
    This shifts email automation from static sequences to intelligent, goal-driven agents that can manage complex conversations over time.

    ### MetaPrompter (Beta)

    MetaPrompter helps teams write and optimize prompts through natural conversation.

    **What's new:**

    * Multi-model support
    * Prompt editing with diff-based suggestions
    * Tool and variable management via chat
    * Automated issue detection and optimization guidance

    **Why this matters:**\
    Prompt development becomes faster, safer, and more accessible, improving agent quality and consistency.
  </Update>

  <Update label="January 21, 2026">
    ### Audio Assets Library and Custom Recordings / Disclaimers

    Voice agents now support custom audio assets for disclaimers and in-call experiences.

    **What's new:**

    * Custom Audio Assets for Disclaimers: Upload or import pre-recorded audio files to use as the recording disclaimer
    * Audio Asset Integration: Use audio assets from your library as hold music during tool calls

    **Why this matters:**\
    This enables brand-consistent voice experiences, helps meet compliance requirements with exact wording, and improves the in-call experience with higher-quality audio.
  </Update>

  <Update label="January 20, 2026">
    ### Voice DTMF Detection

    Transfer flows are now voice-interactive, so representatives can respond using spoken commands instead of pressing phone keys.

    **What's new:**

    * Reps can say "one" to hear context or "nine" to accept the call during warm transfers
    * Improves transfer usability in systems where keypad input isn't supported

    **Why this matters:**\
    This makes handoffs smoother and more natural, and improves compatibility with telephony systems that don't reliably support key presses.
  </Update>

  <Update label="January 19, 2026">
    ### JSON Objects in Webhook Bodies

    Webhook nodes now support working directly with raw JSON payloads.

    **What's new:**

    * Toggle between Builder and JSON modes when configuring webhook bodies
    * Paste a raw JSON object and automatically map it into structured fields
    * Preserves nested objects, booleans, and arrays

    **Why this matters:**\
    This speeds up workflow setup for technical users while still keeping payloads readable and editable in a structured UI.

    ### Contact Intelligence and Memory Updates (Official Release)

    Contact Intelligence has been expanded with new capabilities and is now officially released.

    **What's new:**

    * Extracted attributes: Define custom key-value pairs to extract from conversations and store them on contacts and communication events
    * Granular variable exposure: Option to disable automatic context injection and reference contact context manually in prompts
    * Per-event attribute extraction: Store attributes at the interaction level for more detailed tracking
    * Editable attributes in the UI: Edit, update, or delete extracted attributes directly in the Contacts panel

    **Why this matters:**\
    These updates support structured data capture at scale, improve control over how context is used in prompts, and make it easier to correct and manage extracted data over time.

    ### Node Components (Beta)

    Reusable Node Components are now available in beta.

    **What's new:**

    * Create reusable action node templates from configured action nodes
    * Two modes:
      * Create as Copy: Create a standalone copy you can customize independently
      * Create as Synced: Reuse a synced component across workflows and apply updates everywhere
    * Parameterized inputs to support runtime values
    * Component library UI to browse, create, and manage components with version history

    **Why this matters:**\
    Node Components reduce duplication, improve consistency across workflows, and make large-scale updates safer and faster.

    ### Revamped Resources

    The UI/UX for Integrations and Assets has been revamped, including Components, Knowledge Bases, Phone Numbers, and Voices.

    **What's new:**

    * Updated layouts and interaction patterns across resources-related pages
    * More consistent organization and navigation

    **Why this matters:**\
    A more consistent UI reduces cognitive load and makes the platform easier to use as workflows and assets scale.
  </Update>

  <Update label="January 16, 2026">
    ### Interruption Loop Breaker

    Voice agents now detect and break out of interruption loops to keep conversations natural when users and agents talk over each other.

    **What's new:**

    * Detects repeated interruptions during an agent response
    * Produces a short, contextual phrase that yields the floor back to the user

    **Why this matters:**\
    This reduces awkward back-and-forth behavior and improves the overall conversational experience.
  </Update>

  <Update label="January 14, 2026">
    ### Module Change Node

    You can now transition **from one prompt module to any other prompt module** within a workflow.

    **What's new:**

    * Seamlessly switch between any prompts in a workflow
    * No longer limited to navigating only to previous prompts

    **Why this matters:**\
    This enables more powerful and flexible workflow design, allowing agents to move dynamically between prompts based on context or logic.
  </Update>

  <Update label="January 12, 2026">
    ### Multi-Lingual Transcriber v2 & Keyterms Generation

    HappyRobot now includes a new multi-lingual transcription engine with automatic and manual keyterms support for more accurate speech-to-text.

    **What's included:**

    * Improved multi-lingual transcriber with smoother live language switching
    * Significantly improved transcription quality across supported languages
    * Automatic keyterms generation using AI to extract domain-specific vocabulary from agent prompts
    * Manual keyterms management with inline entry and bulk import
    * Variable support for dynamic keyterms (such as names, organizations, or caller-specific terms)

    **Why this matters:**\
    The previous transcriber struggled with language detection and switching. The new engine fixes these issues while improving baseline transcription quality. Combined with keyterms, agents can accurately transcribe industry-specific terms that standard speech-to-text often misses.

    **Availability:**\
    Available to all users. The new transcriber is enabled by default when multiple languages are selected, and keyterms generation is available platform-wide.

    ### Dynamic Credentials for Integrations

    Credentialed integration actions can now accept **dynamic Credential IDs** instead of requiring a static credential selection.

    **What's new:**

    * Use Credential IDs dynamically within workflows
    * Copy Credential IDs directly from the Integrations page
    * Switch between static and dynamic credential configuration per step

    **Why this matters:**\
    This enables multi-user workflows without duplication and reduces configuration overhead by eliminating the need to clone workflows just to swap credentials.

    ### Safe Email Testing with Environment Tabs & Testing Credentials

    Gmail and Outlook nodes now support **per-environment configurations** and safe testing credentials.

    **What's new:**

    * Separate Production, Staging, and Development tabs for email nodes
    * Environment-based behavior when publishing workflows
    * Safe testing using a dedicated Testing Credential for email actions

    **Why this matters:**\
    This prevents accidental reads or sends from production inboxes during testing and enables faster, safer QA across environments.

    ### Platform Improvements: Models, Webhooks, and File Uploads

    Several platform improvements have been released to improve compatibility and flexibility.

    **What's new:**

    * Anthropic models are now available for text agents
    * Deprecated models are no longer selectable in agents
    * Webhooks now support XML payloads via `Content-Type: application/xml`
    * File uploads now support `.xls` and `.xlsx` formats

    **Why this matters:**\
    These updates simplify enterprise integrations, improve model flexibility, and reduce reliance on external tooling for common workflows.
  </Update>

  <Update label="January 6, 2026">
    ### OAuth2 Authentication for Webhook Triggers

    Webhook triggers now support OAuth2-based authentication, providing stronger security and more flexible access control.

    **What's new:**

    * Triggers now accept Authorization: Bearer \<token> authentication
    * Token validation via a configurable authenticator
    * Support for Google, Microsoft, and custom identity providers

    **Why this matters:**\
    OAuth2 authentication reduces accidental triggers, improves auditability, and enables scoped, revocable access that better meets enterprise security and compliance requirements.
  </Update>

  <Update label="January 4, 2026">
    ### Knowledge Bases & Retrieval-Augmented Generation (RAG) v1

    HappyRobot's Knowledge Bases and RAG capabilities have been significantly enhanced with more powerful ingestion, search, and customization options.

    **What's included:**

    * Direct URL ingestion with support for ingesting up to 20 URLs in parallel
    * Hybrid search that combines keyword and semantic search with tunable weighting
    * Document-level search mode for improved accuracy when information spans multiple chunks
    * Metadata enrichment using file-level details (such as title and file type) to improve retrieval quality
    * Enhanced configuration options for file uploads and re-chunking

    These capabilities are available in both the Assets page "Ask" feature and the Knowledge Base node in the workflow builder.

    **Why this matters:**\
    These improvements enable more accurate, flexible, and scalable knowledge retrieval, supporting advanced agent workflows and complex information-retrieval use cases.
  </Update>

  <Update label="December 30, 2025">
    ### Improved Call Transfer Visibility

    The Direct Transfer node now provides detailed transfer outcomes directly in its node output, giving you clearer insight into what happens during call handoffs.

    **What's new:**

    * Visibility into whether a transfer succeeded or failed
    * Confirmation of when the receiving rep picked up and when the transfer completed
    * Indicators for warm handoff actions, including:
      * Whether the rep pressed 1 to hear the recording
      * Whether the rep pressed 9 to connect to the original call
      * Whether the rep disconnected before completing the transfer

    **Why this matters:**\
    Transfers are no longer a black box. You can now understand exactly how each handoff unfolded and use these outcomes to log rep behavior, monitor performance, or trigger follow-up workflows when a transfer doesn't complete as expected.
  </Update>

  <Update label="December 16, 2025">
    ### Knowledge Bases & Retrieval-Augmented Generation (RAG)

    HappyRobot now supports Knowledge Bases and Retrieval-Augmented Generation to help agents access long-form and proprietary information more effectively.

    **What's included:**

    * Upload documents such as PDFs, text files, images, or audio
    * Search and retrieve relevant information during conversations
    * Use retrieved knowledge inside workflows and agent logic

    **Why this matters:**\
    This allows agents to answer questions using customer-specific knowledge that is too large or complex to include directly in prompts, improving accuracy and flexibility for support and internal use cases.

    ### Contact Intelligence & Interaction Memory

    HappyRobot now provides deeper visibility into conversations and contacts across channels.

    **What's included:**

    * Centralized view of contacts and their interactions
    * Ability to retain context across conversations
    * Improved handling of follow-ups and repeat interactions

    **Why this matters:**\
    Maintaining context across interactions helps agents deliver more consistent, informed, and human-like experiences over time.
  </Update>

  <Update label="December 12, 2025">
    ### Improved Conversation Handling with Filler Detection

    HappyRobot has improved how agents handle interruptions and conversational noise.

    **What's included:**

    * Smarter handling of short acknowledgments and background speech
    * Reduced unnecessary interruptions during conversations
    * Improved conversational flow and responsiveness

    **Why this matters:**\
    Agents can better understand when to respond and when to wait, creating more natural and effective conversations.

    ### Business Hours Configuration

    You can now define and manage business hours directly in the platform.

    **What's included:**

    * Custom business hour schedules
    * Control over agent behavior outside operating hours
    * Cleaner handling of after-hours scenarios

    **Why this matters:**\
    This makes it easier to align agent behavior with real-world operating schedules without complex workarounds.
  </Update>

  <Update label="December 7, 2025">
    ### Chatbot Agent

    The first version of the HappyRobot Chatbot Agent is now available.

    **What's included:**

    * Embeddable chatbot for websites
    * Customizable branding and appearance
    * Designed to integrate with broader conversational workflows

    **Why this matters:**\
    This expands HappyRobot's omnichannel capabilities, allowing agents to engage users directly on the web.

    ### Text Agents over SMS

    HappyRobot now supports AI agents over SMS.

    **What's included:**

    * Inbound and outbound SMS agents
    * Flexible number setup
    * Media support, including image handling and voice note transcription
    * Ability to combine SMS with other channels in workflows

    **Why this matters:**\
    SMS becomes a fully supported channel, enabling seamless communication across voice, text, and other platforms.
  </Update>

  <Update label="December 5, 2025">
    ### Text Agents over WhatsApp

    HappyRobot now supports AI agents over WhatsApp.

    **What's included:**

    * Inbound and outbound WhatsApp agents
    * Support for approved outbound templates
    * Media and audio handling, including voice notes and images
    * Integration with multi-channel workflows

    **Why this matters:**\
    Agents can now engage users on WhatsApp with the same intelligence and flexibility as other channels.

    ### Workflow Validation Improvements

    HappyRobot now provides better visibility into workflow configuration issues.

    **What's new:**

    * Clear indicators for missing or unused variables
    * Warnings shown before publishing workflows

    **Why this matters:**\
    This helps prevent configuration errors and improves reliability when building or reusing workflows.

    ### Dead Variable Visibility

    You can now see empty or unused variables directly within workflow nodes, making it easier to catch issues before publishing.

    **What's new:**

    * Visibility into empty variables within workflow nodes
    * Warnings shown in the tools panel and before publishing to any environment

    **Why this matters:**\
    When duplicating or importing workflows, unused variables can be easy to miss—especially in complex setups. This update helps you identify and resolve these issues faster, reducing debugging time and improving workflow reliability.
  </Update>

  <Update label="December 3, 2025">
    ### Improved Text-to-Speech Voices

    HappyRobot has enhanced its text-to-speech capabilities.

    **What's included:**

    * Improved voice quality in English and Spanish
    * Faster response times
    * Better handling of numbers and structured information

    **Why this matters:**\
    Clearer, faster speech improves the overall conversational experience for end users.
  </Update>

  <Update label="November 18, 2025">
    ### New Voice Models Available

    Three new voice models are now available for testing in voice agents:

    * **GPT-5.1**
    * **Fast GPT-5.1** (optimized for lower latency)
    * **Gemini 3 Pro** — Minimal, Low, and High Thinking modes

    These models provide improved reasoning, tool use, and more natural conversational behavior.
  </Update>

  <Update label="November 14, 2025">
    ### New Assets Page

    A unified **Assets** page now centralizes all deployment resources:

    * Phone numbers
    * Voices
    * Integrations
    * Prompt Components

    This update improves organization and prepares for future asset types such as knowledge bases and templates.

    ### Prompt Components

    A new reusable system for managing prompt logic across multiple agents.

    **Highlights:**

    * Parent changes propagate to all instances
    * Built-in version history
    * Component updates appear in workflow version history
    * Variables allow instance-level customization
  </Update>

  <Update label="November 12, 2025">
    ### Development Environment (Dev → Staging → Prod)

    Workflows can now be published to a dedicated **Development** environment before Staging or Production.

    **Highlights:**

    * Environment-specific variables and triggers
    * Pre-publish checks for missing or incomplete nodes
    * "Play" and web-call triggers now execute the correct environment version

    ### Pull Runs Into Chat Playground

    You can now open workflow runs directly inside the **Chat Playground**.

    **You can:**

    * Replay user and agent messages
    * Edit messages and regenerate responses
    * Trigger associated tool calls
    * Modify variables with **Current Variables**

    ### Infinite Nested Folders

    You can now organize content with **unlimited nested folders**, supporting large organizations and multi-team structures.

    ### Microsoft Teams — Push Subscription Service

    The Teams integration now includes a push-based subscription service, offering:

    * More reliable message delivery
    * Clearer subscription status visibility
    * Improved scalability

    ### Email Integrations — Service Accounts

    Gmail and Outlook integrations now support **Service Accounts**.

    **Benefits:**

    * Secure, governed access
    * Stable background automation
    * Enterprise compliance
  </Update>

  <Update label="November 10, 2025">
    ### Metabuilder v0 — Prompt Issue Detection

    The Metabuilder now analyzes prompt logic and tool usage to help identify potential issues before publishing workflows.

    **What's new:**

    * Detects prompt logic issues
    * Provides warnings before deployment
    * Enhances workflow reliability
  </Update>
</div>

---

Fuente original: https://docs.happyrobot.ai/release-notes
