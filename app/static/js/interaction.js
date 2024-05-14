const templates_popup = document.getElementById("templates_popup");
const local_popup = document.getElementById("popup_local");
const list_inputs = document.querySelectorAll("input");

function set_animate_label(list_inputs, local = false) {
  list_inputs.forEach((input) => {
    let label = document.querySelector(`label[for="${input.id}"]`);
    let icon = document.getElementById(`icon_${input.id}`);

    if (local) {
      label = local.querySelector(`label[for="${input.id}"]`);
      icon = local.querySelector(`#icon_${input.id}`);
    }
    let inFocus = false;

    function verify() {
      if (inFocus) {
        input.classList.remove("input_error");
        if (label) {
          label.classList.add("selected");
        }
        if (icon) {
          icon.classList.add("selected");
        }
        if (input.type === "time") {
          input.classList.add("visible");
        }
      } else {
        if (input.value.trim() === "") {
          input.value = "";
          if (label) {
            label.classList.remove("selected");
          }
          if (icon) {
            icon.classList.remove("selected");
          }
          if (input.type === "time") {
            input.classList.remove("visible");
          }
        } else {
          if (label) {
            label.classList.add("selected");
          }
          if (icon) {
            icon.classList.add("selected");
          }
          if (input.type === "time") {
            input.classList.add("visible");
          }
        }
      }
    }
    input.addEventListener("focus", function () {
      inFocus = true;
    });
    input.addEventListener("blur", function () {
      inFocus = false;
    });
    setInterval(verify, 100);
  });
}
set_animate_label(list_inputs);

const inputs_tell = document.querySelectorAll('[class*="format_tell"]');
function set_valid_tell(inputs_tell) {
  inputs_tell.forEach((input) => {
    input.addEventListener("input", () => {
      let digits = input.value.replace(/\D/g, "").substring(0, 11);
      let num = digits.split("");

      let tell_formated = "";
      if (num.length > 0) {
        tell_formated += `${num.slice(0, 2).join("")}`;
      }
      if (num.length > 2) {
        tell_formated = `(${tell_formated}) ${num.slice(2, 7).join("")}`;
      }
      if (num.length > 7) {
        tell_formated += `-${num.slice(7).join("")}`;
      }
      input.value = tell_formated;
    });
  });
}
set_valid_tell(inputs_tell);

const inputs_name = document.querySelectorAll('[class*="format_name"]');
function set_valid_name(inputs_name) {
  inputs_name.forEach((input) => {
    input.addEventListener("input", () => {
      input.value = input.value.replace(
        /[^a-zA-ZàáâãçéêíîóôõúüÀÁÂÃÇÉÊÍÎÓÔÕÚÜ\s]/g,
        ""
      );
    });
  });
}
set_valid_name(inputs_name);

const inputs_options = document.querySelectorAll('[class*="format_options"]');
function set_input_options(inputs_options) {
  function ajust_text(list, input) {
    const value = input.value
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase();
    list.forEach((element) => {
      const text = element.textContent
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase();
      element.classList.toggle("inactive", !text.includes(value));
    });
  }

  inputs_options.forEach((input) => {
    const list_options = input.parentNode.parentNode.querySelector("ul");
    const elements = list_options.querySelectorAll("li");
    animate_itens(elements);

    elements.forEach((li) => {
      li.addEventListener("mouseenter", () => {
        input.value = li.textContent;
      });
    });

    input.addEventListener("input", () => {
      ajust_text(elements, input);
    });

    input.addEventListener("focus", () => {
      input.classList.add("option_focus");
      list_options.classList.remove("inactive");
      list_options.scrollTop = 0;
      ajust_text(elements, input);
    });

    input.addEventListener("blur", () => {
      input.classList.remove("option_focus");
      list_options.classList.add("inactive");

      elements.forEach((element) => {
        element.classList.remove("inactive");
      });
    });
  });
}
set_input_options(inputs_options);

const forms = document.querySelectorAll("form");
function set_submit_form(forms) {
  forms.forEach((form) => {
    form.addEventListener("keyup", function (event) {
      if (event.key === "Enter") {
        submit(form.id);
      }
    });
  });
}
set_submit_form(forms);
set_observerScroll(document.querySelectorAll("form.scroll_vertical"));

function createObserver(root = null, range_visibility = 0.2) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          entry.target.classList.remove("hidden");
        } else {
          entry.target.classList.remove("visible");
          entry.target.classList.add("hidden");
        }
      });
    },
    {
      root: root,
      rootMargin: "0px",
      threshold: range_visibility,
    }
  );
  return observer;
}

