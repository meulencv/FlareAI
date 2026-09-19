---
title: "Get Load"
description: "Get details for a specific load"
---

# Get Load

> Get details for a specific load

Retrieve details for a single load by its ID.

### Path Parameters

<ParamField path="load_id" type="string" required>
  The unique identifier of the load
</ParamField>

### Query Parameters

<ParamField query="carrier_id" type="string">
  Filter loads available to a specific carrier ID
</ParamField>

### Response

<ResponseField name="statusCode" type="number">
  HTTP status code
</ResponseField>

<ResponseField name="body" type="object">
  Response body containing the result

  <ResponseField name="load" type="object">
    The load object

    <Expandable title="Load properties">
      <ResponseField name="reference_number" type="string" required>
        Custom identifier for the load
      </ResponseField>

      <ResponseField name="contact" type="object">
        <Expandable title="Contact properties">
          <ResponseField name="name" type="string">
            Name of the contact
          </ResponseField>

          <ResponseField name="email" type="string">
            Email address
          </ResponseField>

          <ResponseField name="phone" type="string" required>
            Phone number
          </ResponseField>

          <ResponseField name="extension" type="string">
            Extension
          </ResponseField>

          <ResponseField name="type" type="string">
            Contact type
          </ResponseField>
        </Expandable>
      </ResponseField>

      <ResponseField name="type" type="enum" required>
        Type of load

        <Expandable title="Available values">
          * `owned` - Load that is already owned
          * `can_get` - Load that can be acquired
        </Expandable>
      </ResponseField>

      <ResponseField name="stops" type="array" required>
        List of stops for the load in order of stop sequence

        <Expandable title="Stop properties">
          <ResponseField name="type" type="enum" required>
            Type of stop

            <Expandable title="Available values">
              * `origin` - Origin location
              * `destination` - Destination location
              * `pick` - Pickup location
              * `drop` - Drop-off location
            </Expandable>
          </ResponseField>

          <ResponseField name="location" type="object" required>
            <Expandable title="Location properties">
              <ResponseField name="city" type="string" required>
                City name
              </ResponseField>

              <ResponseField name="state" type="string" required>
                State code
              </ResponseField>

              <ResponseField name="zip" type="string" required>
                ZIP/Postal code
              </ResponseField>

              <ResponseField name="country" type="string" required>
                Country name
              </ResponseField>
            </Expandable>
          </ResponseField>

          <ResponseField name="stop_timestamp_open" type="string">
            Timestamp for stop window open (format: YYYY-MM-DDTHH:MM:SS without timezone)
          </ResponseField>

          <ResponseField name="stop_timestamp_close" type="string">
            Timestamp for stop window close (format: YYYY-MM-DDTHH:MM:SS without timezone)
          </ResponseField>
        </Expandable>
      </ResponseField>

      <ResponseField name="max_buy" type="number" required>
        Maximum buying rate for the load (numeric with up to 2 decimal places)
      </ResponseField>

      <ResponseField name="status" type="enum" required>
        Current status of the load

        <Expandable title="Available values">
          * `at_pickup` - Load is at pickup location
          * `picked_up` - Load has been picked up
          * `at_delivery` - Load is at delivery location
          * `dispatched` - Load has been dispatched
          * `delivered` - Load has been delivered
          * `en_route` - Load is en route
          * `in_transit` - Load is in transit
          * `completed` - Load is completed
          * `available` - Load is available for booking
          * `covered` - Load has been covered
          * `unavailable` - Load is unavailable
        </Expandable>
      </ResponseField>

      <ResponseField name="is_partial" type="boolean" required>
        Whether this is a partial load
      </ResponseField>

      <ResponseField name="is_hazmat" type="boolean" required>
        Whether this is a hazmat load
      </ResponseField>

      <ResponseField name="posted_carrier_rate" type="number" required>
        Rate posted for carriers (numeric with up to 2 decimal places)
      </ResponseField>

      <ResponseField name="sale_notes" type="string">
        Additional notes about the sale
      </ResponseField>

      <ResponseField name="branch" type="string">
        Branch handling the load
      </ResponseField>

      <ResponseField name="commodity_type" type="string" required>
        Type of commodity being transported in a human readable format
      </ResponseField>

      <ResponseField name="weight" type="number">
        Weight of the load in pounds (numeric with up to 2 decimal places)
      </ResponseField>

      <ResponseField name="number_of_pieces" type="integer">
        Number of pieces in the load
      </ResponseField>

      <ResponseField name="miles" type="integer">
        Total miles for the trip
      </ResponseField>

      <ResponseField name="dimensions" type="string">
        Dimensions of the load
      </ResponseField>

      <ResponseField name="bridge" type="object">
        Integration status information

        <Expandable title="Bridge properties">
          <ResponseField name="status" type="enum" required>
            Integration processing status

            <Expandable title="Available values">
              * `success` - Load was successfully processed and integrated
              * `failed` - Load processing failed
            </Expandable>
          </ResponseField>

          <ResponseField name="bridge_load_id" type="string">
            The ID assigned to this load in the bridge system (when status is success)
          </ResponseField>
        </Expandable>
      </ResponseField>

      <ResponseField name="equipment_type" type="string" required>
        Equipment type required for the load. Must be one of: `Dry Van`, `Reefer`, `Flatbed`, `Step Deck`, `Box Truck`, `Power Only`
      </ResponseField>
    </Expandable>
  </ResponseField>
