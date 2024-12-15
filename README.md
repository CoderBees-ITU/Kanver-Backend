# Flask Backend

## Local Development

Follow these steps to set up and contribute to the Flask backend locally:

### Workflow

1. **Create or Choose an Issue**
   - Before making any changes, always create an issue for the task you intend to complete or choose an existing one.

2. **Create a Branch**
   - Create a new branch for the issue you're working on. Use descriptive names for the branch that reflect the issue, e.g., `feature/add-authentication` or `bugfix/fix-404-error`.

3. **Complete the Task**
   - Work on your assigned task. Ensure your code is well-documented and follows the project's conventions.

4. **Create a Pull Request (PR)**
   - Once your task is complete, create a PR to merge your changes into the `main` branch.
   - Request reviews from your team members.

5. **Ensure Build Integrity**
   - Make sure all builds and tests for the PR pass successfully before merging to maintain the integrity of the `main` branch.

### Setting Up the Environment

1. **Create a `.env` File**
   - Copy the provided `.env.example` file to a new file named `.env`.
   - Update the `.env` file with your local configuration if necessary.
   - `MYSQL*` variables are not effective if docker is used. See `docker-compose.yml` for docker specific variables.

2. **Using Docker for Local Development**
   - Although you can manually create and configure a database using the `MYSQL*` variables in the `.env` file, the easiest and most tested option is to use Docker.
   - Run the backend and the database using the following command:
     ```bash
     docker-compose up --build -d
     ```
   - This command will spin up both the backend and the database in a Dockerized environment.

### Permanent Backend Instances

We have permanent backend instances available for use (as long as credits last). These include tagged revisions and the latest stable revision:

| **Tagged Revisions** | **URL**                                      |
|-----------------------|----------------------------------------------|
| v1.0.0 ( Exposed secrets ) | [https://stable-but-unsecure---kanver-backend-ujtqwslguq-uc.a.run.app/](https://stable1-unsecure---kanver-backend-ujtqwslguq-uc.a.run.app/) |


| **Latest Revision**  | **URL**                                      |
|-----------------------|----------------------------------------------|
| Latest Revision (Always Latest Successful Build) | [https://latest-revision---kanver-backend-ujtqwslguq-uc.a.run.app](https://latest-revision---kanver-backend-ujtqwslguq-uc.a.run.app) |

Feel free to use these URLs for testing and integration purposes.

---

Thank you for contributing to this project! Make sure to follow the guidelines to ensure smooth collaboration.
