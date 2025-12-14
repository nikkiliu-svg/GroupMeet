# Final Project Proposal: GroupMeet

**Team Name**: GroupMeet 
**Submission Date**: 11/13/2025  
**GitHub Organization**: https://github.com/orgs/GroupMeet/repositories

---

## Team Information

### Team Members

| Name | PennKey | Primary Role(s) | Secondary Skills |
|------|---------|----------------|------------------|
| Alexander Mehta | amehta26 | [e.g., Frontend Dev, UI/UX] | [e.g., Python, Data Analysis] |
| Brandon Yan | bdonyan | Backend Dev, API Integration | Database Design |
| Connor Cummings | connorcc | [e.g., QC Module, Data Pipeline] | [e.g., Statistics, ML] |
| Nikki Liu | nikkiliu | [e.g., Aggregation, Analysis] | Python, Data Analysis, Visualization |

### Team Skills Inventory

**Skills we have:**
- Project Management & Outreach: Alexander Mehta/amehta26
- Database design and Backend Dev: Brandon Yan/bdonyan
- Statistical Analysis & ML: Connor Cummings/connorcc
- Python scripting & Data Viz: Nikki Liu/nikkiliu

**Skills we need to learn/acquire:**
- **Penn CAS/SSO Integration**: Adapting the `cas-flask-demo` logic to authenticate users and retrieve PennKeys securely - [Nikki will learn it]
- Simple data storage (Firebase or Google Sheets API): Needed to store form submissions cleanly and safely - Brandon will lead.
- Basic engagement tracking: Needed to measure match completion - Nikki will learn it.
- Email automation (SendGrid/SMTP): Needed to send match results - Alexander will learn it.

**External resources we might need:**
- `penn-classlist-scraper`: Tool to extract class lists for enrollment QC.
- `cas-flask-demo`: Reference repository for implementing Penn Single Sign-On.
- SMTP Server/Email API: SendGrid or university mail relay.

### Team Availability for TA Meetings

**Week of [Date]:**

_List all time slots when the ENTIRE team can meet with a TA. Use Eastern Time. Format: Day, Time-Time_

- Monday: [e.g., 2:00 PM - 4:00 PM, 6:00 PM - 8:00 PM]
- Tuesday: [e.g., 10:00 AM - 12:00 PM]
- Wednesday: [e.g., 3:00 PM - 5:00 PM]
- Thursday: [Not available]
- Friday: [e.g., 1:00 PM - 3:00 PM]

**Preferred meeting duration**: [30 min / 45 min / 60 min]

**Meeting format preference**: Zoom

**Primary contact for scheduling**: [Name and email]

---

## Project Overview

### Project Connection to Round 4

**Round 4 Decision**: PIVOTING

**Original idea from**: Instructor-proposed project

**How the idea evolved**: 
In Rounds 1–3 I worked on TerraTruth, an ambitious humanitarian mapping project that combined geospatial pipelines, AI pre-filtering, and volunteer crowdsourcing. After seeing the viability scores and feedback, I pivoted in Round 4 to GroupMeet, an instructor idea with a much tighter scope and a directly testable crowd loop. For the final proposal, we further narrowed GroupMeet to a single-course pilot with a simple form-based matcher and lightweight feedback survey so we can validate the matching loop end-to-end within one semester.

### Problem Statement

Penn students in medium and large classes often struggle to find reliable, compatible study partners; existing tools like GroupMe, Discord, and ad-hoc Piazza posts are noisy, unstructured, and don’t account for schedule constraints or working styles. As a result, many students either work alone or end up in ineffective groups, which hurts learning outcomes and sense of belonging in the course. GroupMeet addresses this by collecting structured data about course enrollment, availability, and study preferences, then using crowdsourced feedback on each match to iteratively improve future group formation.

### One-Sentence Pitch

GroupMeet is a lightweight web platform that matches Penn students into study groups based on class, availability, and study preferences, then uses quick feedback surveys to continuously improve match quality.

### Target Users

**End Users**: Penn students enrolled in medium-to-large lecture courses who want better-matched study groups.

**Crowd Workers**: The same Penn students, acting as the crowd by submitting their course/availability information and later rating the quality of their study groups via short feedback forms.

**Scale**: For a successful demo we aim for ~30–40 student participants total, with at least 25 unique form submissions, 8–12 study groups formed, and 20+ feedback responses across one or two pilot courses.

