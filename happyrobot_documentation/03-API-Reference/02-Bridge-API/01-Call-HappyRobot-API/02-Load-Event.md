---
title: "Load Event"
description: "Create one or more loads in the system. This endpoint accepts either a single load object or an array of load objects. The response will match the input format - if you send a single object, you'll receive a single object; if you send an array, you'll receive an array."
---

# Load Event

> Create one or more loads in the system. This endpoint accepts either a single load object or an array of load objects. The response will match the input format - if you send a single object, you'll receive a single object; if you send an array, you'll receive an array.

Create a new load (or loads) with all associated details including pickup/delivery information, equipment requirements, and pricing. **This can only be used if you coordinate with us, we will need to give you an API key and the endpoint to use.**

### Authentication

This endpoint requires an API key in the X-API-Key header:

```bash theme={null}
X-API-Key: <your_api_key>
```

### Body

**Input Format**: This endpoint accepts either a single load object or an array of load objects. The response will match the input format.

<ParamField body="load_data" type="object|array" required>
  **Single Load Object**: Send a single load object to create one load **Array
  of Load Objects**: Send an array of load objects to create multiple loads The
  response will match the input format: - Single object input → Single object
  response - Array input → Array response
</ParamField>

<ParamField body="event_type" type="string" required>
  Type of event. Must be 'load\_upsert'.
</ParamField>

<ParamField body="org_id" type="string">
  Your organization's unique identifier
</ParamField>

<ParamField body="custom_load_id" type="string" required>
  Custom identifier for the load (This is the load number you use in your TMS)
</ParamField>

<ParamField body="equipment_type_name" type="string">
  Name of the required equipment type
</ParamField>

<ParamField body="status" type="enum" required>
  Load status. Must be one of: - `at_pickup` - `picked_up` - `at_delivery` -
  `dispatched` - `delivered` - `en_route` - `in_transit` - `completed` -
  `available` - `covered` - `unavailable`
</ParamField>

<ParamField body="posted_carrier_rate" type="number">
  Rate posted for carriers (numeric with up to 2 decimal places)
</ParamField>

<ParamField body="type" type="enum" default="owned">
  Type of load. Must be one of: - `owned` - `can_get`
</ParamField>

<ParamField body="is_partial" type="boolean" default="false">
  Whether this is a partial load
</ParamField>

<ParamField body="contacts" type="array">
  List of contacts for this load

  <Expandable title="Contact properties">
    <ParamField body="name" type="string" required>
      Name of the contact
    </ParamField>

    <ParamField body="email" type="string" required>
      Email address
    </ParamField>

    <ParamField body="phone" type="string" required>
      Phone number (digits only)
    </ParamField>

    <ParamField body="type" type="enum" required>
      Contact type. Must be one of: - `assigned` - `transfer`
    </ParamField>

    <ParamField body="extension" type="string">
      Phone extension
    </ParamField>
  </Expandable>
</ParamField>

<ParamField body="origin" type="object">
  Origin location

  <Expandable title="Location properties">
    <ParamField body="city" type="string" required>
      City name
    </ParamField>

    <ParamField body="state" type="string" required>
      State code
    </ParamField>

    <ParamField body="zip" type="string" required>
      ZIP/Postal code
    </ParamField>

    <ParamField body="country" type="string" default="US">
      Country code
    </ParamField>

    <ParamField body="address" type="string">
      Street address
    </ParamField>
  </Expandable>
</ParamField>

<ParamField body="destination" type="object">
  Destination location

  <Expandable title="Location properties">
    <ParamField body="city" type="string" required>
      City name
    </ParamField>

    <ParamField body="state" type="string" required>
      State code
    </ParamField>

    <ParamField body="zip" type="string" required>
      ZIP/Postal code
    </ParamField>

    <ParamField body="country" type="string" default="US">
      Country code
    </ParamField>

    <ParamField body="address" type="string">
      Street address
    </ParamField>
  </Expandable>
</ParamField>

