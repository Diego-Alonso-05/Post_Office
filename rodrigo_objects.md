# CHECKLIST:
Invoice:      1, 3, 4, 6, 7, 17, 19, 20, 21, 22 = 10
InvoiceItem:  2, 15, 16, 23 = 4
Vehicle:      5, 8, 9, 24, 25, 26, 27 = 7
Route:        10, 11, 18, 28, 29, 30, 31 = 7
Dashboard:    13, 14 = 2
= 30 / 31

# NOT USED OBJECTS
12. v_invoice_totals (Invoice | View) — materialized-view-like summary not referenced by any functionality

##### INVOICES (8 functionalities)
---
| #   | Function               | URL                      | Method   | Roles             | Description                                                                                                    |
| --- | ---------------------- | ------------------------ | -------- | ----------------- | -------------------------------------------------------------------------------------------------------------- |
| 1X  | `invoice_list`         | `/invoices/`             | GET      | admin, client     | List invoices. Clients see only their own. Computes subtotal, ta  (23%), total dynamically from InvoiceItems (`qty * unit_price`). |
| 2X  | `invoice_create`       | `/invoices/create/`      | GET/POST | admin             | Create invoice + inline InvoiceItem formset (exra=1, can_delete=True). Sends notification on success.         |
| 3X  | `invoice_edit`         | `/invoices/<id>/edit/`   | GET/POST | admin             | Edit invoice + its InvoiceItems via formset. Sends notification on success.                                    |
| 4X  | `invoice_delete`       | `/invoices/<id>/delete/` | POST only| admin             | Delete invoice (cascades items). Sends notification. Flash message.                                            |
| 5   | `invoices_import_json` | `/invoices/import/json/` | GET/POST | *(no decorator)*  | Upload JSON file, create Invoice rows. Links `user_id` if provided.                                           |
| 6   | `invoices_export_json` | `/invoices/export/json/` | GET      | admin, manager    | Export all invoices as JSON download. Handles Decimal/datetime serialization. Sends notification.               |
| 7   | `invoices_export_csv`  | `/invoices/export/csv/`  | GET      | admin, manager    | Export via raw SQL: `SELECT * FROM export_invoices_csv()`. Sends notification.                                 |
| 8   | `invoices_export_pdf`  | `/invoices/export/pdf/`  | GET      | admin, client     | Generate PDF via xhtml2pdf. Clients see only their own. Computes subtotal/tax/total per invoice.               |

1 - (GET invoices/ invoice_list)
### (R)EAD INVOICES Logic
6.*v_invoices_with_items*  -> pre-joined view returning invoice header + warehouse_name, staff_name, client_name, item_count
    invoice_list: SELECT * FROM v_invoices_with_items (+ WHERE client_id = %s for clients)

CRUD OPERATIONS FOR INVOICE
    CREATE INVOICES LOGIC:
        To create and invoice we call the procedure: sp_create_invoice
        this returns the invoice id, to be used for the procedure to create this invoice items: sp_add_invoice_item
        invoice.total_item_cost column is not inserted yet, being left out intentionally to be comeplete with the trigger: trg_invoice_item_calc_total
        this triggred is fired and calls the function: fn_calculate_item_total, that calculates invoice.total_item_cost, using : qty × unit_price per item
        Now invoice_item is written and is fired: trg_invoice_update_cost, that will call the function fn_invoice_total,
        this function then calls :
            fn_invoice_subtotal: SUM of all invoice.total_item_cost   and
            fn_calculate_tax: adds the IVA (subtotal × 0.23)
    READ INVOICES LOGIC:
        We use this simple view object to list all the invoices together with the invoices items: v_invoices_with_items
        This view returns the invoice header + warehouse_name, staff_name, client_name and item_count
    UPDATE INVOICES LOGIC:
        (...)
    DELETE INVOICES LOGIC:
        (...)

---

2 - (POST invoices/<int:invoice_id>/edit/ invoice_edit)
### U(PDATE) INVOICE Logic
20.*sp_update_invoice*(id, war_id, staff_id, client_id, status, type, quantity, cost, paid, pay_method, name, address, contact)
    -> UPDATEs invoice header (COALESCE — NULL keeps existing value)
    then: DELETE FROM invoice_item WHERE inv_id = %s  -> clears all existing items
        fires: 16.*trg_invoice_update_cost*  -> invoice.cost goes to 0
    then for each item in formset:
        23.*sp_add_invoice_item*  -> re-inserts items
            fires: 15.*trg_invoice_item_calc_total*  -> sets total_item_cost
            fires: 16.*trg_invoice_update_cost*      -> recalculates invoice.cost

