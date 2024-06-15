function get_data_student(obj_click) {
  const data_route = return_data_route();
  const name_student = obj_click.querySelector("p").textContent;
  const info_local = obj_click.querySelector("h1");

  const secondary = {
    name_point: document
      .getElementById("route_stop_path_local")
      .textContent.trim(),
  };
  if (info_local && info_local.textContent === "Contr...") {
    secondary.contraturno = true;
  }

  const data = {
    principal: [data_route.name_line, data_route.shift, name_student],
    secondary: secondary,
  };

  open_popup("config_aluno");
  fetch("/get_student" + generate_url_dict(data), { method: "GET" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const data_student = response.data;
        for (info in data_student) {
          document.getElementById(`config_aluno_${info}`).textContent =
            data_student[info];
        }
      } else {
        close_popup("config_aluno");
        create_popup(response.title, response.text, "Ok");
      }
    });
}
