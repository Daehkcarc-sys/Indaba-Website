# SENTINEL Hybrid Observatory

A jury-facing, offline-capable React replay of the final Qwen3-8B defense evaluation.

## Run

```bash
pnpm install
pnpm dev
```

Open the Vite address shown in the terminal. `pnpm build` and `pnpm lint` work from the repository root.

## Evidence

`front/public/data` bundles 62 scenarios, 186 masked traces, the final analysis and reason-code explanations. The website does not require Ollama, Python, a defense checkout or a running API. `/demo` provides a presentation view, while `/trace` exposes raw event order and a separate evaluator overlay.

The source corpus was the completed `final_corpus` archive from defense commit `05860f01f4e9c2253b1f1b02dd783dc3477834cc`. The normalized snapshot was produced with:

```bash
python3 scripts/export-sentinel-evidence.py --corpus /absolute/path/to/final_corpus
```

The script masks `SENTINEL_SECRET_*` synthetic restricted values, checks sequential event order, and refuses to leave those strings in the exported JSON. Original unmasked evidence belongs in the defense evidence archive, not this website. The script classifies scenario origin using `scenario_path`, since the YAML split field is not authoritative for self-authored scenarios.

## Interpretation

Metrics are self-test evidence, not an official jury score. Attack-task utility and overall task success are derived diagnostics. The attack landing marker is evaluator presentation metadata and is verified only for the two featured attack traces. Defense View hides evaluator events; it does not provide scenario labels to the runtime defense. Replays display recorded events; they do not rerun Qwen.

The reference observability vocabulary was reviewed against the latest accessible `sentinel-defense` main branch. This website does not modify either defense repository.
