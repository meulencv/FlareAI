---
title: "Custom Code"
description: "Run Python code within your workflow"
---

# Custom Code

> Run Python code within your workflow

The Custom Code node lets you run Python code directly inside your workflow. Use it when you need custom data transformation, calculation, or logic that isn't covered by other node types.

Python runs in a sandboxed runtime in an isolated container. Pick an **execution profile** to control which packages are available — **Standard** for standard-library and date/time work, or **Advanced** for a curated set of document, data, text, and image libraries. Network access and arbitrary package installs are disabled in both profiles.

<Note>
  The legacy **Run Python** node has been retired. It can no longer be created — from the node picker, the [API](https://docs.happyrobot.ai/api-reference/overview), or the [MCP server](../../02-Developer-Tools/01-MCP/01-MCP-servers.md) — and every existing Run Python node has been migrated to the sandbox on the **Standard** profile. Your code and inputs carry over unchanged.
</Note>

## Configuration

### Execution profile

A segmented control at the top of the node selects how the sandbox runs:

| Profile      | Python version | Available packages                                                                                                                                                                  |
| ------------ | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Standard** | Python 3.10    | The Python standard library plus `DateTime`, `python-dateutil`, and `pytz`. Best for one-liners, string formatting, JSON shaping, date/time handling, and lightweight control flow. |
| **Advanced** | Python 3.12    | A curated set of document, spreadsheet, text, and image libraries. Use for document parsing, data processing, text transformation, images, and geospatial work.                     |

New nodes default to the **Standard** profile. Switch to **Advanced** when your code imports one of the curated packages listed below.

Select the profile's **Available Libraries** info icon in the node to see the full package list for that profile, grouped by category, directly in the editor.

### Input data

Define key-value pairs that are passed into your code. Each key becomes accessible in the `input_data` dictionary.

* **Key** — The variable name you'll reference in code (e.g., `phone_numbers`, `raw_data`)
* **Value** — The value to pass in, which can be a static value or a variable reference

Supports variables — type `@` in the value field to insert outputs from previous nodes.

### Code

A Python code editor (Monaco) where you write your logic. Access input values through the `input_data` dictionary:

```python theme={null}
# Access input data
raw_text = input_data['transcript']
numbers = input_data['phone_numbers']

# Process data
cleaned = raw_text.strip().lower()
formatted_numbers = [n.replace('-', '') for n in numbers]

# Store results in the output variable
output = {
    'cleaned_text': cleaned,
    'formatted_numbers': formatted_numbers,
    'count': len(formatted_numbers)
}
```

## Available libraries

Which libraries you can import depends on the [execution profile](#execution-profile). Network access and arbitrary package installs are disabled in both profiles.

### Standard profile

Runs on **Python 3.10** with the standard library plus date/time helpers:

| Group    | Packages                                                       |
| -------- | -------------------------------------------------------------- |
| Included | Python standard library, `DateTime`, `python-dateutil`, `pytz` |

### Advanced profile

Runs on **Python 3.12** with a curated set of packages for document, data, text, and image work:

| Group                        | Packages                                                                                                                |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Documents and PDFs           | `pypdf`, `pdfplumber`, `python-docx`, `docx2txt`, `mammoth`, `python-pptx`                                              |
| Spreadsheets and data        | `pandas`, `polars`, `numpy`, `pyarrow`, `duckdb`, `openpyxl`, `XlsxWriter`                                              |
| Validation and serialization | `orjson`, `jsonschema`, `pydantic`                                                                                      |
| Dates and contact data       | `DateTime`, `python-dateutil`, `dateparser`, `phonenumbers`, `email-validator`                                          |
| Text and markup              | `rapidfuzz`, `python-slugify`, `ftfy`, `Unidecode`, `beautifulsoup4`, `markdown`, `mistune`, `markdownify`, `html2text` |
| Images and spatial data      | `Pillow`, `piexif`, `qrcode`, `shapely`, `pyproj`                                                                       |
| Utilities                    | `networkx`, `more-itertools`, `toolz`, `boltons`                                                                        |

The exact package list for the selected profile is also shown in the node's **Available Libraries** popover. If you need a library that isn't available in either profile, reach out so the sandbox profile can be extended.

## Output

Your code **must** store results in a variable called `output`. This variable becomes the node's output and is available to all downstream nodes via the `@` picker.

The `output` variable can be a string, number, list, dictionary, or any JSON-serializable value.

<Warning>
  Do not use `time.sleep()` or any blocking delay in your code. Use the [Schedule](07-Schedule.md) node for delays instead. Custom Code executions have a timeout limit — long-running operations will be terminated.
</Warning>

## Example

A previous node returns a list of load records. The Custom Code node filters for loads over 40,000 lbs, calculates the average weight, and formats a summary string — all in a few lines of Python that would be awkward to express with other node types.

## Related

<CardGroup cols={2}>
  <Card title="AI Extract" icon="wand-magic-sparkles" href="02-AI-Extract.md">
    Extract structured data using AI instead of code.
  </Card>

  <Card title="Variables" icon="brackets-curly" href="../02-Workflows/07-Variables.md">
    Learn how to pass data between nodes.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/core-nodes/custom-code