<ParamField body="stops" type="array">
  List of stops for this load. NOTE: You have to pass in the origin and
  destination

  <Expandable title="Stop properties">
    <ParamField body="type" type="enum" required>
      Type of stop. Must be one of: - `origin` - `destination` - `pick` - `drop`
    </ParamField>

    <ParamField body="location" type="object" required>
      <Expandable title="Location properties">
        <ParamField body="city" type="string" required>
          City name
        </ParamField>

        <ParamField body="state" type="string" required>
          State code
        </ParamField>

        <ParamField body="zip" type="string" required>
          ZIP/Postal code
        </ParamField>

        <ParamField body="country" type="string" default="US">
          Country code
        </ParamField>

        <ParamField body="address" type="string">
          Street address
        </ParamField>
      </Expandable>
    </ParamField>

    <ParamField body="loading_type" type="string">
      Type of loading required
    </ParamField>

    <ParamField body="notes" type="string">
      Additional notes for this stop
    </ParamField>

    <ParamField body="stop_timestamp_open" type="string" required>
      Timestamp for when the stop window opens (format: YYYY-MM-DDTHH:MM:SS
      without timezone). We will not do any timezone conversions.
    </ParamField>

    <ParamField body="stop_timestamp_close" type="string" required>
      Timestamp for when the stop window closes (format: YYYY-MM-DDTHH:MM:SS
      without timezone). We will not do any timezone conversions.
    </ParamField>

    <ParamField body="stop_order" type="integer" required>
      Order of this stop in the sequence
    </ParamField>
  </Expandable>
</ParamField>

<ParamField body="max_buy" type="number">
  Maximum buying rate for the load (numeric with up to 2 decimal places)
</ParamField>

<ParamField body="sale_notes" type="string">
  Additional notes about the sale
</ParamField>

<ParamField body="branch" type="string">
  Branch handling the load
</ParamField>

<ParamField body="team" type="string">
  Team handling the load
</ParamField>

<ParamField body="commodity_type" type="string">
  Type of commodity being transported
</ParamField>

<ParamField body="weight" type="number">
  Weight of the load in pounds (numeric with up to 2 decimal places)
</ParamField>

<ParamField body="number_of_pieces" type="integer">
  Number of pieces in the load
</ParamField>

<ParamField body="miles" type="integer">
  Total miles for the trip
</ParamField>

<ParamField body="dimensions" type="string">
  Dimensions of the load
</ParamField>

<ParamField body="pickup_date_open" type="string">
  Timestamp for pickup window open (format: YYYY-MM-DDTHH:MM:SS without
  timezone). We will not do any timezone conversions.
</ParamField>

<ParamField body="pickup_date_close" type="string">
  Timestamp for pickup window close (format: YYYY-MM-DDTHH:MM:SS without
  timezone). We will not do any timezone conversions.
</ParamField>

<ParamField body="delivery_date_open" type="string">
  Timestamp for delivery window open (format: YYYY-MM-DDTHH:MM:SS without
  timezone). We will not do any timezone conversions.
</ParamField>

<ParamField body="delivery_date_close" type="string">
  Timestamp for delivery window close (format: YYYY-MM-DDTHH:MM:SS without
  timezone). We will not do any timezone conversions.
</ParamField>

<ParamField body="temp_configuration" type="string">
  Temperature configuration requirements
</ParamField>

<ParamField body="min_temp" type="number">
  Minimum temperature requirement (numeric with up to 2 decimal places)
</ParamField>

<ParamField body="max_temp" type="number">
  Maximum temperature requirement (numeric with up to 2 decimal places)
</ParamField>

<ParamField body="is_temp_metric" type="boolean">
  Whether temperature is in metric units
</ParamField>

<ParamField body="pickup_number" type="string">
  Pickup reference number
</ParamField>

<ParamField body="bol_number" type="string">
  Bill of Lading number
</ParamField>

<ParamField body="trailer_number" type="string">
  Trailer number
</ParamField>

<ParamField body="truck_number" type="string">
  Truck number
</ParamField>

<ParamField body="cargo_value" type="number">
  Value of the cargo (numeric with up to 2 decimal places)
</ParamField>

<ParamField body="is_hazmat" type="boolean">
  Whether the load contains hazardous materials
</ParamField>

<ParamField body="po_number" type="string">
  Purchase order number
</ParamField>

<ParamField body="is_team_required" type="boolean">
  Whether a team driver is required
</ParamField>

<ParamField body="un_number" type="string">
  UN number for hazardous materials
</ParamField>

<ParamField body="package_group" type="string">
  Package group for hazardous materials
</ParamField>

<ParamField body="hazmat_class" type="string">
  Hazmat class
</ParamField>

<ParamField body="is_hazardous" type="boolean">
  Whether the load is hazardous
</ParamField>

