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

  const btn_atualizar_trajeto = document.getElementById(
    "btn_atualizar_trajeto"
  );
  let elements = [];
  if (type === "partida") {
    replace_forecast("partida");
    btn_partida.classList.add("selected");
    btn_retorno.classList.remove("selected");

    container_partida.classList.remove("inactive");
    container_retorno.classList.add("inactive");
    elements = Array.from(container_partida.children);

    if (btn_atualizar_trajeto) {
      btn_atualizar_trajeto.textContent = "Iniciar trajeto de partida";
    }
  } else {
    replace_forecast("retorno");
    btn_retorno.classList.add("selected");
    btn_partida.classList.remove("selected");

    container_retorno.classList.remove("inactive");
    container_partida.classList.add("inactive");
    elements = Array.from(container_retorno.children);

    if (btn_atualizar_trajeto) {
      btn_atualizar_trajeto.textContent = "Iniciar trajeto de retorno";
    }
  }
  animate_itens(elements, "fadeDown", 0.7, 0);
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
                if (number && data[number - 1][info]) {
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
        if (response.hoje.includes("Indisponível")) {
          msg_load_forecast.textContent = response.hoje;
        } else {
          msg_load_forecast.textContent = `Painel de Hoje (${response.hoje})`;
        }

        document.getElementById(`previsao_${type}`).textContent = data.previsao;
        document.getElementById(`no_veiculo_${type}`).textContent =
          data.presente;

        if (execute) {
          replace_path("partida");
        }
      } else {
        document.getElementById("interface_load_forecast").textContent =
          "Erro de carregamento";
        create_popup(response.title, response.text);
      }
    });
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

function return_stop_path(pos) {
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
    }
  }

  if (target) {
    return document.getElementById(`${target.id}_local`).textContent.trim();
  }
  return null;
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
  data.principal.push(type)
  data.principal.push(local)

  fetch("/get_data_stop_path" + generate_url_dict(data), { method: "GET" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        console.log(response)
      } else {
        create_popup(response.title, response.text)
      }
    });
}
