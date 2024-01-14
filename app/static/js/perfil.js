function enterProfile() {
    loadPerfil()
    const perfil = document.querySelector('section.perfil__container')
    const header = perfil.querySelector('header')
    header.classList.remove('enter')

    const elements = document.querySelectorAll('[class*="enter"]')
    config_animate(0, header, 'fadeDown', 0.5, 0, 0.06)
    animate_itens(elements, 'fadeDown', 0.5, 0.2)
}


function closeProfile(logout = false) {
    const perfil = document.querySelector('section.perfil__container')
    const header = perfil.querySelector('header')
    header.classList.add('enter')

    const elements = document.querySelectorAll('[class*="enter"]')
    animate_itens(elements, 'outUp', 0.5, 0, 0.03, 1)

    if (logout) {
        cancel_popup_edit('confirm_logout')
        fetch('/logout', {method: 'GET'})
        setTimeout(() => {
            history.pushState(null, null, '/'); 
            window.location.href = '/'
        }, 1000)
    } else {
        setTimeout(() => {
            window.location.href = "/page_user"
        }, 700)
    }
    setTimeout(() => {enterProfile()}, 1100)
}


function loadPerfil() {
    fetch('/get_profile', {method: 'GET'})
    .then(response => response.json())
    .then(response => {
        for (let key in response) {
            const info = document.getElementById(`perfil_${key}`)
            info.textContent = response[key]
        }
    })
}


function editData_perfil(obj_click) {
    let execute = true
    const key = obj_click.id.replace('formulario_', '')
    let data = obj_click.id.split('_')
    data = data[data.length - 1]

    const input_newValue = document.getElementById(key + '_new')
    const input_password_conf = document.getElementById(key + '_conf')

    switch (data) {
        case 'email':
            if (!validationEmail(input_newValue.value.trim())) {
                execute = false
                var erro_titulo = 'Email inválido'
                var erro_texto = 'O email especificado não é válido.'
            }
            break

        case 'telefone':
            if (!validationTelefone(input_newValue.value.trim())) {
                execute = false
                var erro_titulo = 'Telefone inválido'
                var erro_texto = 'O campo telefone deve conter apenas números.'
            }
            break
    }

    if (execute) {
        fetch("/edit_profile", {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'field': data, 'new_value': input_newValue.value.trim(), 'password': input_password_conf.value.trim()})
        })
        .then(response => response.json())
        .then(response => {
            if (!response['error']) {
                cancel_popup_edit(key)
                create_popup(response['title'], response['text'], 'Ok', 'success')
                loadPerfil()
            } else {
                if (response['title'].includes('Telefone')) {
                    input_newValue.classList.add('input_error')
                } else {
                    input_password_conf.classList.add('input_error')
                }
                create_popup(response['title'], response['text'], 'Voltar', 'error', '', false)
            }
        })
    } else {
        input_newValue.classList.add('input_error')
        create_popup(erro_titulo, erro_texto, 'Voltar', 'error', '', false)
    }
}
