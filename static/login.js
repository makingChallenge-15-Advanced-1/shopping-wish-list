function login() {
  let user_id = $('#user_id_input').val()
  let user_pwd = $('#user_pwd_input').val()

  if (user_id == "" || user_pwd == "") {
    alert("모든 칸을 입력해 주세요!!")
    return
  }

  $.ajax({
    type: 'POST',
    url: '/user/login',
    data: { user_id_give: user_id, user_pwd_give: user_pwd },
    success: function (response) {
      alert(response['msg'])
      if (response['login'] == true) {
        window.location.href = '/index'
      } else {
        window.location.reload()
      }
    }
  });
}