---
title: "Get Loads"
description: "Search for loads matching the given criteria"
---

# Get Loads

> Search for loads matching the given criteria

Search for loads using optional filter parameters. Returns a list of matching loads with a maximum of 3 results. Depending on the use case, you may need to implement different filters, not all of these are required for everyone.

### Query Parameters

<ParamField query="origin_city" type="string">
  Filter by origin city
</ParamField>

<ParamField query="origin_state" type="string">
  Filter by origin state
</ParamField>

<ParamField query="destination_city" type="string">
  Filter by destination city
</ParamField>

<ParamField query="destination_state" type="string">
  Filter by destination state
</ParamField>

<ParamField query="equipment_type" type="string">
  Filter by equipment type name
</ParamField>

<ParamField query="reefer_min_temp" type="number">
  Filter Reefer loads by the minimum allowed temperature
</ParamField>

<ParamField query="reefer_max_temp" type="number">
  Filter Reefer loads by the maximum allowed temperature
</ParamField>

<ParamField query="pickup_date" type="string">
  Filter by pickup date (ISO 8601 format)
</ParamField>

<ParamField query="origin_lat" type="number">
  Latitude coordinate for the origin location (in decimal degrees)
</ParamField>

<ParamField query="origin_lng" type="number">
  Longitude coordinate for the origin location (in decimal degrees)
</ParamField>

<ParamField query="origin_radius" type="number">
  Search radius (in miles) from the origin coordinates
</ParamField>

<ParamField query="destination_lat" type="number">
  Latitude coordinate for the destination location (in decimal degrees)
</ParamField>

<ParamField query="destination_lng" type="number">
  Longitude coordinate for the destination location (in decimal degrees)
</ParamField>

<ParamField query="destination_radius" type="number">
  Search radius (in miles) from the destination coordinates
</ParamField>

<ParamField query="carrier_id" type="string">
  Filter loads available to a specific carrier ID
</ParamField>

### Status Codes

<ResponseField name="200" type="number">
  Successfully retrieved the list of loads
</ResponseField>

<ResponseField name="500" type="number">
  Internal server error
</ResponseField>

### Response

<ResponseField name="statusCode" type="number">
  HTTP status code
</ResponseField>

<ResponseField name="body" type="object">
  Response body containing the results

  <ResponseField name="loads" type="array">
    List of loads matching the search criteria (maximum 3 results)

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
        Dimensions of the load in a human readable format
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

<RequestExample>
  ```bash Geographic Search theme={null}
  curl --request GET \
       --url 'https://api.example.com/api/v1/loads?origin_lat=41.8781&origin_lng=-87.6298&origin_radius=50&destination_lat=40.7128&destination_lng=-74.0060&destination_radius=25' \
       --header 'Authorization: Bearer API_KEY'
  ```

  ```bash City/State Search theme={null}
  curl --request GET \
       --url 'https://api.example.com/api/v1/loads?origin_city=Chicago&destination_state=NY' \
       --header 'Authorization: Bearer API_KEY'
  ```

  ```bash Reefer with Temperature Requirements theme={null}
  curl --request GET \
       --url 'https://api.example.com/api/v1/loads?equipment_type=Reefer&reefer_min_temp=34&reefer_max_temp=38' \
       --header 'Authorization: Bearer API_KEY'
  ```
</RequestExample>

<ResponseExample>
  ```json 200 Success theme={null}
  {
    "statusCode": 200,
    "body": {
      "loads": [
      {
        "reference_number": "LOAD123",
        "contact": {
          "name": "John Doe",
          "email": "john@example.com",
          "phone": "15552220123",
          "extension": "123",
          "type": "assigned"
        },
        "type": "can_get",
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
        "posted_carrier_rate": 1200.00,
        "weight": 40000,
        "number_of_pieces": 100,
        "commodity_type": "Automobile Parts",
        "sale_notes": "This is a test load",
        "branch": "Chicago",
        "dimensions": "53 Feet",
        "miles": 500,
        "bridge": {
          "status": "success",
          "bridge_load_id": "BRK-456789"
        }
      }
      ]
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

Fuente original: https://docs.happyrobot.ai/bridge-api-reference/your-api/find-loads
