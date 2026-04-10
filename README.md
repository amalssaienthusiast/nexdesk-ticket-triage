---
title: Nexdesk Ticket Triage
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# NexDesk

I built this for the OpenEnv competition because I've worked IT helpdesk and know exactly how messy ticket triage can be in the real world.

The idea is simple: an AI agent learns to classify, route, and resolve IT tickets. But real helpdesks aren't just simple text classification problems. They have tight SLAs, sudden ticket surges, and frustrated users waiting for answers. I tried to build those realities into this environment. 

It's not perfect but it works well for the 4 tasks I defined.

## What makes this different

Instead of just checking if the agent picked the right category from a list, I added a few things that made debugging this a nightmare but makes the environment way more realistic:

* **SLA Time Pressure**: A ticket resolved in 5 minutes vs 55 minutes isn't the same. I added a penalty system that kicks in if the agent takes too long to decide. Speed matters.
* **Batch Surges**: Real outages don't wait for you to finish one ticket. Task 4 dumps 10 tickets at once in a simulated outage. The agent has to prioritize the critical ones first.
* **Call your shots**: Agents can optionally pass a confidence score. If they are well-calibrated (they know they are right), they get a bonus. If they are overconfident and wrong, they get penalized heavily. 

## The Tasks

I split it into 4 levels of difficulty:

1. `ticket_classify` (Easy)
Just look at a string and figure out priority and category.

2. `ticket_route` (Medium)
Classify it, but mostly figure out which specific team needs to handle it and what system is actually broken. This takes 2 steps.

3. `ticket_resolve` (Hard)
Full resolution pipeline. You have to route it, draft a response to the user, and write out actual resolution steps with estimated SLA hours. (Scoring the text response was tough, so I made a basic keyword coverage grader for it).

4. `crisis_surge` (Hard)
The batch outage scenario mentioned above. Drops 10 tickets on you at once.

## Baseline Results

I spent a weekend testing this with `Qwen/Qwen2.5-72B-Instruct` just to see if it was solvable.

- `ticket_classify`: ~0.85 (Pretty good at the basic stuff)
- `ticket_route`: ~0.78 (Routing to specific teams tripped it up sometimes)
- `ticket_resolve`: ~0.65 (Drafting good responses and steps is hard)
- `crisis_surge`: ~0.60 (It really struggles to prioritize under pressure)

Random guessing gets you around 0.15-0.25 max.

## Setup

If you want to run this yourself:

**With Docker (Easiest)**
```bash
docker build -t nexdesk .
docker run -p 7860:7860 nexdesk
```

**Local dev**
```bash
pip install -r requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

**Run my baseline script**
```bash
export HF_TOKEN=your_token
export ENV_BASE_URL=http://localhost:7860
python inference.py
```

## API

The main endpoints are exactly what you'd expect:
- `POST /reset` - start an episode `{"task": "ticket_classify"}`
- `POST /step` - take an action passing your `session_id`
- `GET /metrics` - see how much money the agent theoretically saved (this is just a rough calc based on some industry averages I found)

## Thoughts

This took way longer than I expected, mostly fighting with getting the deterministic grading to always stay strictly between 0 and 1 so the Meta validator would stop complaining. It's stable now.

Still working on a few edge cases, but the core engine is solid. Feel free to use it or break it.