---

3 - (POST /invoice/create/ invoice_create)
### C(REATE) INVOICE:
19.*sp_create_invoice*(war_id, staff_id, client_id, status, type, quantity, cost, paid, pay_method, name, address, contact, p_id INOUT)
    -> INSERTs into invoice, returns new id via INOUT
    Then using this id is called sp_add_invoice_item to create the invoice_items

### C(REATE) INVOICE_ITEM : Logic to calculate INVOICE_ITEM.TOTAL_ITEM_COST
Data inserted with 23.*sp_add_invoice_item*
    the column total_item_cost is not inserted yet, being left out intentionally
        fires: 15.*trg_invoice_item_calc_total* that calculates
            using 2.*fn_calculate_item_total* : INVOICE_ITEM.TOTAL_ITEM_COST : qty × unit_price per item

### C(REATE) INVOICE :Logic to INVOICE.COST:
After invoice_item is saved, fires 16.*trg_invoice_update_cost* (AFTER INSERT/UPDATE/DELETE on invoice_item)
  16.*trg_invoice_update_cost*
      └── calls 4.*fn_invoice_total*
              ├── calls 3.fn_invoice_subtotal  ->  SUM of all items
              └── calls 1.fn_calculate_tax     ->  subtotal × 0.23
          -> result stored in invoice.cost

---

4 - (POST invoices/<int:invoice_id>/delete/ invoice_delete)
### D(ELETE) INVOICE (soft-delete):
21.*sp_delete_invoice*(id)  -> issues DELETE FROM invoice
    fires: 17.*trg_invoice_soft_delete* (BEFORE DELETE)
        -> sets status = 'cancelled', cancels the actual DELETE
        -> row stays in DB
    sp_delete_invoice verifies status = 'cancelled'  -> raises exception if invoice not found

---

5 - (GET/POST /invoices/import/json/ invoices_import_json)
### C(REATE) IMPORT INVOICE TO JSON
22.*sp_import_invoices*(p_data JSONB)  -> bulk-import invoices (+ nested items) from a JSONB array
    POST: reads uploaded JSON file, converts to JSONB, CALL sp_import_invoices(p_data)
    sp_import_invoices loops through each JSON element:
        -> INSERTs into invoice (header row), RETURNING id
        -> If JSON element has "items" array, INSERTs each into invoice_item
            fires: 15.*trg_invoice_item_calc_total*  -> sets total_item_cost
                └── calls 2.*fn_calculate_item_total*(qty, unit_price)
            fires: 16.*trg_invoice_update_cost*  -> recalculates invoice.cost
                └── calls 4.*fn_invoice_total*
                        ├── calls 3.*fn_invoice_subtotal*  -> SUM of all items
                        └── calls 1.*fn_calculate_tax*     -> subtotal × 0.23

---

6 - (GET/ /invoices/export/json/ invoices_export_json)
### (R)EAD EXPORT INVOICE TO JSON
7.*v_invoices_export*  -> flat view formatted for JSON export (all invoice columns, ORDER BY id)
    invoices_export_json: SELECT * FROM v_invoices_export
    Python handles Decimal/datetime serialization → json.dumps → HttpResponse as JSON download

---

7 - (GET/ /invoices/export/csv/ invoices_export_csv)
### (R)EAD EXPORT INVOICE TO CSV
7.*v_invoices_export*  -> flat view formatted for CSV export (same view as JSON export)
    invoices_export_csv: SELECT * FROM v_invoices_export
    Python formats rows as CSV string with header → HttpResponse as CSV download

---

