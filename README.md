# 🚀 IoT Platform API

A secure, scalable FastAPI-based backend API server for IoT platform with comprehensive authentication, device management, and real-time streaming capabilities.

## 🚀 Features

- **JWT Authentication**: Secure user authentication with access tokens (30 minutes) and WebSocket streaming tokens (1 hour)
- **User Management**: User registration, login, and profile management
- **Device Management**: Full CRUD operations for IoT devices with user-scoped access
- **WebSocket Streaming**: MQTT-compatible token generation for real-time streaming with topic-based permissions
- **Rate Limiting**: Configurable rate limits for different endpoints
- **Database Integration**: PostgreSQL with SQLAlchemy ORM
- **Docker Deployment**: Production-ready containerized deployment
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## 🏗️ Architecture

### Business Logic Summary
- **User-centric authentication system**: JWT-based access control with role-based permissions
- **Device ownership management**: Complete data isolation per user with strict access control
- **Secure streaming infrastructure**: MQTT-compatible tokens with topic-based permissions and rate limiting

## 📋 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/stream/token` - WebSocket/MQTT streaming token generation

### Users
- `GET /users/me` - Get current user profile

### Devices
- `GET /devices/` - List user's devices
- `POST /devices/` - Create new device
- `GET /devices/{device_id}` - Get device details
- `PUT /devices/{device_id}` - Update device
- `DELETE /devices/{device_id}` - Delete device

### Health Check
- `GET /health` - API health status

## 🔒 WebSocket/MQTT Token Structure

The WebSocket streaming tokens follow MQTT standard patterns with the following payload structure:

```json
{
  "sub": "user@example.com",           // User email as subject
  "iat": 1750112214,                   // Issued at timestamp
  "exp": 1750115814,                   // Expires at timestamp (1 hour)
  "subs": [                            // Subscription topics user can listen to
    "devices/{user_id}/#",
    "user/{user_id}/data",
    "user/{user_id}/status"
  ],
  "publ": [                            // Publish topics user can send to
    "devices/{user_id}/commands"
  ],
  "user_id": 2,                        // User ID for context
  "type": "websocket"                  // Token type identifier
}
```

### Topic Permissions
- **Subscription Topics**: Users can subscribe to all device topics under their user ID
- **Publish Topics**: Users can publish commands to their devices
- **User Isolation**: Complete topic isolation between users

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/iot_platform

# JWT Configuration (Legacy - kept for backward compatibility)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production

# JWT Configuration for WebSocket/MQTT Streaming
# Base64-encoded secret key for WebSocket/MQTT token generation
JWT_SECRET_BASE64=WsNiwFBf2CJqVRz8/9OT58zgsXtRqArsUtvoeFrI+rc=

# Application Configuration
DEBUG=True
PORT=8000

# PostgreSQL Configuration (for docker-compose)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=iot_platform
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd iot-platform-api
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Build and Run**:
   ```bash
   docker-compose up --build -d
   ```

3. **Verify Deployment**:
   ```bash
   curl http://localhost:8000/health
   ```

### Manual Docker Build

```bash
# Build the image
docker build -t iot-platform-api .

# Run with PostgreSQL
docker run -d --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=iot_platform \
  -p 5432:5432 postgres:15-alpine

# Run the API
docker run -d --name iot-api \
  -e DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/iot_platform \
  -e JWT_SECRET_BASE64=WsNiwFBf2CJqVRz8/9OT58zgsXtRqArsUtvoeFrI+rc= \
  -p 8000:8000 iot-platform-api
```

## 🧪 Testing

### Using Postman

1. Import the provided Postman collection: `postman/iot-api.postman_collection.json`
2. The collection includes automatic JWT token management
3. Test all endpoints in the following order:
   - Register/Login
   - Get User Profile
   - Device Management
   - WebSocket Token Generation

### Using cURL/PowerShell

```powershell
# Register a new user
$registerResponse = Invoke-RestMethod -Uri "http://localhost:8000/auth/register" -Method POST -ContentType "application/json" -Body '{"email": "user@example.com", "password": "password123"}'

# Login and get token
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method POST -ContentType "application/json" -Body '{"email": "user@example.com", "password": "password123"}'
$token = $loginResponse.access_token
$headers = @{Authorization = "Bearer $token"}

# Get WebSocket token
$wsToken = Invoke-RestMethod -Uri "http://localhost:8000/auth/stream/token" -Method POST -Headers $headers
Write-Host "WebSocket Token: $($wsToken.websocket_token)"
Write-Host "Subscription Topics: $($wsToken.subscription_topics)"
Write-Host "Publish Topics: $($wsToken.publish_topics)"
```

## 📊 Rate Limiting

- **Authentication endpoints**: 5 requests per minute
- **Device management**: 10 requests per minute  
- **WebSocket token generation**: 5 requests per minute

## 🗃️ Database Schema

### Users Table
- `id` (Primary Key)
- `email` (Unique)
- `hashed_password`
- `is_admin` (Boolean)
- `created_at` (Timestamp)

### Devices Table
- `id` (Primary Key)
- `name`
- `device_id` (Unique)
- `user_id` (Foreign Key to Users)
- `created_at` (Timestamp)

## 🔐 Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- User-scoped device access
- Rate limiting protection
- Base64-encoded secret keys
- MQTT-compatible token structure
- Topic-based permission system

## 📚 API Documentation

Once the application is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛠️ Development

### Local Development Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL**:
   ```bash
   # Using Docker
   docker run -d --name postgres \
     -e POSTGRES_USER=postgres \
     -e POSTGRES_PASSWORD=postgres \
     -e POSTGRES_DB=iot_platform \
     -p 5432:5432 postgres:15-alpine
   ```

3. **Run the Application**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Technology Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn
- **Authentication**: OAuth2 + JWT (PyJWT), Passlib (bcrypt)
- **Database**: PostgreSQL, SQLAlchemy
- **Rate Limiting**: SlowAPI
- **Containerization**: Docker, Docker Compose
- **Documentation**: OpenAPI/Swagger

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Kill process using port 8000
sudo lsof -t -i tcp:8000 | xargs kill -9

# Or use different port
docker-compose up --build -e PORT=8001
```

#### Database Connection Issues
```bash
# Reset database
docker-compose down -v
docker-compose up --build
```

#### JWT Token Issues
- Ensure the JWT_SECRET_KEY is set in your environment
- Check token expiration (30 minutes for access tokens)
- Verify the Authorization header format: `Bearer <token>`

### Getting Help

- Check the API documentation at `/docs`
- View application logs: `docker-compose logs web`
- Test endpoints with the provided Postman collection

---

🎉 **Happy IoT Development!** 🎉 