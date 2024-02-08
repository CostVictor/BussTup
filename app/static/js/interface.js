function ajust_interface(interface) {
    window.addEventListener('beforeunload', function () {
        this.setTimeout(() => {
            enterInterface(interface)
        }, 50)
    })
}


function createObserver(root = null, range_visibility = 0.2) {
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                entry.target.classList.remove('hidden')
            } else {
                entry.target.classList.remove('visible');
                entry.target.classList.add('hidden');
            }
        });
    }, {
        root: root,
        rootMargin: '0px',
        threshold: range_visibility
    });
    return observer
}


function set_observerScroll(list_obj) {
    for (let index = 0; index < list_obj.length; index++) {
        const observer = createObserver(list_obj[index], 0.15)
        let elements_animate = list_obj[index]
        elements_animate = elements_animate.querySelectorAll('div.hidden')
        elements_animate.forEach(element => {
            observer.observe(element)
        })
    }
}


function set_limitScroll(element_scroll, size_limit = 30) {
    const maxHeight = size_limit * window.innerHeight / 100
    const size_element = element_scroll.scrollHeight

    if (element_scroll.childElementCount) {
        if (size_element > maxHeight) {
            element_scroll.style.minHeight = `${maxHeight}px`
        } else {element_scroll.style.minHeight = `${size_element}px`}
    } else {element_scroll.style.minHeight = '0px'}
}


const inputs = document.querySelectorAll('input')
inputs.forEach(input => {
    const label = document.querySelector(`label[for="${input.id}"]`)
    const icon = document.getElementById(`icon_${input.id}`)
    let inFocus = false

    function verify() {
        if (inFocus) {
            input.classList.remove('input_error')
            if (label) {label.classList.add('selected')}
            if (icon) {icon.classList.add('selected')}
            if (input.type === 'time') { input.classList.add('visible') }
        } else {
            if (input.value.trim() === '') {
                input.value = ''
                if (label) {label.classList.remove('selected')}
                if (icon) {icon.classList.remove('selected')}
                if (input.type === 'time') { input.classList.remove('visible') }
            } else {
                if (label) {label.classList.add('selected')}
                if (icon) {icon.classList.add('selected')}
                if (input.type === 'time') { input.classList.add('visible') }
            }
        }
    }
    input.addEventListener('focus', function() {inFocus = true})
    input.addEventListener('blur', function() {inFocus = false})
    setInterval(verify, 100)
})


const forms = document.querySelectorAll('form')
forms.forEach(form => {
    form.addEventListener('keyup', function(event) {
        if (event.key === 'Enter') {submit(form.id)}
    });
})

set_observerScroll(document.querySelectorAll('form.scroll_vertical'))


function animateIconPassword(obj_click) {
    const container_password = obj_click.parentNode
    const iconPassword = container_password.querySelector('[id*="btn"]')
    const inputPassword = container_password.querySelector('input')

    if (inputPassword.type === 'password') {
        iconPassword.className = inputPassword.className.includes('white') ? "bi bi-eye-slash-fill form__btn--password white" : "bi bi-eye-slash-fill form__btn--password"
        inputPassword.type = 'text'
    } else {
        iconPassword.className = inputPassword.className.includes('white') ? "bi bi-eye-fill form__btn--password white" : "bi bi-eye-fill form__btn--password"
        inputPassword.type = 'password'
    }
}


function config_animate(index, item, name, duraction, value_initial, sum) {
    item.style.animation = `${name} ${duraction}s forwards ${value_initial + (index * sum)}s`
}


function animate_itens(list_itens, animate='fadeDown', duraction = 0.3, dalay_init = 0, interval_itens = 0.06, opacity = 0, exception = false) {
    if (list_itens) {
        list_execute = []
        list_itens.forEach(item => {
            if (exception) {
                if (!item.className.includes('inactive') || item.id.includes(exception)) {
                    list_execute.push(item)
                }
            } else {
                if (!item.className.includes('inactive')) {
                    list_execute.push(item)
                }
            }
        })

        list_execute.forEach((item, index) => {
            item.style.opacity = opacity
            config_animate(index, item, animate, duraction, dalay_init, interval_itens)
        })
    }
}


function enterInterface(type) {
    if (type === 'login') {
        const elements = document.querySelectorAll('[class*="enter"]')
        animate_itens(elements, 'fadeDown', 0.6, 0.55)

        const container = document.getElementById('container')
        container.style.transition = 'border-radius 0.5s ease, height 0.85s ease 0.15s'
        container.classList.remove('container_complete')
        container.classList.add('enter--radius')
        
    } else if (type === 'register') {
        const elements = document.querySelectorAll('[class*="enter"]')
        animate_itens(elements, 'fadeDown', 0.8, 0, 0.1)

    } else if (type === 'page_user') {
        enterPage()
    }
}


