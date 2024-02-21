templates = document.getElementById("templates_model");
models = document.importNode(templates.content, true);

function loadInterfaceLine(name_line, load_complete = true) {
  fetch(`/get_interface-line/${encodeURIComponent(name_line)}`, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        let adm = false;
        const aviso_entrada = document.getElementById("interface_line_enter");
        aviso_entrada.classList.add("inactive");

        if (response.role === "motorista") {
          const config_linha = document.getElementById("interface_config");
          config_linha.classList.add("inactive");

          if (response.relacao) {
            if (response.relacao === "dono") {
              config_linha.classList.remove("inactive");
              adm = true;
            } else if (response.relacao === "adm") {
              adm = true;
            }
          } else {
            aviso_entrada.classList.remove("inactive");
          }
        } else {
          if (!response.relacao || response.relacao === "não participante") {
            aviso_entrada.classList.remove("inactive");
          }
        }

        for (dado in response.data) {
          if (dado === "paga") {
            const area_paga = document.getElementById("area_paga");
            if (!response.data[dado]) {
              area_paga.classList.add("inactive");
            } else {
              area_paga.classList.remove("inactive");
            }
          } else if (dado === "ferias") {
            const info_ferias = document.getElementById("interface_ferias");
            if (!response.data[dado]) {
              info_ferias.classList.add("inactive");
            } else {
              info_ferias.classList.remove("inactive");
            }
          } else {
            const info = document.getElementById(`interface_${dado}`);
            const edit = document.getElementById(
              info.id.replace("interface", "edit")
            );
            info.textContent = response.data[dado];

            if (edit) {
              if (adm) {
                edit.classList.remove("inactive");
              } else {
                edit.classList.add("inactive");
              }
            }
          }
        }

        if (load_complete) {
          loadInterfaceDriver(name_line);
          if (response.role === "motorista") {
            loadInterfaceVehicle(name_line);
            loadInterfacePoints(name_line);
          }
          loadInterfaceRoutes(name_line);
        }
      } else {
        create_popup(response.title, response.text, "Voltar");
      }
      const elements = document.querySelectorAll('[class*="-enter-"]');
      animate_itens(elements, "fadeDown", 0.6, 0.2);
    });
}

function loadInterfaceDriver(name_line) {
  fetch(`/get_interface-driver/${encodeURIComponent(name_line)}`, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const data = response.data;
        const local_motorista = document.getElementById("area_motoristas");
        const elements_remove = Array.from(local_motorista.children);
        elements_remove.forEach((element) => {
          if (element.id.includes("motorista")) {
            local_motorista.removeChild(element);
          }
        });

        const model_motorista = models.querySelector("#model_motorista");
        for (tipo in data) {
          for (pos in data[tipo]) {
            const motorista = model_motorista.cloneNode(true);
            motorista.id = `motorista_${tipo}-${pos}`;

            const ids = motorista.querySelectorAll('[id*="model_motorista"]');
            ids.forEach((element) => {
              element.id = element.id.replace("model_motorista", motorista.id);
            });
            for (info in data[tipo][pos]) {
              const tag = motorista.querySelector(`[id*="${info}"]`);
              tag.textContent = data[tipo][pos][info];
            }

            const dono = motorista.querySelector('[id*="dono"]');
            const adm = motorista.querySelector('[id*="adm"]');
            if (response.role === "motorista") {
              if (response.relacao === "dono" && tipo !== "dono") {
                const btn_config = motorista.querySelector('[id*="btn"]');
                btn_config.classList.remove("inactive");
              }
            }
            if (tipo === "dono") {
              dono.classList.remove("inactive");
              adm.classList.remove("inactive");
            } else if (tipo === "adm") {
              adm.classList.remove("inactive");
            }

            motorista.classList.remove("inactive");
            local_motorista.appendChild(motorista);
          }
        }
      } else {
        create_popup(response.title, response.text, "Voltar");
      }
    });
}

function adicionar_veiculo(model, list, container) {}

function loadInterfaceVehicle(name_line) {
  fetch(`/get_interface-vehicle/${encodeURIComponent(name_line)}`, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const model_vehicle = models.querySelector('model')
      } else {
        create_popup(response.title, response.text);
      }
    });
}

