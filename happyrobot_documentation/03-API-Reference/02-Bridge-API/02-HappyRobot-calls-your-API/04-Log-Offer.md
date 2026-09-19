---
title: "Log Offer"
description: "Record a carrier's offer for a specific load"
---

# Log Offer

> Record a carrier's offer for a specific load

Log a price offer from a carrier for a specific load in the system.

### Request Body

<ParamField body="load_id" type="string" required>
  The unique identifier of the load for which the offer is being made
</ParamField>

<ParamField body="mc_number" type="string" required>
  The Motor Carrier (MC) number of the carrier making the offer
</ParamField>

<ParamField body="carrier_offer" type="number" required>
  The price offered by the carrier in USD
</ParamField>

<ParamField body="notes" type="string">
  Additional notes or context about the offer
</ParamField>

### Response

<ResponseField name="status" type="number">
  HTTP status code indicating the result of the operation
</ResponseField>

### Status Codes

<ResponseField name="201" type="number">
  Offer successfully logged
</ResponseField>

<ResponseField name="400" type="number">
  Bad request - Missing or invalid parameters
</ResponseField>

<ResponseField name="404" type="number">
  Load or carrier not found
</ResponseField>

<ResponseField name="409" type="number">
  Conflict - An identical offer already exists
</ResponseField>

<ResponseField name="500" type="number">
  Internal server error
</ResponseField>

<RequestExample>
  ```bash Request theme={null}
  curl --request POST \
       --url 'https://api.example.com/api/v1/offers/log' \
       --header 'Content-Type: application/json' \
       --header 'Authorization: Bearer API_KEY' \
       --data '{
         "load_id": "LOAD123456",
         "mc_number": "987654",
         "carrier_offer": 1850.00,
         "notes": "Available for pickup tomorrow morning"
       }'
  ```
</RequestExample>

<ResponseExample>
  ```json 201 Success theme={null}
  {
    "status": 201
  }
  ```

  ```json 400 Bad Request theme={null}
  {
    "status": 400,
    "error": "Missing required field: carrier_offer"
  }
  ```

  ```json 404 Not Found theme={null}
  {
    "status": 404,
    "error": "Load with ID LOAD123456 not found"
  }
  ```

  ```json 409 Conflict theme={null}
  {
    "status": 409,
    "error": "An identical offer from this carrier already exists for this load"
  }
  ```

  ```json 500 Internal Server Error theme={null}
  {
    "status": 500,
    "error": "Internal server error"
  }
  ```
</ResponseExample>

---

Fuente original: https://docs.happyrobot.ai/bridge-api-reference/your-api/log-offer
