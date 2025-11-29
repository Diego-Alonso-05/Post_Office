###### Relationships

### USER
- All USER must be EMPLOYEE or CLIENT
Stores common data all accross entities that are people
# USER (1) ────── UserInheritance ────── (1) EMPLOYEE
# USER (1) ────── UserInheritance ────── (1) CLIENT

### EMPLOYEE (Supertype)
- Every employee is assigned to a primary post office location for administrative purposes (payroll, scheduling, reporting). Tracks which store each employee belongs to for workforce management
# EMPLOYEE (N) ────── Works_At ────── (1) POST_OFFICE_STORE
- All EMPLOYEE must be EMPLOYEE_DRIVER or EMPLOYEE_STAFF
- Stores common data all accross entities that are employees
# EMPLOYEE (1) ────── EmployeeInheritance ────── (1) EMPLOYEE_DRIVER
# EMPLOYEE (1) ────── EmployeeInheritance ────── (1) EMPLOYEE_STAFF

### EMPLOYEE_DRIVER (Subtype)
Links each route to the specific driver responsible for executing it. Essential for route planning, driver accountability, and tracking who is assigned to which deliveries on a given day
# EMPLOYEE_DRIVER (1) ────── Is_Assigned_To ────── (N) ROUTE

### EMPLOYEE_STAFF (Subtype)
Identifies which staff member (cashier/admin) handled each customer INVOICE at the counter. Used for sales performance tracking, commission calculation, and accountability for financial INVOICEs.
# PO_STAFF (1) ────── Processes ────── (N) INVOICE

### CLIENT
Links each INVOICE to the customer who initiated it. Enables customer history tracking, loyalty programs, billing, and customer service inquiries. A client can have multiple INVOICEs over time
# CLIENT (1) ────── Requests ────── (N) INVOICE
(1:N) Tracks which stores a client has used for picking up parcels. A client can pick up at one or more POST_OFFICE_STORE, and each store serves multiple clients. Used for customer convenience analysis and store traffic patterns - ???
# CLIENT (1) ────── Picks_Up_At ────── (N) POST_OFFICE_STORE - ???

### POST_OFFICE_STORE
Tracks at which post office store each INVOICE was completed. Essential for revenue tracking per location, store performance analysis, and financial reconciliation by location
# POST_OFFICE_STORE (1) ────── Records ────── (N) INVOICE
Logistics tracking - identifies which store physically dispatches the delivery route (where the delivery van departs from). This may differ from where items were registered due to inter-store transfers to consolidation/distribution hubs. Critical for operational planning and driver assignment
# POST_OFFICE_STORE (1) ────── Dispatches ────── (N) ROUTE

### INVOICE
One INVOICE can create multiple mail items (e.g., customer sends 3 packages to different addresses in one INVOICE). Links payment/billing record to the actual items being sent. Essential for financial reconciliation and itemized tracking
# INVOICE (1) ────── Generates ────── (N) DELIVERY

### DELIVERY
Identifies who is sending the mail item. Essential for returns, sender liability, tracking outgoing mail per customer, and customer service for senders
# DELIVERY (N) ────── Sent_By ────── (1) CLIENT (as Sender)
Identifies the intended recipient. Critical for delivery, notifications, failed delivery handling, and tracking incoming mail per customer. Note: Sender and recipient can be the same client (self-shipments)
# DELIVERY (N) ────── Addressed_To ────── (1) CLIENT (as Recipient)
Assigns mail items to a specific delivery route for transportation. Groups items by geographic area/delivery schedule. An item belongs to one route at a time (though it may be re-routed if delivery fails). Essential for route optimization and tracking item location
# DELIVERY (N) ────── Belongs_To ────── (1) ROUTE
Links notifications sent to customers about a specific mail item (shipment confirmation, out for delivery, delivery failed, delivered, etc.). Enables customer communication tracking and notification history audit trail
# DELIVERY (1) ────── Triggers ────── (N) NOTIFICATION

# ROUTE
Assigns a specific vehicle to each delivery route. Multiple routes can use the same vehicle on different days. Essential for vehicle scheduling, capacity planning, maintenance coordination, and ensuring vehicle availability matches route requirements
# ROUTE (N) ────── Uses ────── (1) VEHICLE

