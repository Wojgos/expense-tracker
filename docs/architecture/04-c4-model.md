# Zadanie 4 — Model C4: stan obecny (As-Is) i docelowy (To-Be)

> Architektura systemu **Smart Expense Buddy** w notacji C4 (poziomy: Context i Container).
> Wariant As-Is = jak wygląda dzisiaj. Wariant To-Be = jak powinien wyglądać po
> wprowadzeniu Bounded Contexts z `03-bounded-contexts.md`.

> Uwaga techniczna: zamiast `C4Context` / `C4Container` z Mermaida (które bywają zawodne
> w niektórych rendererach, m.in. przy przecinkach i nawiasach w opisach), używam tu
> `flowchart` z `subgraph` i klasami stylów. To jest powszechnie stosowane
> zastępstwo, w pełni zgodne z duchem C4 (kontener / system / aktor / relacja).

## 4.1 C4 Level 1 — System Context (wspólny dla As-Is i To-Be)

```mermaid
flowchart LR
    classDef person fill:#fff4cf,stroke:#b7791f,stroke-width:2px,color:#000
    classDef system fill:#cfe2ff,stroke:#1d4e89,stroke-width:2px,color:#000
    classDef ext    fill:#e8e8e8,stroke:#555,stroke-width:1px,color:#000

    user(["Użytkownik<br/><i>Person</i><br/>Członek grupy rozliczeniowej"]):::person
    seb["Smart Expense Buddy<br/><i>System</i><br/>Aplikacja do dzielenia wydatków w grupach"]:::system
    nbp["NBP API<br/><i>External system</i><br/>Kursy walut"]:::ext

    user -- "Korzysta (HTTPS, WebSocket)" --> seb
    seb  -- "Pobiera kursy walut (HTTPS)" --> nbp
```

**Komentarz.** Z perspektywy świata zewnętrznego system widać jako jedną całość;
jedyne dwie istotne relacje to: użytkownik → system (UI po HTTPS i WS),
system → NBP (pobieranie kursów).

## 4.2 C4 Level 2 — Container, **As-Is**

Tu pokazana jest dzisiejsza topologia: monolit FastAPI z wszystkimi obszarami
biznesowymi w jednym procesie i jednej bazie.

```mermaid
flowchart TB
    classDef person fill:#fff4cf,stroke:#b7791f,stroke-width:2px,color:#000
    classDef app    fill:#cfe2ff,stroke:#1d4e89,stroke-width:1px,color:#000
    classDef db     fill:#dbe9f1,stroke:#1d4e89,stroke-width:1px,color:#000
    classDef ext    fill:#e8e8e8,stroke:#555,stroke-width:1px,color:#000

    user(["Użytkownik"]):::person
    nbp["NBP API<br/>(External)"]:::ext

    subgraph seb["Smart Expense Buddy"]
      spa["Frontend SPA<br/>React + TS + Vite<br/>UI, React Query, WS client"]:::app
      api["Backend API<br/>FastAPI Python<br/>auth, groups, expenses, settlements,<br/>recurring, accounts, currency, ws<br/>+ APScheduler in-process"]:::app
      ws["WebSocket endpoint<br/>(w tym samym procesie co API)"]:::app
      db[("PostgreSQL<br/>jedna schema, wszystkie tabele")]:::db
      cache[("Redis<br/>cache kursów walut")]:::db
    end

    user -- "HTTPS" --> spa
    spa  -- "REST /api/*" --> api
    spa  -- "WebSocket /ws/groups/{id}" --> ws
    api  -- "SQLAlchemy async" --> db
    api  -- "redis-py async" --> cache
    api  -- "httpx HTTPS" --> nbp
    ws   -- "współdzieli proces" --- api
```

**Komentarz do As-Is.**

- Całość API to **jeden monolit** — wszystkie obszary biznesowe (auth, grupy,
  wydatki, rozliczenia, recurring, konta osobiste, waluty, WS) żyją w tym samym
  procesie i tej samej bazie.
- **Scheduler** (APScheduler) jest częścią procesu API → przy poziomym skalowaniu
  utworzy się N kopii joba.
- **WebSocket** = osobny endpoint, ale w tym samym procesie; broadcast realizuje
  globalny singleton `notification_manager.manager` importowany przez `api/*` i scheduler.
- Brak jawnych granic między obszarami biznesowymi — wszystko może wszystkiego użyć
  (i tak właśnie się dzieje, patrz wycieki opisane w `01-case-study.md`).

## 4.3 C4 Level 2 — Container, **To-Be**

Wariant docelowy: **modularny monolit** z jawnymi Bounded Contexts jako modułami
wewnątrz tego samego procesu. Komunikacja między BC odbywa się przez **wewnętrzną
szynę zdarzeń** (in-process), a nie przez bezpośrednie importy klas między modułami.
Scheduler wyniesiony z procesu API. Schemat bazy podzielony per kontekst (PostgreSQL,
ale różne schemy lub odrębne tabele z jasnym właścicielem).