### Project Type

- [ ] Human computation algorithm
- [ ] Social science experiment with the crowd
- [X] Tool for crowdsourcing (requesters or workers)
- [ ] Business idea using crowdsourcing
- [ ] Other: [specify]

---

## System Architecture


### Flow Diagram

**Flow diagram location**: 
![](ArchDiagram.png)

Your flow diagram MUST clearly show:
- [X] Where/when the crowd touches the data
- [X] Your quality control module
- [X] Your aggregation module
- [X] Data flow between components
- [X] What happens before crowd involvement
- [X] What happens after crowd contribution


### Major System Components

| Component | Description | Points | Owner(s) | Dependencies |
|-----------|-------------|--------|----------|--------------|
| **C1. Auth & QC Service** | Flask endpoints that handle CAS login, maintain sessions, and run enrollment/QC checks before accepting profiles. | 4 | Connor, Nikki | Roster ingestion done; CAS credentials configured |
| **C2. Intake & Feedback Frontend** | React UI for signup (preferences form) and post-match feedback form, wired to backend via REST. | 3 | Brandon | Auth endpoints available; basic API contract agreed upon |
| **C3. Matching / Aggregation Engine** | Batch script/module that reads validated profiles, computes compatibility, and forms groups of 3–5 with scores. | 4 | Nikki | QC-validated profile data in Firebase; schema stable |
| **C4. Notification & Email Utility** | Shared utility that formats and sends match emails and follow-up feedback emails via SendGrid or SMTP. | 3 | Alexander | Group assignments available; SMTP/SendGrid configured |
| **C5. Admin Dashboard & Analytics** | Lightweight dashboard to inspect participation, group structures, and satisfaction metrics; supports CSV export. | 3 | Alexander, Connor | Matching + feedback data available; aggregation schema finalized |

**Total Points**: 4 + 3 + 4 + 3 + 3 = **17 points**

**Point allocation rationale**:  
- **C1** and **C3** are the most technically involved: they touch security, data integrity, and the core crowdsourcing logic, hence 4 points each.  
- **C2**, **C4**, and **C5** are smaller but still non-trivial integrations that involve UI work, external APIs, and data visualization, hence 3 points each.  
- The distribution keeps the workload balanced and reflects where most engineering complexity and risk lie (auth + matching).


### Detailed Workflow

_Step-by-step description of how your system works from start to finish_

1. **Professor Setup**: Instructor provides course ID (e.g., CIS 1200); System scrapes/imports the class list using `penn-classlist-scraper`.
2. **Student Login (Authentication)**: Student visits the GroupMeet web app and clicks "Login with PennKey." The system redirects them to Penn's official CAS login page.
3. **Identity Verification**: Upon successful login, Penn CAS redirects back to our app with the student's `pennkey`. The app creates a secure session for this user.
4. **Preference Input**: The authenticated student fills out the preference form. The system automatically attaches their `pennkey` to the submission (preventing spoofing).
5. **QC Processing**: System validates that the authenticated `pennkey` exists in the imported class roster. If valid, the data is accepted.
6. **Aggregation (Matching)**: At the deadline, the script clusters students into groups of 3-5 based on compatibility scores.
7. **Distribution**: The System emails the formed groups, introducing them and providing a "First Meeting Agenda" template.
8. **Feedback**: 5 days later, students receive a "Rate your Group" link.

## Human vs. Automated Tasks

| Task | Performed By | Justification |
|------|--------------|---------------|
| Filling out course, availability, and study preference form | **Human (student)** | Only the student knows their real schedule constraints, working style, and goals; this requires subjective self-report. |
| Verifying enrollment and PennKey authenticity | **Automated (QC module)** | Given CAS assertions and roster data, enrollment checks are a straightforward database lookup and rules-based validation. |
| Forming study groups from validated profiles | **Automated (aggregation module)** | Grouping can be done by deterministic algorithms/heuristics that maximize compatibility based on structured features. |
| Rating group quality and giving feedback | **Human (student)** | Perceived group quality, whether meetings occurred, and subjective satisfaction cannot be reliably inferred by an algorithm. |

---

## Quality Control Module

### QC Strategy Overview

Our QC strategy relies on **Institutional Authentication (SSO)** combined with **Enrollment Verification**. By integrating Penn CAS (Central Authentication Service), we eliminate the risk of fake users or external spammers. We then validate that the authenticated PennKey is actually enrolled in the target course using official rosters.