8 - (GET/ /invoices/export/pdf/ invoices_export_PDF)
### (R)EAD EXPORT INVOICE TO PDF
6.*v_invoices_with_items*  -> pre-joined view returning invoice header + warehouse_name, staff_name, client_name, item_count
    invoices_export_pdf: SELECT * FROM v_invoices_with_items (+ WHERE client_id = %s for clients)
    then: SELECT * FROM invoice_item WHERE inv_id = ANY(%s)  -> fetches items per invoice
        pdf_template.html uses {{ item.total_item_cost }} (matches DB column directly)
    invoice.cost already contains subtotal + tax (computed by triggers 15, 16)
    For per-invoice subtotal/tax/total breakdown in PDF template:
        Option A (Python-computed, 0 extra DB calls):
            subtotal = sum(item["total_price"] for item in items)
            tax = subtotal × 0.23
            total = subtotal + tax  (should match invoice.cost)
        Option B (DB functions, N extra calls):
            3.*fn_invoice_subtotal*(invoice_id)  -> SUM of all item total_item_cost
            1.*fn_calculate_tax*(subtotal)        -> subtotal × 0.23
    Python renders HTML template with xhtml2pdf (pisa) → HttpResponse as PDF download



------

##### Vehicle (7 functionalities)

| #   | Function               | URL                       | Method   | Roles                | Description                                                                                    |
| --- | ---------------------- | ------------------------- | -------- | -------------------- | ---------------------------------------------------------------------------------------------- |
| 1   | `vehicles_list`        | `/vehicles/`              | GET      | admin, manager, staff| Paginated list (10/page).                                                                      |
| 2   | `vehicles_create`      | `/vehicles/create/`       | GET/POST | admin, manager       | Create vehicle via VehicleForm. Sends notification.                                            |
| 3   | `vehicles_edit`        | `/vehicles/<id>/edit/`    | GET/POST | admin, manager       | Edit vehicle via VehicleForm. Sends notification.                                              |
| 4   | `vehicles_delete`      | `/vehicles/<id>/delete/`  | POST only| admin                | Delete vehicle. Sends notification. Flash message.                                             |
| 5   | `vehicles_import_json` | `/vehicles/import/json/`  | GET/POST | admin, manager       | Upload JSON, create Vehicle rows. Strips `id` field. Uses `VehicleImportForm`. Sends notification. |
| 6   | `vehicles_export_json` | `/vehicles/export/json/`  | GET      | admin, manager, staff| Export all vehicles as JSON download. Handles date serialization. Sends notification.           |
| 7   | `vehicles_export_csv`  | `/vehicles/export/csv/`   | GET      | admin, manager       | Export via raw SQL: `SELECT * FROM export_vehicles_csv()`. Sends notification.                 |

1 - (GET vehicle/ vehicle_list)
### (R)EAD VEHICLE Logic
8.*v_vehicles_full*  -> all vehicle data for list pages (all columns, ORDER BY id)
    vehicles_list: SELECT * FROM v_vehicles_full
    Python paginates results (Paginator, 10/page)

---

2 - (POST vehicle/<int:vehicle_id>/edit/ vehicle_edit)
### U(PDATE) VEHICLE Logic
8.*v_vehicles_full*  -> used on GET to pre-populate form
    vehicles_edit GET: SELECT * FROM v_vehicles_full WHERE id = %s
25.*sp_update_vehicle*(id, vehicle_type, plate_number, capacity, brand, model, vehicle_status, year, fuel_type, last_maintenance_date, is_active)
    -> UPDATEs vehicle (COALESCE — NULL keeps existing value)
    internally calls 5.*fn_is_valid_year*(year) if year is provided -> validates year between 1900 and current+1

---

3 - (POST /vehicle/create/ vehicle_create)
### C(REATE) VEHICLE:
24.*sp_create_vehicle*(vehicle_type, plate_number, capacity, brand, model, vehicle_status, year, fuel_type, last_maintenance_date, p_id INOUT)
    -> INSERTs into vehicle, returns new id via INOUT
    internally calls 5.*fn_is_valid_year*(year) -> validates year between 1900 and current+1

---

4 - (POST vehicles/<int:vehicle_id>/delete/ vehicle_delete)
### D(ELETE) VEHICLE (hard-delete):
26.*sp_delete_vehicle*(id)  -> issues DELETE FROM vehicle
    first checks: IF EXISTS active routes (delivery_status IN ('not_started','on_going')) using this vehicle
        -> RAISE EXCEPTION if vehicle is assigned to active routes
    then: DELETE FROM vehicle WHERE id = %s
    sp_delete_vehicle raises exception if vehicle not found

---

