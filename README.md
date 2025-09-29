
# POI Management System (CLI)

A reference implementation of the **POI Management System** for AI1030.

- Map grid: `1000 x 1000`, integer coordinates in `[0, 999]` inclusive.
- POI identifiers are unique and **never reused** (IDs of deleted POIs remain reserved).
- POI names and coordinates are immutable (no updates; only insert/delete).
- A **POI type** can be deleted **only** if there are no POIs of that type.
- Distances use Euclidean metric with an epsilon (`EPSILON=1e-6`) to ensure **boundary correctness**.
- For large-area POIs (e.g., beach, forest), the stored coordinate is the **center** point.

> This implementation follows the assignment spec. See the PDF for the full problem statement.

## Install & Run

No third-party dependencies are required. YAML config is supported **if** `pyyaml` is available; otherwise, use JSON.

```bash
# Run the CLI
python -m poi_system.cli
```

## Configuration format (YAML or JSON)

Structure:

```yaml
poi_types:
  - name: park
    attributes: [size, has_playground]
  - name: museum
    attributes: [theme]

pois:
  - id: 1
    name: Al Noor Park
    type: park
    x: 100
    y: 120
    attributes:
      size: large
      has_playground: true

visitors:
  - id: 1
    name: Amal
    nationality: UAE
  - id: 2
    name: Omar
    nationality: Jordan

visits:
  - visitor_id: 1
    poi_id: 1
    date: "01/05/2024"
    rating: 8
```

JSON with the same keys is also accepted.

### Loader behavior & validation

- Missing optional fields are filled with reasonable defaults (`attributes` -> `{}`).
- Extra unknown keys are ignored.
- Coordinates must be integers in `[0,999]`.
- Visit date must be `dd/mm/yyyy`. Rating, if provided, must be integer `1..10`.
- POIs specify attributes **only** from the schema of their type; others are ignored.
- On completion, the loader returns a *warning dictionary* with any skipped items.

## Queries (CLI options)

- (12) **List POIs for a type** - id, name, coords, attributes.  
- (13) **Closest pair of POIs** (id, name, coords, distance).  
- (14) **Count POIs per type**.  
- (15) **Within radius**: given `c0=(x0,y0)`, `r` - POIs with distance `<= r` (uses epsilon).  
- (16) **k closest**: given `c0`, `k` - sorted by distance, then id, then name.  
- (17) **Exactly at radius**: `|d - r| <= eps`.  
- Visitor queries (18–23) implement the required statistics including **coverage fairness**.

## Edge Policies

- `EPSILON = 1e-6` (see `poi_system/utils.py`).
- When sorting by counts, ties are broken by **id ascending**, then **name ascending**.
- Counting is **distinct by default**: e.g., "number of visitors per POI" counts each visitor at most once per POI.

## Optional extensions (implemented)

- **Rename attribute** for a type with automatic migration of all existing POIs. Unmatched attributes are created with `None`.
- **Rename POI type** with consistent propagation to existing POIs.

## Tests

Run with:

```bash
python -m unittest discover -s tests -v
```

The suite contains at least 6 tests covering: distance epsilon, type/attribute updates, visitor stats, nearest queries, and config validation.
