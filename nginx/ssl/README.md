# SSL Certificates Directory

This directory holds SSL certificates for production deployment.

## For Let's Encrypt (recommended):
SSL certificates are managed automatically by certbot container.

## For manual SSL:
Place your certificates here:
- `fullchain.pem` - Full certificate chain
- `privkey.pem` - Private key

**Note:** Never commit real certificates to git!
