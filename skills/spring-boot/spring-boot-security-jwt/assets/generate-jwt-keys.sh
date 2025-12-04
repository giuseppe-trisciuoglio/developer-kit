#!/bin/bash

# JWT Key Generation Script
# This script generates RSA keys for JWT signing and verification

set -e

# Configuration
KEY_SIZE=${KEY_SIZE:-2048}
KEY_ALIAS=${KEY_ALIAS:-jwt}
KEYSTORE_PASSWORD=${KEYSTORE_PASSWORD:-changeit}
PRIVATE_KEY_PASSWORD=${PRIVATE_KEY_PASSWORD:-changeit}
OUTPUT_DIR=${OUTPUT_DIR:-./keys}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== JWT Key Generation ===${NC}"
echo

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Generate RSA key pair
echo "Generating $KEY_SIZE-bit RSA key pair..."
keytool -genkeypair \
    -alias "$KEY_ALIAS" \
    -keyalg RSA \
    -keysize "$KEY_SIZE" \
    -validity 3650 \
    -keypass "$PRIVATE_KEY_PASSWORD" \
    -storepass "$KEYSTORE_PASSWORD" \
    -keystore "$OUTPUT_DIR/jwt.jks" \
    -dname "CN=JWT Key, OU=Security, O=My Company, L=City, ST=State, C=US"

echo -e "${GREEN}✅ Key pair generated successfully${NC}"

# Extract public key
echo "Extracting public key..."
keytool -exportcert \
    -alias "$KEY_ALIAS" \
    -storepass "$KEYSTORE_PASSWORD" \
    -keystore "$OUTPUT_DIR/jwt.jks" \
    -rfc \
    -file "$OUTPUT_DIR/jwt-public.cer"

echo -e "${GREEN}✅ Public key extracted${NC}"

# Convert to PEM format
echo "Converting to PEM format..."
openssl x509 \
    -inform DER \
    -outform PEM \
    -in "$OUTPUT_DIR/jwt-public.cer" \
    -out "$OUTPUT_DIR/jwt-public.pem"

echo -e "${GREEN}✅ PEM certificate created${NC}"

# Generate JWK Set
echo "Generating JWK Set..."
cat > "$OUTPUT_DIR/jwk-set.json" << EOF
{
  "keys": [
    {
      "kty": "RSA",
      "use": "sig",
      "alg": "RS256",
      "kid": "$KEY_ALIAS",
      "n": "$(openssl x509 -in "$OUTPUT_DIR/jwt-public.pem" -pubkey -noout | openssl rsa -pubin -outform DER 2>/dev/null | openssl base64 -A | tr -d '=' | tr '/+' '_-' | sed 's/\//_/g' | sed 's/+/-/g')",
      "e": "AQAB"
    }
  ]
}
EOF

echo -e "${GREEN}✅ JWK Set generated${NC}"

# Generate Spring Security properties
echo "Generating Spring Security properties..."
cat > "$OUTPUT_DIR/application-security.properties" << EOF
# JWT Configuration
jwt.key-store=classpath:jwt.jks
jwt.key-store-password=$KEYSTORE_PASSWORD
jwt.key-alias=$KEY_ALIAS
jwt.private-key-password=$PRIVATE_KEY_PASSWORD

# Alternative: Public key configuration
jwt.public-key-location=classpath:jwt-public.pem

# JWK Set configuration (for distributed systems)
jwt.jwk-set-uri=https://auth.myapp.com/.well-known/jwks.json
EOF

echo -e "${GREEN}✅ Spring properties generated${NC}"

# Display generated files
echo
echo -e "${GREEN}Generated files:${NC}"
ls -la "$OUTPUT_DIR"

# Display key information
echo
echo "Key Information:"
echo "- Key Size: $KEY_SIZE bits"
echo "- Algorithm: RSA"
echo "- Validity: 10 years"
echo "- Keystore: $OUTPUT_DIR/jwt.jks"
echo "- Public Certificate: $OUTPUT_DIR/jwt-public.cer"
echo "- PEM Certificate: $OUTPUT_DIR/jwt-public.pem"
echo "- JWK Set: $OUTPUT_DIR/jwk-set.json"

# Security warning
echo
echo -e "${YELLOW}⚠️  IMPORTANT SECURITY NOTES:${NC}"
echo "1. Change the default passwords before production use"
echo "2. Store the keystore file securely (don't commit to version control)"
echo "3. Use environment variables or secret management in production"
echo "4. Consider using a cloud KMS (AWS KMS, Azure Key Vault, etc.)"
echo "5. Implement key rotation strategy"

# Instructions for usage
echo
echo -e "${GREEN}Usage Instructions:${NC}"
echo "1. Copy jwt.jks to your application's classpath"
echo "2. Add the properties to your application.properties"
echo "3. Or use the JWK Set for distributed authentication"
echo
echo "Example configuration:"
echo "```yaml"
echo "jwt:"
echo "  key-store: classpath:jwt.jks"
echo "  key-store-password: \${JWT_KEYSTORE_PASSWORD}"
echo "  key-alias: jwt"
echo "```"

# Cleanup temporary files
rm -f "$OUTPUT_DIR/jwt-public.cer"

echo
echo -e "${GREEN}✅ Key generation complete!${NC}"