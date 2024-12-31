# Para cada cenário:

## 1. Para endpoints na mesma rede:
- Service-to-service authentication usando tokens JWTs
- mTLS (mutual TLS) para comunicação segura
- API keys internas + validação por IP

## 2. Sistema de API Keys:
- Útil para controle de acesso
- Rastreamento de uso
- Rate limiting por serviço
- Implementação:

## 3. Para serviços externos:
Para serviços externos:
- OAuth2/JWT para autenticação
- Rate limiting
- Documentação OpenAPI completa
- Versionamento de API
- Monitoramento de uso
- SLAs claros



# permissioes linux
```terminal
chmod 600 certs/client.key certs/ca.key
chmod 644 certs/client.crt certs/ca.crt
```

# Configurar permissões restritas para as chaves privadas
$acl = Get-Acl "certs\client.key"
$acl.SetAccessRuleProtection($true, $false)  # Remove herança
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "$env:USERNAME",  # Usuário atual
    "Read,Write",     # Permissões
    "Allow"          # Tipo de regra
)
$acl.AddAccessRule($rule)
Set-Acl "certs\client.key" $acl

# Repita para ca.key
$acl = Get-Acl "certs\ca.key"
$acl.SetAccessRuleProtection($true, $false)
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "$env:USERNAME",
    "Read,Write",
    "Allow"
)
$acl.AddAccessRule($rule)
Set-Acl "certs\ca.key" $acl

# Configurar permissões menos restritas para os certificados
$acl = Get-Acl "certs\client.crt"
$acl.SetAccessRuleProtection($true, $false)
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "Everyone",      # Todos os usuários
    "Read",         # Apenas leitura
    "Allow"
)
$acl.AddAccessRule($rule)
Set-Acl "certs\client.crt" $acl

# Repita para ca.crt
$acl = Get-Acl "certs\ca.crt"
$acl.SetAccessRuleProtection($true, $false)
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "Everyone",
    "Read",
    "Allow"
)
$acl.AddAccessRule($rule)
Set-Acl "certs\ca.crt" $acl

# No diretório certs
# 1. Gerar chave privada do servidor
openssl genrsa -out server.key 4096

# 2. Gerar CSR do servidor
openssl req -new -key server.key -out server.csr \
  -subj "/CN=localhost"

# 3. Assinar o certificado do servidor usando a mesma CA
openssl x509 -req -in server.csr \
  -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out server.crt -days 365


Para testar a implementação do mTLS, precisamos seguir alguns passos:

Primeiro, vamos gerar os certificados necessários. Crie uma pasta certs no diretório raiz do projeto:

# 1. Gerar chave privada e certificado da CA (Certificate Authority)
openssl req -x509 -newkey rsa:4096 -days 365 -nodes \
  -keyout ca.key -out ca.crt \
  -subj "/CN=My Gateway CA"

# 2. Gerar chave privada do cliente (Gateway)
openssl genrsa -out client.key 4096

# 3. Gerar CSR (Certificate Signing Request) do cliente
openssl req -new -key client.key -out client.csr \
  -subj "/CN=API Gateway"

# 4. Assinar o certificado do cliente usando a CA
openssl x509 -req -in client.csr \
  -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out client.crt -days 365