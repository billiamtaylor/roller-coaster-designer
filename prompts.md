# Prompt Log

Chronological record of requests in the available project conversation. Outcomes reflect the checks that were actually performed; user questions answered without code changes are included.

## 2026-11-24

### 1. Create a top-level `AGENTS.md` with two project instructions
- **Asked:** Add the two specified instructions to a new top-level `AGENTS.md` and commit it.
- **Changed:** Created `AGENTS.md`.
- **Outcome / problems:** The directory was not a Git repository, so Git was initialized before the requested commit. The file was committed successfully.

### 2. Update `spec.md` to describe a Tkinter desktop app
- **Asked:** Describe the project as a Python desktop app using Tkinter; do not build it.
- **Changed:** Added a Tkinter platform description to `spec.md` and started this request log.
- **Outcome / problems:** Documentation change completed; no application was built for this request.

### 3. Build the desktop app from the specification
- **Asked:** Read `spec.md` and build its desktop app, using `index.html` as a reference.
- **Changed:** Added `app.py` with the track editor, ride controls, readouts, plots, and simulation calculations.
- **Outcome / problems:** Python syntax and calculation checks passed, and the app process launched and remained running until stopped. `index.html` only contained a title and short description, so detailed behavior followed `spec.md`.

### 4. Explain the command for starting the app
- **Asked:** Tell what command to type to display the app.
- **Changed:** Provided `python app.py` (with the then-configured interpreter path).
- **Outcome / problems:** No application files changed; this was a launch-instructions response.

### 5. Rerun the specification's numerical validation and report expected/actual values
- **Asked:** Run the validation cases in `spec.md` against the app calculations.
- **Changed:** Ran the speed calculation and the 20 m radius g-force formula.
- **Outcome / problems:** Speed matched: 24.26107994 m/s and 54.27049021 mph. The initial three-point test spline had a 27.7778 m radius, so its app-calculated g-force was 3.16 g rather than the separate 20 m-radius case's 4.00 g. This geometry distinction was recorded; a later run used a spline with the specified 20 m radius and passed.

### 6. Add Save/Open design files
- **Asked:** Add a File menu with JSON Save and Open and restore the complete design.
- **Changed:** Added the menu actions and JSON handling for track points, physics, safety limits, and playback position.
- **Outcome / problems:** Syntax and JSON serialization/round-trip checks passed. The native dialog workflow was not manually exercised.

### 7. Add CSV export
- **Asked:** Export calculated track position, height, speed, and g-force values for Excel.
- **Changed:** Added CSV export to the File menu and ride controls.
- **Outcome / problems:** Syntax and CSV read-back checks passed; the generated file had the expected headings and 801 simulation rows.

### 8. Add PDF design report export
- **Asked:** Export a formatted report with design inputs, diagrams, safety checks, and results.
- **Changed:** Added PDF generation using ReportLab and Matplotlib, and listed both packages in `requirements.txt`.
- **Outcome / problems:** The first test exposed a temporary-image lifetime error; PDF generation was moved inside the temporary-directory scope. The retry produced a valid `%PDF` file.

### 9. Audit feature integration and update the Out of Scope text
- **Asked:** Preserve existing controls while integrating Save/Open and exports, and remove any Out of Scope reference to saving.
- **Changed:** Audited the UI and export paths; updated `spec.md` to state that saving and exporting are supported. No saving reference existed in Out of Scope.
- **Outcome / problems:** No application behavior was changed. A launch check found ReportLab missing from the system interpreter; installing the declared requirements resolved it, and the app then launched.

### 10. Rerun the `spec.md` validation cases
- **Asked:** Confirm that the specification's validation still passes.
- **Changed:** Ran `calculate_ride` using a spline whose bottom radius was actually 20 m.
- **Outcome / problems:** Passed: bottom height 0 m, speed 24.26107994 m/s (54.27049021 mph), radius 20 m, and vertical g-force 4.00 g, matching the expected rounded values.

### 11. Write a short README
- **Asked:** Summarize the app, packages to install, and startup command.
- **Changed:** Created an initial `README.md` with a feature summary and install/run commands.
- **Outcome / problems:** Documentation was added; no application behavior changed.

### 12. Add at least two features beyond the web version
- **Asked:** Add two useful features not present in the web version.
- **Changed:** Added Shift-click control-point insertion, selected interior-point removal, and Undo/Redo (buttons and keyboard shortcuts). Updated `README.md` and `spec.md`.
- **Outcome / problems:** Syntax and headless interaction checks for add, remove, undo, and redo passed.

### 13. Complete the Platform section in `spec.md`
- **Asked:** Document language/version, Tkinter, OS, dependencies, entry point, run command, file formats, and development environment without changing other sections.
- **Changed:** Expanded the Platform section using the implementation, `requirements.txt`, and installed package metadata.
- **Outcome / problems:** Documentation-only change; the other specification sections were left unchanged.

