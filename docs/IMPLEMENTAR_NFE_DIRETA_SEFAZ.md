# Implementação de Emissão de NF-e Direta com SEFAZ

Como empresa desenvolvedora, você pode emitir NF-e diretamente com a SEFAZ sem usar APIs terceiras.

## 🎯 Estrutura Criada

Foi criada a estrutura básica em `gestao_rural/services_nfe_sefaz.py` que:
- ✅ Gera XML da NF-e conforme layout oficial
- ✅ Estrutura para assinatura digital
- ✅ Estrutura para envio à SEFAZ

## 📦 Opções de Implementação

### Opção 1: Usar PyNFe (Recomendado)

**PyNFe** é a biblioteca Python mais completa para NF-e:

```bash
pip install pynfe
```

**Vantagens:**
- ✅ Implementação completa e testada
- ✅ Suporta todas as UFs brasileiras
- ✅ Comunidade ativa
- ✅ Documentação disponível

**Exemplo de uso:**
```python
from pynfe.processamento.comunicacao import ComunicacaoSefaz
from pynfe.processamento.serializacao import SerializacaoXML
from pynfe.processamento.assinatura import AssinaturaA1

# Configurar certificado
certificado = 'caminho/certificado.p12'
senha = 'senha_certificado'

# Criar instância
nfe = SerializacaoXML(certificado, senha)

# Gerar e assinar NF-e
xml_assinado = nfe.gerar_nfe(nota_fiscal)

# Enviar para SEFAZ
comunicacao = ComunicacaoSefaz(uf='SP', certificado=certificado, senha=senha)
resultado = comunicacao.autorizar(modelo='nfe', versao='4.00', xml=xml_assinado)
```

### Opção 2: Usar PyTrustNFe

```bash
pip install pytrustnfe
```

**Vantagens:**
- ✅ Interface simplificada
- ✅ Focada em comunicação com SEFAZ
- ✅ Boa documentação

### Opção 3: Completar Implementação Própria

Você pode completar a implementação em `services_nfe_sefaz.py`:

1. **Assinatura Digital**: Implementar assinatura XML-DSig completa
2. **Comunicação SOAP**: Implementar cliente SOAP para cada UF
3. **Validações**: Adicionar todas as validações necessárias

## ⚙️ Configuração no settings.py

```python
# Configuração para emissão direta com SEFAZ
NFE_SEFAZ = {
    'USAR_DIRETO': True,  # Ativar emissão direta
    'CERTIFICADO_PATH': os.getenv('NFE_CERTIFICADO_PATH', ''),
    'SENHA_CERTIFICADO': os.getenv('NFE_SENHA_CERTIFICADO', ''),
    'AMBIENTE': os.getenv('NFE_AMBIENTE', 'homologacao'),  # 'homologacao' ou 'producao'
    'UF': os.getenv('NFE_UF', 'SP'),
    'UF_EMITENTE': '35',  # Código da UF (SP = 35)
    'CODIGO_MUNICIPIO': '3550308',  # Código do município (IBGE)
    'CNPJ_EMITENTE': '12345678000190',  # CNPJ da propriedade
    'CNAE_FISCAL': '0142100',  # CNAE Fiscal
    'CRT': '3',  # 1=Simples, 2=Simples excesso, 3=Regime Normal
}
```

## 🔐 Certificado Digital

### Tipos de Certificado

1. **A1 (Arquivo)**: Arquivo `.p12` ou `.pfx`
   - Mais fácil de usar
   - Pode ser copiado
   - Válido por 1 ano

2. **A3 (Token/Cartão)**: Hardware físico
   - Mais seguro
   - Não pode ser copiado
   - Válido por 3 anos
   - Requer driver específico

### Onde Obter

- **Serasa**: https://www.serasa.com.br/certificado-digital
- **Certisign**: https://www.certisign.com.br
- **Serpro**: https://www.serpro.gov.br
- Outras ACs credenciadas pela ICP-Brasil

## 📋 Checklist de Implementação

- [ ] Obter certificado digital A1 ou A3
- [ ] Instalar biblioteca especializada (PyNFe recomendado)
- [ ] Configurar `NFE_SEFAZ` nas settings
- [ ] Testar em ambiente de homologação
- [ ] Validar XML gerado
- [ ] Testar assinatura digital
- [ ] Testar envio para SEFAZ
- [ ] Processar respostas da SEFAZ
- [ ] Implementar tratamento de erros
- [ ] Migrar para produção após testes

## 🧪 Ambiente de Homologação

**Importante**: Sempre teste primeiro em homologação!

- NF-e de homologação **NÃO têm validade fiscal**
- Use para testes e desenvolvimento
- URLs de homologação são diferentes por UF

## 📚 Recursos

- **Manual de Integração**: Site da SEFAZ de cada estado
- **Layout NF-e 4.00**: Especificações técnicas oficiais
- **PyNFe GitHub**: https://github.com/TadaSoftware/PyNFe
- **PyTrustNFe Docs**: https://pytrustnfe.readthedocs.io

## ⚠️ Importante

1. **Certificado**: Nunca commite no repositório
2. **Senha**: Use variáveis de ambiente
3. **Testes**: Sempre teste em homologação primeiro
4. **Validação**: Valide XML antes de enviar
5. **Backup**: Mantenha backup do certificado em local seguro

## 🔄 Próximos Passos Recomendados

1. **Instalar PyNFe**: `pip install pynfe`
2. **Configurar certificado**: Adicionar caminho e senha nas settings
3. **Atualizar serviço**: Integrar PyNFe em `services_nfe_sefaz.py`
4. **Testar**: Emitir NF-e de teste em homologação
5. **Produção**: Migrar após validação completa

