---
title: "Get Carrier"
description: "Get details for a specific carrier"
---

# Get Carrier

> Get details for a specific carrier

Locate a carrier in the system using either their MC number or DOT number.

### Query Parameters

<ParamField query="mc" type="string">
  The Motor Carrier (MC) number of the carrier. Either mc or dot must be provided.
</ParamField>

<ParamField query="dot" type="string">
  The Department of Transportation (DOT) number of the carrier. Either mc or dot must be provided.
</ParamField>

### Response

<ResponseField name="statusCode" type="number">
  HTTP status code
</ResponseField>

<ResponseField name="body" type="object">
  Response body containing the result

  <ResponseField name="carrier" type="object">
    The carrier object

    <Expandable title="Carrier properties">
      <ResponseField name="carrier_id" type="string">
        Unique identifier for the carrier in the system
      </ResponseField>

      <ResponseField name="carrier_name" type="string" required>
        Legal name of the carrier
      </ResponseField>

      <ResponseField name="status" type="enum" required>
        Current status of the carrier.

        <Expandable title="Available values">
          * `active` - Carrier is active and approved
          * `fail` - Carrier failed verification
          * `inactive` - Carrier is inactive
          * `in_review` - Carrier is under review
          * `not_set` - Status has not been set
        </Expandable>
      </ResponseField>

      <ResponseField name="dot_number" type="string">
        Department of Transportation (DOT) number
      </ResponseField>

      <ResponseField name="mc_number" type="string">
        Motor Carrier (MC) number
      </ResponseField>

      <ResponseField name="contacts" type="array">
        List of contacts for this carrier

        <Expandable title="Contact properties">
          <ResponseField name="name" type="string">
            Name of the contact
          </ResponseField>

          <ResponseField name="email" type="string">
            Email address
          </ResponseField>

          <ResponseField name="phone" type="string">
            Phone number
          </ResponseField>

          <ResponseField name="type" type="enum">
            Contact type. Must be one of: - `primary` - `dispatch` - `billing` - `driver` - `claims`
          </ResponseField>

          <ResponseField name="extension" type="string">
            Phone extension
          </ResponseField>

          <ResponseField name="preferred_contact_method" type="enum">
            Preferred contact method. Must be one of: - `email` - `phone` - `text`
          </ResponseField>
        </Expandable>
      </ResponseField>

      <ResponseField name="bridge" type="object">
        Integration status information

        <Expandable title="Bridge properties">
          <ResponseField name="status" type="enum" required>
            Integration processing status

            <Expandable title="Available values">
              * `success` - Carrier was successfully processed and integrated
              * `failed` - Carrier processing failed
            </Expandable>
          </ResponseField>

          <ResponseField name="bridge_carrier_id" type="string">
            The ID assigned to this carrier in the bridge system (when status is success)
          </ResponseField>
        </Expandable>
      </ResponseField>
    </Expandable>
  </ResponseField>
</ResponseField>

### Status Codes

<ResponseField name="200" type="number">
  Successfully found the carrier
</ResponseField>

<ResponseField name="400" type="number">
  Bad request - Missing required parameters
</ResponseField>

<ResponseField name="404" type="number">
  Carrier not found with the specified identifiers
</ResponseField>

<ResponseField name="500" type="number">
  Internal server error
</ResponseField>

<RequestExample>
  ```bash Request theme={null}
  curl --request GET \
       --url 'https://api.example.com/api/v1/carriers/find?mc=123456' \
       --header 'Authorization: Bearer API_KEY'
  ```

  ```bash Request with DOT Number theme={null}
  curl --request GET \
       --url 'https://api.example.com/api/v1/carriers/find?dot=987654' \
       --header 'Authorization: Bearer API_KEY'
  ```
</RequestExample>

<ResponseExample>
  ```json Response 200 Success theme={null}
  {
    "statusCode": 200,
    "body": {
      "carrier": {
      "carrier_id": "CAR123456",
      "carrier_name": "ABC Trucking Inc.",
      "status": "active",
      "dot_number": "987654",
      "mc_number": "123456",
      "contacts": [
        {
          "name": "John Dispatcher",
          "email": "dispatch@abctrucking.com",
          "phone": "5551234567",
          "type": "dispatch",
          "extension": "101",
          "preferred_contact_method": "phone"
        }
      ],
      "bridge": {
        "status": "success",
        "bridge_carrier_id": "BRK-CAR-789"
      }
      }
    }
  }
  ```

  ```json 400 Bad Request theme={null}
  {
    "statusCode": 400,
    "body": {
      "error": "Either mc or dot must be provided"
    }
  }
  ```

  ```json 404 Not Found theme={null}
  {
    "statusCode": 404,
    "body": {
      "error": "Carrier not found with the specified identifiers"
    }
  }
  ```

  ```json 500 Internal Server Error theme={null}
  {
    "statusCode": 500,
    "body": {
      "error": "Internal server error"
    }
  }
  ```
</ResponseExample>

---

Fuente original: https://docs.happyrobot.ai/bridge-api-reference/your-api/find-carrier
