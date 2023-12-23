window.sr = ScrollReveal({ reset: true })

const header = document.getElementById('header_page')
const content = document.getElementById('content_page')
const nav = document.getElementById('nav_page')

const divs = content.querySelectorAll('div.page__container--aba')
const btns = nav.querySelectorAll('i.page__icon--btn')
let aba_atual = nav.querySelector('i.btn_selected').id

// ~~ Web Socket ~~ //

fetch('/gerar_token', {method: 'GET'})
.then(response => response.json())
.then(response => {
    const token = response['token_access']
    const socket = io.connect('http://localhost:5000', {secure: true})

    // ~~ Connect
    
    socket.on('connect', () => {
        function request_line(type) {
            if (type === 'schedule') {
                socket.emit('send_line_schedule', { token })
            }
        }

        function request_realTime() {
            switch (aba_atual) {
                case 'agenda': break
                case 'ponto': break
                case 'linha': break
                case 'chat': break
            }
        }
        socket.emit('send_schedule', { token })
        let aba_ant = aba_atual
    
        setInterval(() => {
            if (aba_ant !== aba_atual) {
                aba_ant = aba_atual
                request_realTime()
            }
        }, 500)
        setInterval(request_realTime, 3000)
        
        // ~~ Action

        socket.on('return_lines', (data) => {
            console.log(data)
        })

        socket.on('return_schedule', (data) => {
            const area_agenda = document.getElementById('area_agenda')
        })

    })
})


// ~~ Página ~~ //

function enterPage(reset_header = false) {
    content.classList.remove('content_noBorder')

    setTimeout(() => {
        header.classList.remove('header_hidden')
    }, 180)

    setTimeout(() => {
        header.style.opacity = '1'
        sr.reveal('.page__container--header', {
            duraction: 600, 
            beforeReveal: (domElement) => {
                domElement.style.opacity = '1';
            } 
        })
        nav.classList.remove('nav_hidden')
    }, 500)

    setTimeout(() => {
        divs.forEach(element => {
            itens = element.querySelectorAll('[class*="enter"]')
            animate_itens(itens, 'fadeDown', 0.7, 0)
        })
    }, 600)
    setTimeout(() => {
        sr.reveal(header, { reset: true })
    }, 1150)
}

function closePage() {
    const aba = document.getElementById(`aba_${aba_atual}`)
    const itens = aba.querySelectorAll('[class*="enter"]')
    header.style.opacity = '0'

    setTimeout(() => {
        animate_itens(itens, 'outUp', 0.5, 0, 0.03, 1)
    }, 100)

    setTimeout(() => {
        header.classList.add('header_hidden')
        nav.classList.add('nav_hidden')
    }, 150)

    setTimeout(() => {
        content.classList.add('content_noBorder')
    }, 400)
}

