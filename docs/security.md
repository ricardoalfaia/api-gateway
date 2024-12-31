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


# Para windows

Esse erro no Windows ocorre porque o formato dos certificados precisa ser ajustado para o sistema. 
Vamos gerar os certificados de uma forma compatível com Windows:
Primeiro, vamos criar os certificados com o formato correto:

# 1. Criar diretório (se ainda não existir)
mkdir certs

# 2. Gerar CA
openssl req -x509 -sha256 -days 356 -nodes -newkey rsa:2048 ^
-keyout certs/ca.key -out certs/ca.crt ^
-subj "/CN=My Root CA"

# 3. Gerar chave privada e CSR para o cliente (API Gateway)
openssl req -newkey rsa:2048 -nodes ^
-keyout certs/client.key -out certs/client.csr ^
-subj "/CN=API Gateway Client"

# 4. Gerar certificado do cliente usando a CA
openssl x509 -req -sha256 -days 365 ^
-in certs/client.csr ^
-CA certs/ca.crt -CAkey certs/ca.key -CAcreateserial ^
-out certs/client.crt

# 5. Gerar chave privada e CSR para o servidor
openssl req -newkey rsa:2048 -nodes ^
-keyout certs/server.key -out certs/server.csr ^
-subj "/CN=localhost"

# 6. Gerar certificado do servidor usando a CA
openssl x509 -req -sha256 -days 365 ^
-in certs/server.csr ^
-CA certs/ca.crt -CAkey certs/ca.key -CAcreateserial ^
-out certs/server.crt

# 7. Converter o certificado do cliente para PFX (formato Windows)
openssl pkcs12 -export -out certs/client.pfx ^
-inkey certs/client.key ^
-in certs/client.crt ^
-certfile certs/ca.crt ^
-passout pass:password123


# Agora você pode testar usando o arquivo .pfx:
curl --cert-type P12 --cert certs/client.pfx:password123 ^
-k https://localhost:8001


# **Algumas observações importantes:**

O -k desabilita a verificação do certificado (útil para testes)
A senha "password123" é apenas para teste, use uma senha forte em produção
O formato PFX/P12 é mais adequado para Windows pois inclui tanto o certificado quanto a chave privada

Se você ainda tiver problemas, pode também tentar: