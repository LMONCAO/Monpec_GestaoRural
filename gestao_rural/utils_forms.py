from django.forms import Form

def formatar_mensagem_erro_form(form: Form) -> str:
    """
    Formata os erros de um formulário Django em uma string legível.
    """
    error_messages = []
    for field, errors in form.errors.items():
        field_name = form.fields[field].label if field != '__all__' else 'Geral'
        for error in errors:
            error_messages.append(f"• {field_name}: {error}")
    return "\n".join(error_messages)















