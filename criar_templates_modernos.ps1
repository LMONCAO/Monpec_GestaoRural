# ========================================
# CRIAR TEMPLATES MODERNOS - AUTOMÁTICO
# ========================================

Write-Host "🎨 CRIANDO TEMPLATES MODERNOS AUTOMATICAMENTE" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Yellow

Set-Location "monpec_local"

# 1. TEMPLATE BASE
Write-Host "📄 Criando template base..." -ForegroundColor Cyan

@"
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Monpec Projetista{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --primary-color: #004a99;
            --primary-hover: #003366;
            --secondary-color: #28a745;
            --success-color: #28a745;
            --warning-color: #ffc107;
            --danger-color: #dc3545;
            --light-color: #f8f9fa;
            --dark-color: #343a40;
            --border-radius: 8px;
            --box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .navbar {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
            box-shadow: var(--box-shadow);
            padding: 1rem 0;
        }
        
        .navbar-brand {
            font-weight: 700;
            font-size: 1.5rem;
            color: white !important;
        }
        
        .navbar-nav .nav-link {
            color: rgba(255,255,255,0.9) !important;
            font-weight: 500;
            margin: 0 0.5rem;
            transition: all 0.3s ease;
        }
        
        .navbar-nav .nav-link:hover {
            color: white !important;
            transform: translateY(-2px);
        }
        
        .card {
            border: none;
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            transition: all 0.3s ease;
            background: white;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }
        
        .card-header {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
            color: white;
            border-radius: var(--border-radius) var(--border-radius) 0 0 !important;
            font-weight: 600;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
            border: none;
            border-radius: var(--border-radius);
            font-weight: 500;
            padding: 0.75rem 1.5rem;
            transition: all 0.3s ease;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,74,153,0.3);
        }
        
        .btn-success {
            background: linear-gradient(135deg, var(--success-color) 0%, #218838 100%);
            border: none;
            border-radius: var(--border-radius);
            font-weight: 500;
            padding: 0.75rem 1.5rem;
            transition: all 0.3s ease;
        }
        
        .btn-success:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(40,167,69,0.3);
        }
        
        .stats-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: var(--border-radius);
            padding: 2rem;
            text-align: center;
            margin-bottom: 1.5rem;
        }
        
        .stats-card h3 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .stats-card p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .table {
            background: white;
            border-radius: var(--border-radius);
            overflow: hidden;
            box-shadow: var(--box-shadow);
        }
        
        .table thead th {
            background: var(--primary-color);
            color: white;
            border: none;
            font-weight: 600;
            padding: 1rem;
        }
        
        .table tbody td {
            padding: 1rem;
            border-color: #f1f3f4;
        }
        
        .table tbody tr:hover {
            background: #f8f9fa;
        }
        
        .form-control {
            border-radius: var(--border-radius);
            border: 2px solid #e9ecef;
            padding: 0.75rem 1rem;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .form-control:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 0.2rem rgba(0,74,153,0.25);
        }
        
        .alert {
            border-radius: var(--border-radius);
            border: none;
            font-weight: 500;
        }
        
        .sidebar {
            background: white;
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            padding: 1.5rem;
            height: fit-content;
        }
        
        .sidebar .nav-link {
            color: #666;
            font-weight: 500;
            padding: 0.75rem 1rem;
            border-radius: var(--border-radius);
            margin-bottom: 0.5rem;
            transition: all 0.3s ease;
        }
        
        .sidebar .nav-link:hover,
        .sidebar .nav-link.active {
            background: var(--primary-color);
            color: white;
        }
        
        .main-content {
            background: white;
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            padding: 2rem;
        }
        
        .page-header {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
            color: white;
            padding: 2rem;
            border-radius: var(--border-radius);
            margin-bottom: 2rem;
        }
        
        .page-header h1 {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .page-header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .module-card {
            background: white;
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            padding: 2rem;
            text-align: center;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }
        
        .module-card:hover {
            transform: translateY(-5px);
            border-color: var(--primary-color);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }
        
        .module-icon {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1.5rem;
            font-size: 2rem;
            color: white;
        }
        
        .module-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--primary-color);
        }
        
        .module-description {
            color: #666;
            margin-bottom: 1.5rem;
            line-height: 1.6;
        }
        
        .footer {
            background: var(--dark-color);
            color: white;
            padding: 2rem 0;
            margin-top: 3rem;
        }
        
        @media (max-width: 768px) {
            .stats-card h3 {
                font-size: 2rem;
            }
            
            .page-header h1 {
                font-size: 1.5rem;
            }
            
            .module-card {
                margin-bottom: 1rem;
            }
        }
    </style>
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% if user.is_authenticated %}
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg">
        <div class="container">
            <a class="navbar-brand" href="{% url 'dashboard' %}">
                <i class="fas fa-seedling me-2"></i>Monpec Projetista
            </a>
            
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'dashboard' %}">
                            <i class="fas fa-tachometer-alt me-1"></i>Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'proprietarios_lista' %}">
                            <i class="fas fa-users me-1"></i>Proprietários
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'propriedades_lista' %}">
                            <i class="fas fa-home me-1"></i>Propriedades
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'projetos_lista' %}">
                            <i class="fas fa-project-diagram me-1"></i>Projetos
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'relatorios_dashboard' %}">
                            <i class="fas fa-chart-bar me-1"></i>Relatórios
                        </a>
                    </li>
                </ul>
                
                <ul class="navbar-nav">
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-user me-1"></i>{{ user.username }}
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{% url 'logout' %}">
                                <i class="fas fa-sign-out-alt me-1"></i>Sair
                            </a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    {% endif %}
    
    <!-- Messages -->
    {% if messages %}
        <div class="container mt-3">
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        </div>
    {% endif %}
    
    <!-- Main Content -->
    <div class="container-fluid">
        {% block content %}{% endblock %}
    </div>
    
    <!-- Footer -->
    {% if user.is_authenticated %}
    <footer class="footer">
        <div class="container text-center">
            <p>&copy; 2024 Monpec Projetista. Todos os direitos reservados.</p>
        </div>
    </footer>
    {% endif %}
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
"@ | Out-File -FilePath "templates/gestao_rural/base.html" -Encoding UTF8

