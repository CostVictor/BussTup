var templates = document.getElementById("templates_model");
var models = document.importNode(templates.content, true);

function action_popup(popup, card, id, obj_click) {
  if (id === "edit_vehicle_capacidade") {
    const surname = extract_info(obj_click, "surname");
    popup.querySelector("span").textContent = surname;
    card.querySelector("h2").textContent = `Digite a capacidade de ${surname}:`;
  } else if (id === "edit_vehicle_motorista") {
    const data = {
      principal: [document.getElementById("interface_nome").textContent],
      secondary: {},
    };

    const surname_vehicle = extract_info(obj_click, "surname");
    const info_atual = extract_info(obj_click, "motorista");
    popup.querySelector("span").textContent = surname_vehicle;
    card.querySelector(
      "h2"
    ).textContent = `Selecione o motorista de ${surname_vehicle}:`;

    const container = document.getElementById(
      "edit_vehicle_motorista_container"
    );
    container.innerHTML = "";

    let option_nenhum = true;
    if (info_atual === "Nenhum") {
      option_nenhum = false;
    }
    include_options_container(container, "option_driver", data, option_nenhum);
  } else if (id === "config_motorista") {
    card.querySelector("h1").textContent = extract_info(obj_click, "nome");
  } else if (id === "config_aluno") {
    const nome = extract_info(obj_click, "nome");
    const pos = obj_click.querySelector("span").textContent;
    let turno = "Matutino";
    let contraturno = false;
    if (obj_click.id.includes("Vespertino")) {
      turno = "Vespertino";
    } else if (obj_click.id.includes("Noturno")) {
      turno = "Noturno";
    }
    if (obj_click.id.includes("contraturno")) {
      contraturno = true;
    }
    const name_point = document.getElementById("config_point_nome");
    config_popup_aluno(nome, turno, pos, contraturno, name_point);
  } else if (id === "config_point") {
    config_popup_point(extract_info(obj_click, "nome"));
  } else if (id === "config_route") {
    config_popup_route(obj_click);
    document.getElementById("config_route_pos").textContent =
      obj_click.querySelector("span").textContent;
  } else if (id === "config_line") {
    card.querySelector("h1").textContent = extract_info(obj_click, "nome");
    card.querySelector("p#config_line_cidade").textContent = extract_info(
      obj_click,
      "cidade"
    );
    const options_ferias = document.getElementById(
      "config_line_options_ferias"
    );
    const options_gratuidade = document.getElementById(
      "config_line_options_gratuidade"
    );
    const info_ferias = document.getElementById("interface_ferias");
    const area_paga = document.getElementById("area_paga");

    if (info_ferias.className.includes("inactive")) {
      config_bool(options_ferias, "Não");
    } else {
      config_bool(options_ferias, "Sim");
    }

    if (area_paga.className.includes("inactive")) {
      config_bool(options_gratuidade, "Não");
    } else {
      config_bool(options_gratuidade, "Sim");
    }
  } else if (id === "add_vehicle" || id === "add_route") {
    const data = {
      principal: [document.getElementById("interface_nome").textContent],
      secondary: {},
    };
    const container = card.querySelector(
      "div#" + popup.id + "_options_container"
    );
    container.innerHTML = "";
    const option = id === "add_vehicle" ? "option_driver" : "option_vehicle";
    include_options_container(container, option, data);
  } else if (
    id === "promover_motorista" ||
    id === "rebaixar_motorista" ||
    id === "del_ponto" ||
    id === "del_linha"
  ) {
    card.querySelector("h2").textContent = extract_info(obj_click, "nome");
  } else if (id === "del_vehicle") {
    document.getElementById("del_vehicle_surname").textContent = extract_info(
      obj_click,
      "surname"
    );
  } else if (id === "config_relacao_ponto_rota") {
    card.querySelector(`p#${popup.id}_nome`).textContent = extract_info(
      obj_click,
      "nome"
    );
    card.querySelector(`p#${popup.id}_ordem`).textContent = extract_info(
      obj_click,
      "number"
    );
    card.querySelector(`p#${popup.id}_horario`).textContent = extract_info(
      obj_click,
      "horario"
    );
  } else if (id === "edit_route_onibus") {
    const data = {
      principal: [document.getElementById("interface_nome").textContent],
      secondary: { surname_ignore: extract_info(obj_click, "onibus") },
    };
    const container = document.getElementById(id + "_container");
    container.innerHTML = "";

    let option_nenhum = true;
    if (data.secondary.surname_ignore === "Não definido") {
      option_nenhum = false;
    }
    include_options_container(container, "option_vehicle", data, option_nenhum);
  } else if (id === "add_point_route") {
    const container = document.getElementById(id + "_container");
    const data = return_data_route(null, (format_dict_url = true));

    let tipo = obj_click.id.trim().split("_");
    tipo = tipo[tipo.length - 1];

    data["principal"].push(tipo);
    container.innerHTML = "";
    popup.querySelector("span").textContent = tipo;
    include_options_container(container, "option_point", data, false);
  } else if (id === "config_rel_point_route") {
    const data = return_data_route(null, (format_dict_url = true));
    data.principal.push(
      obj_click.id.includes("partida") ? "partida" : "retorno"
    );
    data.principal.push(extract_info(obj_click, "nome"));
    document.getElementById("config_rel_point_route_ordem").textContent =
      extract_info(obj_click, "number");
    config_popup_relationship(data);
  } else if (id === "edit_vehicle_surname") {
    const surname = extract_info(obj_click, "surname");
    popup.querySelector("span").textContent = surname;
    card.querySelector(
      "h2"
    ).textContent = `Defina o novo apelido de ${surname}:`;
  } else if (id === "aparence_vehicle") {
    const surname_vehicle = extract_info(obj_click, "surname");
    document.getElementById("aparence_vehicle_surname").textContent =
      surname_vehicle;
    config_popup_aparence(surname_vehicle);
  } else if ("vehicle_utilities_routes") {
    const surname_vehicle = extract_info(obj_click, "surname");
    document.getElementById("vehicle_utilities_routes_surname").textContent =
      surname_vehicle;
    config_popup_routes_vehicle(surname_vehicle);
  }
}

