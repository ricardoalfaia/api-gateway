# Exemplo de geração de certificados para teste:
"""
# 1. Gerar chave privada e certificado da CA
openssl req -x509 -newkey rsa:4096 -days 365 -nodes \
  -keyout ca.key -out ca.crt -subj "/CN=My CA"

# 2. Gerar chave privada do cliente
openssl genpkey -algorithm RSA -out client.key

# 3. Gerar CSR (Certificate Signing Request) do cliente
openssl req -new -key client.key -out client.csr \
  -subj "/CN=My Client"

# 4. Assinar o certificado do cliente usando a CA
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out client.crt -days 365
"""
