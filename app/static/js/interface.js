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


function extract_info(obj_click, reference, local = 'id') {
    const verify = obj_click.querySelector(`[${local}*="${reference}"]`)
    if (verify) {return verify.textContent}

    let tag = obj_click.parentNode
    while (true) {
        var identify_nome = tag.querySelector(`[${local}*="${reference}"]`)
        if (identify_nome) {
            return identify_nome.textContent
        } else {
            tag = tag.parentNode
        }
    }
}


// ~~~~~ Animações de formulário ~~~~~ //

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


// ~~~~~ Animação de icone ~~~~~ //

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


// ~~~~~ Animação de interface ~~~~~ //

function config_animate(index, item, name, duraction, value_initial, sum) {
    item.style.animation = `${name} ${duraction}s forwards ${value_initial + (index * sum)}s`
}


function animate_itens(list_itens, animate='fadeDown', duraction = 0.3, dalay_init = 0, interval_itens = 0.06, opacity = 0) {
    if (list_itens) {
        list_itens.forEach((item, index) => {
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

    } else if (type === 'pag_usuario') {
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

    } else if (type === 'pag_usuario') {
        closePage()
    }

    let elements = document.querySelectorAll('[class*="enter"]:not(#container)')
    animate_itens(elements, 'outUp', 0.4, 0, 0.07, 1)

    setTimeout(() => {
        ajust_interface(type)
        window.location.href = redirect
    }, time)
}


function enterInterface_popup(obj_line) {
    loadInterfaceLinha(obj_line)
    closePage()

    const interface = document.getElementById('interface_linha')
    const header_interface = document.getElementById('interface_linha_header')
    const content_interface = document.getElementById('interface_linha_content')
    const header_pag = document.getElementById('header_page')
    const content_page = document.getElementById('content_page')
    const nav_page = document.getElementById('nav_page')
    const elements = Array.from(content_interface.children)
    const abas = content_interface.querySelectorAll('[id*="btn"]')
    const containers = content_interface.querySelectorAll('[id*="container"]')

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


function closeInterface_popup() {
    const interface = document.getElementById('interface_linha')
    const header_interface = document.getElementById('interface_linha_header')
    const content_interface = document.getElementById('interface_linha_content')
    const header_pag = document.getElementById('header_page')
    const content_page = document.getElementById('content_page')
    const nav_page = document.getElementById('nav_page')
    const elements = Array.from(content_interface.children)

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


function actionContainer(obj_click, container_space = false, set_limit = false) {
    const icon = obj_click.querySelector('i')
    const container = document.getElementById(obj_click.id.replace('btn', 'container'))
    const elements = Array.from(container.children)
    obj_click.style.transition = '0s ease'
    container.removeAttribute('style')

    if (obj_click.id.includes('onibus')) {
        const motorista_nome = obj_click.querySelectorAll('h3')
        motorista_nome.forEach((element, index) => {
            if (!index) {
                icon.className.includes('open') ? element.classList.remove('max_width') : element.classList.add('max_width')
            } else {
                icon.className.includes('open') ? element.classList.remove('inactive') : element.classList.add('inactive')
            }
        })
    }

    animate_itens(elements)
    if (icon.className.includes('open')) {
        container.classList.remove('space')
        container.classList.add('inactive')
        icon.classList.remove('open')
        obj_click.classList.remove('margin_bottom')

        elements.forEach(element => {
            element.classList.remove('selected')
        })
    } else {
        container.classList.remove('inactive')
        if (!container_space) {
            if (container.className.includes('scroll')) {
                container.classList.add('space')
            } else {
                obj_click.classList.add('margin_bottom')
            }
        } else { container.classList.add('space') }
        container.scrollTop = 0
        icon.classList.add('open')

        if (set_limit) {
            set_limitScroll(container, set_limit)
        } else {
            set_limitScroll(container)
        }
    }

    const btn_children = container.querySelectorAll('[id*="btn"]')
    if (btn_children) {
        btn_children.forEach(btn => {
            const icon = btn.querySelector('i')
            if (icon.className.includes('open')) {
                actionContainer(btn)
            }
        })
    }

    const rolament = container.querySelector('div.scroll_vertical')
    if (rolament) { rolament.scrollTop = 0 }

    elements.forEach(element => {
        if (element.className.includes('scroll')) {
            set_limitScroll(element)
        }
    })
}


// ~~~~~ Troca de formulário ~~~~~ //

function replace_form(obj_button) {
    function reset_form(form) {
        form.querySelectorAll('input').forEach(input => {
            input.value = ''
        })
    }
    const buttons = document.querySelectorAll('button.form__btn--select')
    const form_aluno = document.getElementById('form_aluno')
    const form_motorista = document.getElementById('form_motorista')

    elements_aluno = form_aluno.querySelectorAll('div')
    elements_motorista = form_motorista.querySelectorAll('div')

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


// ~~~~~ Ação de icone ~~~~~ //

function copy_text(obj_click = null) {
    const icons = document.querySelectorAll('[class*="copy"]')
    
    icons.forEach(icon => {
        if (icon === obj_click) {
            icon.classList.replace('bi-clipboard', 'bi-check-lg')
            const div_pai = icon.parentNode
            const element_text = div_pai.querySelector('p.content')
            navigator.clipboard.writeText(element_text.innerText)
        } else {
            icon.classList.replace('bi-check-lg', 'bi-clipboard')
        }
    })
}
