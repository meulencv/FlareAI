---
title: "Carrier Event"
description: "Create or update a carrier in the system"
---

# Carrier Event

> Create or update a carrier in the system

Create or update a carrier with their MC number and status information.  **This can only be used if you coordinate with us, we will need to give you an API key and the endpoint to use.**

### Authentication

This endpoint requires an API key in the X-API-Key header:

```bash theme={null}
X-API-Key: <your_api_key>
```

### Body

<ParamField body="event_type" type="string" required>
  Type of event. Must be 'carrier\_upsert'.
</ParamField>

<ParamField body="org_id" type="string" required>
  Your organization's unique identifier
</ParamField>

<ParamField body="mc_number" type="string">
  The carrier's MC (Motor Carrier) number
</ParamField>

<ParamField body="dot_number" type="string">
  The carrier's DOT (Department of Transportation) number
</ParamField>

<ParamField body="status" type="enum">
  Carrier's status. Must be one of: - `active` - `fail` - `inactive` - `in_review` - `not_set`
</ParamField>

<ParamField body="contacts" type="array">
  List of contacts for this carrier

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
      Contact type. Must be one of: - `primary` - `dispatch` - `billing` - `driver` - `claims`
    </ParamField>

    <ParamField body="extension" type="string">
      Phone extension
    </ParamField>

    <ParamField body="preferred_contact_method" type="enum" default="phone">
      Preferred contact method. Must be one of: - `email` - `phone` - `text`
    </ParamField>
  </Expandable>
</ParamField>

<ParamField body="markets" type="array">
  List of markets this carrier services

  <Expandable title="Market properties">
    <ParamField body="origin" type="object" required>
      Origin location for this market

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

    <ParamField body="destination" type="object" required>
      Destination location for this market

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
  </Expandable>
</ParamField>

### Response

<ResponseField name="id" type="string">
  The UUID of the created/updated carrier
</ResponseField>

<ResponseField name="created_at" type="string">
  ISO 8601 formatted creation timestamp
</ResponseField>

<RequestExample>
  ```json theme={null}
  {
    "event_type": "carrier_upsert",
    "org_id": "01111111-11aa-11aa-1111-a11111111111",
    "mc_number": "55555",
    "dot_number": "123456",
    "status": "active",
    "contacts": [
      {
        "name": "John Dispatcher",
        "email": "dispatch@abctrucking.com",
        "phone": "5551234567",
        "type": "dispatch",
        "extension": "101",
        "preferred_contact_method": "phone"
      },
      {
        "name": "Jane Driver",
        "email": "jane@abctrucking.com",
        "phone": "5559876543",
        "type": "driver",
        "preferred_contact_method": "text"
      }
    ],
    "markets": [
      {
        "origin": {
          "city": "Chicago",
          "state": "IL",
          "zip": "60601",
          "country": "US"
        },
        "destination": {
          "city": "New York",
          "state": "NY",
          "zip": "10001",
          "country": "US"
        }
      },
      {
        "origin": {
          "city": "Dallas",
          "state": "TX",
          "zip": "75201",
          "country": "US"
        },
        "destination": {
          "city": "Los Angeles",
          "state": "CA",
          "zip": "90210",
          "country": "US"
        }
      }
    ]
  }
  ```
</RequestExample>

<ResponseExample>
  ```json theme={null}
  {
    "id": "01111111-11aa-11aa-1111-a11111111111",  
    "created_at": "2024-03-19T08:00:00Z",
    "status": "active",
    "mc_number": "55555",
    "dot_number": "123456",
    "contacts": [
      {
        "name": "John Dispatcher",
        "email": "dispatch@abctrucking.com", 
        "phone": "5551234567",
        "type": "dispatch"
      }
    ],
    "markets": [
      {
        "origin": {
          "city": "Chicago",
          "state": "IL", 
          "zip": "60601"
        },
        "destination": {
          "city": "New York",
          "state": "NY",
          "zip": "10001" 
        }
      }
    ]
  }
  ```
</ResponseExample>

---

Fuente original: https://docs.happyrobot.ai/bridge-api-reference/our-api/ingest-carrier