</ResponseField>

### Status Codes

<ResponseField name="200" type="number">
  Successfully retrieved the load
</ResponseField>

<ResponseField name="404" type="number">
  Load not found with the specified ID
</ResponseField>

<ResponseField name="409" type="number">
  Multiple loads found with the same ID
</ResponseField>

<ResponseField name="500" type="number">
  Internal server error.
</ResponseField>

<RequestExample>
  ```bash Request theme={null}
  curl --request GET \
       --url 'https://api.example.com/api/v1/loads/LOAD123' \
       --header 'Authorization: Bearer API_KEY'
  ```
</RequestExample>

<ResponseExample>
  ```json Response 200 Success theme={null}
  {
    "statusCode": 200,
    "body": {
      "load": {
      "reference_number": "LOAD123",
      "contact": {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "15552220123",
        "extension": "123",
        "type": "assigned"
      },
      "type": "owned",
      "stops": [
        {
          "type": "origin",
          "location": {
            "city": "Chicago",
            "state": "IL",
            "zip": "60601",
            "country": "US"
          },
          "stop_timestamp_open": "2024-03-20T14:00:00",
          "stop_timestamp_close": "2024-03-20T16:00:00"
        },
        {
          "type": "destination",
          "location": {
            "city": "New York",
            "state": "NY",
            "zip": "10001",
            "country": "US"
          },
          "stop_timestamp_open": "2024-03-21T14:00:00",
          "stop_timestamp_close": "2024-03-21T16:00:00"
        }
      ],
      "equipment_type": "Dry Van",
      "max_buy": 1500.50,
      "status": "available",
      "is_partial": false,
      "is_hazmat": false,
      "posted_carrier_rate": 1200.00,
      "weight": 40000,
      "number_of_pieces": 100,
      "commodity_type": "Automobile Parts",
      "sale_notes": "This is a test load",
      "dimensions": "53 Feet",
      "branch": "Chicago",
      "miles": 500,
      "bridge": {
        "status": "success",
        "bridge_load_id": "BRK-456789"
      }
      }
    }
  }
  ```

  ```json 404 Not Found theme={null}
  {
    "statusCode": 404,
    "body": {
      "error": "Load not found with the specified ID"
    }
  }
  ```

  ```json 409 Conflict theme={null}
  {
    "statusCode": 409,
    "body": {
      "error": "Multiple loads found with the same ID"
    }
  }
  ```

  ```json 500 Internal Server Error theme={null}
  {
    "statusCode": 500,
    "body": {
      "error": "Internal server error."
    }
  }
  ```
</ResponseExample>

---

Fuente original: https://docs.happyrobot.ai/bridge-api-reference/your-api/find-load
