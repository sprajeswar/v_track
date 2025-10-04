# project - Consume external API
This project is to consume external API and demonstrate the funationality of a couple of APIs

---

## To get started
### 1. Clone Repository
```
   git clone https://github.com/sprajeswar/v_track.git
   cd v_track
   export PYTHONPATH=$PWD
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

## Authentication
Check for default token from config file for basic authorization.
Or else export your own token like below
```export KEY_TOKEN=<your token>
```
Ex: export KEY_TOKEN=admin

- Use the same token value on Swagger to authenticate!

## Usage
To run the application, execute the following command:
(Default LOG_LEVEL is set to INFO under config.py
Run the below to change its behaviour, say to DEBUG export below.

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

     {"status":"OK. Server is up and running."}

Swagger docs:

```http://127.0.0.1:8000/docs```
And its done. You are free to experiment.

### Application logs
Application level logs are available under <PYTHONPATH>/opt/logs directory
Application log file: app.log
Ser the below vars from config for different values

```LOG_DIR
LOG_FILE_PATH
```

## Notes:
- An individual query within the queryset can return more than 1,000 vulnerabilities
- The entire queryset can return more than 3,000 vulnerabilities total
- If query is taking more than 20 seconds to execute then there are chances of pagenation!
-- Refer header info for handling this
- If no vulnerabilities for a given package, then it is not skipped but returns {}
- The order of packages preservred - Request to Response
---
## In scope
This is for MVP and is to demonstrate consuming third party API
- Read vulnerabilities for a given package
- Read vulnerabilities for bunch of packages uploaded through a file (consider pagination)
- List all the proejcts created
- List all the projects with vulnerabilities
- In-memory cache (lru_cache) with configurable cache size

### Limitations
- Test on Swagger!
- Modeling is not considered
- As of now NOT seen any package with reponse for pagination
## out of scope
- The response for a given package is not processed, but sent back untouched!
- Case sensitivity of the packages are not handled (There are packes comes with camel case!)
- Rate Limit the API calls
- Pagination (need to check for onepackage crossing 1000 vulners)

## TBD - Enhancements
- To address the Limitations
- Consider persisting data
- Tailored response - to discuss more
- Cache 'key'
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

    Method: POST

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

## Samples
### Data for requirements file
{"name": "Django", "version": "3.2.0", "ecosystem": "PyPI"}
{"name": "pandas", "version": "1.3.0", "ecosystem": "PyPI"}
{"name": "requests", "version": "2.28.1", "ecosystem": "PyPI"}

### When packages are not available
- Same for Get Projects, Get Project Vulnerabilities, Get All Dependencies

{
  "status": "Success",
  "message": "No projects found. Create a project first.",
  "data": {}
}
### Package specific details - hit the API
- The o/p is big!!!
### Package creation
- Pulled data

    {
    "status": "Success",
    "message": "Project 'V_TRACK' created successfully.",
    "data": {
        "V_TRACK": {
        "description": "MVP - Project with FastAPI",
        "dependencies": {
            "Django": "28 vulnerabilities found",
            "pandas": "vulnerabilities NOT found!",
            "requests": "4 vulnerabilities found"
                        }
                    }
            }
    }
- Pulled None

    {
    "status": "Success",
    "message": "Project 'V_TRACK_Pandas' created successfully.",
    "data": {
        "V_TRACK_Pandas": {
        "description": "MVP - Project with FastAPI",
        "dependencies": {
            "pandas": "vulnerabilities NOT found!"
                    }
                }
        }
    }
- Project already exists

    {
    "status": "Success",
    "message": "Project with name 'V_TRACK' already exists.",
    "data": {}
    }
- Got into an issue

    {
    "status": "Error",
    "message": "Invalid value found: Missing required fields in row: {\"name\": \"pandas\", \"version \": \"2.3.3\", \"ecosystem\": \"PyPI\"}",
    "data": {}
    }

### Get all created packages (but having vunlerabilities)
    {
    "status": "Success",
    "message": "Project count: 2. 1 project(s) with vulnerabilities found.",
    "data": {
        "V_TRACK": {
        "description": "MVP - Project with FastAPI",
        "dependencies": {
            "Django": "28 vulnerabilities found",
            "pandas": "vulnerabilities NOT found!",
            "requests": "4 vulnerabilities found"
                    }
                }
        }
    }

### Project specific details (Which are craeted already)
- Project available

    {
    "status": "Success",
    "message": "Vulnerabilities found for the project 'V_TRACK'.",
    "data": {
        "vulnerabilities": {
        "Django": "28 vulnerabilities found",
        "requests": "4 vulnerabilities found"
                    }
            }
    }

- Project not available

    {
    "status": "Success",
    "message": "Project 'AmIThere' not found.",
    "data": {}
    }

### Get all dependencies (from created projects)
    {
    "status": "Success",
    "message": "Fetched dependencies with vulnerabilities across all projects.",
    "data": {
        "dependencies": {
        "django": "V_TRACK: 28",
        "requests": "V_TRACK: 4"
                }
        }
    }