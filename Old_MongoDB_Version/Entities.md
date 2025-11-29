###### Entities
# USER -> (Super Entity) Stores all people common Info
ID_USER                   -> INT (PK, Auto-increment)
USERNAME                  -> VARCHAR(20)
PSSWD_HASH                -> VARCHAR(50)
NAME                      -> VARCHAR(100)
CONTACT                   -> VARCHAR(20)
ADDRESS                   -> VARCHAR(255)
EMAIL                     -> VARCHAR(100)
CREATED_AT                -> TIMESTAMP [Default CURRENT_TIMESTAMP]
UPDATED_AT                -> TIMESTAMP [Default CURRENT_TIMESTAMP]
ROLE                      -> VARCHAR(16)

# CLIENT -> (Sub Entity) Inherits all info from USER
ID_USER                   -> INT (PK, Auto-increment)
Tax_ID                    -> VARCHAR(50) [For business clients]

# EMPLOYEE (Super Entity) Stores all employtee common Info
ID_Employee              -> INT (PK, Auto-increment)
Position                 -> VARCHAR(32) [Driver, Staff] [Discriminator attribute]
Schedule                 -> TEXT
Wage                     -> DECIMAL(10,2) [Hourly or monthly rate]
Is_active                -> BOOLEAN [True/False ]
Hire_date                -> DATE

# EMPLOYEE_DRIVER (Sub Entity) Inherits all info from USER and EMPLOYEE
# Only for drivers
ID_Employee              -> INT (PK, Auto-increment)
License_number           -> VARCHAR(50) [UNIQUE]
License_Category         -> VARCHAR(20) [Category A, B, C, D - for different vehicle types]
License_expiry_date      -> DATE
Driving_experience_years -> INT
Driver_status            -> VARCHAR(20) [Available, On_Route, Off_Duty, On_Break]

# EMPLOYEE_STAFF (Sub Entity) Inherits all info from USER and EMPLOYEE
# Only For employees that work inside the PO
ID_Employee              -> INT (PK, Auto-increment)
Department               -> VARCHAR(50) [Customer_Service, Sorting, Administration]

# INVOICE -> Registry of the items a client wants to send, knowing he may want to send diff packages to diff places and paying them altogether
ID_Invoice         -> INT (PK, Auto-increment)
Invoice_status       -> VARCHAR(30) [Pending, Completed, Cancelled, Refunded]
Invoice_type         -> VARCHAR(50) [Paid_on_Send, Paid_On_Delivery]
Quantity                 -> INT [Number of items/stamps/services]
Invoice_datetime     -> TIMESTAMP [When transaction occurred]
Cost                     -> DECIMAL(10,2) [Total cost]
Paid                     -> BOOLEAN [True/False ]
Payment_method           -> VARCHAR(30) [Cash, Card, Mobile_Payment, Account]
Morada                   -> TEXT
Contacto                 -> TEXT

# DELIVERY -> Each Package to be delivered
ID_Delivery              -> INT (PK, Auto-increment)
Tracking_number          -> VARCHAR(50) [UNIQUE]
Description              -> (Special_instructions)
Sender_name              -> VARCHAR(100)
Sender_address           -> TEXT
Sender_phone             -> VARCHAR(20)
Sender_email             -> VARCHAR(100)
Recipient_name           -> VARCHAR(100)
Recipient_address        -> TEXT
Recipient_phone          -> VARCHAR(20)
Recipient_email          -> VARCHAR(100)
Item_type                -> VARCHAR(20) ['letter', 'package', 'express', 'registered']
Weight                   -> INT (grams)
Dimensions               -> VARCHAR(50)  ["30x20x10 cm"]
Status                   ->  VARCHAR(20) ['Registered', 'Sorted', 'Ready', 'Out_for_Delivery', 'Delivered', 'Failed', 'Returned']
Priority                 ->  VARCHAR(20) ['low', 'normal', 'high', 'urgent'] [Default 'normal']
Registered_at            -> TIMESTAMP [Default CURRENT_TIMESTAMP]
Updated_at               -> TIMESTAMP [Default CURRENT_TIMESTAMP ON UPDATE]
In_transition             -> BOOLEAN [True/False ]

# ROUTE -> Trip containing every individual packages
ID_Route                 -> INT (PK, Auto-increment)
Description              -> TEXT [Route details, area covered, special instructions]
Delivery_status          -> VARCHAR(20) [NotStarted, On_Going, Finished, Cancelled]
Delivery_date            -> DATE
Delivery_start_time      -> TIMESTAMP
Delivery_end_time        -> TIMESTAMP
Expected_duration        -> TIME [Expected duration of route, e.g., "03:30:00" for 3.5 hours]
Kms_travelled            -> DECIMAL(8,2)
Driver_Notes             -> TEXT [In case the driver wants to add some information about the delivery]

# POST_OFFICE_STORE -> Physical storage zones/warehouses within a Post Office for organizing and tracking mail items
ID_PostOffice_Store      -> INT (PK, Auto-increment)
Name                     -> VARCHAR(100)
Address                  -> VARCHAR(255)
Contact                  -> VARCHAR(20)
PO_Shedule               -> TEXT
Maximum_storage_capacity -> INT (kgs? or m^3?)

# VEHICLE -> Registar each vehicle of the PO info
ID_Vehicle               -> INT (PK, Auto-increment)
Vehicle_type             -> VARCHAR(50) [Van, Truck, Motorcycle, Bicycle, Car,..]
Plate_number             -> VARCHAR(20) [UNIQUE]
Capacity                 -> DECIMAL(10,2) [Weight in kg or volume in m³]
Brand                    -> VARCHAR(50) [Ford, Mercedes, Honda, etc.]
Model                    -> VARCHAR(50)
Vehicle_status           -> VARCHAR(20) [Available, In_Use, Maintenance, Out_of_Service]
Year                     -> INT
Fuel_type                -> VARCHAR(30) [Diesel, Petrol, Electric, Hybrid]
Last_maintenance_date    -> DATE

# NOTIFICATION
Notification_ID          -> INT (PK, Auto-increment)
Notification_type        -> VARCHAR(20) ["sms", "email", "push", "whatsapp"] [Not Null]
Recipient_contact        -> VARCHAR(100) [Not Null] [Phone number for SMS/WhatsApp or email]
Subject                  -> VARCHAR(200) [Nullable] [Email subject line or notification title]
Message                  -> TEXT [Not Null] [Full notification message content]
Status                   -> VARCHAR(20) ["pending", "sent", "delivered", "failed"] [Not Null]
Error_message            -> TEXT [Nullable] [Error details if status=failed]
Created_at               -> TIMESTAMP [Default CURRENT_TIMESTAMP]