### Specific QC Mechanisms

**Primary mechanism**: **Penn SSO + Roster Cross-reference**

**Implementation details**:
- Input format: Authenticated Session Data (`pennkey` from CAS) + Course Selection.
- Processing: 
  1. Verify CAS ticket validity via Penn's servers.
  2. Check `if session['pennkey'] in class_roster_list`.
  3. Check `if session['pennkey'] not in already_matched`.
- Output format: Boolean `is_valid` + Access Token.
- Threshold for acceptance: Valid CAS login AND presence on class list.

**Additional mechanisms**:
- [ ] **Attention checks**: Included in the form to verify availability.
- [X] **Reputation system**: Tracking "ghosting" behavior tied to the persistent PennKey identity.

### QC Module Code Plan

**Location in repo**: `src/qc/quality_control.py` (or a similar path, e.g., `backend/qc/quality_control.py`)

**Key functions/classes** (suggested):

1. `validate_session(request) -> str | None`  
   - **Purpose**: Validate the CAS ticket / session cookie and return the authenticated `pennkey` or `None` if invalid.

2. `check_enrollment(pennkey: str, course_id: str) -> bool`  
   - **Purpose**: Check if `pennkey` appears in the roster for `course_id`, using roster data loaded at startup or from Firebase.

3. `check_eligibility(pennkey: str, course_id: str) -> tuple[bool, str | None]`  
   - **Purpose**: Enforce additional rules such as “not already matched,” “not opted out,” and return `(is_ok, error_code)`.

4. `sanitize_form_payload(raw_payload: dict) -> dict`  
   - **Purpose**: Strip unexpected fields, normalize availability and preference fields, and enforce type/format constraints.

5. `qc_intake_submission(session, raw_payload) -> dict`  
   - **Purpose**: Orchestrator function called by the Flask route:
     - Grabs `pennkey` from session (via `validate_session`).  
     - Runs `check_enrollment` and `check_eligibility`.  
     - Calls `sanitize_form_payload` if all checks pass.  
     - Writes sanitized data to Firebase under `validated_profiles`.  
     - Returns a standard QC response object.

**Input data format** (from intake endpoint):

```json
{
  "course": "CIS1200",
  "availability": ["Mon_PM", "Tue_AM", "Thu_PM"],
  "study_style": "collaborative",
  "goal": "Problem sets",
  "other_notes": "Prefer in-person on campus"
}

**Output data format**:

{
  "is_valid": true,
  "error_code": null,
  "sanitized_data": {
    "pennkey": "amehta26",
    "course": "CIS1200",
    "availability": ["Mon_PM", "Tue_AM", "Thu_PM"],
    "study_style": "collaborative",
    "goal": "Problem sets",
    "timestamp": "2025-11-13T10:00:00Z"
  }
}

### on failure: 

{
  "is_valid": false,
  "error_code": "NOT_ENROLLED",
  "sanitized_data": null
}


**Sample scenario**:
_Walk through a concrete example of your QC module in action_

[Example: "Worker A labels image as 'cat', Worker B labels as 'dog', Worker C labels as 'cat'. QC module applies majority voting, outputs 'cat' with confidence 0.67, flags disagreement for potential review."]

---

## Aggregation Module

### Aggregation Strategy Overview

Our aggregation problem is **group formation**, not majority voting. The goal is to place students into groups of 3–5 that:

- Share at least one overlapping availability block.  
- Have compatible study styles and goals.  
- Avoid leaving large numbers of students unmatched.

We treat each validated student profile as a feature vector:

- Categorical: `study_style`, `goal`, maybe `experience_level`.  
- Multi-label: `availability` (list of time blocks).  
- Course: `course` (for now mostly a single course, but design supports multiple).

We then define a **pairwise compatibility score** that combines:

1. **Availability overlap score**: fraction or count of shared time blocks.  
2. **Preference similarity score**: 1 if preferences match, 0.5 if “compatible”, 0 otherwise.  
3. **Optional weightings**: e.g., give 70% weight to availability and 30% to preferences.

The aggregation engine uses these scores to construct groups via a simple heuristic:

1. For each course, build a compatibility graph where nodes are students and edge weights are compatibility scores.  
2. Iteratively:
   - Pick the unmatched student with the highest average compatibility to others.  
   - Form a group by greedily adding the best-matching students until the group size reaches 3–5.  
   - Remove those students from the unmatched pool and repeat.

This gives a clear, explainable baseline. If time permits, we can layer in a more advanced clustering method (e.g., k-medoids or constrained clustering) for comparison.

---

### Aggregation Method

**Primary method**: **Greedy compatibility-based grouping**

**Implementation details**:

- **Input format**: List of QC-validated student objects for a given course:

```json
[
  {
    "pennkey": "amehta26",
    "course": "CIS1200",
    "availability": ["Mon_PM", "Wed_PM"],
    "study_style": "collaborative",
    "goal": "Problem sets"
  },
  {
    "pennkey": "connorcc",
    "course": "CIS1200",
    "availability": ["Mon_PM", "Thu_PM"],
    "study_style": "collaborative",
    "goal": "Problem sets"
  }
]

