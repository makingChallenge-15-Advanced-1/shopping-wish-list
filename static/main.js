var url_verifier = 'false';

$(document).ready(function () {       //페이지 로딩 시 wishlist_get_all() 함수 호출
    wishlist_get_all();
});

// DB 정보를 표시해 주는 함수들
function list_to_card(wishlist) {        //받은 list를 카드로 만들어 화면에 추가해 주는 함수
    for (let i = 0; i < wishlist.length; i++) {
        let image = wishlist[i]['image']
        let url = wishlist[i]['url']
        let name = wishlist[i]['name']
        let memo = wishlist[i]['memo']
        let price = wishlist[i]['price']
        let status = wishlist[i]['status']
        let listId = wishlist[i]['listId']

        let statusClass = ""
        //구매 상태 아이콘 지정
        if (status === 'toBuy') { // 구매예정
            statusClass = "status-toBuy";
        } else if (status === 'hold') { // 구매보류
            statusClass = "status-hold";            
        } else if (status === 'order') { // 구매완료
            statusClass = "status-order";
        }

        temp_html = `
                    <div class="col">
                        <div class="card">
                            <div class="status-bar">
                                <div class="${statusClass}">${status}</div>
                                <input onclick="wishlist_delete(${listId})" type='button' class='btn-del' name='btn' value='삭제하기'>
                                <input onclick="open_modify_box(${listId})" type='button' class='btn-modify' name='btn' value='수정하기'>
                            </div>
                            <div class="embed-responsive embed-responsive-4by3">
                                <a href="${url}" target="_blank">
                                    <img src="${image}" class="card-img-top embed-responsive-item" alt="링크이동">
                                </a>
                            </div>
                            <div class="card-body">
                                <h4 class="card-title">${name}</h4>
                                <p class="card-price" id="card_price">${price}</p>
                                <p class="card-text" id="card_memo">${memo}</p>
                            </div>
                        </div>
                    </div>
                `
        $('#cards_box').append(temp_html)
    }
    return
}

function wishlist_get_all() {                //모든 정보를 보여줌
    $('#cards_box').empty()
    $.ajax({                        //ajax GET으로 list를 읽어와서 카드 생성
        type: 'GET',                //받는 변수 : image, url, name, price, memo, status, listId
        url: '/wishlist?list=all',
        data: {},
        success: function (response) {
            wishlist = response['wishlist']
            list_to_card(wishlist)
        }
    })
}
function wishlist_get_toBuy() {          //당장구매 아이템만 보여줌
    $('#cards_box').empty()
    $.ajax({                        //ajax GET으로 list를 읽어와서 카드 생성
        type: 'GET',                //받는 변수 : image, url, name, price, memo, status, listId
        url: '/wishlist?list=toBuy',
        data: {},
        success: function (response) {
            wishlist = response['wishlist']
            list_to_card(wishlist)
        }
    })
}
function wishlist_get_hold() {          //보류 아이템만 보여줌
    $('#cards_box').empty()
    $.ajax({                        //ajax GET으로 list를 읽어와서 카드 생성
        type: 'GET',                //받는 변수 : image, url, name, price, memo, status, listId
        url: '/wishlist?list=hold',
        data: {},
        success: function (response) {
            wishlist = response['wishlist']
            list_to_card(wishlist)
        }
    })
}
function wishlist_get_order() {          //구매완료 아이템만 보여줌
    $('#cards_box').empty()
    $.ajax({                        //ajax GET으로 list를 읽어와서 카드 생성
        type: 'GET',                //받는 변수 : image, url, name, price, memo, status, listId
        url: '/wishlist?list=order',
        data: {},
        success: function (response) {
            wishlist = response['wishlist']
            list_to_card(wishlist)
        }
    })
}

//alert
function checkedAlert(msg) {
    Swal.fire({
        // position: 'top-end',
        icon: 'success',
        title: msg,
        showConfirmButton: false,
        timer: 500
    })
}
//alert ok창
function okAlert(msg) {
    Swal.fire(msg)
}

//DB에 새로운 정보를 추가하는 함수(등록하기)
function wishlist_post() {
    let url = $('#url_input').val()    //변수 : url, name, price, memo, status
    let name = $('#name_input').val()
    let price = $('#price_input').val()
    let memo = $('#memo_input').val()
    // let status = $('#status_input').val()
    // let test = $('#status_btn').val()
    let status = $("input[type=radio][name=status]:checked").val(); // 상태 변경 (수정)

    let alertMsg = "";
    if (url_verifier == 'false') {
        alertMsg = 'URL 유효성 체크 해주세요!';
        okAlert(alertMsg);
        return
    }
    if (name.length == 0) {
        alertMsg = '상품명을 입력해 주세요!';
        okAlert(alertMsg);
        return
    }
    $.ajax({
        type: 'POST',
        url: '/wishlist',
        data: { url_give: url, name_give: name, price_give: price, memo_give: memo, status_give: status },
        success: function (response) {
            checkedAlert(response['msg'])
            window.location.reload()
        }
    });
}


//특정 listId를 가진 사용자의 정보를 수정
function wishlist_modify(listId) {
    let url = $('#url_modify').val()
    let name = $('#name_modify').val()
    let price = $('#price_modify').val()
    let memo = $('#memo_modify').val()
    let status = $("input[type=radio][name=status]:checked").val(); // 상태 변경 (수정)

    let alertMsg = "";
    if (url_verifier == 'false') {
        alertMsg =  'URL 유효성 체크 해주세요!';
        okAlert(alertMsg);
        return
    }
    if (name.length == 0) {
        alertMsg = '상품명을 입력해 주세요!';
        okAlert(alertMsg);
        return
    }
    $.ajax({                                 //변수: url, name, price, memo, status, listId
        type: 'PUT',
        url: '/wishlist/{listId}',
        data: { url_give: url, name_give: name, price_give: price, memo_give: memo, status_give: status, listId_give: listId },
        success: function (response) {
            checkedAlert(response['msg'])
            window.location.reload()
        }
    });
}

