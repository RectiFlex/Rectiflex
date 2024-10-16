# Rectiflex

Rectiflex is a work order management application that allows users to create, update, categorize, and search work orders efficiently. It provides a streamlined process for managing maintenance tasks, assigning technicians, and tracking progress.

## Overview

Rectiflex utilizes Node.js for server-side operations, MongoDB as the database for storing work order information, and technologies like Express and Mongoose for seamless integration and data modeling. The project structure includes a React frontend for user interaction and a Node.js backend for handling business logic.

## Features

- **Work Order Management**: Users can create new work orders with detailed information such as title, description, priority, assigned technician, due date, and status. They can also edit existing work orders, change statuses, and reassign technicians.
- **Filtering and Searching**: The system supports filtering and searching work orders based on criteria like status, priority, technician, etc.
- **Notifications**: Users receive notifications for new work orders assigned to them or updates on existing work orders they are involved in.
- **Categorization**: Work orders are categorized based on the type of maintenance required (e.g., electrical, plumbing, HVAC).

## Getting started

### Requirements

- Node.js: JavaScript runtime for building apps.
- MongoDB: NoSQL database for storing work order information.
- Express: Web server framework for Node.js.
- Mongoose: MongoDB object modeling for Node.js.

### Quickstart

1. Clone the project repository.
2. Install dependencies using `npm install`.
3. Set up MongoDB locally or use a cloud version like MongoDB Atlas.
4. Start the server with `npm start`.
5. Access the application at `http://localhost:PORT` in your browser.

### License

Copyright (c) 2024.