**Output data format**:
```json
{
  "group_id": "CIS1200-001",
  "course": "CIS1200",
  "members": ["amehta26", "connorcc", "bdonyan"],
  "meeting_slot": "Mon_PM",
  "avg_compat": 0.87,
  "created_at": "2025-11-22T12:00:00Z"
}

```

**Sample scenario**:

Suppose 12 validated students submit profiles for CIS1200. Each provides availability (e.g., Mon_PM, Tue_AM), study style (collaborative vs. independent), and goals (problem sets vs. concept review).

The aggregation module computes pairwise compatibility across all 12 students based on overlapping availability and matching preferences. It then forms groups greedily:

- Group 1: Students with shared Mon_PM availability and similar “collaborative + problem-set” preferences → avg_compat = 0.86  
- Group 2: Students who overlap on Tue_AM with mixed but compatible styles → avg_compat = 0.78  
- Group 3: Last four students overlap best on Thu_PM → avg_compat = 0.81  

The module outputs three groups of size 3–4, each with a recommended meeting slot and compatibility score.

### Integration: QC ↔ Aggregation

**How do these modules interact?**

QC always runs **before** aggregation. Every intake submission first passes through the QC module, which:

1. Confirms the user’s CAS-authenticated `pennkey`.
2. Verifies enrollment against the course roster.
3. Checks basic eligibility (not already matched / not opted out).
4. Sanitizes and normalizes the payload.

Only after these steps does the profile get written to the `validated_profiles/{course_id}/{pennkey}` collection in Firebase.  

The **aggregation module** never touches raw form data; it only reads from `validated_profiles`. This guarantees that:

- Every profile in the matching pool corresponds to a real Penn student in the course.
- Each student appears at most once per course in the matching run.
- Downstream matching logic can assume a consistent schema.

In other words:

> **Raw Form Submissions → QC Module → Validated Profiles → Aggregation / Matching**

**Data flow diagram** (conceptual, text-only)

```text
Form Submission
    ↓
QC Module (CAS validation + roster + eligibility + sanitization)
    ↓ (only if valid)
Firebase: validated_profiles/{course_id}/{pennkey}
    ↓
Aggregation / Matching Engine
    ↓
Firebase: groups/{course_id}/{group_id}
    ↓
Notification + Feedback
```
---

## User Interface & Mockups

### Interfaces Required

_You need mockups for ALL user-facing interfaces_

**For Crowd Workers:**
- [ ] Task interface / HIT design
- [ ] Instructions page
- [ ] Training/qualification interface (if applicable)

**For End Users:**
- [ ] Main interface
- [ ] Results display
- [ ] Any configuration/input screens

**For Administrators (your team):**
- [ ] Dashboard/monitoring
- [ ] Data management interface

### Mockup Details

**Mockup location**: [e.g., `docs/mockups/` folder or links to Figma/Marvel/etc.]

**For each interface, describe**:

#### Interface 1: [Name]
- **User type**: [Crowd worker / End user / Admin]
- **Purpose**: [What is this interface for?]
- **Key elements**: [What must be visible/interactive?]
- **Mockup file**: [filename or link]
- **Notes**: [Any important design decisions or requirements]

#### Interface 2: [Name]
- **User type**: [Crowd worker / End user / Admin]
- **Purpose**: [What is this interface for?]
- **Key elements**: [What must be visible/interactive?]
- **Mockup file**: [filename or link]
- **Notes**: [Any important design decisions or requirements]

_Continue for all interfaces..._

### Task Design (for crowd workers)