function create_popup(
  title,
  text = "",
  text_buttom = "Ok",
  icon = "warning",
  redirect = "",
  color = ""
) {
  document.body.classList.add("no-scroll");
  Swal.fire({
    title: title,
    html: `<p${
      text.split(" ").length > 12 ? ' style="text-align: justify;"' : ""
    }>${text}</p>`,
    icon: icon,
    width: "80%",
    confirmButtonText: text_buttom,
    confirmButtonColor: "#004aad",
    iconColor: color
      ? color
      : `${
          icon === "warning"
            ? "#ffe646"
            : icon === "success"
            ? "#0aa999"
            : "#ff7272"
        }`,
  }).then(() => {
    const itens = local_popup.querySelectorAll("section");
    if (!itens.length) {
      document.body.classList.remove("no-scroll");
    }
    if (redirect) {
      window.location.href = "/" + redirect;
    }
  });
}

function set_observerScroll(list_obj) {
  for (let index = 0; index < list_obj.length; index++) {
    const observer = createObserver(list_obj[index], 0.15);
    let elements_animate = list_obj[index];
    elements_animate = elements_animate.querySelectorAll("div.hidden");
    elements_animate.forEach((element) => {
      observer.observe(element);
    });
  }
}

function action_container(
  obj_click,
  set_limit = false,
  visible_contante_scroll = true
) {
  const icon = obj_click.querySelector("i");
  const container = document.getElementById(
    obj_click.id.replace("btn", "container")
  );
  const elements = Array.from(container.children);
  obj_click.style.transition = "0s ease";
  container.removeAttribute("style");

  if (obj_click.id.includes("vehicle")) {
    const motorista_nome = obj_click.querySelectorAll("h3");
    motorista_nome.forEach((element, index) => {
      if (!index) {
        if (icon.className.includes("open")) {
          element.classList.remove("max_width");
        } else {
          element.classList.add("max_width");
        }
      } else {
        if (icon.className.includes("open")) {
          element.classList.remove("inactive");
        } else {
          element.classList.add("inactive");
        }
      }
    });
  }

  animate_itens(elements);
  if (icon.className.includes("open")) {
    container.classList.add("inactive");
    icon.classList.remove("open");

    elements.forEach((element) => {
      element.classList.remove("selected");
    });
  } else {
    container.classList.remove("inactive");
    container.scrollTop = 0;
    icon.classList.add("open");

    if (visible_contante_scroll) {
      if (container.className.includes("scroll")) {
        if (set_limit) {
          set_limitScroll(container, set_limit);
        } else {
          set_limitScroll(container);
        }
      }
    }
  }

  const btn_children = container.querySelectorAll('[id*="btn"]');
  if (btn_children) {
    btn_children.forEach((btn) => {
      const icon = btn.querySelector("i");
      if (icon.className.includes("open")) {
        action_container(btn);
      }
    });
  }

  if (visible_contante_scroll) {
    elements.forEach((element) => {
      if (element.className.includes("scroll")) {
        element.scrollTop = 0;
        element.classList.remove("inactive");
        animate_itens(Array.from(element.children));
        set_limitScroll(element, set_limit ? set_limit : 30);
      }
    });
  }
}

function animateIconPassword(obj_click) {
  const container_password = obj_click.parentNode;
  const iconPassword = container_password.querySelector('[id*="btn"]');
  const inputPassword = container_password.querySelector("input");

  if (inputPassword.type === "password") {
    iconPassword.className = inputPassword.className.includes("white")
      ? "bi bi-eye-slash-fill form__btn--password white"
      : "bi bi-eye-slash-fill form__btn--password";
    inputPassword.type = "text";
  } else {
    iconPassword.className = inputPassword.className.includes("white")
      ? "bi bi-eye-fill form__btn--password white"
      : "bi bi-eye-fill form__btn--password";
    inputPassword.type = "password";
  }
}

function popup_enter_animate(popup) {
  const card = popup.querySelector("div.popup__container");
  popup.classList.remove("inactive");
  popup.classList.remove("close");
  card.classList.remove("close");
}

function popup_close_animate(popup) {
  const card = popup.querySelector("div.popup__container");
  card.classList.add("close");
  popup.classList.add("close");

  setTimeout(() => {
    popup.classList.add("inactive");
  }, 200);
}

