const header = document.getElementById('header_page')
const content = document.getElementById('content_page')
const nav = document.getElementById('nav_page')

const divs = content.querySelectorAll('div.page__container--aba')
const btns = nav.querySelectorAll('i.page__icon--btn')
let aba_atual = nav.querySelector('i.btn_selected').id

header.style.opacity = 0
observer_header = createObserver(null)
observer_header.observe(header)

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
        header.removeAttribute('style')
        nav.classList.remove('nav_hidden')
    }, 500)

    setTimeout(() => {
        divs.forEach(element => {
            itens = element.querySelectorAll('[class*="enter"]')
            animate_itens(itens, 'fadeDown', 0.7, 0)
        })
    }, 600)
}


function closePage() {
    const aba = document.getElementById(`aba_${aba_atual}`)
    const itens = aba.querySelectorAll('[class*="enter"]')
    header.style.opacity = 0

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


// ~~ Animação de rolamento ~~ //

function ajustAba(index_atual) {
    const abas = document.querySelectorAll('[id*="area"].page__container.column')
    abas.forEach((aba, index_aba) => {
        if (index_aba === index_atual) {
            checkLine()
        } else {
            aba.classList.add('inactive')
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

function replaceAba(btn_click) {
    btns.forEach((element, index) => {
        if (element === btn_click) {
            const divAlvo = divs[index]
            content.scrollLeft = divAlvo.offsetLeft
            element.classList.add('btn_selected')
        } else {
            element.classList.remove('btn_selected')
        }
    })
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
            area.classList.add('inactive')
            aviso.classList.remove('inactive')
        } else {
            if (area) {area.classList.remove('inactive')}
            if (aviso) {aviso.classList.add('inactive')}
        }
    })
}
