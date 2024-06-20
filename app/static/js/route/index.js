const templates_model = document.getElementById("templates_model");
const models = document.importNode(templates_model.content, true);

function loadInterfaceRoute() {
  const elements = document.querySelectorAll('[class*="-enter-"]');
  animate_itens(elements, "fadeDown", 0.6, 0.2);

  load_info((type = "partida"), (execute = true));
  load_info((type = "retorno"), (execute = false));
  load_path("partida");
  load_path("retorno");
}

function replace_path(type) {
  const btn_partida = document.getElementById("route_btn_partida");
  const container_partida = document.getElementById("route_container_partida");

  const btn_retorno = document.getElementById("route_btn_retorno");
  const container_retorno = document.getElementById("route_container_retorno");

  const btn_iniciar_trajeto = document.getElementById("btn_iniciar_trajeto");
  let elements = [];
  if (type === "partida") {
    replace_forecast("partida");
    btn_partida.classList.add("selected");
    btn_retorno.classList.remove("selected");

    container_partida.classList.remove("inactive");
    container_retorno.classList.add("inactive");
    elements = Array.from(container_partida.children);

    if (btn_iniciar_trajeto) {
      btn_iniciar_trajeto.textContent = "Iniciar trajeto de partida";
    }
  } else {
    replace_forecast("retorno");
    btn_retorno.classList.add("selected");
    btn_partida.classList.remove("selected");

    container_retorno.classList.remove("inactive");
    container_partida.classList.add("inactive");
    elements = Array.from(container_retorno.children);

    if (btn_iniciar_trajeto) {
      btn_iniciar_trajeto.textContent = "Iniciar trajeto de retorno";
    }
  }
  animate_itens(elements, "fadeDown", 0.7, 0);
}

function open_stop_current() {
  const container = document.getElementById(
    `route_container_${return_path_selected()}`
  );
  const local = Array.from(container.children).find((value) =>
    value.querySelector("i:not(.inactive)")
  );
  close_popup("route_stop_path");
  setTimeout(() => {
    open_stop_path(local);
  }, 250);
}

function return_data_route() {
  const horarios = document
    .getElementById("interface_horarios")
    .textContent.trim()
    .split(" > ");
  const times = horarios[1].split(" ~ ");

  return {
    name_line: document.getElementById("interface_nome").textContent.trim(),
    surname: document.getElementById("interface_vehicle").textContent.trim(),
    shift: horarios[0],
    time_par: times[0],
    time_ret: times[1],
  };
}

function load_path(type) {
  const data = {
    principal: Object.values(return_data_route()),
  };
  data.principal.push(type);

  fetch("/get_stop_path" + generate_url_dict(data), { method: "GET" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const data = response.data;
        const model_stop_path = models.querySelector("#model_stop_path");
        const container = document.getElementById(`route_container_${type}`);
        container.innerHTML = "";

        for (index in data) {
          const stop = model_stop_path.cloneNode(true);
          stop.id = container.id + `_stop_${index}`;

          ids = stop.querySelectorAll(`[id*="${model_stop_path.id}"]`);
          ids.forEach((value) => {
            value.id = value.id.replace(model_stop_path.id, stop.id);
          });

          if (
            (response.relacao && response.relacao !== "não participante") ||
            response.passagem_diaria
          ) {
            stop.onclick = function () {
              open_stop_path(this);
            };
          }

          for (info in data[index]) {
            const value = data[index][info];

            if (info === "passou") {
              const container_efect = stop.querySelector(`#${stop.id}_efect`);
              container_efect.classList.remove("passou");

              const text_efect = container_efect.querySelector("p");
              const icon = container_efect.querySelector("i");

              const number = parseInt(index);
              stop.querySelector(`#${stop.id}_posicao`).textContent =
                number + 1;

              if (value) {
                icon.classList.add("inactive");
                text_efect.classList.remove("inactive");
                container_efect.classList.add("passou");
              } else {
                if (
                  (!number && type === response.estado) ||
                  (number && data[number - 1][info])
                ) {
                  icon.classList.remove("inactive");
                  text_efect.classList.add("inactive");
                }
              }
            } else if (info === "meu_ponto") {
              if (value) {
                stop.classList.add("selected");
              }
            } else {
              stop.querySelector(`#${stop.id}_${info}`).textContent = value;
            }
          }
          container.appendChild(stop);
        }
        const btn_update = document.getElementById("route_update_path");
        btn_update.querySelector("p").textContent = "Atualizar trajeto";
        btn_update.onclick = function () {
          reload_data_path();
        };
      } else {
        create_popup(response.title, response.text);
      }
    });
}

