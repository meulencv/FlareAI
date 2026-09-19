---
title: "List available voices"
description: "Returns the voice catalog available to the authenticated workspace in this HappyRobot cluster. Use the returned id in workflow agent.voices configuration."
---

# List available voices

> Returns the voice catalog available to the authenticated workspace in this HappyRobot cluster. Use the returned id in workflow agent.voices configuration.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /voices/
openapi: 3.0.3
info:
  title: Happyrobot Public API
  description: Public API endpoints for Happyrobot
  version: 0.1.1
servers:
  - url: https://platform.happyrobot.ai/api/v2
security:
  - bearerAuth: []
paths:
  /voices/:
    get:
      tags:
        - Voice
      summary: List available voices
      description: >-
        Returns the voice catalog available to the authenticated workspace in
        this HappyRobot cluster. Use the returned id in workflow agent.voices
        configuration.
      parameters:
        - schema:
            type: string
            minLength: 1
          in: query
          name: language
          required: false
          description: >-
            Optional language filter. Prefixes such as en or es match every
            accent; locales/accent keys such as en-GB or es-MX match that
            specific locale.
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: string
                      description: Voice ID to use in workflow agent.voices configuration.
                    name:
                      type: string
                    provider:
                      type: string
                      enum:
                        - elevenlabs
                        - happyrobot
                        - elevenlabs-non-streaming
                        - cartesia
                        - munsit
                    provider_voice_id:
                      nullable: true
                      description: Provider-specific voice ID, when available.
                      type: string
                    model_id:
                      nullable: true
                      type: string
                    model_family:
                      type: string
                      enum:
                        - turbo
                        - flash
                        - eleven_v3
                        - happyrobot
                        - sonic
                        - munsit
                    language:
                      type: string
                      enum:
                        - en-US
                        - en-GB
                        - en-AU
                        - en-NZ
                        - en-IN
                        - en-CA
                        - en-IE
                        - es-ES
                        - es-AR
                        - es-MX
                        - es-CO
                        - es-VE
                        - es-PE
                        - es-419
                        - pt-PT
                        - pt-BR
                        - de-DE
                        - de-CH
                        - fr-FR
                        - fr-CA
                        - zh-CN
                        - zh-TW
                        - zh-HK
                        - bg-BG
                        - ca-ES
                        - cs-CZ
                        - da-DK
                        - el-GR
                        - et-EE
                        - fi-FI
                        - hi-IN
                        - hr-HR
                        - hu-HU
                        - id-ID
                        - it-IT
                        - ja-JP
                        - ko-KR
                        - lt-LT
                        - lv-LV
                        - ms-MY
                        - nl-NL
                        - nl-BE
                        - no-NO
                        - pl-PL
                        - ro-RO
                        - ru-RU
                        - sk-SK
                        - sv-SE
                        - th-TH
                        - tr-TR
                        - uk-UA
                        - vi-VN
                        - af-ZA
                        - am-ET
                        - hy-AM
                        - as-IN
                        - ast-ES
                        - az-AZ
                        - bs-BA
                        - my-MM
                        - ceb
                        - ny-MW
                        - fil-PH
                        - ff-NG
                        - lg-UG
                        - ka-GE
                        - gu-IN
                        - ha-NG
                        - is-IS
                        - ig-NG
                        - jv-ID
                        - kea
                        - kn-IN
                        - kk-KZ
                        - km-KH
                        - ku-TR
                        - ky-KG
                        - lo-LA
                        - ln-CD
                        - luo-KE
                        - lb-LU
                        - mk-MK
                        - ml-IN
                        - mi-NZ
                        - ne-NP
                        - nso-ZA
                        - oc-FR
                        - or-IN
                        - ps-AF
                        - pa-IN
                        - sr-RS
                        - sn-ZW
                        - sd-PK
                        - so-SO
                        - tg-TJ
                        - te-IN
                        - umb-AO
                        - uz-UZ
                        - wo-SN
                        - xh-ZA
                        - zu-ZA
                        - ba-RU
                        - eu-ES
                        - gl-ES
                        - eo
                        - ia
                        - ug-CN
                        - ar-001
                        - ar-EG
                        - ur-PK
                        - bn-BD
                        - sl-SI
                    languages:
                      type: array
                      items:
                        type: string
                      description: >-
                        Language prefixes supported by this voice, including its
                        stored primary language.
                    locales:
                      type: array
                      items:
                        type: string
                      description: >-
                        Specific locales and accent keys supported by this
                        voice. These values can be passed as the language filter
                        for location-specific matches.
                    gender:
                      type: string
                      enum:
                        - male
                        - female
                  required:
                    - id
                    - name
                    - provider
                    - provider_voice_id
                    - model_id
                    - model_family
                    - language
                    - languages
                    - locales
                    - gender
                  additionalProperties: false
        '401':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                  message:
                    type: string
                  statusCode:
                    type: integer
                    minimum: -9007199254740991
                    maximum: 9007199254740991
                  details: {}
                required:
                  - error
                additionalProperties: false
        '403':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                  message:
                    type: string
                  statusCode:
                    type: integer
                    minimum: -9007199254740991
                    maximum: 9007199254740991
                  details: {}
                required:
                  - error
                additionalProperties: false
        '500':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                  message:
                    type: string
                  statusCode:
                    type: integer
                    minimum: -9007199254740991
                    maximum: 9007199254740991
                  details: {}
                required:
                  - error
                additionalProperties: false
      security:
        - bearerAuth: []
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: Opaque

````

---

Fuente original: https://docs.happyrobot.ai/api-reference/voice/list-available-voices
