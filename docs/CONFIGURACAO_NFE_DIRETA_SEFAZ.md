# Configuração de Emissão de NF-e Direta com SEFAZ

Este documento explica como configurar a emissão de NF-e diretamente com a SEFAZ, sem usar APIs terceiras.

## 🎯 Visão Geral

Como empresa desenvolvedora, você pode emitir NF-e diretamente com a SEFAZ usando certificado digital, sem depender de APIs terceiras como Focus NFe ou NFe.io.

## 📋 Requisitos

### 1. Certificado Digital

Você precisa de um **Certificado Digital A1** (arquivo) ou **A3** (token/cartão):

- **A1**: Arquivo `.p12` ou `.pfx` com certificado e chave privada
- **A3**: Token ou cartão com certificado (requer driver específico)

**Onde obter:**
- Autoridades Certificadoras (AC): Serasa, Certisign, Serpro, etc.
- Certificado e-CNPJ ou e-CPF válido

### 2. Inscrição Estadual

A propriedade precisa ter **Inscrição Estadual** cadastrada.

### 3. Dados da Empresa

- CNPJ da propriedade/produtor
- Endereço completo
- CNAE Fiscal
- Código de Regime Tributário (CRT)

## ⚙️ Configuração

Adicione as seguintes configurações no arquivo `settings.py`:

```python
# Configuração para emissão direta com SEFAZ
NFE_SEFAZ = {
    'USAR_DIRETO': True,  # Ativar emissão direta
    'CERTIFICADO_PATH': '/caminho/para/certificado.p12',  # Caminho do certificado
    'SENHA_CERTIFICADO': 'senha_do_certificado',  # Senha do certificado
    'AMBIENTE': 'homologacao',  # 'homologacao' ou 'producao'
    'UF': 'SP',  # UF do emitente
    'UF_EMITENTE': '35',  # Código da UF (SP = 35)
    'CODIGO_MUNICIPIO': '3550308',  # Código do município (IBGE)
    'CNPJ_EMITENTE': '12345678000190',  # CNPJ da propriedade
    'CNAE_FISCAL': '0142100',  # CNAE Fiscal (exemplo)
    'CRT': '3',  # 1=Simples, 2=Simples excesso, 3=Regime Normal
}
```

## 📦 Bibliotecas Necessárias

As seguintes bibliotecas já foram adicionadas ao `requirements.txt`:

- `pyOpenSSL>=23.0.0` - Para certificados digitais
- `lxml>=4.9.0` - Para processamento XML
- `zeep>=4.2.0` - Cliente SOAP para comunicação com SEFAZ
- `xmlsec>=1.3.13` - Para assinatura digital XML

**Instalar:**
```bash
pip install -r requirements.txt
```

## 🔧 Implementação Atual

O sistema já possui uma estrutura básica em `gestao_rural/services_nfe_sefaz.py` que:

1. ✅ Gera XML da NF-e conforme layout oficial
2. ✅ Estrutura básica para assinatura digital
3. ✅ Estrutura básica para envio à SEFAZ

## ⚠️ Implementação Completa Necessária

Para funcionamento completo, você precisará implementar:

### 1. Assinatura Digital Completa

A assinatura XML requer:
- Carregamento correto do certificado PKCS12
- Assinatura do XML conforme padrão XML-DSig
- Validação da assinatura

**Bibliotecas recomendadas:**
- `PyNFe` - Biblioteca completa para NF-e
- `PyTrustNFe` - Biblioteca focada em comunicação com SEFAZ
- `xmlsec` - Para assinatura XML

### 2. Comunicação SOAP com SEFAZ

Cada UF tem seu próprio webservice. Você precisa:

- Implementar cliente SOAP para cada UF
- Tratar autenticação com certificado
- Processar respostas da SEFAZ
- Tratar erros e retornos

### 3. Validações e Regras de Negócio

- Validação de campos obrigatórios
- Cálculo de impostos (ICMS, PIS, COFINS)
- Validação de CFOP e NCM
- Cálculo de chave de acesso
- Validação de dígito verificador

## 🚀 Opções de Implementação

### Opção 1: Usar Biblioteca PyNFe (Recomendado)

```bash
pip install pynfe
```

**Vantagens:**
- ✅ Implementação completa e testada
- ✅ Suporta todas as UFs
- ✅ Mantida pela comunidade
- ✅ Documentação disponível

**Desvantagens:**
- ⚠️ Pode ter dependências específicas
- ⚠️ Requer adaptação ao seu modelo de dados

### Opção 2: Usar Biblioteca PyTrustNFe

```bash
pip install pytrustnfe
```

**Vantagens:**
- ✅ Focada em comunicação com SEFAZ
- ✅ Interface simplificada
- ✅ Boa documentação

### Opção 3: Implementação Própria

Você pode completar a implementação em `services_nfe_sefaz.py`:

1. Completar função `_assinar_xml_nfe()` com assinatura XML-DSig
2. Completar função `_enviar_para_sefaz()` com comunicação SOAP
3. Implementar tratamento de respostas da SEFAZ
4. Adicionar suporte para todas as UFs necessárias

## 📚 Documentação Oficial

- **Manual de Integração do Contribuinte**: Disponível no site da SEFAZ de cada estado
- **Layout NF-e 4.00**: Especificações técnicas oficiais
- **Webservices SEFAZ**: URLs e endpoints por UF

## 🔐 Segurança

- ⚠️ **NUNCA** commite o certificado digital no repositório
- ⚠️ **NUNCA** commite a senha do certificado
- ✅ Use variáveis de ambiente para senhas
- ✅ Armazene certificados em local seguro
- ✅ Use permissões de arquivo restritivas

## 📝 Exemplo de Configuração com Variáveis de Ambiente

```python
# settings.py
import os

NFE_SEFAZ = {
    'USAR_DIRETO': True,
    'CERTIFICADO_PATH': os.getenv('NFE_CERTIFICADO_PATH', ''),
    'SENHA_CERTIFICADO': os.getenv('NFE_SENHA_CERTIFICADO', ''),
    'AMBIENTE': os.getenv('NFE_AMBIENTE', 'homologacao'),
    'UF': os.getenv('NFE_UF', 'SP'),
    # ... outros campos
}
```

## 🧪 Testes

1. **Ambiente de Homologação**: Use sempre primeiro para testes
2. **Validação de XML**: Valide o XML antes de enviar
3. **Testes Incrementais**: Teste cada parte separadamente

## 📞 Suporte

Para implementação completa, recomenda-se:
1. Consultar a documentação oficial da SEFAZ do seu estado
2. Usar biblioteca especializada (PyNFe ou PyTrustNFe)
3. Contratar consultoria especializada se necessário

## 🔄 Próximos Passos

1. Instalar biblioteca especializada (PyNFe recomendado)
2. Configurar certificado digital
3. Testar em ambiente de homologação
4. Ajustar configurações conforme necessário
5. Migrar para produção após testes completos

