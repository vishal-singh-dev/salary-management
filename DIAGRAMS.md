# System Diagrams

This page explains the Salary Management system with high-level diagrams.

## Deployment Flow

```mermaid
flowchart LR
    user[User Browser]
    vercel[Vercel\nNext.js Frontend]
    render[Render HTTPS Proxy\nNode/Express]
    ec2[AWS EC2\nFastAPI Backend Container]
    neon[(Neon PostgreSQL)]

    user -->|HTTPS| vercel
    vercel -->|HTTPS API calls| render
    render -->|HTTP proxy| ec2
    ec2 -->|PostgreSQL SSL| neon
```

The browser talks only to HTTPS services. The Render proxy is used because the backend currently
runs on EC2 over HTTP, and browsers block HTTPS frontend pages from calling HTTP APIs directly.

## Application Request Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend as Vercel Frontend
    participant Proxy as Render Proxy
    participant API as FastAPI Backend
    participant DB as PostgreSQL

    User->>Frontend: Open dashboard or employee page
    Frontend->>Proxy: Request /api/v1/...
    Proxy->>API: Forward same API path
    API->>DB: Query or update data
    DB-->>API: Return rows
    API-->>Proxy: JSON response
    Proxy-->>Frontend: JSON response over HTTPS
    Frontend-->>User: Render updated screen
```

## Employee Create Flow

```mermaid
flowchart TD
    start([Open Add Employee])
    nextId[Load next employee ID]
    master[Load master data]
    country[Select country]
    department[Select department\nfiltered by country]
    title[Select job title\nfiltered by department]
    salary[Enter initial salary]
    submit[Create employee]
    validate[Backend validates\nmaster-data chain and salary]
    save[(Save employee\nand current salary)]
    detail[Redirect to employee details]

    start --> nextId
    start --> master
    master --> country
    country --> department
    department --> title
    title --> salary
    salary --> submit
    submit --> validate
    validate --> save
    save --> detail
```

Department stays locked until a country is selected. Job title stays locked until a department is
selected, so invalid country-department-title combinations are prevented before the request reaches
the backend.

## Master Data Dependency

```mermaid
flowchart LR
    country[Country\nIN, CHN, AUS, US, GB, DE, CA]
    department[Department\nparent = Country]
    title[JobTitle\nparent = Department]
    currency[Currency\nindependent]

    country --> department
    department --> title
    currency
```

Master data is stored in `master_data_config`. Department rows reference a country through
`parent_code`, and job-title rows reference a department through `parent_code`. Currency has no
parent because payments can be made in any configured country currency.

## Backend Startup Flow

```mermaid
flowchart TD
    container[Backend container starts]
    migrate[Run Alembic migrations]
    seedFx[Seed fixed exchange rates]
    seedMaster[Seed master data config]
    checkEmployees{Employees table empty?}
    seedEmployees[Seed demo employees\nwith valid master-data combinations]
    api[Start Uvicorn API]

    container --> migrate
    migrate --> seedFx
    seedFx --> seedMaster
    seedMaster --> checkEmployees
    checkEmployees -->|Yes| seedEmployees
    checkEmployees -->|No| api
    seedEmployees --> api
```

The bootstrap seed is safe for repeated container starts. It always ensures fixed reference data is
present, but it creates demo employees only when the employee table is empty.

## Frontend Loading Flow

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Loading: GET request
    Idle --> Saving: POST/PATCH/DELETE request
    Loading --> Idle: Response received
    Saving --> Idle: Response received

    Loading: Show loading messages
    Saving: Show saving messages
```

The global loader listens to active API requests. Read requests show loading messages, while create,
update, and delete requests show saving messages.