### Response

The response format matches the input format:

**Single Object Response** (when single object was sent):

<ResponseField name="id" type="string">
  The UUID of the created load
</ResponseField>

<ResponseField name="created_at" type="string">
  ISO 8601 formatted creation timestamp
</ResponseField>

**Array Response** (when array was sent):

<ResponseField name="loads" type="array">
  Array of created load objects, each containing:

  <Expandable title="Load object properties">
    <ResponseField name="id" type="string">
      The UUID of the created load
    </ResponseField>

    <ResponseField name="created_at" type="string">
      ISO 8601 formatted creation timestamp
    </ResponseField>
  </Expandable>
</ResponseField>

<RequestExample>
  ```json Creating a single load theme={null}
  {
    "event_type": "load_upsert",
    "org_id": "01111111-11aa-11aa-1111-a11111111111",
    "custom_load_id": "123455555555",
    "equipment_type_name": "Dry Van",
    "status": "available",
    "posted_carrier_rate": 1500.00,
    "max_buy": 1200.00,
    "type": "owned",
    "is_partial": false,
    "weight": 25000,
    "number_of_pieces": 10,
    "miles": 750,
    "commodity_type": "General Merchandise",
    "pickup_date_open": "2023-06-15T08:00:00",
    "pickup_date_close": "2023-06-15T12:00:00",
    "delivery_date_open": "2023-06-16T09:00:00",
    "delivery_date_close": "2023-06-16T13:00:00",
    "contacts": [
      {
        "name": "John Smith",
        "email": "john@example.com",
        "phone": "5551234567",
        "type": "assigned",
        "extension": "123"
      }
    ],
    "origin": {
      "city": "Chicago",
      "state": "IL",
      "zip": "60601",
      "country": "US",
      "address": "123 Main St"
    },
    "destination": {
      "city": "New York",
      "state": "NY",
      "zip": "10001",
      "country": "US",
      "address": "456 Park Ave"
    },
    "stops": [
      {
        "type": "origin",
        "location": {
          "city": "Chicago",
          "state": "IL",
          "zip": "60601",
          "country": "US",
          "address": "123 Main St"
        },
        "stop_timestamp_open": "2023-06-15T08:00:00",
        "stop_timestamp_close": "2023-06-15T12:00:00",
        "stop_order": 1,
        "notes": "Pickup at loading dock"
      },
      {
        "type": "pick",
        "location": {
          "city": "Cleveland",
          "state": "OH",
          "zip": "44113",
          "country": "US"
        },
        "stop_timestamp_open": "2023-06-16T09:00:00",
        "stop_timestamp_close": "2023-06-16T13:00:00",
        "stop_order": 2
      },
      {
        "type": "destination",
        "location": {
          "city": "New York",
          "state": "NY",
          "zip": "10001",
          "country": "US",
          "address": "456 Park Ave"
        },
        "stop_timestamp_open": "2023-06-17T10:00:00",
        "stop_timestamp_close": "2023-06-17T14:00:00",
        "stop_order": 3,
        "notes": "Call 30 minutes before arrival"
      }
    ],
    "min_temp": 32,
    "max_temp": 38,
    "is_temp_metric": false,
    "cargo_value": 50000,
    "is_hazmat": false,
    "is_team_required": false
  }
  ```

  ```json Creating multiple loads theme={null}
  [
    {
      "event_type": "load_upsert",
      "org_id": "01111111-11aa-11aa-1111-a11111111111",
      "custom_load_id": "123455555555",
      "equipment_type_name": "Dry Van",
      "status": "available",
      "posted_carrier_rate": 1500.0,
      "max_buy": 1200.0,
      "type": "owned",
      "is_partial": false,
      "weight": 25000,
      "number_of_pieces": 10,
      "miles": 750,
      "commodity_type": "General Merchandise",
      "pickup_date_open": "2023-06-15T08:00:00",
      "pickup_date_close": "2023-06-15T12:00:00",
      "delivery_date_open": "2023-06-16T09:00:00",
      "delivery_date_close": "2023-06-16T13:00:00",
      "contacts": [
        {
          "name": "John Smith",
          "email": "john@example.com",
          "phone": "5551234567",
          "type": "assigned",
          "extension": "123"
        }
      ],
      "origin": {
        "city": "Chicago",
        "state": "IL",
        "zip": "60601",
        "country": "US",
        "address": "123 Main St"
      },
      "destination": {
        "city": "New York",
        "state": "NY",
        "zip": "10001",
        "country": "US",
        "address": "456 Park Ave"
      },
      "stops": [
        {
          "type": "origin",
          "location": {
            "city": "Chicago",
            "state": "IL",
            "zip": "60601",
            "country": "US",
            "address": "123 Main St"
          },
          "stop_timestamp_open": "2023-06-15T08:00:00",
          "stop_timestamp_close": "2023-06-15T12:00:00",
          "stop_order": 1,
          "notes": "Pickup at loading dock"
        },
        {
          "type": "destination",
          "location": {
            "city": "New York",
            "state": "NY",
            "zip": "10001",
            "country": "US",
            "address": "456 Park Ave"
          },
          "stop_timestamp_open": "2023-06-17T10:00:00",
          "stop_timestamp_close": "2023-06-17T14:00:00",
          "stop_order": 2,
          "notes": "Call 30 minutes before arrival"
        }
      ],
      "min_temp": 32,
      "max_temp": 38,
      "is_temp_metric": false,
      "cargo_value": 50000,
      "is_hazmat": false,
      "is_team_required": false
    },
    {
      "event_type": "load_upsert",
      "org_id": "01111111-11aa-11aa-1111-a11111111111",
      "custom_load_id": "123477777776",
      "equipment_type_name": "Refrigerated",
      "status": "available",
      "posted_carrier_rate": 1800.0,
      "max_buy": 1500.0,
      "type": "owned",
      "is_partial": false,
      "weight": 30000,
      "number_of_pieces": 15,
      "miles": 850,
      "commodity_type": "Food Products",
      "pickup_date_open": "2023-06-18T09:00:00",
      "pickup_date_close": "2023-06-18T13:00:00",
      "delivery_date_open": "2023-06-19T10:00:00",
      "delivery_date_close": "2023-06-19T14:00:00",
      "contacts": [
        {
          "name": "Jane Doe",
          "email": "jane@example.com",
          "phone": "5559876543",
          "type": "assigned"
        }
      ],
      "origin": {
        "city": "Los Angeles",
        "state": "CA",
        "zip": "90210",
        "country": "US",
        "address": "789 Sunset Blvd"
      },
      "destination": {
        "city": "Phoenix",
        "state": "AZ",
        "zip": "85001",
        "country": "US",
        "address": "321 Desert Ave"
      },
      "stops": [
        {
          "type": "origin",
          "location": {
            "city": "Los Angeles",
            "state": "CA",
            "zip": "90210",
            "country": "US",
            "address": "789 Sunset Blvd"
          },
          "stop_timestamp_open": "2023-06-18T09:00:00",
          "stop_timestamp_close": "2023-06-18T13:00:00",
          "stop_order": 1,
          "notes": "Temperature controlled pickup"
        },
        {
          "type": "destination",
          "location": {
            "city": "Phoenix",
            "state": "AZ",
            "zip": "85001",
            "country": "US",
            "address": "321 Desert Ave"
          },
          "stop_timestamp_open": "2023-06-19T10:00:00",
          "stop_timestamp_close": "2023-06-19T14:00:00",
          "stop_order": 2,
          "notes": "Deliver to cold storage"
        }
      ],
      "min_temp": 28,
      "max_temp": 35,
      "is_temp_metric": false,
      "cargo_value": 75000,
      "is_hazmat": false,
      "is_team_required": false
    }
  ]
  ```
</RequestExample>

<ResponseExample>
  ```json Response for single load creation theme={null}
  {
    "id": "01111111-11aa-11aa-1111-a11111111111",
    "created_at": "2024-03-19T08:00:00Z",
    "status": "available",
    "custom_load_id": "LOAD123"
  }
  ```

  ```json Response for multiple loads creation theme={null}
  [
    {
      "id": "01111111-11aa-11aa-1111-a11111111111",
      "created_at": "2024-03-19T08:00:00Z",
      "status": "available",
      "custom_load_id": "LOAD123"
    },
    {
      "id": "02222222-22bb-22bb-2222-b22222222222",
      "created_at": "2024-03-19T08:01:00Z",
      "status": "available",
      "custom_load_id": "LOAD124"
    }
  ]
  ```
</ResponseExample>

---

Fuente original: https://docs.happyrobot.ai/bridge-api-reference/our-api/ingest-load