**If using MTurk or similar platform:**

**HIT title**: [Your HIT title]

**HIT description**: [What workers will see in the HIT listing]

**Task instructions**: 
_Write the actual instructions workers will see. Be specific and clear._

[Your instructions here]

**Example task**:
[Show workers exactly what one complete task looks like]

**Estimated time per task**: [X minutes]

**Payment per task**: $[amount]

**Number of tasks per HIT**: [number]

**Qualifications required**: [e.g., >95% approval rate, >100 HITs, US location]

---
## Technical Stack

### Technologies

**Frontend**: React (Simple, responsive form for student intake)

**Backend**: Python (Flask) - Chosen for ease of writing matching logic and integrating the `cas-flask-demo` authentication routes.

**Authentication**: Penn CAS (Central Authentication Service) via `xmltodict` and `requests`.

**Database**: Firebase (Real-time database, handles JSON documents easily).

**Crowdsourcing Platform**: Custom Web App (recruitment via Class Lists/Direct Link).

**ML/AI Tools**: scikit-learn (for clustering/similarity scoring).

**Hosting/Deployment**: Vercel (Frontend) + Render or Heroku (Backend).

**Other tools**: 
- `penn-classlist-scraper` (for enrollment verification)
- SendGrid (for automated emails)

### Repository Structure

**Current structure**:

```
group-meet/
├── README.md
├── docs/
│   ├── flow-diagram.pdf
│   ├── mockups/
│   └── ...
├── src/
│   ├── qc/
│   ├── aggregation/
│   └── ...
├── data/
│   ├── raw/
│   ├── sample-qc-input/
│   ├── sample-qc-output/
│   ├── sample-agg-input/
│   └── sample-agg-output/
└── utils/
...
```

**Explain any deviations**: We added a `utils/` folder for the email notification logic, as it is a shared resource between modules but not strictly QC or Aggregation.

---

## Data Management

### Input Data

**Source**: Web form submissions (React frontend) and Official Class Lists (Scraped/CSV).

**Format**: JSON for form data; CSV for class lists.

**Sample data location**: `data/raw/`

**Sample data description**:
Synthetic profiles of 50 students in CIS 1200, containing PennKeys, emails, availability blocks (Mon-Fri, AM/PM), and study style preferences.

**How much data do you need?**
- For testing/development: ~50 synthetic profiles.
- For your final demo/analysis: 25-40 real student submissions.

**Data collection plan**:
We will open the form immediately after Week 1 recruitment emails are sent. Data is collected in real-time via the web app and stored in Firebase.

### QC Module Data

**Input location**: `data/sample-qc-input/`

**Input format**:
```
{
  "pennkey": "amehta26",
  "email": "amehta26@upenn.edu",
  "course": "CIS1200",
  "timestamp": "2025-11-13T10:00:00",
  "availability": ["Mon_PM", "Tue_AM"],
  "goal": "Active Learning"
}
```

**Output location**: `data/sample-qc-output/`

**Output format**:
```
{
  "is_valid": true,
  "error_code": null,
  "sanitized_data": { ... }
}
```

**Sample scenario documentation**:
Included in data/README.md: Explains how the validator checks the course field against the loaded CSV roster.

### Aggregation Module Data

**Input location**: `data/sample-agg-input/`

**Input format**:
```
[
  {"id": "user1", "avail": ["Mon_PM"], "style": "visual", "goal": "problems"},
  {"id": "user2", "avail": ["Mon_PM", "Tue_AM"], "style": "textual", "goal": "problems"}
]
```

**Output location**: `data/sample-agg-output/`

**Output format**:
```
[
  {
    "group_id": 101, 
    "members": ["user1", "user2", "user5"], 
    "avg_compat": 0.85,
    "meeting_time": "Mon_PM"
  }
]
```

**Sample scenario documentation**:
Included in data/README.md: details the clustering logic used to group user1 and user2 based on their shared "Mon_PM" slot.

### Data Dependencies

**Does your QC module output feed into your aggregation module?**
Yes. The Aggregation module strictly requires a list of validated student objects. It cannot process raw input.

**Data flow between modules**:
Raw Form Data (Frontend) → QC Module (Verifies Enrollment) → Validated Data Lake (Firebase) → Aggregation Module (Batch Process) → Group Assignments → Email Service.

---

## Crowd Recruitment & Management

### Recruitment Strategy

