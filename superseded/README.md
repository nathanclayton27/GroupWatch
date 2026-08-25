# Superseded migrations — do not run

These files were once live migrations. They are kept for history and **must not
be pasted into the SQL editor**, because each one silently undoes protection
that later work installed. Neither raises an error when re-run; both leave their
own verification blocks passing.

They were moved out of the `migrate-*.sql` namespace deliberately: they used to
sit in the repo root with names shaped exactly like the migrations that ARE meant
to be run, which is the whole hazard.

## `migrate-add-friend-privacy.sql`

Recreates `"mutual friends read progress"` **without the gated-list term**. Run
after FINAL-1 and the password-gated list is readable by every mutual friend
again. Superseded by `scratch/security/FINAL-2-privacy.sql`.

## `migrate-add-thumbs.sql`

Worse, and its own header used to say *"Additive and safe to re-run"* — the only
one of these that actively invited the thing that breaks it. Its policy carries
**neither** the gated-list term nor the privacy term, so re-running it undoes
both PART 1 §5b and FINAL-1 §6 in a single statement. The table-creation half is
already applied and is not needed again. Superseded by
`scratch/security/FINAL-1-rls-locks.sql` §6.

Flagged by the independent SQL re-check on 2026-08-25 (CLU-201).