5 - (GET/POST /vehicles/import/json/ vehicles_import_json)
### C(REATE) IMPORT VEHICLE TO JSON
27.*sp_import_vehicles*(p_data JSONB)  -> bulk-import vehicles from a JSONB array
    POST: reads uploaded JSON file, converts to JSONB, CALL sp_import_vehicles(p_data)
    sp_import_vehicles loops through each JSON element:
        -> validates year via 5.*fn_is_valid_year*(year) -> RAISE EXCEPTION if invalid (consistent with sp_create_vehicle)
        -> INSERTs into vehicle (vehicle_type, plate_number, capacity, brand, model, vehicle_status, year, fuel_type, last_maintenance_date, is_active)
        -> defaults: vehicle_status='available', is_active=true

---

6 - (GET/ /vehicles/export/json/ vehicles_export_json)
### (R)EAD EXPORT VEHICLE TO JSON
9.*v_vehicles_export*  -> flat view formatted for JSON export (all vehicle columns, ORDER BY id)
    vehicles_export_json: SELECT * FROM v_vehicles_export
    Python handles date serialization → json.dumps → HttpResponse as JSON download

---

7 - (GET/ /vehicles/export/csv/ vehicles_export_csv)
### (R)EAD EXPORT VEHICLE TO CSV
9.*v_vehicles_export*  -> flat view formatted for CSV export (same view as JSON export)
    vehicles_export_csv: SELECT * FROM v_vehicles_export
    Python formats rows as CSV string with header → HttpResponse as CSV download

---


##### Route (7 functionalities)

| #   | Function             | URL                     | Method   | Roles          | Description                                                                                                   |
| --- | -------------------- | ----------------------- | -------- | -------------- | ------------------------------------------------------------------------------------------------------------- |
| 1   | `routes_list`        | `/routes/`              | GET      | any logged-in  | Paginated list (10/page) with `select_related("driver", "vehicle", "warehouse")`.                             |
| 2   | `routes_create`      | `/routes/create/`       | GET/POST | admin          | Create route via RouteForm. Sends notification.                                                               |
| 3   | `routes_edit`        | `/routes/<id>/edit/`    | GET/POST | admin          | Edit route via RouteForm. Sends notification.                                                                 |
| 4   | `routes_delete`      | `/routes/<id>/delete/`  | POST only| admin          | Delete route. Sends notification. Flash message.                                                              |
| 5   | `routes_import_json` | `/routes/import/json/`  | GET/POST | admin, manager | Upload JSON, create Route rows. Strips `id`. Maps `vehicle_id`, `driver_id`, `warehouse_id`. Sends notification. |
| 6   | `routes_export_json` | `/routes/export/json/`  | GET      | admin, manager | Export all routes as JSON. Handles date/time/timedelta serialization. Sends notification.                     |
| 7   | `routes_export_csv`  | `/routes/export/csv/`   | GET      | admin, manager | Export via raw SQL: `SELECT * FROM export_routes_csv()`. Sends notification.                                  |

1 - (GET routes/ routes_list)
### (R)EAD ROUTES Logic
10.*v_routes_full*  -> routes joined with driver_name, license_number, license_category, plate_number, vehicle_name, warehouse_name
    routes_list: SELECT * FROM v_routes_full
    Python paginates results (Paginator, 10/page)

---

2 - (POST /routes/create/ routes_create)
### C(REATE) ROUTE:
28.*sp_create_route*(driver_id, vehicle_id, war_id, description, delivery_status, delivery_date, delivery_start_time, delivery_end_time, expected_duration, kms_travelled, driver_notes, p_id INOUT)
    -> INSERTs into route, returns new id via INOUT
    -> defaults: delivery_status='not_started', is_active=true
    fires: 18.*trg_route_time_check* (BEFORE INSERT) -> validates delivery_end_time > delivery_start_time (when both set)

---

3 - (POST routes/<int:route_id>/edit/ routes_edit)
### U(PDATE) ROUTE Logic
10.*v_routes_full*  -> used on GET to pre-populate form
    routes_edit GET: SELECT * FROM v_routes_full WHERE id = %s
29.*sp_update_route*(id, driver_id, vehicle_id, war_id, description, delivery_status, delivery_date, delivery_start_time, delivery_end_time, expected_duration, kms_travelled, driver_notes, is_active)
    -> UPDATEs route (COALESCE — NULL keeps existing value)
    fires: 18.*trg_route_time_check* (BEFORE UPDATE) -> validates delivery_end_time > delivery_start_time (when both set)

