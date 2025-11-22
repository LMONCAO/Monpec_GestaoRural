# Script Interativo para Guiar Configuração de Domínio
# Este script faz perguntas e guia você passo a passo

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GUIA INTERATIVO - CONFIGURAR DOMÍNIO" -ForegroundColor Cyan
Write-Host "  monpec.com.br no Google Cloud Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Este guia vai te ajudar passo a passo!" -ForegroundColor Green
Write-Host ""

# Pergunta inicial
Write-Host "Em que etapa você está?" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Ainda não comecei - preciso de ajuda para começar" -ForegroundColor White
Write-Host "2. Estou no Google Cloud Console - preciso saber o que fazer" -ForegroundColor White
Write-Host "3. Já mapeei no Google Cloud - agora preciso configurar no Registro.br" -ForegroundColor White
Write-Host "4. Estou no Registro.br - não sei onde adicionar os registros DNS" -ForegroundColor White
Write-Host "5. Já configurei tudo - preciso saber como verificar se funcionou" -ForegroundColor White
Write-Host "6. Tenho um problema específico - preciso de ajuda" -ForegroundColor White
Write-Host ""

$etapa = Read-Host "Digite o número da sua situação (1-6)"

switch ($etapa) {
    "1" {
        Write-Host ""
        Write-Host "=== VOCÊ ESTÁ NO INÍCIO ===" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Você precisa fazer 2 coisas principais:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. No Google Cloud Run:" -ForegroundColor White
        Write-Host "   - Mapear o domínio monpec.com.br" -ForegroundColor Gray
        Write-Host "   - Anotar os registros DNS fornecidos" -ForegroundColor Gray
        Write-Host ""
        Write-Host "2. No Registro.br:" -ForegroundColor White
        Write-Host "   - Adicionar os registros DNS no painel" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Vamos começar?" -ForegroundColor Yellow
        Write-Host ""
        
        $comecar = Read-Host "Deseja abrir o Google Cloud Console agora? (S/N)"
        if ($comecar -eq "S" -or $comecar -eq "s") {
            Write-Host ""
            Write-Host "Abrindo Google Cloud Console..." -ForegroundColor Green
            Start-Process "https://console.cloud.google.com/run"
            Write-Host ""
            Write-Host "Siga estas instruções:" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "1. Selecione o projeto correto (se tiver vários)" -ForegroundColor White
            Write-Host "2. Procure pelo serviço 'monpec'" -ForegroundColor White
            Write-Host "3. Clique no serviço 'monpec'" -ForegroundColor White
            Write-Host "4. Procure pela aba 'DOMÍNIOS CUSTOMIZADOS' no topo" -ForegroundColor White
            Write-Host "5. Clique em 'ADICIONAR Mapeamento de Domínio'" -ForegroundColor White
            Write-Host "6. Digite: monpec.com.br" -ForegroundColor White
            Write-Host "7. Clique em CONTINUAR" -ForegroundColor White
            Write-Host ""
            Write-Host "⚠️ IMPORTANTE: Anote todos os registros DNS que aparecerem!" -ForegroundColor Yellow
            Write-Host ""
        }
    }
    
    "2" {
        Write-Host ""
        Write-Host "=== VOCÊ ESTÁ NO GOOGLE CLOUD CONSOLE ===" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Instruções passo a passo:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. Certifique-se de que está no projeto correto" -ForegroundColor White
        Write-Host "2. Na lista de serviços, encontre 'monpec'" -ForegroundColor White
        Write-Host "3. Clique no serviço 'monpec'" -ForegroundColor White
        Write-Host ""
        Write-Host "Na página do serviço:" -ForegroundColor Yellow
        Write-Host "4. Procure por ABAS no topo da página (tabs)" -ForegroundColor White
        Write-Host "5. Clique na aba 'DOMÍNIOS CUSTOMIZADOS' ou 'Custom Domains'" -ForegroundColor White
        Write-Host "6. Clique no botão 'ADICIONAR Mapeamento de Domínio'" -ForegroundColor White
        Write-Host "7. Digite: monpec.com.br" -ForegroundColor White
        Write-Host "8. Clique em CONTINUAR" -ForegroundColor White
        Write-Host ""
        Write-Host "Depois de clicar em CONTINUAR:" -ForegroundColor Yellow
        Write-Host "9. O Google vai mostrar REGISTROS DNS" -ForegroundColor White
        Write-Host "10. ⚠️ ANOTE TODOS esses registros (IP do tipo A e valor do tipo CNAME)" -ForegroundColor Red
        Write-Host ""
        Write-Host "Tire uma foto ou copie para um documento!" -ForegroundColor Yellow
        Write-Host ""
        
        $proximo = Read-Host "Depois de anotar os registros, você vai configurar no Registro.br. Quer que eu abra o guia do Registro.br? (S/N)"
        if ($proximo -eq "S" -or $proximo -eq "s") {
            Start-Process "CONFIGURAR_DOMINIO_PASSO_A_PASSO.md"
        }
    }
    
    "3" {
        Write-Host ""
        Write-Host "=== CONFIGURAR NO REGISTRO.BR ===" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Ótimo! Você já tem os registros DNS do Google Cloud." -ForegroundColor Green
        Write-Host ""
        Write-Host "Agora você precisa:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. Acessar: https://registro.br/painel/" -ForegroundColor White
        Write-Host "2. Fazer login na sua conta" -ForegroundColor White
        Write-Host "3. Encontrar onde adicionar registros DNS" -ForegroundColor White
        Write-Host ""
        
        Write-Host "Onde encontrar no Registro.br:" -ForegroundColor Yellow
        Write-Host "- Procure no menu lateral por: 'DNS' ou 'Zona DNS' ou 'Registros DNS'" -ForegroundColor White
        Write-Host "- Se não encontrar, procure por: 'UTILIZAR DNS DO REGISTRO.BR' e clique" -ForegroundColor White
        Write-Host ""
        
        Write-Host "Você tem os registros DNS anotados?" -ForegroundColor Yellow
        $temRegistros = Read-Host "Você tem os registros DNS do Google Cloud? (S/N)"
        
        if ($temRegistros -eq "S" -or $temRegistros -eq "s") {
            Write-Host ""
            Write-Host "Perfeito! Agora você precisa adicionar:" -ForegroundColor Green
            Write-Host ""
            Write-Host "1. Registro tipo A:" -ForegroundColor Yellow
            Write-Host "   - Nome/Host: @ ou deixe em branco" -ForegroundColor White
            Write-Host "   - Valor: [o IP que o Google Cloud forneceu]" -ForegroundColor White
            Write-Host ""
            Write-Host "2. Registro tipo CNAME:" -ForegroundColor Yellow
            Write-Host "   - Nome/Host: www" -ForegroundColor White
            Write-Host "   - Valor: [o valor que o Google Cloud forneceu, geralmente ghs.googlehosted.com]" -ForegroundColor White
            Write-Host ""
            Write-Host "Você encontrou onde adicionar esses registros no Registro.br?" -ForegroundColor Yellow
            $encontrou = Read-Host "Conseguiu encontrar a seção de registros DNS? (S/N)"
            
            if ($encontrou -ne "S" -and $encontrou -ne "s") {
                Write-Host ""
                Write-Host "⚠️ Se você não encontrou:" -ForegroundColor Yellow
                Write-Host "1. Ligue para o suporte do Registro.br: 0800 777 0001" -ForegroundColor White
                Write-Host "2. Peça para ativar 'DNS Hosting' ou 'Zona DNS'" -ForegroundColor White
                Write-Host "3. Peça para mostrar onde adicionar registros tipo A e CNAME" -ForegroundColor White
                Write-Host ""
            }
        } else {
            Write-Host ""
            Write-Host "⚠️ Você precisa dos registros DNS primeiro!" -ForegroundColor Red
            Write-Host "Volte para o Passo 2 (Google Cloud Console) e anote os registros." -ForegroundColor Yellow
            Write-Host ""
        }
        
        Write-Host "Abrindo guia completo..." -ForegroundColor Green
        Start-Process "CONFIGURAR_DOMINIO_PASSO_A_PASSO.md"
    }
    
    "4" {
        Write-Host ""
        Write-Host "=== VOCÊ ESTÁ NO REGISTRO.BR ===" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Se você está vendo 'ALTERAR SERVIDORES DNS':" -ForegroundColor Yellow
        Write-Host "- Isso NÃO é o que você precisa!" -ForegroundColor Red
        Write-Host "- Você precisa encontrar 'Zona DNS' ou 'Registros DNS'" -ForegroundColor White
        Write-Host ""
        Write-Host "O que fazer:" -ForegroundColor Yellow
        Write-Host "1. Procure no MENU LATERAL por:" -ForegroundColor White
        Write-Host "   - 'DNS' → 'Zona DNS'" -ForegroundColor Gray
        Write-Host "   - 'DNS' → 'Registros DNS'" -ForegroundColor Gray
        Write-Host "   - 'Gerenciar' → 'DNS'" -ForegroundColor Gray
        Write-Host ""
        Write-Host "2. Se não encontrar, procure por um botão:" -ForegroundColor White
        Write-Host "   - 'UTILIZAR DNS DO REGISTRO.BR' (botão cinza)" -ForegroundColor Gray
        Write-Host "   - Clique nele para ativar o DNS Hosting" -ForegroundColor Gray
        Write-Host "   - Aguarde alguns minutos e atualize a página (F5)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "3. Depois de ativar, você deve ver uma seção para adicionar registros" -ForegroundColor White
        Write-Host ""
        
        Write-Host "Ainda não encontrou?" -ForegroundColor Yellow
        $naoEncontrou = Read-Host "Não conseguiu encontrar onde adicionar registros? (S/N)"
        
        if ($naoEncontrou -eq "S" -or $naoEncontrou -eq "s") {
            Write-Host ""
            Write-Host "📞 Contate o suporte do Registro.br:" -ForegroundColor Cyan
            Write-Host "   Telefone: 0800 777 0001" -ForegroundColor White
            Write-Host "   Email: suporte@registro.br" -ForegroundColor White
            Write-Host ""
            Write-Host "O que pedir:" -ForegroundColor Yellow
            Write-Host "- Ativar 'DNS Hosting' ou 'Zona DNS' para monpec.com.br" -ForegroundColor White
            Write-Host "- Mostrar onde adicionar registros tipo A, CNAME e TXT" -ForegroundColor White
            Write-Host ""
        }
        
        Write-Host "Abrindo guia completo..." -ForegroundColor Green
        Start-Process "CONFIGURAR_DOMINIO_PASSO_A_PASSO.md"
    }
    
    "5" {
        Write-Host ""
        Write-Host "=== VERIFICAR SE FUNCIONOU ===" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Após configurar os registros DNS:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. Aguarde 15 minutos - 2 horas para propagação DNS" -ForegroundColor White
        Write-Host ""
        Write-Host "2. Verificar propagação DNS:" -ForegroundColor Yellow
        Write-Host "   - Acesse: https://dnschecker.org" -ForegroundColor White
        Write-Host "   - Digite: monpec.com.br" -ForegroundColor White
        Write-Host "   - Selecione: Tipo A" -ForegroundColor White
        Write-Host "   - Clique em Search" -ForegroundColor White
        Write-Host ""
        Write-Host "3. Testar o site:" -ForegroundColor Yellow
        Write-Host "   - Acesse: https://monpec.com.br" -ForegroundColor White
        Write-Host "   - Verifique se o site carrega" -ForegroundColor White
        Write-Host ""
        Write-Host "4. SSL/HTTPS:" -ForegroundColor Yellow
        Write-Host "   - O certificado SSL pode demorar até 24 horas" -ForegroundColor White
        Write-Host "   - Se aparecer 'não seguro', aguarde mais um pouco" -ForegroundColor White
        Write-Host ""
        
        Write-Host "Deseja testar agora?" -ForegroundColor Yellow
        $testar = Read-Host "Quer que eu abra o site para testar? (S/N)"
        if ($testar -eq "S" -or $testar -eq "s") {
            Start-Process "https://monpec.com.br"
            Start-Process "https://dnschecker.org"
        }
    }
    
    "6" {
        Write-Host ""
        Write-Host "=== AJUDA COM PROBLEMAS ===" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Qual é o seu problema?" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. Não encontro a aba 'DOMÍNIOS CUSTOMIZADOS' no Google Cloud" -ForegroundColor White
        Write-Host "2. Não encontro onde adicionar registros DNS no Registro.br" -ForegroundColor White
        Write-Host "3. Não sei quais são os valores corretos dos registros" -ForegroundColor White
        Write-Host "4. O site não está funcionando após configurar" -ForegroundColor White
        Write-Host "5. Outro problema" -ForegroundColor White
        Write-Host ""
        
        $problema = Read-Host "Digite o número do seu problema (1-5)"
        
        switch ($problema) {
            "1" {
                Write-Host ""
                Write-Host "Soluções:" -ForegroundColor Yellow
                Write-Host "- Verifique se está na página do serviço 'monpec'" -ForegroundColor White
                Write-Host "- Role a página para baixo - a aba pode estar mais abaixo" -ForegroundColor White
                Write-Host "- Atualize a página (F5)" -ForegroundColor White
                Write-Host "- Verifique se tem permissões de administrador no projeto" -ForegroundColor White
                Write-Host ""
            }
            "2" {
                Write-Host ""
                Write-Host "Soluções:" -ForegroundColor Yellow
                Write-Host "- Procure no menu lateral: 'DNS' → 'Zona DNS'" -ForegroundColor White
                Write-Host "- Ou clique em 'UTILIZAR DNS DO REGISTRO.BR' para ativar" -ForegroundColor White
                Write-Host "- Ligue para o suporte: 0800 777 0001" -ForegroundColor White
                Write-Host ""
            }
            "3" {
                Write-Host ""
                Write-Host "Os valores vêm do Google Cloud:" -ForegroundColor Yellow
                Write-Host "- Você precisa mapear o domínio no Cloud Run primeiro" -ForegroundColor White
                Write-Host "- O Google Cloud mostrará os valores corretos" -ForegroundColor White
                Write-Host "- Tire uma foto ou copie os valores para um documento" -ForegroundColor White
                Write-Host ""
            }
            "4" {
                Write-Host ""
                Write-Host "Verificações:" -ForegroundColor Yellow
                Write-Host "- Aguardou pelo menos 15 minutos após configurar?" -ForegroundColor White
                Write-Host "- Verificou se os registros DNS foram salvos corretamente?" -ForegroundColor White
                Write-Host "- Os valores estão exatamente como o Google Cloud forneceu?" -ForegroundColor White
                Write-Host "- Testou a propagação em: https://dnschecker.org" -ForegroundColor White
                Write-Host ""
                Write-Host "Se ainda não funcionar, aguarde até 2 horas (propagação pode demorar)" -ForegroundColor Yellow
                Write-Host ""
            }
            "5" {
                Write-Host ""
                Write-Host "Abra o guia completo para mais informações:" -ForegroundColor Yellow
                Start-Process "CONFIGURAR_DOMINIO_PASSO_A_PASSO.md"
                Write-Host ""
            }
        }
    }
    
    default {
        Write-Host ""
        Write-Host "❌ Opção inválida!" -ForegroundColor Red
        Write-Host "Por favor, digite um número de 1 a 6" -ForegroundColor Yellow
        Write-Host ""
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deseja abrir o guia completo passo a passo?" -ForegroundColor Yellow
$abrir = Read-Host "Abrir CONFIGURAR_DOMINIO_PASSO_A_PASSO.md? (S/N)"

if ($abrir -eq "S" -or $abrir -eq "s") {
    Start-Process "CONFIGURAR_DOMINIO_PASSO_A_PASSO.md"
}

Write-Host ""
Write-Host "Boa sorte!" -ForegroundColor Green
Write-Host ""