**Where will workers come from?**
- Professor Partnership: We are emailing professors of CIS 1200, MATH 1400, CIS 5450, and CIS 5480 to distribute the link.

- Direct Outreach: If professor partnership is slow, we will post on r/UPenn, Penn Clubs, and large course GroupMe chats.

**How will you reach them?**
"Need a study group for the Final? Fill out this 2-min form to get matched based on your schedule and learning style."

We will post on ED and show up to the begining of lectures to pitch our product.

**When will you recruit?**
Starting Wednesday, Nov 19th (Week 1), immediately after the form is live.

### Worker Incentives

**Compensation model**: 
- Payment per task: $0.00 (Intrinsic Value)
- Estimated time per task: 2 minutes
- Effective hourly rate: N/A

**Or alternative incentive**: The incentive is the utility of the service: finding a compatible study group for homework or final exams without the social friction of asking around.

**Justification**: Students have a strong immediate need (upcoming finals) and high friction in current solutions (spamming chats). The value of a "good match" exceeds the 2 minutes of effort required.

### Scale Requirements

**For MVP/Demo**:
- Minimum workers needed: 25 students
- Minimum tasks completed: 25 form submissions, 2 groups created
- Timeline: By Nov 28th (Thanksgiving Break)

**For Full Analysis**:
- Target workers: 40+ students
- Target tasks: 40+ form submissions, 5 groups created
- Timeline: By Dec 8th (Final Exam Period)

### Backup Plan

**If recruitment fails or is insufficient**:
- [ ] Use MTurk/paid workers (budget: $[amount])
- [ ] Simplify task to require fewer workers
- [ ] Use simulated/synthetic data
- [ X ] Other: We will pivot to a "General Productivity" or "Co-working" pool (not class-specific) and recruit from our own social networks/clubs to ensure we have enough humans to validate the matching algorithm, even if the "class roster" aspect is simulated. This will involve going beyond the penn community likely.

---

## Project Milestones & Timeline

### Week-by-Week Plan

**Week 1 (Dates: [11/13 - 11/20])**
- Milestone: MVP Launch & Initial Recruitment
- Tasks:
  - [ ] Build and Deploy Intake Form (React/Firebase) - Brandon
  - [ ] Develop QC Validator & Scraper Integration - Connor
  - [ ] Secure 1 Professor/Class Partner & Send Announcements - Alexander
  - [] Port `cas-flask-demo` code into backend to handle login/logout routes - Nikki
- Deliverable: Live URL for signups; First batch of data entering the system.

**Week 2 (Dates: [11/21 - 11/27])**
- Milestone: Matching Pilot & Result Distribution
- Tasks:
  - [ ] Finalize Aggregation Script (Clustering Logic) - Nikki
  - [ ] Run Matching Batch on Week 1 Data - Connor
  - [ ] Create Group Success Monitoring Strategy - Brandon
  - [ ] Distribute Results via Automated Email - Alexander
- Deliverable: [What will be done/ready by end of week]

**Week 3 (Dates: [11/28 - 12/04])**
- Milestone: Feedback Loop & Admin Dashboard
- Tasks:
  - [ ] Send "Rate Your Group" Feedback Survey - Brandon
  - [ ] Build Admin Dashboard (CSV Export) for Instructors - Alexander
  - [ ] Analyze Feedback Data vs. Matching Score - Connor
- Deliverable: Final Project Report, Dashboard Demo, and Analysis of Match Quality.

**Week 4 (Dates: [12/05 - 12/11])**
- Milestone: Final Presentation Prep and Overview
- Tasks:
  - [ ] Compile all metrics (signup rate, match success, satisfaction) - Nikki
  - [ ] Polish Codebase and Documentation - All
  - [ ] Record Demo Video - All
- Deliverable: Final Presentation and Code Submission.


### Critical Path

**Blocking dependencies** (what MUST be done before other work can proceed):
1. Intake Form must be live before Recruitment can effectively start.

2. Recruitment must reach N=20 participants before Matching Script can produce meaningful clusters.

3. Matching must occur before Feedback Surveys can be sent.

**Parallel work** (what can be done simultaneously):
- Nikki can build the Aggregation/Matching Logic while Brandon builds the Frontend Form.
- Connor can build the QC/Scraper while Alexander handles Recruitment Outreach.

