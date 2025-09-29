# Report

## Design & Data Model

**Entities**

* **POIType** *(name, [attributes])*  -  defines the attribute schema for POIs of that type.
* **POI** *(id, name, type_name, x:int, y:int, attributes:dict)*  -  lives on a fixed **1000×1000** integer grid (`0..999` inclusive). For large‑area POIs (e.g., beach/forest), we store the **center** coordinate. Names and coordinates are immutable after insertion. 
* **Visitor** *(id, name, nationality)*.
* **Visit** *(visitor_id, poi_id, date dd/mm/yyyy, rating 1–10 optional)*. We store visit events; all "counts per …" queries use **distinct** semantics unless stated otherwise. 

**Invariants**

* **Type deletion constraint:** a POI type can be deleted **only if no POIs** of that type exist. 
* **POI identifiers are unique and never reused.** Deleting `id=X` does not free it for reuse. Names and coordinates are immutable (no "update" operation). 
* **Coordinate bounds:** `(x,y)` are integers in `[0,999]`. 

**Persistence / Pre‑configuration format**

* **Human‑readable config** accepted as YAML (preferred if `pyyaml` exists) or JSON with this structure:

```yaml
poi_types:
  - name: park
    attributes: [size, playground]
  - name: museum
    attributes: [theme]
  - name: beach
    attributes: [lifeguard_on_duty]

pois:
  - id: 1
    name: Green Park
    type: park
    x: 10
    y: 10
    attributes: {size: small, playground: true}
  - id: 2
    name: Blue Museum
    type: museum
    x: 20
    y: 20
    attributes: {theme: art}
  - id: 3
    name: Sunny Beach
    type: beach
    x: 30
    y: 10
    attributes: {lifeguard_on_duty: false}
  - id: 4
    name: Riverside Park
    type: park
    x: 12
    y: 10
    attributes: {size: large, playground: false}

visitors:
  - {id: 1, name: Amal,  nationality: UAE}
  - {id: 2, name: Omar,  nationality: Jordan}
  - {id: 3, name: Zara,  nationality: Pakistan}

visits:
  - {visitor_id: 1, poi_id: 1, date: "01/06/2024", rating: 9}
  - {visitor_id: 2, poi_id: 1, date: "14/06/2024"}
  - {visitor_id: 2, poi_id: 2, date: "15/06/2024"}
  - {visitor_id: 2, poi_id: 3, date: "16/06/2024"}
  - {visitor_id: 3, poi_id: 1, date: "16/06/2024"}
  - {visitor_id: 3, poi_id: 2, date: "17/06/2024"}
```

The loader is robust to missing/extra fields and validates against the rules above, as required in **Initialization & Pre‑configuration**. It reports and skips invalid items with clear warnings. 

**Optional extensions implemented**

* **Rename attribute (with migration)** and **rename POI type** (propagates to existing POIs). Documented under Edge Policies.

---

## Edge Policies

* **Boundary ε policy.** Let `ε = 1e−6`.

  * "Within radius" uses `d ≤ r + ε`.
  * "Exactly at radius" uses `|d − r| ≤ ε`.
  * Distances are Euclidean; large‑area POIs use their stored center. These rules prevent exclusion or duplication of boundary points, per **Boundary correctness** in Queries §4.6. 
* **Tie‑break rules.**

  * For **k closest** results, sort by *(distance asc, poi_id asc, name asc)*.
  * For "top‑k by counts," sort by *(count desc, id asc, name asc)*, matching the **deterministic ordering** guideline. 
* **Counting rules.** All "number of X per Y" counts are **distinct** (each visitor counts at most once per POI, and vice versa), aligned with **Counting Conventions**. 
* **Coordinate bounds.** All `(x,y)` must be integers in `[0,999]`; validations reject out‑of‑range or non‑integer inputs. 
* **Optional rename policies.**

  * *Attribute rename:* migrate every POI of that type; unmatched attributes are created with `None`.
  * *Type rename:* update the type registry and rewrite `type_name` in all affected POIs.

---

## Usage Guide

### Running the CLI

```bash
python -m poi_system.cli
```

### Sample menu session (using the configuration above)

1. **Load configuration** → choose `1` and paste the file path. You'll see warnings (if any) listed.
2. **PQ2 – Closest pair** → `13` → Output (with sample data):
   `((1, 'Green Park', (10, 10)), (4, 'Riverside Park', (12, 10)), 2.0)`  -  Green Park & Riverside Park are 2 units apart. 
3. **PQ4 – Within radius** → `15` → enter `x=10, y=10, r=12` →
   `(1, 'Green Park', (10, 10), 'park', 0.0)`
   `(4, 'Riverside Park', (12, 10), 'park', 2.0)` 
4. **PQ5 – k closest** → `16` → enter `x=10, y=10, k=2` →
   `(1, 'Green Park', (10, 10), 'park', 0.0)`
   `(4, 'Riverside Park', (12, 10), 'park', 2.0)` 
5. **Boundary correctness (PQ6a/b)** → `17` → enter `x=10, y=10, r=2` →
   `(4, 'Riverside Park', (12, 10), 'park', 2.0)` (exactly at `r`, included by ε equality). 
6. **VQ4 – Top‑k visitors by distinct POIs** → `21` → enter `k=2` →
   `(2, 'Omar', 3)`
   `(3, 'Zara', 2)` 
7. **VQ5 – Top‑k POIs by distinct visitors** → `22` → enter `k=2` →
   `(1, 'Green Park', 3)`
   `(2, 'Blue Museum', 2)` 
