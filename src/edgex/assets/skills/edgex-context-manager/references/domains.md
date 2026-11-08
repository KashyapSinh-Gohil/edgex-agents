# EdgeX domain requirements

These are EdgeX operational checks. Select every applicable domain; an interdisciplinary project must satisfy their intersection. Record which checks apply, the evidence artifact for each, and a reason for each omission. This file is self-contained and does not require a sibling skill. No domain checklist alone establishes safety, validity, or approval.

## Common scientific contract

Specify the object of study, question, observational or experimental unit, assumptions, variables, units, admissible data, comparison, decision rule, resource limit, and intended scope of inference. Separate established results, working hypotheses, speculation, and EdgeX inferences. Present derivations and measured observations distinctly. Preserve negative results and unresolved contradictions.

For every domain, keep primary-source versions, exact evidence locators, code/data/config hashes, environment, uncertainty, limitations, and a reproducible procedure. Validate physical units, mathematical domains, sampling assumptions, and software behavior where applicable. Do not promote an idealized result into a real-world claim without checking the transfer assumptions.

## Machine learning (ML)

**Inputs:** dataset release and license, intended population, prediction/decision target, feature availability time, split specification, baseline, metric definition, compute budget, and intended use.

**Procedure:** establish split independence at the right unit (person, group, site, device, or time). Fit preprocessing and feature selection on training folds only; tune on validation data; lock the held-out test set before selection. Audit duplicates, target-derived features, label contamination, pretraining overlap where assessable, and train/test temporal leakage. Compare meaningful simple and strong baselines under comparable data and compute access. Record hyperparameter search space, search trials including failures, selection rule, random generators, and inference cost.

**Gates:** report absolute scores and effect differences, uncertainty at the independent sampling unit, subgroup/sample-size limitations, calibration when probabilities inform decisions, and distribution-shift tests relevant to the use. Include ablations that isolate the intervention. A single lucky seed or benchmark score does not establish generality.

**Failure conditions:** leaked evaluation, untracked model/data versions, unlicensed inputs, post-selection test tuning, unsuitable baseline, or deployment claims unsupported by the evaluation distribution. Treat a contaminated holdout as unusable; create a newly authorized independent evaluation rather than quietly relabeling it.

## Deep learning (DL)

Apply the ML requirements as well.

**Inputs:** architecture graph/config, initialization or pretrained checkpoint identity, tokenizer/preprocessing version, objective, optimizer/scheduler, precision, batch/accumulation policy, hardware, distributed topology, training and checkpoint selection budgets.

**Procedure:** verify tensor shapes, masking, label alignment, loss reductions, gradient accumulation scaling, clipping, and train/eval mode. Run a tiny-batch overfit check and loss/gradient finite-value checks when appropriate. Record optimizer state, scheduler state, step, sampler/random-generator states, and data order needed for restart. Measure memory, latency, throughput, and numerical stability under the actual precision and device.

**Gates:** fair comparison of parameter count/data/compute or explicit unmatched factors; training and validation curves with all relevant seeds; no selective checkpoint or failed-run deletion. Document stochastic kernels and nondeterminism. If comparing language models, version prompts, decoding, tools, graders, and contamination assessments; separate model ability from tool-assisted system ability.

**Failure conditions:** NaN/Inf training, silent shape broadcasting, validation contamination, untracked pretrained weights, OOM counted as a low score, or an unsupported assertion of bitwise determinism. A stopped run is a failure record, not an invented final metric.

## Programming and systems

**Inputs:** behavioral specification, interfaces, supported environments, workload/limits, authorized write scope, threat assumptions, and acceptance examples.

**Procedure:** choose the smallest readable design; state relevant time and space complexity. Check empty/degenerate inputs, numeric bounds, serialization, filesystem paths, dependency failures, timeout/retry behavior, and error propagation. For concurrency, identify shared state, synchronization, cancellation, deadlock risks, and idempotency boundaries. For distributed work, specify required consistency and partition behavior rather than invoking CAP without a system model. Avoid interpreting untrusted input as code or instructions.

**Gates:** tests target observable behavior and credible regressions; integration checks exercise important boundaries. Benchmark comparable workloads and separate startup, steady state, I/O, and warm-cache effects. Record exact revisions, dependencies, commands, exit codes, and relevant platform characteristics.

**Failure conditions:** tests not executed but reported passing, swallowed errors, unauthorized production/network changes, hardcoded credentials, unverifiable performance claims, or an implementation that alters the evaluation metric to pass.

## Mathematics

**Inputs:** precise statement, quantifiers, definitions, ambient structures, field/characteristic when relevant, regularity/domain assumptions, and allowed results.

**Procedure:** state proof obligations and assumptions; select a proof strategy and attack small/degenerate cases first. Justify each nontrivial implication and theorem applicability. Track exclusions when dividing, taking logarithms, interchanging limits/integrals, or assuming compactness/measurability. Search for counterexamples to the exact quantified statement. Use symbolic computation to check algebra when tools are available, recording expressions, assumptions, tool/version, and output.

**Gates:** proof covers all cases and boundaries, uses no circular lemma, and distinguishes equality from approximation. State whether verification is hand-checked, computer-assisted, or checked by a named proof assistant with its version and trusted assumptions. A computer search over finitely many cases is not a proof of an unbounded universal statement.

**Failure conditions:** unsupported lemma, missing domain restrictions, invalid limit exchange, numerical agreement called proof, or a conjecture presented as a theorem. If symbolic tools are unavailable, mark the symbolic check unperformed; provide inspectable algebra and leave any required tool gate open.

## Physics

**Inputs:** system boundaries, regime (classical, quantum, relativistic, statistical), scales, governing laws, initial/boundary conditions, material parameters, units, and measured observables.

