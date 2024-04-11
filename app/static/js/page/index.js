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

function action_popup(popup, card, id, obj_click) {
  if (id === "summary_route") {
    const name_line = extract_info(obj_click, "line");
    const shift = extract_info(obj_click, "turno");
    const hr_par = extract_info(obj_click, "horario_partida");
    const hr_ret = extract_info(obj_click, "horario_retorno");
    const surname = extract_info(obj_click, "apelido");
    const driver = extract_info(obj_click, "motorista");

    popup.querySelector("#summary_route_span_turno").textContent = shift;
    popup.querySelector("#summary_route_span_partida").textContent = hr_par;
    popup.querySelector("#summary_route_span_retorno").textContent = hr_ret;

    popup.querySelector("#summary_route_linha").textContent = name_line;
    popup.querySelector("#summary_route_motorista").textContent = driver;
    popup.querySelector("#summary_route_veiculo").textContent = surname;
    popup.querySelector(
      "#summary_route_horarios"
    ).textContent = `${shift} > ${hr_par} ~ ${hr_ret}`;
    load_popup_route(popup);
  } else if (id === "summary_line") {
  }
}

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

function create_routes(
  list,
  container,
  format_min = false,
  selected = false,
  compare = false,
  reset_container = true
) {
  const model_rota = models.querySelector("#model_route");
  if (reset_container) {
    container.innerHTML = "";
  }

  for (index in list) {
    const route = model_rota.cloneNode(true);
    if (format_min) {
      route.querySelector("div.popup__input_big").classList.add("max");
      route.querySelector("p.display").classList.add("min");
    }
    route.id = `${container.id}-rota_${index}`;

    ids = route.querySelectorAll(`[id*="${model_rota.id}"]`);
    ids.forEach((value) => {
      value.id = value.id.replace(model_rota.id, route.id);
    });

    const dados = list[index];
    for (dado in dados) {
      if (dado === "estado") {
        const estado = route.querySelector('[id*="estado"]');
        estado.classList.add(dados[dado] === "Inativa" ? "red" : "green");
        estado.textContent = dados[dado];
      } else {
        route.querySelector(`[id*="${dado}"]`).textContent = dados[dado];
      }
    }

    delete dados.quantidade;
    if (compare) {
      if (Array.isArray(compare)) {
        for (pos in compare) {
          if (compare[pos][0]) {
            for (pos2 in compare[pos]) {
              const item = compare[pos][pos2];
              delete item.quantidade;

              if (JSON.stringify(item) === JSON.stringify(dados)) {
                route.classList.add("selected");
              }
            }
          } else {
            delete compare[pos].quantidade;
            if (JSON.stringify(compare[pos]) === JSON.stringify(dados)) {
              route.classList.add("selected");
            }
          }
        }
      } else {
        delete compare.quantidade;
        if (JSON.stringify(compare) === JSON.stringify(dados)) {
          route.classList.add("selected");
        }
      }
    }

    if (selected) {
      route.classList.add("selected");
    }

    route.classList.remove("inactive");
    container.appendChild(route);
  }
}

function loadLines() {
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

function loadRoutes() {
  fetch("/get_routes", { method: "GET" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const data = response.data;
        const area_minhas_rotas = document.getElementById("minha_rota_area");
        const area_rotas = document.getElementById("rotas_local");

        if (response.role === "motorista") {
          area_rotas.innerHTML = "";
          area_minhas_rotas.innerHTML = "";

          const model_regiao = models.querySelector("#model_regiao");
          const model_local = models.querySelector("#model_local");

          for (linha in data.minhas_rotas) {
            const list = data.minhas_rotas[linha];
            const local = model_local.cloneNode(true);
            const msg = local.querySelector("h2");

            local.id = `${area_minhas_rotas.id}-${linha}`;
            msg.textContent = linha;

            create_routes(list, local, false, false, false, false);
            local.classList.remove("inactive");

            if (Array.from(minha_linha_area.children).length > 1) {
              msg.classList.add("margin_top");
            }
            area_minhas_rotas.appendChild(local);
          }

          for (linha in data.rotas) {
            const list = data.rotas[linha];
            const local = model_regiao.cloneNode(true);
            const msg = local.querySelector("h2");

            local.id = `${area_rotas.id}-${linha}`;
            msg.textContent = linha;

            create_routes(
              list,
              local,
              false,
              false,
              Object.values(data.minhas_rotas),
              false
            );
            local.classList.remove("inactive");
            local.classList.add("-enter-");
            area_rotas.appendChild(local);
          }
        } else {
          const local_msg = document.getElementById("minhas_rotas_msg");
          local_msg.innerHTML = "";

          if (response.msg.length) {
            for (value in response.msg) {
              const text = document.createElement("p");
              text.className =
                "text secundario fundo cinza justify margin_bottom -enter-";
              text.textContent = response.msg[value];
              local_msg.appendChild(text);
            }
          }
          create_routes(data.minhas_rotas, area_minhas_rotas);
          create_routes(
            data.rotas,
            area_rotas,
            false,
            false,
            data.minhas_rotas
          );
        }
        const elements = divs[1].querySelectorAll('[class*="-enter-"]');
        animate_itens(elements, "fadeDown", 0.7, 0);
      } else {
        create_popup(response.title, response.text, "Voltar");
      }
    });
}
set_observerScroll(document.querySelectorAll("div.scroll_horizontal"));
set_observerScroll(document.querySelectorAll("div.scroll_vertical"));