---

4 - (POST routes/<int:route_id>/delete/ route_delete)
### D(ELETE) ROUTE (hard-delete):
30.*sp_delete_route*(id)  -> issues DELETE FROM route
    first checks: IF EXISTS active deliveries (status NOT IN ('completed','cancelled')) on this route
        -> RAISE EXCEPTION if route has active deliveries
    then: DELETE FROM route WHERE id = %s
    sp_delete_route raises exception if route not found

---

5 - (GET/POST /routes/import/json/ routes_import_json)
### C(REATE) IMPORT ROUTES TO JSON
31.*sp_import_routes*(p_data JSONB)  -> bulk-import routes from a JSONB array
    POST: reads uploaded JSON file, converts to JSONB, CALL sp_import_routes(p_data)
    sp_import_routes loops through each JSON element:
        -> INSERTs into route (driver_id, vehicle_id, war_id, description, delivery_status, delivery_date, delivery_start_time, delivery_end_time, expected_duration, kms_travelled, driver_notes, is_active)
        -> defaults: delivery_status='not_started', is_active=true
        fires: 18.*trg_route_time_check* -> validates end > start for each inserted row

---

6 - (GET/ /routes/export/json/ routes_export_json)
### (R)EAD EXPORT ROUTES TO JSON
11.*v_routes_export*  -> flat view formatted for JSON export (all route columns with raw FK ids, ORDER BY id)
    routes_export_json: SELECT * FROM v_routes_export
    Python handles date/datetime/time/timedelta/Decimal serialization → json.dumps → HttpResponse as JSON download

---

7 - (GET/ /routes/export/csv/ routes_export_csv)
### (R)EAD EXPORT ROUTES TO CSV
11.*v_routes_export*  -> flat view formatted for CSV export (same view as JSON export)
    routes_export_csv: SELECT * FROM v_routes_export
    Python formats rows as CSV string with header → HttpResponse as CSV download

-----

## DASHBOARD (1 functionality)

| #   | Function    | URL  | Method | Roles         | Description                                                                                                                                                                       |
| --- | ----------- | ---- | ------ | ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `dashboard` | `/`  | GET    | any logged-in | Role-specific stats: **admin** gets counts (vehicles, deliveries, clients, employees, active routes, pending deliveries, invoices); **driver** gets own deliveries; **client/staff/manager** gets own deliveries. |

1 - (GET / dashboard)
### (R)EAD DASHBOARD Logic
13.*v_dashboard_stats*  -> simple view with cached aggregate counts (single-row):
    total_vehicles (active), total_deliveries, total_clients, total_employees (active), active_routes, pending_deliveries, total_invoices
    unique index: idx_v_dashboard_stats_pk ON ((1))  -> allows REFRESH MATERIALIZED VIEW CONCURRENTLY
    ⚠ must be refreshed periodically (e.g. after bulk imports, or via cron) — data is NOT live
\
14.*fn_get_dashboard_stats*(p_user_id INT, p_role VARCHAR(20))  -> RETURNS TABLE(stat_name TEXT, stat_value BIGINT)
    role-specific branching:
    **admin/manager** (p_role IN ('admin','manager')):
        -> RETURN QUERY: 7 rows from 13.*v_dashboard_stats* (UNION ALL):
            'total_vehicles', 'total_deliveries', 'total_clients', 'total_employees',
            'active_routes', 'pending_deliveries', 'total_invoices'
    **driver** (p_role = 'driver'):
        -> RETURN QUERY: 1 row — 'my_deliveries', COUNT(*) FROM delivery WHERE driver_id = p_user_id
    **client** (p_role = 'client'):
        -> RETURN QUERY: 1 row — 'my_deliveries', COUNT(*) FROM delivery WHERE client_id = p_user_id
    **staff/other**:
        -> RETURN QUERY: 1 row — 'total_deliveries', COUNT(*) FROM delivery

    dashboard view: SELECT * FROM fn_get_dashboard_stats(%s, %s) with (request.user.id, request.user.role)
    Python converts rows to dict: {stat_name: stat_value, ...} → render template with stats + role