function loadInterfacePoints(name_line) {
  fetch(`/get_interface-points/${encodeURIComponent(name_line)}`, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const model = models.querySelector("#interface_model_ponto");
        const local_pontos = document.getElementById("interface_pontos_local");
        const division = document.getElementById("interface_pontos_division");
        const add_ponto = document.getElementById("interface_pontos_add");

        const relacao = response.relacao;
        const data = response.data;

        local_pontos.innerHTML = "";
        document.getElementById("interface_pontos_quantidade").textContent =
          response.quantidade;
        division.classList.add("inactive");
        add_ponto.classList.add("inactive");
        if (data.length) {
          if (relacao && relacao !== "membro") {
            division.classList.remove("inactive");
            add_ponto.classList.remove("inactive");
          }

          for (index in data) {
            const ponto = model.cloneNode(true);
            ponto.id = `${local_pontos.id}-ponto_${index}`;
            const text = ponto.querySelector("p");
            text.textContent = data[index];
            text.id = ponto.id + "_nome";

            if (relacao) {
              ponto.onclick = function () {
                open_popup("config_point", this);
              };
              ponto.querySelector("i").classList.remove("inactive");
              ponto.classList.add("grow");
            }

            ponto.classList.remove("inactive");
            local_pontos.appendChild(ponto);
          }
        } else {
          if (relacao && relacao !== "membro") {
            add_ponto.classList.remove("inactive");
          }
        }
      } else {
        create_popup(response.title, response.text, "Voltar");
      }
    });
}

function loadInterfaceStudents(name_line) {
  const model_aluno = models.querySelector("#interface_model_aluno");
  fetch(`/get_interface-students/${encodeURIComponent(name_line)}`, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        document.getElementById("interface_alunos_quant").textContent =
          response.quantidade;
        const data = response.data;

        for (shift in data) {
          document.getElementById(
            `interface_alunos_${shift}_quantidade`
          ).textContent = data[shift].quantidade;
          const container = document.getElementById(
            `interface_alunos_${shift}_container`
          );
          const alunos = data[shift].alunos;
          criar_aluno(alunos, container, response, model_aluno);
        }
      } else {
        create_popup(response.title, response.text, "Voltar");
      }
    });
}

