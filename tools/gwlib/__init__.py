"""gwlib — the shared toolkit for property generators.

Every function here was extracted from a shipped generator or verifier after
it survived contact with real data; the docstrings name the incident that
taught each lesson. Generators keep their individuality — sources, era
framings, judgment calls, docstrings — and share only the plumbing that kept
going wrong when copy-pasted: fetching, table parsing, cleaning, id rules,
and the standard asserts.

Modules:
    wiki      fetch + parse Wikipedia (tables with rowspan, episode lists,
              infoboxes, wikitext cleaning)
    wikidata  batch QID and runtime resolution with year gates
    hltb      HowLongToBeat story hours, verify-by-name
    prop      ids, note assembly, validation, and the property emitter
"""
