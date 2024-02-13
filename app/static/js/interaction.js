const list_inputs = document.querySelectorAll('input')
function set_animate_label(list_inputs, local = false) {
    list_inputs.forEach(input => {
        let label = document.querySelector(`label[for="${input.id}"]`)
        let icon = document.getElementById(`icon_${input.id}`)

        if (local) {
            label = local.querySelector(`label[for="${input.id}"]`)
            icon = local.querySelector((`#icon_${input.id}`))
        }
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
}
set_animate_label(list_inputs)


const inputs_tell = document.querySelectorAll('[class*="format_tell"]')
function set_valid_tell(inputs_tell) {
    inputs_tell.forEach(input => {
        input.addEventListener('input', () => {
            let digits = input.value.replace(/\D/g, '').substring(0, 11)
            let num = digits.split('')
            
            let tell_formated = ''
            if (num.length > 0) {tell_formated += `${num.slice(0, 2).join('')}`}
            if (num.length > 2) {tell_formated = `(${tell_formated}) ${num.slice(2, 7).join('')}`}
            if (num.length > 7) {tell_formated += `-${num.slice(7).join('')}`}
            input.value = tell_formated
        })
    })
}
set_valid_tell(inputs_tell)


const inputs_name = document.querySelectorAll('[class*="format_name"]')
function set_valid_name(inputs_name) {
    inputs_name.forEach(input => {
        input.addEventListener('input', () => {
            input.value = input.value.replace(/[^a-zA-ZàáâãçéêíîóôõúüÀÁÂÃÇÉÊÍÎÓÔÕÚÜ\s]/g, '')
        })
    })
}
set_valid_name(inputs_name)


const inputs_options = document.querySelectorAll('[class*="format_options"]')
function set_input_options(inputs_options) {
    function ajust_text(list, input) {
        const value = input.value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
        list.forEach(element => {
            const text = element.textContent.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
            element.classList.toggle('inactive', !text.includes(value));
        })
    }

    inputs_options.forEach(input => {
        const list_options = input.parentNode.parentNode.querySelector('ul')
        const elements = list_options.querySelectorAll('li')
        animate_itens(elements)

        elements.forEach(li => {
            li.addEventListener('mouseenter', () => {
                input.value = li.textContent
            })
        })

        input.addEventListener('input', () => {
            ajust_text(elements, input)
        })

        input.addEventListener('focus', () => {
            input.classList.add('option_focus')
            list_options.classList.remove('inactive')
            list_options.scrollTop = 0
            ajust_text(elements, input)
        })

        input.addEventListener('blur', () => {
            input.classList.remove('option_focus')
            list_options.classList.add('inactive')

            elements.forEach(element => {
                element.classList.remove('inactive')
            })
        })
    })
}
set_input_options(inputs_options)


const forms = document.querySelectorAll('form')
function set_submit_form(forms) {
    forms.forEach(form => {
        form.addEventListener('keyup', function(event) {
            if (event.key === 'Enter') {submit(form.id)}
        });
    })
}
set_submit_form(forms)
set_observerScroll(document.querySelectorAll('form.scroll_vertical'))


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


function create_popup(title, text='', text_buttom='Ok', icon='info', redirect='', open_scroll = true) {
    document.body.classList.add('no-scroll')
    Swal.fire({
        title: title,
        html: `<p${text.split(' ').length > 12 ? ' style="text-align: justify;"' : ''}>${text}</p>`,
        icon: icon,
        width: '80%',
        confirmButtonText: text_buttom,
        confirmButtonColor: '#004aad',
        iconColor: `${icon === 'info' ? "#ffe646" : icon === 'success'? "#0aa999" : "#ff7272"}`
    }).then(() => {
        if (open_scroll) {document.body.classList.remove('no-scroll')}
        if (redirect) {window.location.href = '/' + redirect}
    })
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


function action_container(obj_click, set_limit = false) {
    const icon = obj_click.querySelector('i')
    const container = document.getElementById(obj_click.id.replace('btn', 'container'))
    const elements = Array.from(container.children)
    obj_click.style.transition = '0s ease'
    container.removeAttribute('style')

    if (obj_click.id.includes('veiculo')) {
        const motorista_nome = obj_click.querySelectorAll('h3')
        motorista_nome.forEach((element, index) => {
            if (!index) {
                if (icon.className.includes('open')) {
                    element.classList.remove('max_width')
                } else {element.classList.add('max_width')}
            } else {
                if (icon.className.includes('open')) {
                    element.classList.remove('inactive')
                } else {element.classList.add('inactive')}
            }
        })
    }

    animate_itens(elements)
    if (icon.className.includes('open')) {
        container.classList.add('inactive')
        icon.classList.remove('open')

        elements.forEach(element => {
            element.classList.remove('selected')
        })
    } else {
        container.classList.remove('inactive')
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
                action_container(btn)
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


const templates_popup = document.getElementById('templates_popup')
const local_popup = document.getElementById('popup_local')

function open_popup(id, obj_click=false) {
    const popups = document.importNode(templates_popup.content, true)
    const popup = popups.querySelector(`#${id}`)
    const card = popup.querySelector('div.popup__container')

    const inputs = popup.querySelectorAll('input')
    set_animate_label(inputs, popup)

    const inputs_tell = popup.querySelectorAll('[class*="format_tell"]')
    set_valid_tell(inputs_tell)

    const inputs_name = popup.querySelectorAll('[class*="format_name"]')
    set_valid_name(inputs_name)
    
    const inputs_options = popup.querySelectorAll('[class*="format_options"]')
    set_input_options(inputs_options)

    const forms = popup.querySelectorAll('form')
    set_submit_form(forms)

    local_popup.appendChild(popup)
    document.body.classList.add('no-scroll')

    popup.classList.remove('inactive')
    popup.classList.remove('close')
    card.classList.remove('close')

    $(function() {
        $(".sortable").each(function() {
            setSortable($(this))
        })
    })

    if (obj_click) {
        action_popup(popup, card, id, obj_click)
    }
}


function close_popup(id) {
    const popup = local_popup.querySelector(`#${id}`)
    const card = popup.querySelector('div.popup__container')

    card.classList.add('close')
    popup.classList.add('close')

    $(function() {
        $(".sortable").each(function() {
            destroySortable($(this))
        })
    })

    setTimeout(() => {
        popup.classList.add('inactive')
        document.body.classList.remove('no-scroll')
    }, 150)
    setTimeout(() => {
        local_popup.removeChild(popup)
    }, 160)
    copy_text()
}


function config_bool(container_options, reference = 'Sim') {
    const icon_selected = container_options.querySelector('i.selected')
    const text_selected = icon_selected.parentNode.querySelector('p').textContent
    const option = container_options.querySelector('i:not(.selected)').parentNode
    if (text_selected !== reference) {popup_selectOption(option, true)}
}


function popup_confirmBox(item) {
    icon = item.querySelector('i')
    if (icon.className.includes('selected')) {
        icon.classList.replace('bi-check2-circle', 'bi-circle')
        icon.classList.remove('selected')
    } else {
        icon.classList.replace('bi-circle', 'bi-check2-circle')
        icon.classList.add('selected')
    }
}


function popup_selectOption(obj_click,  open_boxOptions = false, multiple_options = false) {
    const reference = obj_click.parentNode
    const reference_elements = Array.from(reference.children)
    const text = obj_click.querySelector('p')
    const icon = obj_click.querySelector('i')

    if (!multiple_options) {
        if (!icon.className.includes('selected')) {
            reference_elements.forEach(item => {popup_confirmBox(item)})
            if (open_boxOptions) {
                const title_options = document.getElementById(`${reference.id}_title`)
                const reference_container = document.getElementById(`${reference.id}_container`)
                const list_itens = reference_container ? reference_container.querySelectorAll('div') : false

                if (text.textContent === 'Sim') {
                    if (title_options) {title_options.classList.remove('inactive')}
                    if (reference_container) {
                        reference_container.classList.remove('inactive')
                        reference_container.scrollTop = 0
                        set_limitScroll(reference_container)
                        animate_itens(list_itens)
                    }
                } else {
                    if (reference_container) {
                        const options = reference_container.querySelectorAll('div')
                        options.forEach(item => {item.classList.remove('selected')})
                        if (title_options) {title_options.classList.add('inactive')}
                        reference_container.classList.add('inactive')
                    }
                }
            }
        }
    } else {
        if (!obj_click.className.includes('selected')) {
            reference_elements.forEach(item => {
                if (item === obj_click) {
                    item.classList.add('selected')
                } else {
                    item.classList.remove('selected')
                }
            })
        }
    }
}


function submit(form_id = false) {
    if (!form_id) {
        const buttom = document.querySelector('button.form__btn--select.selected')
        var form = document.getElementById(`form_${buttom.textContent.toLowerCase()}`)
    } else {var form = document.getElementById(form_id)}

    let execute = true
    const inputs = form.querySelectorAll('input')
    inputs.forEach(input => {
        if (input.type === 'submit') {
            execute = false
        }
    })

    if (execute) {
        if (form.checkValidity()) {
            form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
        } else {form.reportValidity()}
    }
}
