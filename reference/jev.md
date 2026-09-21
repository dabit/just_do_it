# Jev operations

JDI asks **Jev** — TypeSafe's System One model — for typed judgments through five named
operations. Commands and roles call them **by name**; this file says what each one means, what it
sends, and what the caller does with the answer.

Jev is not a second agent. It returns a number, not prose and not a decision: a probability, a
chosen option, or a position on a described scale. It never sees a tool, never writes a file, and
never chooses JDI's next step. Every operation here is a role **narrowing a list it already has**
before doing the work it was always going to do.

Everything in this file is inert unless `jev.enabled` is `true`. With the default `false`, no
operation runs, nothing is sent anywhere, and no command says a word about it.

## The universal rules

1. **Jev narrows; it never decides.** An operation may reorder a list, flag a candidate, or
   pre-select one option from a set the caller already enumerated. It may never be the reason a
   step is skipped, a file is written, a tracker is updated, a commit is made, or a pull request is
   opened. Those remain the role's own judgment and the user's own approval.
2. **A low or absent answer means more work, never less.** When an answer is uncertain, the role
   does what it does with `jev.enabled: false` — reads every candidate, asks the user, works it out
   itself. Uncertainty widens the role's attention; it never narrows it.
3. **The caller enumerates the candidates.** Jev chooses among options it was given and cannot
   return one it was not. A missing candidate is a caller bug, not a model error — assemble the
   list in the workflow first, then ask.
4. **Capability is proven, not assumed.** Jev is available for a run only once a real request has
   come back with a real answer. A key that exists is not proof; the absence of an error is not
   proof.
5. **Announce a degradation once; say nothing when the feature is off.** `jev.enabled: false` is
   silent — nothing was skipped. A configured `true` that could not run is announced once, at the
   top of the run, and the run continues without Jev from there.
6. **Never send a secret, and never print the key.** State is assembled from the repository's own
   text. Pass the key by reference (`$TYPESAFE_API_KEY`, or `$(cat ~/.config/typesafe/api_key)`) —
   never paste its value into a command line, a file, a plan, or a commit.

## The degradation ladder

The **Butler** runs this ladder **once**, at step 0, before it delegates to anything. Take the
first rung that applies, say which one out loud, and treat the run as `jev.enabled: false` from
there on. Roles are never told to run the ladder themselves and never re-probe.