function loadInterfaceRoutes(name_line) {
  const model_route = models.querySelector("#model_interface_rota");
  function load_route(list_itens, container_include) {
    for (index in list_itens) {
      const route = model_route.cloneNode(true);
      route.id = `${container_include.id}-rota_${index}`;

      ids = route.querySelectorAll(`[id*="${model_route.id}"]`);
      ids.forEach((element) => {
        element.id = element.id.replace(model_route.id, route.id);
      });

      const dados = list_itens[index];
      for (dado in dados) {
        const info = route.querySelector(`[id*="${dado}"]`);
        info.textContent = dados[dado];
      }

      if (index) {
        let qnt = 0;
        const dados_ant = list_itens[index - 1];
        for (num in dados_ant) {
          if (dados_ant[num] === dados[num]) {
            qnt++;
          }
        }

        if (qnt === Object.keys(dados).length) {
          const route_ant = document.getElementById(
            `${container_include.id}-rota_${index - 1}`
          );
          const span_ant = route_ant.querySelector("span");
          if (!span_ant.textContent) {
            span_ant.textContent = 0;
          }
          route.querySelector("span").textContent =
            parseInt(span_ant.textContent) + 1;
        }
      }
      route.classList.remove("inactive");
      container_include.appendChild(route);
    }
  }

  fetch(`/get_interface-routes/${encodeURIComponent(name_line)}`, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const local_ativas = document.getElementById("interface_rotas_ativas");
        const ativas = response.ativas;

        local_ativas.innerHTML = "";
        if (response.role == "motorista") {
          const local_desativas = document.getElementById(
            "interface_rotas_desativas"
          );
          const division_desativas = document.getElementById(
            "interface_rotas_desativas_division"
          );
          const title_desativas = document.getElementById(
            "interface_rotas_desativas_title"
          );
          const desativas = response.desativas;

          local_desativas.innerHTML = "";
          local_desativas.classList.add("inactive");
          division_desativas.classList.add("inactive");
          title_desativas.classList.add("inactive");

          document.getElementById("interface_rotas_quantidade").textContent =
            response.quantidade;
          const route_division = document.getElementById(
            "interface_rotas_division"
          );
          const route_add = document.getElementById("interface_rotas_add");

          route_division.classList.add("inactive");
          route_add.classList.add("inactive");

          if (response.relacao && response.relacao !== "membro") {
            route_add.classList.remove("inactive");
            if (ativas.length || desativas.length) {
              route_division.classList.remove("inactive");
            }
          }
          if (desativas.length) {
            local_desativas.classList.remove("inactive");
            division_desativas.classList.remove("inactive");
            title_desativas.classList.remove("inactive");
          }
          load_route(desativas, local_desativas);
        }
        load_route(ativas, local_ativas);
      } else {
        create_popup(response.title, response.text, "Voltar");
      }
    });
}

function config_popup_route(obj_click, data = false) {
  if (!data) {
    data = return_data_route(obj_click, (format_dict_url = true));
  }
  document.getElementById("config_route_pos").textContent = data.pos;
  close_popup("config_point");

  fetch("/get_route" + generate_url_dict(data), { method: "GET" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const msg_desativada = document.getElementById(
          "config_route_desativada"
        );
        const data = response.data;
        const information = response.info;
        const role = response.role;
        const relacao = response.relacao;

        msg_desativada.classList.add("inactive");
        if (response.msg_desativada) {
          msg_desativada.classList.remove("inactive");
        }

        if (role === "aluno") {
          const msg_cadastrar = document.getElementById(
            "config_route_aviso_cadastrar"
          );
          const msg_contraturno = document.getElementById(
            "config_route_aviso_contraturno"
          );
          const btn_contraturno = document.getElementById(
            "config_route_btn_contraturno"
          );

          msg_cadastrar.classList.add("inactive");
          msg_contraturno.classList.add("inactive");
          btn_contraturno.classList.add("inactive");
          if (response.msg_cadastrar) {
            msg_cadastrar.classList.remove("inactive");
          }

          if (response.msg_contraturno) {
            msg_contraturno.classList.remove("inactive");
            btn_contraturno.classList.remove("inactive");
          }
        } else {
          const route_division = document.getElementById("route_division");
          const route_del = document.getElementById("route_del");

          if (relacao && relacao !== "membro") {
            route_division.classList.remove("inactive");
            route_del.classList.remove("inactive");
          } else {
            route_division.classList.add("inactive");
            route_del.classList.add("inactive");
          }
        }

        const popup = document.getElementById("config_route");
        for (nome in information) {
          const value = information[nome];
          const info = popup.querySelector(`[id*="${nome}"]`);
          info.textContent = value;
          if (role == "motorista") {
            const icon = info.parentNode.querySelector("i");
            if (icon) {
              if (relacao && relacao !== "membro") {
                icon.classList.remove("inactive");
              } else {
                icon.classList.add("inactive");
              }
            }
          }
        }

        const model_relacao = models.querySelector(
          "#interface_model_option_headli"
        );
        for (nome in data) {
          const tipo = data[nome];
          const paradas = tipo.paradas;
          const btn_aba = document.getElementById(
            `config_route_pontos_container_${nome}_btn`
          );
          const container = popup.querySelector(`[id*="${nome}_area"]`);
          container.innerHTML = "";

          if (return_btn_open(btn_aba)) {
            action_container(btn_aba);
          }
          if (role === "motorista") {
            const area_division = container.parentNode.querySelector("h1");
            const area_add = container.parentNode.querySelector("div.justify");

            area_division.classList.add("inactive");
            area_add.classList.add("inactive");
            if (relacao && relacao !== "membro") {
              area_add.classList.remove("inactive");
              if (paradas.length) {
                area_division.classList.remove("inactive");
              }
            }
          }

          popup.querySelector(`[id*="quantidade_${nome}"]`).textContent =
            tipo.quantidade;
          for (index in paradas) {
            const relacao = model_relacao.cloneNode(true);
            relacao.id = `${container.id}-relacao_${index}`;

            ids = relacao.querySelectorAll(`[id*="${model_relacao.id}"]`);
            ids.forEach((element) => {
              element.id = element.id.replace(model_relacao.id, relacao.id);
            });

            dados = paradas[index];
            for (dado in dados) {
              const value = dados[dado];
              relacao.querySelector(`[id*="${dado}"]`).textContent = value;
            }

            if (role === "motorista") {
              icon = relacao.querySelector("i");
              icon.classList.add("inactive");
              if (relacao && relacao !== "membro") {
                icon.classList.remove("inactive");
              }
            } else {
              if (response.meu_turno === information.turno_rota) {
                relacao.onclick = function () {
                  open_popup("config_rel_point_route", this);
                };
              } else {
                relacao.onclick = function () {
                  create_popup(
                    "Comunicado",
                    'Olá! Esta rota não pertence ao seu turno, portanto, seus pontos fixos estão disponíveis apenas para visualização. Se desejar definir um ponto como contraturno, selecione o botão "Definir contraturno".',
                    "Ok",
                    "warning",
                    "",
                    "#1468d6"
                  );
                };
              }
            }

            relacao.classList.remove("inactive");
            container.appendChild(relacao);
          }
        }
      } else {
        close_popup("config_route");
        create_popup(response.title, response.text, "Voltar");
      }
    });
}

