# Guia Completo: Emissão de NF-e Direta com SEFAZ

Como empresa desenvolvedora, você pode emitir NF-e diretamente com a SEFAZ sem depender de APIs terceiras.

## ✅ O que foi implementado

1. **Estrutura básica** em `gestao_rural/services_nfe_sefaz.py`
   - Geração de XML conforme layout oficial
   - Estrutura para assinatura digital
   - Estrutura para comunicação com SEFAZ

2. **Exemplo com PyNFe** em `gestao_rural/services_nfe_sefaz_pynfe.py`
   - Implementação completa usando biblioteca especializada
   - Pronta para uso após instalar PyNFe

3. **Integração automática** no sistema
   - O sistema tenta usar PyNFe se disponível
   - Caso contrário, usa estrutura básica (requer completar)

## 🚀 Implementação Rápida (Recomendada)

### Passo 1: Instalar PyNFe

```bash
pip install pynfe
```

### Passo 2: Configurar settings.py

```python
# settings.py
import os

# Configuração para emissão direta com SEFAZ
NFE_SEFAZ = {
    'USAR_DIRETO': True,  # Ativar emissão direta
    'CERTIFICADO_PATH': os.getenv('NFE_CERTIFICADO_PATH', '/caminho/certificado.p12'),
    'SENHA_CERTIFICADO': os.getenv('NFE_SENHA_CERTIFICADO', ''),
    'AMBIENTE': os.getenv('NFE_AMBIENTE', 'homologacao'),  # 'homologacao' ou 'producao'
    'UF': os.getenv('NFE_UF', 'SP'),
    'UF_EMITENTE': '35',  # Código da UF (SP = 35)
    'CODIGO_MUNICIPIO': '3550308',  # Código do município (IBGE)
    'CNPJ_EMITENTE': '12345678000190',  # CNPJ da propriedade
    'CNAE_FISCAL': '0142100',  # CNAE Fiscal (exemplo: criação de bovinos)
    'CRT': '3',  # 1=Simples, 2=Simples excesso, 3=Regime Normal
}
```

### Passo 3: Obter Certificado Digital

1. **Escolha uma Autoridade Certificadora (AC)**:
   - Serasa, Certisign, Serpro, etc.

2. **Tipo de Certificado**:
   - **A1 (Arquivo)**: Mais fácil, arquivo `.p12` ou `.pfx`
   - **A3 (Token)**: Mais seguro, hardware físico

3. **Documentos necessários**:
   - CNPJ da empresa
   - Documentos do responsável
   - Comprovante de endereço

### Passo 4: Testar em Homologação

1. Configure `AMBIENTE: 'homologacao'`
2. Emita uma NF-e de teste
3. Verifique se foi autorizada
4. Valide todos os campos

### Passo 5: Migrar para Produção

1. Configure `AMBIENTE: 'producao'`
2. Use certificado de produção
3. Teste novamente
4. Monitore primeiras emissões

## 📋 Checklist de Configuração

- [ ] Certificado digital obtido e instalado
- [ ] PyNFe instalado (`pip install pynfe`)
- [ ] `NFE_SEFAZ` configurado nas settings
- [ ] Certificado digital em local seguro
- [ ] Senha do certificado em variável de ambiente
- [ ] Código do município (IBGE) configurado
- [ ] CNAE Fiscal configurado
- [ ] CRT (Código de Regime Tributário) configurado
- [ ] Inscrição Estadual da propriedade cadastrada
- [ ] Testado em ambiente de homologação
- [ ] Validado XML gerado
- [ ] Testado envio para SEFAZ
- [ ] Processado respostas da SEFAZ
- [ ] Tratamento de erros implementado

## 🔐 Segurança

### ⚠️ IMPORTANTE

1. **NUNCA** commite o certificado digital no Git
2. **NUNCA** commite a senha do certificado
3. Use variáveis de ambiente para senhas
4. Armazene certificados em local seguro
5. Use permissões restritivas no arquivo do certificado

### Exemplo de .gitignore

```
# Certificados digitais
*.p12
*.pfx
*.pem
*.key
certificados/
```

## 📚 Documentação e Recursos

### Bibliotecas Python

- **PyNFe**: https://github.com/TadaSoftware/PyNFe
- **PyTrustNFe**: https://pytrustnfe.readthedocs.io
- **nfelib**: https://pypi.org/project/nfelib/

### Documentação Oficial

- **Manual de Integração**: Site da SEFAZ de cada estado
- **Layout NF-e 4.00**: Especificações técnicas oficiais
- **Webservices SEFAZ**: URLs e endpoints por UF

### Links Úteis

- **Consulta de Códigos IBGE**: https://www.ibge.gov.br/explica/codigos-dos-municipios.php
- **Consulta de CNAE**: https://cnae.ibge.gov.br/
- **SEFAZ por Estado**: Cada estado tem seu próprio site

## 🧪 Testes

### Ambiente de Homologação

- ✅ Use sempre primeiro para testes
- ✅ NF-e de homologação **NÃO têm validade fiscal**
- ✅ URLs diferentes por UF
- ✅ Certificado de homologação (geralmente fornecido pela AC)

### Validação

1. **Validação de XML**: Use validador oficial da SEFAZ
2. **Validação de Assinatura**: Verifique assinatura digital
3. **Validação de Envio**: Teste envio para SEFAZ
4. **Validação de Resposta**: Processe respostas corretamente

## 🔄 Fluxo de Emissão

```
1. Criar NF-e no sistema
   ↓
2. Gerar XML da NF-e
   ↓
3. Assinar XML com certificado digital
   ↓
4. Enviar para SEFAZ (webservice SOAP)
   ↓
5. Receber resposta da SEFAZ
   ↓
6. Processar autorização/rejeição
   ↓
7. Salvar chave de acesso e protocolo
   ↓
8. Gerar DANFE (PDF) se autorizado
```

## 💡 Dicas

1. **Comece simples**: Use PyNFe para começar rapidamente
2. **Teste muito**: Sempre teste em homologação primeiro
3. **Monitore logs**: Acompanhe todos os erros
4. **Valide dados**: Certifique-se de que todos os dados estão corretos
5. **Backup**: Mantenha backup do certificado em local seguro

## 🆘 Problemas Comuns

### Erro: "Certificado não encontrado"
- Verifique o caminho do certificado
- Verifique permissões do arquivo
- Certifique-se de que o arquivo existe

### Erro: "Senha do certificado incorreta"
- Verifique a senha configurada
- Teste abrindo o certificado manualmente

### Erro: "XML inválido"
- Valide o XML gerado
- Verifique todos os campos obrigatórios
- Consulte o manual de validação da SEFAZ

### Erro: "Comunicação com SEFAZ falhou"
- Verifique conexão com internet
- Verifique URL do webservice
- Verifique certificado e autenticação

## 📞 Próximos Passos

1. **Instalar PyNFe**: `pip install pynfe`
2. **Configurar certificado**: Adicionar caminho e senha
3. **Testar em homologação**: Emitir NF-e de teste
4. **Validar**: Verificar se tudo funciona
5. **Produção**: Migrar após validação completa

---

**Nota**: A estrutura básica está pronta. Para funcionamento completo, instale PyNFe e configure o certificado digital conforme este guia.