function open_popup(id, obj_click = false, jquery = true) {
  const popups = document.importNode(templates_popup.content, true);
  const popup = popups.querySelector(`#${id}`);

  if (popup) {
    const card = popup.querySelector("div.popup__container");

    const inputs = popup.querySelectorAll("input");
    set_animate_label(inputs, popup);

    const inputs_tell = popup.querySelectorAll('[class*="format_tell"]');
    set_valid_tell(inputs_tell);

    const inputs_name = popup.querySelectorAll('[class*="format_name"]');
    set_valid_name(inputs_name);

    const inputs_options = popup.querySelectorAll('[class*="format_options"]');
    set_input_options(inputs_options);

    const forms = popup.querySelectorAll("form");
    set_submit_form(forms);

    const list = Array.from(local_popup.children);
    list.forEach((item) => popup_close_animate(item));

    local_popup.appendChild(popup);
    document.body.classList.add("no-scroll");
    setTimeout(() => {
      popup_enter_animate(popup);
    }, 55);

    if (jquery && !window.location.href.includes("profile")) {
      $(function () {
        $(".sortable").each(function () {
          setSortable($(this));
        });
      });
    }

    if (obj_click) {
      action_popup(popup, card, id, obj_click);
    }
  }
}

function close_popup(id) {
  const popup = local_popup.querySelector(`#${id}`);
  if (popup) {
    popup_close_animate(popup);

    const itens = local_popup.querySelectorAll("section");
    if (itens.length === 1) {
      document.body.classList.remove("no-scroll");
    }

    const list = Array.from(local_popup.children);
    if (list.length >= 2) {
      setTimeout(() => {
        popup_enter_animate(list[list.length - 2]);
      }, 55);
    }

    setTimeout(() => {
      local_popup.removeChild(popup);
    }, 160);
    copy_text();
  }
}

function config_bool(container_options, reference = "Sim") {
  const icon_selected = container_options.querySelector("i.selected");
  const text_selected = icon_selected.parentNode.querySelector("p").textContent;
  const option = container_options.querySelector("i:not(.selected)").parentNode;
  if (text_selected !== reference) {
    popup_selectOption(option, true);
  }
}

function popup_confirmBox(item) {
  icon = item.querySelector("i");
  if (icon.className.includes("selected")) {
    icon.classList.replace("bi-check2-circle", "bi-circle");
    icon.classList.remove("selected");
  } else {
    icon.classList.replace("bi-circle", "bi-check2-circle");
    icon.classList.add("selected");
  }
}

function popup_selectOption(
  obj_click,
  open_boxOptions = false,
  multiple_options = false
) {
  const reference = obj_click.parentNode;
  const reference_elements = Array.from(reference.children);
  const text = obj_click.querySelector("p");
  const icon = obj_click.querySelector("i");

  if (!multiple_options) {
    if (!icon.className.includes("selected")) {
      reference_elements.forEach((item) => {
        popup_confirmBox(item);
      });
      if (open_boxOptions) {
        const title_options = document.getElementById(`${reference.id}_title`);
        const reference_container = document.getElementById(
          `${reference.id}_container`
        );
        const list_itens = reference_container
          ? reference_container.querySelectorAll("div")
          : false;

        if (text.textContent === "Sim") {
          if (title_options) {
            title_options.classList.remove("inactive");
          }
          if (reference_container) {
            reference_container.classList.remove("inactive");
            reference_container.scrollTop = 0;
            set_limitScroll(reference_container);
            animate_itens(list_itens);
          }
        } else {
          if (reference_container) {
            const options = reference_container.querySelectorAll("div");
            options.forEach((item) => {
              item.classList.remove("selected");
            });
            if (title_options) {
              title_options.classList.add("inactive");
            }
            reference_container.classList.add("inactive");
          }
        }
      }
    }
  } else {
    if (!obj_click.className.includes("selected")) {
      reference_elements.forEach((item) => {
        if (item === obj_click) {
          item.classList.add("selected");
        } else {
          item.classList.remove("selected");
        }
      });
    }
  }
}

function popup_selectOption_span(obj_click, includes_container = []) {
  if (!obj_click.className.includes("selected_intense")) {
    const reference = obj_click.parentNode;
    const reference_elements = Array.from(reference.children);

    reference_elements.forEach((item) => {
      const elements = Array.from(item.querySelector("span").children);
      if (item === obj_click) {
        elements.forEach((element) => {
          element.classList.add("selected_intense");
        });
      } else {
        elements.forEach((element) => {
          element.classList.remove("selected_intense");
        });
      }
    });

    for (index in includes_container) {
      const elements_container = Array.from(includes_container[index].children);
      elements_container.forEach((item) => {
        const elements_item = Array.from(item.querySelector("span").children);
        elements_item.forEach((element) => {
          element.classList.remove("selected_intense");
        });
      });
    }
  }
}