```mermaid
flowchart TB
    classDef person fill:#fff4cf,stroke:#b7791f,stroke-width:2px,color:#000
    classDef app    fill:#cfe2ff,stroke:#1d4e89,stroke-width:1px,color:#000
    classDef core   fill:#fde2e2,stroke:#c0392b,stroke-width:2px,color:#000
    classDef sup    fill:#fff4cf,stroke:#b7791f,stroke-width:1px,color:#000
    classDef gen    fill:#e2efda,stroke:#3a7d44,stroke-width:1px,color:#000
    classDef infra  fill:#dbe9f1,stroke:#1d4e89,stroke-width:1px,color:#000
    classDef ext    fill:#e8e8e8,stroke:#555,stroke-width:1px,color:#000

    user(["Użytkownik"]):::person
    nbp["NBP API"]:::ext

    subgraph seb["Smart Expense Buddy (To-Be)"]
      spa["Frontend SPA<br/>React + TS"]:::app

      subgraph backend["Backend (modularny monolit)"]
        iam["IAM<br/>UserAccount, JWT"]:::gen
        gm["Group Membership<br/>Group, Membership"]:::sup
        se["Shared Expenses<br/>Expense + Split<br/>(CORE)"]:::core
        gs["Group Settlements<br/>Settlement, GroupBalance<br/>(CORE)"]:::core
        re["Recurring Expenses<br/>RecurringTemplate"]:::sup
        pa["Personal Accounting<br/>Wallet + LedgerEntry"]:::sup
        ce["Currency Exchange<br/>(ACL do NBP)"]:::gen
        rn["Realtime Notifications<br/>WebSocket"]:::sup
        bus{{"In-process Event Bus<br/>(domain events)"}}:::app
      end

      sched["Scheduler<br/>Celery beat / k8s CronJob<br/>(wyniesiony z procesu API)"]:::gen
      db[("PostgreSQL<br/>schema per BC")]:::infra
      cache[("Redis")]:::infra
    end

    user -- "HTTPS / WS" --> spa
    spa  -- "REST + WS" --> iam
    spa  -- "REST" --> gm
    spa  -- "REST" --> se
    spa  -- "REST" --> gs
    spa  -- "REST" --> re
    spa  -- "REST" --> pa
    spa  -- "WS" --> rn

    iam -- "UserRegistered" --> bus
    gm  -- "MemberAdded / Removed" --> bus
    se  -- "ExpenseCreated / Deleted" --> bus
    gs  -- "SettlementRecorded" --> bus
    re  -- "RecurringExpenseDue" --> bus

    bus -- "MemberAdded → autoryzacja" --> se
    bus -- "ExpenseCreated/Deleted → przelicz bilans" --> gs
    bus -- "RecurringExpenseDue → utwórz Expense (przez agregat)" --> se
    bus -- "wszystkie events → broadcast WS" --> rn

    ce  -- "kurs (OHS)" --> se
    ce  -- "kurs (OHS)" --> pa
    ce  -. "ACL" .-> nbp

    sched -- "tick co dobę" --> re

    iam  -- "schema: iam" --> db
    gm   -- "schema: groups" --> db
    se   -- "schema: shared_expenses" --> db
    gs   -- "schema: settlements" --> db
    re   -- "schema: recurring" --> db
    pa   -- "schema: personal_accounting" --> db
    ce   -- "schema: currency" --> db
    ce   --> cache
```

**Komentarz do To-Be — co się zmienia względem As-Is:**

1. **Jawne moduły per Bounded Context** w jednym backendzie (modularny monolit).
   To pozwala później wyodrębnić mikroserwisy bez przepisywania domeny.
2. **In-process Event Bus** rozplątuje sprzężenia: `Recurring → Shared Expenses → Settlements`
   nie odbywa się już przez bezpośrednie importy klas SQLAlchemy.
3. **Scheduler poza procesem API** — można skalować backend horyzontalnie.
4. **ACL na granicy z NBP** — `Currency Exchange` izoluje resztę systemu od konwencji NBP
   ("rate X → PLN") i pozwala wymienić providera.
5. **Schema bazy per BC** — fizycznie wciąż jedna baza, ale jasny właściciel każdej tabeli.
6. **WebSocket** staje się czystym konsumentem zdarzeń, a nie globalnym singletonem
   wstrzykiwanym do API.

## 4.4 Roadmap przejścia As-Is → To-Be

| Krok | Działanie                                                                                              | Wpływa na                                                  |
| ---- | ------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------- |
| 1    | Utworzyć katalogi `app/contexts/<bc>/` i przenieść do nich obecne `api/`, `crud/`, `models/`, `schemas/` | wszystkie BC (czysta reorganizacja, bez zmian logiki)      |
| 2    | Zlikwidować import `SplitType` z `RecurringExpense` — własny enum w Recurring lub przekazywanie stringa | Shared Expenses ↔ Recurring                                |
| 3    | Wprowadzić mały `EventBus` (in-process, async) i zacząć od jednego eventu: `ExpenseCreated`            | Shared Expenses, Settlements, Notifications                |
| 4    | Przepisać scheduler na publikację `RecurringExpenseDue`; konsument w Shared Expenses tworzy `Expense` przez agregat | Recurring, Shared Expenses                                 |
| 5    | Zamienić ręczne sprawdzenia uprawnień w endpointach na wspólny `Depends(require_group_role(...))`      | Group Membership, Shared Expenses, Settlements, Recurring  |
| 6    | Dodać walutę do `ExpenseSplit.owed_amount` i przejść w `compute_balances` na waluty per uczestnik       | Shared Expenses, Settlements, Currency Exchange            |
| 7    | Zmienić nazwy: `Account → Wallet`, `AccountTransaction → LedgerEntry` (migracja + DTO + UI)             | Personal Accounting                                        |
| 8    | Wynieść scheduler do osobnego procesu (Celery beat / k8s CronJob)                                       | Recurring, infrastruktura                                  |
| 9    | Podzielić bazę na schemy per BC (`iam`, `groups`, `shared_expenses`, ...)                               | wszystkie BC                                               |
| 10   | Zaktualizować CORS na port `:3000` (lub konfigurowalny przez env)                                        | infrastruktura                                              |