function criar_aluno(list_aluno, container, response, model_aluno) {
  container.innerHTML = "";

  for (index in list_aluno) {
    const aluno = model_aluno.cloneNode(true);
    aluno.id = `${container.id}-aluno_${index}`;
    const nome = aluno.querySelector("p");
    nome.textContent = list_aluno[index];
    nome.id = aluno.id + "_nome";

    if (index) {
      if (list_aluno[index - 1] === nome.textContent) {
        const aluno_ant = document.getElementById(
          `${container.id}-aluno_${index - 1}`
        );
        const span_ant = aluno_ant.querySelector("span");
        if (!span_ant.textContent) {
          span_ant.textContent = 0;
        }
        aluno.querySelector("span").textContent =
          parseInt(span_ant.textContent) + 1;
      }
    }

    if (response.relacao !== "membro") {
      aluno.classList.add("grow");
      aluno.querySelector("i").classList.remove("inactive");
      aluno.onclick = function () {
        open_popup("config_aluno", this);
      };
    }
    aluno.classList.remove("inactive");
    container.appendChild(aluno);
  }
}

function config_popup_point(name_point) {
  const name_line = document.getElementById("interface_nome").textContent;
  const get = { principal: [name_line, name_point] };
  const model_aluno = models.querySelector("#interface_model_aluno");

  fetch("/get_point" + generate_url_dict(get), { method: "GET" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const data = response.info;
        const utilizacao = response.utilizacao;
        const turnos = response.turnos;

        for (info in data) {
          const local = document.getElementById("config_point_" + info);
          local.textContent = data[info];

          if (response.relacao !== "membro") {
            document
              .getElementById(local.id + "_edit")
              .classList.remove("inactive");
          }
        }

        document
          .getElementById("config_point_utilizacao_btn")
          .querySelector("p").textContent = utilizacao.quantidade;
        const utilizacao_container = document.getElementById(
          "config_point_utilizacao_container"
        );
        criar_rota(utilizacao.rotas, utilizacao_container, true);

        for (turno in turnos) {
          const btn = document.getElementById(`config_point_${turno}_btn`);
          const container_turno = document.getElementById(
            `config_point_${turno}_area`
          );
          const container_contraturno = document.getElementById(
            `config_point_${turno}_area_contraturno`
          );

          const info = turnos[turno];
          btn.querySelector("p").textContent = info.quantidade;
          criar_aluno(info.alunos, container_turno, response, model_aluno);
          criar_aluno(
            info.contraturno,
            container_contraturno,
            response,
            model_aluno
          );
        }
      } else {
        close_popup("config_point");
        create_popup(response.title, response.text, "Voltar");
      }
    });
}

function config_popup_aluno(nome, turno, pos, contraturno, name_point = false) {
  const name_line = document.getElementById("interface_nome").textContent;
  const secondary = {};
  if (name_point) {
    secondary.name_point = name_point.textContent;
  }
  if (contraturno) {
    secondary.contraturno = true;
  }
  if (pos) {
    secondary.pos = pos;
  }
  const data = {
    principal: [name_line, turno, nome],
    secondary: secondary,
  };

  fetch("/get_student" + generate_url_dict(data), { method: "GET" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const data = response.data;
        for (info in data) {
          document.getElementById(`config_aluno_${info}`).textContent =
            data[info];
        }
      } else {
        close_popup("config_aluno");
        create_popup(response.title, response.text, "Voltar");
      }
    });
}

function set_sequence(obj_child) {
  const container = obj_child.parentNode;
  elements = Array.from(container.children);
  elements.forEach((element, index) => {
    const tag_sequence = element.querySelector('[id*="number"]');
    tag_sequence.textContent = index + 1;
  });
}

$(function () {
  $(".sortable").sortable({
    handle: ".icon_move",
    tolerance: "pointer",
    forcePlaceholderSize: true,

    start: function (event, ui) {
      var icon = ui.item.find("i");
      var number = ui.item.find("h4");
      var text = ui.item.find("p");

      icon.addClass("shadow");
      icon.addClass("grabbing");
      number.addClass("shadow");
      text.addClass("shadow");
    },
    stop: function (event, ui) {
      var icon = ui.item.find("i");
      var number = ui.item.find("h4");
      var text = ui.item.find("p");

      set_sequence(ui.item[0]);
      icon.removeClass("grabbing");
      setTimeout(() => {
        icon.removeClass("shadow");
        number.removeClass("shadow");
        text.removeClass("shadow");
      }, 400);
    },
  });
});
