# event-generator

## Overview

`event-generator` is a Python toolset for managing events, tickets, and attendee questions for Dundee Data Meetup using the Tito API. It provides scripts to automate the creation of events, bulk ticket releases, and attendee question management.

## Features

- **Automated Event Creation:** Generate recurring events (e.g. last Tuesday of each month) with templated descriptions.
- **Bulk Ticket & Question Management:** Interactively create ticket releases and attendee questions for multiple events.

## Prerequisites

- Python 3.14 or higher
- [uv](https://github.com/astral-sh/uv) for package management

## Setup

### 1. Install Dependencies

Install the required dependencies using uv:

```bash
uv sync
```

### 2. Set Up Environment Variables

Create a `.env` file in the root of the project and add the following environment variables:

```
API_TOKEN=your_tito_api_token
```

- `API_TOKEN`: Your Tito API token for authentication. This can be generated from <https://id.tito.io/api-access-tokens>

### 3. Usage

#### Generate Events

To generate events for a given year using a Markdown template:

```bash
uv run generate-events.py
```

- This will read `event_description_template.md` and create events for each month's last Tuesday.

#### Bulk Update Tickets & Questions

To interactively create ticket releases and attendee questions for upcoming events:

```bash
uv run bulk-update.py
```

- You will be prompted to select actions and events via the command line.

## Files

- [`generate-events.py`](generate-events.py): Script for automated event creation.
- [`bulk-update.py`](bulk-update.py): Script for bulk ticket and question management.
- [`event_description_template.md`](event_description_template.md): Markdown template for event descriptions.
- [`pyproject.toml`](pyproject.toml): Project configuration and dependencies.