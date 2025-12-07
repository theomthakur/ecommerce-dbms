# E-Commerce DBMS - Complete Technical Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture Diagram](#system-architecture-diagram)
3. [Project Architecture](#project-architecture)
4. [Project Flow Diagrams](#project-flow-diagrams)
5. [Database Schema Diagrams](#database-schema-diagrams)
6. [Directory Structure](#directory-structure)
7. [Detailed File Documentation](#detailed-file-documentation)
8. [Data Flow Diagram](#data-flow-diagram)
9. [Setup and Execution Guide](#setup-and-execution-guide)

---

## Project Overview

This project implements a complete end-to-end e-commerce database management system with the following components:
- **ETL Pipeline**: Extracts, transforms, and loads raw CSV data into a normalized OLTP database
- **OLTP Database**: Normalized transactional database (SQLite and PostgreSQL support)
- **Data Warehouse**: Star schema dimensional model for analytics
- **Analytics Dashboard**: Interactive Streamlit web application with visualizations
- **Testing Suite**: Unit and integration tests
- **CI/CD**: GitHub Actions workflow for automated testing

---

## System Architecture Diagram

```mermaid
graph TB
    subgraph Raw["📁 RAW DATA"]
        Orders[Orders CSV<br/>~25K rows]
        Returns[Returns CSV<br/>~1K rows]
    end

    subgraph ETL["🔄 ETL PIPELINE"]
        Extract[Extract<br/>Read CSVs]
        Transform[Transform<br/>Clean & Validate]
        Validate[Validate<br/>Integrity Checks]
        Extract --> Transform
        Transform --> Validate
    end

    subgraph Cleaned["📄 CLEANED DATA"]
        CleanCSV1[cleaned_customers.csv]
        CleanCSV2[cleaned_products.csv]
        CleanCSV3[cleaned_orders.csv]
        CleanCSV4[cleaned_order_items.csv]
        CleanCSV5[cleaned_returns.csv]
    end

    subgraph OLTP["🗄️ OLTP DATABASE"]
        SQLite[(SQLite<br/>oltp.db)]
        Customers[customers<br/>17K rows]
        Products[products<br/>3.8K rows]
        OrdersT[orders<br/>25K rows]
        OrderItems[order_items<br/>51K rows]
        ReturnsT[returns<br/>1K rows]
        
        SQLite --- Customers
        SQLite --- Products
        SQLite --- OrdersT
        SQLite --- OrderItems
        SQLite --- ReturnsT
    end

    subgraph Postgres["🐘 POSTGRESQL"]
        PG[(PostgreSQL<br/>DB)]
        PGStaging[Staging Area<br/>pg_load/]
    end

    subgraph DW["🏢 DATA WAREHOUSE"]
        DWDb[(dw.db)]
        DimDate[dim_date<br/>1.5K rows]
        DimCustomer[dim_customer<br/>17K rows]
        DimProduct[dim_product<br/>3.8K rows]
        DimRegion[dim_region<br/>24 rows]
        FactSales[fact_sales<br/>51K rows]
        
        DWDb --- DimDate
        DWDb --- DimCustomer
        DWDb --- DimProduct
        DWDb --- DimRegion
        DWDb --- FactSales
    end

    subgraph Dashboard["📊 ANALYTICS DASHBOARD"]
        Streamlit[Streamlit App<br/>localhost:8501]
        KPI[KPI Cards]
        Charts[Visualizations]
        Filters[Interactive Filters]
        Maps[Geographic Map]
        
        Streamlit --> KPI
        Streamlit --> Charts
        Streamlit --> Filters
        Streamlit --> Maps
    end

    Orders --> Extract
    Returns --> Extract
    Validate --> Cleaned
    Cleaned --> OLTP
    Cleaned --> PGStaging
    PGStaging --> PG
    OLTP --> DW
    DW --> Dashboard

    style Raw fill:#e1f5ff
    style ETL fill:#fff3e0
    style Cleaned fill:#f1f8e9
    style OLTP fill:#fce4ec
    style Postgres fill:#e8eaf6
    style DW fill:#fff9c4
    style Dashboard fill:#e0f2f1
```

---

## Project Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         RAW DATA                                 │
│          (CSV Files: Orders, Returns)                            │
└──────────────────┬────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ETL PIPELINE                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Data Cleaning│->│Transformation│->│ Validation   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└──────────────────┬───────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CLEANED DATA                                   │
│           (Cleaned CSV Snapshots)                                │
└───────────┬──────────────────────────┬────────────────────────────┘
           │                          │
           ▼                          ▼
┌──────────────────────   ┌─────────────────────────┐
│   OLTP DATABASE      │   │   DATA WAREHOUSE        │
│   (SQLite/Postgres)  │   │   (Star Schema)         │
│                      │   │                         │
│  - customers         │   │  - dim_customer         │
│  - products          │   │  - dim_product          │
│  - orders            │   │  - dim_date             │
│  - order_items       │   │  - dim_region           │
│  - returns           │   │  - fact_sales           │
└──────────────────────┘   └────────┬────────────────┘
                                    │
                                    ▼
                          ┌──────────────────────┐
                          │  STREAMLIT DASHBOARD │
                          │                      │
                          │  - KPIs              │
                          │  - Visualizations    │
                          │  - Geographic Map    │
                          │  - Filters           │
                          └──────────────────────┘
```

---

## Project Flow Diagrams

### 1. ETL Pipeline Flow

```mermaid
flowchart TD
    Start([Start ETL]) --> ReadOrders[Read Orders CSV]
    ReadOrders --> ReadReturns[Read Returns CSV]
    
    ReadReturns --> CleanCust[Clean Customer Data<br/>- Deduplicate<br/>- Normalize names<br/>- Generate IDs]
    
    CleanCust --> CleanProd[Clean Product Data<br/>- Deduplicate<br/>- Standardize categories<br/>- Generate IDs]
    
    CleanProd --> CleanOrders[Clean Order Data<br/>- Validate dates<br/>- Parse ship modes<br/>- Check FK integrity]
    
    CleanOrders --> CleanItems[Clean Order Items<br/>- Validate numerics<br/>- Calculate metrics<br/>- Handle nulls]
    
    CleanItems --> CleanReturns[Clean Returns Data<br/>- Infer dates<br/>- Normalize flags<br/>- Match to orders]
    
    CleanReturns --> ValidateData{Validation<br/>Passed?}
    
    ValidateData -->|No| LogErrors[Log Errors]
    LogErrors --> FixData[Manual Fix Required]
    FixData --> Stop1([Stop])
    
    ValidateData -->|Yes| WriteCSV[Write Cleaned CSVs<br/>to data/ directory]
    
    WriteCSV --> ApplySchema[Apply OLTP Schema<br/>oltp_schema.sql]
    
    ApplySchema --> CreateTables[Create Tables<br/>- customers<br/>- products<br/>- orders<br/>- order_items<br/>- returns]
    
    CreateTables --> LoadData[Load Data into SQLite<br/>oltp.db]
    
    LoadData --> CreateIndex[Create Indexes<br/>on FK columns]
    
    CreateIndex --> ValidateLoad{Row Counts<br/>Match?}
    
    ValidateLoad -->|No| LogLoad[Log Discrepancies]
    LogLoad --> Stop2([Stop with Error])
    
    ValidateLoad -->|Yes| Success([✅ ETL Complete])
    
    style Start fill:#4caf50,color:#fff
    style Success fill:#4caf50,color:#fff
    style Stop1 fill:#f44336,color:#fff
    style Stop2 fill:#f44336,color:#fff
    style ValidateData fill:#ff9800,color:#fff
    style ValidateLoad fill:#ff9800,color:#fff
```

### 2. Data Transformation Pipeline

```mermaid
flowchart TD
    subgraph Input["📥 INPUT DATA"]
        RawOrders[Orders CSV<br/>~25,000 rows<br/>Mixed quality]
        RawReturns[Returns CSV<br/>~1,000 rows<br/>Missing dates]
    end

    subgraph Transform["🔧 TRANSFORMATION FUNCTIONS"]
        
        subgraph TransCustomer["transform.clean_customer_data()"]
            C1[Extract unique customers<br/>by Customer ID + Name]
            C2[Normalize names<br/>Title case, strip whitespace]
            C3[Standardize addresses<br/>City, State, Country]
            C4[Generate customer_id<br/>Hash-based unique ID]
            C5[Deduplicate<br/>17,415 unique customers]
            C1 --> C2 --> C3 --> C4 --> C5
        end

        subgraph TransProduct["transform.clean_product_data()"]
            P1[Extract unique products<br/>by Product ID + Name]
            P2[Standardize categories<br/>Furniture, Office, Technology]
            P3[Normalize sub-categories<br/>Consistent naming]
            P4[Generate product_id<br/>Hash-based unique ID]
            P5[Deduplicate<br/>3,788 unique products]
            P1 --> P2 --> P3 --> P4 --> P5
        end

        subgraph TransOrder["transform.clean_order_data()"]
            O1[Parse order dates<br/>Handle multiple formats]
            O2[Parse ship dates<br/>Validate chronology]
            O3[Normalize ship modes<br/>Standard Second, First, Same Day]
            O4[Validate customer FK<br/>Match to customer_id]
            O5[25,728 clean orders]
            O1 --> O2 --> O3 --> O4 --> O5
        end

        subgraph TransItems["transform.clean_order_items()"]
            I1[Validate numeric fields<br/>Sales, Profit, Discount]
            I2[Calculate derived metrics<br/>Unit price, margins]
            I3[Handle missing values<br/>Fill with defaults or remove]
            I4[Validate FK integrity<br/>order_id, product_id]
            I5[51,290 order items]
            I1 --> I2 --> I3 --> I4 --> I5
        end

        subgraph TransReturns["transform.clean_returns_data()"]
            R1[Normalize returned flag<br/>Yes/No standardization]
            R2[Match to orders<br/>Join on Order ID]
            R3[Infer return dates<br/>Use order_date heuristics]
            R4[Validate region<br/>Match to order region]
            R5[1,079 clean returns]
            R1 --> R2 --> R3 --> R4 --> R5
        end
    end

    subgraph Validate["✅ VALIDATION"]
        V1{Check data types}
        V2{Check FK integrity}
        V3{Check completeness}
        V4{Check duplicates}
        
        V1 --> V2 --> V3 --> V4
    end

    subgraph Output["📤 OUTPUT"]
        OutCust[cleaned_customers.csv<br/>17,415 rows]
        OutProd[cleaned_products.csv<br/>3,788 rows]
        OutOrders[cleaned_orders.csv<br/>25,728 rows]
        OutItems[cleaned_order_items.csv<br/>51,290 rows]
        OutReturns[cleaned_returns.csv<br/>1,079 rows]
    end

    RawOrders --> TransCustomer
    RawOrders --> TransProduct
    RawOrders --> TransOrder
    RawOrders --> TransItems
    RawReturns --> TransReturns

    C5 --> V1
    P5 --> V1
    O5 --> V1
    I5 --> V1
    R5 --> V1

    V4 -->|Pass| OutCust
    V4 -->|Pass| OutProd
    V4 -->|Pass| OutOrders
    V4 -->|Pass| OutItems
    V4 -->|Pass| OutReturns

    V4 -->|Fail| Error[❌ Validation Failed<br/>Log errors and stop]

    style Input fill:#e1f5ff
    style Transform fill:#fff3e0
    style TransCustomer fill:#f1f8e9
    style TransProduct fill:#fce4ec
    style TransOrder fill:#e8eaf6
    style TransItems fill:#fff9c4
    style TransReturns fill:#e0f2f1
    style Validate fill:#ff9800,color:#fff
    style Output fill:#4caf50,color:#fff
    style Error fill:#f44336,color:#fff
```

### 3. PostgreSQL Migration Flow

```mermaid
flowchart TD
    Start([Start Migration]) --> PrepStaging[Prepare Staging Area<br/>Create pg_load/ directory]
    
    PrepStaging --> CopyFiles[Copy Cleaned CSVs<br/>to pg_load/]
    
    CopyFiles --> Dedupe[Additional Deduplication<br/>- Customers by ID<br/>- Orders by ID]
    
    Dedupe --> Normalize[Normalize Data<br/>- Boolean conversion<br/>- Column headers<br/>- Data types]
    
    Normalize --> ApplyDDL[Apply PostgreSQL DDL<br/>oltp_schema_psql.sql]
    
    ApplyDDL --> CreatePGTables[Create PostgreSQL Tables]
    
    CreatePGTables --> Truncate{Truncate<br/>Flag Set?}
    
    Truncate -->|Yes| DeleteData[DELETE FROM tables]
    Truncate -->|No| SkipTruncate[Skip truncation]
    
    DeleteData --> LoadStart
    SkipTruncate --> LoadStart
    
    LoadStart[Start CSV Loading] --> CountBefore[Count rows BEFORE load]
    
    CountBefore --> TryCopy1[Try Method 1:<br/>psycopg2 COPY]
    
    TryCopy1 --> Copy1Success{Success?}
    
    Copy1Success -->|Yes| ValidateRows
    Copy1Success -->|No| TryCopy2[Try Method 2:<br/>psycopg v3 COPY]
    
    TryCopy2 --> Copy2Success{Success?}
    
    Copy2Success -->|Yes| ValidateRows
    Copy2Success -->|No| TryPsql[Try Method 3:<br/>psql \copy CLI]
    
    TryPsql --> PsqlSuccess{Success?}
    
    PsqlSuccess -->|Yes| ValidateRows
    PsqlSuccess -->|No| Fallback[Fallback Method 4:<br/>pandas to_sql]
    
    Fallback --> ChunkSize[Start with<br/>chunksize=10000]
    
    ChunkSize --> PandasLoad{Load<br/>Success?}
    
    PandasLoad -->|Parameter Limit Error| Reduce[Reduce chunksize<br/>÷ 10]
    Reduce --> PandasLoad
    
    PandasLoad -->|Other Error| FatalError([❌ Fatal Error])
    
    PandasLoad -->|Success| ValidateRows[Count rows AFTER load]
    
    ValidateRows --> Compare{after_count ><br/>before_count?}
    
    Compare -->|No| SilentFail[❌ Silent Failure Detected]
    SilentFail --> FatalError
    
    Compare -->|Yes| NextTable{More<br/>Tables?}
    
    NextTable -->|Yes| CountBefore
    NextTable -->|No| SmokeTe[Run Smoke Tests<br/>Validate row counts]
    
    SmokeTe --> PrintSummary[Print Summary Statistics]
    
    PrintSummary --> Complete([✅ Migration Complete])
    
    style Start fill:#4caf50,color:#fff
    style Complete fill:#4caf50,color:#fff
    style FatalError fill:#f44336,color:#fff
    style Copy1Success fill:#ff9800,color:#fff
    style Copy2Success fill:#ff9800,color:#fff
    style PsqlSuccess fill:#ff9800,color:#fff
    style Compare fill:#ff9800,color:#fff
    style TryCopy1 fill:#2196f3,color:#fff
    style TryCopy2 fill:#2196f3,color:#fff
    style TryPsql fill:#2196f3,color:#fff
    style Fallback fill:#9c27b0,color:#fff
```

### 4. Data Warehouse Build Flow

```mermaid
flowchart TD
    Start([Start DW Build]) --> ReadOLTP[Read OLTP Database<br/>oltp.db]
    
    ReadOLTP --> ExtractCustomers[Extract Customers]
    ReadOLTP --> ExtractProducts[Extract Products]
    ReadOLTP --> ExtractOrders[Extract Orders]
    ReadOLTP --> ExtractItems[Extract Order Items]
    
    ExtractCustomers --> BuildDimCust[Build dim_customer<br/>- Add surrogate key<br/>- Preserve attributes<br/>- 17K rows]
    
    ExtractProducts --> BuildDimProd[Build dim_product<br/>- Add surrogate key<br/>- Preserve hierarchy<br/>- 3.8K rows]
    
    ExtractOrders --> ExtractDates[Extract Unique Dates]
    ExtractDates --> BuildDimDate[Build dim_date<br/>- Generate date_key YYYYMMDD<br/>- Compute year, quarter, month<br/>- Compute weekday, is_weekend<br/>- 1.5K rows]
    
    ExtractOrders --> ExtractRegions[Extract Unique Regions]
    ExtractRegions --> BuildDimRegion[Build dim_region<br/>- Add surrogate key<br/>- 24 rows]
    
    ExtractItems --> JoinOrders[Join with orders table]
    JoinOrders --> JoinCustomers[Join with customers table]
    JoinCustomers --> JoinProducts[Join with products table]
    
    BuildDimCust --> WaitDims[Wait for all dimensions]
    BuildDimProd --> WaitDims
    BuildDimDate --> WaitDims
    BuildDimRegion --> WaitDims
    
    WaitDims --> BuildFact[Build fact_sales]
    JoinProducts --> BuildFact
    
    BuildFact --> MapDateKey[Map to date_key<br/>from order_date]
    MapDateKey --> MapCustKey[Map to customer_key<br/>from customer_id]
    MapCustKey --> MapProdKey[Map to product_key<br/>from product_id]
    MapProdKey --> MapRegionKey[Map to region_key<br/>from region]
    
    MapRegionKey --> AddMeasures[Add Measures<br/>- quantity<br/>- sales<br/>- discount<br/>- profit<br/>- shipping_cost]
    
    AddMeasures --> Fact51K[51K fact rows<br/>One per order item]
    
    Fact51K --> ApplySchema[Apply DW Schema<br/>dw_schema.sql]
    
    ApplySchema --> CreateDWTables[Create Tables in dw.db]
    
    CreateDWTables --> LoadDimDate[Load dim_date]
    LoadDimDate --> LoadDimCustomer[Load dim_customer]
    LoadDimCustomer --> LoadDimProduct[Load dim_product]
    LoadDimProduct --> LoadDimRegion[Load dim_region]
    LoadDimRegion --> LoadFactSales[Load fact_sales]
    
    LoadFactSales --> CreateIndexes[Create Indexes<br/>on FK columns]
    
    CreateIndexes --> ValidateStar{Validate<br/>Star Schema?}
    
    ValidateStar -->|Failed| Error([❌ Build Failed])
    ValidateStar -->|Passed| Complete([✅ DW Build Complete])
    
    style Start fill:#4caf50,color:#fff
    style Complete fill:#4caf50,color:#fff
    style Error fill:#f44336,color:#fff
    style BuildDimCust fill:#9c27b0,color:#fff
    style BuildDimProd fill:#9c27b0,color:#fff
    style BuildDimDate fill:#9c27b0,color:#fff
    style BuildDimRegion fill:#9c27b0,color:#fff
    style BuildFact fill:#ff9800,color:#fff
    style ValidateStar fill:#ff9800,color:#fff
```

### 5. Dashboard Data Flow

```mermaid
flowchart LR
    subgraph User["👤 USER INTERACTIONS"]
        SelectCategory[Select Category]
        SelectRegion[Select Region]
        SelectDate[Select Date Range]
        AdjustSliders[Adjust Sliders<br/>Top N, Bins]
        Export[Export CSV]
    end

    subgraph Cache["💾 CACHE LAYER"]
        CacheDims[@st.cache_data<br/>Load Dimensions]
        CacheKPI[@st.cache_data<br/>Load KPIs]
        CacheSales[@st.cache_data<br/>Load Sales Data]
        CacheProducts[@st.cache_data<br/>Load Products]
        CacheCustomers[@st.cache_data<br/>Load Customers]
        CacheGeo[@st.cache_data<br/>Load Geography]
    end

    subgraph DB["🗄️ DATA WAREHOUSE"]
        DW[(dw.db<br/>Star Schema)]
        QDims[Query Dimensions<br/>for Filters]
        QKPI[Query Aggregates<br/>SUM, COUNT, AVG]
        QTime[Query Time Series<br/>GROUP BY month]
        QTop[Query Rankings<br/>ORDER BY sales DESC]
        QDist[Query Distribution<br/>Histogram bins]
        QGeo[Query Geography<br/>GROUP BY location]
    end

    subgraph Viz["📊 VISUALIZATIONS"]
        KPICards[KPI Metric Cards<br/>Sales, Orders, AOV]
        LineChart[Line Chart<br/>Monthly Sales Trend]
        BarChart[Bar Charts<br/>Top Products/Customers]
        Treemap[Treemap<br/>Category Hierarchy]
        Histogram[Histogram<br/>Order Value Distribution]
        GeoMap[Geographic Map<br/>Sales by Location]
        ReturnsChart[Returns Analysis<br/>Rate by Category]
        DrillDown[Product Drilldown<br/>Time Series]
    end

    subgraph Output["🖥️ WEB INTERFACE"]
        Browser[Browser<br/>localhost:8501]
        Sidebar[Sidebar Filters]
        MainArea[Main Dashboard Area]
        ExportBtn[CSV Export Button]
    end

    SelectCategory --> CacheDims
    SelectRegion --> CacheDims
    SelectDate --> CacheDims
    AdjustSliders --> CacheDims

    CacheDims --> QDims
    QDims --> DW

    CacheDims --> CacheKPI
    CacheDims --> CacheSales
    CacheDims --> CacheProducts
    CacheDims --> CacheCustomers
    CacheDims --> CacheGeo

    CacheKPI --> QKPI
    CacheSales --> QTime
    CacheProducts --> QTop
    CacheCustomers --> QTop
    CacheProducts --> QDist
    CacheGeo --> QGeo

    QKPI --> DW
    QTime --> DW
    QTop --> DW
    QDist --> DW
    QGeo --> DW

    QKPI --> KPICards
    QTime --> LineChart
    QTop --> BarChart
    CacheSales --> Treemap
    QDist --> Histogram
    QGeo --> GeoMap
    CacheSales --> ReturnsChart
    CacheProducts --> DrillDown

    KPICards --> MainArea
    LineChart --> MainArea
    BarChart --> MainArea
    Treemap --> MainArea
    Histogram --> MainArea
    GeoMap --> MainArea
    ReturnsChart --> MainArea
    DrillDown --> MainArea

    SelectCategory --> Sidebar
    SelectRegion --> Sidebar
    SelectDate --> Sidebar
    AdjustSliders --> Sidebar

    Sidebar --> Browser
    MainArea --> Browser
    Export --> ExportBtn
    ExportBtn --> Browser

    style User fill:#e1f5ff
    style Cache fill:#fff3e0
    style DB fill:#fce4ec
    style Viz fill:#f1f8e9
    style Output fill:#e0f2f1
```

### 6. Testing & CI/CD Flow

```mermaid
flowchart TD
    Start([Developer Commits Code]) --> GitPush[Push to GitHub]
    
    GitPush --> Trigger{GitHub Actions<br/>Trigger}
    
    Trigger --> CI[Start CI/CD Pipeline<br/>.github/workflows/ci.yml]
    
    CI --> Setup[Setup Environment<br/>- Ubuntu Latest<br/>- Python 3.9<br/>- PostgreSQL 13 Container]
    
    Setup --> Install[Install Dependencies<br/>pip install -r requirements.txt]
    
    Install --> StartPG[Start PostgreSQL Service<br/>postgres:postgres@localhost:5432]
    
    StartPG --> RunUnit[Run Unit Tests<br/>pytest test_pipeline.py]
    
    RunUnit --> UnitResult{Unit Tests<br/>Pass?}
    
    UnitResult -->|Fail| UnitFail[❌ Report Failure]
    UnitFail --> NotifyDev[Notify Developer]
    NotifyDev --> EndFail([❌ CI Failed])
    
    UnitResult -->|Pass| TestTransforms[✅ Test Transformations<br/>- clean_customer_data<br/>- clean_product_data<br/>- clean_order_data<br/>- clean_returns_data]
    
    TestTransforms --> RunIntegration[Run Integration Tests<br/>pytest test_integration_postgres.py]
    
    RunIntegration --> IntResult{Integration<br/>Tests Pass?}
    
    IntResult -->|Fail| IntFail[❌ Report Failure]
    IntFail --> NotifyDev
    
    IntResult -->|Pass| TestMigration[✅ Test PostgreSQL Migration<br/>- psycopg2 driver<br/>- psycopg v3 driver<br/>- Compare parity]
    
    TestMigration --> ValidateRows[Validate Row Counts<br/>- customers: 17,415<br/>- products: 3,788<br/>- orders: 25,728<br/>- order_items: 51,290<br/>- returns: 1,079]
    
    ValidateRows --> RowMatch{Row Counts<br/>Match?}
    
    RowMatch -->|No| RowFail[❌ Parity Check Failed]
    RowFail --> NotifyDev
    
    RowMatch -->|Yes| Coverage[Generate Coverage Report<br/>pytest --cov]
    
    Coverage --> Badge[Update Status Badge<br/>✅ Passing]
    
    Badge --> Success([✅ CI Passed])
    
    subgraph Local["💻 LOCAL TESTING"]
        DevTest[Developer Runs Tests Locally]
        DevUnit[pytest test_pipeline.py -v]
        DevInt[pytest test_integration_postgres.py -v]
        DevAll[pytest -v --cov]
        
        DevTest --> DevUnit
        DevUnit --> DevInt
        DevInt --> DevAll
    end
    
    Local -.->|Before Push| GitPush
    
    style Start fill:#4caf50,color:#fff
    style Success fill:#4caf50,color:#fff
    style EndFail fill:#f44336,color:#fff
    style UnitResult fill:#ff9800,color:#fff
    style IntResult fill:#ff9800,color:#fff
    style RowMatch fill:#ff9800,color:#fff
    style TestTransforms fill:#2196f3,color:#fff
    style TestMigration fill:#2196f3,color:#fff
    style Local fill:#e1f5ff
```

---

## Database Schema Diagrams

### OLTP Database Schema (3NF)

```mermaid
erDiagram
    CUSTOMERS ||--o{ ORDERS : places
    ORDERS ||--o{ ORDER_ITEMS : contains
    PRODUCTS ||--o{ ORDER_ITEMS : "ordered in"
    ORDERS ||--o{ RETURNS : "may have"

    CUSTOMERS {
        string customer_id PK
        string customer_name
        string segment
        string city
        string state
        string country
        string postal_code
        string region
    }

    PRODUCTS {
        string product_id PK
        string category
        string sub_category
        string product_name
    }

    ORDERS {
        string order_id PK
        string customer_id FK
        date order_date
        date ship_date
        string ship_mode
        string region
    }

    ORDER_ITEMS {
        integer item_id PK
        string order_id FK
        string product_id FK
        integer quantity
        decimal sales
        decimal discount
        decimal profit
        decimal shipping_cost
    }

    RETURNS {
        integer return_id PK
        string order_id FK
        string returned_flag
        string region
    }
```

### Data Warehouse Star Schema

```mermaid
erDiagram
    FACT_SALES }o--|| DIM_DATE : "order date"
    FACT_SALES }o--|| DIM_CUSTOMER : "purchased by"
    FACT_SALES }o--|| DIM_PRODUCT : "product sold"
    FACT_SALES }o--|| DIM_REGION : "sold in"

    DIM_DATE {
        integer date_key PK "YYYYMMDD"
        date date
        integer year
        integer quarter "1-4"
        integer month "1-12"
        integer day "1-31"
        string weekday "Monday-Sunday"
        boolean is_weekend
    }

    DIM_CUSTOMER {
        integer customer_key PK "Surrogate"
        string customer_id "Natural key"
        string customer_name
        string segment "Consumer/Corporate/Home"
        string city
        string state
        string country
        string postal_code
    }

    DIM_PRODUCT {
        integer product_key PK "Surrogate"
        string product_id "Natural key"
        string category "Furniture/Office/Tech"
        string sub_category
        string product_name
    }

    DIM_REGION {
        integer region_key PK "Surrogate"
        string region "Central/East/South/West"
    }

    FACT_SALES {
        integer fact_id PK "Surrogate"
        integer date_key FK
        integer customer_key FK
        integer product_key FK
        integer region_key FK
        integer quantity "Measure"
        decimal sales "Measure"
        decimal discount "Measure"
        decimal profit "Measure"
        decimal shipping_cost "Measure"
    }
```

---

## Directory Structure

### Project File Tree

```mermaid
graph TD
    Root[📁 ecommerce-dbms/] --> GitHub[📁 .github/]
    Root --> Data[📁 data/]
    Root --> Notebooks[📁 notebooks/]
    Root --> Scripts[📁 scripts/]
    Root --> SQL[📁 sql/]
    Root --> Tests[📁 tests/]
    Root --> Web[📁 web/]
    Root --> Config[📄 Config Files]

    GitHub --> Workflows[📁 workflows/]
    Workflows --> CI[📄 ci.yml<br/>GitHub Actions]

    Data --> RawCSV[📄 Raw CSV Files<br/>Orders, Returns]
    Data --> CleanedCSV[📄 Cleaned CSV Files<br/>5 tables]
    Data --> Archive[📁 archive/<br/>Intermediate files]
    Data --> PGLoad[📁 pg_load/<br/>PostgreSQL staging]

    Notebooks --> EDA[📄 EDA_and_Cleaning.ipynb<br/>Exploratory Analysis]

    Scripts --> Init1[📄 __init__.py]
    Scripts --> Logger[📄 logger.py<br/>Logging config]
    Scripts --> DB[📄 db.py<br/>Database connections]
    Scripts --> Transform[📄 transform.py<br/>Data cleaning]
    Scripts --> ETL[📄 etl_oltp.py<br/>Main ETL pipeline]
    Scripts --> BuildDW[📄 build_dw.py<br/>DW builder]
    Scripts --> MigratePG[📄 migrate_to_postgres.py<br/>PG orchestrator]
    Scripts --> LoadCSV[📄 load_from_csv_psql.py<br/>CSV loader]
    Scripts --> Views[📄 create_views.py<br/>SQL views]
    Scripts --> CDC[📄 cdc_extractor.py<br/>Change capture]

    SQL --> OLTPSchema[📄 oltp_schema.sql<br/>SQLite schema]
    SQL --> PGSchema[📄 oltp_schema_psql.sql<br/>PostgreSQL schema]
    SQL --> DWSchema[📄 dw_schema.sql<br/>Star schema]
    SQL --> ViewsSQL[📄 views.sql<br/>Analytical views]

    Tests --> UnitTests[📄 test_pipeline.py<br/>Unit tests]
    Tests --> IntTests[📄 test_integration_postgres.py<br/>Integration tests]

    Web --> Streamlit[📄 streamlit_app.py<br/>Dashboard app]

    Config --> GitIgnore[📄 .gitignore]
    Config --> Pytest[📄 pytest.ini]
    Config --> Reqs[📄 requirements.txt]
    Config --> Readme[📄 README.md]
    Config --> Report[📄 REPORT.md]
    Config --> Docs[📄 DOCUMENTATION.md]
    Config --> Proposal[📄 proposal.md]

    style Root fill:#4caf50,color:#fff
    style Scripts fill:#2196f3,color:#fff
    style SQL fill:#9c27b0,color:#fff
    style Data fill:#ff9800,color:#fff
    style Tests fill:#f44336,color:#fff
    style Web fill:#00bcd4,color:#fff
```

### Directory Details

```
ecommerce-dbms/
│
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions CI/CD configuration
│
├── data/                             # Data directory
│   ├── Awesome_Inc_Superstore_Orders.csv      # Raw orders data
│   ├── Awesome_Inc_Superstore_Returns.csv     # Raw returns data
│   ├── cleaned_customers.csv         # Cleaned customer data
│   ├── cleaned_products.csv          # Cleaned product data
│   ├── cleaned_orders.csv            # Cleaned order data
│   ├── cleaned_order_items.csv       # Cleaned order items data
│   ├── cleaned_returns.csv           # Cleaned returns data
│   ├── date_summary.csv              # Date analysis summary
│   ├── archive/                      # Archived intermediate files
│   │   ├── returns_with_inferred_dates.csv
│   │   ├── returns_date_matches.csv
│   │   └── ... (other analysis files)
│   └── pg_load/                      # PostgreSQL staging area
│       ├── cleaned_customers.csv
│       ├── cleaned_products.csv
│       └── ... (staged CSVs for Postgres)
│
├── notebooks/                        # Jupyter notebooks
│   └── EDA_and_Cleaning.ipynb       # Exploratory Data Analysis
│
├── scripts/                          # Python scripts
│   ├── __init__.py                   # Package initializer
│   ├── db.py                         # Database connection utilities
│   ├── logger.py                     # Logging configuration
│   ├── transform.py                  # Data transformation functions
│   ├── etl_oltp.py                   # Main ETL pipeline script
│   ├── build_dw.py                   # Data warehouse builder
│   ├── migrate_to_postgres.py        # PostgreSQL migration orchestrator
│   ├── load_from_csv_psql.py         # PostgreSQL CSV loader with fallbacks
│   ├── create_views.py               # SQL views creator
│   └── cdc_extractor.py              # Change Data Capture utility
│
├── sql/                              # SQL schema definitions
│   ├── oltp_schema.sql               # SQLite OLTP schema
│   ├── oltp_schema_psql.sql          # PostgreSQL OLTP schema
│   ├── dw_schema.sql                 # Data warehouse schema
│   └── views.sql                     # Analytical views
│
├── tests/                            # Test suite
│   ├── test_pipeline.py              # Unit tests for ETL pipeline
│   └── test_integration_postgres.py  # PostgreSQL integration tests
│
├── web/                              # Web application
│   └── streamlit_app.py              # Streamlit dashboard application
│
├── .gitignore                        # Git ignore rules
├── pytest.ini                        # Pytest configuration
├── requirements.txt                  # Python dependencies
├── README.md                         # Project README
├── REPORT.md                         # Implementation report
├── DOCUMENTATION.md                  # This file
└── proposal.md                       # Project proposal
```

---

## Detailed File Documentation

### Root Configuration Files

#### `.gitignore`
**Purpose**: Specifies files and directories that Git should ignore
**Contents**:
- Python cache files (`__pycache__`, `*.pyc`)
- Virtual environments (`.venv`, `venv/`)
- Database files (`*.db`, `*.sqlite`)
- IDE settings (`.vscode/`, `.idea/`)
- Environment files (`.env`)

#### `requirements.txt`
**Purpose**: Lists all Python package dependencies
**Key Dependencies**:
- `pandas>=2.0.0` - Data manipulation
- `sqlalchemy>=1.4.0` - Database ORM
- `streamlit>=1.28.0` - Web dashboard framework
- `plotly>=5.17.0` - Interactive visualizations
- `psycopg2-binary` - PostgreSQL driver (v2)
- `psycopg` - PostgreSQL driver (v3, optional)
- `pytest>=7.4.0` - Testing framework
- `python-dateutil` - Date parsing
- `tqdm` - Progress bars

#### `pytest.ini`
**Purpose**: Pytest configuration file
**Configuration**:
- Registers custom test markers (e.g., `integration`)
- Sets test discovery patterns
- Configures test output format

---

### SQL Schema Files (`sql/`)

#### `sql/oltp_schema.sql`
**Purpose**: Defines the normalized OLTP database schema for SQLite
**Tables Defined**:
1. **customers**
   - Primary Key: `customer_id`
   - Columns: customer_name, segment, city, state, country, postal_code, region
   
2. **products**
   - Primary Key: `product_id`
   - Columns: category, sub_category, product_name
   
3. **orders**
   - Primary Key: `order_id`
   - Foreign Key: `customer_id` → customers
   - Columns: order_date, ship_date, ship_mode, region
   
4. **order_items**
   - Primary Key: `item_id`
   - Foreign Keys: `order_id` → orders, `product_id` → products
   - Columns: quantity, sales, discount, profit, shipping_cost
   
5. **returns**
   - Primary Key: `return_id`
   - Foreign Key: `order_id` → orders
   - Columns: returned_flag, region

**Key Features**:
- Normalized to 3NF (Third Normal Form)
- Foreign key constraints enforce referential integrity
- Indexes on frequently queried columns

#### `sql/oltp_schema_psql.sql`
**Purpose**: PostgreSQL-specific OLTP schema
**Differences from SQLite Schema**:
- Uses PostgreSQL data types (e.g., `BOOLEAN`, `NUMERIC`)
- Returns table uses `BOOLEAN` for returned_flag
- Optimized for PostgreSQL's query planner
- Supports COPY command for bulk loading

#### `sql/dw_schema.sql`
**Purpose**: Defines the star schema for the data warehouse
**Dimension Tables**:

1. **dim_date**
   - Primary Key: `date_key` (YYYYMMDD format)
   - Columns: date, year, quarter, month, day, weekday, is_weekend
   - Purpose: Time dimension for temporal analysis

2. **dim_customer**
   - Primary Key: `customer_key` (surrogate key)
   - Columns: customer_id, customer_name, segment, city, state, country, postal_code
   - Purpose: Customer dimension for customer analysis

3. **dim_product**
   - Primary Key: `product_key` (surrogate key)
   - Columns: product_id, category, sub_category, product_name
   - Purpose: Product dimension for product analysis

4. **dim_region**
   - Primary Key: `region_key` (surrogate key)
   - Columns: region
   - Purpose: Geographic dimension

**Fact Table**:

5. **fact_sales**
   - Primary Key: `fact_id` (surrogate key)
   - Foreign Keys: date_key, customer_key, product_key, region_key
   - Measures: quantity, sales, discount, profit, shipping_cost
   - Grain: One row per order item
   - Purpose: Central fact table for sales analysis

**Design Pattern**: Classic star schema optimized for OLAP queries

#### `sql/views.sql`
**Purpose**: Defines analytical SQL views
**Views**:
- Aggregated sales by category
- Customer lifetime value
- Product performance metrics
- Regional sales summaries

---

### Data Files (`data/`)

#### Raw Data Files

**`Awesome_Inc_Superstore_Orders.csv`**
- **Source**: Original orders dataset
- **Rows**: ~25,000 order records
- **Columns**: Order ID, Order Date, Ship Date, Customer details, Product details, Sales metrics

**`Awesome_Inc_Superstore_Returns.csv`**
- **Source**: Original returns dataset  
- **Rows**: ~1,000 return records
- **Columns**: Returned flag, Order ID, Region

#### Cleaned Data Files

All cleaned files are generated by `scripts/etl_oltp.py` and `scripts/transform.py`:

**`cleaned_customers.csv`**
- Deduplicated customer records
- Normalized names and addresses
- Unique customer_id per customer

**`cleaned_products.csv`**
- Deduplicated product records
- Standardized category names
- Unique product_id per product

**`cleaned_orders.csv`**
- Validated order dates
- Parsed ship modes
- Foreign keys to customers

**`cleaned_order_items.csv`**
- Line-item level details
- Validated numeric fields (sales, profit, discount)
- Foreign keys to orders and products

**`cleaned_returns.csv`**
- Normalized returned_flag (Yes/No)
- Inferred return dates using order date heuristics
- Foreign keys to orders

#### Staging Directory (`data/pg_load/`)

Contains staged CSV files for PostgreSQL import:
- Additional deduplication for PostgreSQL constraints
- Column header normalization
- Boolean value conversion (Yes/No → TRUE/FALSE)
- Files named with `.staged.csv` suffix

#### Archive Directory (`data/archive/`)

Contains intermediate analysis files from the returns date inference process:
- `returns_with_inferred_dates.csv` - Returns with estimated dates
- `returns_date_matches.csv` - Date matching analysis
- Various parsing attempt logs

---

### Python Scripts (`scripts/`)

#### `scripts/__init__.py`
**Purpose**: Makes scripts directory a Python package
**Contents**: Empty file for package recognition

#### `scripts/logger.py`
**Purpose**: Centralized logging configuration
**Functions**:
```python
def get_logger(name: str) -> logging.Logger
```
**Features**:
- Configures logging format with timestamps
- Sets log levels (INFO, DEBUG, ERROR)
- Creates loggers for each module
**Usage**: `logger = get_logger('module_name')`

#### `scripts/db.py`
**Purpose**: Database connection utilities
**Functions**:
```python
def get_engine(db_path: str) -> sqlalchemy.Engine
```
**Features**:
- Creates SQLAlchemy engine from database path
- Supports SQLite and PostgreSQL connection strings
- Respects `DATABASE_URL` environment variable
- Returns reusable connection engine
**Usage**: `engine = get_engine('sqlite:///oltp.db')`

#### `scripts/transform.py`
**Purpose**: Data transformation and cleaning utilities
**Key Functions**:

1. `clean_customer_data(df: pd.DataFrame) -> pd.DataFrame`
   - Deduplicates customers
   - Standardizes address fields
   - Generates unique customer IDs

2. `clean_product_data(df: pd.DataFrame) -> pd.DataFrame`
   - Deduplicates products
   - Normalizes category names
   - Generates unique product IDs

3. `clean_order_data(df: pd.DataFrame) -> pd.DataFrame`
   - Validates date fields
   - Parses ship modes
   - Ensures referential integrity

4. `clean_order_items(df: pd.DataFrame) -> pd.DataFrame`
   - Validates numeric fields
   - Calculates derived metrics
   - Handles missing values

5. `clean_returns_data(df: pd.DataFrame) -> pd.DataFrame`
   - Infers return dates from order dates
   - Normalizes returned flags
   - Matches to orders

**Design Pattern**: Pure functions that take a DataFrame and return a transformed DataFrame

#### `scripts/etl_oltp.py`
**Purpose**: Main ETL pipeline orchestrator
**Command Line Arguments**:
```bash
python scripts/etl_oltp.py \
    --orders data/Awesome_Inc_Superstore_Orders.csv \
    --returns data/Awesome_Inc_Superstore_Returns.csv \
    --out oltp.db
```

**Workflow**:
1. **Extract**: Read raw CSV files
2. **Transform**: 
   - Call transformation functions from `transform.py`
   - Validate data quality
   - Generate cleaned CSVs
3. **Load**:
   - Apply OLTP schema (`sql/oltp_schema.sql`)
   - Insert data into SQLite database
   - Create indexes
4. **Validate**: Check row counts and constraints

**Output Files**:
- `oltp.db` - SQLite OLTP database
- Cleaned CSV files in `data/` directory

#### `scripts/build_dw.py`
**Purpose**: Data warehouse builder
**Command Line Arguments**:
```bash
python scripts/build_dw.py --oltp oltp.db --dw dw.db
```

**Workflow**:
1. **Read OLTP Data**: Query from oltp.db
2. **Build Dimensions**:
   - `dim_date`: Extract unique dates, compute date attributes
   - `dim_customer`: Transform customer records, add surrogate keys
   - `dim_product`: Transform product records, add surrogate keys
   - `dim_region`: Extract unique regions
3. **Build Fact Table**:
   - Join order_items with dimensions
   - Map to dimension keys
   - Aggregate measures
4. **Write DW**: 
   - Apply star schema (`sql/dw_schema.sql`)
   - Load dimensions and facts
   - Create indexes

**Output**: `dw.db` - SQLite data warehouse

**Key Function**:
```python
def create_dim_date(dates: pd.Series) -> pd.DataFrame
```
Creates date dimension with computed attributes (quarter, weekday, weekend flag)

#### `scripts/migrate_to_postgres.py`
**Purpose**: Orchestrates PostgreSQL migration
**Command Line Arguments**:
```bash
python scripts/migrate_to_postgres.py \
    --database-url 'postgresql+psycopg2://user:pass@host:port/db' \
    --truncate
```

**Workflow**:
1. **Prepare Staging**:
   - Create `data/pg_load/` directory
   - Copy cleaned CSVs
   - Perform additional deduplication for customers and orders
   - Normalize returns boolean values (Yes/No → TRUE/FALSE)
   
2. **Apply DDL**:
   - Execute `sql/oltp_schema_psql.sql`
   - Create tables with constraints
   
3. **Truncate** (if --truncate flag):
   - Delete existing data for idempotent runs
   
4. **Load Data**:
   - Call `load_from_csv_psql.py` for each table
   - Pass database URL and file paths
   
5. **Validate**:
   - Query row counts (smoke test)
   - Print summary statistics

**Non-Destructive**: By default, does not truncate; use `--truncate` for idempotent runs

#### `scripts/load_from_csv_psql.py`
**Purpose**: Robust CSV to PostgreSQL loader with multiple fallback strategies
**Strategy Hierarchy**:

1. **Primary: Server-side COPY (psycopg2)**
   ```python
   cursor.copy_expert("COPY table FROM STDIN WITH CSV HEADER", file)
   ```
   - Fastest method (direct server copy)
   - Requires psycopg2 driver
   
2. **Secondary: Server-side COPY (psycopg v3)**
   ```python
   with cursor.copy("COPY table FROM STDIN WITH CSV HEADER") as copy:
       copy.write(data)
   ```
   - Modern psycopg v3 API
   - Attempts if psycopg2 fails
   
3. **Tertiary: Client-side psql \copy**
   ```bash
   psql -c "\copy table FROM 'file.csv' CSV HEADER"
   ```
   - Uses psql command-line tool
   - Works when drivers fail
   
4. **Final Fallback: pandas to_sql**
   ```python
   df.to_sql('table', engine, if_exists='append', chunksize=1000)
   ```
   - Progressive chunksize reduction on parameter limit errors
   - Always succeeds but slowest

**Key Features**:
- **Staging**: Creates normalized `.staged.csv` files with matching column headers
- **Validation**: Counts rows before and after COPY to detect silent failures
- **Error Handling**: Catches driver-specific exceptions and tries next method
- **Logging**: Detailed logs of which method succeeded

**Function Signature**:
```python
def load_csv_to_postgres(
    engine: sqlalchemy.Engine,
    table_name: str,
    csv_path: Path
) -> None
```

#### `scripts/create_views.py`
**Purpose**: Creates analytical SQL views
**Workflow**:
- Reads `sql/views.sql`
- Executes view definitions on target database
- Used for creating pre-computed aggregations

#### `scripts/cdc_extractor.py`
**Purpose**: Change Data Capture (CDC) utility
**Function**: Extracts incremental changes from OLTP for DW updates
**Not actively used**: Future enhancement for real-time sync

---

### Test Suite (`tests/`)

#### `tests/test_pipeline.py`
**Purpose**: Unit tests for ETL pipeline
**Test Cases**:

1. `test_transform_customers()`
   - Tests customer deduplication
   - Validates generated customer IDs
   - Checks data types

2. `test_transform_products()`
   - Tests product normalization
   - Validates category standardization

3. `test_transform_orders()`
   - Tests date parsing
   - Validates foreign key relationships

4. `test_clean_returns()`
   - Tests returns data cleaning
   - Validates date inference logic

**Run Command**: `pytest tests/test_pipeline.py -v`

#### `tests/test_integration_postgres.py`
**Purpose**: PostgreSQL integration tests
**Test Marker**: `@pytest.mark.integration`

**Test Case**: `test_postgres_migration_parity()`
**What it Tests**:
1. Runs migration with psycopg2 dialect
2. Runs migration with psycopg v3 dialect
3. Compares row counts from both runs
4. Asserts they match (driver parity)

**Smoke Test Validation**:
- customers: 17,415 records
- products: 3,788 records
- orders: 25,728 records
- order_items: 51,290 records
- returns: 1,079 records

**Skip Condition**: Skips if migration fails (e.g., no DB connection)

**Run Command**: `pytest tests/test_integration_postgres.py -v`

---

### Web Application (`web/`)

#### `web/streamlit_app.py`
**Purpose**: Interactive analytics dashboard
**Framework**: Streamlit

**Architecture**:
```python
# Caching Layer
@st.cache_data
def load_data():
    # Query dw.db and cache results
    pass

# UI Layer
st.sidebar  # Filters
st.metric   # KPIs
st.plotly_chart  # Visualizations
```

**Data Loading Functions**:

1. `load_categories()` → List of product categories
2. `load_regions()` → List of geographic regions
3. `load_date_bounds()` → Min/max dates in dataset
4. `load_monthly_sales_filtered(...)` → Monthly sales time series
5. `load_kpis(...)` → Total sales, orders, avg order value
6. `load_top_products(...)` → Top N products by sales
7. `load_product_time_series(...)` → Product-level time series
8. `load_sales_by_category(...)` → Sales by category
9. `load_order_value_distribution(...)` → Order value histogram data
10. `load_top_customers(...)` → Top customers by sales
11. `load_returns_df()` → Returns data from CSV
12. `load_returns_rate_by_category(...)` → Return rate analysis
13. `load_sales_by_location(...)` → Geographic sales data

**Visualizations**:

1. **KPI Cards**
   - Total Sales ($)
   - Total Orders (count)
   - Average Order Value ($)
   - Displayed in 3-column layout with `st.metric`

2. **Monthly Sales Chart**
   - Line chart showing sales trend over time
   - Filterable by category, region, date range
   - CSV export button
   - Uses Plotly Express

3. **Top Products Bar Chart**
   - Top N products (configurable via slider)
   - Horizontal bar chart
   - Click to drill down

4. **Product Drilldown**
   - Time series for selected product
   - Shows monthly sales trend
   - Dropdown selection

5. **Category Treemap**
   - Hierarchical visualization of sales by category
   - Bubble size proportional to sales
   - Plotly treemap

6. **Order Value Distribution**
   - Histogram of order values
   - Adjustable bin count (slider)
   - Log scale toggle for skewed distributions

7. **Returns Analysis**
   - Bar chart: return rate by category
   - Sample table of returned orders
   - Data from `cleaned_returns.csv`

8. **Top Customers Bar Chart**
   - Top K customers (configurable via slider)
   - Total sales per customer

9. **Geographic Sales Map** (NEW)
   - Interactive world map using `scatter_geo`
   - Bubble size = sales volume
   - Color gradient = sales intensity
   - Hover: city, state, country, sales, orders
   - Natural Earth projection
   - Top 10 cities table below map

**Sidebar Filters**:
- Category dropdown (All, or specific category)
- Region dropdown (All, or specific region)
- Date range picker
- Top N slider (products)
- Top K slider (customers)
- Histogram bins slider
- Log scale checkbox

**Caching Strategy**:
- All data loading functions use `@st.cache_data`
- Cache invalidates when function parameters change
- Improves performance by avoiding redundant queries

**Error Handling**:
- Checks if `dw.db` exists before rendering
- Displays user-friendly error message if database missing
- Early `st.stop()` to prevent crashes

**Run Command**: 
```bash
streamlit run web/streamlit_app.py --server.port 8501
```

---

### CI/CD Configuration

#### `.github/workflows/ci.yml`
**Purpose**: GitHub Actions CI/CD pipeline
**Triggers**:
- Push to `main` branch
- Pull requests to `main`

**Jobs**:

**Job 1: test**
```yaml
runs-on: ubuntu-latest
steps:
  - Checkout code
  - Set up Python 3.9
  - Install dependencies
  - Run pytest
```

**Services**:
- PostgreSQL 13 container for integration tests
- Exposed on port 5432
- Credentials: postgres/postgres

**Environment Variables**:
- `DATABASE_URL`: Set to PostgreSQL service URL

**Test Execution**:
```bash
pytest -v --tb=short
```

**Status Badge**: Can be added to README.md

---

### Documentation Files

#### `README.md`
**Purpose**: Project README with setup instructions
**Sections**:
- Project overview
- Features list
- Installation instructions
- Usage examples
- Testing guide
- PostgreSQL migration guide
- Contributing guidelines

#### `REPORT.md`
**Purpose**: Implementation summary report
**Sections**:
- Components implemented
- Files changed
- Local validation results
- How to run commands
- Screenshot checklist for deliverable
- Next steps

#### `DOCUMENTATION.md` (This File)
**Purpose**: Complete technical documentation
**Sections**:
- Architecture diagrams
- File-by-file documentation
- Data flow explanations
- Setup guides

#### `proposal.md`
**Purpose**: Initial project proposal
**Contents**:
- Problem statement
- Proposed solution
- Technical approach
- Deliverables

---

## Data Flow Diagram

### Complete System Flow

```
┌───────────────────────────────────────────────────────────────┐
│                           DATA SOURCES                               │
│                                                                       │
│  ┌─────────────────────────┐  ┌──────────────────────────┐          │
│  │ Superstore_Orders.csv   │  │ Superstore_Returns.csv   │          │
│  │ (~25K rows)             │  │ (~1K rows)               │          │
│  └────────────┬────────────┘  └────────────┬─────────────┘          │
└───────────────┼──────────────────────────────┼────────────────────────┘
                │                            │
                └────────────┬───────────────┘
                             │
                             ▼
┌───────────────────────────────────────────────────────────────────────┐
│                     ETL PIPELINE (scripts/etl_oltp.py)               │
│                                                                       │
│  1. EXTRACT                                                           │
│     ├─ Read CSV files                                                │
│     └─ Parse with pandas                                             │
│                                                                       │
│  2. TRANSFORM (scripts/transform.py)                                 │
│     ├─ Clean customer data (dedupe, normalize)                       │
│     ├─ Clean product data (dedupe, standardize)                      │
│     ├─ Clean order data (validate dates)                             │
│     ├─ Clean order items (validate numerics)                         │
│     └─ Clean returns (infer dates, normalize flags)                  │
│                                                                       │
│  3. VALIDATE                                                          │
│     ├─ Check referential integrity                                   │
│     ├─ Validate data types                                           │
│     └─ Ensure completeness                                           │
│                                                                       │
│  4. LOAD                                                              │
│     ├─ Write cleaned CSVs to data/                                   │
│     ├─ Apply OLTP schema (sql/oltp_schema.sql)                       │
│     └─ Insert into SQLite (oltp.db)                                  │
└────────────────────┬──────────────────────────────────────────────────┘
                     │
                     ├───────────────────
                     │                   │
                     ▼                   ▼
┌─────────────────────────────────┐  ┌────────────────────────────────────┐
│   CLEANED CSV SNAPSHOTS      │  │      OLTP DATABASE (SQLite)        │
│                              │  │                                    │
│  data/                       │  │  oltp.db                           │
│  ├─ cleaned_customers.csv    │  │  ├─ customers (17K rows)          │
│  ├─ cleaned_products.csv     │  │  ├─ products (3.8K rows)          │
│  ├─ cleaned_orders.csv       │  │  ├─ orders (25K rows)             │
│  ├─ cleaned_order_items.csv  │  │  ├─ order_items (51K rows)        │
│  └─ cleaned_returns.csv      │  │  └─ returns (1K rows)             │
└─────────────┬────────────────┘  └──────────────┬─────────────────────┘
              │                                  │
              │                                  │
              │  PostgreSQL Migration Path       │  DW Build Path
              │                                  │
              ▼                                  ▼
┌──────────────────────────────┐  ┌───────────────────────────────────┐
│  POSTGRES MIGRATION           │  │   DW BUILDER                       │
│  (migrate_to_postgres.py)    │  │   (build_dw.py)                    │
│                               │  │                                    │
│  1. Prepare Staging           │  │   1. Read OLTP Data                │
│     └─ data/pg_load/          │  │      └─ Query oltp.db              │
│        ├─ Dedupe customers    │  │                                    │
│        ├─ Dedupe orders       │  │   2. Create Date Dimension         │
│        └─ Normalize returns   │  │      ├─ Extract unique dates       │
│                               │  │      └─ Compute attributes         │
│  2. Apply PostgreSQL DDL      │  │                                    │
│     └─ oltp_schema_psql.sql   │  │   3. Create Customer Dimension     │
│