function open_popup_edit(id, obj_click=false) {
    document.body.classList.add('no-scroll')
    const popup = document.getElementById(id)
    const card = popup.querySelector('div.popup__container')
    popup.classList.remove('inative')
    popup.classList.remove('close')
    card.classList.remove('close')

    if (obj_click) {
        function define_checkbox(item, text_reference) {
            const text = item.querySelector('p')
            const icon = item.querySelector('i')
            if (text.textContent === text_reference) {
                icon.className = 'bi bi-check2-circle popup__icon ratio selected'
            } else {icon.className = 'bi bi-circle popup__icon ratio'}
        }
        function correct_options(condiction, options, title, container, list_itens) {
            if (condiction) {
                options.forEach(item => {define_checkbox(item, 'Sim')})
                title.classList.remove('inative')
                container.classList.remove('inative')
                animate_itens(list_itens)
                list_itens.forEach((item, index) => {
                    if (index === parseInt(condiction)) {
                        item.classList.add('selected')
                    } else {
                        item.classList.remove('selected')
                    }
                })
            } else {
                options.forEach(item => {define_checkbox(item, 'Não')})
                title.classList.add('inative')
                container.classList.add('inative')
                list_itens.forEach(item => {
                    item.classList.remove('selected')
                })
            }
        }
        function extract_placa() {
            const reference = obj_click.parentNode.parentNode.id.replace('_container', '_placa')
            return document.getElementById(reference).textContent
        }

        if (id === 'edit_dia') {
            const dia = document.getElementById('dia')
            const data = document.getElementById('data_dia')
            const options_falta = document.getElementById('options_falta').querySelectorAll('div')
            const options_contraturno = document.getElementById('options_contraturno').querySelectorAll('div')
            const options_subida = document.getElementById('options_subida').querySelectorAll('div')
            const options_descer = document.getElementById('options_retorno').querySelectorAll('div')
            
            const text_dia = obj_click.querySelector('h1').textContent
            const text_falta = obj_click.querySelector(`p#falta_${text_dia}`).textContent
            const text_contraturno = obj_click.querySelector(`p#contraturno_${text_dia}`).textContent
            const text_subir = obj_click.querySelector(`p#pSubida_${text_dia}`).textContent
            const text_descer = obj_click.querySelector(`p#pDescida_${text_dia}`).textContent
    
            dia.textContent = `Editar ${text_dia}`
            data.textContent = obj_click.querySelector(`p#data_${text_dia}`).textContent
            options_falta.forEach(item => {define_checkbox(item, text_falta)})
            options_contraturno.forEach(item => {define_checkbox(item, text_contraturno)})
            
            const title_subir = document.getElementById('options_subida_title')
            const container_subir = document.getElementById('options_subida_container')
            const list_itens_subir = container_subir.querySelectorAll('div')
            correct_options(text_subir, options_subida, title_subir, container_subir, list_itens_subir)
    
            const title_descer = document.getElementById('options_retorno_title')
            const container_descer = document.getElementById('options_retorno_container')
            const list_itens_descer = container_descer.querySelectorAll('div')
            correct_options(text_descer, options_descer, title_descer, container_descer, list_itens_descer)

        } else if (id === 'edit_valor') {
            card.querySelector('h2').textContent = `Digite o novo valor da ${obj_click.id.includes('cartela') ? 'cartela' : 'diária'}:`

        } else if (id === 'edit_capacidade') {
            card.querySelector('h2').textContent = `Digite a capacidade de ${extract_placa()}:`

        } else if (id === 'edit_motorista') {
            card.querySelector('h2').textContent = `Selecione o motorista de ${extract_placa()}:`

        } else if (id == 'excluir_veiculo') {
            card.querySelector(`h2#${id}_placa`).textContent = extract_placa()
        }
    }
}

function cancel_popup_edit(id, reset_bool = false, reference_bool = 'Não') {
    const popup = document.getElementById(id)
    const card = popup.querySelector('div.popup__container')
    const scrolls = popup.querySelectorAll('div.scroll_vertical')

    card.classList.add('close')
    popup.classList.add('close')
    setTimeout(() => {
        popup.classList.add('inative')
        document.body.classList.remove('no-scroll')
        
        if (popup.querySelector('form')) {
            const inputs = popup.querySelectorAll('input')
            inputs.forEach(element => {
                element.classList.remove('input_error')
                element.value = ''
            })
        }
        if (reset_bool) {
            const options = card.querySelectorAll('div.popup__input.bool')
            options.forEach(element => {
                const icon = element.querySelector('i')
                const text = element.querySelector('p')
                if (text.textContent !== reference_bool) {
                    icon.className = 'bi bi-circle popup__icon ratio'
                } else {
                    const titles = popup.querySelectorAll('h3.popup__text.info.space')
                    const containers = popup.querySelectorAll('[id*="container"]')

                    icon.className = 'bi bi-check2-circle popup__icon ratio selected'
                    if (titles && containers) {
                        titles.forEach(element => {
                            text.textContent == 'Não' ? element.classList.add('inative') : element.classList.remove('inative')
                        })
                        containers.forEach(element => {
                            if (element.id !== 'scroll_principal') {
                                text.textContent == 'Não' ? element.classList.add('inative') : element.classList.remove('inative')

                                Array.from(element.children).forEach(item => {
                                    item.classList.remove('selected')
                                })
                            }
                        })
                    }
                }
            })
        } else {
            const containers = popup.querySelectorAll('[id*="container"]')
            if (containers) {
                containers.forEach(element => {
                    Array.from(element.children).forEach(item => {
                        item.classList.remove('selected')
                    })
                })
            }
        }

    }, 100)
    scrolls.forEach(element => {
        element.scrollTop = 0
    })
}


// ~~ Animação de rolamento ~~ //

function ajustAba(index_atual) {
    const abas = document.querySelectorAll('div.page__container.column')
    abas.forEach((aba, index_aba) => {
        if (index_aba === index_atual) {
            checkLine()
        } else {
            aba.classList.add('inative')
        }
    })
}

