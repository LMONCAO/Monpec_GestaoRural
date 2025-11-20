# ========================================
# CRIAR TEMPLATES FALTANTES
# ========================================

Write-Host "🎨 CRIANDO TEMPLATES FALTANTES" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Yellow

# 1. IR PARA DIRETÓRIO
Write-Host "📁 Navegando para diretório..." -ForegroundColor Cyan
Set-Location "monpec_clean"

# 2. CRIAR TEMPLATE PROPRIETARIOS_LISTA
Write-Host "📄 Criando proprietarios_lista.html..." -ForegroundColor Cyan

@"
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Proprietários - Monpec Projetista</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8f9fa;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .header {
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 1rem 0;
            margin-bottom: 2rem;
        }
        
        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: 700;
            color: #004a99;
        }
        
        .nav-links {
            display: flex;
            gap: 2rem;
        }
        
        .nav-links a {
            color: #666;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
        }
        
        .nav-links a:hover {
            color: #004a99;
        }
        
        .user-menu {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .btn-logout {
            background: #dc3545;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            text-decoration: none;
            font-size: 0.9rem;
        }
        
        .page-header {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .page-header h1 {
            font-size: 2rem;
            font-weight: 700;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .page-header p {
            color: #666;
            font-size: 1.1rem;
        }
        
        .actions {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .actions h2 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #333;
        }
        
        .btn-group {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
        }
        
        .btn-primary {
            background: #004a99;
            color: white;
        }
        
        .btn-primary:hover {
            background: #003366;
            transform: translateY(-2px);
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-success:hover {
            background: #218838;
            transform: translateY(-2px);
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
            transform: translateY(-2px);
        }
        
        .search-form {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .search-form h3 {
            margin-bottom: 1rem;
            color: #333;
        }
        
        .form-group {
            display: flex;
            gap: 1rem;
            align-items: end;
        }
        
        .form-control {
            padding: 0.75rem;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #004a99;
        }
        
        .proprietarios-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }
        
        .proprietario-card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 1.5rem;
            transition: transform 0.3s;
        }
        
        .proprietario-card:hover {
            transform: translateY(-5px);
        }
        
        .proprietario-header {
            border-bottom: 1px solid #e9ecef;
            padding-bottom: 1rem;
            margin-bottom: 1rem;
        }
        
        .proprietario-name {
            font-size: 1.25rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .proprietario-cpf {
            color: #666;
            font-size: 0.9rem;
        }
        
        .proprietario-info {
            margin-bottom: 1rem;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
        }
        
        .info-label {
            color: #666;
            font-weight: 500;
        }
        
        .info-value {
            color: #333;
        }
        
        .proprietario-actions {
            display: flex;
            gap: 0.5rem;
        }
        
        .btn-small {
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
        }
        
        .empty-state {
            text-align: center;
            padding: 3rem;
            color: #666;
        }
        
        .empty-state h3 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #999;
        }
        
        .pagination {
            display: flex;
            justify-content: center;
            gap: 0.5rem;
            margin-top: 2rem;
        }
        
        .pagination a {
            padding: 0.5rem 1rem;
            background: white;
            color: #004a99;
            text-decoration: none;
            border-radius: 6px;
            border: 1px solid #e9ecef;
            transition: all 0.3s;
        }
        
        .pagination a:hover {
            background: #004a99;
            color: white;
        }
        
        .pagination .current {
            background: #004a99;
            color: white;
        }
        
        @media (max-width: 768px) {
            .nav-links {
                display: none;
            }
            
            .proprietarios-grid {
                grid-template-columns: 1fr;
            }
            
            .form-group {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <nav class="nav">
                <div class="logo">Monpec Projetista</div>
                <div class="nav-links">
                    <a href="{% url 'dashboard' %}">Dashboard</a>
                    <a href="{% url 'proprietarios_lista' %}">Proprietários</a>
                    <a href="{% url 'propriedades_lista' %}">Propriedades</a>
                </div>
                <div class="user-menu">
                    <span>Olá, {{ user.username }}</span>
                    <a href="{% url 'logout' %}" class="btn-logout">Sair</a>
                </div>
            </nav>
        </div>
    </header>
    
    <main>
        <div class="container">
            <div class="page-header">
                <h1>Proprietários</h1>
                <p>Gerencie todos os proprietários rurais cadastrados</p>
            </div>
            
            <div class="actions">
                <h2>Ações</h2>
                <div class="btn-group">
                    <a href="{% url 'proprietario_novo' %}" class="btn btn-primary">Novo Proprietário</a>
                    <a href="{% url 'dashboard' %}" class="btn btn-secondary">Voltar ao Dashboard</a>
                </div>
            </div>
            
            <div class="search-form">
                <h3>Buscar Proprietários</h3>
                <form method="get">
                    <div class="form-group">
                        <input type="text" name="search" placeholder="Nome, CPF ou cidade..." class="form-control" value="{{ search }}">
                        <button type="submit" class="btn btn-primary">Buscar</button>
                    </div>
                </form>
            </div>
            
            {% if proprietarios %}
                <div class="proprietarios-grid">
                    {% for proprietario in proprietarios %}
                    <div class="proprietario-card">
                        <div class="proprietario-header">
                            <div class="proprietario-name">{{ proprietario.nome }}</div>
                            <div class="proprietario-cpf">CPF: {{ proprietario.cpf }}</div>
                        </div>
                        
                        <div class="proprietario-info">
                            {% if proprietario.telefone %}
                            <div class="info-item">
                                <span class="info-label">Telefone:</span>
                                <span class="info-value">{{ proprietario.telefone }}</span>
                            </div>
                            {% endif %}
                            
                            {% if proprietario.email %}
                            <div class="info-item">
                                <span class="info-label">Email:</span>
                                <span class="info-value">{{ proprietario.email }}</span>
                            </div>
                            {% endif %}
                            
                            {% if proprietario.cidade %}
                            <div class="info-item">
                                <span class="info-label">Cidade:</span>
                                <span class="info-value">{{ proprietario.cidade }}, {{ proprietario.estado }}</span>
                            </div>
                            {% endif %}
                            
                            <div class="info-item">
                                <span class="info-label">Propriedades:</span>
                                <span class="info-value">{{ proprietario.propriedades.count }}</span>
                            </div>
                        </div>
                        
                        <div class="proprietario-actions">
                            <a href="#" class="btn btn-primary btn-small">Ver Detalhes</a>
                            <a href="#" class="btn btn-success btn-small">Editar</a>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                
                {% if proprietarios.has_other_pages %}
                <div class="pagination">
                    {% if proprietarios.has_previous %}
                        <a href="?page={{ proprietarios.previous_page_number }}">Anterior</a>
                    {% endif %}
                    
                    <span class="current">Página {{ proprietarios.number }} de {{ proprietarios.paginator.num_pages }}</span>
                    
                    {% if proprietarios.has_next %}
                        <a href="?page={{ proprietarios.next_page_number }}">Próxima</a>
                    {% endif %}
                </div>
                {% endif %}
            {% else %}
                <div class="empty-state">
                    <h3>Nenhum proprietário encontrado</h3>
                    <p>Comece cadastrando seu primeiro proprietário</p>
                    <a href="{% url 'proprietario_novo' %}" class="btn btn-primary" style="margin-top: 1rem;">Cadastrar Primeiro Proprietário</a>
                </div>
            {% endif %}
        </div>
    </main>
</body>
</html>
"@ | Out-File -FilePath "templates/gestao_rural/proprietarios_lista.html" -Encoding UTF8

Write-Host "✅ proprietarios_lista.html criado!" -ForegroundColor Green

# 3. CRIAR TEMPLATE PROPRIETARIO_NOVO
Write-Host "📄 Criando proprietario_novo.html..." -ForegroundColor Cyan

@"
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Novo Proprietário - Monpec Projetista</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8f9fa;
            color: #333;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .header {
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 1rem 0;
            margin-bottom: 2rem;
        }
        
        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: 700;
            color: #004a99;
        }
        
        .nav-links {
            display: flex;
            gap: 2rem;
        }
        
        .nav-links a {
            color: #666;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
        }
        
        .nav-links a:hover {
            color: #004a99;
        }
        
        .user-menu {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .btn-logout {
            background: #dc3545;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            text-decoration: none;
            font-size: 0.9rem;
        }
        
        .page-header {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .page-header h1 {
            font-size: 2rem;
            font-weight: 700;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .page-header p {
            color: #666;
            font-size: 1.1rem;
        }
        
        .form-card {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #333;
        }
        
        .form-control {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #004a99;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
            font-size: 1rem;
        }
        
        .btn-primary {
            background: #004a99;
            color: white;
        }
        
        .btn-primary:hover {
            background: #003366;
            transform: translateY(-2px);
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
            transform: translateY(-2px);
        }
        
        .btn-group {
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
        }
        
        .alert {
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            font-weight: 500;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        @media (max-width: 768px) {
            .nav-links {
                display: none;
            }
            
            .form-row {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <nav class="nav">
                <div class="logo">Monpec Projetista</div>
                <div class="nav-links">
                    <a href="{% url 'dashboard' %}">Dashboard</a>
                    <a href="{% url 'proprietarios_lista' %}">Proprietários</a>
                    <a href="{% url 'propriedades_lista' %}">Propriedades</a>
                </div>
                <div class="user-menu">
                    <span>Olá, {{ user.username }}</span>
                    <a href="{% url 'logout' %}" class="btn-logout">Sair</a>
                </div>
            </nav>
        </div>
    </header>
    
    <main>
        <div class="container">
            <div class="page-header">
                <h1>Novo Proprietário</h1>
                <p>Cadastre um novo proprietário rural</p>
            </div>
            
            <div class="form-card">
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-{{ message.tags }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
                
                <form method="post">
                    {% csrf_token %}
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="nome">Nome Completo *</label>
                            <input type="text" id="nome" name="nome" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label for="cpf">CPF *</label>
                            <input type="text" id="cpf" name="cpf" class="form-control" required>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="telefone">Telefone</label>
                            <input type="text" id="telefone" name="telefone" class="form-control">
                        </div>
                        <div class="form-group">
                            <label for="email">E-mail</label>
                            <input type="email" id="email" name="email" class="form-control">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="endereco">Endereço</label>
                        <input type="text" id="endereco" name="endereco" class="form-control">
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="cidade">Cidade</label>
                            <input type="text" id="cidade" name="cidade" class="form-control">
                        </div>
                        <div class="form-group">
                            <label for="estado">Estado</label>
                            <select id="estado" name="estado" class="form-control">
                                <option value="">Selecione</option>
                                <option value="MS">Mato Grosso do Sul</option>
                                <option value="MT">Mato Grosso</option>
                                <option value="GO">Goiás</option>
                                <option value="SP">São Paulo</option>
                                <option value="PR">Paraná</option>
                                <option value="RS">Rio Grande do Sul</option>
                                <option value="SC">Santa Catarina</option>
                                <option value="MG">Minas Gerais</option>
                                <option value="BA">Bahia</option>
                                <option value="DF">Distrito Federal</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="observacoes">Observações</label>
                        <textarea id="observacoes" name="observacoes" class="form-control" rows="3"></textarea>
                    </div>
                    
                    <div class="btn-group">
                        <button type="submit" class="btn btn-primary">Salvar Proprietário</button>
                        <a href="{% url 'proprietarios_lista' %}" class="btn btn-secondary">Cancelar</a>
                    </div>
                </form>
            </div>
        </div>
    </main>
</body>
</html>
"@ | Out-File -FilePath "templates/gestao_rural/proprietario_novo.html" -Encoding UTF8

Write-Host "✅ proprietario_novo.html criado!" -ForegroundColor Green

# 4. CRIAR TEMPLATE PROPRIEDADES_LISTA
Write-Host "📄 Criando propriedades_lista.html..." -ForegroundColor Cyan

@"
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Propriedades - Monpec Projetista</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8f9fa;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .header {
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 1rem 0;
            margin-bottom: 2rem;
        }
        
        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: 700;
            color: #004a99;
        }
        
        .nav-links {
            display: flex;
            gap: 2rem;
        }
        
        .nav-links a {
            color: #666;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
        }
        
        .nav-links a:hover {
            color: #004a99;
        }
        
        .user-menu {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .btn-logout {
            background: #dc3545;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            text-decoration: none;
            font-size: 0.9rem;
        }
        
        .page-header {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .page-header h1 {
            font-size: 2rem;
            font-weight: 700;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .page-header p {
            color: #666;
            font-size: 1.1rem;
        }
        
        .actions {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .actions h2 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #333;
        }
        
        .btn-group {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
        }
        
        .btn-primary {
            background: #004a99;
            color: white;
        }
        
        .btn-primary:hover {
            background: #003366;
            transform: translateY(-2px);
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-success:hover {
            background: #218838;
            transform: translateY(-2px);
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
            transform: translateY(-2px);
        }
        
        .search-form {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .search-form h3 {
            margin-bottom: 1rem;
            color: #333;
        }
        
        .form-group {
            display: flex;
            gap: 1rem;
            align-items: end;
        }
        
        .form-control {
            padding: 0.75rem;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #004a99;
        }
        
        .propriedades-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 1.5rem;
        }
        
        .propriedade-card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 1.5rem;
            transition: transform 0.3s;
        }
        
        .propriedade-card:hover {
            transform: translateY(-5px);
        }
        
        .propriedade-header {
            border-bottom: 1px solid #e9ecef;
            padding-bottom: 1rem;
            margin-bottom: 1rem;
        }
        
        .propriedade-name {
            font-size: 1.25rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .propriedade-proprietario {
            color: #666;
            font-size: 0.9rem;
        }
        
        .propriedade-info {
            margin-bottom: 1rem;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
        }
        
        .info-label {
            color: #666;
            font-weight: 500;
        }
        
        .info-value {
            color: #333;
        }
        
        .propriedade-actions {
            display: flex;
            gap: 0.5rem;
        }
        
        .btn-small {
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
        }
        
        .empty-state {
            text-align: center;
            padding: 3rem;
            color: #666;
        }
        
        .empty-state h3 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #999;
        }
        
        .pagination {
            display: flex;
            justify-content: center;
            gap: 0.5rem;
            margin-top: 2rem;
        }
        
        .pagination a {
            padding: 0.5rem 1rem;
            background: white;
            color: #004a99;
            text-decoration: none;
            border-radius: 6px;
            border: 1px solid #e9ecef;
            transition: all 0.3s;
        }
        
        .pagination a:hover {
            background: #004a99;
            color: white;
        }
        
        .pagination .current {
            background: #004a99;
            color: white;
        }
        
        @media (max-width: 768px) {
            .nav-links {
                display: none;
            }
            
            .propriedades-grid {
                grid-template-columns: 1fr;
            }
            
            .form-group {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <nav class="nav">
                <div class="logo">Monpec Projetista</div>
                <div class="nav-links">
                    <a href="{% url 'dashboard' %}">Dashboard</a>
                    <a href="{% url 'proprietarios_lista' %}">Proprietários</a>
                    <a href="{% url 'propriedades_lista' %}">Propriedades</a>
                </div>
                <div class="user-menu">
                    <span>Olá, {{ user.username }}</span>
                    <a href="{% url 'logout' %}" class="btn-logout">Sair</a>
                </div>
            </nav>
        </div>
    </header>
    
    <main>
        <div class="container">
            <div class="page-header">
                <h1>Propriedades</h1>
                <p>Gerencie todas as propriedades rurais cadastradas</p>
            </div>
            
            <div class="actions">
                <h2>Ações</h2>
                <div class="btn-group">
                    <a href="{% url 'dashboard' %}" class="btn btn-secondary">Voltar ao Dashboard</a>
                    <a href="{% url 'proprietarios_lista' %}" class="btn btn-primary">Ver Proprietários</a>
                </div>
            </div>
            
            <div class="search-form">
                <h3>Buscar Propriedades</h3>
                <form method="get">
                    <div class="form-group">
                        <input type="text" name="search" placeholder="Nome da propriedade, proprietário ou município..." class="form-control" value="{{ search }}">
                        <button type="submit" class="btn btn-primary">Buscar</button>
                    </div>
                </form>
            </div>
            
            {% if propriedades %}
                <div class="propriedades-grid">
                    {% for propriedade in propriedades %}
                    <div class="propriedade-card">
                        <div class="propriedade-header">
                            <div class="propriedade-name">{{ propriedade.nome }}</div>
                            <div class="propriedade-proprietario">Proprietário: {{ propriedade.proprietario.nome }}</div>
                        </div>
                        
                        <div class="propriedade-info">
                            <div class="info-item">
                                <span class="info-label">Área:</span>
                                <span class="info-value">{{ propriedade.area }} hectares</span>
                            </div>
                            
                            <div class="info-item">
                                <span class="info-label">Município:</span>
                                <span class="info-value">{{ propriedade.municipio }}, {{ propriedade.estado }}</span>
                            </div>
                            
                            {% if propriedade.matricula %}
                            <div class="info-item">
                                <span class="info-label">Matrícula:</span>
                                <span class="info-value">{{ propriedade.matricula }}</span>
                            </div>
                            {% endif %}
                            
                            <div class="info-item">
                                <span class="info-label">Projetos:</span>
                                <span class="info-value">{{ propriedade.projetos.count }}</span>
                            </div>
                        </div>
                        
                        <div class="propriedade-actions">
                            <a href="{% url 'propriedade_modulos' propriedade.id %}" class="btn btn-primary btn-small">Ver Módulos</a>
                            <a href="#" class="btn btn-success btn-small">Editar</a>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                
                {% if propriedades.has_other_pages %}
                <div class="pagination">
                    {% if propriedades.has_previous %}
                        <a href="?page={{ propriedades.previous_page_number }}">Anterior</a>
                    {% endif %}
                    
                    <span class="current">Página {{ propriedades.number }} de {{ propriedades.paginator.num_pages }}</span>
                    
                    {% if propriedades.has_next %}
                        <a href="?page={{ propriedades.next_page_number }}">Próxima</a>
                    {% endif %}
                </div>
                {% endif %}
            {% else %}
                <div class="empty-state">
                    <h3>Nenhuma propriedade encontrada</h3>
                    <p>Comece cadastrando proprietários e suas propriedades</p>
                    <a href="{% url 'proprietario_novo' %}" class="btn btn-primary" style="margin-top: 1rem;">Cadastrar Primeiro Proprietário</a>
                </div>
            {% endif %}
        </div>
    </main>
</body>
</html>
"@ | Out-File -FilePath "templates/gestao_rural/propriedades_lista.html" -Encoding UTF8

Write-Host "✅ propriedades_lista.html criado!" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 TEMPLATES CRIADOS COM SUCESSO!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 TEMPLATES CRIADOS:" -ForegroundColor Cyan
Write-Host "✅ proprietarios_lista.html" -ForegroundColor Green
Write-Host "✅ proprietario_novo.html" -ForegroundColor Green
Write-Host "✅ propriedades_lista.html" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 AGORA O SISTEMA FUNCIONA COMPLETAMENTE!" -ForegroundColor Green
Write-Host "Acesse: http://127.0.0.1:8000" -ForegroundColor Yellow


