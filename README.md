<div align="center">

# Medwin Jose

*Computer Science undergraduate · Distributed systems reliability · Formal verification*

<sub>VIT Bhopal &nbsp;·&nbsp; B.Tech CSE, Class of 2028</sub>

<br>

[![LinkedIn](https://img.shields.io/badge/LinkedIn-1F2A44?style=flat-square&logo=linkedin&logoColor=C9B27C)](https://linkedin.com/in/medwinjose)
[![Email](https://img.shields.io/badge/Email-1F2A44?style=flat-square&logo=gmail&logoColor=C9B27C)](mailto:medwinjose@gmail.com)
[![Scholar](https://img.shields.io/badge/Google%20Scholar-1F2A44?style=flat-square&logo=googlescholar&logoColor=C9B27C)](https://scholar.google.com/)
[![Zenodo](https://img.shields.io/badge/Preprint-1F2A44?style=flat-square&logo=zenodo&logoColor=C9B27C)](https://doi.org/10.5281/zenodo.23032043)

</div>

<br>

---

## About

I study how systems behave when some of their participants are dishonest or broken. My work sits between distributed protocols, fault isolation and reputation, and I evaluate everything under adversarial conditions rather than the happy path.

Currently interested in **Byzantine fault isolation** and **reputation systems**.

---

## Research

**CRCI: Local Reputation-Based Fault Isolation for Ad-Hoc Gossip Communication** &nbsp;·&nbsp; 2026
Preprint &nbsp;·&nbsp; [10.5281/zenodo.23032043](https://doi.org/10.5281/zenodo.23032043)

Proposes local reputation-based peer eviction for gossip networks. Evaluates sliding-window anti-replay under packet reordering, and shows that paced attackers can evade isolation.

---

## Selected Work

### [CRCI](https://github.com/medwinjose/crci) &nbsp;·&nbsp; *Crisis Response Communication Infrastructure*
`Rust` `TLA+` `Docker` `Prometheus` `Grafana` `Kotlin`

A mesh protocol for infrastructure-free crisis communication, with local reputation-based peer eviction (three strikes), Ed25519 node identity and AES-256-GCM encrypted storage.

- A replaying attacker is evicted after exactly three strikes; honest peers survived 100/100 loopback runs
- Safety and liveness properties specified in TLA+ and checked with TLC
- 195 passing tests, CI on GitHub Actions, a 5-node WAN testbed and a chaos suite
- Runs on Linux, Raspberry Pi and Android &nbsp;·&nbsp; Apache-2.0

### [SENTINEL](https://github.com/medwinjose/sentinel) &nbsp;·&nbsp; *Trust-Aware Adaptive Market Maker*
`Rust` `Python` `Criterion` `Proptest` `Pandas` `SciPy`

A Rust limit order book paired with an adversarial market simulator.

- ~254 ns median insert and ~577 ns partial-fill crossing (Criterion)
- Invariants verified with Proptest and mutation testing
- Q-learning spoofers against trust-aware spreads; toxicity phase boundaries mapped over 1,000 episodes per regime, using Welch's t-tests, Holm–Bonferroni correction and bootstrap CIs

### DataTrust &nbsp;·&nbsp; *Source reliability and anomaly detection*
`Python` `NumPy` `Pandas` `SciPy` `Pytest`

Built during a research internship at India Infrastructure Publishing.

- Cut aggregation MAE by ~37.5% against majority voting, across ~100,000 observations from 8 sources
- Detected errors of 4σ or more at 96.4% precision and 94.8% recall
- Identified the faulty source in 19 of 20 seeded runs
- 87 automated tests; 11.8 ms median latency per update round

---

## Leadership

**Team Manager, Team Vortex** &nbsp;·&nbsp; VIT Bhopal, SAE Aero Design &nbsp;·&nbsp; 2025 – Present

Co-founded the university's first international aerospace team. Ranked **16th of 75** global teams at SAE Aero Design 2026 in Fort Worth, Texas. Led 50 members across technical, media and operations, and managed a budget of Rs. 30 lakh+ (~USD 33K+) including sponsorships.

---

## Toolkit

| | |
|:--|:--|
| **Languages** | Rust · Python · Java · Kotlin · SQL |
| **Systems** | Distributed Systems · Fault Tolerance · Networking · Chaos Testing · Linux · Docker · AWS |
| **Verification** | TLA+ · TLC · Pytest · Proptest · Criterion · Mutation Testing · Statistical Testing |
| **Tooling** | NumPy · Pandas · SciPy · Git · GitHub Actions · Prometheus · Grafana |

---

<div align="center">

<sub>Open to research collaboration and conversations on distributed systems.</sub>

</div>
