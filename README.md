# ndastro-api
API to serve data for ndastro-ui.

## Running the API

1. **Install dependencies**
   ```sh
   poetry install
   ```

2. **Activate your environment**
   ```sh
   poetry shell
   ```
   Or activate your virtualenv if using another tool.

3. **Setup initial data**
   ```sh
   poetry run pre-start
   poetry run db-migrate
   poetry run init-data

4. **Run the API server**
   From the project root, run:
   ```sh
   uvicorn ndastro_api.main:app --reload
   ```
   - The API will be available at [http://localhost:8000](http://localhost:8000)
   - The OpenAPI docs will be at [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)

## Running Tests

1. **Install dependencies**
   If you use Poetry:
   ```sh
   poetry install
   ```

2. **Activate your environment**
   If using Poetry:
   ```sh
   poetry shell
   ```
   Or activate your virtualenv if using another tool.

3. **Setup initial data**
   ```sh
   $env:ENV_FILE=".env.test" # for powershell
   poetry run pre-start
   poetry run db-migrate
   poetry run init-data

3. **Run the tests**
   From the project root, run:
   ```sh
   pytest --envfile .\\ndastro_api\\.env.test
   ```
   Or, for more detailed output:
   ```sh
   pytest -v
   ```

**Note:**
- If you use a test script (like `scripts/test.sh`), you can also run:
  ```sh
  ./scripts/test.sh
  ```
- Make sure your environment variables (e.g., for test DB) are set if needed.

## References: 
1. [FastApi Template](https://github.com/fastapi/full-stack-fastapi-template/tree/master)
2. [Fastapi Boilerplate](https://github.com/benavlabs/FastAPI-boilerplate)