**Procedure:** derive the model from named equations and state approximations with their dimensionless validity conditions. Nondimensionalize when useful; check dimensions, signs, symmetries, conservation laws, limiting cases, and known analytic solutions. For numerics, separate discretization error, solver error, parameter uncertainty, and measurement uncertainty. Check mesh/time-step convergence and long-time drift before interpreting effects.

**Gates:** no incompatible regimes; constants and unit conventions explicit; numerical residual/conservation error smaller than the claimed effect or its limitation disclosed. Compare to calibrated observations or accepted reference cases in the applicable regime.

**Failure conditions:** unstable integrator mistaken for new dynamics, unit mismatch, boundary artifacts, regime violation, or simulated behavior described as measured physical evidence.

## Chemistry

**Inputs:** chemical identity including stereochemistry/charge/protonation, phase, concentration convention, temperature/pressure, data provenance, computational or experimental model, and permitted scope.

**Procedure:** check mass, charge, stoichiometry, atom mapping, and standard-state conventions. For electronic structure, record functional or wavefunction method, basis, dispersion/solvation treatment, convergence tolerances, spin/multiplicity, and geometry. Distinguish electronic energy, enthalpy, free energy, equilibrium, and kinetic barriers. Track conformers and uncertainty from model and sampling choices; compare like thermodynamic conditions.

**Gates:** valid chemical structures; conserved balances; applicable reference data; method convergence and plausible sensitivity. A computed favorable energy does not establish reaction rate, feasibility, toxicity, or successful synthesis. Wet-lab plans require appropriate qualified review and existing authorization; computational authorization does not include performing chemistry.

**Failure conditions:** unidentified species/units, incompatible standard states, ignored spin or conformer alternatives, invalid extrapolation from simulation to synthesis, or activity outside the authorized safety scope.

## Biology

**Inputs:** organism and reference assembly/version, biological system, cohort/sample provenance, assay and controls, endpoint, biological replicate unit, consent/access restrictions, and permissible analysis.

**Procedure:** distinguish biological from technical replicates; audit batch, confounding, contamination, missingness, and selection effects. Record reference databases, annotation versions, preprocessing, normalization, exclusion criteria, and batch-correction fit boundaries. Use controls and orthogonal evidence appropriate to the claim. For omics, define feature universe and multiplicity correction; for structure prediction, separate predictive confidence from experimentally validated function.

**Gates:** independent-unit uncertainty; endpoint and exclusion transparency; appropriate negative/positive controls; justified causal assumptions; privacy-respecting provenance. Observational association does not establish mechanism, clinical efficacy, or patient benefit. Qualified and institutional permissions cannot be created by an agent.

**Failure conditions:** pseudoreplication, donor/site leakage, inaccessible consent provenance, causal claims from unadjusted associations, or simulated/computational findings described as wet-lab or clinical validation. Stop unapproved intervention or hazardous biological activity; continue permitted analysis where separable.

## Quantum science and computing

Apply mathematics and physics requirements, and ML/DL when learning is involved.

**Inputs:** Hilbert space, subsystem layout, basis and endianness, units including hbar convention, state/preparation, Hamiltonian/channel/circuit, measurement scheme, and classical comparison.

**Procedure:** verify state normalization, density-matrix trace/positivity, operator dimensions/Hermiticity, and unitarity or channel complete positivity/trace preservation as appropriate. Record qubit mapping, compilation, gate set, depth, shots, noise model, device/backend and calibration time. Distinguish state-vector simulation, noisy simulation, and hardware execution. Check small exact systems before scaling.

**Gates:** account for sampling and hardware drift; include state preparation, oracle construction, measurement, mitigation/postselection, and classical preprocessing in claimed resources. State computational assumptions and comparable classical baselines. An idealized asymptotic improvement is not demonstrated practical quantum advantage.

**Failure conditions:** nonphysical state/channel, basis mismatch, discarded failed shots without a rule, ignored preparation costs, or simulator outputs represented as quantum-hardware results.

## Space, astronomy, and orbital science

Apply mathematics and physics requirements; apply chemistry/biology for relevant planetary or life-science claims.

**Inputs:** observation/mission context, coordinate/reference frame and origin, time scale/epoch, ephemeris/catalog release, instrument calibration, uncertainty/covariance, units, and dynamical/observational model.

**Procedure:** reconcile UTC/TAI/TT/TDB and leap-second handling where relevant; distinguish geocentric, barycentric, inertial, and rotating frames. Record force model, gravitational parameters, integrator/tolerance, propagation horizon, and perturbations. For astronomy, track selection functions, masks, exposure, PSF/background, calibration, redshift conventions, and correlated noise. Propagate uncertainties and compare with independent known objects or trajectories.

**Gates:** no frame/time/unit mismatch; numerical convergence and covariance assumptions checked; claims match instrument sensitivity and selection effects. Report detection significance with the search/trials procedure; an anomaly is not established extraterrestrial life or a new physical law.

**Failure conditions:** stale ephemerides for the stated accuracy, covariance ignored in collision inference, catalog leakage, background artifacts, or an analysis treated as authorization for spacecraft commands, navigation, launch, or other operational control.

## Cross-domain dispatch example

For a neural surrogate of quantum orbital dynamics: architect specifies the physical regime and approximation target; domain-scientist checks frames, Hamiltonian, and conservation; mathematician checks the surrogate's claimed bound; statistician checks splits by trajectory/system and uncertainty; builder and executor preserve code/data/config identity; referee tests extrapolation and leakage; reproducibility reruns a frozen small benchmark. Scribe must distinguish approximation accuracy, physical validity, and any claimed computational advantage. If the model is only tested on ideal simulations, report that exact scope.