let isScrolling
content.addEventListener('scroll', function() {
    clearTimeout(isScrolling)
    isScrolling = setTimeout(function() {
        const larguraDiv = content.scrollWidth / divs.length;
        const index = Math.floor(content.scrollLeft / larguraDiv)
      
        btns.forEach((btn) => {
            btn.classList.remove('btn_selected')
        })
        btns[index].classList.add('btn_selected')
        aba_atual = btns[index].id
        ajustAba(index)
    }, 40)
  })

function replaceAba(btn_id) {
    btns.forEach((element, index) => {
        if (element.id === btn_id) {
            const divAlvo = divs[index]
            content.scrollLeft = divAlvo.offsetLeft
            element.classList.add('btn_selected')
        } else {
            element.classList.remove('btn_selected')
        }
    })
}

function set_observerScroll(obj) {
    for (let index = 0; index < obj.length; index++) {
        const observer = createObserver(obj[index], 0.15)
        let elements_animate = obj[index]
        elements_animate = elements_animate.querySelectorAll('div.hidden')
        elements_animate.forEach(element => {
            observer.observe(element)
        })
    }
}
set_observerScroll(document.querySelectorAll('div.scroll_horizontal'))
set_observerScroll(document.querySelectorAll('div.scroll_vertical'))


// ~~ Interações na aba ~~ //

function checkLine() {
    fetch('/checar_linha', { method: 'GET' })
    .then(response => response.json())
    .then(response => {
        const aviso = document.getElementById(`not_line_${aba_atual}`)
        const area = document.getElementById(`area_${aba_atual}`)

        if (!response['conf'] && aba_atual !== 'linhas') {
            area.classList.add('inative')
            aviso.classList.remove('inative')
        } else {
            if (area) {area.classList.remove('inative')}
            if (aviso) {aviso.classList.add('inative')}
        }
    })
}

// ~~ Aba agenda
function checkForecast(id) {
    const btn_title = document.getElementById(`title_${id}`)
    const icon_title = btn_title.querySelector('i')
    const container_dias = document.getElementById(`dias_${id}`)
    dias = container_dias.querySelectorAll('div.align')
    
    if (container_dias.className.includes('inative')) {
        animate_itens(dias)
        container_dias.classList.remove('inative')
        icon_title.classList.add('open')
    } else {
        container_dias.classList.add('inative')
        icon_title.classList.remove('open')
    }
}

// ~~ Interface
function actionContainer(obj_click) {
    const icon = obj_click.querySelector('i')
    const container = document.getElementById(obj_click.id.replace('_btn', '_container'))
    const elements = Array.from(container.children)
    obj_click.style.transition = '0s ease'

    if (obj_click.id.includes('onibus')) {
        const motorista_nome = obj_click.querySelectorAll('h3')
        motorista_nome.forEach((element, index) => {
            if (!index) {
                icon.className.includes('open') ? element.classList.remove('max_width'): element.classList.add('max_width')
            } else {
                icon.className.includes('open') ? element.classList.remove('inative') : element.classList.add('inative')
            }
        })

    }
    
    animate_itens(elements)
    if (icon.className.includes('open')) {
        container.classList.add('inative')
        icon.classList.remove('open')
        obj_click.classList.remove('margin_bottom')
    } else {
        container.classList.remove('inative')
        container.scrollTop = 0
        icon.classList.add('open')
        obj_click.classList.add('margin_bottom')
    }
    const rolament = container.querySelector('div.scroll_vertical')
    if (rolament) {rolament.scrollTop = 0}
}


// ~~ Interações popup edit ~~ //

function set_limitScroll(element_scroll, size_limit = 30) {
    const maxHeight = size_limit * window.innerHeight / 100
    const size_element = element_scroll.scrollHeight

    if (element_scroll.childElementCount) {
        if (size_element > maxHeight) {
            element_scroll.style.minHeight = `${maxHeight}px`
        } else {element_scroll.style.minHeight = `${size_element}px`}
    } else {element_scroll.style.minHeight = '0px'}
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
                const list_itens = reference_container.querySelectorAll('div')

                if (text.textContent === 'Sim') {
                    if (title_options) {title_options.classList.remove('inative')}
                    reference_container.classList.remove('inative')
                    reference_container.scrollTop = 0
                    set_limitScroll(reference_container)
                    animate_itens(list_itens)
                } else {
                    const options = reference_container.querySelectorAll('div')
                    options.forEach(item => {item.classList.remove('selected')})
                    if (title_options) {title_options.classList.add('inative')}
                    reference_container.classList.add('inative')
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
