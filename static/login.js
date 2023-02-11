$(document).ready(() => {
  $('#eye_icon').on('click', () => {
    togglePassword();
  })
})

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

// 비밀번호 보임/숨김 함수
function togglePassword() {
  $('#eye_icon').toggleClass('active');
  if ($('#eye_icon').hasClass('active')) {
    $('#eye_icon').attr('src', "../static/img/eye_look.png")
      .prev('#user_pwd_input').attr('type', "text");
  } else {
    $('#eye_icon').attr('src', "../static/img/eye_hide.png")
      .prev('#user_pwd_input').attr('type', "password");
  }
}