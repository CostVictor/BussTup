function enterProfile() {
    loadProfile()
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
        close_popup('confirm_logout')
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


function loadProfile() {
    fetch('/get_profile', {method: 'GET'})
    .then(response => response.json())
    .then(response => {
        for (let key in response) {
            const info = document.getElementById(`perfil_${key}`)
            info.textContent = response[key]
        }
    })
}


function editData_profile(obj_click) {
    execute = true
    const key = obj_click.id.replace('formulario_', '')
    let data = obj_click.id.split('_')
    data = data[data.length - 1]

    const input_new_value = document.getElementById(key + '_new')
    const new_value = input_new_value.value.trim()
    const input_password_conf = document.getElementById(key + '_conf')
    const password_conf = input_password_conf.value.trim()

    if (data == 'telefone') {
        if (new_value.length !== 15) {
            execute = false
            input_new_value.setCustomValidity('Digite o telefone completo.')
            input_new_value.reportValidity()
        }
    }

    if (execute) {
        fetch("/edit_profile", {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'field': data, 'new_value': new_value, 'password': password_conf})
        })
        .then(response => response.json())
        .then(response => {
            if (!response['error']) {
                close_popup(key)
                create_popup(response['title'], response['text'], 'Ok', 'success')
                loadProfile()
            } else {
                if (response['title'].includes('Senha')) {
                    input_password_conf.classList.add('input_error')
                } else {input_new_value.classList.add('input_error')}
                create_popup(response['title'], response['text'], 'Voltar', 'info', '', false)
            }
        })
    }
}