function load_info(type, execute = false) {
  const data = {
    principal: Object.values(return_data_route()),
  };
  data.principal.push(type);

  fetch("/get_data_route" + generate_url_dict(data), { method: "GET" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const data = response.data;
        document.getElementById("interface_estado").textContent = data.estado;
        const msg_load_forecast = document.getElementById(
          "interface_load_forecast"
        );

        const btn_atualizar_trajeto =
          document.getElementById("route_update_path");
        btn_atualizar_trajeto.style.margin = "0px";

        if (response.role === "motorista") {
          const btn_iniciar_trajeto = document.getElementById(
            "btn_iniciar_trajeto"
          );
          btn_iniciar_trajeto.parentNode.classList.add("inactive");

          if (response.driver_current && data.estado === "Inativa") {
            btn_iniciar_trajeto.parentNode.classList.remove("inactive");
            btn_atualizar_trajeto.removeAttribute("style");
          }
        } else {
          const btn_solicitar_espera = document.getElementById(
            "btn_solicitar_espera"
          );
          btn_solicitar_espera.classList.add("inactive");

          if (
            response.relationship !== "não participante" ||
            response.pass_daily
          ) {
            btn_solicitar_espera.classList.remove("inactive");
            btn_atualizar_trajeto.removeAttribute("style");
          }
        }

        if (response.hoje.includes("Indisponível")) {
          msg_load_forecast.textContent = response.hoje;
        } else {
          msg_load_forecast.textContent = `Painel de Hoje (${response.hoje})`;
        }

        document.getElementById(`previsao_${type}`).textContent = data.previsao;
        document.getElementById(`no_veiculo_${type}`).textContent =
          data.presente;

        if (execute) {
          replace_path(type);
        }
      } else {
        document.getElementById("interface_load_forecast").textContent =
          "Erro de carregamento";
        create_popup(response.title, response.text);
      }
    });
}

function reload_data_path() {
  const btn_update = document.getElementById("route_update_path");
  btn_update.querySelector("p").textContent = "Aguarde...";
  btn_update.onclick = null;

  const type = return_path_selected();
  load_info(type, true);
  load_path(type);
}

function reload_data_stop() {
  const btn_update = document.getElementById("route_update_data_stop");
  btn_update.querySelector("p").textContent = "Aguarde...";
  btn_update.onclick = null;

  const container = document.getElementById(
    `route_container_${return_path_selected()}`
  );
  const local = Array.from(container.children).find(
    (value) =>
      value.querySelector(`#${value.id}_local`).textContent ===
      document.getElementById("route_stop_path_local").textContent
  );
  open_stop_path(local);
}

function replace_forecast(type) {
  const previsao = document.getElementById("previsao_pessoas");
  const quantidade = document.getElementById("quantidade_veiculo");

  if (type === "partida") {
    const previsao_partida = document
      .getElementById("previsao_partida")
      .textContent.trim();
    const quantidade_partida = document
      .getElementById("no_veiculo_partida")
      .textContent.trim();
    previsao.textContent = previsao_partida;
    quantidade.textContent = quantidade_partida;
  } else {
    const previsao_retorno = document
      .getElementById("previsao_retorno")
      .textContent.trim();
    const quantidade_retorno = document
      .getElementById("no_veiculo_retorno")
      .textContent.trim();
    previsao.textContent = previsao_retorno;
    quantidade.textContent = quantidade_retorno;
  }
}

function return_path_selected() {
  const route_btn_partida = document.getElementById("route_btn_partida");
  if (route_btn_partida.className.includes("selected")) {
    return "partida";
  }
  return "retorno";
}

function return_stop_path(pos, return_obj = false) {
  const container = document.getElementById(
    `route_container_${return_path_selected()}`
  );
  const elements = Array.from(container.children);
  let target = null;
  if (elements.length) {
    if (pos === "primeiro") {
      target = elements[0];
    } else if (pos === "ultimo") {
      target = elements[elements.length - 1];
    } else if (pos === "atual") {
      const icon = container.querySelector("i:not(.inactive)");
      if (icon) {
        target = icon.parentNode.parentNode;
      }
    } else if (pos === 'proximo') {
      const icon = container.querySelector("i:not(.inactive)");
      const current = icon.parentNode.parentNode
      const pos_element = Array.prototype.indexOf.call(container.children, current)
      if ((pos_element + 1) <= elements.length) {
        target = elements[pos_element + 1]
      }
    }
  }

  if (target) {
    if (return_obj) {
      return target
    }
    return document.getElementById(`${target.id}_local`).textContent.trim();
  }
  return null;
}