**Integration points** (when pieces must come together):
- Nov 20: Frontend (Form) data must successfully feed into the QC module.
- Nov 21: Validated data must be ready for the Aggregation script to run the first batch.

---

## Risk Management

### Technical Risks

**Risk 1**: Matching logic produces uneven or low-quality groups (e.g., leftover students, conflicting availability).
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: Keep the form extremely constrained (course, coarse availability blocks, one study preference) and test the script with small synthetic datasets before real signups.
- **Backup plan**: Allow flexible group sizes (3–6), or place unmatched students into a secondary “overflow” round instead of forcing bad matches.

**Risk 2**: Email distribution script fails or messages are flagged by university spam filters.
- **Likelihood**: Low
- **Impact**: High
- **Mitigation**: Test email-sending with internal emails first (team + friends) and send messages in small batches to avoid rate limits.
- **Backup plan**: Provide each student with a unique link to a results dashboard instead of sending the actual match details via email.

### Crowd-Related Risks

**Risk 1**: Not enough students sign up to form viable groups if no professor agrees to distribute the form.
- **Likelihood**: [Low / Medium / High]
- **Impact**: [Low / Medium / High]
- **Mitigation**: [How you'll prevent or address it]
- **Backup plan**: [What you'll do if mitigation fails]

**Risk 2**: Low-quality responses or participants not following through (ghosting their assigned group).
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: Make the form very short and specific (e.g. max 3-5 questions, including “problem sets vs. concept review”) to increase match compatibility and reduce friction.
- **Backup plan**: Send a quick confirmation (“Still want to be matched? Yes/No”) before running the matching script to filter out passive or uncommitted participants.

### Resource Risks

**Risk 1**: Running out of time because the MVP requires more implementation effort than expected.
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation**: Keep the scope tightly limited to the essentials (form, matching script, results email) and avoid adding optional features until the core pipeline works.
- **Backup plan**: If timing slips, simplify further by using a Google Form and a lightweight manual matching script to ensure the Week 1 and Week 2 tests still happen.

---

## Evaluation Plan

### What You'll Measure

**Primary metrics**:
1. Signup Rate: Percentage of students in the target class who complete the preference form. How measured: Form submissions ÷ estimated class size. Target: ≥ 15% of a large intro course (e.g., CIS 1200). 
2. Match Completion Rate: Percentage of matched students who open their results email/dashboard. How measured: Email open rates + unique page visits. Target: ≥ 70% engagement.
3. Group Quality Rating: Students’ self-reported satisfaction with their group. How measured: 1–5 star rating submitted 5 days after matching. Target: Average rating ≥ 3.5 stars.

**Secondary metrics**:
1. Form Completion Time: Measured automatically by timestamp difference; used to confirm form is short and frictionless.
2. Group Dropoff Indicators: Counts of participants who report their group never met or who request to be rematched.

### Analysis Approach

**What questions will your analysis answer?**
1. Was recruitment through professors sufficient to generate meaningful participation?
2. Did the simple matching rules (course + availability + preference) produce functional study groups?
3. What user characteristics (e.g., availability type, study preference) correlate with higher satisfaction?

**What comparisons will you make?**
- [ ] Compare crowd vs. expert performance
- [ ] Compare crowd vs. automated baseline
- [✓] Compare different QC methods
- [✓] Compare different aggregation methods
- [✓] Analyze cost/quality tradeoffs
- [ ] Other: [specify]

**Data you'll collect for analysis**:
- Form submissions: Needed to evaluate signup rate, preference distribution, and matching logic performance.
- Match engagement data: Email open rates, click-throughs, and page visits to measure completion and participation.
- Follow-up ratings: Necessary to quantify group quality and evaluate whether matching rules worked.

**Analysis methods**:
- Descriptive statistics (means, proportions) for signup rate, engagement, and ratings.
- Visualizations: bar charts of group quality ratings mainly; funnel charts of user dropoff; heatmaps of availability overlap.
- Simple correlation analysis between study preferences or availability types and satisfaction scores.
- Qualitative analysis of optional free-text feedback to identify failure cases or improvement opportunities.

---

## Ethical Considerations

### Worker Treatment

**Fair compensation**: Not applicable in the traditional “crowd worker” sense - students derive direct value (study partners) rather than monetary compensation.

**Informed consent**: The form and recruitment email clearly state the project purpose, what information is collected, and how it will be used (to create effective study groups only).

**Rejection policy**: No work is “rejected”—all submissions are accepted unless the form is incomplete or empty. Students may be notified if they cannot be matched due to incompatible availability.

### Data Ethics

**Privacy**: Only group members see each other’s emails; no sensitive data (e.g., grades, IDs) is collected. All data is stored in secure, access-controlled files.

**Consent**: Consent is obtained explicitly through the form, which states that participation is voluntary and used solely for this 2-week academic pilot.

**Data storage**: Stored in secure Google Drive or Firebase with limited access; deleted at the end of the project or anonymized for analysis.

### Potential Harms

**Could your project be misused?**: Minimal risk; the most plausible misuse is sharing student emails beyond intended group members.

**Could it cause harm?**: Potential discomfort if a student is matched into an incompatible or inactive group.

**Mitigation**: Limit shared information to first/last name and email; allow students to opt out anytime; run a confirmation step before matching; and avoid storing unnecessary data.

---

## Documentation Standards

### Code Documentation

**Each module must include**:
- Docstrings for all functions/classes
- README in module directory
- Example usage
- Input/output format specifications

**Current documentation status**:
- [ ] QC module: Not yet documented
- [ ] Aggregation module: Not yet documented
- [ ] Other modules: [List status]

### Repository README

**Your main README.md must include**:
- [ ] Project overview and goals
- [ ] Setup instructions
- [ ] How to run the system
- [ ] Where to find QC and aggregation code
- [ ] Data format specifications
- [ ] Team member contacts
- [ ] License information

### Ongoing Documentation

**How will you keep documentation current?**
- Update docstrings whenever logic changes.
- Require that any new script or feature includes a README section before merging.
- Maintain a simple “Changelog” documenting weekly updates to matching rules or form schema.

---

## Questions for Teaching Staff

### Technical Questions

1. Are simple rule-based matching algorithms sufficient for this project, or do you expect experimentation with multiple aggregation methods?
2. Is there a recommended way to track email open/click metrics within course-allowed tools (Firebase, scripts, etc.)?
3. For collecting ratings, is it acceptable to use Google Forms, or must everything be integrated into the web app?

### Scope Questions

1. Is running a pilot on one large course enough to satisfy the crowdsourcing requirement?
2. How lightweight can the results dashboard be while still meeting course standards?
3. Is it acceptable if the feedback survey is optional due to time constraints?

### Resource Questions

1. Are there any free email-sending services you recommend that won’t get flagged by university spam filters?
2. Are there guidelines for acceptable recruitment channels if professor partnership fails?

### Other Concerns

- How strictly should we limit data retention after the project ends?
- Is it okay to anonymize ratings for analysis, or is identified data preferred?

---

## Commitment

**We commit to**:
- [ ] Building a working prototype with functional QC and aggregation modules
- [ ] Creating comprehensive documentation in our GitHub repository
- [ ] Recruiting and managing a real crowd (or simulated crowd)
- [ ] Collecting sufficient data for meaningful analysis
- [ ] Meeting project milestones on schedule
- [ ] Communicating proactively if we encounter blockers
- [ ] Treating crowd workers ethically and fairly

**Team signatures**:

- _________________________ [Name], [Date]
- _________________________ [Name], [Date]
- _________________________ [Name], [Date]
- Nikki Liu, 11/13/2025

---

## Submission Checklist

This submission **is a working document**. You may not have finalized all version (of the flow diagram, the sample data, etc.), which is **acceptable**.

Before submitting this proposal, verify you have:

- [ ] Completed all sections of this template
- [ ] Provided team availability for TA meetings
- [ ] Listed team skills and learning needs
- [ ] Included point values for all components (total 15-20)
- [ ] Described detailed implementation timeline
- [ ] Identified risks and mitigation strategies
- [ ] Had all team members review and sign

Then:

- [ ] Set up GitHub repository with required directory structure
- [ ] Prepared questions for teaching staff
- [ ] Created flow diagram showing QC and aggregation modules
- [ ] Created mockups for all user-facing interfaces
- [ ] Added sample input/output data for QC module
- [ ] Added sample input/output data for aggregation module

**Submission method**:
- **You are able to make multiple successive submission to iterate, complete this proposal.**
- Pull request to `ideation-fall-2025` repository, in `round5_final` folder
- Should be in the root of your GitHub organization

**Submission deadline**: Thursday, Nov. 13 at 11:59PM ET
