# FOGIS Match Event API - Python Reporting Script

## Description

This Python script interacts with the Swedish Football Association (FOGIS) Match Event API. It allows users to:

*   **Log in** to the FOGIS API using credentials.
*   **Interactively report match events** (Goals, Yellow Cards, Red Cards, Substitutions, etc.) for a specific match.
*   **Report match results** (Half-time and Full-time scores).
*   **Delete reported match events** (for testing/correction purposes).

This script is intended to automate the process of reporting match events to the FOGIS system, potentially for referees or match officials.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fogis-reporter.git
   cd fogis-reporter
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

> **Note:** This project requires fogis-api-client-timmyBird version 0.2.4 or higher to function correctly. Earlier versions may encounter API errors due to parameter name mismatches.

## API Documentation Summary

Based on reverse engineering and testing, here's a summary of key findings about the FOGIS Match Event API:

### Base URL
https://fogis.svenskfotboll.se/mdk/MatchWebMetoder.aspx/

### Authentication

*   **Method:** Form-based login with cookie-based session management.
*   **Login Endpoint:** `https://fogis.svenskfotboll.se/mdk/Login.aspx?ReturnUrl=%2fmdk%2f`
*   **Request Method:** `POST` to the Login Endpoint.
*   **Required Headers (Minimal Set):**

    ```json
    {
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
      "Content-Type": "application/x-www-form-urlencoded",
      "Cookie": "",
      "Host": "fogis.svenskfotboll.se",
      "Origin": "https://fogis.svenskfotboll.se",
      "Referer": "https://fogis.svenskfotboll.se/mdk/Login.aspx?ReturnUrl=%2fmdk%2f",
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    ```

*   **Required Cookies:**
    *   `FogisMobilDomarKlient.ASPXAUTH`: Primary authentication cookie (set by server after successful login).
    *   `ASP.NET_SessionId`: Session management cookie (set by server).
    *   `NSC_JOx1rkamdlwrmtgbqy0motevlawo5b2`:  Additional cookie (set by server, purpose unclear but seems necessary).
    *   `cookieconsent_status`: Cookie consent cookie (set by script to `dismiss`).

*   **Login Flow:**
    1.  Send a `GET` request to the login page URL to initiate a session and get initial cookies.
    2.  Extract hidden fields (`__VIEWSTATE`, `__EVENTVALIDATION`, etc.) from the login page HTML.
    3.  Send a `POST` request to the login URL with username, password, hidden fields, and browser-like headers.
    4.  Successful login results in a `302 Redirect` response and the `FogisMobilDomarKlient.ASPXAUTH` cookie being set.
    5.  Follow the redirect URL (relative URL `/mdk/` needs to be converted to absolute).

### Match Event Reporting Endpoint

*   **URL:** `https://fogis.svenskfotboll.se/mdk/MatchWebMetoder.aspx/SparaMatchhandelse`
*   **Method:** `POST`
*   **Request Headers:** `Content-Type: application/json`, `Accept: application/json`, `Cookie` (with authentication cookies).
*   **Request Payload (JSON):**

    ```json
    {
      "matchhandelseid": [event_id_or_0],  // 0 for new event
      "matchid": [match_id],
      "period": [1 or 2],
      "matchminut": [minute],
      "sekund": [second],
      "matchhandelsetypid": [event_type_id],
      "matchlagid": [team_id],
      "spelareid": [player_global_id],
      "spelareid2": [second_player_global_id], // For substitutions
      "hemmamal": [home_goals], // Current score
      "bortamal": [away_goals], // Current score
      "planpositionx": "-1",
      "planpositiony": "-1",
      "matchdeltagareid": [player_match_specific_id_or_0], // Optional, use 0 if not available
      "matchdeltagareid2": [second_player_match_specific_id_or_0], // Optional, use 0 if not available
      "fotbollstypId": 1,
      "relateradTillMatchhandelseID": 0  // For substitutions, server automatically links events
    }
    ```

*   **Response:** Returns a JSON response with details of the created event(s). Substitutions return two linked events in the response.

### Match Event Deletion Endpoint

*   **URL:** `https://fogis.svenskfotboll.se/mdk/MatchWebMetoder.aspx/RaderaMatchhandelse`
*   **Method:** `POST`
*   **Request Headers:** `Content-Type: application/json`, `Accept: application/json`, `Cookie` (with authentication cookies).
*   **Request Payload (JSON):**

    ```json
    {
        "matchhandelseid": [event_id] // ID of the event to delete
    }
    ```

*   **Response:** Returns `{"d":null}` upon successful deletion.

### Match Result Reporting Endpoint

*   **URL:** `https://fogis.svenskfotboll.se/mdk/MatchWebMetoder.aspx/SparaMatchresultatLista`
*   **Method:** `POST`
*   **Request Headers:** `Content-Type: application/json`, `Accept: application/json`, `Cookie` (with authentication cookies).
*   **Request Payload (JSON):**

    ```json
    {
      "matchresultatListaJSON": [
        {
          "matchid": [match_id],
          "matchresultattypid": 1, // 1 for full-time
          "matchlag1mal": [team1_goals],
          "matchlag2mal": [team2_goals],
          "wo": false,
          "ow": false,
          "ww": false
        },
        {
          "matchid": [match_id],
          "matchresultattypid": 2, // 2 for half-time
          "matchlag1mal": [team1_halftime_goals],
          "matchlag2mal": [team2_halftime_goals],
          "wo": false,
          "ow": false,
          "ww": false
        }
      ]
    }
    ```