Write-Host "✅ Template base criado!" -ForegroundColor Green

# 2. LANDING PAGE
Write-Host "🏠 Criando landing page..." -ForegroundColor Cyan

@"
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monpec Projetista - Automatize seus Projetos de Crédito Rural</title>
    
    <style>
        :root {
            --primary-color: #004a99;
            --primary-hover: #003366;
            --secondary-color: #28a745;
            --success-color: #28a745;
            --warning-color: #ffc107;
            --danger-color: #dc3545;
            --light-color: #f8f9fa;
            --dark-color: #343a40;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        
        .hero {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
            color: white;
            padding: 100px 0;
            text-align: center;
        }
        
        .hero h1 {
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            line-height: 1.2;
        }
        
        .hero p {
            font-size: 1.3rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }
        
        .btn-hero {
            background: var(--secondary-color);
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            text-decoration: none;
            font-size: 1.2rem;
            font-weight: 600;
            display: inline-block;
            transition: all 0.3s ease;
            border: none;
        }
        
        .btn-hero:hover {
            background: #218838;
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(40,167,69,0.3);
            color: white;
        }
        
        .features {
            padding: 80px 0;
            background: white;
        }
        
        .feature-card {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
            transition: all 0.3s ease;
            margin-bottom: 2rem;
        }
        
        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }
        
        .feature-icon {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1.5rem;
            font-size: 2rem;
            color: white;
        }
        
        .feature-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--primary-color);
        }
        
        .feature-description {
            color: #666;
            line-height: 1.6;
        }
        
        .cta-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 80px 0;
            text-align: center;
        }
        
        .cta-section h2 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }
        
        .cta-section p {
            font-size: 1.2rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }
        
        .navbar {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            padding: 1rem 0;
        }
        
        .navbar-brand {
            font-weight: 700;
            font-size: 1.5rem;
            color: var(--primary-color) !important;
        }
        
        .nav-link {
            color: #666 !important;
            font-weight: 500;
            margin: 0 1rem;
            transition: all 0.3s ease;
        }
        
        .nav-link:hover {
            color: var(--primary-color) !important;
        }
        
        .btn-login {
            background: var(--primary-color);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .btn-login:hover {
            background: var(--primary-hover);
            transform: translateY(-2px);
            color: white;
        }
        
        .footer {
            background: var(--dark-color);
            color: white;
            padding: 2rem 0;
            text-align: center;
        }
        
        @media (max-width: 768px) {
            .hero h1 {
                font-size: 2.5rem;
            }
            
            .hero p {
                font-size: 1.1rem;
            }
            
            .cta-section h2 {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg fixed-top">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="fas fa-seedling"></i> Monpec Projetista
            </a>
            
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="#features">Funcionalidades</a>
                <a class="nav-link" href="#pricing">Preços</a>
                <a class="nav-link" href="#contact">Contato</a>
                <a class="btn btn-login" href="{% url 'login' %}">Acessar Sistema</a>
            </div>
        </div>
    </nav>
    
    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <h1>Diga adeus à burocracia. Olá, automação.</h1>
            <p>O Monpec Projetista é o sistema definitivo para projetistas de crédito rural que buscam organizar documentos e automatizar processos repetitivos.</p>
            <a href="{% url 'login' %}" class="btn-hero">Comece sua avaliação gratuita</a>
        </div>
    </section>
    
    <!-- Features Section -->
    <section class="features" id="features">
        <div class="container">
            <div class="row">
                <div class="col-md-4">
                    <div class="feature-card">
                        <div class="feature-icon">
                            <i class="fas fa-file-alt"></i>
                        </div>
                        <h3 class="feature-title">Gestão Documental Inteligente</h3>
                        <p class="feature-description">
                            Chega de pastas perdidas. Crie checklists de documentos personalizados por linha de crédito e anexe tudo na nuvem.
                        </p>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="feature-card">
                        <div class="feature-icon">
                            <i class="fas fa-robot"></i>
                        </div>
                        <h3 class="feature-title">Automação de Processos</h3>
                        <p class="feature-description">
                            Gere laudos, orçamentos e planilhas técnicas com um clique. O Monpec preenche automaticamente os dados.
                        </p>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="feature-card">
                        <div class="feature-icon">
                            <i class="fas fa-chart-kanban"></i>
                        </div>
                        <h3 class="feature-title">Fluxo de Trabalho Visual</h3>
                        <p class="feature-description">
                            Acompanhe o status de cada projeto de forma visual. Mova os cartões e tenha clareza imediata.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- CTA Section -->
    <section class="cta-section" id="pricing">
        <div class="container">
            <h2>Pronto para eliminar o retrabalho?</h2>
            <p>Descubra como o Monpec Projetista pode economizar horas do seu dia.</p>
            <a href="{% url 'login' %}" class="btn-hero">Solicite uma Demonstração Gratuita</a>
        </div>
    </section>
    
    <!-- Footer -->
    <footer class="footer" id="contact">
        <div class="container">
            <h3>Entre em contato</h3>
            <p>Tem alguma dúvida? Envie um email para</p>
            <p style="font-size: 1.2rem; font-weight: 600; color: var(--secondary-color);">contato@monpec.com.br</p>
            <p>&copy; 2024 Monpec Projetista. Todos os direitos reservados.</p>
        </div>
    </footer>
    
    <!-- Font Awesome -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"></script>
</body>
</html>
"@ | Out-File -FilePath "templates/gestao_rural/landing.html" -Encoding UTF8

Write-Host "✅ Landing page criada!" -ForegroundColor Green

# 3. LOGIN PAGE
Write-Host "🔐 Criando página de login..." -ForegroundColor Cyan

@"
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Monpec Projetista</title>
    
    <style>
        :root {
            --primary-color: #004a99;
            --primary-hover: #003366;
            --secondary-color: #28a745;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .login-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 3rem;
            width: 100%;
            max-width: 400px;
            text-align: center;
        }
        
        .login-header h1 {
            color: var(--primary-color);
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .login-header p {
            color: #666;
            font-size: 1rem;
            margin-bottom: 2rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
            text-align: left;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #333;
        }
        
        .form-control {
            width: 100%;
            padding: 1rem;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .form-control:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 0.2rem rgba(0,74,153,0.25);
        }
        
        .btn-login {
            width: 100%;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 1rem;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0,74,153,0.3);
        }
        
        .login-footer {
            margin-top: 2rem;
            color: #666;
        }
        
        .login-footer a {
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 600;
        }
        
        .login-footer a:hover {
            text-decoration: underline;
        }
        
        .back-link {
            position: absolute;
            top: 2rem;
            left: 2rem;
            color: white;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .back-link:hover {
            color: rgba(255,255,255,0.8);
        }
    </style>
</head>
<body>
    <a href="{% url 'landing_page' %}" class="back-link">
        <i class="fas fa-arrow-left"></i> Voltar ao início
    </a>
    
    <div class="login-container">
        <div class="login-header">
            <h1><i class="fas fa-seedling"></i> Monpec Projetista</h1>
            <p>Faça login para acessar o sistema</p>
        </div>
        
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }}" style="background: #f8d7da; color: #721c24; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    {{ message }}
                </div>
            {% endfor %}
        {% endif %}
        
        <form method="post">
            {% csrf_token %}
            <div class="form-group">
                <label for="username">Usuário</label>
                <input type="text" id="username" name="username" class="form-control" required>
            </div>
            
            <div class="form-group">
                <label for="password">Senha</label>
                <input type="password" id="password" name="password" class="form-control" required>
            </div>
            
            <button type="submit" class="btn-login">
                <i class="fas fa-sign-in-alt"></i> Entrar
            </button>
        </form>
        
        <div class="login-footer">
            <p>Não tem conta? <a href="#">Contate o administrador</a></p>
        </div>
    </div>
    
    <!-- Font Awesome -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"></script>
</body>
</html>
"@ | Out-File -FilePath "templates/gestao_rural/login.html" -Encoding UTF8

Write-Host "✅ Página de login criada!" -ForegroundColor Green

Write-Host "🎉 TEMPLATES MODERNOS CRIADOS!" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. python manage.py makemigrations" -ForegroundColor White
Write-Host "2. python manage.py migrate" -ForegroundColor White
Write-Host "3. python manage.py createsuperuser" -ForegroundColor White
Write-Host "4. python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Acesse: http://127.0.0.1:8000" -ForegroundColor Green