8. **Coverage Fairness (VQ7)** → `23` → enter `m=2, t=2` →
   `(2, 'Omar', 'Jordan', 3, 3)`
   `(3, 'Zara', 'Pakistan', 2, 2)` 

> The menu labels and required queries (PQ2, PQ4/5, VQ4/5, boundary correctness, coverage fairness) come directly from the **Queries** section. 

---

## Reflection 

Several trade‑offs guided this implementation. First, I chose an **in‑memory registry** (Python dicts and dataclasses) for simplicity and speed of iteration. The assignment does not require persistence beyond a configuration loader, so avoiding a database reduced complexity and made test‑driven development straightforward. If scaled to much larger datasets, swapping in a persistent store and indexes would be advisable; for now, memory is adequate.

For **closest pair**, I used the straightforward **O(n²)** search instead of a plane‑sweep or divide‑and‑conquer approach. Given typical class‑assignment scales, this keeps the code clear and deterministic without premature optimization. A future enhancement could introduce spatial indexing (e.g., k‑d tree) once the problem size justifies it.

Handling **floating‑point boundaries** is subtle. I standardized on `ε = 1e−6` and wrapped comparisons (`≤` and equality) in helpers to prevent exclusion or duplication on the boundary. This aligns with the brief's emphasis on robust boundary correctness and keeps numerical concerns localized. Picking the ε is necessarily heuristic; `1e−6` comfortably exceeds binary rounding noise for small integer coordinates yet is small relative to typical distances.

The **type deletion constraint** and **ID non‑reuse** were modeled explicitly: a set tracks all used POI IDs (even after deletion), and type deletion validates that no POIs of that type remain. These choices enforce the invariants at the data layer, reducing the chance that later features violate them.

For **counting semantics**, the brief's default of **distinct** (unique visitors per POI, unique POIs per visitor) is implemented using sets before aggregation. This avoids subtle bugs where repeat visits inflate counts. At the same time, visit events are stored with dates and optional ratings, enabling future queries that do need multiplicity.

I implemented the **optional rename extensions** because they exercise schema evolution. Attribute rename migrates every POI in that type; if a POI lacks the old attribute, a `None` is created for the new field - an explicit, debuggable policy. Type rename rewrites references inside the registry for consistency. Both operations are guarded by validation and tested.

Finally, I emphasized **deterministic ordering** (tie‑breaks by ID, then name) so outputs are stable across runs and easy to test. Overall, the design prioritizes correctness, clarity, and testability over micro‑optimizations - appropriate for the assignment's goals and evaluation criteria. 

# AI Usage Log

| Prompt                                                                                                                                                                                               | Verification (method & result)                                                                                                                                                                                                                                                                                                                             |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | 
| "Implement a POI Management System with 1000×1000 grid, immutable POI names/coords, never‑reused POI IDs, type deletion constraint, and visitor records with date (dd/mm/yyyy) and optional rating." | Wrote unit tests for invariants and insert/delete flows; attempted deletions of types with extant POIs correctly blocked; duplicate POI IDs rejected; date/ratings validated → **accepted**. |                            
| "Design ε‑safe comparisons for 'within radius' (≤ r) and 'exactly at radius' (                                                                                                                       abs( d−r                                                                                                                                                                                          ) ≤ε). Choose ε and justify." | Boundary tests: points at r and slightly beyond; ε=1e−6 admitted boundary exactly once; no duplicates; "within r" and "exactly r" suites passed → **accepted**. |
| "Specify deterministic tie‑break rules for k‑closest and top‑k counts."                                                                                                                              | Created tests with equal distances and equal counts; outputs sorted by (distance,id,name) and (count desc,id,name) respectively; matched expectations → **accepted**.                        |                             
| "Implement PQ2 (closest pair) simply; discuss complexity trade‑off."                                                                                                                                 | Generated O(n²) implementation; tests with three POIs confirmed correct pair; discussion added to Reflection; scalability acceptable for assignment scale → **accepted**.                    |                         
| "Write robust YAML/JSON config loader that returns warnings for skipped/invalid items and ignores extra keys."                                                                                       | Built a config with a duplicated POI id; loader returned warnings["pois"] length 1; valid items loaded; queries ran successfully → **accepted**.                                             |                            
| "Implement rename attribute (with migration) and rename type; define policy for missing attributes."                                                                                                 | Tests: rename "theme"→"topic" migrated existing POIs; missing fields set to None; type rename reflected in POIs; no data loss → **accepted**.                                                |                         
| "Add visitor/POI analytics: distinct visitors per POI, distinct POIs per visitor, top‑k for each."                                                                                                   | Unit tests created with small dataset; counts matched manual set calculations; tie‑break deterministic → **accepted**.                                                                       |                       
| "Provide CLI menu mapping exactly to PQ/VQ items and edge‑case tools."                                                                                                                               | Manual run: loaded sample config; executed 13, 15, 16, 17, 21, 22, 23; outputs matched test expectations and demo script → **accepted**.                                                     |                         
| "Draft README with usage, config format, and policies."                                                                                                                                              | Cross‑checked against brief sections on initialization, queries, counting conventions; content aligned; no contradictions → **accepted**.                                                    |                     
| "Create demo script and sample data that showcase PQ2, PQ4/5, VQ4/5, boundary correctness, coverage fairness."                                                                                       | Ran the script; observed outputs exactly as shown in the Report; meets demo checklist → **accepted**.                                                                                        |                            

