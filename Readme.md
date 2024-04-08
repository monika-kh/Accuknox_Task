# Project Title

Create an API for social networking application using Django Rest Framework with
below functionalities

## Description

The Social Networking Application is a platform designed to facilitate social interactions between users. It provides features such as user authentication, friend requests, and user profiles. Users can sign up for an account, log in securely, and search for other users to connect with. They can send friend requests to establish connections and manage their list of friends.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
  - [User Authentication](#user-authentication)
  - [Friend Requests](#friend-requests)

## Installation

### Using Docker

1. Clone the repository: `git clone `
2. Navigate to the project directory: `cd Accuknox`
3. Build the Docker image: `docker-compose build`
4. Start the Docker containers: `docker-compose up`
5. The application should now be running and accessible at `http://localhost:8000`

## Usage

Explain how to use your project once it's installed. Include any configuration steps or environment setup required.

## API Documentation

### User Authentication

#### User Signup

- **Create User**: Endpoint to register a new user.
  - Method: POST
  - URL: `/signup/`
  - Request Body:
    ```json
    {
        "email": "user@example.com",
        "password": "your_password",
        "confirm_password": "your_password"
    }
    ```
  - Response: JSON object indicating success or failure.

#### User Login

- **User Login**: Endpoint to authenticate a user using basic authentication.
  - Method: POST
  - URL: `/login/`
  - Authentication: Basic authentication (username and password)
  - Response: JSON object indicating success or failure.

### Friend Requests

#### Create Friend Request

- **Send Friend Request**: Endpoint to send a friend request to another user.
  - Method: POST
  - URL: `/friend-requests/`
  - Request Body:
    ```json
    {
        "to_user": "friend@example.com"
    }
    ```
  - Authentication: Basic authentication required.
  - Response: JSON object indicating success or failure.

#### Accept Friend Request

- **Accept Friend Request**: Endpoint to accept a pending friend request.
  - Method: POST
  - URL: `/friend-requests/{request_id}/accept/`
  - Authentication: Basic authentication required.
  - Response: JSON object indicating success or failure.

#### Reject Friend Request

- **Reject Friend Request**: Endpoint to reject a pending friend request.
  - Method: POST
  - URL: `/friend-requests/{request_id}/reject/`
  - Authentication: Basic authentication required.
  - Response: JSON object indicating success or failure.

#### List Pending Requests

- **List Pending Requests**: Endpoint to retrieve a list of pending friend requests.
  - Method: GET
  - URL: `/friend-requests/list-pending-requests/`
  - Authentication: Basic authentication required.
  - Response: JSON array containing pending friend requests.


#### user-search api

- **show all data according to search**: This API allows users to search for other users by email or username.
  - Method: GET
  - URL: `/user-search/?q=user`
  - `q` (required): (q is mention in parmss like q : "serach perameter" ).The search query to find users by email or username.
  - Authentication: Basic authentication required.
  - Response: JSON array containing pending friend requests.
  - output Body:
    ```json
      {
          "count": 5,
          "next": null,
          "previous": null,
          "results": [
              {
                  "email": "user1@gmail.com"
              },
              {
                  "email": "user2@example.com"
              },
              {
                  "email": "user3@example.com"
              }
          ]
      }
    ```

#### Add pagination
- **add pagination in user-search api**: The default page size is 10, but it can be customized using the page_size query parameter.
  - Method: GET
  - URL: `/user-search/?q=johndoe&page_size=20`
  - `q` (required): (q is mention in parmss like q : "serach perameter" ).The search query to find users by email or username.

