function check_register() {
  let user_id = $('#user_id_input').val()
  let user_pwd = $('#user_pwd_input').val()
  let re_user_pwd = $('#re_user_pwd_input').val()
  let user_phone = $('#user_phone_input').val()
  let regExp_phone = phone_certifi(user_phone)
  let check_id = check_user_id(user_id)['responseJSON']['result'] //user_id가 이미 존재 하는 것이 아닌지 check
  let check_phone = check_user_phone(user_phone)['responseJSON']['result']

  if (user_id == ""){
    alert("사용하실 아이디를 입력해 주세요!!")
  } else if (user_pwd == ""){
    alert("사용하실 비밀번호를 입력해 주세요!!")
  } else if (user_pwd != re_user_pwd){
    alert("비밀번호 재확인란에 동일한 비밀번호를 입력해 주세요!!")
  } else if (user_phone == ""){
    alert("사용자의 휴대전화 번호를 입력해 주세요!!")
  } else if (!regExp_phone) {
    alert("휴대폰 번호를 다시 확인해 주세요!!")
    return
  } else if (check_id == 'fail') {
    alert("이미 존재하는 아이디 입니다!!")
    return
  } else if (check_phone == 'fail') {
    alert("동일한 전화번호가 이미 등록되어 있습니다!!")
    return
  } else {
    register()
  }
}

function register() {
  let user_id = $('#user_id_input').val()
  let user_pwd = $('#user_pwd_input').val()
  let user_phone = $('#user_phone_input').val()
  
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

//폰 번호의 중복이 있는지 check하는 함수
function check_user_phone(user_phone) {
  return $.ajax({
    type: 'GET',
    url: '/user/user_phone_check?user_phone=' + user_phone,
    data: {},
    async: false,
    success: function (response) {
    }
  });
}

function phone_certifi(user_phone) {
  let regex = /^(01[016789]{1})([0-9]{3,4})([0-9]{4})$/
  let result = regex.test(user_phone) ? true : false
  return result
}