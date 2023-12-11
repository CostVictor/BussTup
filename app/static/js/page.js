window.sr = ScrollReveal({ reset: true })

const header = document.getElementById('header')
const content = document.getElementById('content')
const nav = document.getElementById('nav')

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

function enterPage() {
    content.classList.remove('content_noBorder')
    setTimeout(() => {
        header.classList.remove('header_hidden')
    }, 180)
    setTimeout(() => {
        sr.reveal('.page__container--header', { duration: 600 })
        nav.classList.remove('nav_hidden')
    }, 500)
    setTimeout(() => {
        divs.forEach(element => {
            itens = element.querySelectorAll('[class*="enter"]')
            animate_itens(itens, 'fadeDown', 0.7, 0)
        })
    }, 600)
}

function closePage() {}

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
                container.scrollTop = 0
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
    }
}

function cancel_popup_edit(id) {
    const popup = document.getElementById(id)
    const card = popup.querySelector('div.popup__container')
    const scrolls = popup.querySelectorAll('div.scroll_vertical')

    card.classList.add('close')
    popup.classList.add('close')
    setTimeout(() => {
        popup.classList.add('inative')
        document.body.classList.remove('no-scroll')
        
        if (id.includes('ponto')) {
            const titles = popup.querySelectorAll('h3.popup__text.info.space')
            const containers = popup.querySelectorAll('div.scroll_vertical')
            const options = card.querySelectorAll('div.popup__input')

            titles.forEach(element => {
                element.classList.add('inative')
            })
            containers.forEach(element => {
                if (element.id !== 'scroll_principal') {
                    element.classList.add('inative')
                }
            })
            options.forEach(element => {
                if (element.className.includes('bool')) {
                    const icon = element.querySelector('i')
                    const text = element.querySelector('p')
                    if (text.textContent === 'Sim') {
                        icon.className = 'bi bi-circle popup__icon ratio'
                    } else {
                        icon.className = 'bi bi-check2-circle popup__icon ratio selected'
                    }
                } else {
                    if (element.id !== 'model_ponto') {
                        element.remove()
                    }
                }
            })
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


// ~~ Interações popup edit ~~ //

function set_limitScroll(element_scroll, size_limit = 30) {
    const maxHeight = size_limit * window.innerHeight / 100
    const size_element = element_scroll.scrollHeight
    console.log(size_element)

    if (element_scroll.childElementCount) {
        if (size_element > maxHeight) {
            element_scroll.style.minHeight = `${maxHeight}px`
        } else {element_scroll.style.minHeight = `${size_element}px`}
    } else {element_scroll.style.minHeight = '0px'}
}

function popup_selectOption(popup_id, obj_click, multiple_options = false) {
    const popup = document.getElementById(popup_id)
    const elements_popup = Array.from(popup.children)
    const text = obj_click.querySelector('p')
    const icon = obj_click.querySelector('i')

    if (!multiple_options) {
        if (!icon.className.includes('selected')) {
            elements_popup.forEach(item => {popup_confirmBox(item)})
            if (popup_id.includes('subida') || popup_id.includes('retorno')) {
                const title_options = document.getElementById(`${popup_id}_title`)
                const container_options = document.getElementById(`${popup_id}_container`)
                const list_itens = container_options.querySelectorAll('div')

                if (text.textContent === 'Sim') {
                    title_options.classList.remove('inative')
                    container_options.classList.remove('inative')
                    container_options.scrollTop = 0
                    set_limitScroll(container_options)
                    animate_itens(list_itens)
                } else {
                    const options = container_options.querySelectorAll('div')
                    options.forEach(item => {item.classList.remove('selected')})
                    title_options.classList.add('inative')
                    container_options.classList.add('inative')
                }
            }
        }
    } else {
        if (!obj_click.className.includes('selected')) {
            elements_popup.forEach(item => {
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
