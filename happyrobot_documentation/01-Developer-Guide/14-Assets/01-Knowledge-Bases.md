---
title: "Knowledge Bases"
description: "Upload and manage documents for agent reference"
---

# Knowledge Bases

> Upload and manage documents for agent reference

Knowledge bases let you upload documents, URLs, and raw text that your agents can search during conversations using retrieval-augmented generation (RAG). When a voice or text agent needs to answer a question, it queries the knowledge base to find relevant content and uses it to ground its response. You can use knowledge bases in your workflows via the **Knowledge Base** action node — see [Node types](../02-Workflows/04-Node-Types.md) for details.

## Creating a knowledge base

<Steps>
  <Step title="Navigate to knowledge bases">
    Go to **Assets > Knowledge Bases** and click **Create Knowledge Base**.
  </Step>

  <Step title="Name your knowledge base">
    Enter a name and optional description. The name helps you identify the KB when referencing it from workflow nodes.
  </Step>

  <Step title="Organize with folders">
    Optionally create folders on the **Knowledge Bases** page to group related knowledge bases by topic, department, or any structure that makes sense for your use case. See [Organizing the knowledge base list](#organizing-the-knowledge-base-list).
  </Step>

  <Step title="Add content">
    Add content using one or more of the methods described below: file upload, URL scraping, web sources, or free text.
  </Step>
</Steps>

## Adding content

### File upload

Drag and drop files or use the file picker to upload documents. Files are stored in cloud storage and processed asynchronously — you'll see a processing status indicator while chunking completes. Your organization's storage limits are displayed in the UI, so you can track how much capacity remains.

#### Maximum file size

Each knowledge base has a **Maximum file size** setting that caps how large any single item added to it can be. Set it from the knowledge base's settings — open a knowledge base and edit its details to adjust the value.

| Setting               | Description                                                                                                                                                              | Default |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------- |
| **Maximum file size** | The largest size, in MB, allowed for any item added to this knowledge base. Applies to uploaded files, free-text documents, and web-source documents. Range: 1–1,024 MB. | 10 MB   |

Files that exceed the limit are rejected at upload time, and the error names which files were too large. The same limit is enforced on the [public API](https://docs.happyrobot.ai/api-reference) — set `max_file_size_mb` when creating a knowledge base, and upload requests for oversized files are rejected.

### URL scraping

Paste up to 20 URLs to scrape web content directly into the knowledge base. You can optionally assign custom names to each URL for easier identification. The content is fetched, extracted, and indexed automatically.

### Web sources

Web sources keep knowledge base content in sync with a website by crawling it on demand or on a schedule. Unlike one-off **URL scraping**, a web source is a managed connection that you can re-crawl, refresh automatically, and inspect over time. When you add a web source, choose a **Source type** that controls how much of the site is crawled:

| Source type        | What it crawls                                                                                 |
| ------------------ | ---------------------------------------------------------------------------------------------- |
| **This page**      | Only the single URL you provide.                                                               |
| **Selected pages** | HappyRobot discovers the pages reachable from the URL and lets you pick which ones to include. |
| **Entire website** | Every page reachable from the starting URL.                                                    |

For **Selected pages**, click to discover pages from the starting URL, then select the pages you want indexed from the list.

#### Web source options

| Option                        | Description                                                                                                                                                                                   |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Auto-remove missing pages** | When enabled, pages that disappear from the site on a later crawl are removed from the knowledge base automatically.                                                                          |
| **Auto-refresh**              | When enabled, the source is re-crawled on a recurring schedule. Choose a cadence of **Daily**, **Weekly**, or **Monthly**. When off, the source is only crawled when you trigger it manually. |
| **Chunking**                  | Web source pages use the same chunking configuration as files (see [Chunking configuration](#chunking-configuration)).                                                                        |

#### Managing crawls

Each web source tracks its crawl history as a series of **sync runs**. Open a web source to see the runs table, which shows each crawl's status along with the number of **discovered**, **processed**, and **updated** pages and how long it took. From here you can:

* **Refresh** — start a new crawl immediately to pick up the latest content.
* **Cancel** — stop a crawl that is currently running.

Crawled pages appear as files in the knowledge base alongside any uploaded documents, so agents search them the same way.

### Free text

Paste raw text directly into the knowledge base. This is useful for adding FAQs, policy documents, or any structured text that doesn't exist as a file or web page.

## Chunking configuration

Before content can be searched, it's split into smaller segments called **chunks**. Chunking determines how documents are divided for indexing and retrieval — smaller chunks are more precise but may lose surrounding context, while larger chunks preserve context but may include irrelevant content.

| Setting           | Description                                                                                                                                            | Default   |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | --------- |
| **Algorithm**     | `Recursive` splits by character separators (paragraphs, sentences, words). `Token` splits by GPT-4 tokens for more semantically consistent boundaries. | Recursive |
| **Chunk size**    | Maximum size per chunk. Recursive: 100–5,000 characters. Token: 50–2,000 tokens.                                                                       | 1,000     |
| **Chunk overlap** | Number of characters or tokens shared between adjacent chunks. Overlap improves context continuity at chunk boundaries. Range: 0–500.                  | 100       |

<Tip>
  After changing chunking settings, you can trigger re-chunking to reprocess all existing content with the new configuration.
</Tip>

## Searching knowledge bases

When you use a Knowledge Base action node in a workflow, you configure how the search queries and retrieves content. Three search strategies are available:

### Semantic search

Vector similarity search using embeddings. The query is converted to a vector and matched against chunk embeddings to find semantically similar content — even if the exact words don't match.

### Keyword search

Full-text search that matches exact terms in the query against the indexed content. Best when you need precise term matching.

### Hybrid search

Combines semantic and keyword search using Reciprocal Rank Fusion. Configure the balance between approaches with two weights:

* **`vector_weight`** — How much to weight semantic results
* **`keyword_weight`** — How much to weight keyword results

### Search parameters

| Parameter            | Description                                                     | Default |
| -------------------- | --------------------------------------------------------------- | ------- |
| **`top_results`**    | Number of top-ranked results to return. Range: 1–1,000.         | 10      |
| **`max_chunks`**     | Maximum number of chunks to include in results. Range: 1–1,000. | 200     |
| **`max_characters`** | Maximum total characters across all returned chunks.            | 15,000  |

### Document mode

Enable document mode to retrieve full documents instead of individual chunks. This is useful when the agent needs complete context from a document rather than isolated passages.

## Organizing the knowledge base list

**Assets > Knowledge Bases** shows your knowledge bases as a tree, with folders grouping related knowledge bases together. Expand a folder to see the knowledge bases inside it; each folder row totals the file count and storage size of everything it contains.

You can move knowledge bases between folders two ways:

* **Drag and drop** — drag a knowledge base onto a folder to file it there, or onto the list root to take it out of its folder. Select several rows first to move them together. The row jumps to its new position immediately and settles once the move is saved.
* **Row menu** — open a knowledge base's actions menu (**⋯**) and use **Move to folder** or **Remove from folder**.

Searching filters the tree: folders stay visible when their name matches or when they contain a matching knowledge base.

Deleting a folder does not delete the knowledge bases in it — they stop being grouped and move back to the top level.

## Managing knowledge bases

* **File details** — View individual files to see their metadata, processing status, and the chunks generated from them.
* **Chunk preview** — Inspect individual chunks to verify that your chunking settings are producing useful segments.
* **File preview** — Preview uploaded files directly in the platform without downloading them.
* **Deletion** — Delete individual files to remove them from the knowledge base, or delete the entire knowledge base when it's no longer needed.

## Next steps

<CardGroup cols={3}>
  <Card title="Workflows overview" icon="diagram-project" href="../02-Workflows/01-Workflows-Overview.md">
    Learn how to build automated workflows.
  </Card>

  <Card title="Prompts and tools" icon="message" href="../05-Voice-Agents/06-Prompts-and-Tools.md">
    Write effective prompts and attach tools to agents.
  </Card>

  <Card title="Voice agents" icon="microphone" href="../05-Voice-Agents/01-Voice-Agents-Overview.md">
    Get started with AI voice agents.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/assets/knowledge-bases
