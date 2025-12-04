#!/bin/bash

# Spring Security JWT Testing Script
# This script sets up a test environment and validates JWT implementation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BASE_URL=${BASE_URL:-http://localhost:8080}
TEST_EMAIL=${TEST_EMAIL:-test@example.com}
TEST_PASSWORD=${TEST_PASSWORD:-TestPassword123!}

echo -e "${GREEN}=== Spring Security JWT Test Suite ===${NC}"
echo

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${GREEN}ℹ️  $1${NC}"
}

# Function to check if service is running
check_service() {
    curl -s -f "$BASE_URL/actuator/health" > /dev/null 2>&1
}

# Function to create test user
create_test_user() {
    echo "Creating test user..."
    response=$(curl -s -w "%{http_code}" -o /tmp/user_response.json \
        -X POST "$BASE_URL/api/register" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$TEST_EMAIL\",
            \"password\": \"$TEST_PASSWORD\",
            \"firstName\": \"Test\",
            \"lastName\": \"User\"
        }")

    http_code=${response: -3}

    if [ "$http_code" = "201" ]; then
        print_status 0 "Test user created successfully"
        return 0
    elif [ "$http_code" = "409" ]; then
        print_status 0 "Test user already exists"
        return 0
    else
        print_status 1 "Failed to create test user (HTTP $http_code)"
        cat /tmp/user_response.json
        return 1
    fi
}

# Function to authenticate and get JWT
authenticate() {
    echo "Authenticating user..."
    response=$(curl -s -w "%{http_code}" -o /tmp/auth_response.json \
        -X POST "$BASE_URL/api/auth/login" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$TEST_EMAIL\",
            \"password\": \"$TEST_PASSWORD\"
        }")

    http_code=${response: -3}

    if [ "$http_code" = "200" ]; then
        ACCESS_TOKEN=$(jq -r '.accessToken' /tmp/auth_response.json)
        REFRESH_TOKEN=$(jq -r '.refreshToken' /tmp/auth_response.json)
        print_status 0 "Authentication successful"
        print_info "Access token: ${ACCESS_TOKEN:0:20}..."
        return 0
    else
        print_status 1 "Authentication failed (HTTP $http_code)"
        cat /tmp/auth_response.json
        return 1
    fi
}

# Function to test protected endpoint
test_protected_endpoint() {
    local endpoint=$1
    local expected_status=$2
    local description=$3

    if [ -z "$ACCESS_TOKEN" ]; then
        print_status 1 "No access token available"
        return 1
    fi

    response=$(curl -s -w "%{http_code}" -o /tmp/endpoint_response.json \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        "$BASE_URL$endpoint")

    http_code=${response: -3}

    if [ "$http_code" = "$expected_status" ]; then
        print_status 0 "$description"
        return 0
    else
        print_status 1 "$description (Expected $expected_status, got $http_code)"
        cat /tmp/endpoint_response.json
        return 1
    fi
}

# Function to test JWT validation
test_jwt_validation() {
    echo "Testing JWT validation..."

    # Test valid token
    test_protected_endpoint "/api/users/me" 200 "Valid JWT access"

    # Test expired token
    expired_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjoxNjE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

    response=$(curl -s -w "%{http_code}" -o /tmp/expired_response.json \
        -H "Authorization: Bearer $expired_token" \
        "$BASE_URL/api/users/me")

    if [ "${response: -3}" = "401" ]; then
        print_status 0 "Expired token rejected"
    else
        print_status 1 "Expired token accepted"
    fi

    # Test invalid token
    invalid_token="invalid.token.format"

    response=$(curl -s -w "%{http_code}" -o /tmp/invalid_response.json \
        -H "Authorization: Bearer $invalid_token" \
        "$BASE_URL/api/users/me")

    if [ "${response: -3}" = "401" ]; then
        print_status 0 "Invalid token rejected"
    else
        print_status 1 "Invalid token accepted"
    fi

    # Test no token
    response=$(curl -s -w "%{http_code}" -o /tmp/no_token_response.json \
        "$BASE_URL/api/users/me")

    if [ "${response: -3}" = "401" ]; then
        print_status 0 "No token rejected"
    else
        print_status 1 "No token accepted"
    fi
}