function load_popup_route(popup) {
  const data = { principal: Object.values(return_data_route(popup)) };
  fetch("/get_summary_route" + generate_url_dict(data), { method: "GET" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const estado = document.getElementById("summary_route_estado");
        const data = response.data;

        estado.classList.add(response.estado === "Inativa" ? "red" : "green");
        estado.textContent = response.estado;
        document.getElementById(
          "summary_route_capacidade"
        ).textContent = `${response.capacidade} pessoas`;

        let previsao_partida = data.previsao_partida;
        previsao_partida = `${previsao_partida} ${
          previsao_partida === 1 ? "pessoa" : "pessoas"
        }`;
        document.getElementById("summary_route_previsao_partida").textContent =
          previsao_partida;

        if (data.previsao_partida > response.capacidade) {
          document
            .getElementById("summary_route_partida_lotado")
            .classList.remove("inactive");
        }

        let previsao_retorno = data.previsao_retorno;
        previsao_retorno = `${previsao_retorno} ${
          previsao_retorno === 1 ? "pessoa" : "pessoas"
        }`;
        document.getElementById("summary_route_previsao_retorno").textContent =
          previsao_retorno;

        if (data.previsao_retorno > response.capacidade) {
          document
            .getElementById("summary_route_retorno_lotado")
            .classList.remove("inactive");
        }
      } else {
        create_popup(response.title, response.text, "Ok");
        close_popup("summary_route");
      }
    });
}

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
        const sectionAlvo = divs[index];
        content.scrollLeft = sectionAlvo.offsetLeft;
        element.classList.add("selected");

        const abas = document.querySelectorAll(
          '[id*="area"].page__container.column'
        );
        abas.forEach((aba, index_aba) => {
          if (index_aba === index) {
            checkLine(name_aba, aba);
          } else {
            aba.classList.add("inactive");
            const local = aba.id.split("_");
            const not_line = document.getElementById(
              "not_line_" + local[local.length - 1]
            );

            if (not_line) {
              not_line.classList.add("inactive");
            }
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

        const elements = aviso.querySelectorAll('[class*="-enter-"]');
        animate_itens(elements, "fadeDown", 0.7, 0);
      } else {
        if (area) {
          area.classList.remove("inactive");
        }
        if (aviso) {
          aviso.classList.add("inactive");
        }

        if (name_aba === "agenda") {
        } else if (name_aba === "rota") {
          loadRoutes();
        } else if (name_aba === "linhas") {
          loadLines();
        }
      }
      const elements = obj_aba.querySelectorAll('[class*="-enter-"]');
      animate_itens(elements, "fadeDown", 0.7, 0);
    });
}

function redirect_page(id_obj, local) {
  if (id_obj === "summary_route") {
    const obj = document.getElementById(id_obj);
  } else {
  }
}

function return_data_route(obj) {
  return {
    name_line: obj.querySelector(`#${obj.id}_linha`).textContent,
    surname: obj.querySelector(`#${obj.id}_veiculo`).textContent,
    shift: obj.querySelector(`#${obj.id}_span_turno`).textContent,
    time_par: obj.querySelector(`#${obj.id}_span_partida`).textContent,
    time_ret: obj.querySelector(`#${obj.id}_span_retorno`).textContent,
  };
}