function submit(form_id = false) {
  if (!form_id) {
    const buttom = document.querySelector("button.form__btn--select.selected");
    var form = document.getElementById(
      `form_${buttom.textContent.toLowerCase()}`
    );
  } else {
    var form = document.getElementById(form_id);
  }

  let execute = true;
  const inputs = form.querySelectorAll("input");
  inputs.forEach((input) => {
    if (input.type === "submit") {
      execute = false;
    }
  });

  if (execute) {
    if (form.checkValidity()) {
      form.dispatchEvent(
        new Event("submit", { bubbles: true, cancelable: true })
      );
    } else {
      form.reportValidity();
    }
  }
}

function popup_button_load(popup_id, value = false) {
  const popup = document.getElementById(popup_id);
  if (popup) {
    const footer = popup.querySelector("footer");
    const childrens = Array.from(footer.children);
    if (childrens.length > 1) {
      childrens[1].textContent = value ? value : "Aguarde...";
    } else {
      childrens[0].textContent = value ? value : "Aguarde...";
    }
  }
}

function criar_visualizacao_parada(model, list, container) {
  for (index in list) {
    const parada = model.cloneNode(true);
    parada.id = `${container.id}-parada_${index}`;

    ids = parada.querySelectorAll(`[id*="${model.id}"]`);
    ids.forEach((item) => {
      item.id = item.id.replace(model.id, parada.id);
    });

    const data = list[index];
    for (info in data) {
      const value = data[info];
      const tag = parada.querySelector(`[id*="${info}"]`);
      tag.textContent = value;

      if (info === "data") {
        if (value.includes("fixo")) {
          const icon = parada.querySelector(`#${parada.id}_icon_fixed`);
          icon.classList.remove("inactive");
          icon.classList.add(value.includes("|") ? "verde" : "roxo");
          parada.querySelector(`#${parada.id}_point`).classList.add("fixed");
          tag.parentNode.classList.add("fixed");
        } else if (container.id.includes("diaria")) {
          const icon_redirect = parada.querySelector(
            `#${parada.id}_icon_redirect`
          );
          icon_redirect.classList.remove("inactive");
          icon_redirect.onclick = function () {
            stop_redirect(data.linha);
          };
        }
      }
    }
    parada.classList.remove("inactive");
    container.appendChild(parada);
  }
}

function migrate_capacity(data_route, function_reload) {
  const container = document.getElementById("migrate_capacity_container");
  const selected = return_option_selected(container, true);
  if (selected) {
    data_route.targets = selected.map((item) => item.split(" ")[0]);
    data_route.qnt = document
      .getElementById("migrate_capacity_qnt")
      .value.trim();

    popup_button_load("migrate_capacity");
    fetch("/migrate_capacity", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data_route),
    })
      .then((response) => response.json())
      .then((response) => {
        if (!response.error) {
          function_reload()
          const local_popup = document.getElementById("popup_local");
          local_popup.removeChild(local_popup.querySelector("#notice_migrate"));
          close_popup("migrate_capacity");
          create_popup(response.title, response.text, "Ok", "success");

        } else {
          create_popup(response.title, response.text);
          popup_button_load("migrate_capacity", "Transferir");
        }
      });
  } else {
    create_popup(
      "Nenhum Veículo Selecionado",
      "Você precisa selecionar pelo menos um veículo para transferir a quantidade de usuários desejada."
    );
  }
}

function create_migrate_crowded(local) {
  open_popup("migrate_capacity", false, false);
  let data = null;
  let function_reload = function() {}

  if (local === "page") {
    const popup_route = document.getElementById("summary_route")
    data = return_data_route(popup_route);
    function_reload = function() {
      load_popup_route(popup_route)
    }
  } else if (local === "line") {
    data = return_data_route(null);
  }
  data.type = document.getElementById("notice_migrate_type").textContent;
  data.date = document.getElementById("notice_migrate_date").textContent;
  load_popup_migrate(data.name_line, data.surname);

  const form = document.getElementById("formulario_migrate_capacity");
  form.onsubmit = function (event) {
    event.preventDefault();
    migrate_capacity(data, function_reload);
  };
}
