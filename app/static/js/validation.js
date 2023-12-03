// ~~~~~ POPUP ~~~~~ //

function create_popup(title, text='', text_buttom='Ok', icon='info', redirect='') {
    document.body.classList.add('no-scroll')
    Swal.fire({
        title: title,
        text: text,
        icon: icon,
        width: '80%',
        confirmButtonText: text_buttom,
        confirmButtonColor: '#004aad',
        iconColor: `${icon === 'info'? "#ffe959" : icon === 'success'? "#0aa999" : "#ff7272"}`
    }).then(() => {
        document.body.classList.remove('no-scroll')
        if (redirect) {window.location.href = redirect}
    })
}

function create_popup_edit(type) {
    if (type === 'ponto') {
        Swal.fire({
            title: 'teste',
            customClass: {
                title: 'form__text_title'
            }
        })
    }
}


// ~~~~~ Validação de login ~~~~~ //

function validationLogin(event) {
    event.preventDefault()

    const form = document.getElementById('formulario_login')
    let usuario = form.elements.user.value
    let senha = form.elements.password.value

    fetch('/autenticar_usuario', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'user': usuario, 'password': senha})
    })
    .then(response => response.json())
    .then(response => {
        if (response['error']) {
            create_popup('Não foi possível fazer login', 'Verifique suas credenciais e tente novamente.', 'Ok', 'info')
        } else {closeInterface('login', response['redirect'])}
    })
}

function validationRegister(type, event) {
    event.preventDefault()
    function apenas_numeros(str) {return /^[0-9]+$/.test(str)}
    function apenas_letras(str) {return /^[a-zA-ZÀ-ÖØ-öø-ÿ\s]*$/.test(str)}
    function sem_espaco(str) {return str.indexOf(' ') === -1}

    const form = document.getElementById(`form_${type}`)
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
                if (!apenas_letras(campo.value.trim())) {
                    var erro_titulo = `${campoAlvo} inválido`
                    var erro_texto = `O campo ${campo.name} deve conter apenas letras.`
                    execute = false; break
                }
            } else if (campoAlvo === 'Email') {
                if (!campo.value.trim().includes('@')) {
                    var erro_titulo = 'Email inválido'
                    var erro_texto = 'O email especificado não é válido.'
                    execute = false; break
                }
            } else if (campoAlvo === 'Senha') {
                if (!sem_espaco(campo.value.trim())) {
                    var erro_titulo = 'Formato de senha inválido'
                    var erro_texto = 'A senha não deve conter espaços.'
                    execute = false; break
                }
            }

            if (campoAlvo === 'Conf_senha') {
                if (campo.value.trim() !== data['senha']) {
                    var erro_titulo = 'Senha inconsistente'
                    var erro_texto = 'A senha especificada na confirmação é diferente da senha definida.'
                    execute = false; break
                }
            } else {data[campo.name] = campo.value.trim()}
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
                icon = 'info'
                text = `Já existe um usuário cadastrado ${type === "aluno" ? "na matrícula especificada." : "no nome especificado."}`
                text_buttom = 'Voltar'
                redirect = false
            }
            create_popup(retorno['title'], text, text_buttom, icon, redirect)
        })
    } else {
        campo.classList.add('input_error')
        create_popup(erro_titulo, erro_texto, 'Voltar', 'error')
    }
}

function submit() {
    const buttom = document.querySelector('button.form__btn--select_active')
    const form = document.getElementById(`form_${buttom.textContent.toLowerCase()}`)
    if (form.checkValidity()) {
        form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
    } else {form.reportValidity()}
}