# Function to test refresh token
test_refresh_token() {
    echo "Testing refresh token..."

    if [ -z "$REFRESH_TOKEN" ]; then
        print_status 1 "No refresh token available"
        return 1
    fi

    # Use refresh token to get new access token
    response=$(curl -s -w "%{http_code}" -o /tmp/refresh_response.json \
        -X POST "$BASE_URL/api/auth/refresh" \
        -H "Content-Type: application/json" \
        -d "{\"refreshToken\": \"$REFRESH_TOKEN\"}")

    http_code=${response: -3}

    if [ "$http_code" = "200" ]; then
        NEW_ACCESS_TOKEN=$(jq -r '.accessToken' /tmp/refresh_response.json)
        print_status 0 "Refresh token successful"
        print_info "New access token: ${NEW_ACCESS_TOKEN:0:20}..."

        # Test new token
        response=$(curl -s -w "%{http_code}" -o /tmp/new_token_test.json \
            -H "Authorization: Bearer $NEW_ACCESS_TOKEN" \
            "$BASE_URL/api/users/me")

        if [ "${response: -3}" = "200" ]; then
            print_status 0 "New access token works"
        else
            print_status 1 "New access token failed"
        fi
    else
        print_status 1 "Refresh token failed (HTTP $http_code)"
        cat /tmp/refresh_response.json
    fi
}

# Function to test logout
test_logout() {
    echo "Testing logout..."

    if [ -z "$ACCESS_TOKEN" ]; then
        print_status 1 "No access token available"
        return 1
    fi

    # Logout
    response=$(curl -s -w "%{http_code}" -o /tmp/logout_response.json \
        -X POST "$BASE_URL/api/auth/logout" \
        -H "Authorization: Bearer $ACCESS_TOKEN")

    http_code=${response: -3}

    if [ "$http_code" = "200" ]; then
        print_status 0 "Logout successful"

        # Test token is no longer valid
        response=$(curl -s -w "%{http_code}" -o /tmp/post_logout.json \
            -H "Authorization: Bearer $ACCESS_TOKEN" \
            "$BASE_URL/api/users/me")

        if [ "${response: -3}" = "401" ]; then
            print_status 0 "Token invalidated after logout"
        else
            print_status 1 "Token still valid after logout"
        fi
    else
        print_status 1 "Logout failed (HTTP $http_code)"
        cat /tmp/logout_response.json
    fi
}

# Main test execution
main() {
    echo "Starting JWT security tests..."
    echo "Base URL: $BASE_URL"
    echo "Test Email: $TEST_EMAIL"
    echo

    # Check if service is running
    if ! check_service; then
        print_status 1 "Service is not running at $BASE_URL"
        print_info "Please start the application before running tests"
        exit 1
    fi

    print_status 0 "Service is running"

    # Run tests
    echo
    echo "=== Setup Phase ==="
    create_test_user
    authenticate

    echo
    echo "=== Authentication Tests ==="
    test_jwt_validation
    test_refresh_token
    test_logout

    echo
    echo "=== Test Summary ==="
    echo "All tests completed. Review the output above for any issues."
    echo
    echo "For detailed debugging:"
    echo "1. Check application logs: tail -f logs/application.log"
    echo "2. Use debug endpoint: curl -H \"X-Auth-Debug: true\" $BASE_URL/api/users/me"
    echo "3. Verify JWT content at: https://jwt.io/"
}

# Cleanup function
cleanup() {
    rm -f /tmp/*.json
}

# Set up cleanup
trap cleanup EXIT

# Run main function
main "$@"