1. `jev.enabled` is `false` or absent → off, **silently**. Nothing was asked for.
2. No API key — neither `$TYPESAFE_API_KEY` in the environment nor a readable
   `~/.config/typesafe/api_key` → off, announced, with the one line that fixes it:
   `export TYPESAFE_API_KEY=...` (get a key at <https://typesafe.ai>).
3. No way to make an HTTPS request in this session → off, announced.
4. The probe request fails — 401, 422, 429, 5xx, a timeout, or anything that is not an answer →
   off, announced with the status. Do not retry past one backoff; a run that spends its time
   retrying an optional optimisation has already cost more than it saves.
5. The state an operation needs will not fit — Jev's budget is 64k tokens per request, of which
   **32k covers the state plus the longest single question** → that operation is skipped for the
   oversized input, announced, and the caller reads the candidates itself. Never truncate the state
   silently: a judgment made on half a document is worse than no judgment.

**Never degrade upward.** An operation that cannot run falls back to the role's own reading. It
never falls back to "assume the candidate is irrelevant", never to "skip the consumer sweep", and
never to a cheaper judgment nobody asked for. Dropping work because an optional model was
unavailable is a worse failure than not having asked.

**The probe is the first real operation.** There is no separate health check. The first J-op a run
performs is the probe: if it answers, Jev is available for the rest of the run; if it does not,
rung 4 fires and that operation falls back like any other.

## Making a request

One endpoint, one shape. `POST https://api.typesafe.ai/v1/systemone`, with
`Authorization: Bearer <key>` and `Content-Type: application/json`.

```bash
curl -sS -X POST https://api.typesafe.ai/v1/systemone \
  -H "Authorization: Bearer $TYPESAFE_API_KEY" \
  -H "Content-Type: application/json" \
  -d @request.json
```

The body carries `model` (always `jev-latest`), `state`, and a `questions` map whose keys you
choose. The answers come back under the same keys:

```json
{
  "model": "jev-1.13.0",
  "answers": {
    "covers": {
      "type": "score", "score": 2.52, "confidence": 0.52,
      "legend": {"0": "Irrelevant…", "3": "Required…"},
      "probabilities": {"0": 0.0, "1": 0.04, "2": 0.4, "3": 0.56}
    },
    "is_procedure": {"type": "noul", "noul": 0.14}
  },
  "usage": {"input_tokens": 526, "output_tokens": 36}
}
```

**The three question types.** Pick by what the answer *means*, not by how it will be displayed.

| Type | Returns | Use it for |
|---|---|---|
| `noul` | `noul`, a probability 0–1 | Does this condition hold? One per label when several may apply. |
| `choice` | `choice`, `probabilities`, `confidence` | Exactly one option from a set you listed (max 255). |
| `score` | `score`, `legend`, `probabilities`, `confidence` | A position on an ordered scale of 2–10 described levels. |

**Batch every question that shares a state into one request.** Questions are answered
independently and cannot see one another, so batching changes no answer — it only stops you paying
for the same state N times. Ask the speculative ones too; ignore the answers on branches you do not
take.

**Write levels as situations, not degrees.** "Broken, but a workaround exists" is a level;
"moderately severe" is not. A `score` is a probability-weighted position on the legend's number
line, so 2.52 means the answer sits between levels 2 and 3. To compare scores from different
questions, normalise by the top level number (`len(criteria) - 1`).

**Confidence is concentration, not correctness.** It says how tightly the probability sits on one
answer, and nothing about whether that answer is true. Read it with universal rule 2: below ~0.5,
treat the question as unanswered and do the work by hand.

**Keep four documented weaknesses out of the question.** Jev's own jaggedness notes name them, and
each has the same remedy — do that part in code:

- **Counting and arithmetic.** Tally in code; ask Jev about a condition, never for a total.
- **Ordering and comparison**, including dates and sequence numbers. Extract the values, compare
  them yourself. This is why **J4** does not ask whether a task depends on a later one.
- **Indirection.** No double negatives, no multi-hop reasoning. Name the state the question is
  about, directly and in one hop.
- **Irrelevant state.** Filter first and send only the fields the decision needs. A document's
  headings answer **J1** better than the document does, and they fit.

## J1 — Rank the candidate architecture docs

**Caller: the Researcher**, when `docs.path` holds more documents than the change plausibly needs.

The Researcher already lists the candidates; J1 orders them so the ones that constrain this change
are read first and in full.

- **State**: the change description, plus, **per document**, its path, its headings, and its
  opening paragraph. Never the whole file — that is rung 5 waiting to happen.
- **Question**: one `score` per document, always the same four levels, so the scores compare:
  *Irrelevant* (unrelated area), *Background* (same codebase, not this part), *Useful* (a system
  this change meets at its edges), *Required* (describes the exact area and constrains how the
  change must be made).
- **What the caller does**: read *Required* and *Useful* documents in full, in that order. A
  document scored *Irrelevant* is **still listed** in the research findings as considered and not
  read — never silently dropped. Where confidence is below 0.5, read it.

## J2 — Screen the consumers

**Caller: the Researcher**, when `consumers` is non-empty and the change touches a public
interface.

`consumers` exists so "does a client need updating?" is never left unanswered. J2 makes the sweep
cheap enough to run every time instead of only when someone remembers.

- **State**: the change description, the interfaces it alters (endpoints, webhooks, tool surfaces,
  published exports), and the consumer's name and what it is known to call.
- **Question**: one `noul` per consumer — *does this change alter a contract this consumer depends
  on?* — and a second, *would a consumer that is not updated break rather than degrade?*
- **What the caller does**: above 0.5 on the first, investigate that consumer properly and record
  the finding. Below it, record the consumer as swept and clear. The second answer sets the order,
  not the verdict: a breaking consumer is looked at first. **A consumer is never marked clear
  without the sweep running** — if J2 could not run, the Researcher sweeps them all by hand, which
  is what it does with Jev off.

## J3 — Resolve a tracker state by role

**Caller: T4 in `reference/tracker.md`**, whose universal rule 3 already forbids hardcoding a
status name or ID and requires resolving the wanted state by role. T4 is reached from `/jdi:plan`,
`/jdi:prep` and `/jdi:pr`, and those three run the ladder at step 0 for this and nothing else.

**T5 and T8 are deliberately not callers.** T5 resolves no state at all — it upserts a comment. T8
resolves one, but only in `subtickets` mode and only to the **completed** state, which is the one
role a tracker's own state types name unambiguously; putting a probe into `/jdi:done`, `/jdi:next`
and `/jdi:yolo` would tax the three most frequently run commands for the least ambiguous lookup
JDI makes.

Every tracker names its workflow states differently, and a team's are often idiosyncratic
("Baking", "On deck", "Shipped it"). This is the bounded-set case J-ops exist for: the tracker's
own API supplies the options, and Jev picks which one plays the role.

- **State**: the states the tracker listed, each with its name, type and description, plus what the
  workflow is trying to express — *implementation has started*, *a pull request is open for
  review*, *the work is finished*.
- **Question**: one `choice` over those states, with the listed state names as the criteria map.
- **What the caller does**: **confidence above 0.9 only.** Anything less and the caller asks the
  user which state to use, exactly as it would with Jev off. A status transition is a write to
  someone else's board — universal rule 1 applies with no slack, and universal rule 5 of
  `reference/tracker.md` still stands: read the value back and confirm the write landed.

## J4 — Check the split is atomic

**Caller: the Splitter**, after it has written the task files and before it hands them back.

A task that is really two tasks is the defect this catches, and it is one the Splitter is poorly
placed to see in its own output.

- **State**: the plan, plus each task's title, why, and description. One request per split, not per
  task, so the plan is paid for once.
- **Question**: per task, a `noul` for *does this task do exactly one thing?* and a `noul` for
  *can this be verified on its own, without a later task landing first?* **Do not ask Jev whether
  a task depends on one numbered after it** — every task file declares its dependencies, so that
  is a comparison of two numbers and belongs in code. It is the ordering weakness named above.
- **What the caller does**: a task that fails either question is **reported to the Butler as a
  question, not silently re-split**. The Splitter says which task, which property, and what it
  would do about it. The user decides. Jev never re-writes a task file.

## J5 — Rank the findings

**Caller: the Feedbacker**, when a critique produced more findings than a reader will act on.

- **State**: the output under review, the role's stated responsibilities, and each finding.
- **Question**: per finding, a `score` on *what happens if this is shipped unchanged* — levels from
  *Nothing: a matter of taste* through *A reader is briefly confused*, *A reader is misled about
  what the code does*, to *The work is wrong and the error will propagate*; plus a `noul` for *is
  this finding actually supported by the output, rather than a general principle?*
- **What the caller does**: order the findings by score, and **drop nothing**. A finding that fails
  the support check is kept and marked as unsupported, because a critique that quietly deletes its
  own weakest claims is not auditable. The verdict stays the Feedbacker's.

## Adding an operation

The filter a new J-op must pass, in order:

1. **Is there a list?** A J-op exists where a role faces many candidates to rank or filter, or a
   bounded set to choose exactly one from. A one-off judgment with no list is prose, and the role
   already does prose better.
2. **Does the role currently skim?** The value is in attention the role would otherwise not spend
   — reading the twentieth candidate as carefully as the first. If the role already reads
   everything, ranking it changes nothing.
3. **Can the caller enumerate the candidates from the repository?** If the list has to be imagined,
   universal rule 3 is already broken.
4. **Is the answer advisory?** If the operation's result would cause a write, a skip, or an
   irreversible act on its own, it fails universal rule 1 and does not become a J-op.
5. **Does it degrade to more work?** Write what the caller does when the answer never comes. If
   that fallback is "do less", the operation is not admissible.

This is why `/jdi:status`, `/jdi:done`, `/jdi:execute` and `/jdi:yolo` rank nothing of their own.
Status reports ground truth. Done, execute and yolo act on a list whose order the plan already
fixed, and the pull request `/jdi:pr` opens is the most irreversible thing JDI does — rule 4 closes
it. `/jdi:plan` and `/jdi:pr` carry the ladder all the same, because **J3** reaches them through
**T4**; a command can resolve Jev without ever ranking anything itself.
