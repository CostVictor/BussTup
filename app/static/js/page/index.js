const header = window.info_page.header;
const content = window.info_page.content;
const nav = window.info_page.nav;

const divs = content.querySelectorAll("section.page__container--aba");
const btns = nav.querySelectorAll("i.page__icon--btn");

header.style.opacity = 0;
observer_header = createObserver(null);
observer_header.observe(header);

const templates_model = document.getElementById("templates_model");
const models = document.importNode(templates_model.content, true);

function loadLines() {
  function create_lines(local, list_datas, minha_linha = false) {
    const model_linha = models.querySelector(`#model_line`);
    for (index_linha in list_datas) {
      const linha = model_linha.cloneNode(true);
      linha.id = `${local.id}-linha_${index_linha}`;
      if (!parseInt(index_linha)) {
        linha.classList.add("first");
      }

      const dados = list_datas[index_linha];
      for (data in dados) {
        const value = dados[data];

        if (data === "paga") {
          const pago = linha.querySelector("h1#model_line_paga");
          const gratuito = linha.querySelector("h1#model_line_gratuita");
          pago.id = pago.id.replace("model_line", linha.id);
          gratuito.id = gratuito.id.replace("model_line", linha.id);
          if (!value) {
            pago.classList.add("inactive");
            gratuito.classList.remove("inactive");
          }
        } else if (data === "ferias") {
          const ferias = linha.querySelector("h1#model_line_ferias");
          ferias.id = ferias.id.replace("model_line", linha.id);
          if (value) {
            ferias.classList.remove("inactive");
          }
        } else {
          const info = linha.querySelector(`[id*="${data}"]`);
          info.id = linha.id + "_" + data;
          info.textContent = value;
        }
        linha.classList.remove("inactive");

        if (minha_linha) {
          if (Array.isArray(minha_linha)) {
            for (element in minha_linha) {
              if (minha_linha[element]["nome"] === dados.nome) {
                linha.classList.add("selected");
              }
            }
          } else {
            if (dados.nome === minha_linha) {
              linha.classList.add("selected");
            }
          }
        }
      }
      local.appendChild(linha);
    }
  }

  fetch("/get_lines", { method: "GET" })
    .then((response) => response.json())
    .then((response) => {
      if (response.identify) {
        const local_linhas = document.getElementById("local_linhas");
        const minha_linha_area = document.getElementById("minha_linha_area");
        if (minha_linha_area) {
          minha_linha_area.innerHTML = "";
        }
        local_linhas.innerHTML = "";

        const model_regiao = models.querySelector("#model_regiao");
        for (cidade in response.cidades) {
          if (!local_linhas.querySelector(`div#${cidade}`)) {
            var regiao = model_regiao.cloneNode(true);
            regiao.id = cidade;

            regiao.querySelector("h2").textContent = cidade;
            regiao.classList.remove("inactive");
            regiao.classList.add("-enter-");
            local_linhas.appendChild(regiao);
          }
          create_lines(
            regiao,
            response["cidades"][cidade],
            response.minha_linha
          );
        }
        if (minha_linha_area) {
          create_lines(minha_linha_area, response.minha_linha);
        }
        const elements = divs[2].querySelectorAll('[class*="-enter-"]');
        animate_itens(elements, "fadeDown", 0.7, 0);
      }

      if (response.role === "motorista") {
        const container_msg = document.getElementById("msg_criar_linha");
        const texts_msg = container_msg.querySelectorAll("p");
        const text_solicitar = document.getElementById("msg_solicitar_entrada");

        if (!response.minha_linha.length) {
          text_solicitar.classList.remove("inactive");
          texts_msg.forEach((msg) => {
            msg.classList.remove("inactive");
          });
        } else {
          text_solicitar.classList.add("inactive");
          texts_msg.forEach((msg) => {
            msg.classList.add("inactive");
          });
        }
      }
    });
}
set_observerScroll(document.querySelectorAll("div.scroll_horizontal"));
set_observerScroll(document.querySelectorAll("div.scroll_vertical"));

function replaceAba(btn_click, id = "") {
  let name_aba = id;
  let execute = true;

  if (name_aba) {
    btn_click = document.getElementById(name_aba);
  } else {
    name_aba = btn_click.id;
    if (btn_click.className.includes("selected")) {
      execute = false;
    }
  }

  if (execute) {
    btns.forEach((element, index) => {
      if (element === btn_click) {
        const divAlvo = divs[index];
        content.scrollLeft = divAlvo.offsetLeft;
        element.classList.add("selected");

        const abas = document.querySelectorAll(
          '[id*="area"].page__container.column'
        );
        abas.forEach((aba, index_aba) => {
          if (index_aba === index) {
            checkLine(name_aba, aba);
          } else {
            aba.classList.add("inactive");
          }
        });
      } else {
        element.classList.remove("selected");
      }
    });
  }
}

function checkLine(name_aba, obj_aba) {
  fetch("/get_association", { method: "GET" })
    .then((response) => response.json())
    .then((response) => {
      const aviso = document.getElementById(`not_line_${name_aba}`);
      const area = document.getElementById(`area_${name_aba}`);

      if (!response.conf && name_aba !== "linhas") {
        area.classList.add("inactive");
        aviso.classList.remove("inactive");
      } else {
        if (area) {
          area.classList.remove("inactive");
        }
        if (aviso) {
          aviso.classList.add("inactive");
        }

        if (name_aba === "agenda") {
        } else if (name_aba === "rota") {
        } else if (name_aba === "linhas") {
          loadLines();
        }
      }
      const elements = obj_aba.querySelectorAll('[class*="-enter-"]');
      animate_itens(elements, "fadeDown", 0.7, 0);
    });
}
