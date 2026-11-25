# StayWise AI: Clarifying Subjective Hotel Preferences

README prose word count: 795 words.

## 1. Project Overview and Status

StayWise AI is an interactive hotel recommendation prototype developed for Assignment 2 of Intelligent Interactive Systems at the University of Birmingham.

The project addresses ambiguity in subjective hotel preferences, particularly expressions such as "cheap" and "affordable". It uses adaptive clarification to resolve unclear budgets while avoiding unnecessary questions when preferences are already explicit.

### Implemented

- Conversational input and quick-response options.
- Rule-based preference extraction and adaptive clarification.
- Explicit budget confirmation and an optional suggested budget.
- Shared preference state between chat and filters.
- Hotel filtering, ranking and recommendation explanations.
- Hotel details, no-match recovery and editable feedback.
- Clear filters and full search reset.

### Simulated

- Conversational AI behaviour using rules and response templates.
- Eighteen fictional hotels across London, Birmingham and Manchester.
- Generated room illustrations rather than actual hotel photographs.

### Planned

A comparative user study examining clarification versus direct assumption, focusing on satisfaction, interaction effort and successful preference correction.

Live hotel availability, booking and learned language understanding are outside the current scope.

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| HTML | Interface structure |
| CSS | Layout and responsive styling |
| JavaScript | Conversation, clarification, state management and recommendation logic |
| JSON | Local hotel dataset |
| Python and Playwright | Automated browser testing |
| OpenAI Codex | AI-assisted development and testing |
| OpenAI image generation | Fictional hotel room illustrations |

The prototype runs entirely in the browser. No model API, application backend, API key or paid service is required.

## 3. Running the Prototype

Download or clone the repository and open `app/index.html` in a web browser. Keep the complete `app` folder together.

Alternatively, start a local static server from the project root:

```sh
python3 -m http.server 8765 --directory app
```

Open http://localhost:8765 in a browser.

Example requests:

- Find a hotel in Birmingham under £100 with breakfast.
- I want a cheap hotel in London.
- I want an affordable hotel in Manchester.

## 4. Project Structure

- `app/index.html` — main interface.
- `app/style.css` — layout and styling.
- `app/app.js` — interaction and recommendation logic.
- `app/hotels.json` — canonical hotel dataset.
- `app/hotels-data.js` — offline JavaScript data mirror.
- `app/assets/` — generated hotel room illustrations.
- `app/PHOTO_CREDITS.md` — image provenance.
- `tests/` — automated browser tests and dependencies.
- `docs/` — functional checks and image review records.
- `report/` — coursework report and interaction illustrations.

## 5. Development Record

The stages below summarise development completed before the first Git commit.

| Stage | Main decision or change | Reason and check |
|---|---|---|
| Project scope | Developed a working hotel recommendation prototype rather than conducting the original proposed user comparison. | Kept the project manageable while demonstrating the clarification interaction. |
| Clarification policy | Distinguished explicit budgets from subjective expressions. | Checked that clear requests proceed directly and ambiguous budgets trigger clarification. |
| Budget design | Replaced overlapping budget ranges with inclusive maximum prices and an optional £100 demonstration default. | Reduced boundary ambiguity and preserved user control over assumptions. |
| Preference management | Used shared state for chat and filters. | Checked that budget revisions preserve other selected preferences. |
| Recommendation logic | Applied strict filtering and deterministic ranking. | Checked constraints, ordering and explanations against the dataset. |
| Interface development | Added preference summaries, hotel details, feedback and no-match recovery. | Made system decisions visible and preferences easier to correct. |
| Clear filters correction (24 November 2026) | Preserved city, conversation and feedback while clearing other constraints and obsolete budget questions. | Checked updated results and confirmed that New search still performs a full reset. |
| Final review | Completed manual website inspection and revised the architecture diagram. | Reviewed the developed interaction and its representation in the report. |

## 6. Testing and Validation

The supplied automated test record contains 19 passing Chromium checks, including clarification, budget revision, filtering, ranking, feedback, reset and responsive layout.

Eighteen city and budget combinations were checked for recommendation consistency.

I also manually tested the prototype before submission.

Testing evidence:

- [Regression results](docs/REGRESSION_RESULTS.json)
- [Clear filters correction checks](docs/CLEAR_FILTERS_FIX_CHECKS.json)
- [Browser test script](tests/test_browser.py)

The automated test script uses Python, Playwright and Chromium. Its Chromium executable path is configured for Linux and may require adjustment on other operating systems.

These checks establish functional behaviour, not user satisfaction or the effectiveness of clarification compared with assumptions.

## 7. AI Assistance

OpenAI Codex assisted with implementation, interface development, automated testing and report preparation. OpenAI image generation was used to create the eighteen fictional room illustrations.

ChatGPT assisted with architecture diagram design and README revision. The architecture was simplified to distinguish implemented components, simulated behaviour and planned evaluation.

I reviewed the prototype through manual interaction and revised the architecture diagram for the report. Automated checks and manual inspection are distinguished from formal user evaluation.

## 8. Additional Files and Limitations

The coursework report is available in the `report/` folder. Image provenance is documented in `app/PHOTO_CREDITS.md`, with additional image records in `docs/`.

All hotel names, prices, ratings and facilities are fictional demonstration data. Generated images do not represent real properties.

The assistant uses supported input patterns rather than a trained language model. Complex requests may not be fully recognised. Feedback is stored locally in session state and does not train or personalise a model.

No formal user study has been conducted.
