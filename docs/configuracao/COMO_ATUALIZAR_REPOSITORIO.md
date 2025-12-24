# 🚀 COMO ATUALIZAR O REPOSITÓRIO NO OUTRO COMPUTADOR



## ⚡ MÉTODO RÁPIDO (RECOMENDADO)



### **Passo 1: Abrir PowerShell no outro computador**



### **Passo 2: Navegar até a pasta do projeto**



```powershell

cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentário\Monpec_GestaoRural"

```



*(Ajuste o caminho se estiver em outro local)*



### **Passo 3: Executar o script**



```powershell

.\atualizar_repositorio.ps1

```



**Pronto!** O script vai:

- ✅ Verificar se há atualizações no GitHub

- ✅ Mostrar o que será atualizado

- ✅ Perguntar se você quer atualizar

- ✅ Atualizar todos os arquivos automaticamente



---



## 📋 MÉTODO MANUAL (SE O SCRIPT NÃO FUNCIONAR)



Se o script não funcionar, use estes comandos:



```powershell

cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentário\Monpec_GestaoRural"

git pull origin master

```



---



## ⚠️ SE DER ERRO DE PERMISSÃO



Se aparecer erro de "Execution Policy", execute primeiro:



```powershell

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

```



Depois execute o script novamente.



---



## ✅ VERIFICAR SE ATUALIZOU



Depois de executar, verifique:



```powershell

git log --oneline -1

```



Você deve ver o commit mais recente. Se aparecer, está atualizado! ✅

