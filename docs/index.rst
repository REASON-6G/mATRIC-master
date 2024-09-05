.. mATRIC documentation master file, created by
   sphinx-quickstart on Thu Oct 12 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to mATRIC's documentation!
===================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   backend/README
   frontend/README
   deployment
   development

Overview
========

mATRIC is a multi-Access Technology Intelligent Controller developed under the REASON project to support multiple wireless access technologies. It provides capabilities for real-time and near real-time scenarios, monitoring, intelligence, data analytics, and control and optimization of RAN resources.

Technology Stack and Features
=============================

- **FastAPI** for the Python backend API.
- **SQLModel** for the Python SQL database interactions (ORM).
- **Pydantic** for data validation and settings management.
- **PostgreSQL** as the SQL database for User Management/Login.
- **InfluxDB** as the database for Access Point Management.
- **React** for the frontend, using TypeScript, hooks, Vite, and Chakra UI.
- **Docker Compose** for development and production.
- **Secure password hashing** by default.
- **JWT (JSON Web Token)** authentication.
- **Email based password recovery**.
- **Tests with Pytest**.
- **Traefik** as a reverse proxy / load balancer.
- **CI/CD** based on GitHub Actions.

How To Use It
=============

Clone this repository and push the code to your new repository. Update configurations in the `.env` files to customize your settings. Generate secret keys using Python's `secrets` module.

Backend Development
====================

Refer to the `backend/README.md` for detailed backend development instructions.

Frontend Development
=====================

Refer to the `frontend/README.md` for detailed frontend development instructions.

Deployment
==========

Refer to the `deployment.md` for detailed deployment instructions.

Development
===========

Refer to the `development.md` for general development instructions, including using Docker Compose, custom local domains, and `.env` configurations.

License
=======

Licensed under the terms of the MIT license.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