function create_student(container, list, response, list_espera = false) {
  const model_student = models.querySelector("#model_student_path");
  if (list_espera) {
    for (index in list) {
      const name_student = list[index];

      const student = model_student.cloneNode(true);
      student.id = `${container.id}_student_${index}`;
      student.querySelector("p").textContent = name_student;

      if (response.role === "aluno" && response.meu_nome === name_student) {
        student.querySelector("i").classList.remove("inactive");
      }
      container.appendChild(student);
    }
  } else {
    for (index in list) {
      const data_student = list[index];

      const student = model_student.cloneNode(true);
      student.id = `${container.id}_student_${index}`;
      student.querySelector("p").textContent = data_student.nome;

      if (data_student.diaria || data_student.contraturno) {
        const info_daily = document.createElement("h1");
        info_daily.className = "route__text_info";
        student.insertBefore(info_daily, student.children[0]);
        info_daily.textContent = data_student.diaria ? "Diária" : "Contr...";
      }
      if (response.role === "motorista") {
        student.classList.add("click");
        student.querySelector("i").classList.remove("inactive");
        student.onclick = function () {
          get_data_student(this);
        };
      }
      container.appendChild(student);
    }
  }
}

function open_stop_path(obj_click) {
  open_popup("route_stop_path");
  const type = return_path_selected();
  const local = obj_click
    .querySelector(`#${obj_click.id}_local`)
    .textContent.trim();
  document.getElementById("route_stop_path_local").textContent = local;

  const title = document.getElementById("route_stop_path_title_students");
  if (type === "partida") {
    title.textContent = "Sobe neste ponto:";
  } else {
    title.textContent = "Desce neste ponto:";
  }
  const data = {
    principal: Object.values(return_data_route()),
  };
  data.principal.push(type);
  data.principal.push(local);

  fetch("/get_data_stop_path" + generate_url_dict(data), { method: "GET" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const data = response.data;
        const local_espera = document.getElementById("route_stop_path_espera");
        const container_espera = local_espera.querySelector("div");
        const container_subira = document.getElementById(
          "route_stop_path_container_students"
        );
        container_espera.innerHTML = "";
        container_subira.innerHTML = "";

        const btn_fechar = document.getElementById(
          "route_stop_path_btn_fechar"
        );
        btn_fechar.classList.remove("cancel");

        const btn_atual = document.getElementById(
          "route_stop_path_acessar_atual"
        );
        btn_atual.classList.add("inactive");

        const btn_confirmar = document.getElementById(
          "route_stop_path_confirmar"
        );
        if (btn_confirmar) {
          btn_confirmar.classList.add("inactive");
        }

        const title_subira = document.getElementById(
          "route_stop_path_title_students"
        );
        const title_espera = document.getElementById(
          "route_stop_path_title_espera"
        );

        const atual = return_stop_path("atual");
        if (
          atual &&
          atual !== response.ponto_atual &&
          response.estado === type
        ) {
          reload_data_path();
        }

        if (data.pedindo_espera.length) {
          title_subira.classList.remove("first");
          local_espera.classList.remove("inactive");
          title_espera.textContent = `Pedindo para esperar (${data.pedindo_espera.length}):`;
          create_student(
            container_espera,
            data.pedindo_espera,
            response,
            (list_espera = true)
          );
        } else {
          title_espera.textContent = "Pedindo para esperar:";
          local_espera.classList.add("inactive");
          title_subira.classList.add("first");
        }

        const container_msg = document.getElementById(
          "route_stop_path_container_span"
        );
        container_msg.classList.add("inactive");

        const msg_passou = document.getElementById("route_stop_path_passou");
        msg_passou.classList.add("inactive");

        const msg_atual = document.getElementById("route_stop_path_atual");
        msg_atual.classList.add("inactive");

        if (response.passou) {
          container_msg.classList.remove("inactive");
          msg_passou.classList.remove("inactive");
          if (response.estado === type) {
            btn_fechar.classList.add("cancel");
            btn_atual.classList.remove("inactive");
          }
        } else if (response.estado === type) {
          if (response.ponto_atual === local) {
            if (response.role === "motorista" && response.condutor_atual) {
              btn_fechar.classList.add("cancel");
              btn_confirmar.classList.remove("inactive");
            } else {
              container_msg.classList.remove("inactive");
              msg_atual.classList.remove("inactive");
            }
          } else {
            btn_fechar.classList.add("cancel");
            btn_atual.classList.remove("inactive");
          }
        }

        if (type === "partida") {
          title_subira.textContent = `Sobe neste ponto (${data.subira.length}):`;
        } else {
          title_subira.textContent = `Desce neste ponto (${data.subira.length}):`;
        }

        if (data.subira.length) {
          create_student(container_subira, data.subira, response);
        } else {
          const text = document.createElement("p");
          text.className = "text secundario fundo cinza justify";
          text.textContent = "Nenhum aluno previstro para este ponto hoje.";
          container_subira.appendChild(text);
        }

        const btn_update = document.getElementById("route_update_data_stop");
        btn_update.querySelector("p").textContent = "Atualizar informações";
        btn_update.onclick = function () {
          reload_data_stop();
        };
      } else {
        create_popup(response.title, response.text);
      }
    });
}
