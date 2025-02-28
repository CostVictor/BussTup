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

function create_lines(local, list_datas, minha_linha = false) {
  const model_linha = models.querySelector(`#model_line`);
  for (index_linha in list_datas) {
    const linha = model_linha.cloneNode(true);
    linha.id = `${local.id}-linha_${index_linha}`;
    if (!parseInt(index_linha)) {
      linha.classList.add("first");
    }

    ids = linha.querySelectorAll(`[id*="${model_linha.id}"]`);
    ids.forEach((value) => {
      value.id = value.id.replace(model_linha.id, linha.id);
    });

    const dados = list_datas[index_linha];
    for (data in dados) {
      const value = dados[data];

      if (data === "paga") {
        const pago = linha.querySelector('[id*="paga"]');
        const gratuito = linha.querySelector('[id*="gratuita"]');
        if (!value) {
          pago.classList.add("inactive");
          gratuito.classList.remove("inactive");
        }
      } else if (data === "ferias") {
        const ferias = linha.querySelector('[id*="ferias"]');
        if (value) {
          ferias.classList.remove("inactive");
        }
      } else if (data === "diaria") {
        if (value) {
          linha
            .querySelector('[id*="icon_sched"]')
            .classList.remove("inactive");
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
      const local_linhas = document.getElementById("local_linhas");

      if (response.identify) {
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
            response.minha_linha.concat(
              response.role === "motorista" ? response.participacao : []
            )
          );
        }
        if (minha_linha_area) {
          create_lines(minha_linha_area, response.minha_linha);
        }
      } else {
        const text_span = local_linhas.querySelector("span");
        if (text_span) {
          text_span.textContent = "Nenhuma linha encontrada";
          text_span.className =
            "text secundario fundo cinza justify margin_top -enter-";
        }
      }

      if (response.role === "motorista") {
        const container_msg = document.getElementById("msg_criar_linha");
        const texts_msg = container_msg.querySelectorAll("p");
        const text_solicitar = document.getElementById("msg_solicitar_entrada");

        if (!response.minha_linha.length && !response.participacao.length) {
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

        const btn_create_line = document.getElementById("btn_create_line");
        const participacao_title = document.getElementById(
          "linhas_participacao_title"
        );
        const participacao_local = document.getElementById(
          "linhas_participacao_local"
        );
        participacao_local.innerHTML = "";

        if (response.participacao.length) {
          if (!response.minha_linha.length) {
            btn_create_line.style.margin = "0px";
          } else {
            btn_create_line.removeAttribute("style");
          }

          participacao_title.classList.remove("inactive");
          participacao_local.classList.remove("inactive");
          create_lines(participacao_local, response.participacao);
        } else {
          btn_create_line.removeAttribute("style");
          participacao_title.classList.add("inactive");
          participacao_local.classList.add("inactive");
        }
      }
      const elements = divs[2].querySelectorAll('[class*="-enter-"]');
      animate_itens(elements, "fadeDown", 0.7, 0);
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
          area_minhas_rotas.innerHTML = "";
          if (!Object.keys(data.minhas_rotas).length) {
            if (!response.possui_veiculo) {
              document
                .getElementById("sem_veiculo")
                .classList.remove("inactive");
            } else {
              document.getElementById("sem_rota").classList.remove("inactive");
            }
          }

          if (!Object.keys(data.rotas).length) {
            const text_span = area_rotas.querySelector("span");
            if (text_span) {
              text_span.textContent = "Nenhuma rota válida encontrada";
              text_span.className =
                "text secundario fundo cinza justify -enter-";
            }
          } else {
            area_rotas.innerHTML = "";
          }

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
          const model_local = models.querySelector("#model_local");
          const area_diarias = document.getElementById("minha_rota_diaria");
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

          const container_diarias = area_diarias.querySelector("div");
          container_diarias.innerHTML = "";

          if (Object.keys(data.diarias).length) {
            area_diarias.classList.remove("inactive");
            for (linha in data.diarias) {
              const list = data.diarias[linha];
              const container_diaria_local = model_local.cloneNode(true);
              container_diaria_local.id = `${container_diarias.id}-${linha}`;
              container_diaria_local.querySelector("h2").textContent = linha;

              if (Array.from(container_diarias.children).length) {
                container_diaria_local.classList.add("margin_top");
              }

              create_routes(
                list,
                container_diaria_local,
                false,
                false,
                false,
                false
              );
              container_diaria_local.classList.remove("inactive");
              container_diarias.appendChild(container_diaria_local);
            }
          } else {
            if (response.diaria_agendada) {
              area_diarias.classList.remove("inactive");
              const text_span = document.createElement("span");
              text_span.className = "text secundario fundo justify -enter-";
              text_span.textContent =
                "O acesso à rota de uma diária só estará disponível no dia previsto.";
              container_diarias.appendChild(text_span);
            } else {
              area_diarias.classList.add("inactive");
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

          if (!data.minhas_rotas.length) {
            area_minhas_rotas.innerHTML = "";
            const text = document.createElement("p");
            text.className =
              "text secundario fundo cinza justify margin_bottom -enter-";
            text.textContent = "Você não possui nenhuma rota fixa.";
            area_minhas_rotas.appendChild(text);
            local_msg.innerHTML = "";
          }

          if (!data.rotas.length) {
            area_rotas.innerHTML = "";
            const text = document.createElement("p");
            text.className =
              "text secundario fundo cinza justify margin_bottom -enter-";
            text.textContent = response.diaria_agendada
              ? "Seu acesso a esta interface será mantido até o fim da última diária agendada."
              : "Nenhuma rota válida encontrada.";
            area_rotas.appendChild(text);
          }
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

        document.getElementById("summary_route_dia_previsao").textContent =
          response.day_week;
        const span_forecast = document.getElementById(
          "summary_route_span_forecast"
        );
        const forecast = document.getElementById("summary_route_forecast");

        if (response.data_forecast) {
          span_forecast.textContent = "Inclui contraturnos e diárias";
          span_forecast.classList.add("margin_bottom");
          forecast.classList.remove("inactive");

          let previsao_partida = data.previsao_partida;
          previsao_partida = `${previsao_partida} ${
            previsao_partida === 1 ? "pessoa" : "pessoas"
          }`;
          document.getElementById(
            "summary_route_previsao_partida"
          ).textContent = previsao_partida;

          const span_passou = document.getElementById(
            "summary_route_partida_passou"
          );
          if (data.partida_passou) {
            span_passou.classList.remove("inactive");
          } else {
            span_passou.classList.add("inactive");
          }

          const msg_partida_lotado = document.getElementById(
            "summary_route_partida_lotado"
          );
          if (
            data.previsao_partida > response.capacidade &&
            !data.partida_passou
          ) {
            msg_partida_lotado.classList.remove("inactive");
          } else {
            msg_partida_lotado.classList.add("inactive");
          }

          let previsao_retorno = data.previsao_retorno;
          previsao_retorno = `${previsao_retorno} ${
            previsao_retorno === 1 ? "pessoa" : "pessoas"
          }`;
          document.getElementById(
            "summary_route_previsao_retorno"
          ).textContent = previsao_retorno;

          const msg_retorno_lotado = document.getElementById(
            "summary_route_retorno_lotado"
          );
          if (data.previsao_retorno > response.capacidade) {
            msg_retorno_lotado.classList.remove("inactive");
          } else {
            msg_retorno_lotado.classList.add("inactive");
          }
        } else {
          forecast.classList.add("inactive");
          span_forecast.textContent = data;
          span_forecast.classList.remove("margin_bottom");
        }
      } else {
        create_popup(response.title, response.text, "Ok");
        close_popup("summary_route");
      }
    });
}

function load_popup_line(card, name_line) {
  fetch(`/get_summary_line/${encodeURIComponent(name_line)}`, { method: "GET" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        if (!response.paga) {
          document
            .getElementById("summary_line_paga")
            .classList.add("inactive");
          document
            .getElementById("summary_line_gratuita")
            .classList.remove("inactive");
        }
        const data = response.data;
        for (info in data) {
          card.querySelector(`[id*="${info}"]`).textContent = data[info];
        }
        const calendar = response.calendario;
        for (day in calendar) {
          document
            .getElementById(`summary_line_${day}_color`)
            .classList.add(calendar[day]);
        }
      } else {
        create_popup(response.title, response.text, "Ok");
        close_popup("summary_line");
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
          loadSchedule();
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

function redirect_page_to_route() {
  const data = return_data_route(document.getElementById("summary_route"));
  closeInterface("page_user", "route", false, Object.values(data));
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

function page_load_forecast() {
  open_popup("forecast_route", false, false);
  const popup = document.getElementById("summary_route");
  const data = { principal: Object.values(return_data_route(popup)) };
  load_popup_forecast(data);
}
