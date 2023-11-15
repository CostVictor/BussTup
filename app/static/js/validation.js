// ~~~~~ POPUP ~~~~~ //

function create_popup(title, text='', text_buttom='Ok', icon='info', redirect='') {
    document.body.classList.add('no-scroll')
    Swal.fire({
        title: title,
        text: text,
        icon: icon,
        width: '80%',
        confirmButtonText: text_buttom
    }).then(() => {
        document.body.classList.remove('no-scroll')
        if (redirect) {window.location.href = redirect}
    })
}

// ~~~~~ Validação de login ~~~~~ //

function validationLogin(event) {
    event.preventDefault()

    const form = document.getElementById('formulario_login')
    let usuario = form.elements.usuario_login.value
    let senha = form.elements.senha_login.value

    fetch('/autenticar_usuario', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'user': usuario, 'password': senha})
    })
    .then(response => response.json())
    .then(response => {
        if (response['error']) {
            create_popup('Não foi possível fazer login', 'Verifique suas credenciais e tente novamente.', 'Ok', 'info')
        } else {window.location.href = response['redirect']}
    })
}

function validationRegister(type, event) {
    event.preventDefault()
    function apenas_numeros(str) {return /^[0-9]+$/.test(str)}
    function apenas_letras(str) {return /^[a-zA-ZÀ-ÖØ-öø-ÿ\s]*$/.test(str)}
    function sem_espaco(str) {return str.indexOf(' ') === -1}

    const form = document.getElementById(`form_register_${type}`)
    let execute = true
    let data = {}

    for (let index = 0; index < form.elements.length; index++) {
        var campo = form.elements[index]
        const campoAlvo = campo.name.charAt(0).toUpperCase() + campo.name.slice(1)
        
        if (campo.name) {
            if (campoAlvo === 'Matricula' || campoAlvo === 'Telefone') {
                if (!apenas_numeros(campo.value)) {
                    if (campoAlvo === 'Matricula') {
                        var erro_titulo = 'Matrícula inválida'
                        var erro_texto = 'O campo matrícula deve conter apenas números.'
                    } else {
                        var erro_titulo = 'Telefone inválido'
                        var erro_texto = 'O campo telefone deve conter apenas números.'
                    }
                    execute = false; break
                }
            } else if (campoAlvo === 'Nome' || campoAlvo === 'Curso' || campoAlvo === 'Turno') {
                if (!apenas_letras(campo.value)) {
                    var erro_titulo = `${campoAlvo} inválido`
                    var erro_texto = `O campo ${campo.name} deve conter apenas letras.`
                    execute = false; break
                }
            } else if (campoAlvo === 'Senha') {
                if (!sem_espaco(campo.value)) {
                    var erro_titulo = 'Formato de senha inválido'
                    var erro_texto = 'A senha não deve conter espaços.'
                    execute = false; break
                }
            }

            if (campoAlvo === 'Conf_senha') {
                if (campo.value !== data['senha']) {
                    var erro_titulo = 'Senha inconsistente'
                    var erro_texto = 'A senha especificada na confirmação é diferente da senha definida.'
                    execute = false; break
                }
            } else {data[campo.name] = campo.value}
        }
    }

    if (execute) {
        fetch('/cadastrar_usuario', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'table': type, 'data': data})
        })
        .then(response => response.json())
        .then(retorno => {
            let text = ''; let icon = 'success'
            let text_buttom = 'Logar'; let redirect = '/'

            if (retorno['error']) {
                text = retorno['teste']
                icon = 'info'
                text_buttom = 'Voltar'
                redirect = false
            }
            create_popup(retorno['title'], text, text_buttom, icon, redirect)
        })
    } else {
        campo.classList.add('form__box_input--error')
        create_popup(erro_titulo, erro_texto, 'Voltar', 'error')
    }
}