//상태만 수정하는 함수
function modifying_status(listId) {
    let status = $('#status_modify').val()        //status 부분 수정하기
    $.ajax({                                      //변수: status, listId
        type: 'PUT',
        url: '/wishlist/{listId}/status',
        data: { status_give: status, listId_give: listId },
        success: function (response) {
            checkedAlert(response['msg'])
            window.location.reload()
        }
    });
}

//특정 listId를 가진 정보를 삭제
function wishlist_delete(listId) {
    Swal.fire({
        title: '정말 삭제 하시겠습니까?',
        text: "삭제되면 복구할 수 없습니다",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#C068A8',
        cancelButtonColor: '#D9D9D9',
        confirmButtonText: '삭제',
        cancelButtonText: '취소'
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                type: 'DELETE',
                url: '/wishlist/{listId}',
                data: { listId_give: listId },
                success: function (response) {
                    checkedAlert(response['msg'])
                    window.location.reload()
                }
            });
        }
    })
}

//url 형식이 맞는지 검증하는 함수. url 검증 버튼에서 call
function url_certifi() {
    let url = $('#url_input').val()

    let alertMsg = "";
    if (url == "") {
        alertMsg = "URL을 입력해 주세요!";
        okAlert(alertMsg);
        return
    }
    //url 형식 검증
    let regex = /^(((http(s?))\:\/\/)?)([0-9a-zA-Z\-]+\.)+[a-zA-Z]{2,6}(\:[0-9]+)?(\/\S*)?/;

    if (regex.test(url)) {
        // location.href = url;     해당 url로 이동하는 식
        alertMsg = "유효한 URL 입니다";
        okAlert(alertMsg);
        url_verifier = 'true'
        return
    } else {
        alertMsg = "유효하지 않은 URL 입니다";
        okAlert(alertMsg);
        return
    }
}

function url_mod_certifi() {
    let url = $('#url_modify').val()

    if (url == "") {
        alertMsg = "URL을 입력해 주세요!";
        okAlert(alertMsg);
        return
    }
    //url 형식 검증
    let regex = /^(((http(s?))\:\/\/)?)([0-9a-zA-Z\-]+\.)+[a-zA-Z]{2,6}(\:[0-9]+)?(\/\S*)?/;

    if (regex.test(url)) {
        // location.href = url;     해당 url로 이동하는 식
        alertMsg = "유효한 URL 입니다";
        okAlert(alertMsg);
        url_verifier = 'true'
        return
    } else {
        alertMsg = "유효하지 않은 URL입니다";
        okAlert(alertMsg);
        return
    }
}

//box open&close 함수들
function open_posting_box() {            //상품 등록 박스를 open
    $('#posting_box').show()
}
function close_posting_box() {           //상품 등록 박스를 close
    url_verifier = 'false'
    $('#posting_box').hide()
}

function open_modify_box(listId) {         //상품 수정 박스를 open
    $('#modify_box').show()
    $('#modify_box').empty()
    $.ajax({                            //기존 정보를 로딩해서 박스에 뿌려줌
        type: 'GET',                    //받는 변수 : image, url, name, price, memo, status
        url: '/wishlist/{listId}?listId_give=' + listId,
        data: {},
        success: function (response) {
            rows = response['listId_item']
        }
    })
    let temp_html = `
                <div class="card-title" style="display: flex;">
                    <h5>상품 수정하기</h5>
                    <button onclick="close_modify_box()" type="button" class="pop-close">닫기</button>
                </div>
                <div class="form-floating" id="url_box">
                    <label for="url_modify">URL</label>
                    <input type="text" class="required form-url form-control" id="url_modify" placeholder="url">
                    <button class="url-check" onclick="url_mod_certifi()">url 검증</button>
                </div>
                <div class="form-floating">
                    <label for="name_modify">상품명</label>
                    <input type="text" class="required form-control" id="name_modify" placeholder="name">
                </div>
                <div class="form-floating">
                    <label for="price_modify">가격</label>
                    <input type="text" class="form-control" id="price_modify" placeholder="price" >
                </div>
                <div class="form-floating">
                    <label for="memo_modify">메모</label>
                    <textarea class="form-control" id="memo_modify" maxlength="100" placeholder="메모수정"></textarea>
                </div>
                <div class="btn-group" role="group" aria-label="Basic radio toggle button group">
                    <input type="radio" class="btn-check" name="status" id="toBuy" value="toBuy" autocomplete="off">
                    <label class="btn btn-outline-primary" for="toBuy">구매예정</label>
                    <input type="radio" class="btn-check" name="status" id="hold" value="hold" autocomplete="off">
                    <label class="btn btn-outline-primary" for="hold">구매보류</label>
                    <input type="radio" class="btn-check" name="status" id="order" value="order" autocomplete="off">
                    <label class="btn btn-outline-primary" for="order">구매완료</label>
                </div>
                <div class="mybtns">
                    <button onclick="wishlist_modify(${listId})" type="button" class="btn btn-dark">수정하기</button>
                    <button onclick="close_modify_box()" type="button" class="btn btn-outline-secondary">닫기</button>
                </div>
            `
    $('#modify_box').append(temp_html)
}
function close_modify_box() {           //상품 수정 박스를 close
    url_verifier = 'false'
    $('#modify_box').hide()
}

function open_delete_box() {            //상품 삭제 박스를 open
    $('#delete-box').show()
}
function close_delete_box() {           //상품 삭제 박스를 close
    $('#delete-box').hide()
}
