function register() {
  let user_id = $('#user_id_input').val()
  let user_pwd = $('#user_pwd_input').val()
  let re_user_pwd = $('#re_user_pwd_input').val()
  let user_phone = $('#user_phone_input').val()
  let check_result = check_user_id(user_id)['responseJSON']['result'] //user_id가 이미 존재 하는 것이 아닌지 check
  

  if (user_id == "" || user_pwd == "" || re_user_pwd == "") {
    alert("모든 칸을 입력해 주세요!!")
    return
  } else if (user_pwd != re_user_pwd) {
    alert("비밀번호를 다시 확인해 주세요!")
    return
  } else if (check_result == 'fail') {
    alert("이미 존재하는 아이디 입니다!!")
    return
  }

  $.ajax({
    type: 'POST',
    url: '/user/register',
    data: { user_id_give: user_id, user_pwd_give: user_pwd, user_phone_give: user_phone},
    success: function (response) {
      alert(response['msg'])
      window.location.href = '/'
      // window.location.reload()
    }
  });
}

//user_id의 중복이 있는지 check하는 함수
function check_user_id(user_id) {
  return $.ajax({
    type: 'GET',
    url: '/user/user_id_check?user_id=' + user_id,
    data: {},
    async: false,
    success: function (response) {
    }
  });
}