### 14. Set up and review the assignment documentation requirements
- **Asked:** Update `AGENTS.md`, maintain a reliable chronological `prompts.md`, and complete an accurate `README.md`; verify the files and do not commit.
- **Changed:** Expanded `AGENTS.md` with the requested standing instructions, rewrote `prompts.md` into chronological entries with outcomes and known issues, and added the requested README sections and setup details. Application code was not changed.
- **Outcome / problems:** Verified that all three files exist in the project root, all required AGENTS instructions and README sections/commands are present, README dependencies match `requirements.txt`, and whitespace checks pass. The first exact-text check caught the old wording “what you changed”; it was corrected to the requested “what I changed.” No commit or push was made.

### 15. Inspect Git repository setup, history, branch, and worktree
- **Asked:** Check repository initialization, GitHub remote, commit history, current branch/status, and already-committed assignment milestones.
- **Changed:** Inspected Git metadata and history; added this audit summary to the prompt log. No application files were changed.
- **Outcome / problems:** Confirmed the repository is initialized on `master`, has 13 commits, and has no configured remote. The pre-audit worktree had modified `AGENTS.md`, `README.md`, and `prompts.md`, plus untracked `index.html`. No commit or push was made.

### 16. Determine whether `index.html` belongs to the Tkinter application
- **Asked:** Determine the file's purpose and do not delete it without explanation and permission.
- **Changed:** Inspected `index.html`, searched the app and project docs for references, and checked its Git history. Left the file untouched.
- **Outcome / problems:** The HTML contains only the app title and a short description. `app.py` does not use it; the README identifies it as a reference page, and a baseline checkpoint contains it. It is not a runtime requirement for the Tkinter app, but it can remain as a reference. No deletion, commit, or push was made.

### 17. Keep `index.html` as an optional design reference
- **Asked:** Keep the HTML reference, don't integrate or delete it, and clarify in README that `app.py` is the entry point.
- **Changed:** Clarified the entry point and optional/non-runtime status in `README.md`. Left `index.html` and application functionality unchanged.
- **Outcome / problems:** Documentation update completed; no application functionality was modified. No commit or push was made.

### 18. Check for and connect a GitHub repository
- **Asked:** Create a GitHub repository if needed and connect the local repository.
- **Changed:** Confirmed the local repository is initialized but has no remote; checked GitHub search, the signed-in browser account, existing repository contents, and GitHub CLI availability.
- **Outcome / problems:** `gh` is not installed. GitHub is signed in as `billiamtaylor`; the account already has a public `roller-coaster-designer` repository containing related assignment files (`spec.md`, `index.html`, and `prompts.md`) but no `app.py`. After the user chose to connect to the existing repository, added it as `origin` and fetched `origin/main` successfully. Local `master` and remote `main` have no common ancestor (13 local-only and 7 remote-only commits), so they were not merged. No commit or push was made.

### 19. Fill out the open GitHub repository form
- **Asked:** Fill in the currently open GitHub creation form.
- **Changed:** Inspected the shared form and left it unchanged.
- **Outcome / problems:** The selected owner is `billiamtaylor`, visibility is Public, and the requested `roller-coaster-designer` name already exists and is connected as `origin`. A second repo cannot be created under the same owner with that name. The user chose the existing repository; navigated the shared browser page to it instead of creating a duplicate. No commit or push was made.

### 20. Identify the web-app/GitHub Pages mismatch
- **Asked:** Pointed out that GitHub describes a single-file web app while the assignment requires a Tkinter desktop app launched through `app.py`.
- **Changed:** Read the remote `AGENTS.md`, `spec.md`, and `index.html`, compared them with the local README, and inspected GitHub Pages settings. No source or remote settings were changed.
- **Outcome / problems:** Remote guidance/spec describe a web app; local documentation describes Tkinter. GitHub Pages is live from `main` at the repository root, and Tkinter cannot run as a GitHub Pages site. The user authorized a GitHub commit, chose to sync the local desktop app files, and chose to keep the Pages site live.

### 21. Publish the actual prompt history and sync the desktop project
- **Asked:** Reported that the published `prompts.md` contained only a heading and an instruction, and asked to add the actual prompt history in a readable format. Chose to sync the local Tkinter app and its required files to the existing GitHub repository while leaving Pages live.
- **Changed:** Replaced the remote placeholder with this 21-entry chronological request/outcome log. Synced `app.py`, `requirements.txt`, `README.md`, `AGENTS.md`, `spec.md`, and `prompts.md` from the local desktop project. Clarified that GitHub Pages serves the separate `index.html` web version, which remains untouched.
- **Outcome / problems:** The copied `app.py` loaded from the remote worktree, exposed a callable `main`, and produced 801 simulation samples for the default track. AST syntax validation and `git diff --check` passed, and SHA-256 comparisons confirmed the synced files match their local sources. GitHub Pages configuration and `index.html` were left unchanged. Changes were committed and pushed to `main`.