function closeInterface(type, redirect, time = 1000) {
    if (type === 'login') {
        const container = document.getElementById('container')
        container.style.transition = 'border-radius 0.5s ease 0.4s, height 0.7s ease'
        
        setTimeout(() => {
            container.classList.remove('enter--radius')
            container.classList.add('container_complete')
        }, 300)

    } else if (type === 'register') {
        const forms = document.querySelectorAll('form')
        forms.forEach(form => {
            form.classList.add('enter')
        })

    } else if (type === 'page_user') {
        closePage()
    }

    let elements = document.querySelectorAll('[class*="enter"]:not(#container)')
    animate_itens(elements, 'outUp', 0.4, 0, 0.07, 1)

    setTimeout(() => {
        ajust_interface(type)
        window.location.href = redirect
    }, time)
}


function enter_interface_line(obj_click) {
    const name_line = obj_click.querySelector('[id*="nome"]').textContent
    loadInterfaceLine(name_line)
    closePage()

    const interface = document.getElementById('interface_linha')
    const header_interface = document.getElementById('interface_linha_header')
    const content_interface = document.getElementById('interface_linha_content')
    const header_pag = document.getElementById('header_page')
    const content_page = document.getElementById('content_page')
    const nav_page = document.getElementById('nav_page')
    const abas = content_interface.querySelectorAll('[id*="btn"]')
    const containers = content_interface.querySelectorAll('[id*="container"]')
    const elements = Array.from(content_interface.children)

    abas.forEach(aba => {
        const icon = aba.querySelector('i')
        if (icon) {
            icon.classList.remove('open')
        }
        aba.classList.remove('margin_bottom')
    })
    containers.forEach(container => {
        container.classList.add('inactive')
    })

    setTimeout(() => {
        interface.classList.remove('inactive')
        header_pag.classList.add('inactive')
        content_page.classList.add('inactive')
        nav_page.classList.add('inactive')
        interface.scrollTop = 0
        
        config_animate(0, header_interface, 'fadeDown', 0.5, 0, 0.07)
        animate_itens(elements, 'fadeDown', 0.5, 0.07, 0.07, 0)
    }, 900)
}


function close_interface_line() {
    const interface = document.getElementById('interface_linha')
    const header_interface = document.getElementById('interface_linha_header')
    const content_interface = document.getElementById('interface_linha_content')
    const header_pag = document.getElementById('header_page')
    const content_page = document.getElementById('content_page')
    const nav_page = document.getElementById('nav_page')

    const children = Array.from(content_interface.children)
    const elements = children.filter(element => !element.className.includes('inactive'))

    header_pag.classList.remove('inactive')
    content_page.classList.remove('inactive')
    nav_page.classList.remove('inactive')
    
    animate_itens(elements, 'outUp', 0.7, 0.07, 0.07, 1)
    setTimeout(() => {
        config_animate(0, header_interface, 'outUp', 0.7, 0, 0.07)
    }, 350)
    
    setTimeout(() => {
        interface.classList.add('inactive')
        enterPage()
        copy_text()
    }, 650)
}


function replace_form(obj_button) {
    function reset_form(form) {
        form.querySelectorAll('input').forEach(input => {
            input.value = ''
        })
    }
    const buttons = document.querySelectorAll('button.form__btn--select')
    const form_aluno = document.getElementById('form_aluno')
    const form_motorista = document.getElementById('form_motorista')

    const elements_aluno = Array.from(form_aluno.children)
    const elements_motorista = Array.from(form_motorista.children)

    if (obj_button.textContent === 'Aluno' && !buttons[0].className.includes('selected')) {
        buttons[0].classList.add('selected')
        buttons[1].classList.remove('selected')
        form_aluno.classList.add('scroll_vertical')
        form_aluno.classList.remove('inactive')
        form_motorista.classList.add('inactive')
        form_motorista.classList.remove('scroll_vertical')

        reset_form(form_aluno)
        animate_itens(elements_aluno, 'fadeDown', 0.6, 0, 0.07)
        form_aluno.removeAttribute('style')
        form_aluno.classList.remove('enter')
        form_aluno.scrollTop = 0

    } else if (obj_button.textContent === 'Motorista' && !buttons[1].className.includes('selected')) {
        buttons[1].classList.add('selected')
        buttons[0].classList.remove('selected')
        form_motorista.classList.add('scroll_vertical')
        form_motorista.classList.remove('inactive')
        form_aluno.classList.add('inactive')
        form_aluno.classList.remove('scroll_vertical')

        reset_form(form_motorista)
        animate_itens(elements_motorista, 'fadeDown', 0.6, 0, 0.07)
        form_motorista.scrollTop = 0
    }
}
