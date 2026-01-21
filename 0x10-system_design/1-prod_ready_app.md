# high-level architecture of a production app

<div style="text-align: justify;">

## 0. CI/CD pipeline
* allows our code to travel from our repo, through a series of tests and checks, to our prod server w/o manual intervention
* configures using the following technologies among others
    * jenkins
    * GH actions
## 1. load balancers
* allow our prod servers to handle varying amounts of traffic
* most common load balancer is nginx

## 2. storage
* a repository of data that our prod servers can access
* said storage does not run on the same environment as the servers

## 3. logging and monitoring
* allow us to see what happens to our prod servers during interactions with users
* best practice is to store logs in an external server
* examples of loggers and monitors
    * PM2 for back-end
    * sentry for FE
    * ELK stack
* monitors alert the, well, alert service when an anomaly or atypical action/state is discovered
    * alert service will, well, alert the relevant group of people
    * best practice is to integrate said alerts into common collaboration platforms, for example, slack
* say we have a bug
    * devs are alerted through slack
    * devs check the logs for patterns etc to identify the problem
    * devs replicate the problem in a sandbox/staging/test environment
        > **muhimu tena sana!** <br/>- do not debug in prod env <br/> - repeat: do not debug in prod <br/><br/> 
    * devs roll out a hot-fix once the bug is solved
    * monitor hot-fix

## 4. illustrations
### 4.1. overall

```mermaid
    graph TB
        %% CI/CD Pipeline
        Repo[GitHub Repo] -->|Push/PR| CI[CI/CD<br/>Jenkins / GH Actions]
        CI --> Tests[Automated Tests<br/>Unit / Integration / E2E]
        Tests -->|Pass| Build[Build & Package]
        Build -->|Deploy| Prod[Production Servers]
        
        %% Load Balancers & Traffic Flow
        Users[Users] --> LB[Load Balancers<br/>Nginx]
        LB -->|Distribute Traffic| Prod
        
        %% Storage
        Prod -->|Read/Write| Storage[External Storage<br/>Database / File Storage]
        
        %% Logging & Monitoring
        Prod -->|Logs| PM2[PM2 Backend Logs]
        LB -->|Errors| Sentry[Sentry Frontend]
        
        PM2 --> ELK[ELK Stack<br/>External Log Server]
        Sentry --> ELK
        ELK --> Monitor[Monitoring Service]
        
        %% Alerting Flow
        Monitor -->|Anomaly Detected| Alert[Alert Service]
        Alert -->|Slack Integration| Devs[Development Team]
        
        %% Bug Fix Workflow
        Devs -->|Replicate| Sandbox[Staging/Test Env<br/>🚫 NEVER PROD]
        Sandbox -->|Hotfix Ready| Build
        Build -.->|Deploy & Monitor| Prod
        
        %% Styling
        classDef critical fill:#ff6b6b,stroke:#333,stroke-width:2px
        classDef success fill:#51cf66,stroke:#333,stroke-width:2px
        classDef warning fill:#ffd43b,stroke:#333,stroke-width:2px
        classDef info fill:#74c0fc,stroke:#333,stroke-width:2px
        
        class Repo,CI,Tests,Build,Prod success
        class LB,Storage info
        class PM2,Sentry,ELK,Monitor warning
        class Alert,Sandbox critical
```

### 4.2. CI/CD

```mermaid
    graph LR
        A[GitHub Repo<br/>Push/PR] --> B{Gate 1: Lint &<br/>Code Quality}
        B -->|Pass| C[Unit Tests<br/>Jest/Vitest]
        C -->|Pass| D[Integration Tests<br/>API/Database]
        D -->|Pass| E[E2E Tests<br/>Cypress/Playwright]
        E -->|Pass| F[Security Scan<br/>SAST/DAST]
        F -->|Pass| G[Build & Package<br/>Docker/NPM]
        G -->|Success| H[Deploy Staging]
        H -->|Manual Approval| I[Deploy Production]
        
        B -->|Fail| J[Notify Devs<br/>via GitHub]
        C -->|Fail| J
        D -->|Fail| J
        E -->|Fail| J
        F -->|Fail| J
        
        classDef pass fill:#51cf66
        classDef fail fill:#ff6b6b
        classDef gate fill:#74c0fc
        
        class B,D,F,E gate
        class C,G,H,I pass
        class J fail
```

### 4.3. logging and monitoring

```mermaid
    graph TD
        subgraph "Frontend"
            Users[Users] --> App[Frontend App]
            App -->|Errors/Performance| Sentry[Sentry.io]
        end
        
        subgraph "Backend" 
            Server[Prod Servers] -->|App Logs| PM2[PM2 Process Manager]
            Server -->|Access Logs| Nginx[Nginx Logs]
        end
        
        PM2 -->|Ship Logs| Logstash[Logstash]
        Nginx --> Logstash
        Sentry -->|Webhooks| Logstash
        
        Logstash -->|Parse & Transform| ES[Elasticsearch]
        ES --> Kibana[Kibana Dashboard]
        
        subgraph "Alerting"
            ES -->|Anomaly Detection| AlertEngine[Alert Rules]
            AlertEngine -->|Threshold Breached| Slack[Slack Channel]
            AlertEngine -->|PagerDuty| PagerDuty[On-call Rotation]
        end
        
        classDef external fill:#ffba08
        classDef internal fill:#51cf66
        classDef alerting fill:#ff6b6b
        
        class Sentry,Slack,PagerDuty external
        class PM2,Nginx,Logstash,Kibana internal
        class AlertEngine alerting
```

### 4.4. debugging and applying hot-fixes

```mermaid
    sequenceDiagram
        participant U as Users
        participant P as Prod Servers
        participant S as Slack/Alerts
        participant D as Developers
        participant T as Test/Staging
        participant C as CI/CD
        
        U->>P: Encounter Bug
        P->>P: Crash/Error
        P->>S: Alert Triggered
        S->>D: 🚨 Bug Alert in Slack
        Note over D: NEVER DEBUG IN PROD!
        
        D->>S: Ack & Triage
        D->>P: Check Logs (Read-only)
        D->>T: Replicate in Staging
        T->>T: Confirm Bug Behaviour
        
        D->>D: Identify Root Cause
        D->>D: Write Hotfix
        D->>C: PR with Hotfix
        C->>T: Deploy to Staging
        T->>D: Tests Pass ✅
        
        D->>C: Approve Production Deploy
        C->>P: Rollout Hotfix
        P->>S: Monitor Post-Deploy
        S->>D: All Clear ✅
```
</div>