*   **Response:** Returns `{"d":null}` upon successful submission.

### Team Official Disciplinary Action Endpoint

*   **URL:** `https://fogis.svenskfotboll.se/mdk/MatchWebMetoder.aspx/SparaMatchlagledare`
*   **Method:** `POST`
*   **Request Headers:** `Content-Type: application/json`, `Accept: application/json`, `Cookie` (with authentication cookies).
*   **Request Payload (JSON):**

    ```json
    {
      "matchlagledareid": [team_official_id],
      "lagrollid": [team_role_id],
      "avvisadmatchminut": [minute_of_dismissal],
      "avvisadlindrig": [boolean],
      "avvisadgrov": [boolean],
      "varnad": [boolean],
      "ansvarig": [boolean]
    }
    ```

*   **Field Descriptions:**
    *   `matchlagledareid`: Unique identifier for the team official.
    *   `lagrollid`: Role ID of the team official.
    *   `avvisadmatchminut`: Minute when the official was dismissed.
    *   `avvisadlindrig`: Boolean indicating a minor dismissal.
    *   `avvisadgrov`: Boolean indicating a severe dismissal.
    *   `varnad`: Boolean indicating if the official was cautioned.
    *   `ansvarig`: Boolean possibly indicating if the official is the primary responsible person.

*   **Removing Disciplinary Actions:** To remove a disciplinary action, send a request with all boolean values set to `false` and `avvisadmatchminut` set to `0`.

*   **Response:** The endpoint responds with `{"d":null}` upon successful submission.


### Python Script Usage (`fogis_reporter.py`)

... (Detailed instructions on how to use `fogis_reporter.py` as outlined in the previous response) ...

### Code Structure Overview

... (Brief overview of Python functions and their purpose as outlined in the previous response) ...

### Limitations and Known Issues

*   **Basic Error Handling:**  Error handling is basic. More robust error handling, logging, and retry mechanisms are needed for production use.
*   **Input Validation:** Input validation is basic. More comprehensive validation is needed to prevent errors.
*   **Assumptions about `matchdeltagareid`:** The script currently sets `matchdeltagareid` to 0 as it's not available in the XML team sheet.  This might need further investigation or refinement.
*   **API Rate Limits:**  The script does not currently handle API rate limits. Rate limiting might occur if many events are reported in quick succession.
*   **No Match Result Editing/Deletion:** The script currently only supports creating and deleting match events and reporting match results, but not editing existing events or editing/deleting match results.
*   **Limited Event Types:**  Currently supports a limited set of event types (goals, penalties, cards, substitutions).  Needs to be extended to support all documented event types.

## Development

### Code Quality Tools

This project uses several tools to maintain code quality:

#### Linting with Flake8

We use Flake8 with several plugins to enforce code style and catch potential issues:

```bash
# Run flake8 on the codebase
flake8
```

The configuration is in the `.flake8` file and includes:
- Line length of 88 characters (matching Black's default)
- Google import style
- Google docstring convention
- Various plugins for additional checks

#### Type Checking with MyPy

We use MyPy in strict mode to ensure proper type annotations throughout the codebase:

```bash
# Run mypy on the codebase
mypy .
```

The configuration is in the `mypy.ini` file and enforces strict type checking.

#### Pre-commit Hooks

We use pre-commit to automatically run checks before each commit:

```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

## Features

### Smart Goal Reporting

The application includes a streamlined goal reporting system that makes it faster and easier to record goals:

* **Single Input Point**: Enter a jersey number directly to record a regular goal by that player
* **Special Goal Types**: Use single-letter codes to access different goal types:
  * `r` = Regular Goal (same as entering jersey number)
  * `h` = Header Goal
  * `c` = Corner Goal
  * `f` = Free Kick Goal
  * `o` = Own Goal
  * `p` = Penalty Goal

**Example Usage:**
* Enter `10` to record a regular goal by player #10
* Enter `p` then `7` to record a penalty goal by player #7
* Enter `o` then `3` to record an own goal by player #3

### Smart Time Control Event Detection

The application includes intelligent timestamp-based detection for time control events:

* **Automatic Event Type Detection**: Simply enter a timestamp (minute) and the system automatically determines if it's a period start, period end, or game end based on the match structure
* **Match Structure Awareness**: The system knows the number of periods, period lengths, and extra time settings for the match
* **Visual Timeline**: Displays all valid timestamps for the match with clear indications of what each timestamp represents
* **Stoppage Time Support**: Handles stoppage time notation (e.g., 45+2, 90+3)

**Example Usage:**
* Enter `45` to record the end of the first half
* Enter `90` to record the end of the match
* Enter `1` to record the start of the first period
* Enter `46` to record the start of the second half

### Other Features

* Interactive menu system for reporting various event types
* Support for reporting cards, substitutions, and other match events
* Match result reporting with verification
* Event table display showing current match state

### Future Enhancements (Roadmap)

*   Implement support for all documented match event types.
*   Implement match result editing/deletion.
*   Enhance error handling and logging.
*   Improve input validation.
*   Create a more user-friendly interface (even text-based menus).
*   Explore voice input integration for live event reporting.
*   Investigate and handle API rate limits.
*   Add more comprehensive test coverage.
*   ... (Add other potential features) ...

### Disclaimer

**This script is an unofficial tool and is not endorsed or supported by the Swedish Football Association (FOGIS). Use it at your own risk. The FOGIS API may change without notice, which could break this script. Always comply with the FOGIS API terms of service and usage guidelines.**
