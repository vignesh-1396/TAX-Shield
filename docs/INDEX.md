# ITC Shield - Documentation Index

> Quick navigation to all project documentation

---

## 📁 Core Documentation

| Document | Description |
|----------|-------------|
| [README.md](../README.md) | Project overview & quick start |
| [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) | What's done, what's pending |

---

## 📂 Technical Docs

| Document | Description |
|----------|-------------|
| [decision_logic.md](./technical/decision_logic.md) | Decision rules (S1-S3, H1-H3, R1) |
| [system_architecture_master.md](./technical/system_architecture_master.md) | Full system design |
| [DATA_FETCHING_STRATEGY.md](./technical/DATA_FETCHING_STRATEGY.md) | GSP waterfall logic |

---

## 📂 Business Docs

| Document | Description |
|----------|-------------|
| [Commercial_Strategy_and_Budget.md](./business/Commercial_Strategy_and_Budget.md) | Pricing & revenue model |
| [Cofounder_Pitch_Script.md](./business/Cofounder_Pitch_Script.md) | Pitch deck content |

---

## 📂 Go-to-Market

| Document | Description |
|----------|-------------|
| [tally_integration_strategy.md](./go_to_market/tally_integration_strategy.md) | Tally sales approach |
| [competitor_analysis.md](./go_to_market/competitor_analysis.md) | Market landscape |

---

## 📂 Product

| Document | Description |
|----------|-------------|
| [product_scaling_strategy.md](./product/product_scaling_strategy.md) | Growth roadmap |

---

## 🔧 API Reference

- **Base URL:** `http://localhost:8000`
- **Swagger Docs:** `http://localhost:8000/docs`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/check_compliance` | POST | Check vendor GSTIN |
| `/vendor/{gstin}` | GET | Get vendor details |
| `/history` | GET | Audit trail |
| `/test-scenarios` | GET | Test GSTINs |