function config_popup_relationship(data) {
  fetch("/get_relationship-point" + generate_url_dict(data), { method: "GET" })
    .then((response) => response.json())
    .then((response) => {
      const data = response.data;

      for (dado in data) {
        const value = data[dado];
        const info = document.getElementById(`config_rel_point_route_${dado}`);
        info.textContent = value;

        if (response.role == "motorista") {
          const icon = info.parentNode.querySelector("i");
          if (icon) {
            if (response.relacao && response.relacao !== "membro") {
              icon.classList.remove("inactive");
            } else {
              icon.classList.add("inactive");
            }
          }
        }
      }

      if (response.role === "motorista") {
        const model_aluno = models.querySelector("#interface_model_aluno");
        const cadastrados = response.cadastrados;
        for (tipo in cadastrados) {
          document.getElementById(
            `config_rel_point_route_${tipo}_quantidade`
          ).textContent = cadastrados[tipo].quantidade;
          const alunos = cadastrados[tipo].alunos;
          const container = document.getElementById(
            `config_rel_point_route_${tipo}_container`
          );
          create_aluno(alunos, container, model_aluno);
        }

        const division = document.getElementById(
          "config_rel_point_route_division"
        );
        const del = document.getElementById("config_rel_point_route_del");

        division.classList.add("inactive");
        del.classList.add("inactive");
        if (response.relacao && response.relacao !== "membro") {
          division.classList.remove("inactive");
          del.classList.remove("inactive");
        }
      } else {
        const btn_cadastrar = document.getElementById(
          "config_rel_point_route_cadastrar"
        );
        const btn_sair = document.getElementById("config_rel_point_route_sair");

        btn_cadastrar.classList.add("inactive");
        btn_sair.classList.add("inactive");
        if (response.cadastrado) {
          btn_sair.classList.remove("inactive");
        } else {
          btn_cadastrar.classList.remove("inactive");
        }
      }
    });
}

function return_data_route(obj_model = false, format_dict_url = false) {
  const name_line = document.getElementById("interface_nome").textContent;
  if (obj_model) {
    var surname = extract_info(obj_model, "surname");
    var shift = extract_info(obj_model, "turno");
    var time_par = extract_info(obj_model, "horario_partida");
    var time_ret = extract_info(obj_model, "horario_retorno");
    var pos = obj_model.querySelector("span").textContent;
  } else {
    var surname = document.getElementById("config_route_onibus").textContent;
    var shift = document.getElementById("config_route_turno_rota").textContent;
    var time_par = document.getElementById(
      "config_route_horario_partida"
    ).textContent;
    var time_ret = document.getElementById(
      "config_route_horario_retorno"
    ).textContent;
    var pos = document.getElementById("config_route_pos").textContent;
    console.log(pos);
  }

  if (format_dict_url) {
    return {
      principal: [name_line, surname, shift, time_par, time_ret],
      secondary: pos ? { pos: pos } : {},
    };
  }
  return {
    name_line: name_line,
    surname: surname,
    shift: shift,
    time_par: time_par,
    time_ret: time_ret,
    pos: pos,
  };
}
