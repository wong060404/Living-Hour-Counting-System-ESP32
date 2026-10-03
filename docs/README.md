# Diagrams · 圖表

Every image in `docs/images/` was generated for this README.
`docs/images/` 內所有圖片都是為本 README 製作的。 The source is
`.build/make_diagrams.py`, which uses nothing but Pillow and renders at 2× and
downsamples, so the PNGs stay sharp when GitHub scales them.

| File | Shows |
|---|---|
| `architecture.png` | The three tiers: hardware / IoT, Python processing, SQLite data. |
| `data-flow.png` | End-to-end: camera frame → detection → tracking → LBPH → confidence gate → voting → unlock + log, and what each trigger writes. |
| `registration-flow.png` | Phase A sequence diagram — enrolment and training. |
| `runtime-sequence.png` | Phase B sequence diagram — live recognition, voting and unlock. |
| `entry-leave-toggle.png` | The "Single Door" Entry/Leave toggle state machine, and the tailgating flaw. |
| `database-erd.png` | SQLite schema with the relationships between `Info`, the raw event logs and the monthly report tables. |
| `hardware-wiring.png` | ESP32 → relay → electromagnetic lock, plus what the PC talks to and what it does not. |
| `file-map.png` | Every script in the repository, grouped by responsibility. |
| `monthly-lifecycle.png` | The month-end reset → accumulate → compare → aggregate → flag cycle. |
| `prototype-front.jpg` | Photograph of the acrylic door prototype. |
| `terminal-session.png` | Terminal capture of the recognition loop, including graceful relay failure. |
| `report-output.png` | Terminal capture of the under-150-hour report. |

## Regenerating · 重新產生

```bash
python .build/make_diagrams.py
```

Requirements: `pillow`. The fonts used are Arial and Courier New from
`/System/Library/Fonts/Supplemental/`; change `FONT_DIR` and `MONO_DIR` in
`.build/diagramkit.py` if you are not on macOS.

## Editing a diagram · 修改圖表

`make_diagrams.py` has one function per image and a small drawing kit in
`diagramkit.py` (`rect`, `arrow`, `badge`, `text`, `center`). Coordinates are in
plain pixels at 1× scale; the supersampling happens on save. Every function ends
with a single `c.save(...)` call, so you can re-render one diagram during editing
by importing the module:

```python
import sys; sys.path.insert(0, ".build")
import make_diagrams as m
m.hardware_wiring()      # re-render just this one
```

## Note on the report's original diagrams · 關於報告原有圖表的說明

The database figure in the project report is a good structural diagram but its
column order and relationship lines are ambiguous, so `database-erd.png` was
redrawn from the actual `CREATE TABLE` statements in `database_init.py` rather
than traced from the report. The wiring diagram is likewise derived from the
firmware (`RELAY_PIN = 26`) and the photographs, not from a schematic in the
report — because the report does not contain one.
