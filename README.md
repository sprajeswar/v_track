# project - Consume external API
This project is to consume external API and demonstrate the funationality of a couple of APIs

---

## To get started
### 1. clone repository
```
   git clone https://github.com/sprajeswar/v_track.git
   cd v_track
   set PYTHONPATH=<your cloned path>/v_track
   (this should work for windows/Mac)
```

### 2. Setup Virtual Environment
For pipenv based - windows
```
    pip install pipenv
    pipenv install
```

For pip based - Linux/Mac
```
    python -m venv venv
    source venv/bin/activate
```
```
    source venv\bin\activate
    pip install -r requirements.txt
```

## Usage
To run the application, execute the following command:
(Default LOG_LEVEL is set to INFO under config.py
Run the below to change its behaviour, say to DEBUG
```export LOG_LEVEL=DEBUG```
)
```
uvicorn app.main:app --reload
```

## Endpoints Testing
Run
```http://127.0.0.1:8000/```

on your favorite web browser!.

Health check

```http://127.0.0.1:8000/health```
You should see message on the console (something like below)

#### {"status":"OK. Server is up and running."}

Swagger docs:

```http://127.0.0.1:8000/docs```
And its done. You are free to experiment.

### Notes:
- An individual query within the queryset can return more than 1,000 vulnerabilities
- The entire queryset can return more than 3,000 vulnerabilities total
- If query is taking more than 20 seconds to execute then there are chances of pagenation!
-- Refer header info for handling this
- If no vulnerabilities for a given package, then it is not skipped but returns {}
- The order of packages preservred - Request to Response
---
## In scope
- Read vulnerabilities for a package
- Read vulnerabilities for bunch of package (consider pagination)

## out of scope
- More to come!

---

# Further Reading - API Documentation
    https://google.github.io/osv.dev/api/

# End points
- Single - Vulnerabilities for single package

URL - ```https://api.osv.dev/v1/query```

Method: GET

Payload:
    {
            "version": "2.3.3",
            "package": {
                "name": "pandas",
                "ecosystem": "PyPI"
            }
         }
Refer site for sample reponse!

- Batch - Vulnerabilities for a batch of packages

  URL - ```https://api.osv.dev/v1/querybatch```

Method: GET

Payload:
    {
        "queries": [
             {
                "version": "2.4.1",
                "package": {
                    "name": "jinja2",
                    "ecosystem": "PyPI",
                }
             },
            {
                "version": "2.3.3",
                "package": {
                    "name": "pandas",
                    "ecosystem": "PyPI",
                }
            },
            {
                "version": "2.28.1",
                "package": {
                    "name": "requests",
                    "ecosystem": "PyPI",
                }
            }
        ]
    }
Refer site for sample reponse!