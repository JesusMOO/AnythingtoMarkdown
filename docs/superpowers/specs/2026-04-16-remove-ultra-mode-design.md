# Remove Ultra Mode Design

**Date:** 2026-04-16

**Status:** Approved in brainstorming, pending final written-spec review

## Goal

Remove `ultra` as a user-visible mode, command set, and shell state mechanism while keeping `sptool` as a single-mode CLI that still supports:

- existing simplified commands
- REPL `exit`
- the current positional `input [output]` style
- backend native flags written directly after positional arguments

This is a scope-reduction change. It is not a CLI redesign.

## Non-Goals

This change does not:

- add a new subcommand such as `raw` or `native`
- add a `--` separator requirement
- change concurrency behavior
- add parameter conflict detection
- change backend routing rules
- change banner style or the general output style
- remove REPL support entirely
- change the meaning of `exit`

## User-Facing Outcome

After this change, `sptool` has exactly one mode.

The following calls remain valid:

```text
sptool file.pdf
sptool file.pdf out
sptool file.pdf --max-pages 10
sptool file.pdf out --max-pages 10
sptool notes.docx
sptool notes.docx out.md
sptool notes.docx -o out.md
sptool notes.docx out.md --some-flag
sptool a.csv out
sptool a.html out
sptool folder
sptool folder out
```

The following calls are removed as special behavior:

```text
sptool ultra start
sptool ultra exit
```

These strings will no longer be recognized as dedicated mode-control commands. They will fall through normal argument handling.

## CLI Semantics

The command grammar remains:

```text
sptool input [output] [native_args...]
```

The parsing rules are:

1. The first argument is always `input`.
2. If a second argument exists and does not start with `-`, it is treated as explicit `output`.
3. All remaining arguments that follow are passed through as native backend arguments.
4. Native backend arguments may use either short or long flag syntax, for example `-o` or `--max-pages`.
5. This grammar applies uniformly to all supported single-file types, not just PDF or DOCX.

Examples:

```text
sptool report.pdf
sptool report.pdf out
sptool report.pdf --max-pages 10
sptool report.pdf out --max-pages 10
sptool notes.docx out.md
sptool notes.docx -o out.md
sptool data.csv out
```

## Execution Semantics

### Single-file inputs

- Backend selection still depends on file extension.
- Simplified default behavior remains active.
- User-supplied native arguments are appended to the backend command without requiring a mode switch.

### Directory inputs

- Directory scanning behavior remains unchanged.
- Existing concurrent execution remains unchanged.
- The same native arguments, if supplied, are passed to each prepared job in the batch.

### REPL

- `exit` remains supported exactly as it is today.
- `sptool ultra start` and `sptool ultra exit` are removed from REPL special handling.
- The REPL keeps its current overall interaction style.

## Compatibility Decisions

### Removed behavior

The following `ultra`-specific pieces are removed:

- `TOOL_MODE` environment-variable mode switching
- shell-wrapper mode control
- REPL mode control
- help text and README references to `ultra`
- tests whose only purpose is validating `ultra`

### Preserved behavior

The following stay intact:

- `sptool input`
- `sptool input output`
- `sptool --help`
- `sptool --version`
- `exit` in REPL
- extension-based backend routing

### Accepted ambiguity

If a user supplies native backend flags that overlap with default output-related behavior, `sptool` will not add new validation in this change. This work intentionally avoids redesigning argument precedence. The tool only preserves the existing simplified path and allows native flags to be appended in the same invocation.

## Implementation Boundaries

The change is intentionally limited to these areas:

- remove mode/state code
- merge native-argument passthrough into the single default execution path
- remove `ultra` branches from wrappers and REPL
- remove `ultra` references from help text, README, and tests

The change intentionally avoids unrelated refactoring.

## Affected Files

Primary implementation files:

- `src/sptool/cli.py`
- `src/sptool/commands.py`
- `src/sptool/helptext.py`
- `scripts/sptool.ps1`
- `scripts/sptool.cmd`

Mode infrastructure expected to become unused:

- `src/sptool/modes.py`

Documentation:

- `README.md`

Tests expected to change:

- `tests/test_commands.py`
- `tests/test_cli.py`
- `tests/test_modes.py`
- `tests/test_windows_wrappers.py`
- `tests/test_shell_docs.md`

## Testing Strategy

The implementation must verify all of the following:

1. Simplified commands still work for supported file types.
2. Single-file commands still accept explicit `output`.
3. Native flags work without `ultra`.
4. `ultra` commands are no longer special-cased.
5. Wrapper scripts only forward to the Python CLI.
6. Help and README no longer describe multiple modes.

Representative scenarios:

```text
sptool file.pdf
sptool file.pdf out
sptool file.pdf --max-pages 10
sptool file.pdf out --max-pages 10
sptool notes.docx out.md
sptool notes.docx -o out.md
sptool a.csv out
sptool folder
sptool folder out
```

Representative removal checks:

```text
sptool ultra start
sptool ultra exit
```

## Risks

1. Users who rely on `ultra` mode-switch commands will lose that workflow.
2. Native backend flags can still overlap with default output behavior, and this change does not resolve those conflicts.
3. Wrapper behavior changes must stay consistent across `cmd` and PowerShell.

## Success Criteria

This design is complete when:

1. No user-visible `ultra` mode remains.
2. There is only one documented CLI mode.
3. Simplified commands continue to work.
4. Native `-x` and `--xxx` backend flags can be supplied without a mode switch.
5. REPL `exit` remains unchanged.
6. Documentation and tests match the new single-mode behavior.
