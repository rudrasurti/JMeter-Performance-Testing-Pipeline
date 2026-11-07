# JMeter Performance Testing Pipeline

![Performance Tests](https://github.com/rudrasurti/JMeter-Performance-Testing-Pipeline/actions/workflows/performance.yml/badge.svg)
![JMeter](https://img.shields.io/badge/JMeter-5.6.3-D22128)

**Live performance dashboard:** [rudrasurti.github.io/JMeter-Performance-Testing-Pipeline](https://rudrasurti.github.io/JMeter-Performance-Testing-Pipeline/)

A load test for a REST API that runs in CI on every push and every week, fails the build when performance limits are broken, and publishes the JMeter HTML dashboard to GitHub Pages. The same pipeline is included as a Jenkinsfile.

## What the test does

Each virtual user runs this flow against the public [Restful-booker](https://restful-booker.herokuapp.com/apidoc/index.html) API, with 0.5 to 1.5 s think time:

| Step | Request | Check |
|---|---|---|
| 1 | `GET /ping` | Status 201 |
| 2 | `POST /booking` (random price) | Status 200, `bookingid` extracted |
| 3 | `GET /booking/{id}` | Body contains the booking |
| 4 | `GET /booking?firstname=...` | Status 200 |

Load is set with properties, so the same plan works for a smoke run or a bigger test:

```bash
jmeter -n -t perf/booking-load.jmx -Jusers=10 -Jloops=5 -Jrampup=10 \
  -l results/results.jtl -e -o results/dashboard
```

## Performance limits (quality gate)

`scripts/check_thresholds.py` reads the results and fails the build when any request breaks a limit:

| Limit | Default | Set with |
|---|---|---|
| Error rate | 2% | `MAX_ERROR_PCT` |
| 95th percentile response time | 5000 ms | `MAX_P95_MS` |

A per-request table (samples, errors, average, p95, pass/fail) is shown on every GitHub Actions run page.

## CI/CD

| Stage | GitHub Actions | Jenkins |
|---|---|---|
| Trigger | Push, PR, weekly, manual with user/loop inputs | Weekly cron, manual with parameters |
| JMeter | Downloaded once and cached | Downloaded once into the workspace |
| Run | Non-GUI mode, CSV results, HTML dashboard | Same |
| Gate | Threshold script fails the job | Threshold script fails the stage |
| Report | Dashboard on GitHub Pages + artifact | HTML Publisher + archived results |

## Project structure

```
.
├── perf/booking-load.jmx              # JMeter test plan
├── scripts/check_thresholds.py        # error-rate and p95 quality gate
├── .github/workflows/performance.yml  # GitHub Actions pipeline
└── Jenkinsfile                        # Jenkins pipeline
```

---

**Rudra Surti** · Senior SDET · [Website](https://rudrasurti.github.io) · [LinkedIn](https://www.linkedin.com/in/rudra-surti/) · [Medium](https://medium.com/@rudrasurti98)
